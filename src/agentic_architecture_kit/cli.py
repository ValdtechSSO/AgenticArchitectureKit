from __future__ import annotations

import argparse
import sys

from . import __version__
from . import adopt_cli, context_cli, explain_cli, guide_cli, init_cli, validate_cli
from .resources import read_text as read_bundled_text


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aak",
        description="Agentic Architecture Kit: versioned architecture guidance, validation, and context retrieval.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command")
    commands.add_parser("validate", add_help=False, help="Validate a repository against portable rules.")
    commands.add_parser("context", add_help=False, help="Retrieve minimum sufficient repository context.")
    commands.add_parser("explain", add_help=False, help="Explain a rule and its current repository state.")
    commands.add_parser("core", add_help=False, help="Print the complete preventive decision core.")
    commands.add_parser("guide", add_help=False, help="Read packaged operational guidance.")
    commands.add_parser("template", add_help=False, help="Read or list packaged project templates.")
    commands.add_parser("init", add_help=False, help="Initialize project-owned governance files.")
    commands.add_parser("adopt", add_help=False, help="Adopt AAK in an existing repository.")
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
    if namespace.command == "explain":
        return explain_cli.run(remaining)
    if namespace.command == "core":
        if remaining:
            parser.error("aak core does not accept arguments")
        print(read_bundled_text("data/norms/agent-core.md"), end="")
        return 0
    if namespace.command == "guide":
        return guide_cli.run_guide(remaining)
    if namespace.command == "template":
        return guide_cli.run_template(remaining)
    if namespace.command == "init":
        return init_cli.run(remaining)
    if namespace.command == "adopt":
        return adopt_cli.run(remaining)
    if namespace.command == "export-offline":
        return init_cli.export_offline(remaining)
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
