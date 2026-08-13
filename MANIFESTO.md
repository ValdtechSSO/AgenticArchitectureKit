# Repository Architecture Manifesto for Coding Agents

## Initialization, evolution, and conformance protocol — revised version 2

[Español](docs/es/MANIFESTO.md) · [Language policy](docs/language-policy.md)

> **Status:** normative.
>
> **Scope:** this manifesto defines portable rules for repositories created and
> evolved by coding agents. Each project specializes those rules through its own
> policy. Exceptions require an explicit waiver and never silently change a
> portable rule.
>
> **Governing principle:** the agent reasons and proposes; the repository
> declares, locates, constrains, validates, and preserves evidence.

---

# 1. Purpose

This manifesto does not prescribe an exhaustive tree to copy. It defines a
protocol for producing the smallest correct architecture from currently
available knowledge and for growing it only when verifiable needs appear.

## 1.1 Primary objective: governed autonomy

> **An agent must be able to create, modify, and evolve a project autonomously
> within the boundaries decided by the team. The repository must provide enough
> context, policies, and validation for the agent to determine what it may do,
> where the change belongs, and how to prove the result conforms—without human
> intervention unless the request requires a product, risk, ownership, or
> authority decision that has not yet been defined. The repository must also
> organize and provide the minimum sufficient context for each task efficiently,
> progressively, and traceably, so the agent can quickly locate the relevant
> domain, ownership, contracts, decisions, dependencies, code, and tests without
> indiscriminate loading or conversational memory.**

Autonomy is the default behavior. The agent `MUST` continue when a request falls
inside already declared authority and boundaries. It does not seek confirmation
for reversible implementation decisions resolvable through existing contracts,
invariants, ADRs, policy, and evidence.

The agent escalates only when proceeding would assume a material decision the
team has not delegated, such as changing the product, accepting risk,
transferring ownership, weakening a rule, or performing an operation outside
granted authority. A missing secondary preference is not enough to interrupt
work.

Context access is an architectural responsibility. The repository `MUST`
provide a small deterministic bootstrap and `MUST` let the agent expand context
through ownership, contracts, dependencies, consumers, data, tests, and concrete
evidence. The agent `MUST NOT` replace progressive navigation with indiscriminate
repository loading.

Retrieved context `SHOULD` identify provenance and distinguish declared facts,
observed facts, inferences, and open questions. Conversational memory `MUST NOT`
be required to reconstruct the current architecture or continue development.

The target repository lets an agent answer:

```text
Which functional capability owns this request?
Where does the related behavior begin?
Which rules and invariants govern it?
Which code, data, and contracts does it affect?
Which dependencies are allowed?
Which tests and validations are mandatory?
Which evidence proves the change is complete?
Which deviations are authorized, and why?
```

Descriptive name:

> **Capability modules with cohesive vertical slices, incremental evolution,
> deterministic navigation, and evidence-based delivery.**

This manifesto belongs to *Agentic Software Engineering*. It does not define a
multi-agent system architecture or introduce a new meaning for the historical
AOSE acronym.

---

# 2. Normative language

`MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` express requirement level:

- `MUST` / `MUST NOT`: portable mandatory rule;
- `SHOULD` / `SHOULD NOT`: recommendation omitted only with an explicit reason;
- `MAY`: permitted option, never mandatory structure.

A project policy may specialize a portable rule. It cannot silently weaken one.
A deviation requires a bounded waiver.

---

# 3. Universal principles

## 3.1 Architecture follows current knowledge

> **Architectural decisions MUST be based on current requirements and observable
> project evidence. An agent MUST NOT introduce modules, projects, abstractions,
> shared components, or directory levels solely for anticipated future use.**

An uncertain future need is recorded as a risk, assumption, or question. It does
not become structure until a real consumer or boundary exists.

```text
Possible future need
→ documented risk or question
→ no structure yet
```

## 3.2 Structural economy

> **Every module, project, directory, abstraction, and shared component MUST be
> justified by current code or by an enforced boundary.**

Therefore:

