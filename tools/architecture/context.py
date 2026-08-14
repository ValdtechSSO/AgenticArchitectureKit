#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from validator.context import impact, load_policy, locate, references, write_index
from validator.contracts import ContractError


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Retrieve minimum sufficient architecture context.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--policy", default=".agentic/policies/architecture/project-policy.json")
    commands = parser.add_subparsers(dest="command", required=True)
    index = commands.add_parser("index", help="Generate the revision-bound repository index.")
    index.add_argument("--output", default=".agentic/generated/index")
    locate_command = commands.add_parser("locate", help="Find declared starting paths for an intent.")
    locate_command.add_argument("query")
    for name in ("symbol", "references", "tests"):
        command = commands.add_parser(name, help=f"Find {name} with observed provenance.")
        command.add_argument("symbol")
    impact_command = commands.add_parser("impact", help="Find ownership and direct observed consumers of a path.")
    impact_command.add_argument("path")
    return parser


def run(arguments: list[str] | None = None) -> int:
    args = _parser().parse_args(arguments)
    root = Path(args.root).resolve()
    try:
        policy = load_policy(root, args.policy)
        if args.command == "index":
            result = write_index(root, policy, args.output)
            result = {"output": args.output, "files": sorted(result)}
        elif args.command == "locate":
            result = locate(root, policy, args.query)
        elif args.command in ("symbol", "references"):
            result = references(root, policy, args.symbol)
        elif args.command == "tests":
            result = references(root, policy, args.symbol, tests_only=True)
        else:
            result = impact(root, policy, args.path)
        print(json.dumps(result, indent=2))
        return 0
    except (ContractError, OSError, ValueError) as error:
        print(f"architecture context error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(run())
