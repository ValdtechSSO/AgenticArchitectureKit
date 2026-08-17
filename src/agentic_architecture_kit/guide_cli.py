from __future__ import annotations

import argparse

from .resources import resource, read_text


_GUIDES = {
    "adapter-development": (
        "Write and package an external technology observation adapter.",
        "data/guides/adapter-development.md",
    ),
    "bootstrap": (
        "Create a new project or bring an existing repository under the kit.",
        "data/guides/bootstrap.md",
    ),
    "github-governance": (
        "Configure GitHub authority, protected branches, and review evidence.",
        "data/guides/github-governance.md",
    ),
}


def _guide_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aak guide",
        description="Read version-matched operational guidance bundled with Agentic Architecture Kit.",
    )
    parser.add_argument("name", nargs="?", choices=sorted(_GUIDES))
    return parser


def run_guide(arguments: list[str] | None = None) -> int:
    args = _guide_parser().parse_args(arguments)
    if args.name is None:
        for name, (description, _) in sorted(_GUIDES.items()):
            print(f"{name}: {description}")
        return 0
    print(read_text(_GUIDES[args.name][1]), end="")
    return 0


def _template_names() -> list[str]:
    directory = resource("data/templates/project")
    return sorted(item.name for item in directory.iterdir() if item.is_file())


def _template_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aak template",
        description="Read neutral project templates bundled with Agentic Architecture Kit.",
    )
    parser.add_argument("name", nargs="?", choices=_template_names())
    return parser


def run_template(arguments: list[str] | None = None) -> int:
    args = _template_parser().parse_args(arguments)
    if args.name is None:
        for name in _template_names():
            print(name)
        return 0
    print(read_text(f"data/templates/project/{args.name}"), end="")
    return 0
