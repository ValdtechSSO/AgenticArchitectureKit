# Agentic Architecture Kit

[Español](docs/es/README.md) · [Language policy](docs/language-policy.md)

> **Implementation status:** 0.3 preview. The manifesto is normative; the
> [capability matrix](docs/capabilities.md) distinguishes implemented, initial,
> and roadmap behavior.

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

- [`MANIFESTO.md`](MANIFESTO.md): normative initialization, evolution, and
  conformance rules.
- [`docs/team-guide.md`](docs/team-guide.md): human guide for understanding,
  reviewing, and governing the artifacts created by the kit.
- [`docs/capabilities.md`](docs/capabilities.md): honest implementation and
  roadmap matrix for the reference tools.
- [`docs/github-governance.md`](docs/github-governance.md): required CODEOWNERS,
  review, and protected-branch controls that cannot be proven locally.
- [`docs/releasing.md`](docs/releasing.md): package release and PyPI trusted
  publishing procedure for kit maintainers.
- [`docs/create-project-from-zero.md`](docs/create-project-from-zero.md): the
  operational procedure an agent follows to bootstrap a project.
- [`src/agentic_architecture_kit/`](src/agentic_architecture_kit/): versioned
  Python distribution containing the CLI, portable rules, schemas, templates,
  and built-in technology adapters.
- [`tests/`](tests/): conformance suite for the distributed package.
- [`examples/`](examples/): consumer repositories that exercise the installed
  rules without vendoring the implementation.

## Creating a project

1. Give the agent access to this repository and the new project directory.
2. Provide the product objective, known requirements, and constraints.
3. Require it to read `MANIFESTO.md` and
   `docs/create-project-from-zero.md` completely.
4. The agent discovers current capabilities, hosts, and boundaries before
   creating structure.
5. It pins and executes a published validator version without copying its
   implementation into the project.
6. It adapts the templates to declare the project's actual architecture.
7. It runs validator tests and validates the resulting project architecture.

Recommended bootstrap prompt:

```text
Use Agentic Architecture Kit to create the smallest justified architecture for
this project. Read MANIFESTO.md and docs/create-project-from-zero.md completely.
Do not copy an example structure mechanically. Discover capabilities, hosts,
boundaries, and risks from current requirements and observable evidence. Install
the general validator without redefining its rules, create the project-specific
policy, and make assumptions and pending semantic reviews explicit. Work
autonomously inside declared authority and escalate only an undefined material
product, risk, ownership, or authority decision.
```

## Distribution and project-owned payload

Portable code, schemas, the rule catalog, and neutral templates are published
together as `agentic-architecture-kit`. A consumer pins the exact version in
`.agentic/toolchain.json` and runs it with `uvx` or `pipx`:

```bash
uvx --from agentic-architecture-kit==0.3.0 aak validate --fail-on-review
```

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
creates an explicit versioned snapshot with a SHA-256 manifest. That export is
an operational exception, not the default adoption model.

## Verifying the kit

Python 3.9 or later is required. The kit has no third-party runtime dependency.

```bash
python3 -m pip install --no-deps -e .
python3 -m unittest discover -s tests -v
aak --help
aak validate --fail-on-review
aak context index
aak context locate "architecture validation"
aak validate --root examples/dotnet-valid
```

Initialize governance files in an existing project, then let the agent discover
and write its project policy:

```bash
uvx --from agentic-architecture-kit==0.3.0 aak init --root . --codeowner @your-org/architecture
```

The reference implementation supports SDK-style .NET and Python projects. See
[`examples/dotnet-valid/`](examples/dotnet-valid/) for a conforming repository
and [`examples/dotnet-invalid/`](examples/dotnet-invalid/) for an intentional
source-level architecture failure inside a single assembly.

## License

Agentic Architecture Kit is licensed under the
[Apache License 2.0](LICENSE) (`Apache-2.0`).
