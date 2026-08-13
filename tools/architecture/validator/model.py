from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


STATUSES = ("PASS", "FAIL", "WAIVED", "NOT_APPLICABLE", "REVIEW_REQUIRED")


@dataclass(frozen=True)
class Project:
    path: str
    name: str
    references: tuple[str, ...]


@dataclass(frozen=True)
class ObservedArchitecture:
    modules: tuple[str, ...]
    hosts: tuple[str, ...]
    projects: tuple[Project, ...]
    source_files: tuple[str, ...]

    @property
    def projects_by_path(self) -> dict[str, Project]:
        return {project.path: project for project in self.projects}


@dataclass
class Finding:
    rule: str
    status: str
    scope: str
    message: str
    evidence: dict[str, Any] = field(default_factory=dict)
    waiver: str | None = None

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
        return result


@dataclass(frozen=True)
class ValidationContext:
    root: Path
    policy_path: Path
    waiver_path: Path
    policy: dict[str, Any]
    waivers: list[dict[str, Any]]
    catalog: dict[str, dict[str, Any]]
    observed: ObservedArchitecture
    contracts: dict[str, dict[str, Any]]
    contract_errors: dict[str, list[str]]
