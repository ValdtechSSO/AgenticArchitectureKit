# Agent prompt for a module contract

[Español](es/module-contract-authoring-prompt.md)

Use this prompt to instruct a coding agent to create, adopt, or update an AAK
`module.contract.yml`. Replace known bracketed values and leave unknown values
as `UNKNOWN`; the agent must resolve them from authorized repository evidence or
ask only for a material semantic decision. This guide is operational, not a
second normative source. The pinned AAK core, schema, policy, and rule references
remain authoritative.

## 1. Mission and supplied intent

~~~text
Repository root: <REPOSITORY_ROOT>
Compatible AAK version: <AAK_VERSION>
Mode: <CREATE_NEW_MODULE|ADOPT_EXISTING_MODULE|UPDATE_EXISTING_CONTRACT>
Module root or proposed capability: <MODULE_ROOT_OR_CAPABILITY>
User's plain-language intent: <WHAT_THE_MODULE_MUST_OWN_AND_ACHIEVE>
Known exclusions: <WHAT_MUST_NOT_BELONG_TO_THIS_MODULE_OR_UNKNOWN>
Known data or state: <KNOWN_OWNED_DATA_OR_UNKNOWN>
Known invariants: <KNOWN_INVARIANTS_OR_UNKNOWN>
Known risks: <KNOWN_RISKS_OR_UNKNOWN>
Authorized decision sources: <PRODUCT_BRIEF_ISSUES_DOCS_ADRS_OR_CONVERSATION>
Authority to create or update supporting domain documents and ADRs: <YES|NO>

Create or update the smallest truthful module contract supported by current
intent and evidence. The user supplies meaning, not YAML. You own discovery,
field mapping, identifiers, formatting, schema compliance, reference checks,
validation, and the completion report.

Do not ask the user to choose schema properties, YAML syntax, paths, anchors,
identifier casing, or validation commands. Ask only when proceeding would invent
or materially change product scope, semantic ownership, an invariant, accepted
risk, architectural direction, or authorization.
~~~

The minimum usable human brief is one sentence: “Create or update the contract
for the capability that is responsible for `<INTENT>`.” Repository root, pinned
version, mode, module root, and existing evidence should be discovered from the
working context whenever possible. Every other supplied field is optional and
may remain `UNKNOWN` until evidence or an authorized decision resolves it.

## 2. Contract boundary

Preserve these responsibilities:

~~~text
User or delegated product authority
  decides product meaning, ownership, invariants, accepted risk, and material
  architectural direction

Implementation agent
  discovers evidence, proposes wording, writes YAML, maintains references,
  synchronizes authorized related artifacts, and validates the result

module.contract.yml
  records stable module identity, purpose, vocabulary, ownership, risk,
  invariants, and decision references

project-policy.json
  declares the module root, observable projects, roles, namespaces, and allowed
  architectural dependencies

Technology adapter
  observes code and build facts; it does not decide semantic ownership
~~~

Code, database access, folder names, generated indexes, and an existing policy
are evidence, not automatic semantic authority. Never infer that a module owns
data merely because it currently reads, writes, maps, or stores it. Never copy
classes, handlers, endpoints, routes, paths, tests, or file inventories into the
contract.

## 3. Mandatory context and discovery

~~~text
Before writing the contract:

1. Run and read from the exact pinned distribution:

   aak core
   aak guide bootstrap
   aak template module.contract.yml
   aak validate --list-rules

2. Read the bundled `module-contract.schema.json` completely and load the
   current references for MOD001, MOD002, OWN001, DOC001, POL001, and CHG001
   through `aak explain` or the emitted finding references.

3. Read repository and module `AGENTS.md`, project policy, system overview,
   applicable domain documents and ADRs. For adoption or update, inspect the
   module's current source, tests, data access, consumers, and build boundaries.

4. Classify every input as AUTHORIZED_DECISION, MAINTAINED_DOCUMENT,
   OBSERVED_CODE, INFERENCE, or UNKNOWN. Record its path, anchor, issue, or user
   statement. Generated indexes are OBSERVED_CODE evidence at one revision.