- empty directories are not created to complete a template;
- every class does not automatically receive its own file;
- small cohesive classes may share a file when they are found, changed, and
  reviewed together;
- a class receives its own file when responsibility, navigation, or evolution
  becomes independent;
- a project or assembly exists only when it enforces dependency, deployment,
  ownership, language, publication, or runtime boundaries;
- `Shared`, `Common`, `BuildingBlocks`, and common abstractions require current
  consumers and explicit ownership;
- a larger tree is not evidence of a more mature architecture.

## 3.3 Organize by functional capability

Modules represent product capabilities:

```text
Modules/
├── Competitions/
├── Classification/
├── Payments/
└── Identity/
```

Technical categories are not product modules:

```text
Git/
Providers/
Repositories/
Validation/
Services/
```

Those responsibilities stay inside the infrastructure of the module that uses
them unless they form a genuinely independent platform with its own contract,
ownership, and lifecycle.

## 3.4 Vertical slices and feature cohesion

New behavior begins in the owning module and the smallest functional area that
owns its vocabulary, state, and lifecycle:

```text
src/Modules/{Module}/Features/{FeatureArea}/
```

> **A command, handler, endpoint, or use case MUST NOT automatically create a new
> root feature directory.**

Operations remain in one feature area when they:

- act on the same concept or aggregate;
- share state, storage, or lifecycle;
- follow the same invariants;
- require substantially the same review context;
- would gain navigation cost without a real boundary if separated.

A new root feature requires observable independence in vocabulary, ownership,
invariants, risk, dependencies, or evolution.

Valid example:

```text
Modules/Planning/Features/
├── Plan/
│   ├── PlanOrchestrator.cs
│   ├── Prompts/
│   ├── Schemas/
│   └── Validation/
├── Environment/
│   └── DoctorService.cs
└── Run/
    ├── ShowRunService.cs
    └── PruneRunService.cs
```

`ShowRun` and `PruneRun` remain together because they share the `Run` concept,
storage model, and lifecycle.

## 3.5 Clean Architecture is local, not a global taxonomy

When useful, a module may contain:

```text
Module/
├── Domain/
├── Contracts/
├── Features/
└── Infrastructure/
```

These are options, not placeholders. A module without its own domain rules does
not create `Domain/`. A module without technical adapters does not create
`Infrastructure/`.

## 3.6 Declaration and observation are different

Declared architecture expresses intent and ownership. Observed architecture is
derived from source, configuration, and build artifacts.

```text
Declared                         Observed
-----------------------------    --------------------------------
module purpose                   projects and assemblies
functional aliases               namespaces and symbols
ownership                        dependencies
risk                             endpoints and handlers
invariants and ADRs              data access and tests
```

> **Architectural conformance MUST compare declared architecture with observed
> architecture. Validating policy or contract syntax alone is not architectural
> conformance.**

## 3.7 Completion requires evidence

An agent's assertion never satisfies a quality gate by itself. Completion is
derived from build, tests, static analysis, risk-specific validation,
revision-bound evidence, and required approvals.

---

# 4. Conformance layers

Architecture conformance separates three layers.

## 4.1 Portable manifesto rules

Portable rules have stable identifiers:

```text
POL001  Project architecture policy is valid
ARC001  Declared and observed architecture agree
MOD001  Every module has a semantic contract
MOD002  Module id matches its module root
MOD003  Technical categories are not product modules
FEAT001 Application behavior belongs to an owning feature area
HOST001 Hosts do not own application behavior
DEP001  Modules do not depend on hosts
DEP002  Cross-module access uses public contracts
DEP003  Observed project dependencies are authorized
OWN001  Authoritative data has one owner
STR001  Speculative structure is prohibited
DOC001  Invariant and ADR references resolve
WVR001  Waivers are explicit and valid
```

Portable rules belong to the executable catalog shipped with this manifesto,
not to a particular repository. Each catalog entry declares its evaluator,
inputs, and whether it can resolve automatically.

## 4.2 Project-specific policy

Each project declares how it materializes the manifesto. Policy may describe:

