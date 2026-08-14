# Agentic Architecture Kit

[Español](docs/es/README.md) · [Language policy](docs/language-policy.md)

> **Implementation status:** 0.4.3 preview. The published distribution is
> self-contained for agent bootstrap and evolution. The packaged decision core
> and rule references are normative; the manifesto is their human-facing map.
> The [capability matrix](docs/capabilities.md) distinguishes implemented,
> initial, and roadmap behavior.

An executable architecture standard for projects created and evolved by coding
agents.

This repository is not a fixed directory template. It provides the protocol and
tools an agent needs to discover the smallest justified architecture for a
project, materialize it from current knowledge, and protect it as the product
evolves.

## Primary objective

> An agent must be able to create, modify, and evolve a project autonomously
> within the boundaries decided by the team. The repository must provide enough
> context, policies, and validation for the agent to determine what it may do,
> where the change belongs, and how to prove the result conforms—without human
> intervention unless the request requires a product, risk, ownership, or
> authority decision that has not yet been defined. The repository must also
> organize and provide the minimum sufficient context for each task efficiently,
> progressively, and traceably, so the agent can quickly locate the relevant
> domain, ownership, contracts, decisions, dependencies, code, and tests without
> indiscriminate loading or conversational memory.

Autonomy is the default behavior. Human intervention is an exceptional
escalation when the repository does not contain enough authority for a material
decision; it is not a routine development step.

Context access is part of the architecture. The repository provides a small
entry point and lets the agent expand through ownership, dependencies, and
concrete evidence. More context is not necessarily better: relevant context
should arrive when the task requires it.

## What is included

- [`MANIFESTO.md`](MANIFESTO.md): human-facing purpose, enforcement model, and
  map of the canonical sources.
- [`agent-core.md`](src/agentic_architecture_kit/data/norms/agent-core.md): the
  complete preventive context an implementation agent reads before deciding
  structure.
- [`portable-rules.md`](src/agentic_architecture_kit/data/norms/portable-rules.md):
  validator-owned norms loaded progressively through findings.
- [`docs/team-guide.md`](docs/team-guide.md): human guide for understanding,
  reviewing, and governing the artifacts created by the kit.
- [`docs/capabilities.md`](docs/capabilities.md): honest implementation and
  roadmap matrix for the reference tools.
- [`docs/github-governance.md`](docs/github-governance.md): required CODEOWNERS,
  review, and protected-branch controls that cannot be proven locally.
- [`docs/releasing.md`](docs/releasing.md): package release and PyPI trusted
  publishing procedure for kit maintainers.
- [`docs/create-project-from-zero.md`](docs/create-project-from-zero.md): the
  web rendition of the operational procedure bundled as `aak guide bootstrap`.
- [`src/agentic_architecture_kit/`](src/agentic_architecture_kit/): versioned
  Python distribution containing the CLI, operational guides, portable rules,
  schemas, templates, and built-in technology adapters.
- [`tests/`](tests/): conformance suite for the distributed package.
- [`examples/`](examples/): consumer repositories that exercise the installed
  rules without vendoring the implementation.

## Creating a project

1. Give the agent write access to the target project directory and access to the
   package registry, or provide an offline export of the pinned kit version.
2. Provide the product objective, known requirements, and constraints.
3. Require it to run `aak core` and `aak guide bootstrap` from that version and
   read both completely before initialization or the first modification.
4. The agent discovers current capabilities, hosts, and boundaries before
   creating structure.
5. It pins and executes a published kit version without copying its
   implementation into the project.
6. It adapts the templates to declare the project's actual architecture.
7. It runs the project's build and tests and validates the resulting
   architecture.

Recommended bootstrap prompt:

```text
Use Agentic Architecture Kit to create the smallest justified architecture for
this project. Run aak core and aak guide bootstrap from the pinned distribution
and read both completely before initialization or the first modification.
Do not copy an example structure mechanically. Discover capabilities, hosts,
boundaries, and risks from current requirements and observable evidence. Install
the general validator without redefining its rules, create the project-specific
policy, and run the gate before creating product structure or implementation.
For an existing repository, run it before the first modification. Run it again
before declaring the task complete. Follow a finding's normative reference only
when needed; an unresolved reference is a failure, never permission to infer the
rule from memory. Work autonomously inside declared authority and escalate only
an undefined material product, risk, ownership, or authority decision.
```

## Distribution and project-owned payload

