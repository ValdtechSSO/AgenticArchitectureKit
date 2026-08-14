#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from validator import __version__
from validator.adapters import observe
from validator.contracts import ContractError, load_json, load_yaml_subset, validate_schema
from validator.engine import EVALUATORS, evaluate
from validator.model import STATUSES, ValidationContext


def _path(root: Path, value: str) -> Path:
    path = Path(value)
    candidate = path.resolve() if path.is_absolute() else (root / path).resolve()
    return candidate


def _repository_path(root: Path, value: str) -> Path:
    candidate = _path(root, value)
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise ContractError(f"Path escapes repository root: {value}") from error
    return candidate


def _display_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _validate_with_schema(instance: Any, schema_path: Path, label: str) -> None:
    schema = load_json(schema_path)
    errors = validate_schema(instance, schema)
    if errors:
        details = "\n  - ".join(errors)
        raise ContractError(f"{label} does not conform to {schema_path}:\n  - {details}")


def _load_catalog(path: Path) -> dict[str, dict[str, Any]]:
    document = load_json(path)
    if not isinstance(document, dict) or document.get("version") != 1 or not isinstance(document.get("rules"), list):
        raise ContractError(f"Invalid rule catalog: {path}")
    catalog: dict[str, dict[str, Any]] = {}
    required = {"id", "title", "description", "evaluator", "automatic", "inputs"}
    for index, rule in enumerate(document["rules"]):
        if not isinstance(rule, dict) or not required.issubset(rule):
            raise ContractError(f"Invalid rule at {path}:rules[{index}]")
        rule_id = rule["id"]
        if not isinstance(rule_id, str) or not rule_id:
            raise ContractError(f"Rule id is invalid at {path}:rules[{index}]")
        if rule_id in catalog:
            raise ContractError(f"Duplicate rule id '{rule_id}' in {path}")
        if rule["evaluator"] not in EVALUATORS:
            raise ContractError(f"Rule {rule_id} has unknown evaluator '{rule['evaluator']}'")
        catalog[rule_id] = rule
    evaluator_counts = Counter(rule["evaluator"] for rule in catalog.values())
    duplicates = sorted(name for name, count in evaluator_counts.items() if count > 1)
    if duplicates:
        raise ContractError(f"Evaluators may be assigned to only one rule: {', '.join(duplicates)}")
    unused = sorted(set(EVALUATORS) - set(evaluator_counts))
    if unused:
        raise ContractError(f"Rule catalog omits evaluators: {', '.join(unused)}")
    return catalog