- module and host roots;
- cohesive feature areas;
- compilable projects and ownership;
- application, infrastructure, contract, and host roles;
- allowed dependencies;
- host source locations;
- project-specific structural restrictions.

Policy conforms to `architecture-policy.schema.json`. It may contain structural
information because its purpose is to validate physical materialization. It
does not duplicate reliably derivable facts unless they express a desired limit
that must be compared with observation.

Minimal excerpt:

```json
{
  "version": 1,
  "project": "acme",
  "adapter": "dotnet",
  "roots": {
    "modules": "src/Modules",
    "hosts": "src/Hosts"
  },
  "modules": [
    {
      "id": "orders",
      "root": "src/Modules/Orders",
      "featureRoot": "src/Modules/Orders/Features",
      "featureAreas": ["OrderLifecycle"]
    }
  ],
  "hosts": [
    {
      "id": "api",
      "root": "src/Hosts/Api",
      "allowedSourcePatterns": ["Program.cs", "Endpoints/*.cs"]
    }
  ]
}
```

The complete contract and neutral template are distributed with the kit.

## 4.3 Architecture waivers

A waiver authorizes one concrete deviation without changing a portable rule.

```json
{
  "version": 1,
  "waivers": [
    {
      "id": "ACME-ARCH-001",
      "rule": "DEP002",
      "scope": "src/Modules/Reporting/Features/LegacyImport",
      "decision": "Temporarily allow direct Billing infrastructure access.",
      "reason": "The import has not migrated to Billing contracts.",
      "risk": "Reporting remains coupled to an internal implementation.",
      "authorizedBy": [
        "architecture/decisions/ADR-021-legacy-import-migration.md"
      ],
      "expiresOn": "2026-12-31",
      "reviewWhen": [
        "Billing publishes the required import contract",
        "the legacy import changes"
      ]
    }
  ]
}
```

Every waiver `MUST` include:

- affected rule;
- exact scope;
- decision and reason;
- authorizing ADR or authority;
- relevant risk or tradeoff;
- review condition or expiration when applicable.

A waiver never silently turns a deviation into `PASS`. Conformance states are:

```text
PASS
FAIL
WAIVED
NOT_APPLICABLE
REVIEW_REQUIRED
```

## 4.4 Separation rule

> **Conformance MUST separate portable manifesto rules, project-specific policy,
> and authorized waivers. A project policy or waiver MUST NOT silently weaken or
> redefine a portable rule.**

---

# 5. Project initialization protocol

This protocol applies to an empty repository or a product without established
architecture.

## 5.1 Initial discovery

The agent begins with available information:

- current product objective and scope;
- known actors and operations;
- known data and ownership;
- required external interfaces;
- language, runtime, and deployment constraints;
- known risks and invariants;
- available build and test commands.

Missing information is recorded as an assumption or question. It is not filled
with invented architecture.

## 5.2 Capability identification

The agent groups behavior by vocabulary, ownership, rules, and lifecycle. It
creates multiple modules only when real functional boundaries exist.

Decision questions:

```text
Does it have its own vocabulary?
Does it own data or state?
Does it have its own invariants?
Can it evolve independently?
Does it need a contract with another current capability?
```

A negative or unknown answer favors keeping behavior in an existing module or
starting with one module.

## 5.3 Host identification

A host represents a current way to execute or expose the product:

```text
Hosts/
├── Api/
├── Cli/
├── Worker/
└── Mcp/
```

Only currently required hosts are created. A host adapts input and output,
composes dependencies, and delegates. It does not own application behavior.

## 5.4 Compilable boundary identification

A new project, package, or assembly needs at least one current reason:

- prevent prohibited dependencies;
- separate deployments;
- separate runtime or language;
- isolate ownership;
- publish an independent contract.

“It may grow” is not sufficient.

## 5.5 Minimum deliverables

The agent creates only applicable artifacts:

