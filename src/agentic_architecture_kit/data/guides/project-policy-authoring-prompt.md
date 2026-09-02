# Agent prompt for project policy

Use this prompt to instruct a coding agent to create, review, reconcile, or
update an AAK `project-policy.json`. The user describes product intent and
material boundaries in plain language. The agent owns observation, evidence
classification, JSON authoring, schema compliance, cross-document consistency,
validation, and reporting.

This guide is operational, not a second normative source. The exact pinned AAK
core, policy schema, adapter output, contracts, decisions, and rule references
remain authoritative.

## 1. Mission and minimum user request

~~~text
Repository root: <DISCOVER_FROM_WORKSPACE_OR_SUPPLY>
Mode: <CREATE_MINIMUM|REVIEW_OBSERVED_PROPOSAL|UPDATE_FOR_CHANGE|RECONCILE_DRIFT>
Requested product or architecture outcome: <PLAIN_LANGUAGE_INTENT>
Known boundary decisions: <OPTIONAL_OR_UNKNOWN>
Known constraints: <OPTIONAL_OR_UNKNOWN>
Base revision for comparison: <DISCOVER_OR_UNKNOWN>

Create or update the smallest truthful project policy supported by current
intent, repository evidence, and authorized decisions. The user supplies
meaning, not JSON. You own adapter observation, field mapping, identifiers,
paths, selectors, formatting, references, validation, and the completion
report.

Do not ask the user to choose JSON properties, schemas, path syntax, namespace
or package patterns, project roles, dependency-selector syntax, or validation
commands. Ask only when proceeding would invent or materially change capability
ownership, a host boundary, a build/runtime boundary, dependency direction,
normative enforcement, accepted risk, or authority.
~~~

The minimum usable human brief is one sentence, for example: “Adopt the current
repository without treating technical folders as product modules” or “Add the
approved reporting capability.” Repository root, pinned version, adapter, mode,
and current policy should be discovered from the working context whenever
possible.

## 2. What policy declares

Keep these responsibilities separate:

~~~text
User or delegated architecture authority
  decides product boundaries, ownership, dependency direction, enforcement,
  and material architectural change

Technology adapter
  observes technology-specific projects, source identities, roots,
  dependencies, and source files

project-policy.json
  declares which observed boundaries are intentional, who owns them, their
  roles, permitted dependency direction, and project-specific structural scope

Module contracts and domain documents
  declare non-derivable product meaning, ownership, risk, and invariants

Architecture decisions
  explain and authorize material boundary or dependency changes

Validator
  compares declared intent with observed evidence and portable rules
~~~

Policy is neither a generated inventory nor a domain model. A folder, package,
namespace, project file, or dependency can prove that structure exists; it
cannot by itself prove that the structure is intentional or authorized. Never
copy adapter output blindly into policy merely to obtain `PASS`.

## 3. Mandatory preflight and evidence classes

Before editing:

~~~text
1. Read repository instructions and run the architecture gate before change.
2. Run and read `aak core` from the exact version pinned in toolchain.json.
3. Read the complete bundled architecture-policy schema and load POL001,
   ARC001, MOD001, MOD003, FEAT001, HOST001, DEP001, DEP002, DEP003, CHG001,
   STR001, and DOC001 through `aak explain` or finding references.
4. Read the existing policy, toolchain, module contracts, local routers,
   system overview, applicable domain documents, ADRs, waivers, and base policy.
5. Run the selected adapter through `aak validate --format json` and inspect the
   complete declared-versus-observed evidence. Use `aak init` or `aak adopt`
   output as a proposal, never as approval.
6. Inspect current build manifests, source identities, dependency edges, tests,
   execution entry points, and actual module/host roots.
7. Classify every proposed value as AUTHORIZED_DECISION, MAINTAINED_DECLARATION,
   OBSERVED_FACT, INFERENCE, ASSUMPTION, or UNKNOWN and record its source.
8. Compare with the target base revision whenever policy already exists so new
   permissions and reductions in enforcement remain visible to CHG001.
~~~

Evidence precedence depends on the question. The adapter is authoritative for
what it can mechanically observe. Accepted decisions and maintained semantic
documents are authoritative for intent. When they disagree, classify the cause;
do not silently rewrite either side.

## 4. Property evidence contract

Populate the policy using this matrix:

