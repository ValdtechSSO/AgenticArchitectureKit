from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .contracts import ContractError, load_json, validate_schema
from .resources import read_json as read_bundled_json


CHECKPOINT_ROOT = ".agentic/runtime/checkpoints"
TASK_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")
PLACEHOLDER_PATTERN = re.compile(r"^(replace with\b|todo\b|tbd\b|unknown$)", re.IGNORECASE)


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def file_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _timestamp(value: str, label: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ContractError(f"{label} must be an ISO-8601 timestamp") from error
    if parsed.tzinfo is None:
        raise ContractError(f"{label} must include a timezone")
    return parsed.astimezone(timezone.utc)


def validate_task_id(task_id: str) -> None:
    if not TASK_PATTERN.fullmatch(task_id):
        raise ContractError("Task id may contain only letters, digits, dot, underscore, and hyphen")


def repository_file(root: Path, value: str, label: str) -> tuple[Path, str]:
    supplied = Path(value)
    if supplied.is_absolute():
        raise ContractError(f"{label} must be a repository-relative path")
    root = root.resolve()
    path = (root / supplied).resolve()
    try:
        relative = path.relative_to(root).as_posix()
    except ValueError as error:
        raise ContractError(f"{label} escapes the repository root: {value}") from error
    if not path.is_file():
        raise ContractError(f"{label} does not exist or is not a file: {value}")
    return path, relative


def task_directory(root: Path, task_id: str) -> Path:
    validate_task_id(task_id)
    root = root.resolve()
    path = (root / CHECKPOINT_ROOT / task_id).resolve()
    try:
        path.relative_to(root)
    except ValueError as error:
        raise ContractError("Checkpoint directory escapes the repository root") from error
    return path


def _git_bytes(root: Path, *arguments: str) -> bytes:
    try:
        return subprocess.run(
            ["git", *arguments], cwd=root, check=True, capture_output=True
        ).stdout
    except (OSError, subprocess.CalledProcessError) as error:
        raise ContractError("Execution checkpoints require a readable Git repository") from error


def _git_paths(root: Path, *arguments: str) -> list[str]:
    raw = _git_bytes(root, *arguments)
    return [os.fsdecode(item) for item in raw.split(b"\0") if item]


def workspace_snapshot(root: Path) -> dict[str, Any]:
    root = root.resolve()
    revision = _git_bytes(root, "rev-parse", "HEAD").decode("ascii", "strict").strip()
    candidates = sorted(set(_git_paths(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard")))
    excluded_prefix = CHECKPOINT_ROOT + "/"
    manifest: list[dict[str, Any]] = []
    for relative in candidates:
        normalized = Path(relative).as_posix()
        if normalized == CHECKPOINT_ROOT or normalized.startswith(excluded_prefix):
            continue
        if Path(normalized).is_absolute() or ".." in Path(normalized).parts:
            raise ContractError(f"Git returned an unsafe repository path: {relative}")
        path = root / normalized
        try:
            metadata = path.lstat()
        except FileNotFoundError:
            manifest.append({"path": normalized, "kind": "missing", "mode": 0, "digest": canonical_digest(None)})
            continue
        mode = stat.S_IMODE(metadata.st_mode)
        if stat.S_ISLNK(metadata.st_mode):
            payload = os.fsencode(os.readlink(path))
            kind = "symlink"
        elif stat.S_ISREG(metadata.st_mode):
            payload = path.read_bytes()
            kind = "file"
        else:
            raise ContractError(f"Unsupported Git worktree entry for checkpointing: {normalized}")
        manifest.append({
            "path": normalized,
            "kind": kind,
            "mode": mode,
            "digest": "sha256:" + hashlib.sha256(payload).hexdigest(),
        })

    changed = sorted(set(
        _git_paths(root, "diff", "--name-only", "-z", "HEAD", "--")
        + _git_paths(root, "ls-files", "-z", "--others", "--exclude-standard")
    ))
    changed = [
        Path(item).as_posix() for item in changed
        if Path(item).as_posix() != CHECKPOINT_ROOT
        and not Path(item).as_posix().startswith(excluded_prefix)
    ]
    return {
        "repositoryRevision": revision,
        "dirty": bool(changed),
        "fingerprint": canonical_digest(manifest),
        "fileCount": len(manifest),
        "changedPaths": changed,
    }


def _schema_errors(value: Any, resource_name: str) -> list[str]:
    schema = read_bundled_json(f"data/schemas/{resource_name}")
    return validate_schema(value, schema)


def _require_schema(value: Any, resource_name: str, label: str) -> None:
    errors = _schema_errors(value, resource_name)
    if errors:
        raise ContractError(f"Invalid {label}: " + "; ".join(errors))


def validate_state(state_value: Any) -> dict[str, Any]:
    if not isinstance(state_value, dict):
        raise ContractError("Checkpoint state must be a JSON object")
    _require_schema(state_value, "checkpoint-state.schema.json", "checkpoint state")

    def reject_placeholders(value: Any, location: str = "state") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key != "$schema":
                    reject_placeholders(child, f"{location}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                reject_placeholders(child, f"{location}[{index}]")
        elif isinstance(value, str):
            if not value.strip() and not location.endswith(".supersededBy"):
                raise ContractError(f"Checkpoint state contains blank text at {location}")
            if PLACEHOLDER_PATTERN.match(value.strip()):
                raise ContractError(f"Checkpoint state contains an unresolved placeholder at {location}")

    reject_placeholders(state_value)
    for field, identity in (
        ("activeInvariants", "id"),
        ("decisions", "id"),
        ("planDeviations", "id"),
        ("openRisks", "id"),
        ("resolvedRisks", "riskId"),
    ):
        identifiers = [item[identity] for item in state_value[field]]
        if len(identifiers) != len(set(identifiers)):
            raise ContractError(f"Checkpoint state contains duplicate identifiers in {field}")
    decisions = {item["id"]: item for item in state_value["decisions"]}
    for decision in decisions.values():
        if decision["status"] == "active" and decision["supersededBy"]:
            raise ContractError(f"Active decision {decision['id']} cannot declare supersededBy")
        if decision["status"] == "superseded":
            replacement = decision["supersededBy"]
            if not replacement or replacement == decision["id"] or replacement not in decisions:
                raise ContractError(f"Superseded decision {decision['id']} must reference another recorded decision")
    open_ids = {item["id"] for item in state_value["openRisks"]}
    resolved_ids = {item["riskId"] for item in state_value["resolvedRisks"]}
    overlap = open_ids & resolved_ids
    if overlap:
        raise ContractError("Risks cannot be both open and resolved: " + ", ".join(sorted(overlap)))
    return state_value


def load_state(root: Path, state_path: str) -> dict[str, Any]:
    path, _ = repository_file(root, state_path, "State file")
    return validate_state(load_json(path))


def _without_digest(value: dict[str, Any], field: str) -> dict[str, Any]:
    copy = dict(value)
    copy.pop(field, None)
    return copy


def _validate_digest(value: dict[str, Any], field: str, label: str) -> None:
    if value.get(field) != canonical_digest(_without_digest(value, field)):
        raise ContractError(f"{label} digest does not match its content")


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _checkpoint_files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    matches: list[tuple[int, Path]] = []
    for path in directory.glob("checkpoint-*.json"):
        match = re.fullmatch(r"checkpoint-([0-9]{6})-sha256-([0-9a-f]{12})\.json", path.name)
        if not match:
            raise ContractError(f"Unexpected checkpoint filename: {path.name}")
        matches.append((int(match.group(1)), path))
    return [path for _, path in sorted(matches)]


def _validate_test_outputs(root: Path, task_id: str, value: dict[str, Any]) -> None:
    expected_prefix = f"{CHECKPOINT_ROOT}/{task_id}/tests/"
    for stream_name in ("stdout", "stderr"):
        output = value[stream_name]
        if not output["path"].startswith(expected_prefix):
            raise ContractError(f"Test {stream_name} artifact must remain inside its task evidence directory")
        path, _ = repository_file(root, output["path"], f"Test {stream_name} artifact")
        if file_digest(path) != output["digest"] or path.stat().st_size != output["bytes"]:
            raise ContractError(f"Test {stream_name} artifact does not match its retained digest and size")


def _load_test_evidence(root: Path, path: Path, task_id: str) -> dict[str, Any]:
    value = load_json(path)
    if not isinstance(value, dict):
        raise ContractError(f"Test evidence must be an object: {path}")
    _require_schema(value, "checkpoint-test-evidence.schema.json", "checkpoint test evidence")
    _validate_digest(value, "evidenceDigest", "Test evidence")
    if value["taskId"] != task_id:
        raise ContractError(f"Test evidence belongs to another task: {path}")
    if not path.name.endswith(f"sha256-{value['evidenceDigest'].removeprefix('sha256:')[:12]}.json"):
        raise ContractError("Test-evidence filename does not match its content digest")
    if _timestamp(value["completedAt"], "Test completion") < _timestamp(value["startedAt"], "Test start"):
        raise ContractError("Test completion precedes its start")
    if value["outcome"] == "passed" and value["exitCode"] != 0:
        raise ContractError("Passing test evidence must have exit code 0")
    if value["outcome"] in {"failed", "error"} and value["exitCode"] == 0:
        raise ContractError("Non-passing test evidence cannot have exit code 0")
    _validate_test_outputs(root, task_id, value)
    return value


def load_test_evidence(root: Path, directory: Path, task_id: str) -> list[dict[str, Any]]:
    tests = directory / "tests"
    if not tests.is_dir():
        return []
    paths = sorted(tests.glob("*.json"))
    for path in paths:
        if not re.fullmatch(r"test-.+-sha256-[0-9a-f]{12}\.json", path.name):
            raise ContractError(f"Unexpected test-evidence filename: {path.name}")
    return [_load_test_evidence(root, path, task_id) for path in paths]


def _load_receipt(path: Path, task_id: str) -> dict[str, Any]:
    value = load_json(path)
    if not isinstance(value, dict):
        raise ContractError(f"Resume receipt must be an object: {path}")
    _require_schema(value, "checkpoint-resume-receipt.schema.json", "checkpoint resume receipt")
    _validate_digest(value, "receiptDigest", "Resume receipt")
    if value["taskId"] != task_id:
        raise ContractError(f"Resume receipt belongs to another task: {path}")
    if not path.name.endswith(f"sha256-{value['receiptDigest'].removeprefix('sha256:')[:12]}.json"):
        raise ContractError("Resume-receipt filename does not match its content digest")
    _timestamp(value["resumedAt"], "Resume time")
    return value


def load_receipts(directory: Path, task_id: str) -> list[dict[str, Any]]:
    receipts = directory / "receipts"
    if not receipts.is_dir():
        return []
    paths = sorted(receipts.glob("*.json"))
    for path in paths:
        if not re.fullmatch(r"resume-[0-9]{6}-.+-sha256-[0-9a-f]{12}\.json", path.name):
            raise ContractError(f"Unexpected resume-receipt filename: {path.name}")
    values = [_load_receipt(path, task_id) for path in paths]
    digests = [item["receiptDigest"] for item in values]
    if len(digests) != len(set(digests)):
        raise ContractError("Checkpoint task contains duplicate resume receipts")
    return values


def _receipt_for_checkpoint(receipts: Iterable[dict[str, Any]], checkpoint: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        receipt for receipt in receipts
        if receipt["checkpointDigest"] == checkpoint["checkpointDigest"]
        and receipt["checkpointSequence"] == checkpoint["sequence"]
        and receipt["plan"] == checkpoint["plan"]
        and receipt["workspaceFingerprint"] == checkpoint["workspace"]["fingerprint"]
    ]


def _validate_state_progression(previous: dict[str, Any], current: dict[str, Any]) -> None:
    if previous["globalObjective"] != current["globalObjective"]:
        raise ContractError("Global objective cannot change inside one checkpoint chain; start a new task")

    previous_decisions = {item["id"]: item for item in previous["decisions"]}
    current_decisions = {item["id"]: item for item in current["decisions"]}
    immutable_decision_fields = ("decision", "rationale", "affectsInvariants", "source")
    for identifier, old in previous_decisions.items():
        new = current_decisions.get(identifier)
        if new is None:
            raise ContractError(f"Cumulative decision disappeared from checkpoint state: {identifier}")
        if any(old.get(field) != new.get(field) for field in immutable_decision_fields):
            raise ContractError(f"Cumulative decision was rewritten instead of superseded: {identifier}")
        if old["status"] == "superseded" and new["status"] != "superseded":
            raise ContractError(f"Superseded decision became active again: {identifier}")

    for field, identity in (("planDeviations", "id"), ("resolvedRisks", "riskId")):
        current_items = {item[identity]: item for item in current[field]}
        for old in previous[field]:
            if current_items.get(old[identity]) != old:
                raise ContractError(f"Cumulative {field} entry disappeared or was rewritten: {old[identity]}")

    current_open = {item["id"] for item in current["openRisks"]}
    current_resolved = {item["riskId"] for item in current["resolvedRisks"]}
    for risk in previous["openRisks"]:
        if risk["id"] not in current_open and risk["id"] not in current_resolved:
            raise ContractError(f"Open risk disappeared without recorded resolution: {risk['id']}")

    previous_invariants = {item["id"]: item for item in previous["activeInvariants"]}
    current_invariants = {item["id"]: item for item in current["activeInvariants"]}
    new_decisions = [item for key, item in current_decisions.items() if key not in previous_decisions]
    for identifier, old in previous_invariants.items():
        new = current_invariants.get(identifier)
        changed = new is None or new["statement"] != old["statement"]
        if changed and not any(identifier in decision["affectsInvariants"] for decision in new_decisions):
            raise ContractError(
                f"Invariant {identifier} was removed or rewritten without a new decision explaining the change"
            )


def _validate_test_assessment(checkpoint: dict[str, Any]) -> None:
    evidence = checkpoint["testEvidence"]
    workspace = checkpoint["workspace"]
    current = [
        item for item in evidence
        if item["afterWorkspace"]["repositoryRevision"] == workspace["repositoryRevision"]
        and item["afterWorkspace"]["fingerprint"] == workspace["fingerprint"]
    ]
    expected_digests = [item["evidenceDigest"] for item in current]
    if any(item["outcome"] != "passed" for item in current):
        expected_status = "failed"
    elif current:
        expected_status = "passed"
    elif evidence:
        expected_status = "stale"
    else:
        expected_status = "not-run"
    assessment = checkpoint["testAssessment"]
    if assessment["status"] != expected_status or assessment["currentEvidenceDigests"] != expected_digests:
        raise ContractError("Checkpoint test assessment does not match its retained evidence and workspace")


def load_checkpoint_chain(root: Path, task_id: str) -> tuple[Path, list[dict[str, Any]], list[dict[str, Any]]]:
    directory = task_directory(root, task_id)
    receipts = load_receipts(directory, task_id)
    receipt_by_digest = {item["receiptDigest"]: item for item in receipts}
    checkpoints: list[dict[str, Any]] = []
    used_test_evidence: set[str] = set()
    for expected_sequence, path in enumerate(_checkpoint_files(directory), start=1):
        value = load_json(path)
        if not isinstance(value, dict):
            raise ContractError(f"Checkpoint must be a JSON object: {path}")
        _require_schema(value, "execution-checkpoint.schema.json", "execution checkpoint")
        _validate_digest(value, "checkpointDigest", "Checkpoint")
        created_at = _timestamp(value["createdAt"], "Checkpoint creation time")
        expected_name = (
            f"checkpoint-{value['sequence']:06d}-sha256-"
            f"{value['checkpointDigest'].removeprefix('sha256:')[:12]}.json"
        )
        if path.name != expected_name:
            raise ContractError("Checkpoint filename does not match its sequence and digest")
        validate_state(value["state"])
        if value["taskId"] != task_id or value["sequence"] != expected_sequence:
            raise ContractError("Checkpoint chain has a task or sequence mismatch")
        for evidence in value["testEvidence"]:
            _require_schema(evidence, "checkpoint-test-evidence.schema.json", "embedded test evidence")
            _validate_digest(evidence, "evidenceDigest", "Embedded test evidence")
            if _timestamp(evidence["completedAt"], "Test completion") < _timestamp(evidence["startedAt"], "Test start"):
                raise ContractError("Embedded test completion precedes its start")
            if evidence["outcome"] == "passed" and evidence["exitCode"] != 0:
                raise ContractError("Embedded passing test evidence must have exit code 0")
            if evidence["outcome"] in {"failed", "error"} and evidence["exitCode"] == 0:
                raise ContractError("Embedded non-passing test evidence cannot have exit code 0")
            _validate_test_outputs(root, task_id, evidence)
            if evidence["taskId"] != task_id:
                raise ContractError("Embedded test evidence belongs to another task")
            if evidence["evidenceDigest"] in used_test_evidence:
                raise ContractError("Test evidence was consumed by more than one checkpoint")
            used_test_evidence.add(evidence["evidenceDigest"])
        _validate_test_assessment(value)
        if not checkpoints:
            if value["previousCheckpointDigest"] != "ROOT" or value["continuedFromReceipt"] != "ROOT":
                raise ContractError("First checkpoint must start at ROOT")
        else:
            previous = checkpoints[-1]
            if value["previousCheckpointDigest"] != previous["checkpointDigest"]:
                raise ContractError("Checkpoint chain link does not match the previous checkpoint")
            if value["plan"] != previous["plan"]:
                raise ContractError("Original plan identity changed inside the checkpoint chain")
            receipt = receipt_by_digest.get(value["continuedFromReceipt"])
            if receipt not in _receipt_for_checkpoint(receipts, previous):
                raise ContractError("Checkpoint continuation does not reference a valid resume receipt")
            if _timestamp(receipt["resumedAt"], "Resume time") < _timestamp(previous["createdAt"], "Checkpoint creation time"):
                raise ContractError("Checkpoint continuation references a receipt created before its checkpoint")
            if created_at < _timestamp(previous["createdAt"], "Checkpoint creation time"):
                raise ContractError("Checkpoint creation timestamps are not monotonic")
            _validate_state_progression(previous["state"], value["state"])
        checkpoints.append(value)
    return directory, checkpoints, receipts


def _plan_identity(root: Path, plan_path: str) -> tuple[dict[str, str], str]:
    path, relative = repository_file(root, plan_path, "Original plan")
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ContractError("Original plan must be UTF-8 text") from error
    return {"path": relative, "digest": file_digest(path)}, content


def _current_test_assessment(
    evidence: list[dict[str, Any]], workspace: dict[str, Any], no_tests_reason: str | None
) -> dict[str, Any]:
    current = [
        item for item in evidence
        if item["afterWorkspace"]["repositoryRevision"] == workspace["repositoryRevision"]
        and item["afterWorkspace"]["fingerprint"] == workspace["fingerprint"]
    ]
    current_digests = [item["evidenceDigest"] for item in current]
    if any(item["outcome"] != "passed" for item in current):
        return {"status": "failed", "reason": "At least one test command failed against the checkpoint workspace.", "currentEvidenceDigests": current_digests}
    if current:
        return {"status": "passed", "reason": "Recorded test commands passed against the checkpoint workspace.", "currentEvidenceDigests": current_digests}
    if evidence:
        return {"status": "stale", "reason": "Recorded test evidence targets an earlier workspace state.", "currentEvidenceDigests": []}
    if not no_tests_reason or not no_tests_reason.strip():
        raise ContractError("A checkpoint without new test evidence requires --no-tests-reason")
    return {"status": "not-run", "reason": no_tests_reason.strip(), "currentEvidenceDigests": []}


def create_checkpoint(
    root: Path,
    task_id: str,
    plan_path: str,
    state_path: str,
    no_tests_reason: str | None = None,
) -> tuple[Path, dict[str, Any]]:
    root = root.resolve()
    directory, checkpoints, receipts = load_checkpoint_chain(root, task_id)
    plan, _ = _plan_identity(root, plan_path)
    state = load_state(root, state_path)
    workspace = workspace_snapshot(root)
    previous = checkpoints[-1] if checkpoints else None
    if previous and plan != previous["plan"]:
        raise ContractError("Original plan path or content changed; checkpoint chain cannot continue")
    if previous:
        matching = _receipt_for_checkpoint(receipts, previous)
        if not matching:
            raise ContractError("Resume the previous checkpoint before creating the next checkpoint")
        continued_from = matching[-1]["receiptDigest"]
        _validate_state_progression(previous["state"], state)
    else:
        continued_from = "ROOT"

    all_evidence = load_test_evidence(root, directory, task_id)
    consumed = {
        item["evidenceDigest"]
        for checkpoint in checkpoints
        for item in checkpoint["testEvidence"]
    }
    new_evidence = [item for item in all_evidence if item["evidenceDigest"] not in consumed]
    assessment = _current_test_assessment(new_evidence, workspace, no_tests_reason)
    sequence = len(checkpoints) + 1
    checkpoint: dict[str, Any] = {
        "version": 1,
        "taskId": task_id,
        "sequence": sequence,
        "createdAt": utc_now(),
        "previousCheckpointDigest": previous["checkpointDigest"] if previous else "ROOT",
        "continuedFromReceipt": continued_from,
        "plan": plan,
        "workspace": workspace,
        "state": state,
        "testEvidence": new_evidence,
        "testAssessment": assessment,
    }
    checkpoint["checkpointDigest"] = canonical_digest(checkpoint)
    _require_schema(checkpoint, "execution-checkpoint.schema.json", "execution checkpoint")
    path = directory / (
        f"checkpoint-{sequence:06d}-sha256-{checkpoint['checkpointDigest'].removeprefix('sha256:')[:12]}.json"
    )
    if path.exists():
        raise ContractError(f"Checkpoint path already exists: {path}")
    _atomic_json(path, checkpoint)
    return path, checkpoint


def create_resume_receipt(
    root: Path, task_id: str, plan_path: str
) -> tuple[Path, dict[str, Any], dict[str, Any], str]:
    root = root.resolve()
    directory, checkpoints, _ = load_checkpoint_chain(root, task_id)
    if not checkpoints:
        raise ContractError("Task has no checkpoint to resume")
    latest = checkpoints[-1]
    plan, content = _plan_identity(root, plan_path)
    if plan != latest["plan"]:
        raise ContractError("Original plan path or digest does not match the checkpoint")
    workspace = workspace_snapshot(root)
    if workspace["repositoryRevision"] != latest["workspace"]["repositoryRevision"] or workspace["fingerprint"] != latest["workspace"]["fingerprint"]:
        raise ContractError("Workspace changed after the checkpoint; restore it or create a reconciled checkpoint before resuming")
    receipt: dict[str, Any] = {
        "version": 1,
        "taskId": task_id,
        "checkpointSequence": latest["sequence"],
        "checkpointDigest": latest["checkpointDigest"],
        "plan": plan,
        "workspaceFingerprint": workspace["fingerprint"],
        "resumedAt": utc_now(),
    }
    receipt["receiptDigest"] = canonical_digest(receipt)
    stamp = receipt["resumedAt"].replace(":", "-").replace(".", "-")
    path = directory / "receipts" / (
        f"resume-{latest['sequence']:06d}-{stamp}-sha256-{receipt['receiptDigest'].removeprefix('sha256:')[:12]}.json"
    )
    _require_schema(receipt, "checkpoint-resume-receipt.schema.json", "checkpoint resume receipt")
    _atomic_json(path, receipt)
    return path, receipt, latest, content


def _stream_to_log(source: Any, destination: Any, log: Any) -> None:
    while True:
        chunk = source.read(8192)
        if not chunk:
            break
        log.write(chunk)
        log.flush()
        binary = getattr(destination, "buffer", None)
        try:
            if binary is not None:
                binary.write(chunk)
                binary.flush()
            else:
                destination.write(chunk.decode("utf-8", "replace"))
                destination.flush()
        except (OSError, ValueError):
            # A detached terminal must not stop draining the child process or
            # prevent retention of its output artifact.
            pass


def _output_record(root: Path, path: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(root).as_posix(),
        "digest": file_digest(path),
        "bytes": path.stat().st_size,
    }


def record_test_execution(root: Path, task_id: str, command: list[str]) -> tuple[Path, dict[str, Any], int]:
    root = root.resolve()
    directory, checkpoints, receipts = load_checkpoint_chain(root, task_id)
    if checkpoints and not _receipt_for_checkpoint(receipts, checkpoints[-1]):
        raise ContractError("Resume the latest checkpoint before running tests for the next segment")
    arguments = list(command)
    if arguments and arguments[0] == "--":
        arguments = arguments[1:]
    if not arguments or any(not item for item in arguments):
        raise ContractError("run-test requires a command after --")
    before = workspace_snapshot(root)
    started = utc_now()
    stamp = started.replace(":", "-").replace(".", "-")
    test_directory = directory / "tests"
    test_directory.mkdir(parents=True, exist_ok=True)
    stdout_path = test_directory / f"test-{stamp}-stdout.log"
    stderr_path = test_directory / f"test-{stamp}-stderr.log"
    outcome = "error"
    with stdout_path.open("xb") as stdout_log, stderr_path.open("xb") as stderr_log:
        try:
            process = subprocess.Popen(arguments, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError:
            exit_code = 127
        else:
            assert process.stdout is not None and process.stderr is not None
            stdout_thread = threading.Thread(
                target=_stream_to_log, args=(process.stdout, sys.stdout, stdout_log), daemon=True
            )
            stderr_thread = threading.Thread(
                target=_stream_to_log, args=(process.stderr, sys.stderr, stderr_log), daemon=True
            )
            stdout_thread.start()
            stderr_thread.start()
            exit_code = process.wait()
            stdout_thread.join()
            stderr_thread.join()
            outcome = "passed" if exit_code == 0 else "failed"
    after = workspace_snapshot(root)
    evidence: dict[str, Any] = {
        "version": 1,
        "taskId": task_id,
        "startedAt": started,
        "completedAt": utc_now(),
        "command": arguments,
        "exitCode": exit_code,
        "outcome": outcome,
        "beforeWorkspace": before,
        "afterWorkspace": after,
        "stdout": _output_record(root, stdout_path),
        "stderr": _output_record(root, stderr_path),
    }
    evidence["evidenceDigest"] = canonical_digest(evidence)
    path = directory / "tests" / (
        f"test-{stamp}-sha256-{evidence['evidenceDigest'].removeprefix('sha256:')[:12]}.json"
    )
    _require_schema(evidence, "checkpoint-test-evidence.schema.json", "checkpoint test evidence")
    _atomic_json(path, evidence)
    return path, evidence, exit_code


def checkpoint_status(root: Path, task_id: str, plan_path: str) -> dict[str, Any]:
    root = root.resolve()
    directory, checkpoints, receipts = load_checkpoint_chain(root, task_id)
    plan, _ = _plan_identity(root, plan_path)
    workspace = workspace_snapshot(root)
    if not checkpoints:
        return {
            "taskId": task_id,
            "status": "NO_CHECKPOINT",
            "checkpointCount": 0,
            "plan": plan,
            "workspace": workspace,
        }
    latest = checkpoints[-1]
    plan_matches = plan == latest["plan"]
    workspace_matches = (
        workspace["repositoryRevision"] == latest["workspace"]["repositoryRevision"]
        and workspace["fingerprint"] == latest["workspace"]["fingerprint"]
    )
    matching_receipts = _receipt_for_checkpoint(receipts, latest)
    if not plan_matches:
        status = "PLAN_MISMATCH"
    elif workspace_matches and not matching_receipts:
        status = "RESUME_REQUIRED"
    elif matching_receipts:
        status = "RESUMED" if workspace_matches else "IN_PROGRESS"
    else:
        status = "UNRESUMED_WORKSPACE_DRIFT"
    state = latest["state"]
    return {
        "taskId": task_id,
        "status": status,
        "checkpointCount": len(checkpoints),
        "latestCheckpoint": {
            "sequence": latest["sequence"],
            "digest": latest["checkpointDigest"],
            "createdAt": latest["createdAt"],
            "path": _checkpoint_files(directory)[-1].relative_to(root).as_posix(),
        },
        "plan": {"expected": latest["plan"], "current": plan, "matches": plan_matches},
        "workspace": {
            "checkpoint": latest["workspace"],
            "current": workspace,
            "matches": workspace_matches,
        },
        "resumeReceiptDigests": [item["receiptDigest"] for item in matching_receipts],
        "testAssessment": latest["testAssessment"],
        "attention": {
            "invariants": [item["id"] for item in state["activeInvariants"] if item["status"] != "holds"],
            "openRisks": [item["id"] for item in state["openRisks"]],
        },
        "nextObjective": state["nextObjective"],
    }


def verify_checkpoint(root: Path, task_id: str, plan_path: str) -> tuple[int, list[dict[str, str]], dict[str, Any]]:
    status = checkpoint_status(root, task_id, plan_path)
    findings = [{"rule": "CPK001", "status": "PASS", "message": "Checkpoint schemas, digests, and chain links are valid."}]
    if status["status"] == "NO_CHECKPOINT":
        findings.append({"rule": "CPK002", "status": "FAIL", "message": "No durable checkpoint exists for the task."})
    else:
        findings.append({"rule": "CPK002", "status": "PASS", "message": "Checkpoint state contains the required objective, invariants, decisions, deviations, tests, risks, and next objective."})
        if status["plan"]["matches"]:
            findings.append({"rule": "CPK003", "status": "PASS", "message": "The original plan path and content digest match."})
        else:
            findings.append({"rule": "CPK003", "status": "FAIL", "message": "The original plan path or content changed."})
        if status["status"] in {"RESUMED", "IN_PROGRESS"}:
            findings.append({"rule": "CPK004", "status": "PASS", "message": "A valid resume receipt proves the plan and checkpoint were supplied before continuation."})
        elif status["status"] == "RESUME_REQUIRED":
            findings.append({"rule": "CPK004", "status": "REVIEW_REQUIRED", "message": "The next segment must resume from the original plan and latest checkpoint."})
        else:
            findings.append({"rule": "CPK004", "status": "FAIL", "message": "Workspace drift occurred without a valid resume receipt."})
    exit_code = 1 if any(item["status"] in {"FAIL", "REVIEW_REQUIRED"} for item in findings) else 0
    return exit_code, findings, status
