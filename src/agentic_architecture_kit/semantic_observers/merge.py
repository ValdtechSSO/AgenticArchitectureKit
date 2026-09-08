from __future__ import annotations

from dataclasses import replace

from ..model import ObservedArchitecture, SourceDependency
from .contracts import SemanticObservation


def _identity(item: SourceDependency) -> tuple[object, ...]:
    return (
        item.source_path,
        item.source_namespace,
        item.source_symbol or "",
        item.target_namespace,
        item.target_symbol or "",
        item.target_project_path or "",
        item.kind,
        item.configurations,
    )


def merge_observations(
    structural: ObservedArchitecture,
    semantic: SemanticObservation | None,
    mode: str,
) -> ObservedArchitecture:
    del mode  # Enforcement is evaluated separately; merge remains factual and pure.
    if semantic is None:
        return structural
    coverage = semantic.coverage
    replaceable_files = (
        set(coverage.covered_source_files)
        if coverage.status == "complete" and not coverage.truncated
        else set()
    )
    retained = [
        item
        for item in structural.source_dependencies
        if not (item.source_path in replaceable_files and item.resolution in {"syntactic", "textual", "heuristic"})
    ]
    combined = retained + list(semantic.source_dependencies)
    unique = {_identity(item): item for item in combined}
    dependencies = tuple(unique[key] for key in sorted(unique))
    return replace(structural, source_dependencies=dependencies)
