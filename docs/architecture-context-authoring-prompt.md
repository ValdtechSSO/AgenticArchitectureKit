# Agent prompt for architecture context

[Español](es/architecture-context-authoring-prompt.md)

Use this prompt to instruct a coding agent to create, update, or reconcile the
maintained architecture context of an AAK project: architecture decisions,
system overview, global and capability invariants, and repository or module
`AGENTS.md` routers. The user supplies product meaning and material decisions,
not Markdown, filenames, anchors, or navigation instructions.

This guide is operational, not a second normative source. The exact pinned AAK
core, portable rules, project policy, module contracts, authority declaration,
and accepted decisions remain authoritative.

## 1. Mission and minimum user request

~~~text
Repository root: <DISCOVER_FROM_WORKSPACE_OR_SUPPLY>
Mode: <BOOTSTRAP_CONTEXT|RECORD_DECISION|UPDATE_SEMANTICS|REFRESH_ROUTING|RECONCILE_DRIFT>
Requested product or architecture outcome: <PLAIN_LANGUAGE_INTENT>
Known decision or invariant: <OPTIONAL_OR_UNKNOWN>
Affected capability or scope: <DISCOVER_OR_UNKNOWN>
Authority source: <REPOSITORY_POLICY_ISSUE_USER_BRIEF_OR_UNKNOWN>

Create or update only the maintained context required to make the current
architecture understandable and safely actionable by a fresh agent. The user
supplies meaning and decisions, not Markdown. You own discovery, artifact
selection, filenames, numbering, headings, anchors, links, routing, concise
wording, consistency checks, validation, and the completion report.

Do not ask the user to choose an ADR number, document path, heading, anchor,
template section, AGENTS.md layout, link syntax, or validation command. Ask only
when proceeding would invent or materially change product meaning, an invariant,
capability ownership, architectural direction, accepted risk, or authority.
~~~

The minimum usable human brief is one sentence, for example: “Record that stock
reservation belongs to Ordering and must never become negative” or “Prepare the
minimum architecture context for this repository.” Discover everything else
from the repository and its delegated authority whenever possible.

## 2. Artifact boundaries

Keep each artifact focused:

| Artifact | Owns | Must not become |
|---|---|---|
| `architecture/system-overview.md` | Current product purpose, actors, capability boundaries, hosts, dependency direction, integrations, and open architectural questions. | Historical diary, file inventory, or speculative roadmap. |
| `architecture/decisions/ADR-*.md` | Why one material architectural decision was made, its scope, alternatives, consequences, enforcement, and review triggers. | Description of whatever code happens to exist or approval fabricated by the agent. |
| `domain/global-invariants.md` | Stable product rules that cross more than one capability or apply system-wide. | Collection of local validation rules, coding preferences, or implementation details. |
| `domain/contexts/*.md` | Vocabulary, rules, ownership, and invariants belonging to one capability. | Duplicate module contract or generated class/entity catalog. |
| Root `AGENTS.md` | Small deterministic router: purpose, starting context, authoritative commands, critical boundaries, map, and prohibited operations. | Architecture handbook, tutorial, changelog, or conversational memory. |
| Module `AGENTS.md` | Local router to the module contract, relevant domain context, ADRs, commands, and critical rules. | Duplicate contract, generic repository instructions, or source inventory. |
| `architecture-discovery.md` | Optional decision ledger of known, assumed, unknown, and proposed boundaries during bootstrap or adoption. | Permanent speculative design or substitute for accepted decisions. |

Policy declares structural intent; module contracts declare stable module
semantics; adapters observe technology facts. Context documents explain meaning,
rationale, navigation, and constraints. Do not make one artifact impersonate
another.

## 3. Mandatory discovery and evidence classes

Before writing:

~~~text
1. Read repository instructions and run the architecture gate before change.
2. Run and read `aak core` from the exact pinned distribution.
3. Load DOC001, CHG001, MOD001, MOD002, OWN001, AUT001, and any finding-specific
   references through `aak explain` or emitted references.
4. Read project policy, module contracts, existing context documents, ADRs,
   authorities, waivers, current source boundaries, tests, and relevant product
   requirements. Use generated context as revision-bound evidence only.
5. Classify each statement as AUTHORIZED_DECISION, MAINTAINED_SEMANTICS,
   OBSERVED_FACT, INFERENCE, ASSUMPTION, or UNKNOWN and record its source.
6. Identify consumers: which future agent, module, validator reference, or
   reviewer needs this information, and at which narrowest scope.
