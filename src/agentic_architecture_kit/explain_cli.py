from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
from pathlib import Path

from .norms import compute_rule_digest, reference_section
from .resources import read_json as read_bundled_json
from .validate_cli import run as validate


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aak explain",
        description="Explain one portable rule and its current state in a repository.",
    )
    parser.add_argument("rule", help="Portable rule id, for example DEP001.")
    parser.add_argument("--root", default=".", help="Repository root (default: current directory).")
    parser.add_argument("--base-ref", help="Optional Git base for CHG001 and comparative findings.")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def run(arguments: list[str] | None = None) -> int:
    args = _parser().parse_args(arguments)
    root = Path(args.root).resolve()
    catalog_document = read_bundled_json("data/rules.json")
    rule = next(
        (item for item in catalog_document["rules"] if item["id"] == args.rule.upper()),
        None,
    )
    if rule is None:
        print(f"Unknown architecture rule: {args.rule}", file=sys.stderr)
        return 2
    try:
        _, section = reference_section(root, rule["reference"])
    except (FileNotFoundError, ValueError) as error:
        print(f"Normative reference does not resolve for {rule['id']}: {error}", file=sys.stderr)
        return 2
    if section is None:
        print(f"Normative reference has no matching heading for {rule['id']}", file=sys.stderr)
        return 2

    validate_arguments = ["--root", str(root), "--format", "json"]
    if args.base_ref:
        validate_arguments.extend(["--base-ref", args.base_ref])
    output = io.StringIO()
    errors = io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
        validation_exit = validate(validate_arguments)
    if validation_exit == 2:
        print(errors.getvalue().strip() or output.getvalue().strip(), file=sys.stderr)
        return 2
    report = json.loads(output.getvalue())
    findings = [item for item in report["results"] if item["rule"] == rule["id"]]
    explanation = {
        "rule": {
            "id": rule["id"],
            "title": rule["title"],
            "description": rule["description"],
            "enforcer": rule["enforcer"],
            "mode": "automatic" if rule["automatic"] else "review-aware",
            "reference": rule["reference"],
            "ruleDigest": compute_rule_digest(root, rule),
        },
        "repository": {
            "root": report["repositoryRoot"],
            "revision": report["repositoryRevision"],
            "baseRevision": report.get("baseRevision"),
        },
        "findings": findings,
    }
    if args.format == "json":
        print(json.dumps(explanation, indent=2))
        return 0

    definition = explanation["rule"]
    print(f"{definition['id']} — {definition['title']}")
    print(f"State: {', '.join(item['status'] for item in findings) or 'NOT_EVALUATED'}")
    print(f"Mode: {definition['mode']}")
    print(f"Rule digest: {definition['ruleDigest']}")
    print(f"Reference: {definition['reference']}")
    print(f"Repository revision: {report['repositoryRevision']}")
    if report.get("baseRevision"):
        print(f"Base revision: {report['baseRevision']}")
    print(f"Definition: {definition['description']}")
    for finding in findings:
        applied = ""
        if finding.get("waiver"):
            applied = f" waiver={finding['waiver']}"
        elif finding.get("review"):
            applied = f" review={finding['review']}"
        print(f"[{finding['status']}] {finding['scope']}{applied} - {finding['message']}")
        if finding["evidence"]:
            print("  Evidence: " + json.dumps(finding["evidence"], sort_keys=True))
    return 0
