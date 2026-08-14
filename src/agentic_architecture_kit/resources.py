from __future__ import annotations

import json
from importlib import resources
from typing import Any


def files():
    return resources.files("agentic_architecture_kit")


def resource(relative: str):
    current = files()
    for part in relative.split("/"):
        current = current.joinpath(part)
    return current


def read_text(relative: str) -> str:
    return resource(relative).read_text(encoding="utf-8")


def read_json(relative: str) -> Any:
    try:
        return json.loads(read_text(relative))
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid bundled JSON resource {relative}: {error}") from error


def schema(name: str) -> dict[str, Any]:
    value = read_json(f"data/schemas/{name}")
    if not isinstance(value, dict):
        raise ValueError(f"Bundled schema must be an object: {name}")
    return value
