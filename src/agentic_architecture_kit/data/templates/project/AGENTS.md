# {ProjectName}

## Purpose

{One sentence describing the product's current purpose.}

## Start here

- Run `aak core` and read the installed decision core before structural
  decisions; use `aak explain RULE_ID` for validator-owned details.
- Run `aak guide implement-change` before planning or implementing any product
  change. It decides whether contracts, policy, ADRs, or adapters must change.
- If module semantics are created or changed, run
  `aak guide module-contract-authoring-prompt`; the user supplies meaning, not
  YAML.
- If project policy is created, reviewed, reconciled, or changed, run
  `aak guide project-policy-authoring-prompt`; the user supplies architectural
  intent, not JSON.
- If ADRs, invariants, system overview, or agent routers are created or changed,
  run `aak guide architecture-context-authoring-prompt`; the user supplies
  meaning and decisions, not Markdown.
- If a project-specific architecture guarantee is created or changed, run
  `aak guide project-rule-authoring-prompt` and connect its analyzer or test to
  the authoritative local and CI checks.
- If a waiver is proposed, reviewed, changed, or removed, run
  `aak guide waiver-authoring-prompt`. The agent writes the record but never
  authorizes its own architectural deviation.
- Run `aak guide bootstrap` for the version-matched creation and evolution
  procedure; use `aak guide github-governance` when configuring GitHub controls.
- Read `architecture/system-overview.md` and `domain/global-invariants.md`.
- Locate the owning module and cohesive feature area before changing behavior.
- Read the module's `module.contract.yml` and `AGENTS.md`.
- Read applicable ADRs and architecture waivers.

## Authoritative commands

- Build: `{build command}`
- Test: `{test command}`
- Architecture: `uvx --from agentic-architecture-kit=={pinned-version} aak validate --fail-on-review`

## Critical rules

- {Current product invariant or operational boundary.}
- Do not add speculative modules, projects, abstractions, or empty directories.
- Do not weaken portable architecture rules through project policy.
- Boundary changes update declaration, observation, enforcement, and evidence.
- Run the architecture gate before the first implementation change and before
  declaring the task complete.

## Map

- `src/Modules/{CurrentModule}/`: {owned capability}
- `src/Hosts/{CurrentHost}/`: {current execution or delivery mechanism}
- `architecture/`, `domain/`: maintained decisions and invariants
- `.agentic/`: version pin, project policies, generated context, and evidence

## Prohibited operations

- {Project-specific destructive, remote, security, or data operation.}