| Property | What it declares | Reliable evidence | Prohibited shortcut |
|---|---|---|---|
| `$schema`, `version` | Exact policy contract consumed by the pinned kit. | Bundled schema and existing compatible document. | Do not copy a newer URL or version from memory. |
| `project` | Stable machine identity of this product repository. | Existing policy, package/product identity, or explicit project decision. | Do not derive it from a temporary directory or workstation path. |
| `adapter` | Technology observer selected for this repository. | Installed pinned adapter plus supported repository artifacts. | Do not choose an adapter because its output is more permissive. |
| `adapterConfig` | Adapter-specific observation configuration only. | The selected adapter's documented contract and real observation need. | Do not encode portable rules or product decisions here. |
| `roots.modules`, `roots.hosts` | Search conventions for capability and host boundaries. | Actual or explicitly authorized repository layout. | Do not create empty architecture merely to match a template. |
| `projectSearchRoots` | Locations in which build units are observable. | Build/package layout and adapter contract. | Do not narrow the roots to hide an unwanted project. |
| `structureSearchRoots` | Locations governed for structural checks. | Current product source scope and explicit exclusions. | Do not exclude a violating directory to obtain `PASS`. |
| `moduleContract` | Contract filename, schema, and forbidden structural inventory fields. | Pinned AAK defaults or an explicitly compatible project convention. | Do not weaken forbidden fields to duplicate generated structure in contracts. |
| `technicalModuleNames` | Names that cannot masquerade as functional capabilities. | Portable defaults plus stable project technology vocabulary. | Do not remove a name merely because an existing technical module uses it. |
| `forbiddenDirectoryNames` | Catch-all directory names prohibited in governed structure. | Portable defaults plus explicit project-specific structural rules. | Do not use this list for arbitrary style preferences or transient naming. |
| `modules[].id` | Stable identity of a functional capability. | Authorized capability vocabulary and matching module contract. | Do not promote a layer, framework, folder, or team name to a module. |
| `modules[].root` | Real source root owned by the module. | Adapter observation reconciled with the capability decision. | A directory alone does not justify the module. |
| `modules[].featureRoot`, `featureAreas` | Governed cohesive application-behavior areas. | Current meaningful behavior, vocabulary, state, invariants, and lifecycle. | Do not make every handler, endpoint, command, or folder a root feature. |
| `modules[].namespacePatterns` | Source identities mechanically belonging to the module. | Source declarations and adapter-supported package/namespace evidence. | Do not infer them from display or assembly names the adapter does not trust. |
| `modules[].contractNamespacePatterns` | Source identities that form a public cross-module contract. | A current external consumer and an explicit public-contract boundary. | Do not expose implementation namespaces speculatively. |
| `modules[].decisionRefs` | Decisions governing a material module boundary. | Existing resolvable accepted ADRs or authorized decision documents. | Do not fabricate a reference or cite an unrelated ADR. |
| `hosts[].id`, `root` | Stable identity and real root of an execution/adaptation boundary. | Current execution, delivery, scheduling, or composition need. | Do not use a host to own application behavior. |
| `hosts[].allowedSourcePatterns` | Source allowed to perform host adaptation and composition. | Actual minimal entry points and adapter-observed relative paths. | Do not use broad patterns that conceal application behavior in the host. |
| `hosts[].namespacePatterns` | Source identities mechanically belonging to the host. | Source declarations and adapter-supported evidence. | Do not claim identities absent from source. |
| `hosts[].decisionRefs` | Decisions governing a material host boundary. | Resolvable accepted decision for the current host need. | Do not create a host for possible future delivery mechanisms. |
| `projects[].path`, `name` | Exact observed build unit. | Adapter-supported manifests and their real declared names. | Do not invent a project solely to mirror a folder. |
| `projects[].owner` | Module or host accountable for the build unit. | Root specificity, maintained ownership, and authorized boundary decision. | Technical proximity or a reference edge alone does not establish ownership. |
| `projects[].role` | Architectural role enforced by the build unit. | Observable test evidence, current contents, consumers, and decided boundary. | Do not label production code as `test` or `contracts` to weaken dependency rules. |
| `projects[].publicContract` | Whether a contracts build unit is an allowed public target. | Current cross-module consumer plus explicit contract decision. | Do not mark internal application code public for convenience. |
| `projects[].decisionRefs` | Decisions supporting a material build-unit boundary. | Resolvable accepted decision explaining what boundary the unit enforces. | Do not add a project merely because the language permits it. |
| `allowedProjectDependencies[]` | Exact currently authorized dependency edges. | Observed edge plus valid ownership, role, direction, consumer, and decision. | Observation is never authorization; do not bulk-copy every edge. |
| `dependencyRules[]` | Scalable permission for a class of present and future edges. | Explicit architectural direction and a resolvable decision justifying the selector breadth. | Do not replace precise edges with a broad selector merely to reduce maintenance. |

Omit optional properties when they have no current meaning or reliable evidence.
Use empty arrays only when “none currently declared” is true, not as a way to
avoid observing existing architecture.

## 5. Policy evidence ledger

Before editing, produce a ledger in the task report rather than in the JSON:

| Policy subject | Proposed declaration | Evidence and class | Observed agreement | Base delta | Decision needed |
|---|---|---|---|---|---|
| Global scope and adapter | ... | ... | yes/no/unknown | none/add/change | yes/no |
| Each module | ... | ... | yes/no/unknown | none/add/change/remove | yes/no |
| Each host | ... | ... | yes/no/unknown | none/add/change/remove | yes/no |
| Each project and role | ... | ... | yes/no/unknown | none/add/change/remove | yes/no |
| Each exact dependency | ... | ... | yes/no/unknown | none/add/remove | yes/no |
| Each dependency rule | ... | ... | yes/no/unknown | none/add/change/remove | yes/no |
| Structural enforcement | ... | ... | yes/no/unknown | none/increase/reduce | yes/no |

