from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


STATUSES = ("PASS", "FAIL", "WAIVED", "REVIEWED", "NOT_APPLICABLE", "REVIEW_REQUIRED")


@dataclass(frozen=True)
class Project:
    path: str
    name: str
    references: tuple[str, ...]


@dataclass(frozen=True)
class SourceDependency:
    source_path: str
    source_namespace: str
    target_namespace: str
    kind: str
    confidence: str = "exact"


@dataclass(frozen=True)
class ObservedArchitecture:
    modules: tuple[str, ...]
    hosts: tuple[str, ...]
    projects: tuple[Project, ...]
    source_files: tuple[str, ...]
    source_dependencies: tuple[SourceDependency, ...] = ()
    directories: tuple[str, ...] = ()

    @property
    def projects_by_path(self) -> dict[str, Project]:
        return {project.path: project for project in self.projects}

    def as_dict(self) -> dict[str, Any]:
        return {
            "modules": list(self.modules),
            "hosts": list(self.hosts),
            "projects": [
                {"path": item.path, "name": item.name, "references": list(item.references)}
                for item in self.projects
            ],
            "sourceFiles": list(self.source_files),
            "sourceDependencies": [
                {
                    "sourcePath": item.source_path,
                    "sourceNamespace": item.source_namespace,
                    "targetNamespace": item.target_namespace,
                    "kind": item.kind,
                    "confidence": item.confidence,
                }
                for item in self.source_dependencies
            ],
            "directories": list(self.directories),
        }


@dataclass
class Finding:
    rule: str
    status: str
    scope: str
    message: str
    evidence: dict[str, Any] = field(default_factory=dict)
    waiver: str | None = None
    review: str | None = None
    review_fingerprint: str | None = None
    reference: str | None = None
    rule_digest: str | None = None

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "rule": self.rule,
            "status": self.status,
            "scope": self.scope,
            "message": self.message,
            "evidence": self.evidence,
        }
        if self.waiver is not None:
            result["waiver"] = self.waiver
        if self.review is not None:
            result["review"] = self.review
        if self.review_fingerprint is not None:
            result["reviewFingerprint"] = self.review_fingerprint
        if self.reference is not None:
            result["reference"] = self.reference
        if self.rule_digest is not None:
            result["ruleDigest"] = self.rule_digest
        return result


@dataclass(frozen=True)
class ValidationContext:
    root: Path
    policy_path: Path
    waiver_path: Path
    review_path: Path
    authority_path: Path
    policy: dict[str, Any]
    waivers: list[dict[str, Any]]
    reviews: list[dict[str, Any]]
    authorities: dict[str, Any]
    catalog: dict[str, dict[str, Any]]
    norms: dict[str, Any]
    observed: ObservedArchitecture
    contracts: dict[str, dict[str, Any]]
    contract_errors: dict[str, list[str]]
    base_policy: dict[str, Any] | None = None
    base_revision: str | None = None
    base_norms: dict[str, Any] | None = None
