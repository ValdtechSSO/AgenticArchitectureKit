# Agent prompt for implementing a product change

[Español](es/implement-change-prompt.md)

Use this prompt as the default entry point for creating or evolving a product
with Agentic Architecture Kit. The user describes the desired outcome in plain
language. The implementation agent owns architectural classification, repository
discovery, planning, code, maintained artifacts, validation, and reporting.

This guide coordinates specialized AAK guidance; it does not replace the pinned
decision core, schemas, policies, contracts, rule references, or authority.

## 1. Minimum user request

~~~text
Repository root: <DISCOVER_FROM_WORKSPACE_OR_SUPPLY>
Requested product outcome: <PLAIN_LANGUAGE_REQUEST>
Acceptance criteria: <OPTIONAL_OR_UNKNOWN>
Known constraints: <OPTIONAL_OR_UNKNOWN>

Implement the requested outcome completely. Determine its current architectural
owner and the smallest justified change. Maintain AAK artifacts only when their
stable meaning or declared boundaries actually change. Ask me only for a
material product, ownership, invariant, risk, external-effect, or authority
decision that cannot be resolved from delegated repository context.
~~~

The minimum usable request is one sentence, for example: “Notify me when a saved
wine becomes available again.” Do not require the user to mention modules,
features, contracts, policies, adapters, projects, ADRs, schemas, folders,
classes, or validation commands.

## 2. Mandatory preflight

Before planning or editing:

~~~text
1. Read repository instructions and run the architecture gate before change.
2. Run and read `aak core` from the exact version pinned by the repository.
3. Locate the current owning module and smallest cohesive feature area using
   maintained contracts, policy, domain vocabulary, source, consumers, and tests.
   For a language with configured semantic code intelligence, use it to resolve
   symbols, real references, implementations, and direct consumers before
   relying on textual search. Record provider, coverage, and resolution level;
   semantic observation never authorizes an architectural edge.
4. Read only the applicable module contract, local router, invariants, ADRs,
   policy, waivers, and finding references.
5. Inspect the requested behavior's current code, data lifecycle, interfaces,
   dependencies, tests, and technology-observation coverage.
6. Classify evidence as DECLARED, OBSERVED, INFERRED, ASSUMED, or UNKNOWN.
7. Record the repository revision and a base reference suitable for detecting
   architectural growth.
8. If execution may outlive one reliable context, run
   `aak guide long-running-execution`, preserve the original plan, and start the
   durable checkpoint protocol before relying on conversational memory.
~~~

Do not begin by creating a new module, project, layer, abstraction, or directory.
Extend the existing cohesive owner unless current evidence proves that a new
boundary is necessary.

## 3. Change classification algorithm

Classify the request into the first smallest category that satisfies it:

| Classification | Use when | Architectural consequence |
|---|---|---|
| `ROUTINE_EXISTING_FEATURE` | Behavior belongs to an existing capability and cohesive feature owner. | Change implementation and tests. Policy, module contract, and ADR normally remain unchanged. |
| `NEW_FEATURE_AREA` | Behavior belongs to an existing module but has independently meaningful vocabulary, state, invariants, risk, ownership, or lifecycle inside it. | Add the smallest cohesive feature area. If feature policy changes, run `aak guide project-policy-authoring-prompt`. |
| `MODULE_SEMANTICS_CHANGED` | An existing module's stable purpose, vocabulary, ownership, authoritative data, risk, invariants, or governing decisions changed. | Run the module-contract prompt and, when context or boundaries change, the architecture-context and project-policy prompts. |
| `NEW_MODULE` | A current functional capability has independently meaningful vocabulary and ownership, normally with its own state/invariants/lifecycle, and cannot remain cohesive inside an existing module. | Run the module-contract, project-policy, and architecture-context authoring prompts; create one coherent boundary and its implementation. |
| `NEW_HOST` | A currently required way to execute, schedule, compose, or expose the product needs its own runtime/adaptation boundary. | Run the project-policy and architecture-context authoring prompts; declare the host, minimal source, decision, and dependencies. |
| `NEW_BUILD_UNIT` | A separate project/package enforces a real dependency, deployment, runtime, language, publication, distribution, or ownership boundary. | Run `aak guide project-policy-authoring-prompt`; add only the observed build unit, owner, role, decision references, and authorized edges. |
| `NEW_DEPENDENCY_PERMISSION` | The requested design requires a new dependency across declared owners or build units. | Run `aak guide project-policy-authoring-prompt`; prefer a public contract and permit only the exact or scalable edge authorized by a current decision. |
| `TECHNOLOGY_OBSERVATION_GAP` | A real edge is only a syntactic candidate, a required provider is absent, a solution cannot load completely, or evidence is partial or truncated. | Run `aak guide adapter-authoring-prompt`; extend observation without changing portable rule meaning or hiding uncertainty. |
| `PROJECT_RULE_EXTENSION` | A stable project-specific guarantee is required beyond current portable rules. | Run `aak guide project-rule-authoring-prompt`; implement its evidence, evaluator/analyzer, negative tests, exceptions, and local/CI enforcement without overloading policy. |

