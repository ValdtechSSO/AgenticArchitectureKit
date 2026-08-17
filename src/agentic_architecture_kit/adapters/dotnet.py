from __future__ import annotations

import xml.etree.ElementTree as ET
import re
from pathlib import Path

from ..model import ObservedArchitecture, Project, SourceDependency


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
            role_hint = "test" if _is_test_project(Path(relative_path), document) else None
            projects.append(Project(relative_path, name, tuple(sorted(set(references))), role_hint))

    source_files: set[str] = set()
    source_dependencies: set[SourceDependency] = set()
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
            namespace_match = re.search(r"(?m)^\s*namespace\s+([A-Za-z_][\w.]*)\s*[;{]", text)
            if namespace_match:
                source_namespace = namespace_match.group(1)
                for target_namespace in re.findall(
                    r"(?m)^\s*(?:global\s+)?using\s+(?:[A-Za-z_]\w*\s*=\s*)?([A-Za-z_][\w.]*)\s*;",
                    text,
                ):
                    if target_namespace != source_namespace:
                        source_dependencies.add(
                            SourceDependency(
                                relative_source,
                                source_namespace,
                                target_namespace,
                                "using",
                            )
                        )

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
    )
