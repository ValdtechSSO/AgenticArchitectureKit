"""Technology adapters for architecture observation."""

from __future__ import annotations

import importlib
import re
from importlib import metadata
from pathlib import Path

from ..model import ObservedArchitecture


def observe(name: str, root: Path, policy: dict) -> ObservedArchitecture:
    if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
        raise ValueError(f"Invalid technology adapter name: {name}")
    try:
        module = importlib.import_module(f"{__name__}.{name}")
    except ModuleNotFoundError as error:
        if error.name != f"{__name__}.{name}":
            raise
        entry_points = metadata.entry_points()
        if hasattr(entry_points, "select"):
            candidates = entry_points.select(group="agentic_architecture_kit.adapters")
        else:  # Python 3.9 compatibility.
            candidates = entry_points.get("agentic_architecture_kit.adapters", ())
        matches = [item for item in candidates if item.name == name]
        if len(matches) != 1:
            raise ValueError(f"Unsupported or ambiguous technology adapter: {name}") from error
        adapter = matches[0].load()
    else:
        adapter = getattr(module, "observe", None)
    if not callable(adapter):
        raise ValueError(f"Technology adapter has no observe function: {name}")
    observed = adapter(root, policy)
    if not isinstance(observed, ObservedArchitecture):
        raise ValueError(f"Technology adapter returned an invalid model: {name}")
    return observed