```text
repository/
├── AGENTS.md
├── architecture/
│   ├── system-overview.md
│   └── decisions/
├── domain/
│   ├── global-invariants.md
│   └── contexts/
├── src/
│   ├── Modules/
│   │   └── {CurrentModule}/
│   │       ├── AGENTS.md
│   │       ├── module.contract.yml
│   │       └── Features/
│   └── Hosts/                         # only when a host exists
├── tests/
│   └── Architecture/
└── .agentic/
    ├── contracts/
    └── policies/
        └── architecture/
```

Directories without current content or responsibility are omitted.

## 5.6 Executable initial architecture

Initialization does not end with a tree. The agent `MUST` create validation for
the boundaries it declares. At minimum it:

- discovers modules and hosts;
- validates contracts and identifiers;
- checks allowed dependencies;
- prevents modules from depending on hosts;
- resolves invariant and ADR references;
- compares declared boundaries with observed projects and references;
- emits `PASS`, `FAIL`, `WAIVED`, `NOT_APPLICABLE`, or `REVIEW_REQUIRED`.

---

# 6. Evolution protocol

Every implementation plan or development request executes this protocol.

## 6.1 Locate before creating

The agent decides in this order:

1. Which module owns the request?
2. Which feature area owns its concept and lifecycle?
3. Is it an operation inside that feature?
4. Does current complexity justify an operation subdirectory?
5. Is there real shared logic that should be promoted?
6. Has an independent capability appeared that justifies a module?
7. Is a new assembly needed to enforce a verifiable boundary?

The default is to extend an existing cohesive boundary, not create structure.

## 6.2 Placement rule

Behavior remains under `Features/{FeatureArea}` when it:

- orchestrates an operation of that capability;
- transforms input or output;
- contains feature-specific validation;
- coordinates ports for that behavior;
- is not an autonomous domain rule.

It is promoted to `Domain/` when it expresses infrastructure-independent domain
meaning used by current behavior. It is promoted to `Contracts/` when another
module or host consumes it as a public API. It belongs in `Infrastructure/` when
it implements filesystem, network, persistence, process, messaging, SDK, or
external-service access.

## 6.3 Justified growth

### New operation subdirectory

Create one when the operation has enough content, navigation cost, or
independent evolution. A command alone is not justification.

### New root feature

Create one when vocabulary, state, invariants, risk, or lifecycle is independent
inside the module.

### New module

Create one when a functional capability gains independent ownership and
contracts. Never create a product module for a technical category.

### New assembly or package

Create one only when it enforces dependency, deployment, runtime, language,
distribution, publication, or ownership boundaries.

### Shared component

Create one only with at least two current consumers, cohesive responsibility,
and explicit ownership. Small duplication may be preferable to premature
abstraction.

## 6.4 Atomic architectural change

> **A change that modifies an architectural boundary is incomplete until the
> declared architecture, observed structure, enforcement rules, and
> documentation agree.**

A boundary change updates every applicable artifact together:

- code and build projects;
- module semantic contract;
- local `AGENTS.md`;
- domain documents;
- ADR;
- project policy;
- architecture tests;
- structural index;
- waivers;
- change evidence.

## 6.5 Authority of plans and requests

An implementation plan is an input, not superior architectural authority.

```text
Request or plan
        ↓
Portable manifesto rules
        ↓
Project policy and waivers
        ↓
Contracts, invariants, and ADRs
        ↓
Implementation
```

When a plan conflicts with a rule:

1. the agent attempts a compatible solution;
2. if deviation is necessary, it proposes an ADR and waiver;
3. if product, ownership, risk, or authority changes materially, it escalates;
4. it never introduces an exception silently.

---

# 7. Permitted structural grammar

These are possible locations, not a mandatory tree:

```text
repository/
├── AGENTS.md
├── architecture/                    # maintained decisions and boundaries
├── domain/                          # vocabulary and invariants
├── src/
│   ├── Modules/                     # functional capabilities
│   ├── Hosts/                       # current execution mechanisms
│   └── BuildingBlocks/              # exceptional, real consumers required
├── web/                             # independent frontend, when present
├── tests/
├── docs/
├── tools/
└── .agentic/
```

