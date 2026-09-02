# Agentic Architecture Kit

## Purpose

This repository distributes an executable architecture standard for projects
created and evolved by coding agents.

## Start here

- Read `src/agentic_architecture_kit/data/norms/agent-core.md` completely before
  making structural decisions. Load validator-owned rules through finding
  references or `aak explain`.
- Run `python3 tools/aak.py guide implement-change` before planning or
  implementing a product change. If it classifies module semantics as new or
  changed, also run `python3 tools/aak.py guide module-contract-authoring-prompt`.
- If project policy is created, reviewed, reconciled, or changed, run
  `python3 tools/aak.py guide project-policy-authoring-prompt`; the user supplies
  architectural intent, not JSON.
- If ADRs, invariants, system overview, or agent routers are created or changed,
  run `python3 tools/aak.py guide architecture-context-authoring-prompt`; the
  user supplies meaning and decisions, not Markdown.
- If a project-specific architecture guarantee is created or changed, run
  `python3 tools/aak.py guide project-rule-authoring-prompt` and connect its
  analyzer or test to the authoritative local and CI checks.
- If a waiver is proposed, reviewed, changed, or removed, run
  `python3 tools/aak.py guide waiver-authoring-prompt`. An agent may derive and
  write the record but must never authorize its own architectural deviation.
- Read `docs/create-project-from-zero.md` before changing bootstrap guidance.
- Read `docs/team-guide.md` before changing human governance guidance.
- Read `docs/github-governance.md` before changing review authority or CI enforcement.
- Read `docs/language-policy.md` before changing public documentation.
- Portable rule semantics, schemas, and templates live in the installable
  `agentic_architecture_kit` package under `src/`.
- Neutral bootstrap templates belong under the package's `data/templates/project/`;
  executable conformance examples belong under `examples/`.

## Authoritative commands

- Install locally: `python3 -m pip install --no-deps -e .`
- Validator tests: `python3 -m unittest discover -s tests -v`
- Architecture check: `aak validate --fail-on-review`
- Context index: `aak context index`
- CLI help: `aak --help`
- Syntax check: `python3 -m compileall -q src tests tools`

## Critical rules

- Do not turn the manifesto into an exhaustive folder template.
- Do not encode one project's modules, hosts, or dependencies as portable rules.
- Keep portable rules, project policy, explicit waivers, and fingerprint-bound
  semantic reviews separate.
- A semantic rule that cannot be proven mechanically returns `REVIEW_REQUIRED`.
- New technology support extends observation through an adapter; it does not
  redefine rule semantics.
- English is canonical. Changes to canonical public documentation update the
  corresponding Spanish translation under `docs/es/` in the same change.
