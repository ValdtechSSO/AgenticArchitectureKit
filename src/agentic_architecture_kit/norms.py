from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .resources import read_text as read_bundled_text


def markdown_slug(heading: str) -> str:
    value = re.sub(r"[`*_~]", "", heading.strip().casefold())
    value = re.sub(r"[^\w\- ]", "", value, flags=re.UNICODE)
    return re.sub(r"[\s-]+", "-", value).strip("-")


def split_reference(reference: str) -> tuple[str, str | None]:
    document, separator, anchor = reference.partition("#")
    return document, anchor if separator else None


def read_reference_document(root: Path, reference: str) -> tuple[str, str]:
    document, _ = split_reference(reference)
    if document.startswith("package:"):
        return document, read_bundled_text(document.removeprefix("package:"))
    target = (root / document).resolve()
    target.relative_to(root.resolve())
    return target.relative_to(root.resolve()).as_posix(), target.read_text(encoding="utf-8")


def markdown_sections(text: str) -> list[dict[str, Any]]:
    lines = text.splitlines()
    headings: list[tuple[int, int, str, str]] = []
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if match:
            title = match.group(2).strip()
            headings.append((index, len(match.group(1)), title, markdown_slug(title)))
    sections: list[dict[str, Any]] = []
    for position, (start, level, title, anchor) in enumerate(headings):
        end = len(lines)
        for next_start, next_level, _, _ in headings[position + 1:]:
            if next_level <= level:
                end = next_start
                break
        sections.append({
            "level": level,
            "title": title,
            "anchor": anchor,
            "text": "\n".join(lines[start:end]).strip(),
        })
    return sections


def reference_section(root: Path, reference: str) -> tuple[str, dict[str, Any] | None]:
    document, anchor = split_reference(reference)
    _, text = read_reference_document(root, reference)
    if anchor is None:
        return document, None
    section = next(
        (item for item in markdown_sections(text) if item["anchor"] == anchor.casefold()),
        None,
    )
    return document, section


def compute_rule_digest(root: Path, rule: dict[str, Any]) -> str:
    semantic_rule = {
        key: rule[key]
        for key in ("id", "description", "evaluator", "automatic", "inputs", "enforcer")
    }
    try:
        _, section = reference_section(root, str(rule["reference"]))
        normative_text = section["text"] if section else None
    except (FileNotFoundError, ValueError):
        normative_text = None
    payload = json.dumps(
        {"rule": semantic_rule, "normativeSection": normative_text},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()