7. Detect contradictions, stale statements, broken links, duplicate meaning,
   placeholders, and accepted ADRs that would be rewritten by the proposed change.
~~~

Product requirements and authorized decisions establish meaning. Maintained
contracts and domain documents establish current declared semantics. Source and
adapter output show implementation facts. An observed implementation pattern is
not automatically an invariant or accepted decision.

## 4. Artifact evidence contract

Use this matrix to decide what to write:

| Subject | Reliable evidence | Authoring rule | Prohibited shortcut |
|---|---|---|---|
| System purpose and actors | Current product brief, accepted scope, real interfaces and users. | State what exists and is currently intended in product language. | Do not turn assumptions or possible users into scope. |
| Capability boundaries | Contracts, policy, domain vocabulary, ownership, state, invariants, lifecycle, and accepted decisions. | Explain why each current module is a cohesive functional boundary. | Do not derive capabilities from folders, layers, frameworks, or teams. |
| Hosts and integrations | Current execution/exposure needs, ports, external systems, and policy. | Describe adaptation/composition and isolation direction. | Do not give hosts application ownership or document planned integrations as current. |
| Dependency direction | Accepted decisions, public contracts, policy permissions, and consumers. | Explain stable direction and reason without copying every edge. | Do not infer authorization merely from an observed dependency. |
| ADR context | Current forces, constraints, evidence, and the precise problem requiring a decision. | Record why a decision is needed now. | Do not manufacture urgency or retrospective rationale. |
| ADR decision and status | Explicit delegated authority, accepted requirement, or unresolved proposal. | Use `proposed` until the repository's real authority has accepted it; use `accepted` only with evidence. | The ability to edit the file is not authority to accept the decision. |
| ADR consequences | Real benefits, costs, risks, enforcement, migration, and review triggers. | Include negative consequences and operational impact. | Do not write generic benefits or hide tradeoffs. |
| ADR alternatives | Options actually evaluated. | Record why plausible current alternatives were rejected. | Do not invent straw alternatives after the fact. |
| Global invariant | Stable rule spanning multiple capabilities or every relevant operation. | Give it a unique durable heading and precise must/must-not statement. | Do not promote a local rule solely for visibility. |
| Capability invariant | Explicit rule owned by one functional capability. | Place it in that domain context and reference its exact heading from the contract. | Do not duplicate the prose in contract, router, policy, and tests. |
| Vocabulary and ownership | Product language, module purpose, authoritative-data decisions, and domain authority. | Define only terms needed to remove ambiguity for current work. | Do not infer ownership from reads, tables, ORM mappings, or namespaces alone. |
| Root router purpose and map | Current repository purpose, maintained roots, and authoritative commands. | Keep it small and route to deeper context. | Do not list every directory, file, or implementation convention. |
| Critical router rules | High-cost safety boundaries, domain invariants, authority limits, and required gates. | Include only rules a new agent must see before acting. | Do not duplicate the complete portable rule catalog. |
| Module router | Contract, narrow domain context, applicable ADRs, targeted commands, and module-specific rules. | Route locally and inherit repository instructions. | Do not restate the module contract or unrelated module rules. |
| Open questions | Material unknowns supported by evidence gaps. | Keep them explicitly unresolved and out of policy/structure. | Do not materialize an unknown as a placeholder module or abstraction. |

Every invariant or ADR link used by a contract or policy must resolve to a real
repository path. Every invariant anchor must correspond to a unique, stable
heading. Prefer one authoritative statement plus links over repeated prose.
When a critical rule requires new project-owned mechanical enforcement, run
`aak guide project-rule-authoring-prompt`; documentation alone is not a gate.

## 5. Decision and invariant lifecycle

### Architecture decisions

Create an ADR only for a material architectural choice that needs durable
rationale: capability creation/merge/split, ownership transfer, host or build
boundary, dependency direction, public contract, significant persistence or
integration strategy, normative enforcement reduction, or authorized waiver.
When an accepted ADR authorizes a temporary portable-rule deviation, run
`aak guide waiver-authoring-prompt` to materialize the bounded grant; the ADR
alone does not waive a finding.

Do not create an ADR for routine implementation placement already determined by
current architecture. Number new ADRs from repository evidence without
renumbering history. Preserve accepted ADR text as the record of the decision at
that time. When direction changes materially, create a superseding ADR and mark
the old one `superseded` with a resolvable reference.

### Invariants

