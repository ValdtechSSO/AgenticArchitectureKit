# Agentic Architecture Kit

## Purpose

This repository distributes an executable architecture standard for projects
created and evolved by coding agents.

## Start here

- Read `MANIFESTO.md` completely.
- Read `docs/create-project-from-zero.md` before changing bootstrap guidance.
- Read `docs/language-policy.md` before changing public documentation.
- Portable rule semantics live in `tools/architecture/rules.json` and the
  validator engine.
- Project-specific examples belong under `.agentic/templates/project/`.

## Authoritative commands

- Validator tests: `python3 -m unittest discover -s tools/architecture/tests -v`
- CLI help: `python3 tools/architecture/validate.py --help`
- Syntax check: `python3 -m py_compile tools/architecture/validate.py tools/architecture/validator/*.py tools/architecture/validator/adapters/*.py`

## Critical rules

- Do not turn the manifesto into an exhaustive folder template.
- Do not encode one project's modules, hosts, or dependencies as portable rules.
- Keep portable rules, project policy, and explicit waivers separate.
- A semantic rule that cannot be proven mechanically returns `REVIEW_REQUIRED`.
- New technology support extends observation through an adapter; it does not
  redefine rule semantics.
- English is canonical. Changes to canonical public documentation update the
  corresponding Spanish translation under `docs/es/` in the same change.