A module materializes only the areas it needs:

```text
src/Modules/{Module}/
├── AGENTS.md                         # required
├── module.contract.yml               # required
├── Domain/                           # optional
├── Contracts/                        # optional
├── Features/                         # when behavior exists
└── Infrastructure/                   # when technical adapters exist
```

Catch-all directories such as `Managers`, `Helpers`, `Utils`, `Common`, and
`Application/Services` are prohibited by default because they hide ownership.
A bounded waiver with clear responsibility is required to permit one.

---

# 8. Module semantic contract

Every module maintains:

```text
src/Modules/{Module}/module.contract.yml
```

Example:

```yaml
id: classification
name: Classification
purpose: >
  Calculates standings, rankings, and tie-break rules.
intent:
  aliases:
    - classification
    - standings
    - ranking
    - league table
ownership:
  domain: competition-classification
  authoritative_data:
    - ClassificationSnapshots
risk:
  default: high
  reasons:
    - Business-critical calculation
invariants:
  - domain/contexts/classification.md#team-inclusion
  - domain/contexts/classification.md#disqualified-teams
architecture_decisions:
  - architecture/decisions/ADR-014-classification-rules.md
```

The contract contains semantics that cannot be derived reliably:

- purpose;
- vocabulary and intent;
- ownership;
- risk;
- invariants;
- applicable ADRs.

It does not contain derivable structural facts:

```yaml
paths:
entrypoints:
handlers:
classes:
tests:
entities_read:
entities_written:
routes:
```

Contract conformance covers form and meaning:

- schema is valid;
- `id` matches the observed module;
- invariant and ADR references resolve;
- aliases do not collide without resolution;
- declared ownership agrees with observed access;
- authoritative data is not written directly by another module.

---

# 9. Observed architecture and generated index

Real structure is derived from the repository through language and platform
adapters. A generated index may live at:

```text
.agentic/generated/index/
├── repository.json
├── projects.json
├── modules.json
├── symbols.json
├── references.json
├── dependencies.json
├── endpoints.json
├── handlers.json
├── entities.json
├── data-access.json
├── tests.json
└── documents.json
```

Only indices relevant to the project are generated. Each index records at least:

```json
{
  "repositoryRevision": "73a9c45",
  "generatorVersion": "1.0.0",
  "generatedAt": "2026-07-27T10:00:00Z"
}
```

An index that does not match the code revision is stale and cannot satisfy a
validation gate.

Technology adapters may extract:

- projects, packages, or assemblies;
- namespaces, symbols, and references;
- endpoints, handlers, and composition registrations;
- entities, tables, and migrations;
- event producers and consumers;
- module dependencies;
- related tests.

The portable engine evaluates a common architectural model. .NET, Java,
TypeScript, Python, and other adapters construct that model without turning
technology-specific facts into universal rules.

---

# 10. Architecture validation

## 10.1 Pipeline

```text
Source and configuration
        ↓
Observed architecture model
        ↓
Portable rules + project policy
        ↓
Comparison with contracts and ADRs
        ↓
Visible waiver application
        ↓
PASS / FAIL / WAIVED / NOT_APPLICABLE / REVIEW_REQUIRED
```

## 10.2 Automatic validation

When the platform permits, the validator checks:

- modules, hosts, and contracts exist where declared;
- identifiers and references are valid;
- projects and dependencies follow policy;
- modules do not depend on hosts;
- hosts do not contain application behavior outside declared adapter paths;
- infrastructure does not leak into domain or application boundaries;
- cross-module access uses public contracts;
- namespaces or packages correspond to ownership;
- handlers and endpoints belong to feature areas;
- tests reflect modules and features;
- declared data ownership agrees with observed reads and writes;
- waivers have valid scope, authority, and lifetime;
- generated indices match the current revision.

## 10.3 Semantic review

Some decisions are semantic and must not be disguised as deterministic checks:

- whether two operations are truly cohesive;
- whether a capability deserves a module;
- whether an abstraction is worth its cost;
- whether a functional name expresses ownership correctly;
- whether a waiver remains reasonable.

