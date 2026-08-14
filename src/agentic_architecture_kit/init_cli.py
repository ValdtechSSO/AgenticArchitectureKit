from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .contracts import ContractError
from .resources import files as package_files, read_json


def _write_new(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def _json(value: object) -> str:
    return json.dumps(value, indent=2) + "\n"


def _init_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Initialize only project-owned architecture governance files.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--codeowner", required=True, help="GitHub CODEOWNER principal, for example @team/architecture.")
    parser.add_argument("--authority-id", default="architecture-maintainers")
    parser.add_argument("--protected-branch", default="main")
    return parser


def initialize(
    root: Path,
    codeowner: str,
    authority_id: str = "architecture-maintainers",
    protected_branch: str = "main",
) -> dict[str, Any]:
    root = root.resolve()
    if not root.is_dir():
        raise ContractError(f"Repository root does not exist: {root}")
    if not codeowner.startswith("@"):
        raise ContractError("codeowner must be a GitHub user or team beginning with @")
    toolchain = {
            "$schema": "https://raw.githubusercontent.com/ValdtechSSO/AgenticArchitectureKit/v0.4.0/src/agentic_architecture_kit/data/schemas/toolchain.schema.json",
            "version": 1,
            "distribution": "agentic-architecture-kit",
            "toolVersion": __version__,
            "catalogVersion": 2,
            "extensions": [],
    }
    authorities = read_json("data/templates/project/authorities.json")
    authorities["authorities"][0]["id"] = authority_id
    authorities["authorities"][0]["principals"] = [codeowner]
    authorities["enforcement"]["protectedBranches"] = [protected_branch]
    documents = {
        root / ".agentic/toolchain.json": _json(toolchain),
        root / ".agentic/policies/architecture/waivers.json": _json(read_json("data/templates/project/waivers.json")),
        root / ".agentic/policies/architecture/reviews.json": _json(read_json("data/templates/project/reviews.json")),
        root / ".agentic/policies/architecture/authorities.json": _json(authorities),
    }
    created = [path.relative_to(root).as_posix() for path, content in documents.items() if _write_new(path, content)]
    codeowners = root / ".github/CODEOWNERS"
    if not codeowners.exists():
        created.append(codeowners.relative_to(root).as_posix())
        _write_new(
            codeowners,
            "# Architecture governance\n"
            f"/.agentic/policies/architecture/ {codeowner}\n"
            f"/architecture/decisions/ {codeowner}\n"
            f"/domain/ {codeowner}\n",
        )
    return {
        "root": str(root),
        "toolVersion": __version__,
        "created": created,
        "next": [
            "Run aak core and read the complete preventive decision context.",
            "Discover the smallest justified modules, hosts, and projects.",
            "Create .agentic/policies/architecture/project-policy.json from observed project facts.",
            "Create module contracts and local AGENTS.md files only for actual modules.",
            "Configure protected branches according to docs/github-governance.md.",
            "Run the pinned distribution with: aak validate --fail-on-review.",
        ],
    }


def run(arguments: list[str] | None = None) -> int:
    args = _init_parser().parse_args(arguments)
    try:
        result = initialize(Path(args.root), args.codeowner, args.authority_id, args.protected_branch)
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