def _validate_policy_semantics(root: Path, policy: dict[str, Any]) -> None:
    def unique(items: list[dict[str, Any]], key: str, label: str) -> None:
        values = [item[key] for item in items]
        duplicates = sorted(value for value, count in Counter(values).items() if count > 1)
        if duplicates:
            raise ContractError(f"Duplicate {label}: {', '.join(duplicates)}")

    unique(policy["modules"], "id", "module ids")
    unique(policy["modules"], "root", "module roots")
    unique(policy["hosts"], "id", "host ids")
    unique(policy["hosts"], "root", "host roots")
    unique(policy["projects"], "path", "project paths")

    module_ids = {item["id"] for item in policy["modules"]}
    host_ids = {item["id"] for item in policy["hosts"]}
    project_paths = {item["path"] for item in policy["projects"]}
    for value in (
        policy["roots"]["modules"],
        policy["roots"]["hosts"],
        *policy["projectSearchRoots"],
        *policy["structureSearchRoots"],
        policy["moduleContract"]["schema"],
        *(item["root"] for item in policy["modules"]),
        *(item.get("featureRoot", item["root"]) for item in policy["modules"]),
        *(item["root"] for item in policy["hosts"]),
        *(item["path"] for item in policy["projects"]),
    ):
        _repository_path(root, value)

    for module in policy["modules"]:
        feature_root = module.get("featureRoot")
        if feature_root and not (
            feature_root == module["root"] or feature_root.startswith(module["root"].rstrip("/") + "/")
        ):
            raise ContractError(f"Feature root must belong to module '{module['id']}': {feature_root}")

    for project in policy["projects"]:
        owner = project["owner"]
        known = module_ids if owner["kind"] == "module" else host_ids
        if owner["id"] not in known:
            raise ContractError(f"Project {project['path']} references unknown {owner['kind']} '{owner['id']}'")
        if owner["kind"] == "host" and project["role"] != "host":
            raise ContractError(f"Host-owned project must use role 'host': {project['path']}")
        if owner["kind"] == "module" and project["role"] == "host":
            raise ContractError(f"Module-owned project cannot use role 'host': {project['path']}")

    dependency_pairs: set[tuple[str, str]] = set()
    for dependency in policy["allowedProjectDependencies"]:
        pair = (dependency["from"], dependency["to"])
        if pair in dependency_pairs:
            raise ContractError(f"Duplicate allowed dependency: {pair[0]} -> {pair[1]}")
        dependency_pairs.add(pair)
        if pair[0] not in project_paths or pair[1] not in project_paths:
            raise ContractError(f"Allowed dependency references an undeclared project: {pair[0]} -> {pair[1]}")
        if pair[0] == pair[1]:
            raise ContractError(f"A project cannot depend on itself: {pair[0]}")

    for rule in policy.get("dependencyRules", []):
        for side in ("from", "to"):
            selector = rule[side]
            if not selector:
                raise ContractError(f"Dependency rule {side} selector cannot be empty")
            owner_id = selector.get("ownerId")
            if owner_id and owner_id not in module_ids | host_ids:
                raise ContractError(f"Dependency rule references unknown owner '{owner_id}'")
            if selector.get("ownerKind") == "module" and selector.get("ownerId") not in (None, *module_ids):
                raise ContractError(f"Dependency rule references unknown module '{selector['ownerId']}'")
            if selector.get("ownerKind") == "host" and selector.get("ownerId") not in (None, *host_ids):
                raise ContractError(f"Dependency rule references unknown host '{selector['ownerId']}'")


def _canonical_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()


def _load_base_policy(root: Path, policy_path: Path, base_ref: str | None) -> tuple[dict[str, Any] | None, str | None]:
    if not base_ref:
        return None, None
    try:
        relative = policy_path.resolve().relative_to(root).as_posix()
    except ValueError as error:
        raise ContractError("--base-ref requires the project policy to live inside the repository") from error
    try:
        revision = _git(root, "rev-parse", "--verify", f"{base_ref}^{{commit}}")
        content = _git(root, "show", f"{revision}:{relative}")
    except (OSError, subprocess.CalledProcessError) as error:
        raise ContractError(f"Cannot load base policy from {base_ref}: {error}") from error
    try:
        value = json.loads(content)
    except json.JSONDecodeError as error:
        raise ContractError(f"Base policy at {base_ref} is not valid JSON: {error}") from error
    if not isinstance(value, dict):
        raise ContractError(f"Base policy at {base_ref} must be a JSON object")
    return value, revision


