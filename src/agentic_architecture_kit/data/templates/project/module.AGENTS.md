# {ModuleName} module

## Purpose

{Capability owned by this module.}

## Read before changing

- `module.contract.yml`
- `{relevant domain context}`
- `{relevant ADR}`
- Before creating or changing stable module semantics, run
  `aak guide module-contract-authoring-prompt`. Do not infer ownership,
  invariants, or accepted risk from code alone.
- Before creating or changing this router, referenced invariants, or governing
  ADRs, run `aak guide architecture-context-authoring-prompt`.

## Commands

- `{targeted test command}`
- `uvx --from agentic-architecture-kit=={pinned-version} aak validate --fail-on-review`

## Critical rules

- {Invariant enforced by this module.}
- Keep application behavior in the owning cohesive feature area.
- Keep technical adapters behind this module's ports.