A request may have one primary classification and necessary secondary
consequences. Do not promote secondary mechanics into independent architecture.
For example, a new endpoint is normally part of an existing feature; it is not
automatically a feature root, module, host, or project.

## 4. New-module decision gate

Create a module only when current evidence supports a separate product
capability. Build this decision record before materializing it:

~~~text
Proposed capability and real domain vocabulary:
Existing module considered first:
Why the existing module would become incoherent:
Independent ownership or authority:
Owned state or authoritative data:
Independent invariants or risk:
Independent lifecycle or evolution pressure:
Current consumers and required public contract:
Required build/deployment boundary, if any:
Decision source and authority:
Rejected technical-only justification:
~~~

One strong ownership boundary can be sufficient. Several weak naming or folder
signals are not. `Services`, `Infrastructure`, `Persistence`, `Validation`, a
framework, a database, or a team name are not product modules unless they form
an independently owned platform capability with its own contract and lifecycle.

If evidence does not justify the boundary, implement inside the existing module
and record no speculative module. If two materially different ownership choices
remain valid and authority has not delegated one, ask the user one concise
domain-level question with a recommendation and consequences.

## 5. Policy update rules

Treat `project-policy.json` as declared intent checked against observation, not
as an inventory automatically copied from the current tree.

Whenever the plan contains a non-`NONE` policy delta, run
`aak guide project-policy-authoring-prompt` and follow its evidence ledger,
mode-specific reconciliation, authorization, and validation procedure. The
table below is the classification handoff, not a replacement for that guide.

Use this decision table:

| Change | Policy action |
|---|---|
| Routine behavior, refactor, handler, endpoint, test, internal adapter, or internal library | No policy change unless a declared boundary actually changes. |
| New feature area inside a module | Update `featureRoot` or `featureAreas` only when those concepts are governed by the current policy and the area is already justified. |
| New module | Add its stable `id`, real `root`, optional feature declaration, source-identity patterns supported by evidence, and applicable decision references. |
| New host | Add its `id`, real `root`, allowed adaptation/composition source patterns, source identities when observable, and decision references. |
| New build unit | Add its observed path and name, semantic owner, mechanically supported role, public-contract designation when applicable, and decision references. |
| New project/source dependency | Add permission only after validating direction, owner, role, public contract, necessity, and decision authority. Observation alone is never authorization. |
| Adapter discovers unexpected existing structure | Correct accidental code/structure, declare an already intended boundary with evidence, or keep the finding visible. Never broaden policy merely to obtain PASS. |

The agent derives mechanical values from the adapter and repository. The agent
derives semantic mappings from authorized intent and maintained decisions. The
user never fills JSON. If a new boundary is material, record a resolvable ADR or
other accepted decision before relying on the permission.

When a module is created, update atomically as applicable:

~~~text
implementation
+ module.contract.yml
+ module AGENTS.md router
+ domain invariants or context
+ architecture decision
+ project-policy modules/projects/dependencies
+ architecture tests or adapter coverage
+ generated context and validation evidence
~~~

Do not create a separate build unit merely because a module exists. Do not add
dependency permission for an edge that the chosen implementation can avoid.

## 6. User-intervention gate

Continue autonomously when the requested outcome, repository authority, current
contracts, invariants, and accepted decisions determine a safe answer.

Ask the user only when at least one unresolved choice would materially change:

- product behavior or acceptance criteria;
- which capability owns behavior or authoritative data;
- a domain invariant;
- accepted security, privacy, compliance, durability, availability, or
  irreversible-effect risk;
- an external action requiring new authority;
- whether to create, merge, split, or transfer a real capability boundary;
- whether to permit a dependency that changes architectural direction.

Do not ask about YAML, JSON, schema fields, identifiers, namespace/package
patterns, folder placement, project manifests, parser implementation, test
layout, or validation commands when those are derivable. Group related unknowns
into one concise question, recommend the smallest safe option, and explain its
consequence.

## 7. Implementation plan contract

Before implementation, produce a short evidence-backed plan containing:

