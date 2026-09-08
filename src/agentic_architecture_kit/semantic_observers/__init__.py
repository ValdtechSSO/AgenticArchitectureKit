"""Provider-neutral semantic architecture observation."""

from __future__ import annotations

import re
import subprocess
from dataclasses import replace
from importlib import metadata
from pathlib import Path
from typing import Any, Iterable

from ..adapters import observe as observe_structural
from ..contracts import validate_schema
from ..model import SourceDependency
from ..resources import schema as bundled_schema
from .contracts import (
    COVERAGE_STATUSES,
    ERROR_CODES,
    SEMANTIC_CAPABILITY,
    CoverageExclusion,
    ObservationDiagnostic,
    ObservationInput,
    ObservationBundle,
    SemanticCoverage,
    SemanticObservation,
    SemanticObservationStatus,
)
from .fingerprint import SemanticObservationError, repository_path, validate_input_manifest
from .merge import merge_observations


ENTRY_POINT_GROUP = "agentic_architecture_kit.semantic_observers"
PROVIDER_PATTERN = re.compile(r"[a-z][a-z0-9_]*")
RESOLUTIONS = {"manifest", "semantic", "syntactic", "textual", "heuristic"}


def _entry_points() -> Iterable[Any]:
    discovered = metadata.entry_points()
    if hasattr(discovered, "select"):
        return discovered.select(group=ENTRY_POINT_GROUP)
    return discovered.get(ENTRY_POINT_GROUP, ())  # pragma: no cover - Python 3.9 compatibility


def _revision(root: Path) -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _status(config: dict[str, Any] | None, **values: Any) -> SemanticObservationStatus:
    return SemanticObservationStatus(
        configured=config is not None,
        provider=config.get("provider") if config else None,
        mode=config.get("mode") if config else None,
        capabilities=tuple(config.get("capabilities", ())) if config else (),
        available=values.pop("available", False),
        coverage=values.pop("coverage", "unavailable"),
        resolution_used=values.pop("resolution_used", "syntactic"),
        fallback_used=values.pop("fallback_used", config is not None),
        **values,
    )


def _validate_paths(root: Path, observation: SemanticObservation) -> None:
    if observation.subject_path:
        repository_path(root, observation.subject_path)
    for value in observation.coverage.covered_source_files:
        repository_path(root, value, must_exist=True)
    for exclusion in observation.coverage.exclusions:
        repository_path(root, exclusion.path)
    for dependency in observation.source_dependencies:
        repository_path(root, dependency.source_path, must_exist=True)
        if dependency.target_project_path:
            repository_path(root, dependency.target_project_path)
        for location in dependency.locations:
            repository_path(root, location.path, must_exist=True)
            if min(location.start_line, location.start_column, location.end_line, location.end_column) < 1:
                raise SemanticObservationError("INVALID_PROVIDER_OUTPUT", "Semantic source locations are one-based")


def _dependency_key(item: SourceDependency) -> tuple[object, ...]:
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


