from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .adapters import observe
from .contracts import ContractError
from .resources import files as package_files, read_json


_POLICY_SCHEMA = "https://raw.githubusercontent.com/ValdtechSSO/AgenticArchitectureKit/v0.4.6/src/agentic_architecture_kit/data/schemas/architecture-policy.schema.json"
_TECHNICAL_MODULE_NAMES = [
    "Git", "Providers", "Repositories", "Validation", "Services", "Infrastructure",
]
_FORBIDDEN_DIRECTORY_NAMES = ["Services", "Managers", "Helpers", "Utils", "Common"]


def _write_new(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def _json(value: object) -> str:
    return json.dumps(value, indent=2) + "\n"


def _init_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Initialize project-owned architecture governance and an observed policy proposal.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--codeowner", required=True, help="GitHub CODEOWNER principal, for example @team/architecture.")
    parser.add_argument("--authority-id", default="architecture-maintainers")
    parser.add_argument(
        "--authority-mode",
        choices=("team", "solo-maintainer"),
        default="team",
        help="Team review or explicit single-maintainer attestation governance.",
    )
    parser.add_argument("--protected-branch", default="main")
    parser.add_argument(
        "--adapter",
        choices=("auto", "dotnet", "python"),
        default="auto",
        help="Technology adapter. Auto-detected by default; required explicitly before a new repository contains technology artifacts.",
    )
    return parser


def _relative(root: Path, path: Path) -> str:
    value = path.resolve().relative_to(root.resolve()).as_posix()
    return value or "."


def _slug(value: str, fallback: str) -> str:
    result = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return result or fallback


def _unique_id(value: str, fallback: str, used: set[str]) -> str:
    base = _slug(value, fallback)
    candidate = base
    suffix = 2
    while candidate in used:
        candidate = f"{base}-{suffix}"
        suffix += 1
    used.add(candidate)
    return candidate


def _technology_files(root: Path, pattern: str) -> list[Path]:
    return sorted(
        path
        for path in root.rglob(pattern)
        if not any(part in (".git", ".agentic", ".venv", "venv", "bin", "obj", "node_modules") for part in path.parts)
    )


def _detect_adapter(root: Path, requested: str) -> str:
    if requested != "auto":
        return requested
    if _technology_files(root, "*.csproj"):
        return "dotnet"
    if (root / "pyproject.toml").is_file() or _technology_files(root, "*.py"):
        return "python"
    raise ContractError(
        "Cannot infer a technology adapter from this repository yet; rerun init with --adapter dotnet or --adapter python."
    )


def _search_roots(root: Path, paths: list[Path], include_root_file: bool = False) -> list[str]:
    values: set[str] = set()
    for path in paths:
        relative = path.relative_to(root)
        if len(relative.parts) == 1 and include_root_file:
            values.add(".")
        elif relative.parts:
            values.add(relative.parts[0])
    return sorted(values) or ["."]


def _common_parent(root: Path, paths: list[Path]) -> str:
    if not paths:
        return "."
    common = Path(os.path.commonpath([str(path.parent.resolve()) for path in paths]))
    if len(paths) == 1 and common != root.resolve():
        common = common.parent
    try:
        return _relative(root, common)
    except ValueError:
        return "."


def _seed_policy(root: Path, adapter: str) -> dict[str, Any]:
    if adapter == "dotnet":
        projects = _technology_files(root, "*.csproj")
        project_roots = _search_roots(root, projects)
        conventional_modules = next(
            (path for path in (root / "src/Modules", root / "Modules") if path.is_dir()),
            None,
        )
        conventional_hosts = next(
            (path for path in (root / "src/Hosts", root / "Hosts") if path.is_dir()),
            None,
        )
        modules_root = _relative(root, conventional_modules) if conventional_modules else _common_parent(root, projects)
        hosts_root = _relative(root, conventional_hosts) if conventional_hosts else ("src/Hosts" if (root / "src").is_dir() else "Hosts")
        adapter_config: dict[str, Any] = {}
    else:
        projects = _technology_files(root, "pyproject.toml")
        project_roots = _search_roots(root, projects, include_root_file=True)
        package_root = root / "src" if (root / "src").is_dir() else root
        modules_root = _relative(root, package_root)
        host_root = next(
            (
                path
                for path in (root / "tools", root / "scripts")
                if path.is_dir() and any(item.suffix == ".py" for item in path.iterdir() if item.is_file())
            ),
            None,
        )
        hosts_root = _relative(root, host_root) if host_root else ("src/Hosts" if package_root.name == "src" else "Hosts")
        adapter_config = {"packageRoots": [modules_root]}
        if "." not in project_roots and (root / "pyproject.toml").is_file():
            project_roots.insert(0, ".")

    structure_roots = [value for value in project_roots if value != "."]
    if not structure_roots:
        structure_roots = [modules_root if modules_root != "." else "."]
    return {
        "adapter": adapter,
        "adapterConfig": adapter_config,
        "roots": {"modules": modules_root, "hosts": hosts_root},
        "projectSearchRoots": project_roots,
        "structureSearchRoots": structure_roots,
    }


def _root_owner_for(
    path: str,
    modules: list[dict[str, Any]],
    hosts: list[dict[str, Any]],
) -> tuple[str, str] | None:
    candidates: list[tuple[int, str, str]] = []
    for kind, declarations in (("module", modules), ("host", hosts)):
        for item in declarations:
            root = item["root"].rstrip("/")
            if root == "." or path == root or path.startswith(root + "/"):
                candidates.append((len(root), kind, item["id"]))
    if candidates:
        _, kind, owner_id = max(candidates)
        return kind, owner_id
    return None


def _owner_for(path: str, modules: list[dict[str, Any]], hosts: list[dict[str, Any]]) -> tuple[str, str]:
    root_owner = _root_owner_for(path, modules, hosts)
    if root_owner:
        return root_owner
    if modules:
        return "module", modules[0]["id"]
    if hosts:
        return "host", hosts[0]["id"]
    raise ContractError(f"Observed project has no module or host owner candidate: {path}")


def _common_namespace(namespaces: set[str]) -> str | None:
    if not namespaces:
        return None
    parts = [namespace.split(".") for namespace in sorted(namespaces)]
    common: list[str] = []
    for values in zip(*parts):
        if len(set(values)) != 1:
            break
        common.append(values[0])
    return ".".join(common) or None


def _observed_namespace_patterns(observed: set[str], explicit_roots: set[str]) -> list[str]:
    uncovered = {
        namespace
        for namespace in observed
        if not any(namespace == root or namespace.startswith(root + ".") for root in explicit_roots)
    }
    roots = set(explicit_roots)
    common = _common_namespace(uncovered)
    if common and (len(common.split(".")) > 1 or len(uncovered) == 1):
        roots.add(common)
    elif uncovered:
        roots.update(uncovered)
    minimal_roots = {
        root
        for root in roots
        if not any(root != other and root.startswith(other + ".") for other in roots)
    }
    return sorted({pattern for root in minimal_roots for pattern in (root, root + ".*")})


def _observed_policy(root: Path, adapter: str) -> tuple[dict[str, Any], dict[str, int]]:
    seed = _seed_policy(root, adapter)
    observed = observe(adapter, root, {
        **seed,
        "modules": [],
        "hosts": [],
    })
    used_ids: set[str] = set()
    modules: list[dict[str, Any]] = []
    for module_root in observed.modules:
        module_id = _unique_id(Path(module_root).name, "repository", used_ids)
        item: dict[str, Any] = {
            "id": module_id,
            "root": module_root,
            "namespacePatterns": [Path(module_root).name.replace("-", "_"), Path(module_root).name.replace("-", "_") + ".*"],
        }
        features = root / module_root / "Features"
        if features.is_dir():
            item["featureRoot"] = _relative(root, features)
            item["featureAreas"] = sorted(path.name for path in features.iterdir() if path.is_dir())
        modules.append(item)

    hosts: list[dict[str, Any]] = []
    for host_root in observed.hosts:
        host_id = _unique_id(Path(host_root).stem, "host", used_ids)
        prefix = host_root.rstrip("/") + "/"
        if (root / host_root).is_file():
            sources = [Path(host_root).name]
        else:
            sources = sorted(path[len(prefix):] for path in observed.source_files if path.startswith(prefix))
        hosts.append({
            "id": host_id,
            "root": host_root,
            "allowedSourcePatterns": sources,
            "namespacePatterns": [Path(host_root).stem.replace("-", "_"), Path(host_root).stem.replace("-", "_") + ".*"],
        })

    projects: list[dict[str, Any]] = []
    project_owners: dict[str, tuple[str, str]] = {}
    for project in observed.projects:
        kind, owner_id = _owner_for(project.path, modules, hosts)
        project_owners[project.path] = (kind, owner_id)
        projects.append({
            "path": project.path,
            "name": project.name,
            "owner": {"kind": kind, "id": owner_id},
            "role": project.role_hint or ("host" if kind == "host" else "application"),
        })

    if adapter == "dotnet":
        test_project_paths = {
            project.path
            for project in observed.projects
            if project.role_hint == "test"
        }
        for kind, declarations in (("module", modules), ("host", hosts)):
            for declaration in declarations:
                owned_projects = [
                    item
                    for item in observed.projects
                    if project_owners.get(item.path) == (kind, declaration["id"])
                    and item.path not in test_project_paths
                ]
                explicit_roots = {
                    project.root_namespace
                    for project in owned_projects
                    if project.root_namespace
                }
                observed_namespaces = {
                    item.namespace
                    for item in observed.source_namespaces
                    if item.project_path not in test_project_paths
                    and (
                        _root_owner_for(item.source_path, modules, hosts)
                        or project_owners.get(item.project_path or "")
                    ) == (kind, declaration["id"])
                }
                patterns = _observed_namespace_patterns(observed_namespaces, explicit_roots)
                if patterns:
                    declaration["namespacePatterns"] = patterns
                else:
                    declaration.pop("namespacePatterns", None)

    dependencies = [
        {"from": project.path, "to": target}
        for project in observed.projects
        for target in project.references
        if target in project_owners
    ]
    project_name = root.name
    if adapter == "python" and observed.projects:
        project_name = observed.projects[0].name
    policy = {
        "$schema": _POLICY_SCHEMA,
        "version": 1,
        "project": _slug(project_name, "project"),
        **seed,
        "moduleContract": {
            "fileName": "module.contract.yml",
            "schema": "package:module-contract.schema.json",
            "forbiddenStructuralFields": ["paths", "entrypoints", "handlers", "classes", "tests", "entities_read", "entities_written", "routes"],
        },
        "technicalModuleNames": _TECHNICAL_MODULE_NAMES,
        "forbiddenDirectoryNames": _FORBIDDEN_DIRECTORY_NAMES,
        "modules": modules,
        "hosts": hosts,
        "projects": projects,
        "allowedProjectDependencies": dependencies,
        "dependencyRules": [],
    }
    return policy, {
        "modules": len(modules),
        "hosts": len(hosts),
        "projects": len(projects),
        "dependencies": len(dependencies),
    }


def _initialization_plan(
    root: Path,
    codeowner: str,
    authority_id: str = "architecture-maintainers",
    protected_branch: str = "main",
    adapter: str = "auto",
    authority_mode: str = "team",
) -> dict[str, Any]:
    root = root.resolve()
    if not root.is_dir():
        raise ContractError(f"Repository root does not exist: {root}")
    if not codeowner.startswith("@"):
        raise ContractError("codeowner must be a GitHub user or team beginning with @")
    if authority_mode not in ("team", "solo-maintainer"):
        raise ContractError("authority_mode must be team or solo-maintainer")
    policy_path = root / ".agentic/policies/architecture/project-policy.json"
    if policy_path.is_file():
        try:
            policy = json.loads(policy_path.read_text(encoding="utf-8"))
            selected_adapter = policy["adapter"]
            observation = {
                "modules": len(policy["modules"]),
                "hosts": len(policy["hosts"]),
                "projects": len(policy["projects"]),
                "dependencies": len(policy["allowedProjectDependencies"]),
            }
        except (json.JSONDecodeError, KeyError, TypeError) as error:
            raise ContractError(f"Existing project policy cannot be preserved because it is invalid: {error}") from error
        proposal_basis = "existing"
    else:
        selected_adapter = _detect_adapter(root, adapter)
        policy, observation = _observed_policy(root, selected_adapter)
        proposal_basis = "observed"
    toolchain = {
        "$schema": "https://raw.githubusercontent.com/ValdtechSSO/AgenticArchitectureKit/v0.4.6/src/agentic_architecture_kit/data/schemas/toolchain.schema.json",
        "version": 1,
        "distribution": "agentic-architecture-kit",
        "toolVersion": __version__,
        "catalogVersion": 2,
        "extensions": [],
    }
    authorities = read_json("data/templates/project/authorities.json")
    authorities["enforcement"]["mode"] = authority_mode
    if authority_mode == "solo-maintainer":
        authorities["enforcement"]["requirements"] = [
            "pull-request",
            "no-direct-push",
            "required-status-checks",
        ]
    authorities["authorities"][0]["id"] = authority_id
    authorities["authorities"][0]["principals"] = [codeowner]
    authorities["enforcement"]["protectedBranches"] = [protected_branch]
    documents = {
        root / ".agentic/toolchain.json": _json(toolchain),
        policy_path: _json(policy),
        root / ".agentic/policies/architecture/waivers.json": _json(read_json("data/templates/project/waivers.json")),
        root / ".agentic/policies/architecture/reviews.json": _json(read_json("data/templates/project/reviews.json")),
        root / ".agentic/policies/architecture/authorities.json": _json(authorities),
    }
    codeowners = root / ".github/CODEOWNERS"
    return {
        "rootPath": root,
        "documents": documents,
        "codeownersPath": codeowners,
        "codeownersContent": "# Architecture governance\n" f"* {codeowner}\n",
        "root": str(root),
        "toolVersion": __version__,
        "adapter": selected_adapter,
        "policyProposal": {"basis": proposal_basis, **observation},
    }


def preview_initialization(
    root: Path,
    codeowner: str,
    authority_id: str = "architecture-maintainers",
    protected_branch: str = "main",
    adapter: str = "auto",
    authority_mode: str = "team",
) -> dict[str, Any]:
    plan = _initialization_plan(
        root,
        codeowner,
        authority_id,
        protected_branch,
        adapter,
        authority_mode,
    )
    root_path = plan["rootPath"]
    paths = [*plan["documents"], plan["codeownersPath"]]
    return {
        "root": plan["root"],
        "toolVersion": plan["toolVersion"],
        "adapter": plan["adapter"],
        "policyProposal": plan["policyProposal"],
        "projectPolicy": json.loads(plan["documents"][root_path / ".agentic/policies/architecture/project-policy.json"]),
        "planned": [path.relative_to(root_path).as_posix() for path in paths if not path.exists()],
        "existing": [path.relative_to(root_path).as_posix() for path in paths if path.exists()],
    }


def initialize(
    root: Path,
    codeowner: str,
    authority_id: str = "architecture-maintainers",
    protected_branch: str = "main",
    adapter: str = "auto",
    authority_mode: str = "team",
) -> dict[str, Any]:
    plan = _initialization_plan(
        root,
        codeowner,
        authority_id,
        protected_branch,
        adapter,
        authority_mode,
    )
    root = plan["rootPath"]
    documents = plan["documents"]
    created = [path.relative_to(root).as_posix() for path, content in documents.items() if _write_new(path, content)]
    codeowners = plan["codeownersPath"]
    if not codeowners.exists():
        created.append(codeowners.relative_to(root).as_posix())
        _write_new(codeowners, plan["codeownersContent"])
    return {
        "root": plan["root"],
        "toolVersion": plan["toolVersion"],
        "adapter": plan["adapter"],
        "policyProposal": plan["policyProposal"],
        "created": created,
        "next": [
            "Run aak core and read the complete preventive decision context.",
            "Run aak guide bootstrap and follow the version-matched operational procedure.",
            "Review the observed project-policy.json proposal and remove accidental or unjustified boundaries.",
            "Create module contracts and local AGENTS.md files only for actual modules.",
            "Configure protected branches according to aak guide github-governance.",
            "Run the pinned distribution with: aak validate --fail-on-review.",
        ],
    }


def run(arguments: list[str] | None = None) -> int:
    args = _init_parser().parse_args(arguments)
    try:
        result = initialize(
            Path(args.root),
            args.codeowner,
            args.authority_id,
            args.protected_branch,
            args.adapter,
            args.authority_mode,
        )
        print(_json(result), end="")
        return 0
    except (ContractError, OSError, ValueError) as error:
        print(f"architecture init error: {error}", file=sys.stderr)
        return 2


def _export_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export a versioned offline package payload.")
    parser.add_argument("--output", required=True)
    return parser


def _copy_package_tree(source: Any, destination: Path, target: Path, files: list[dict[str, str]]) -> None:
    for item in source.iterdir():
        if item.name == "__pycache__" or item.name.endswith((".pyc", ".pyo")):
            continue
        item_destination = destination / item.name
        if item.is_dir():
            item_destination.mkdir(parents=True, exist_ok=True)
            _copy_package_tree(item, item_destination, target, files)
            continue
        item_destination.parent.mkdir(parents=True, exist_ok=True)
        payload = item.read_bytes()
        item_destination.write_bytes(payload)
        files.append({
            "path": item_destination.relative_to(target).as_posix(),
            "sha256": hashlib.sha256(payload).hexdigest(),
        })


def export_payload(output: Path) -> dict[str, Any]:
    output = output.resolve()
    target = output / f"agentic-architecture-kit-{__version__}"
    if target.exists():
        raise ContractError(f"target already exists: {target}")
    target.mkdir(parents=True)
    files: list[dict[str, str]] = []
    destination = target / "agentic_architecture_kit"
    destination.mkdir(parents=True)
    _copy_package_tree(package_files(), destination, target, files)
    manifest = {
        "distribution": "agentic-architecture-kit",
        "toolVersion": __version__,
        "entrypoint": "PYTHONPATH=. python3 -m agentic_architecture_kit.cli",
        "files": sorted(files, key=lambda item: item["path"]),
    }
    (target / "OFFLINE-MANIFEST.json").write_text(_json(manifest), encoding="utf-8")
    return {
        "output": str(target),
        "fileCount": len(files),
        "distribution": manifest["distribution"],
        "toolVersion": manifest["toolVersion"],
    }


def export_offline(arguments: list[str] | None = None) -> int:
    args = _export_parser().parse_args(arguments)
    try:
        print(_json(export_payload(Path(args.output))), end="")
        return 0
    except (ContractError, OSError, ValueError) as error:
        print(f"offline export error: {error}", file=sys.stderr)
        return 2