The analyzer may produce evidence and heuristics, but returns
`REVIEW_REQUIRED` when it cannot prove the rule. `REVIEW_REQUIRED` is not
automatically a request for user input: the agent completes the review when the
decision falls within delegated authority and escalates only when material
authority is missing.

## 10.4 Supplied reference implementation

The manifesto `MUST` ship with a versioned general validator. An agent does not
reimplement portable rules for each repository:

```text
tools/architecture/
├── rules.json                    # stable portable catalog
├── validate.py                   # CLI and pipeline assembly
├── validator/
│   ├── engine.py                 # evaluation and waiver application
│   ├── contracts.py              # input and output contracts
│   └── adapters/
│       └── dotnet.py             # technology observation
└── tests/                        # validator conformance
```

The project supplies only project-specific configuration:

```text
.agentic/
├── contracts/schemas/
│   ├── architecture-policy.schema.json
│   ├── architecture-waivers.schema.json
│   └── architecture-result.schema.json
└── policies/architecture/
    ├── project-policy.json
    └── waivers.json
```

An agent may add a missing technology adapter or project-specific check. It may
not silently redefine a portable rule. A rule that cannot be demonstrated
returns `REVIEW_REQUIRED`.

Reference commands:

```bash
./tools/scripts/validate-architecture.sh
./tools/scripts/validate-architecture.sh --format json
./tools/scripts/validate-architecture.sh --fail-on-review
./tools/scripts/validate-architecture.sh --list-rules
```

`FAIL` returns exit code 1. Invalid input or configuration returns exit code 2.
`REVIEW_REQUIRED` remains visible and may be promoted to a blocking gate through
`--fail-on-review`.

## 10.5 Portable and project tests

```text
tools/architecture/tests/             # portable rules and engine
tests/Architecture/                   # project-specific decisions
```

The reference validator is tested at minimum against:

- a conforming architecture;
- an unauthorized dependency;
- a broken document reference;
- a valid, visible, bounded waiver;
- invalid contracts or configuration;
- an attempted project-policy weakening of a portable rule.

Project-specific tests extend enforcement when a decision depends on domain or
technology semantics the common model cannot observe.

---

# 11. `AGENTS.md` as a router

## 11.1 Root router

The root `AGENTS.md` is brief and contains:

- repository purpose;
- authoritative commands;
- critical rules;
- module and host map;
- initial workflow;
- prohibited operations.

It is not a copy of the whole architecture or domain.

## 11.2 Module router

Every module maintains local guidance:

```markdown
# Classification module

## Purpose

Calculates competition standings and tie-break rules.

## Read before changing

- `module.contract.yml`
- `/domain/contexts/classification.md`
- relevant ADRs

## Commands

- targeted module tests
- architecture validation

## Critical rules

- Teams without games remain visible.
- Performance validation is required for query changes.
```

Derivable structural facts are not duplicated here.

---

# 12. Progressive navigation and context

The agent begins with minimum context:

```text
Task
Root AGENTS.md
Repository revision
Risk and permission policies
Available navigation tools
```

It then locates and expands:

```text
Minimum bootstrap
→ Locate owning module and feature area
→ Read contract, invariants, ADRs, policy, and waivers
→ Inspect observed entry points
→ Expand through dependencies, consumers, data, and tests
→ Analyze impact
→ Implement
```

Recommended navigation capabilities:

```bash
agentic locate "where is classification calculated?"
agentic symbol ClassificationCalculator
agentic references ClassificationCalculator
agentic tests find ClassificationCalculator
agentic impact src/Modules/Classification/Features/Standings/
agentic data owner ClassificationSnapshots
agentic decisions find "classification ordering"
```

These commands illustrate capabilities, not a mandatory tool brand. Ordinary
repository search and language tooling may provide them.

Navigation output always distinguishes:

- declared semantics;
- observed structure;
- inferences or heuristics;
- confidence;
- repository revision used.

The context record preserves provenance and public reasons for expansion. It
never records or requires private chain-of-thought.

