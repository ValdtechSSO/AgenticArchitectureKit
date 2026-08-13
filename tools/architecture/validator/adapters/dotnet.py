from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from ..model import ObservedArchitecture, Project


def _relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as error:
        raise ValueError(f"Path escapes repository root: {path}") from error


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def observe(root: Path, policy: dict) -> ObservedArchitecture:
    roots = policy["roots"]
    modules_root = root / roots["modules"]
    hosts_root = root / roots["hosts"]

    modules = tuple(
        sorted(
            _relative(root, path)
            for path in modules_root.iterdir()
            if path.is_dir()
        )
    ) if modules_root.is_dir() else ()
    hosts = tuple(
        sorted(
            _relative(root, path)
            for path in hosts_root.iterdir()
            if path.is_dir()
        )
    ) if hosts_root.is_dir() else ()

    projects: list[Project] = []
    seen: set[str] = set()
    for search_root in policy["projectSearchRoots"]:
        base = root / search_root
        if not base.is_dir():
            continue
        for project_path in sorted(base.rglob("*.csproj")):
            relative_path = _relative(root, project_path)
            if relative_path in seen or any(part in ("bin", "obj") for part in project_path.parts):
                continue
            seen.add(relative_path)
            try:
                document = ET.parse(project_path)
            except ET.ParseError as error:
                raise ValueError(f"Invalid MSBuild XML in {relative_path}: {error}") from error

            name = project_path.stem
            references: list[str] = []
            for element in document.getroot().iter():
                tag = _local_name(element.tag)
                if tag == "AssemblyName" and element.text and element.text.strip():
                    name = element.text.strip()
                elif tag == "ProjectReference":
                    include = element.attrib.get("Include")
                    if include:
                        target = (project_path.parent / include.replace("\\", "/")).resolve()
                        references.append(_relative(root, target))
            projects.append(Project(relative_path, name, tuple(sorted(set(references)))))

    source_files: set[str] = set()
    for search_root in policy["projectSearchRoots"]:
        base = root / search_root
        if not base.is_dir():
            continue
        for source_path in base.rglob("*.cs"):
            if any(part in ("bin", "obj") for part in source_path.parts):
                continue
            source_files.add(_relative(root, source_path))

    return ObservedArchitecture(
        modules,
        hosts,
        tuple(sorted(projects, key=lambda item: item.path)),
        tuple(sorted(source_files)),
    )