Portable code, operational agent guides, schemas, the rule catalog, and neutral
templates are published together as `agentic-architecture-kit`. A consumer pins
the exact version in `.agentic/toolchain.json` and runs it with `uvx` or `pipx`:

```bash
uvx --from agentic-architecture-kit==0.4.3 aak core
uvx --from agentic-architecture-kit==0.4.3 aak guide bootstrap
uvx --from agentic-architecture-kit==0.4.3 aak validate --fail-on-review
```

The agent does not need access to this source checkout. The pinned distribution
contains the preventive core, operational guides, rules, schemas, templates,
adapters, and validation engine required for bootstrap and later evolution.

Only project-owned decisions and context live in the consumer repository:

```text
AGENTS.md
architecture/system-overview.md
architecture/decisions/
domain/global-invariants.md
.agentic/toolchain.json
.agentic/policies/architecture/project-policy.json
.agentic/policies/architecture/waivers.json
.agentic/policies/architecture/authorities.json
.agentic/policies/architecture/reviews.json
.github/CODEOWNERS
{actual-module-root}/AGENTS.md
{actual-module-root}/module.contract.yml
```

Only applicable artifacts are created. Empty directories, speculative
abstractions, technical modules, and assemblies without a current enforceable
boundary are prohibited.

For disconnected environments, `aak export-offline --output <directory>`
creates an explicit versioned snapshot containing the same code, guides,
schemas, rules, and templates with a SHA-256 manifest. That export is an
operational exception, not the default adoption model.

## Adopting AAK in an existing project

Run the adoption preview from the existing repository root before modifying the
project. It observes the current Python or SDK-style .NET structure and reports
every file it would add, the proposed policy, CI integration, validation result,
and semantic work that still requires a real decision:

```bash
uvx --from agentic-architecture-kit==0.4.3 aak adopt \
  --root . \
  --codeowner @your-org/architecture \
  --ci github \
  --dry-run
```

Review the JSON plan, then apply the same command without `--dry-run`:

```bash
uvx --from agentic-architecture-kit==0.4.3 aak adopt \
  --root . \
  --codeowner @your-org/architecture \
  --ci github
```

For a single-owner repository, add `--authority-mode solo-maintainer` and use
that maintainer as `--codeowner`. `aak adopt` refuses a dirty worktree unless
`--allow-dirty` is explicit. It preserves existing files and workflows, so
re-running it is safe; an existing workflow without the AAK gate is reported
for integration instead of being overwritten.

The command automates the mechanical bootstrap: governance records, observed
policy proposal, optional GitHub Actions gate, strict validation, and the
context index. It exits nonzero when conformance or semantic work remains and
lists that work under `requiredActions`. It never fabricates module contracts,
local `AGENTS.md` content, waivers, or semantic approvals. Complete those items
from actual project knowledge, run the project build and tests, and rerun
`aak validate --fail-on-review` before merging.

## Verifying the kit

Python 3.9 or later is required. The kit has no third-party runtime dependency.

```bash
python3 -m pip install --no-deps -e .
python3 -m unittest discover -s tests -v
aak --help
aak validate --fail-on-review
aak core
aak guide
aak guide bootstrap
aak guide github-governance
aak template
aak template AGENTS.md
aak adopt --help
aak explain DEP001
aak context index
aak context locate "architecture validation"
aak validate --root examples/dotnet-valid
```

For lower-level or new-project initialization, `aak init` creates governance
files and writes an observed `project-policy.json` proposal without running the
complete adoption workflow:

```bash
uvx --from agentic-architecture-kit==0.4.3 aak init --root . --codeowner @your-org/architecture
```

For a repository maintained by one person, declare that constraint honestly
instead of configuring an impossible self-review requirement:

```bash
uvx --from agentic-architecture-kit==0.4.3 aak init --root . \
  --codeowner @your-user --authority-mode solo-maintainer
```

Solo-maintainer reviews use a durable GitHub maintainer-attestation URL. They do
not claim that approving one's own pull request is independent review.

For an empty repository, select the known technology explicitly with
`--adapter dotnet` or `--adapter python`. The observed proposal is a starting
point, not approval of every discovered boundary: review it and remove accidental
or unjustified structure before implementation.

The reference implementation supports SDK-style .NET and Python projects. See
[`examples/dotnet-valid/`](examples/dotnet-valid/) for a conforming repository
and [`examples/dotnet-invalid/`](examples/dotnet-invalid/) for an intentional
source-level architecture failure inside a single assembly.

## License

Agentic Architecture Kit is licensed under the
[Apache License 2.0](LICENSE) (`Apache-2.0`).