~~~text
Requested outcome and acceptance criteria:
Current owning module and feature area:
Primary change classification:
Boundary decision and evidence:
Implementation and test scope:
Module-contract delta: <NONE|SUMMARY>
Policy delta: <NONE|SUMMARY>
ADR/invariant delta: <NONE|SUMMARY>
Adapter/rule-extension delta: <NONE|SUMMARY>
Code-intelligence provider and evidence level: <PROVIDER|NONE> / <SEMANTIC|SYNTACTIC|TEXTUAL>
Risk and authority checks:
Validation commands including base comparison:
Only unresolved material decision, if any:
~~~

If the user requested implementation and no material decision blocks it, do not
stop after producing the plan. Execute it, keep changes scoped, and revise the
plan when repository evidence invalidates an assumption.

Whenever `ADR/invariant delta` is not `NONE`, or a system overview or agent
router must change, run `aak guide architecture-context-authoring-prompt`. Use
it to place each decision or invariant at one authoritative scope and repair all
references without asking the user to author Markdown.

Whenever `Adapter/rule-extension delta` includes a project-specific guarantee,
run `aak guide project-rule-authoring-prompt`. The project check and AAK
validation remain separate unless the complete common model, evaluator, catalog,
and conformance path are deliberately extended.

## 8. Execution and atomicity

Implement the smallest vertical outcome that satisfies current acceptance
criteria. Keep application behavior in its owning capability and cohesive
feature area, domain meaning independent of infrastructure, public contracts
limited to current consumers, infrastructure behind owned ports, and hosts
limited to adaptation and composition.

For an architectural change, code and declarations must land together. Do not
leave policy describing files that do not exist, observed boundaries undeclared,
contracts pointing to missing documents, or ADRs describing unimplemented
intent. Do not use a waiver or semantic review to conceal an implementation
mistake.

Preserve unrelated user changes. Avoid generated or vendor output unless a
required tool owns it. Update context indexes and retained evidence only through
their authoritative generators.

For a long-running task, checkpoint after each bounded segment. Before the next
segment, use `aak checkpoint resume` so the unchanged original plan and complete
latest state are supplied together. Do not continue only from accumulated or
compacted conversation context.

## 9. Validation and correction loop

Run validation in proportion to the change:

~~~text
1. Targeted tests for changed behavior.
2. Affected module, contract, integration, and architecture tests.
3. Required build, lint, type, migration, or package checks.
   Use compiler diagnostics for rapid local feedback when available, then run
   the project's authoritative build and tests. A green semantic diagnostic
   query does not replace build targets, generators, packaging, migrations,
   integration tests, or browser tests.
4. `aak validate` for current-state agreement.
5. `aak validate --base-ref <TARGET_BASE> --fail-on-review` for architectural
   growth and strict completion.
6. `aak context index` when maintained boundaries or navigational context changed.
~~~

Resolve results by cause:

| Result | Response |
|---|---|
| Code violates an existing authorized boundary | Correct the code. |
| Maintained declaration is stale against a newer authorized decision | Update the declaration and related semantic artifacts. |
| New boundary is intended but lacks a decision | Run the architecture-context prompt in `RECORD_DECISION` mode; keep authority honest and do not weaken `CHG001`. |
| Adapter cannot observe required evidence | Keep uncertainty visible and invoke adapter authoring. |
| Semantic truth cannot be proven mechanically | Return `REVIEW_REQUIRED` and follow declared authority. |
| A necessary temporary deviation is authorized | Run `aak guide waiver-authoring-prompt`; record a bounded waiver and never convert it to PASS. |

Repeat the loop until required checks pass or a genuine unresolved authority or
product decision remains. A passing validator does not compensate for missing
behavioral tests or fabricated semantics.

## 10. Friendly completion report

Report outcomes in product language first:

~~~text
Product outcome delivered:
Where the behavior belongs and why:
Classification: <ROUTINE|FEATURE|MODULE|HOST|BUILD_UNIT|DEPENDENCY|OTHER>
User decisions required: <NONE|SUMMARY>
Code and tests changed:
Architecture artifacts changed: <NONE|PLAIN_LANGUAGE_SUMMARY>
Why policy changed or remained unchanged:
New module decision record, if applicable:
Dependencies introduced or rejected:
Validation commands and results:
Remaining FAIL, WAIVED, or REVIEW_REQUIRED findings:
Risks or follow-up:
~~~

Do not make the user reconstruct the result from filenames or rule identifiers.
Mention those as supporting evidence after explaining their product meaning.
Never declare completion when only scaffolding, policy, or documentation exists
but the requested product outcome is not implemented and verified.