5. Reconcile contradictions before writing. Maintained semantic documents outrank
   generated observations, but stale documents must be reported rather than
   copied. Code disagreement may be a conformance problem, not permission to
   rewrite the contract.
~~~

For a new module, verify that current requirements justify a separate functional
capability through vocabulary, ownership, invariants, lifecycle, or an enforced
boundary. Do not create a module only because a technical category, framework,
folder, or layer exists.

## 4. Property evidence contract

Populate every property according to this matrix:

| Property | Meaning | Preferred evidence | Prohibited shortcut |
|---|---|---|---|
| `id` | Stable machine identity of the capability. | Existing policy id and module root; for a new authorized module, derive a normalized id from agreed domain vocabulary. | Do not copy a framework, layer, team, or temporary project name. |
| `name` | Human-readable capability name. | Product vocabulary used consistently in authorized requirements and maintained domain documents. | Do not prettify an unexplained directory name and present it as decided meaning. |
| `purpose` | Concise statement of what the module owns and why it exists. | User intent, product brief, system overview, domain context, and applicable ADRs. | Do not describe classes, endpoints, storage, libraries, or implementation workflow. |
| `intent.aliases` | Real phrases that should route tasks and questions to this module. | Terms used by users, domain experts, requirements, issues, commands, and maintained documentation. At least one is required. | Do not generate speculative synonyms merely to make the list longer. |
| `ownership.domain` | Functional domain boundary for which the module is accountable. | Explicit product or domain ownership decision supported by vocabulary and invariants. | Do not equate namespace, database schema, repository path, or team name with semantic ownership. |
| `ownership.authoritative_data` | Stable data concepts for which the module is the source of truth. | Explicit ownership decision, domain documentation, data lifecycle, write authority, and conflict resolution responsibility. An empty list is valid when none is known. | Reads, writes, tables, entities, or ORM mappings alone do not prove ownership. Never list files or implementation types. |
| `risk.default` | Default consequence level for changes: `low`, `medium`, `high`, or `critical`. | Current impact, reversibility, data durability, security/privacy, availability, compliance, and team risk policy. | Do not derive risk only from code size, test count, complexity, or agent confidence. |
| `risk.reasons` | Concrete reasons supporting the selected risk. | Consequences and protected concerns in requirements, invariants, incidents, ADRs, or explicit authority. Empty is valid only when no current reason exists. | Do not use generic filler such as “changes may break things.” |
| `invariants` | Repository references to rules that must always hold for this capability. | Existing authoritative domain documents with exact resolvable anchors. Create or update documents only when authorized. Empty is valid if no invariant is currently decided. | Do not invent an anchor, duplicate invariant prose, or turn current implementation behavior into a domain rule. |
| `architecture_decisions` | Repository references explaining material boundaries and architectural choices. | Applicable accepted ADRs with resolvable paths. A new material module boundary normally needs an authorized decision. | Do not fabricate an ADR, cite an unrelated decision, or use the contract itself as justification. |

The schema proves shape, not truth. A schema-valid purpose such as “does stuff”
is still unacceptable. Conversely, an empty optional array is more truthful than
invented semantics.

## 5. Evidence and decision ledger

Before editing, produce this ledger and keep it in the task report rather than
inside the contract:

| Property | Proposed value | Evidence and classification | Confidence | Decision needed |
|---|---|---|---|---|
| `id` | ... | ... | exact/proposed | yes/no |
| `name` | ... | ... | exact/proposed | yes/no |
| `purpose` | ... | ... | exact/proposed | yes/no |
| `intent.aliases` | ... | ... | exact/proposed | yes/no |
| `ownership.domain` | ... | ... | exact/proposed | yes/no |
| `ownership.authoritative_data` | ... | ... | exact/proposed | yes/no |
| `risk.default` and `reasons` | ... | ... | exact/proposed | yes/no |
| `invariants` | ... | ... | exact/proposed | yes/no |
| `architecture_decisions` | ... | ... | exact/proposed | yes/no |

