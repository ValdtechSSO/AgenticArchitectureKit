from __future__ import annotations

import argparse
import sys

from . import __version__
from . import context_cli, init_cli, validate_cli


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aak",
        description="Agentic Architecture Kit: versioned architecture validation and context retrieval.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command")
    commands.add_parser("validate", add_help=False, help="Validate a repository against portable rules.")
    commands.add_parser("context", add_help=False, help="Retrieve minimum sufficient repository context.")
    commands.add_parser("init", add_help=False, help="Initialize project-owned governance files.")
    commands.add_parser("export-offline", add_help=False, help="Export an explicit versioned offline payload.")
    return parser


def main(arguments: list[str] | None = None) -> int:
    values = list(arguments) if arguments is not None else sys.argv[1:]
    parser = _parser()
    if not values:
        parser.print_help()
        return 0
    namespace, remaining = parser.parse_known_args(values)
    if namespace.command == "validate":
        return validate_cli.run(remaining)
    if namespace.command == "context":
        return context_cli.run(remaining)
    if namespace.command == "init":
        return init_cli.run(remaining)
    if namespace.command == "export-offline":
        return init_cli.export_offline(remaining)
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