Context expansion follows a concrete need. Direct dependencies, consumers,
contracts, data access, tests, and evidence gaps are valid expansion paths.
Speculative whole-repository crawling is prohibited.

---

# 13. Control and evidence

Policies may live at:

```text
.agentic/policies/
├── architecture/
│   ├── project-policy.json
│   └── waivers.json
├── risk-levels.yml
├── permissions.yml
├── quality-gates.yml
└── state-transitions.yml
```

Task evidence is tied to a repository revision:

```text
.agentic/runtime/evidence/{task-id}/{revision}/
├── manifest.json
├── architecture.json
├── build.json
├── tests.json
├── security.json
├── performance.json
├── review.json
└── unresolved-risks.json
```

Example:

```json
{
  "taskId": "AG-142",
  "revision": "73a9c45",
  "check": "architecture",
  "tool": "agentic-architecture-validator",
  "command": "./tools/scripts/validate-architecture.sh --format json",
  "exitCode": 0,
  "result": "PASS"
}
```

If the revision changes, prior evidence no longer satisfies the gate.

Negative evidence is also recorded:

- checks not run and the reason;
- inconclusive results;
- flaky tests;
- waivers used;
- pending semantic reviews;
- unresolved risks.

Evidence classes:

| Class | Examples |
|---|---|
| Deterministic | Build, tests, schema, dependencies |
| Static | Linter, SAST, ownership analysis |
| Observational | Benchmark, trace, metrics |
| Probabilistic | Agent or LLM review |
| Declarative | Unsupported assertion |

A declarative assertion never satisfies a gate by itself.

---

# 14. Tests

Tests are organized by type, then by module, feature area, or host when that
distinction improves navigation:

```text
tests/
├── Unit/{Module}/{FeatureArea}/
├── Integration/{Module}/{FeatureArea}/
├── Contract/{Module}/
├── Architecture/
├── EndToEnd/{Host}/
├── Performance/{Module}/
├── Security/{Module}/
└── Agentic/
```

Empty categories are omitted. A small project may keep several feature tests
directly under `Unit/{Module}` while they remain easy to locate.

Architecture tests are product code, not auxiliary documentation. They protect:

- applicable portable rules;
- project-specific policy;
- boundaries between modules and hosts;
- waiver validity;
- correspondence between declaration and observation.

---

# 15. Accumulated architectural state

After every change, the repository contains enough information for another
agent to continue without prior conversation:

```text
Portable manifesto
+ project policy
+ module contracts
+ AGENTS.md routers
+ domain and invariants
+ ADRs
+ observed architecture
+ architecture tests
+ waivers
+ evidence
= current architectural state
```

Conversational memory is not an architectural source of truth.

---

# 16. Adoption in an existing repository

Do not perform a mass migration merely to reproduce this grammar.

Recommended order:

1. inventory current capabilities, hosts, and dependencies;
2. declare policy and contracts without falsifying observed state;
3. record debt and temporary waivers;
4. protect critical boundaries first;
5. reorganize when touching an area or when benefit justifies migration;
6. remove waivers as declaration and observation converge.

A partially migrated architecture reports `WAIVED` or `REVIEW_REQUIRED`; it
does not present itself as fully conforming.

---

# 17. Contents of `.agentic`

Only used areas are materialized:

```text
.agentic/
├── contracts/                # policy, waiver, result, and module schemas
├── policies/                 # architecture, risk, permissions, and gates
├── workflows/                # reusable operating cycles
├── skills/                   # specialized procedures
├── prompts/                  # engineering-process prompts
├── templates/                # worksheets, handoffs, and evidence
├── generated/                # reproducible derived data
├── runtime/                  # state and traces
└── evals/                    # experiments and results
```

Prompts that are product behavior live beside their owning feature. Cross-cutting
engineering prompts live under `.agentic/prompts`.

Normally versioned:

- architecture and domain documents;
- contracts and policies;
- ADRs and waivers;
- workflows, skills, and templates;
- schemas, datasets, graders, and tooling.

