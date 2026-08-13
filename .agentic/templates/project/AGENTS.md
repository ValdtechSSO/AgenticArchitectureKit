# {ProjectName}

## Purpose

{One sentence describing the product's current purpose.}

## Start here

- Read `architecture/system-overview.md` and `domain/global-invariants.md`.
- Locate the owning module and cohesive feature area before changing behavior.
- Read the module's `module.contract.yml` and `AGENTS.md`.
- Read applicable ADRs and architecture waivers.

## Authoritative commands

- Build: `{build command}`
- Test: `{test command}`
- Architecture: `./tools/scripts/validate-architecture.sh`

## Critical rules

- {Current product invariant or operational boundary.}
- Do not add speculative modules, projects, abstractions, or empty directories.
- Do not weaken portable architecture rules through project policy.
- Boundary changes update declaration, observation, enforcement, and evidence.

## Map

- `src/Modules/{CurrentModule}/`: {owned capability}
- `src/Hosts/{CurrentHost}/`: {current execution or delivery mechanism}
- `architecture/`, `domain/`: maintained decisions and invariants
- `.agentic/`: executable contracts and project policies

## Prohibited operations

- {Project-specific destructive, remote, security, or data operation.}
