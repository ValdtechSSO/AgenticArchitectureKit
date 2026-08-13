from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


class ContractError(ValueError):
    pass


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ContractError(f"Required file does not exist: {path}") from error
    except json.JSONDecodeError as error:
        raise ContractError(f"Invalid JSON in {path}: {error}") from error


def load_yaml_subset(path: Path) -> Any:
    """Parse the deliberately small YAML subset used by module contracts.

    Supported constructs are indentation-based mappings, scalar sequences,
    quoted or plain scalars, inline JSON arrays/objects, and `>`/`|` blocks.
    Unsupported YAML features fail closed instead of being guessed.
    """

    try:
        raw_lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as error:
        raise ContractError(f"Required file does not exist: {path}") from error

    tokens: list[tuple[int, str, int]] = []
    for number, raw in enumerate(raw_lines, start=1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if "\t" in raw[: len(raw) - len(raw.lstrip())]:
            raise ContractError(f"Tabs are not supported in {path}:{number}")
        indent = len(raw) - len(raw.lstrip(" "))
        tokens.append((indent, raw.strip(), number))

    if not tokens:
        raise ContractError(f"YAML document is empty: {path}")

    def scalar(value: str, line: int) -> Any:
        if value.startswith(("&", "*", "!")):
            raise ContractError(f"Unsupported YAML feature in {path}:{line}")
        if value in ("null", "Null", "NULL", "~"):
            return None
        if value.lower() in ("true", "false"):
            return value.lower() == "true"
        if re.fullmatch(r"-?(0|[1-9][0-9]*)", value):
            return int(value)
        if value.startswith(("[", "{")):
            try:
                return json.loads(value)
            except json.JSONDecodeError as error:
                raise ContractError(
                    f"Inline YAML collections must use JSON syntax in {path}:{line}"
                ) from error
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            if value[0] == '"':
                try:
                    return json.loads(value)
                except json.JSONDecodeError as error:
                    raise ContractError(f"Invalid quoted scalar in {path}:{line}") from error
            return value[1:-1].replace("''", "'")
        return value

    def parse_block(index: int, indent: int) -> tuple[Any, int]:
        if index >= len(tokens) or tokens[index][0] != indent:
            line = tokens[index][2] if index < len(tokens) else tokens[-1][2]
            raise ContractError(f"Invalid indentation in {path}:{line}")
        is_list = tokens[index][1].startswith("- ") or tokens[index][1] == "-"
        container: Any = [] if is_list else {}

        while index < len(tokens):
            current_indent, content, line = tokens[index]
            if current_indent < indent:
                break
            if current_indent > indent:
                raise ContractError(f"Unexpected indentation in {path}:{line}")

            if is_list:
                if not (content.startswith("- ") or content == "-"):
                    raise ContractError(f"Mixed mapping and sequence in {path}:{line}")
                item = content[1:].strip()
                if not item:
                    if index + 1 >= len(tokens) or tokens[index + 1][0] <= indent:
                        raise ContractError(f"Empty sequence item in {path}:{line}")
                    value, index = parse_block(index + 1, tokens[index + 1][0])
                    container.append(value)
                    continue
                if re.match(r"^[A-Za-z_][A-Za-z0-9_-]*\s*:", item):
                    raise ContractError(
                        f"Mapping sequence items are not supported in module contracts: {path}:{line}"
                    )
                container.append(scalar(item, line))
                index += 1
                continue

            match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_-]*):(?:\s*(.*))?", content)
            if not match:
                raise ContractError(f"Invalid mapping entry in {path}:{line}")
            key, remainder = match.group(1), match.group(2) or ""
            if key in container:
                raise ContractError(f"Duplicate key '{key}' in {path}:{line}")

            if remainder in (">", "|"):
                folded = remainder == ">"
                index += 1
                parts: list[str] = []
                while index < len(tokens) and tokens[index][0] > indent:
                    parts.append(tokens[index][1])
                    index += 1
                container[key] = (" " if folded else "\n").join(parts)
                continue

            if remainder:
                container[key] = scalar(remainder, line)
                index += 1
                continue

            if index + 1 < len(tokens) and tokens[index + 1][0] > indent:
                value, index = parse_block(index + 1, tokens[index + 1][0])
                container[key] = value
            else:
                container[key] = None
                index += 1

        return container, index

    parsed, next_index = parse_block(0, tokens[0][0])
    if next_index != len(tokens):
        raise ContractError(f"Could not parse complete YAML document: {path}")
    return parsed


def validate_schema(instance: Any, schema: dict[str, Any], location: str = "$") -> list[str]:
    """Validate the JSON Schema subset used by the bundled contracts."""

    errors: list[str] = []
    expected = schema.get("type")
    type_matches = {
        "object": isinstance(instance, dict),
        "array": isinstance(instance, list),
        "string": isinstance(instance, str),
        "integer": isinstance(instance, int) and not isinstance(instance, bool),
        "boolean": isinstance(instance, bool),
        "null": instance is None,
    }
    if isinstance(expected, str) and not type_matches.get(expected, True):
        return [f"{location}: expected {expected}"]

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{location}: value is not in the allowed enum")

    if isinstance(instance, str) and len(instance) < schema.get("minLength", 0):
        errors.append(f"{location}: string is shorter than {schema['minLength']}")

    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            errors.append(f"{location}: array has fewer than {schema['minItems']} items")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, value in enumerate(instance):
                errors.extend(validate_schema(value, item_schema, f"{location}[{index}]"))

    if isinstance(instance, dict):
        properties = schema.get("properties", {})
        for required in schema.get("required", []):
            if required not in instance:
                errors.append(f"{location}: missing required property '{required}'")
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in properties:
                    errors.append(f"{location}: unknown property '{key}'")
        for key, value in instance.items():
            child_schema = properties.get(key)
            if isinstance(child_schema, dict):
                errors.extend(validate_schema(value, child_schema, f"{location}.{key}"))

    return errors