Indices may be versioned or regenerated depending on cost. Runtime state,
caches, traces, and large results are normally retained as CI or observability
artifacts.

---

# 18. Falsifiable evaluation

The architecture is useful only if it measurably improves outcomes over a
conventional repository.

Suggested experimental conditions:

```text
Baseline
  conventional repository + standard tools

Static Context
  structure + AGENTS.md + fixed initial context

Adaptive Repository
  contracts + index + progressive navigation + evidence gates
```

Metrics:

- acceptance tests passed;
- defects and merge blockers;
- scope or module violations;
- time to first relevant file;
- location and test-selection precision;
- impact-analysis precision;
- false completion claims;
- tokens, tool calls, cost, and duration;
- relevant context versus total loaded context;
- unnecessary human escalations;
- material decisions made without authority.

Semantic search, MCP, and multi-agent collaboration are optional extensions.
They are added only when evaluation demonstrates improvement over simpler
mechanisms.

---

# 19. Complete operational flow

```text
Request
  ↓
Minimum bootstrap
  ↓
Locate owning module and feature area
  ↓
Read contract, invariants, ADRs, policy, and waivers
  ↓
Compare declared and observed architecture
  ↓
Extend an existing boundary or justify a new one
  ↓
Implement autonomously within delegated authority
  ↓
Update declaration and enforcement when a boundary changes
  ↓
Run risk-appropriate validation
  ↓
Retain revision-bound evidence
  ↓
PASS / FAIL / WAIVED / NOT_APPLICABLE / REVIEW_REQUIRED
  ↓
Escalate only an undefined material decision
  ↓
Human or automated delivery according to policy
```

---

# 20. Closed normative decisions

1. The manifesto is a decision protocol, not an exhaustive template.
2. Governed agent autonomy is the primary objective.
3. Human escalation is exceptional and requires an undefined material decision.
4. The repository provides minimum sufficient context progressively and
   traceably.
5. Architecture is created from current needs and observable evidence.
6. Product structure follows functional capabilities and cohesive feature areas.
7. A command or use case does not automatically create a root feature.
8. Technical modules are prohibited unless they are real independently owned
   platforms.
9. Structure is materialized on demand; mandatory placeholders do not exist.
10. An assembly or package needs a verifiable boundary.
11. Shared code needs current consumers and explicit ownership.
12. Maintained contracts contain non-derivable semantics.
13. Declared architecture is compared with observed architecture.
14. Portable rules, project policy, and waivers are separate layers.
15. Waivers are visible, bounded, authorized, and reviewable.
16. A boundary change updates code, declaration, enforcement, and evidence
    atomically.
17. An implementation plan cannot silently ignore architecture.
18. `AGENTS.md` is a router, not an encyclopedia.
19. Context is recovered progressively from a deterministic bootstrap.
20. Conversation is not architectural memory.
21. Evidence is tied to a repository revision.
22. An agent assertion does not satisfy a quality gate.
23. Semantic uncertainty is reported as `REVIEW_REQUIRED`, not fabricated
    certainty.
24. Architecture utility must be falsifiable through evaluation.
25. Complex tools are added only when they demonstrate value.

---

# 21. Final success criterion

The manifesto succeeds when a new agent can:

1. create the smallest justified architecture from current knowledge;
2. distinguish known facts, assumptions, and unknowns;
3. locate ownership, module, and feature area for a later request;
4. retrieve minimum sufficient context without indiscriminate crawling;
5. evolve the project without speculative structure;
6. recognize when a genuinely new boundary is justified;
7. update declared and observed architecture atomically;
8. validate portable rules, project decisions, and waivers;
9. identify affected code, data, dependencies, and tests;
10. make routine implementation decisions without unnecessary human questions;
11. escalate only when a material decision lies outside delegated authority;
12. produce revision-bound evidence;
13. hand the repository to another agent without conversational memory.

The directory tree is a visible consequence of this protocol. The real
architecture is the coherent set of decisions, ownership, code, validation,
context routes, and evidence that lets the repository explain and protect its
own growth while enabling autonomous work.
