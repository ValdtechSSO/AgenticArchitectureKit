from __future__ import annotations

import argparse
import contextlib
import io
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from . import __version__
from . import validate_cli
from .context import load_policy, write_index
from .contracts import ContractError
from .init_cli import initialize, preview_initialization
from .resources import read_text as read_bundled_text


_POLICY = ".agentic/policies/architecture/project-policy.json"
_TOOLCHAIN = ".agentic/toolchain.json"
_GITHUB_WORKFLOW = ".github/workflows/architecture.yml"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Adopt Agentic Architecture Kit in an existing repository.",
    )
    parser.add_argument("--root", default=".")
    parser.add_argument("--codeowner", required=True, help="GitHub CODEOWNER principal beginning with @.")
    parser.add_argument("--authority-id", default="architecture-maintainers")
    parser.add_argument(
        "--authority-mode",
        choices=("team", "solo-maintainer"),
        default="team",
    )
    parser.add_argument("--protected-branch", default="main")
    parser.add_argument("--adapter", choices=("auto", "dotnet", "python"), default="auto")
    parser.add_argument("--ci", choices=("none", "github"), default="none")
    parser.add_argument("--base-ref", help="Optional existing AAK baseline for comparative validation.")
    parser.add_argument("--dry-run", action="store_true", help="Report planned writes without changing the repository.")
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Allow adoption to be mixed with existing uncommitted work.",
    )
    parser.add_argument("--output", help="Also write the adoption report to this path after applying changes.")
    return parser


def _git(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )


def _preflight(root: Path) -> dict[str, Any]:
    repository = _git(root, "rev-parse", "--is-inside-work-tree")
    if repository.returncode != 0 or repository.stdout.strip() != "true":
        return {
            "gitRepository": False,
            "revision": "unknown",
            "branch": None,
            "dirty": False,
            "changedPaths": [],
        }
    revision = _git(root, "rev-parse", "HEAD")
    branch = _git(root, "branch", "--show-current")
    status = _git(root, "status", "--porcelain")
    changed = [line[3:] for line in status.stdout.splitlines() if len(line) > 3]
    return {
        "gitRepository": True,
        "revision": revision.stdout.strip() if revision.returncode == 0 else "unknown",
        "branch": branch.stdout.strip() or None,
        "dirty": bool(changed),
        "changedPaths": changed,
    }


def _is_configured(root: Path) -> bool:
    return (root / _TOOLCHAIN).is_file() or (root / _POLICY).is_file()


def _output_path(root: Path, output: str | None) -> Path | None:
    if output is None:
        return None
    path = Path(output)
    path = path if path.is_absolute() else root / path
    try:
        path = path.resolve()
        path.relative_to(root)
    except ValueError as error:
        raise ContractError("--output must stay inside the repository") from error
    return path


def _validation(root: Path, base_ref: str | None = None) -> dict[str, Any]:
    arguments = ["--root", str(root), "--format", "json", "--fail-on-review"]
    if base_ref:
        arguments.extend(("--base-ref", base_ref))
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        exit_code = validate_cli.run(arguments)
    if exit_code == 2:
        return {
            "status": "CONFIGURATION_ERROR",
            "exitCode": exit_code,
            "error": stderr.getvalue().strip(),
        }
    try:
        report = json.loads(stdout.getvalue())
    except json.JSONDecodeError as error:
        raise ContractError(f"Validator did not return a JSON adoption result: {error}") from error
    findings = [
        {
            "rule": item["rule"],
            "status": item["status"],
            "scope": item["scope"],
            "message": item["message"],
            "reference": item["reference"],
        }
        for item in report["results"]
        if item["status"] in ("FAIL", "WAIVED", "REVIEW_REQUIRED")
    ]
    return {
        "status": "PASS" if exit_code == 0 else "ACTION_REQUIRED",
        "exitCode": exit_code,
        "summary": report["summary"],
        "findings": findings,
    }


def _github_ci_plan(root: Path) -> dict[str, Any]:
    path = root / _GITHUB_WORKFLOW
    if not path.exists():
        return {"provider": "github", "path": _GITHUB_WORKFLOW, "status": "PLANNED"}
    content = path.read_text(encoding="utf-8", errors="replace")
    status = "EXISTING" if "aak validate" in content else "REVIEW_REQUIRED"
    result = {"provider": "github", "path": _GITHUB_WORKFLOW, "status": status}
    if status == "REVIEW_REQUIRED":
        result["message"] = "Existing workflow is preserved but does not contain an AAK validation gate."
    return result


def _ensure_github_ci(root: Path) -> dict[str, Any]:
    plan = _github_ci_plan(root)
    if plan["status"] != "PLANNED":
        return plan
    path = root / _GITHUB_WORKFLOW
    path.parent.mkdir(parents=True, exist_ok=True)
    template = read_bundled_text("data/templates/project/github-architecture.yml")
    path.write_text(template.replace("{tool-version}", __version__), encoding="utf-8")
    return {**plan, "status": "CREATED"}