An invariant states an outcome that must remain true across all relevant
operations, including failure, retry, concurrency, migration, and alternative
interfaces where applicable. Place it at the narrowest truthful ownership
scope. Give each referenced invariant its own descriptive heading rather than a
number-only anchor.

Changing an invariant is a product or risk decision, not documentation cleanup.
If observed code violates an accepted invariant, correct the implementation or
surface the conflict; never weaken the wording to describe the bug.

## 6. Mode-specific workflow

### `BOOTSTRAP_CONTEXT`

Build an evidence ledger of known, assumed, and unknown facts. Create the root
router and current system overview from known evidence. Create module routers,
domain contexts, invariants, and ADRs only where real current semantics or
decisions justify them. Remove every unused template placeholder. Unknowns may
remain questions; they must not become speculative structure.

### `RECORD_DECISION`

Determine whether the choice is material and not already governed. Locate the
real authority, draft the smallest ADR, keep status honest, and synchronize only
the policy, contracts, invariants, routers, implementation, and tests affected
by that same decision. Run `aak guide project-policy-authoring-prompt` or
`aak guide module-contract-authoring-prompt` when those artifacts change.

### `UPDATE_SEMANTICS`

Identify the authorized semantic change and its owner. Update the single
authoritative invariant or domain statement, then repair references and
summaries without duplicating it. Preserve history through a new ADR when an
accepted architectural direction changed materially.

### `REFRESH_ROUTING`

Update a router only when purpose, reading path, commands, critical safety
boundaries, map, or prohibited operations changed. Verify each command and link.
Keep details in their owned documents and keep the router short enough to be
read at task start.

### `RECONCILE_DRIFT`

Classify each conflict before editing:

~~~text
IMPLEMENTATION_DRIFT
  correct code or structure to the accepted decision or invariant

STALE_CONTEXT
  update context from a newer authorized decision and matching implementation

CONTRADICTORY_DECLARATIONS
  identify the authoritative owner; do not merge incompatible statements

UNAUTHORIZED_SEMANTIC_CHANGE
  preserve current authority and request the missing material decision

BROKEN_NAVIGATION
  repair path, anchor, command, or router mechanically without changing meaning

INSUFFICIENT_EVIDENCE
  keep the unknown explicit and do not turn it into architecture
~~~

## 7. User-intervention gate

Continue autonomously when existing authority and evidence determine the
meaning, scope, placement, links, and status. Ask one concise product-level
question only when alternatives would materially change:

- product purpose or capability ownership;
- an invariant or its scope;
- accepted architectural direction or risk;
- whether a decision is proposed or authorized;
- which incompatible maintained declaration is authoritative;
- authority to supersede a decision or change a protected rule.

Recommend the smallest safe option and explain its consequence. Never ask the
user to write Markdown, name a file, select an anchor, number an ADR, arrange a
router, or duplicate information between artifacts.

## 8. Atomic synchronization and validation

Before completion:

~~~text
1. Check that each fact has one authoritative home and all summaries agree.
2. Resolve every repository path and Markdown heading referenced by policy or
   module contracts; run AAK validation for DOC001 and related rules.
3. Verify ADR numbers are unique, status is truthful, supersession links
   resolve, and decisionRefs point to applicable decisions.
4. Verify invariants are placed at the narrowest truthful scope, have stable
   unique headings, and are reflected in current tests or review evidence where
   enforceable.
5. Verify every command and link in root and module AGENTS.md routers.
6. Remove placeholders, speculative claims, stale inventories, duplicated
   normative prose, and conversational references.
7. Run affected product and architecture tests, `aak validate`, strict base
   comparison when applicable, and `aak context index` after navigation changes.
8. Confirm a fresh agent can locate the owner, meaning, constraints, commands,
   and decision rationale without the prior conversation.
~~~

A valid link proves only that the document exists. It does not prove that an
invariant is authorized, an ADR was approved, or a summary is semantically true.

## 9. Completion report

~~~text
Mode and scope:
Plain-language meaning or decision recorded:
Evidence and authority sources:
Files created or changed and why:
Authoritative home of each invariant or decision:
ADR status, alternatives, consequences, and review triggers:
References and anchors checked:
Routers and commands checked:
Related policy or module-contract changes:
User decisions requested, if any:
Assumptions and unknowns kept explicit:
Validation commands and results:
Remaining contradictions, FAIL, WAIVED, or REVIEW_REQUIRED findings:
~~~

Do not declare completion while context contains placeholders, fabricated
approval, undocumented semantic changes, broken references, duplicated sources
of truth, stale commands, speculative architecture, or a material decision that
exists only in conversation.