Continue without questioning when repository authority and supplied intent make
the answer unambiguous. If a material row remains `UNKNOWN` or contradictory,
ask one concise domain-level question that groups the unresolved decision. Show
a recommendation and its consequences; never ask the user to author YAML.

## 6. Authoring sequence

~~~text
1. Determine whether the requested capability is new, existing, merged, split,
   or merely a technical area inside an existing module.
2. Locate the module root and current policy declaration, or propose both from
   authorized intent without materializing speculative structure.
3. Build and reconcile the evidence ledger.
4. Resolve only material semantic unknowns with the authorized person.
5. Draft the contract using exactly the schema properties and stable domain
   language. Preserve existing valid meaning during updates.
6. Resolve every invariant and ADR path and anchor. If a required reference is
   missing, run `aak guide architecture-context-authoring-prompt` and create or
   update the supporting document only when authorized; otherwise report the
   blocker.
7. For a new or changed boundary, run the project-policy and architecture-context
   authoring prompts and synchronize policy, router, domain documents, ADRs, and
   architecture tests only to the extent authorized by the same decision. Never
   change policy merely to silence validation.
8. Review the diff for structural inventories, fabricated meaning, stale
   references, duplicated prose, and accidental ownership changes.
9. Run schema-aware AAK validation and the project's required checks.
10. Return the final contract plus a plain-language semantic summary and evidence
    ledger. The user approves meaning, not serialization details.
~~~

## 7. Validation and acceptance

The result is complete only when all applicable checks succeed:

- the YAML loads under AAK's supported YAML subset;
- it conforms to the exact pinned `module-contract.schema.json`;
- all required properties exist and no additional properties are present;
- `MOD001` finds the contract and local module router;
- `MOD002` confirms that the contract id matches the declared module root;
- `DOC001` resolves every invariant and ADR path and anchor;
- `OWN001` reports no duplicate declared owner; any ownership conflict remains
  visible, and unprovable observed write access stays `REVIEW_REQUIRED` until
  handled under declared authority;
- `POL001` and `CHG001` remain valid when a policy boundary changed;
- `aak validate --fail-on-review` and required project checks pass, or every
  remaining finding is reported without weakening policy;
- a fresh agent can understand responsibility, vocabulary, ownership, risk, and
  protected meaning without reading the prior conversation.

Validation success does not prove semantic truth. Present the proposed purpose,
ownership, invariants, and risk in plain language so an authorized person can
notice a wrong assumption.

## 8. Maintenance rules

Update the contract when the module's stable purpose, vocabulary, ownership,
authoritative data, risk, invariants, or governing decisions change. Do not edit
it for routine refactors, new classes, endpoints, handlers, tests, folder moves,
or internal library changes that preserve those semantics.

When code and contract disagree, classify the cause before editing:

~~~text
IMPLEMENTATION_DRIFT
  change code or policy back to the already authorized contract

STALE_CONTRACT
  update the contract from a newer authorized semantic decision

NEW_ARCHITECTURE_DECISION
  record and authorize the decision, then update contract and related artifacts

INSUFFICIENT_EVIDENCE
  keep uncertainty visible and request the missing semantic decision
~~~

Never rewrite stable semantic history to make the current implementation appear
intentional.

## 9. Completion report

~~~text
Mode and module root:
AAK version and schema:
Files created or changed:
Plain-language module summary:
Property evidence ledger:
User decisions requested, if any:
Assumptions rejected or left unknown:
Ownership and authoritative-data conclusion:
Risk conclusion and reasons:
Invariant references checked:
ADR references checked:
Related policy/router/document changes:
Validation commands and results:
Remaining FAIL or REVIEW_REQUIRED findings:
Semantic review requested from:
~~~

Do not declare completion while the contract contains placeholders, unresolved
references, fabricated semantics, silent contradictions, or an unauthorized
ownership, risk, invariant, or architectural decision.
