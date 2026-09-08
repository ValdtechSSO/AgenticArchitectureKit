from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .contracts import ObservationInput


class SemanticObservationError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def repository_path(root: Path, value: str, *, must_exist: bool = False) -> Path:
    path = Path(value)
    if path.is_absolute() or not value or "\\" in value or any(part == ".." for part in path.parts):
        raise SemanticObservationError("PATH_ESCAPE", f"Semantic observation path is not repository-relative POSIX: {value}")
    candidate = (root / path).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as error:
        raise SemanticObservationError("PATH_ESCAPE", f"Semantic observation path escapes repository root: {value}") from error
    if must_exist and not candidate.is_file():
        raise SemanticObservationError("STALE_INPUT", f"Semantic observation input is missing: {value}")
    return candidate


def file_sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_fingerprint(inputs: tuple[ObservationInput, ...]) -> str:
    payload = [item.as_dict() for item in sorted(inputs, key=lambda item: item.path)]
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def validate_input_manifest(root: Path, inputs: tuple[ObservationInput, ...]) -> str:
    paths = [item.path for item in inputs]
    if len(paths) != len(set(paths)):
        raise SemanticObservationError("INVALID_PROVIDER_OUTPUT", "Semantic observation input manifest contains duplicate paths")
    for item in inputs:
        path = repository_path(root, item.path, must_exist=True)
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", item.sha256):
            raise SemanticObservationError("INVALID_PROVIDER_OUTPUT", f"Invalid SHA-256 value for semantic input: {item.path}")
        if file_sha256(path) != item.sha256:
            raise SemanticObservationError("INPUT_HASH_MISMATCH", f"Semantic observation input changed: {item.path}")
    return manifest_fingerprint(inputs)