def _required_actions(
    root: Path,
    proposal_basis: str,
    ci: dict[str, Any],
    policy: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    if proposal_basis == "observed":
        actions.append({
            "kind": "SEMANTIC_REVIEW",
            "scope": _POLICY,
            "message": "Review the observed policy and remove accidental or unjustified boundaries.",
        })
    if not (root / "AGENTS.md").is_file():
        actions.append({
            "kind": "PROJECT_CONTEXT",
            "scope": "AGENTS.md",
            "message": "Create the repository agent entry point from current project facts.",
        })
    policy_path = root / _POLICY
    if policy is None and policy_path.is_file():
        policy = load_policy(root, _POLICY)
    if policy is not None:
        contract_name = policy["moduleContract"]["fileName"]
        for module in policy["modules"]:
            module_root = root / module["root"]
            for name in ("AGENTS.md", contract_name):
                path = module_root / name
                if not path.is_file():
                    actions.append({
                        "kind": "MODULE_CONTEXT",
                        "scope": path.relative_to(root).as_posix(),
                        "message": "Create this artifact from decided module semantics; do not use placeholders.",
                    })
    if ci.get("status") == "REVIEW_REQUIRED":
        actions.append({
            "kind": "CI_INTEGRATION",
            "scope": str(ci["path"]),
            "message": str(ci["message"]),
        })
    if ci.get("provider") == "github":
        actions.append({
            "kind": "PLATFORM_ENFORCEMENT",
            "scope": ".agentic/policies/architecture/authorities.json",
            "message": "Configure protected branches and required checks using `aak guide github-governance`.",
        })
    return actions


def adopt(
    root: Path,
    codeowner: str,
    authority_id: str = "architecture-maintainers",
    protected_branch: str = "main",
    adapter: str = "auto",
    authority_mode: str = "team",
    ci_provider: str = "none",
    base_ref: str | None = None,
    dry_run: bool = False,
    allow_dirty: bool = False,
    output: str | None = None,
) -> tuple[dict[str, Any], int]:
    root = root.resolve()
    if not root.is_dir():
        raise ContractError(f"Repository root does not exist: {root}")
    if ci_provider not in ("none", "github"):
        raise ContractError("ci_provider must be none or github")
    report_path = _output_path(root, output)
    preflight = _preflight(root)
    if preflight["dirty"] and not allow_dirty and not dry_run:
        raise ContractError(
            "Repository has uncommitted changes; commit or stash them, or rerun with --allow-dirty."
        )

    preview = preview_initialization(
        root,
        codeowner,
        authority_id,
        protected_branch,
        adapter,
        authority_mode,
    )
    baseline = _validation(root, base_ref) if _is_configured(root) else {
        "status": "NOT_CONFIGURED",
        "exitCode": None,
    }
    ci = _github_ci_plan(root) if ci_provider == "github" else {
        "provider": "none",
        "status": "SKIPPED",
    }
    if dry_run:
        report = {
            "tool": "agentic-architecture-adoption",
            "toolVersion": __version__,
            "root": str(root),
            "dryRun": True,
            "preflight": preflight,
            "baselineValidation": baseline,
            "initialization": preview,
            "ci": ci,
            "contextIndex": {"status": "PLANNED", "output": ".agentic/generated/index"},
            "validation": {"status": "PLANNED"},
            "requiredActions": _required_actions(
                root,
                preview["policyProposal"]["basis"],
                ci,
                preview["projectPolicy"],
            ),
            "result": "PLAN",
        }
        return report, 0
    if baseline["status"] == "CONFIGURATION_ERROR":
        report = {
            "tool": "agentic-architecture-adoption",
            "toolVersion": __version__,
            "root": str(root),
            "dryRun": False,
            "preflight": preflight,
            "baselineValidation": baseline,
            "initialization": preview,
            "ci": ci,
            "contextIndex": {"status": "SKIPPED"},
            "validation": {"status": "SKIPPED"},
            "requiredActions": [],
            "result": "CONFIGURATION_ERROR",
        }
        return report, 2

    initialization = initialize(
        root,
        codeowner,
        authority_id,
        protected_branch,
        adapter,
        authority_mode,
    )
    ci = _ensure_github_ci(root) if ci_provider == "github" else ci
    validation = _validation(root, base_ref)
    context_result: dict[str, Any]
    try:
        policy = load_policy(root, _POLICY)
        generated = write_index(root, policy)
        context_result = {
            "status": "GENERATED",
            "output": ".agentic/generated/index",
            "files": [f"{name}.json" for name in sorted(generated)],
        }
    except (ContractError, OSError, ValueError, KeyError) as error:
        context_result = {"status": "CONFIGURATION_ERROR", "error": str(error)}
    required_actions = _required_actions(
        root,
        initialization["policyProposal"]["basis"],
        ci,
        preview["projectPolicy"],
    )
    exit_code = 2 if validation["status"] == "CONFIGURATION_ERROR" or context_result["status"] == "CONFIGURATION_ERROR" else int(validation["exitCode"])
    result = "CONFIGURATION_ERROR" if exit_code == 2 else "ACTION_REQUIRED" if exit_code == 1 else "PASS"
    report = {
        "tool": "agentic-architecture-adoption",
        "toolVersion": __version__,
        "root": str(root),
        "dryRun": False,
        "preflight": preflight,
        "baselineValidation": baseline,
        "initialization": initialization,
        "ci": ci,
        "contextIndex": context_result,
        "validation": validation,
        "requiredActions": required_actions,
        "result": result,
    }
    if report_path is not None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report, exit_code


def run(arguments: list[str] | None = None) -> int:
    args = _parser().parse_args(arguments)
    try:
        report, exit_code = adopt(
            Path(args.root),
            args.codeowner,
            args.authority_id,
            args.protected_branch,
            args.adapter,
            args.authority_mode,
            args.ci,
            args.base_ref,
            args.dry_run,
            args.allow_dirty,
            args.output,
        )
        print(json.dumps(report, indent=2) + "\n", end="")
        return exit_code
    except (ContractError, OSError, ValueError) as error:
        print(f"architecture adoption error: {error}", file=sys.stderr)
        return 2
