from __future__ import annotations

from importlib import metadata
from pathlib import Path
from typing import Any

from . import __version__
from .contracts import ContractError, load_json, validate_schema
from .resources import schema


def load_toolchain(path: Path, catalog_version: int) -> dict[str, Any]:
    document = load_json(path)
    errors = validate_schema(document, schema("toolchain.schema.json"))
    if errors:
        raise ContractError(
            "Architecture toolchain does not conform to package:toolchain.schema.json:\n  - "
            + "\n  - ".join(errors)
        )
    if document["distribution"] != "agentic-architecture-kit":
        raise ContractError(f"Unsupported architecture distribution: {document['distribution']}")
    if document["toolVersion"] != __version__:
        raise ContractError(
            f"Project requires agentic-architecture-kit=={document['toolVersion']}, but running version is {__version__}. "
            f"Run the declared version, for example: uvx --from agentic-architecture-kit=={document['toolVersion']} aak validate"
        )
    if document["catalogVersion"] != catalog_version:
        raise ContractError(
            f"Project pins catalog version {document['catalogVersion']}, but distribution provides {catalog_version}"
        )
    for extension in document["extensions"]:
        try:
            observed_version = metadata.version(extension["distribution"])
        except metadata.PackageNotFoundError as error:
            raise ContractError(f"Pinned architecture extension is not installed: {extension['distribution']}") from error
        if observed_version != extension["version"]:
            raise ContractError(
                f"Architecture extension {extension['distribution']} pins {extension['version']}, "
                f"but {observed_version} is installed"
            )
    return document
