# Agentic Architecture Kit

[Español](docs/es/README.md) · [Language policy](docs/language-policy.md)

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
- [`docs/create-project-from-zero.md`](docs/create-project-from-zero.md): the
  operational procedure an agent follows to bootstrap a project.
- [`tools/architecture/`](tools/architecture/): portable validator, rule
  catalog, technology adapters, and conformance tests.
- [`.agentic/contracts/schemas/`](.agentic/contracts/schemas/): contracts for
  project policy, waivers, results, and modules.
- [`.agentic/templates/project/`](.agentic/templates/project/): neutral
  templates used to materialize only the decisions that apply to a project.

## Creating a project

1. Give the agent access to this repository and the new project directory.
2. Provide the product objective, known requirements, and constraints.
3. Require it to read `MANIFESTO.md` and
   `docs/create-project-from-zero.md` completely.
4. The agent discovers current capabilities, hosts, and boundaries before
   creating structure.
5. It installs the validator and schemas without changing their portable
   semantics.
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

## Payload installed in the project

The agent copies these portable assets without reinterpretation:

```text
tools/architecture/
tools/scripts/validate-architecture.sh
.agentic/contracts/schemas/
```

It then generates project-specific artifacts:

```text
AGENTS.md
architecture/system-overview.md
architecture/decisions/
domain/global-invariants.md
src/Modules/{CurrentModule}/AGENTS.md
src/Modules/{CurrentModule}/module.contract.yml
.agentic/policies/architecture/project-policy.json
.agentic/policies/architecture/waivers.json
```

Only applicable artifacts are created. Empty directories, speculative
abstractions, technical modules, and assemblies without a current enforceable
boundary are prohibited.

## Verifying the kit

Python 3.9 or later is required. The kit has no third-party runtime dependency.

```bash
python3 -m unittest discover -s tools/architecture/tests -v
python3 tools/architecture/validate.py --help
```

After installation in a project:

```bash
./tools/scripts/validate-architecture.sh
./tools/scripts/validate-architecture.sh --format json
./tools/scripts/validate-architecture.sh --fail-on-review
```

The initial adapter supports SDK-style .NET projects. Future technologies are
added as adapters to the same observed model; adapters do not redefine portable
rule semantics.

## License

Agentic Architecture Kit is licensed under the
[Apache License 2.0](LICENSE) (`Apache-2.0`).