def load_semantic_observation(
    root: Path,
    policy: dict[str, Any],
    toolchain: dict[str, Any] | None = None,
    entry_points: Iterable[Any] | None = None,
) -> SemanticObservationStatus:
    config = policy.get("observation", {}).get("semantic")
    if config is None:
        return _status(None, reason_code="PROVIDER_NOT_CONFIGURED", fallback_used=False)
    if not isinstance(config, dict):
        return SemanticObservationStatus(
            True, None, None, (), False, "unavailable", "syntactic", True,
            "INVALID_PROVIDER_OUTPUT", "Semantic observation configuration must be an object", None, True,
        )
    provider = config.get("provider")
    mode = config.get("mode")
    capabilities = config.get("capabilities")
    if not isinstance(provider, str) or mode not in {"advisory", "required"} or not isinstance(capabilities, list):
        return _status(
            config,
            reason_code="INVALID_PROVIDER_OUTPUT",
            message="Semantic observation configuration is incomplete or unsupported",
            invalid=True,
        )
    if not PROVIDER_PATTERN.fullmatch(provider):
        return _status(config, reason_code="INVALID_PROVIDER_OUTPUT", message="Invalid semantic provider name", invalid=True)
    matches = [item for item in (entry_points if entry_points is not None else _entry_points()) if item.name == provider]
    if not matches:
        return _status(config, reason_code="PROVIDER_NOT_INSTALLED", message=f"Semantic provider is not installed: {provider}")
    if len(matches) != 1:
        return _status(config, reason_code="PROVIDER_AMBIGUOUS", message=f"Multiple semantic providers are registered as {provider}")
    entry_point = matches[0]
    distribution = getattr(getattr(entry_point, "dist", None), "name", None)
    if distribution and toolchain is not None:
        pinned = {item["distribution"].lower().replace("_", "-") for item in toolchain.get("extensions", [])}
        if distribution.lower().replace("_", "-") not in pinned:
            return _status(config, reason_code="PROVIDER_NOT_PINNED", message=f"Semantic provider distribution is not pinned: {distribution}", invalid=True)
    try:
        observer = entry_point.load()
        if not callable(observer):
            raise SemanticObservationError("INVALID_PROVIDER_OUTPUT", "Semantic provider entry point is not callable")
        observation = observer(root, config)
        if not isinstance(observation, SemanticObservation):
            raise SemanticObservationError("INVALID_PROVIDER_OUTPUT", "Semantic provider returned an invalid contract type")
        if observation.provider != provider:
            raise SemanticObservationError("INVALID_PROVIDER_OUTPUT", "Semantic provider identity differs from project policy")
        if observation.capability != SEMANTIC_CAPABILITY or observation.capability not in config["capabilities"]:
            raise SemanticObservationError("CAPABILITY_NOT_PROVIDED", "Semantic provider did not return the configured capability")
        if any(
            str(root.resolve()) in item.message
            or re.search(r"(?:[A-Za-z]:[\\/]|/(?:Users|home|private|tmp|var)/)", item.message)
            for item in observation.diagnostics
        ):
            raise SemanticObservationError("INVALID_PROVIDER_OUTPUT", "Semantic diagnostics contain an absolute local path")
        schema_errors = validate_schema(observation.as_dict(), bundled_schema("semantic-observation.schema.json"))
        if schema_errors:
            raise SemanticObservationError("INVALID_PROVIDER_OUTPUT", "; ".join(schema_errors))
        if observation.coverage.status not in COVERAGE_STATUSES:
            raise SemanticObservationError("INVALID_PROVIDER_OUTPUT", "Semantic coverage status is invalid")
        if observation.coverage.status == "complete" and not observation.inputs:
            raise SemanticObservationError("INVALID_PROVIDER_OUTPUT", "Complete semantic coverage requires a non-empty input manifest")
        if tuple(sorted(observation.inputs, key=lambda item: item.path)) != observation.inputs:
            raise SemanticObservationError("INVALID_PROVIDER_OUTPUT", "Semantic observation inputs are not canonically sorted")
        if tuple(sorted(observation.coverage.covered_source_files)) != observation.coverage.covered_source_files:
            raise SemanticObservationError("INVALID_PROVIDER_OUTPUT", "Covered source files are not canonically sorted")
        if len(set(observation.coverage.covered_source_files)) != len(observation.coverage.covered_source_files):
            raise SemanticObservationError("INVALID_PROVIDER_OUTPUT", "Covered source files contain duplicates")
        if tuple(sorted(observation.coverage.configurations)) != observation.coverage.configurations:
            raise SemanticObservationError("INVALID_PROVIDER_OUTPUT", "Semantic configurations are not canonically sorted")
        if tuple(sorted(observation.source_dependencies, key=_dependency_key)) != observation.source_dependencies:
            raise SemanticObservationError("INVALID_PROVIDER_OUTPUT", "Semantic dependencies are not canonically sorted")
        if any(item.resolution not in RESOLUTIONS or item.resolution != "semantic" for item in observation.source_dependencies):
            raise SemanticObservationError("INVALID_PROVIDER_OUTPUT", "Semantic provider emitted a non-semantic dependency")
        if any(item.provider != observation.provider for item in observation.source_dependencies):
            raise SemanticObservationError("INVALID_PROVIDER_OUTPUT", "Semantic dependency provider differs from observation provider")
        if observation.coverage.status == "unavailable" and (
            observation.coverage.covered_source_files or observation.source_dependencies
        ):
            raise SemanticObservationError("INVALID_PROVIDER_OUTPUT", "Unavailable semantic coverage cannot contain covered files or dependencies")
        covered = set(observation.coverage.covered_source_files)
        if any(item.source_path not in covered for item in observation.source_dependencies):
            raise SemanticObservationError("INVALID_PROVIDER_OUTPUT", "Semantic dependency source is not declared covered")
        if any(tuple(sorted(item.configurations)) != item.configurations for item in observation.source_dependencies):
            raise SemanticObservationError("INVALID_PROVIDER_OUTPUT", "Semantic dependency configurations are not canonically sorted")
        _validate_paths(root, observation)
        actual_fingerprint = validate_input_manifest(root, observation.inputs)
        if actual_fingerprint != observation.workspace_fingerprint:
            raise SemanticObservationError("STALE_INPUT", "Semantic observation workspace fingerprint does not match its inputs")
        revision = _revision(root)
        if revision != "unknown" and observation.repository_revision != revision:
            raise SemanticObservationError("STALE_INPUT", "Semantic observation was produced for another repository revision")
    except SemanticObservationError as error:
        return _status(config, reason_code=error.code, message=str(error), invalid=True)
    except Exception as error:  # Providers are an external operational boundary.
        return _status(
            config,
            reason_code="PROVIDER_UNAVAILABLE",
            message=f"Semantic provider failed with {type(error).__name__}",
        )

    coverage = observation.coverage.status
    reason = None
    if observation.coverage.truncated:
        coverage = "partial"
        reason = "TRUNCATED_RESULT"
    elif coverage == "partial":
        reason = "PARTIAL_COVERAGE"
    elif coverage == "unavailable":
        reason = "PROVIDER_UNAVAILABLE"
    complete = coverage == "complete"
    return _status(
        config,
        available=coverage != "unavailable",
        coverage=coverage,
        resolution_used="semantic" if complete else "semantic+syntactic" if coverage == "partial" else "syntactic",
        fallback_used=not complete,
        reason_code=reason,
        observation=observation,
    )