Every row that grants a new boundary, public contract, dependency permission,
or reduction of enforcement must identify the authorizing decision. Mechanical
values such as paths may be derived after the semantic decision is established.

## 6. Mode-specific authoring algorithm

### `CREATE_MINIMUM`

Start with the selected adapter and truthful search scope. Keep modules, hosts,
projects, and permissions empty until current product requirements and actual or
immediately materialized structure justify them. Do not copy the sample policy.

### `REVIEW_OBSERVED_PROPOSAL`

For every adapter-proposed module, host, project, role, namespace, and dependency:

1. confirm the observed fact is current and correctly identified;
2. decide whether it represents intended architecture or accidental drift;
3. verify functional ownership and boundary justification;
4. retain it only when intention and evidence agree;
5. otherwise correct the implementation, classification, adapter observation,
   or proposal instead of legitimizing the accident;
6. create missing semantic contracts only through their authoring prompt and
   missing decisions or context through
   `aak guide architecture-context-authoring-prompt`, always from authorized
   meaning.

### `UPDATE_FOR_CHANGE`

Begin from the base policy and make the smallest delta required by the approved
product change. Run `aak guide module-contract-authoring-prompt` when module
semantics are created or changed. Run
`aak guide architecture-context-authoring-prompt` when decisions, invariants,
overview, or routers must change. Add decision references before relying on a
new module, host, build unit, public contract, dependency permission, or reduced
enforcement. Land implementation, policy, contracts, routers, decisions, tests,
and context atomically.

### `RECONCILE_DRIFT`

Classify each mismatch before editing:

~~~text
IMPLEMENTATION_DRIFT
  restore code and build structure to the already authorized policy

STALE_POLICY
  update policy from a newer authorized decision and matching implementation

OBSERVATION_GAP
  run aak guide adapter-authoring-prompt; do not guess or hide the evidence

UNAUTHORIZED_BOUNDARY
  remove or redesign the boundary, or obtain a real decision before declaration

INSUFFICIENT_EVIDENCE
  keep the mismatch visible and request only the missing material decision
~~~

Never assume that current code wins merely because it exists, or that policy
wins when maintained evidence shows it is stale.

## 7. User-intervention gate

Continue autonomously when current requirements, repository authority, accepted
decisions, maintained contracts, and adapter evidence determine one safe policy.

Ask one concise plain-language question only when unresolved alternatives would
materially change:

- whether behavior forms a separate functional capability;
- which capability owns a build unit or public contract;
- whether an execution mechanism deserves a host boundary;
- whether a new dependency direction or scalable permission is accepted;
- whether observed structure is intentional or must be corrected;
- whether normative enforcement may be reduced;
- who has authority to approve the architectural decision.

Recommend the smallest safe option and explain its consequence. Never ask the
user to edit JSON, select a schema field, construct a selector, normalize an id,
or transcribe adapter output.

## 8. Validation and correction loop

The policy is complete only after:

~~~text
1. Parse and validate it against the exact bundled architecture-policy schema.
2. Run `aak validate` and resolve POL001 before interpreting downstream results.
3. Reconcile all ARC001 declared-versus-observed mismatches by cause.
4. Resolve applicable MOD, FEAT, HOST, DEP, STR, and DOC findings without
   broadening policy merely to silence them.
5. Run `aak validate --base-ref <TARGET_BASE> --fail-on-review` when a base
   policy exists so CHG001 evaluates architectural growth.
6. Run project-specific architecture tests and the affected build/test suite.
7. Regenerate `aak context index` when maintained boundaries changed.
8. Review the final diff against the evidence ledger and reject unexplained
   permissions, missing observed facts, stale references, and placeholders.
~~~

A current-state `PASS` does not authorize a new boundary. A comparative
`REVIEW_REQUIRED` remains visible until handled through declared authority. A
waiver is not a mechanism for approving normal architecture growth.

## 9. Completion report

~~~text
Mode and repository root:
Pinned AAK version, schema, and adapter:
Plain-language architecture represented:
Policy evidence ledger:
Observed proposal entries retained and why:
Observed proposal entries rejected and corrective action:
Modules, hosts, projects, and roles changed:
Dependency permissions added, removed, or rejected:
Structural enforcement changed or preserved:
Decision references and authority:
Related contracts, routers, ADRs, tests, or code changed:
User decisions requested, if any:
Validation commands and results:
Remaining FAIL, WAIVED, or REVIEW_REQUIRED findings:
~~~

Do not declare completion while policy contains sample values, placeholders,
fabricated intent, an unexplained observation mismatch, an unauthorized
permission, an unresolved reference, or a material boundary change that exists
only in conversation.
