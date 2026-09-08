from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..model import ObservedArchitecture, SourceDependency


SEMANTIC_CAPABILITY = "source-dependencies"
COVERAGE_STATUSES = ("complete", "partial", "unavailable")
ERROR_CODES = (
    "PROVIDER_NOT_CONFIGURED",
    "PROVIDER_NOT_INSTALLED",
    "PROVIDER_NOT_PINNED",
    "PROVIDER_AMBIGUOUS",
    "PROVIDER_UNAVAILABLE",
    "SUBJECT_NOT_FOUND",
    "SUBJECT_AMBIGUOUS",
    "INDEXING_INCOMPLETE",
    "UNSUPPORTED_CONFIGURATION",
    "PARTIAL_COVERAGE",
    "TRUNCATED_RESULT",
    "STALE_INPUT",
    "INPUT_HASH_MISMATCH",
    "PATH_ESCAPE",
    "INVALID_PROVIDER_OUTPUT",
    "CAPABILITY_NOT_PROVIDED",
)


@dataclass(frozen=True)
class ObservationInput:
    path: str
    sha256: str

    def as_dict(self) -> dict[str, str]:
        return {"path": self.path, "sha256": self.sha256}


@dataclass(frozen=True)
class CoverageExclusion:
    path: str
    reason: str

    def as_dict(self) -> dict[str, str]:
        return {"path": self.path, "reason": self.reason}


@dataclass(frozen=True)
class ObservationDiagnostic:
    code: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


@dataclass(frozen=True)
class SemanticCoverage:
    status: str
    covered_source_files: tuple[str, ...]
    exclusions: tuple[CoverageExclusion, ...]
    configurations: tuple[str, ...]
    truncated: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "coveredSourceFiles": list(self.covered_source_files),
            "exclusions": [item.as_dict() for item in self.exclusions],
            "configurations": list(self.configurations),
            "truncated": self.truncated,
        }


@dataclass(frozen=True)
class SemanticObservation:
    provider: str
    provider_version: str
    capability: str
    repository_revision: str
    workspace_fingerprint: str
    subject_path: str | None
    inputs: tuple[ObservationInput, ...]
    coverage: SemanticCoverage
    source_dependencies: tuple[SourceDependency, ...]
    diagnostics: tuple[ObservationDiagnostic, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "providerVersion": self.provider_version,
            "capability": self.capability,
            "repositoryRevision": self.repository_revision,
            "workspaceFingerprint": self.workspace_fingerprint,
            "subjectPath": self.subject_path,
            "inputs": [item.as_dict() for item in self.inputs],
            "coverage": self.coverage.as_dict(),
            "sourceDependencies": [
                ObservedArchitecture((), (), (), (), (item,)).as_dict()["sourceDependencies"][0]
                for item in self.source_dependencies
            ],
            "diagnostics": [item.as_dict() for item in self.diagnostics],
        }


@dataclass(frozen=True)
class SemanticObservationStatus:
    configured: bool
    provider: str | None
    mode: str | None
    capabilities: tuple[str, ...]
    available: bool
    coverage: str
    resolution_used: str
    fallback_used: bool
    reason_code: str | None = None
    message: str | None = None
    observation: SemanticObservation | None = None
    invalid: bool = False

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "configured": self.configured,
            "provider": self.provider,
            "mode": self.mode,
            "available": self.available,
            "capabilities": list(self.capabilities),
            "coverage": self.coverage,
            "resolutionUsed": self.resolution_used,
            "fallbackUsed": self.fallback_used,
        }
        if self.reason_code:
            result["reasonCode"] = self.reason_code
        if self.message:
            result["message"] = self.message
        if self.observation:
            result.update({
                "providerVersion": self.observation.provider_version,
                "workspaceFingerprint": self.observation.workspace_fingerprint,
                "repositoryRevision": self.observation.repository_revision,
                "subjectPath": self.observation.subject_path,
                "truncated": self.observation.coverage.truncated,
                "inputs": [item.as_dict() for item in self.observation.inputs],
                "exclusions": [item.as_dict() for item in self.observation.coverage.exclusions],
                "configurations": list(self.observation.coverage.configurations),
                "diagnostics": [item.as_dict() for item in self.observation.diagnostics],
            })
        return result


@dataclass(frozen=True)
class ObservationBundle:
    architecture: ObservedArchitecture
    semantic: SemanticObservationStatus
    structural_provider: str = "technology-adapter"

    def as_dict(self) -> dict[str, Any]:
        structural = self.architecture.as_dict()
        structural["layers"] = [
            {
                "provider": self.structural_provider,
                "resolution": "structural+syntactic",
            },
            *([self.semantic.as_dict()] if self.semantic.configured else []),
        ]
        return structural