def observe_architecture(
    root: Path,
    policy: dict[str, Any],
    toolchain: dict[str, Any] | None = None,
    entry_points: Iterable[Any] | None = None,
) -> ObservationBundle:
    structural = observe_structural(policy["adapter"], root, policy)
    semantic = load_semantic_observation(root, policy, toolchain, entry_points)
    if semantic.observation is not None and not semantic.invalid:
        covered = set(semantic.observation.coverage.covered_source_files)
        excluded = {item.path for item in semantic.observation.coverage.exclusions}
        uncovered = sorted(set(structural.source_files) - covered - excluded)
        declared_fallback = sorted(set(structural.source_files) - covered)
        if (uncovered or declared_fallback) and semantic.coverage == "complete":
            reason = "PARTIAL_COVERAGE"
            detail = "Semantic coverage does not include every structurally observed source file"
            if declared_fallback and not uncovered:
                detail = "Semantic coverage explicitly excludes structurally observed source files"
            semantic = replace(
                semantic,
                coverage="partial",
                resolution_used="semantic+syntactic",
                fallback_used=True,
                reason_code=reason,
                message=detail,
            )
    merged = merge_observations(structural, semantic.observation if not semantic.invalid else None, semantic.mode or "advisory")
    return ObservationBundle(merged, semantic, f"{policy['adapter']}-adapter")


__all__ = [
    "CoverageExclusion",
    "ObservationDiagnostic",
    "ObservationInput",
    "ObservationBundle",
    "SemanticCoverage",
    "SemanticObservation",
    "SemanticObservationStatus",
    "SemanticObservationError",
    "ERROR_CODES",
    "load_semantic_observation",
    "merge_observations",
    "observe_architecture",
]
