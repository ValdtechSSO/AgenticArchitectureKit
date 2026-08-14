from __future__ import annotations

import ast
import re
from pathlib import Path

from ..model import ObservedArchitecture, Project, SourceDependency


def _relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as error:
        raise ValueError(f"Path escapes repository root: {path}") from error


def _project_name(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    in_project = False
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("["):
            in_project = line == "[project]"
            continue
        if in_project:
            match = re.fullmatch(r'name\s*=\s*["\']([^"\']+)["\']', line)
            if match:
                return match.group(1)
    return path.parent.name


def _module_name(package_root: Path, source: Path) -> str:
    relative = source.relative_to(package_root)
    parts = list(relative.with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def observe(root: Path, policy: dict) -> ObservedArchitecture:
    modules_root = root / policy["roots"]["modules"]
    hosts_root = root / policy["roots"]["hosts"]

    modules = ()
    if modules_root.is_dir():
        if (modules_root / "__init__.py").is_file():
            modules = (_relative(root, modules_root),)
        else:
            modules = tuple(
                sorted(
                    _relative(root, path)
                    for path in modules_root.iterdir()
                    if path.is_dir() and (path / "__init__.py").is_file()
                )
            )
    hosts = tuple(
        sorted(
            _relative(root, path)
            for path in hosts_root.iterdir()
            if path.is_file() and path.suffix == ".py" and path.name != "__init__.py"
        )
    ) if hosts_root.is_dir() else ()

    projects: list[Project] = []
    seen_projects: set[str] = set()
    for search_root in policy["projectSearchRoots"]:
        base = root / search_root
        if not base.exists():
            continue
        candidates = [base] if base.is_file() and base.name == "pyproject.toml" else base.rglob("pyproject.toml")
        for project_path in sorted(candidates):
            relative_project = _relative(root, project_path)
            if relative_project in seen_projects:
                continue
            seen_projects.add(relative_project)
            projects.append(Project(relative_project, _project_name(project_path), ()))

    source_files: set[str] = set()
    dependencies: set[SourceDependency] = set()
    adapter_config = policy.get("adapterConfig", {})
    package_roots = [root / value for value in adapter_config.get("packageRoots", policy["projectSearchRoots"])]
    for search_root in policy["projectSearchRoots"]:
        base = root / search_root
        if not base.is_dir():
            continue
        for source in base.rglob("*.py"):
            if any(part in (".git", "__pycache__", ".venv", "venv") for part in source.parts):
                continue
            relative_source = _relative(root, source)
            source_files.add(relative_source)
            package_root = next((candidate for candidate in package_roots if source.is_relative_to(candidate)), source.parent)
            source_module = _module_name(package_root, source)
            try:
                tree = ast.parse(source.read_text(encoding="utf-8"), filename=relative_source)
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                targets: list[str] = []
                if isinstance(node, ast.Import):
                    targets = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                    targets = [node.module]
                for target in targets:
                    dependencies.add(SourceDependency(relative_source, source_module, target, "import"))

    directories = tuple(
        sorted(
            _relative(root, path)
            for search_root in policy["structureSearchRoots"]
            for path in (root / search_root).rglob("*")
            if path.is_dir()
            and not any(part in (".git", "__pycache__", ".venv", "venv") for part in path.parts)
            and not _relative(root, path).startswith((".agentic/generated", ".agentic/runtime"))
        )
    )
    return ObservedArchitecture(
        modules,
        hosts,
        tuple(sorted(projects, key=lambda item: item.path)),
        tuple(sorted(source_files)),
        tuple(sorted(dependencies, key=lambda item: (item.source_path, item.target_namespace))),
        directories,
    )
