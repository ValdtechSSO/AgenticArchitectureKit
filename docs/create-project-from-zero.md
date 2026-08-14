# Creating a project from zero with Agentic Architecture Kit

[Español](es/create-project-from-zero.md)

This guide accompanies the packaged
[`architecture decision core`](../src/agentic_architecture_kit/data/norms/agent-core.md).
Read that core completely before making structural decisions. Validator-owned
details are loaded through finding references or `aak explain`, not through a
complete manifesto read.

For an existing repository, run the architecture gate before the first
modification. For a new repository, initialization and the minimum declaration
are bootstrap writes; run the gate immediately afterward and before creating
product structure or implementation. Run it again before completion.

## 1. Required inputs

Before creating code or directories, the agent gathers:

- the product's current purpose and scope;
- known actors and operations;
- known data, ownership, and invariants;
- required external interfaces;
- language, runtime, and deployment constraints;
- known risks;
- available build and test commands.

Every input is classified as `KNOWN`, `ASSUMED`, or `UNKNOWN`. An assumption or
unknown must not become a module, assembly, abstraction, or directory.

## 2. Discover the smallest architecture

The agent identifies capabilities through vocabulary, ownership, rules, and
lifecycle. It begins with one module unless current evidence justifies more.

For every proposed boundary it asks:

```text
Does it have its own vocabulary?
Does it own data or state?
Does it have its own invariants?
Can it evolve independently?
Does it currently need a contract with another capability?
```

Hosts derive only from current ways to execute or expose the product. A separate
compilable project needs an enforceable dependency, deployment, runtime,
language, publication, or ownership boundary.

## 3. Propose before materializing

The initial decision records:

- proposed modules and evidence for each boundary;
- cohesive feature areas inside each module;
- current hosts;
- required projects or packages and the boundary each enforces;
- allowed dependencies;
- initial invariants, risks, and ADRs;
- assumptions and open questions;
- automatic checks and required semantic reviews.

When the user has already authorized project creation, the agent records this
proposal in the repository and continues without unnecessary confirmation. A
decision that materially changes product behavior, risk, ownership, or granted
authority must be escalated.

## 4. Install the executable foundation

Choose a released kit version and execute it directly, preferably with `uvx`:

```bash
uvx --from agentic-architecture-kit==0.4.0 aak init --root . --codeowner @your-org/architecture
```

The initializer creates `.agentic/toolchain.json`, empty governance records, and
repository-wide CODEOWNERS coverage. It also writes an observed
`project-policy.json` proposal. If no technology artifact exists yet, pass
`--adapter dotnet` or `--adapter python`. It does not copy the portable engine,
catalog, schemas, or templates into the project. Then materialize only
applicable project-specific assets:

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

Optional paths are omitted when they have no current content or responsibility.

## 5. Review the project-specific policy proposal

The initializer writes the observed proposal at:

```text
.agentic/policies/architecture/project-policy.json
```

Keep observed facts that represent intentional boundaries, remove accidental
structure, and add decided semantics the adapter cannot infer:

- module and host roots;
- existing functional areas;
- observable projects and their owners;
- application, infrastructure, contract, and host roles;
- allowed dependencies;
- permitted source locations inside each host;
- prohibited technical-module and catch-all names.

Policy declares intent. The adapter obtains observed structure. The validator
compares both. Policy must never be written to hide a portable-rule violation.

## 6. Technology adapter

Use a built-in adapter unchanged when one supports the technology. Otherwise,
create a separately versioned Python distribution exposing an entry point in
the `agentic_architecture_kit.adapters` group:

```toml
[project.entry-points."agentic_architecture_kit.adapters"]
technology = "my_aak_adapter:observe"
```

The adapter only discovers modules, hosts, projects, dependencies, and source
files. It does not decide which architecture is valid or redefine rules. Pin
the extension distribution and exact version in `.agentic/toolchain.json`.

## 7. Waivers

`waivers.json` starts empty. Add a waiver only for a concrete, authorized
deviation. It identifies the rule, current `ruleDigest`, exact scope, decision,
reason, risk, authorizing ADR, and review conditions. Its result is `WAIVED`,
never `PASS`. A missing or stale digest prevents the waiver from applying.

## 7.1 Authority and semantic reviews

Replace the authority template principals with real repository users or teams
and mirror them in `.github/CODEOWNERS`. Configure every declared protected
branch using [`github-governance.md`](github-governance.md). A review record
requires an exact fingerprint, current `ruleDigest`, a full reachable ancestor
SHA, a declared principal, and approval evidence from the platform. The agent
must not create a review record merely because it can edit JSON.

## 8. Context bootstrap and expansion

Generate the initial repository index with `aak context index`. Use `locate` for the declared
starting point and expand with `references`, `tests`, and `impact`; keep the
reported declared/observed provenance and confidence.

The project must give an agent a small deterministic starting context:

```text
Task
Root AGENTS.md
Repository revision
Risk and permission policy
Authoritative build, test, and architecture commands
```

The agent then locates the owning module and feature area, reads the module
contract, invariants, ADRs, project policy, and waivers, and expands only through
concrete dependencies, consumers, data access, tests, or evidence gaps. It
records provenance and distinguishes declared facts, observed facts, inferences,
and open questions. Conversational memory is never required to continue work.

## 9. Completion validation

The initial project is incomplete until these checks run:

```bash
uvx --from agentic-architecture-kit==0.4.0 aak validate
uvx --from agentic-architecture-kit==0.4.0 aak validate --base-ref origin/main --fail-on-review
```

Use `aak explain RULE_ID` to inspect the current findings, scopes, evidence,
digest, reference, and any applied waiver or review. If a normative reference
does not resolve, validation fails; the agent does not infer its likely meaning.

The distribution's conformance suite runs before publication; consumers do not
copy or rerun those tests. The project's own build, tests, and project-specific
architecture tests also run. `REVIEW_REQUIRED` results are listed
and reviewed; they are not presented as automatic passes. A semantic review
within already delegated authority does not by itself require user interaction.
Persist that acceptance in `reviews.json` using the exact emitted fingerprint;
do not suppress the finding or convert it into a claimed mechanical pass.

## 10. Later evolution

Every later request first locates the owning module and cohesive feature area. A
new boundary is created only when new evidence justifies it. When a boundary
changes, code, policy, contracts, ADRs, validators, waivers, and evidence are
updated atomically.

The agent updates project policy as the project grows, but never merely to make
a failure disappear:

- a legitimate new boundary updates policy and its supporting decision;
- an accidental violation changes the code;
- a necessary authorized deviation creates a visible waiver;
- unresolved semantics remain `REVIEW_REQUIRED`.

CI supplies `--base-ref` so policy growth is compared with the target branch.
New boundary or dependency permissions without an existing decision reference
fail even when the code would otherwise be green.

Conversation is not architectural memory. At completion, another agent must be
able to continue by reading only the repository.