def _revision(root: Path) -> str:
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        return f"{sha}+dirty" if dirty else sha
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate portable manifesto rules against declared and observed architecture."
    )
    parser.add_argument("--root", default=".", help="Repository root (default: current directory).")
    parser.add_argument(
        "--policy",
        default=".agentic/policies/architecture/project-policy.json",
        help="Project-specific architecture policy, relative to root.",
    )
    parser.add_argument(
        "--waivers",
        default=".agentic/policies/architecture/waivers.json",
        help="Explicit architecture waivers, relative to root.",
    )
    parser.add_argument(
        "--reviews",
        default=".agentic/policies/architecture/reviews.json",
        help="Accepted semantic reviews, relative to root.",
    )
    parser.add_argument(
        "--catalog",
        default="tools/architecture/rules.json",
        help="Portable rule catalog, relative to root.",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--output", help="Also write the structured JSON result to this path.")
    parser.add_argument(
        "--base-ref",
        help="Git revision used to detect architecture-policy growth (for example origin/main).",
    )
    parser.add_argument(
        "--write-review-template",
        help="Write a review template for unresolved REVIEW_REQUIRED findings.",
    )
    parser.add_argument(
        "--task-id",
        help="Retain the JSON result under .agentic/runtime/evidence/<task-id>/<revision>/.",
    )
    parser.add_argument(
        "--fail-on-review",
        action="store_true",
        help="Return a failing exit code when REVIEW_REQUIRED findings remain.",
    )
    parser.add_argument("--list-rules", action="store_true", help="Print the catalog and exit.")
    return parser


def run(arguments: list[str] | None = None) -> int:
    cli_arguments = list(arguments) if arguments is not None else sys.argv[1:]
    args = _build_parser().parse_args(cli_arguments)
    root = Path(args.root).resolve()
    try:
        if not root.is_dir():
            raise ContractError(f"Repository root does not exist: {root}")
        policy_path = _path(root, args.policy)
        waiver_path = _path(root, args.waivers)
        review_path = _path(root, args.reviews)
        catalog_path = _path(root, args.catalog)
        catalog = _load_catalog(catalog_path)

        if args.list_rules:
            for rule in catalog.values():
                mode = "automatic" if rule["automatic"] else "review-aware"
                print(f"{rule['id']}\t{mode}\t{rule['title']}")
            return 0

        policy = load_json(policy_path)
        waiver_document = load_json(waiver_path)
        review_document = load_json(review_path)
        policy_schema = root / ".agentic/contracts/schemas/architecture-policy.schema.json"
        waiver_schema = root / ".agentic/contracts/schemas/architecture-waivers.schema.json"
        review_schema = root / ".agentic/contracts/schemas/architecture-reviews.schema.json"
        result_schema = root / ".agentic/contracts/schemas/architecture-result.schema.json"
        _validate_with_schema(policy, policy_schema, "Architecture policy")
        _validate_with_schema(waiver_document, waiver_schema, "Architecture waivers")
        _validate_with_schema(review_document, review_schema, "Architecture reviews")
        _validate_policy_semantics(root, policy)
        base_policy, base_revision = _load_base_policy(root, policy_path, args.base_ref)
        if base_policy is not None:
            _validate_with_schema(base_policy, policy_schema, "Base architecture policy")
            _validate_policy_semantics(root, base_policy)

        observed = observe(policy["adapter"], root, policy)

        module_schema_path = _repository_path(root, policy["moduleContract"]["schema"])
        module_schema = load_json(module_schema_path)
        contracts: dict[str, dict[str, Any]] = {}
        contract_errors: dict[str, list[str]] = {}
        contract_file = policy["moduleContract"]["fileName"]
        for module_root in observed.modules:
            relative = f"{module_root}/{contract_file}"
            path = root / relative
            if not path.is_file():
                continue
            try:
                contract = load_yaml_subset(path)
            except ContractError as error:
                contract_errors[relative] = [str(error)]
                continue
            if not isinstance(contract, dict):
                contract_errors[relative] = ["Module contract root must be a mapping."]
                continue
            contracts[relative] = contract
            errors = validate_schema(contract, module_schema)
            if errors:
                contract_errors[relative] = errors

        context = ValidationContext(
            root=root,
            policy_path=policy_path,
            waiver_path=waiver_path,
            review_path=review_path,
            policy=policy,
            waivers=waiver_document["waivers"],
            reviews=review_document["reviews"],
            catalog=catalog,
            observed=observed,
            contracts=contracts,
            contract_errors=contract_errors,
            base_policy=base_policy,
            base_revision=base_revision,
        )
        findings = evaluate(context)
        counts = Counter(finding.status for finding in findings)
        planned_exit = 1 if counts["FAIL"] or (args.fail_on_review and counts["REVIEW_REQUIRED"]) else 0
        revision = _revision(root)
        report = {
            "tool": "agentic-architecture-validator",
            "toolVersion": __version__,
            "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "repositoryRoot": str(root),
            "repositoryRevision": revision,
            "project": policy["project"],
            "adapter": policy["adapter"],
            "policy": _display_path(root, policy_path),
            "waivers": _display_path(root, waiver_path),
            "reviews": _display_path(root, review_path),
            "policyDigest": _canonical_digest(policy),
            "waiverDigest": _canonical_digest(waiver_document),
            "reviewDigest": _canonical_digest(review_document),
            "catalogDigest": _canonical_digest({"version": 1, "rules": list(catalog.values())}),
            "observedDigest": _canonical_digest(observed.as_dict()),
            "summary": {status: counts[status] for status in STATUSES},
            "results": [finding.as_dict() for finding in findings],
        }
        if base_revision:
            report["baseRevision"] = base_revision
        result_errors = validate_schema(report, load_json(result_schema))
        if result_errors:
            raise ContractError("Validator produced an invalid result:\n  - " + "\n  - ".join(result_errors))

        serialized = json.dumps(report, indent=2, sort_keys=False) + "\n"
        if args.output:
            output = _path(root, args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(serialized, encoding="utf-8")
        if args.write_review_template:
            pending = []
            reviewable = [
                item for item in findings
                if item.status == "REVIEW_REQUIRED" and item.review_fingerprint
            ]
            for index, finding in enumerate(reviewable):
                pending.append({
                    "id": f"REVIEW-{index + 1:03d}",
                    "rule": finding.rule,
                    "scope": finding.scope,
                    "subjectFingerprint": finding.review_fingerprint,
                    "decision": "Replace with the accepted semantic judgment.",
                    "authority": "Replace with the accountable role or team.",
                    "authorizedBy": ["architecture/decisions/ADR-XXX.md"],
                    "reviewedAtRevision": revision,
                    "reviewWhen": ["The reviewed subject or its evidence changes."],
                })
            review_output = _path(root, args.write_review_template)
            review_output.parent.mkdir(parents=True, exist_ok=True)
            review_output.write_text(json.dumps({"version": 1, "reviews": pending}, indent=2) + "\n", encoding="utf-8")
        if args.task_id:
            if not re.fullmatch(r"[A-Za-z0-9._-]+", args.task_id):
                raise ContractError("--task-id may contain only letters, digits, dot, underscore, and hyphen")
            safe_revision = revision.replace("+", "-")
            evidence_dir = root / ".agentic/runtime/evidence" / args.task_id / safe_revision
            evidence_dir.mkdir(parents=True, exist_ok=True)
            (evidence_dir / "architecture.json").write_text(serialized, encoding="utf-8")
            manifest = {
                "taskId": args.task_id,
                "repositoryRevision": revision,
                "artifact": "architecture.json",
                "artifactDigest": _canonical_digest(report),
                "createdAt": report["generatedAt"],
                "tool": report["tool"],
                "toolVersion": report["toolVersion"],
                "arguments": cli_arguments,
                "exitCode": planned_exit,
                "result": "FAIL" if counts["FAIL"] else "REVIEW_REQUIRED" if counts["REVIEW_REQUIRED"] else "PASS",
            }
            (evidence_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if args.format == "json":
            print(serialized, end="")
        else:
            for finding in findings:
                waiver = f" waiver={finding.waiver}" if finding.waiver else ""
                review = f" review={finding.review}" if finding.review else ""
                print(f"[{finding.status}] {finding.rule} {finding.scope}{waiver}{review} - {finding.message}")
            summary = " ".join(f"{status}={counts[status]}" for status in STATUSES)
            print(f"Architecture validation: {summary}")

        return planned_exit
    except (ContractError, OSError, ValueError) as error:
        print(f"architecture validator configuration error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(run())
