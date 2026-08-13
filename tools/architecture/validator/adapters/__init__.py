"""Technology adapters for architecture observation."""

from __future__ import annotations

import importlib
import re
from pathlib import Path

from ..model import ObservedArchitecture


def observe(name: str, root: Path, policy: dict) -> ObservedArchitecture:
    if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
        raise ValueError(f"Invalid technology adapter name: {name}")
    try:
        module = importlib.import_module(f"{__name__}.{name}")
    except ModuleNotFoundError as error:
        if error.name == f"{__name__}.{name}":
            raise ValueError(f"Unsupported technology adapter: {name}") from error
        raise
    adapter = getattr(module, "observe", None)
    if not callable(adapter):
        raise ValueError(f"Technology adapter has no observe function: {name}")
    observed = adapter(root, policy)
    if not isinstance(observed, ObservedArchitecture):
        raise ValueError(f"Technology adapter returned an invalid model: {name}")
    return observed
