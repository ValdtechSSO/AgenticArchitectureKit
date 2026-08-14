from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import __version__
from .adapters import observe
from .contracts import load_json, load_yaml_subset


INDEX_FILES = ("repository", "modules", "projects", "dependencies", "documents", "tests")
SOURCE_SUFFIXES = {".cs", ".py", ".fs", ".vb", ".js", ".jsx", ".ts", ".tsx", ".java", ".kt", ".go", ".rs"}


def _revision(root: Path) -> str:
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain"], cwd=root, check=True, capture_output=True, text=True
        ).stdout
        return f"{sha}+dirty" if dirty else sha
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _metadata(root: Path) -> dict[str, str]:
    return {
        "repositoryRevision": _revision(root),
        "generatorVersion": __version__,
        "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def _repo_path(root: Path, value: str) -> Path:
    path = (root / value).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as error:
        raise ValueError(f"Path escapes repository root: {value}") from error
    return path


def _source_files(root: Path, search_roots: list[str]) -> list[Path]:
    files: set[Path] = set()
    ignored = {".git", "bin", "obj", "node_modules", ".venv", "venv", "__pycache__"}
    for value in search_roots:
        base = _repo_path(root, value)
        candidates = [base] if base.is_file() else base.rglob("*") if base.is_dir() else []
        for path in candidates:
            if path.is_file() and path.suffix in SOURCE_SUFFIXES and not any(part in ignored for part in path.parts):
                files.add(path)
    return sorted(files)


def _contract(root: Path, module: dict[str, Any], file_name: str) -> dict[str, Any]:
    path = _repo_path(root, f"{module['root']}/{file_name}")
    if not path.is_file():
        return {}
    value = load_yaml_subset(path)
    return value if isinstance(value, dict) else {}


def build_index(root: Path, policy: dict[str, Any]) -> dict[str, dict[str, Any]]:
    root = root.resolve()
    observed = observe(policy["adapter"], root, policy)
    meta = _metadata(root)
    contract_file = policy["moduleContract"]["fileName"]
    module_items = []
    for module in policy["modules"]:
        contract = _contract(root, module, contract_file)
        module_items.append({
            "id": module["id"],
            "root": module["root"],
            "featureRoot": module.get("featureRoot"),
            "featureAreas": module.get("featureAreas", []),
            "purpose": contract.get("purpose"),
            "aliases": contract.get("intent", {}).get("aliases", []),
            "risk": contract.get("risk", {}).get("default"),
            "startingPaths": [value for value in (module.get("featureRoot"), module["root"]) if value],
            "provenance": "declared",
        })
    project_items = []
    declarations = {item["path"]: item for item in policy["projects"]}
    for project in observed.projects:
        declared = declarations.get(project.path, {})
        project_items.append({
            "path": project.path,
            "name": project.name,
            "owner": declared.get("owner"),
            "role": declared.get("role"),
            "references": list(project.references),
            "provenance": {"identity": "observed", "ownership": "declared"},
        })
    dependencies = [
        {"from": item.path, "to": target, "kind": "project-reference", "confidence": "exact", "provenance": "observed"}
        for item in observed.projects for target in item.references
    ] + [
        {
            "from": item.source_namespace,
            "to": item.target_namespace,
            "sourcePath": item.source_path,
            "kind": item.kind,
            "confidence": item.confidence,
            "provenance": "observed",
        }
        for item in observed.source_dependencies
    ]
    documents = sorted(
        path.relative_to(root).as_posix()
        for directory in ("architecture", "domain", "docs")
        for path in (_repo_path(root, directory).rglob("*.md") if _repo_path(root, directory).is_dir() else [])
    )
    tests = [
        path.relative_to(root).as_posix()
        for path in _source_files(root, policy["projectSearchRoots"])
        if any(part.casefold() in {"test", "tests"} or "test" in part.casefold() for part in path.parts)
    ]
    repository = {
        **meta,
        "project": policy["project"],
        "adapter": policy["adapter"],
        "policy": ".agentic/policies/architecture/project-policy.json",
        "counts": {
            "modules": len(observed.modules),
            "hosts": len(observed.hosts),
            "projects": len(observed.projects),
            "sourceDependencies": len(observed.source_dependencies),
        },
    }
    return {
        "repository": repository,
        "modules": {**meta, "items": module_items},
        "projects": {**meta, "items": project_items},
        "dependencies": {**meta, "items": dependencies},
        "documents": {**meta, "items": [{"path": item, "provenance": "observed"} for item in documents]},
        "tests": {**meta, "items": [{"path": item, "provenance": "observed"} for item in tests]},
    }


def write_index(root: Path, policy: dict[str, Any], output: str = ".agentic/generated/index") -> dict[str, dict[str, Any]]:
    root = root.resolve()
    documents = build_index(root, policy)
    target = _repo_path(root, output)
    target.mkdir(parents=True, exist_ok=True)
    for name, document in documents.items():
        (target / f"{name}.json").write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return documents


def locate(root: Path, policy: dict[str, Any], query: str) -> dict[str, Any]:
    root = root.resolve()
    terms = {term for term in re.findall(r"[\w-]+", query.casefold()) if len(term) > 1}
    modules = build_index(root, policy)["modules"]["items"]
    matches = []
    for module in modules:
        haystack = " ".join(str(value) for value in (module["id"], module["purpose"], *module["aliases"])).casefold()
        score = sum(3 if term == module["id"].casefold() else 1 for term in terms if term in haystack)
        if score:
            matches.append({**module, "score": score})
    return {**_metadata(root), "query": query, "matches": sorted(matches, key=lambda item: (-item["score"], item["id"]))}


def references(root: Path, policy: dict[str, Any], symbol: str, tests_only: bool = False) -> dict[str, Any]:
    root = root.resolve()
    pattern = re.compile(rf"\b{re.escape(symbol)}\b")
    matches = []
    for path in _source_files(root, policy["projectSearchRoots"]):
        relative = path.relative_to(root).as_posix()
        if tests_only and not any("test" in part.casefold() for part in path.parts):
            continue
        if path.stem == symbol:
            matches.append({
                "path": relative,
                "line": 1,
                "excerpt": path.name,
                "provenance": "observed",
                "confidence": "exact-file-name",
            })
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if pattern.search(line):
                matches.append({
                    "path": relative,
                    "line": number,
                    "excerpt": line.strip()[:240],
                    "provenance": "observed",
                    "confidence": "exact-text-match",
                })
    return {**_metadata(root), "symbol": symbol, "matches": matches}


def impact(root: Path, policy: dict[str, Any], target_path: str) -> dict[str, Any]:
    root = root.resolve()
    normalized = _repo_path(root, target_path).relative_to(root).as_posix()
    index = build_index(root, policy)
    projects = index["projects"]["items"]
    owners = [item for item in projects if normalized == item["path"] or normalized.startswith(str(Path(item["path"]).parent) + "/")]
    owner_paths = {item["path"] for item in owners}
    reverse = [item for item in index["dependencies"]["items"] if item["to"] in owner_paths]
    modules = [item for item in index["modules"]["items"] if normalized == item["root"] or normalized.startswith(item["root"] + "/")]
    return {
        **_metadata(root),
        "path": normalized,
        "owners": owners,
        "modules": modules,
        "directConsumers": reverse,
        "provenance": {"owners": "declared-and-observed", "consumers": "observed"},
    }


def load_policy(root: Path, value: str) -> dict[str, Any]:
    path = Path(value)
    return load_json(path if path.is_absolute() else root / path)
