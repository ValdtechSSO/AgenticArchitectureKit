from __future__ import annotations

import xml.etree.ElementTree as ET
import re
from dataclasses import replace
from pathlib import Path

from ..model import ObservedArchitecture, Project, SourceDependency, SourceNamespace


def _relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as error:
        raise ValueError(f"Path escapes repository root: {path}") from error


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _is_test_project(project_path: Path, document: ET.ElementTree) -> bool:
    root = document.getroot()
    sdk_values = [root.attrib.get("Sdk", "")]
    package_references: set[str] = set()
    for element in root.iter():
        tag = _local_name(element.tag)
        if tag in ("IsTestProject", "IsTestingPlatformApplication"):
            if (element.text or "").strip().casefold() == "true":
                return True
        elif tag == "ProjectCapability" and element.attrib.get("Include", "").casefold() == "testcontainer":
            return True
        elif tag == "Sdk":
            sdk_values.append(element.attrib.get("Name", element.text or ""))
        elif tag == "PackageReference":
            package_references.add(element.attrib.get("Include", element.attrib.get("Update", "")).casefold())

    if any(value.casefold().startswith(("mstest.sdk", "microsoft.testing.platform.msbuild")) for value in sdk_values):
        return True
    if package_references.intersection({
        "microsoft.net.test.sdk",
        "microsoft.testing.platform",
        "mstest.testframework",
        "nunit",
        "xunit",
        "tunit",
    }):
        return True

    relative_parts = [part.casefold() for part in project_path.parts]
    conventional_name = re.search(r"(?:^|[._-])tests?$", project_path.stem, re.IGNORECASE)
    camel_case_name = re.search(r"Tests?$", project_path.stem)
    return "tests" in relative_parts or "test" in relative_parts or bool(conventional_name or camel_case_name)


def _source_project(source_path: str, projects: list[Project]) -> Project | None:
    candidates: list[tuple[int, Project]] = []
    for project in projects:
        project_root = Path(project.path).parent.as_posix()
        if project_root == "." or source_path.startswith(project_root.rstrip("/") + "/"):
            candidates.append((len(project_root), project))
    if not candidates:
        return None
    most_specific = max(length for length, _ in candidates)
    matches = [project for length, project in candidates if length == most_specific]
    return matches[0] if len(matches) == 1 else None


def observe(root: Path, policy: dict) -> ObservedArchitecture:
    roots = policy["roots"]
    modules_root = root / roots["modules"]
    hosts_root = root / roots["hosts"]

    modules = ()
    if modules_root.is_dir():
        if any(path.is_file() for path in modules_root.glob("*.csproj")):
            modules = (_relative(root, modules_root),)
        else:
            modules = tuple(
                sorted(
                    _relative(root, path)
                    for path in modules_root.iterdir()
                    if path.is_dir() and not path.name.startswith(".")
                )
            )
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
            root_namespace: str | None = None
            references: list[str] = []
            for element in document.getroot().iter():
                tag = _local_name(element.tag)
                if tag == "AssemblyName" and element.text and element.text.strip():
                    name = element.text.strip()
                elif tag == "RootNamespace" and element.text and element.text.strip() and "$(" not in element.text:
                    root_namespace = element.text.strip()
                elif tag == "ProjectReference":
                    include = element.attrib.get("Include")
                    if include:
                        target = (project_path.parent / include.replace("\\", "/")).resolve()
                        references.append(_relative(root, target))
            role_hint = "test" if _is_test_project(Path(relative_path), document) else None
            projects.append(
                Project(
                    relative_path,
                    name,
                    tuple(sorted(set(references))),
                    role_hint,
                    root_namespace,
                )
            )

    source_files: set[str] = set()
    source_dependencies: set[SourceDependency] = set()
    source_namespaces: set[SourceNamespace] = set()
    project_namespaces: dict[str, set[str]] = {project.path: set() for project in projects}
    for search_root in policy["projectSearchRoots"]:
        base = root / search_root
        if not base.is_dir():
            continue
        for source_path in base.rglob("*.cs"):
            if any(part in ("bin", "obj") for part in source_path.parts):
                continue
            relative_source = _relative(root, source_path)
            source_files.add(relative_source)
            text = source_path.read_text(encoding="utf-8", errors="replace")
            declared_namespaces = set(
                re.findall(r"(?m)^\s*namespace\s+([A-Za-z_][\w.]*)\s*[;{]", text)
            )
            if declared_namespaces:
                project = _source_project(relative_source, projects)
                target_namespaces = set(
                    re.findall(
                        r"(?m)^\s*(?:global\s+)?using\s+(?:[A-Za-z_]\w*\s*=\s*)?([A-Za-z_][\w.]*)\s*;",
                        text,
                    )
                )
                for source_namespace in declared_namespaces:
                    if project is not None:
                        project_namespaces[project.path].add(source_namespace)
                    source_namespaces.add(
                        SourceNamespace(
                            relative_source,
                            source_namespace,
                            project.path if project is not None else None,
                        )
                    )
                    for target_namespace in target_namespaces:
                        if target_namespace != source_namespace:
                            source_dependencies.add(
                                SourceDependency(
                                    relative_source,
                                    source_namespace,
                                    target_namespace,
                                    "using",
                                )
                            )

    projects = [
        replace(project, namespaces=tuple(sorted(project_namespaces[project.path])))
        for project in projects
    ]

    directories = tuple(
        sorted(
            _relative(root, path)
            for search_root in policy["structureSearchRoots"]
            for path in (root / search_root).rglob("*")
            if path.is_dir()
            and not any(part in (".git", "bin", "obj", "node_modules", "__pycache__") for part in path.parts)
            and not _relative(root, path).startswith((".agentic/generated", ".agentic/runtime"))
        )
    )

    return ObservedArchitecture(
        modules,
        hosts,
        tuple(sorted(projects, key=lambda item: item.path)),
        tuple(sorted(source_files)),
        tuple(sorted(source_dependencies, key=lambda item: (item.source_path, item.target_namespace))),
        directories,
        tuple(sorted(source_namespaces, key=lambda item: (item.source_path, item.namespace))),
    )
