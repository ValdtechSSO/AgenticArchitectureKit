# Agent prompt for a project-specific architecture rule

[Español](es/project-rule-authoring-prompt.md)

Use this prompt to instruct a coding agent to create, update, or reconcile an
enforceable architecture rule owned by one project, such as “all DTOs must be
records.” The user supplies the guarantee, how affected subjects are recognized,
allowed exceptions, and what evidence is trustworthy. The agent owns rule
design completion, implementation, tests, documentation, pipeline wiring, and
verification.

This guide is operational, not a second normative source. Project rules extend
the project's guarantees; they do not silently change AAK portable rule
semantics, the common observation model, or the meaning of `aak validate`.

## 1. Mission and minimum user request

~~~text
Repository root: <DISCOVER_FROM_WORKSPACE_OR_SUPPLY>
Mode: <CREATE|UPDATE|RECONCILE|PROMOTE_CANDIDATE>
Desired guarantee: <WHAT_MUST_ALWAYS_BE_TRUE>
Affected subjects: <HOW_TO_IDENTIFY_WHAT_THE_RULE_APPLIES_TO_OR_UNKNOWN>
Allowed exceptions: <EXPLICIT_EXCEPTIONS_OR_NONE_OR_UNKNOWN>
Trustworthy evidence: <WHAT_PROVES_COMPLIANCE_OR_VIOLATION_OR_UNKNOWN>
Enforcement expectation: <LOCAL_AND_CI|LOCAL_ONLY|ADVISORY_REVIEW>
Authority source: <PROJECT_POLICY_ADR_ISSUE_USER_BRIEF_OR_UNKNOWN>

Create the smallest reliable project-owned rule that enforces the requested
guarantee. The user defines architectural intent, not analyzer code, test
framework, configuration syntax, file paths, rule identifiers, or CI commands.
You own repository discovery, technology choice, subject detection, evaluator,
fixtures, negative tests, exception mechanics, documentation, integration,
validation, and the completion report.

Ask only when a missing answer would materially change the guarantee, affected
subjects, accepted evidence, exceptions, enforcement severity, or authority.
Never ask the user to implement the observer or evaluator.
~~~

The minimum usable request can be one sentence: “In this project, every DTO must
be a record.” If “DTO” has one reliable meaning already declared by the
repository, derive it. If several incompatible classifications are plausible,
ask one concise semantic question with a recommendation rather than guessing
from a suffix alone.

## 2. Four decisions and agent responsibilities

Every rule starts with four project decisions:

| Decision owned by project authority | Question |
|---|---|
| Guarantee | What must always be true? |
| Subject identification | Which exact elements are governed? |
| Exceptions | Which explicit cases are allowed, and who may authorize them? |
| Trustworthy evidence | What observation proves compliance, violation, or uncertainty? |

The agent expands those decisions into a stable rule id, scope, technology
mapping, evaluator, deterministic output, documentation, positive fixtures,
negative mutations, false-positive tests, exception tests, local command, and CI
gate. The agent must not invent product semantics to fill a missing decision.

## 3. Choose the correct enforcement boundary

Select the smallest mechanism that can prove the guarantee:

| Mechanism | Use when | Examples |
|---|---|---|
| Compiler or language-native analyzer | The language exposes exact syntax or semantic symbols and supports stable diagnostics. | Roslyn analyzer, compiler plugin, linter rule. |
| Project architecture test | The guarantee can be evaluated deterministically from source, manifests, reflection metadata, or a compiled model inside this repository. | Dependency test, naming/annotation contract, schema assertion. |
| Build/package validation script | Authoritative manifests or generated schemas provide exact evidence and no native analyzer is justified. | Package metadata, deployment manifest, migration policy. |
| AAK technology adapter extension | Additional technology observation is needed by an existing portable rule or a separately implemented evaluator. | New source identity or dependency construct. |
| AAK core/catalog extension | The rule needs a new common observation field, evaluator, result semantics, schema, or portable reference and has real cross-project value. | New portable architectural guarantee. |
| Semantic review | No reliable mechanical evidence exists, but a durable human judgment can bind exact evidence. | Cohesion or ownership judgment. |

For a project-only syntax rule, prefer a native analyzer or architecture test.
Do not put validation semantics inside a technology adapter: the adapter reports
facts; the evaluator decides whether they conform. Do not overload an unrelated
project-policy field to make the common validator appear to enforce the rule.

`aak validate` runs only rules registered in the pinned AAK catalog. A separate
project analyzer or test must be wired into the repository's authoritative
local and CI commands. The completion report must state which command enforces
the rule and must never imply that an AAK `PASS` covers an external check.

## 4. Rule specification contract

Before implementation, record the rule in the project's existing architecture
rule convention. If none exists and durable explanation is needed, create the
smallest project-owned document, for example
`architecture/rules/<stable-rule-id>.md`; do not create an empty rule hierarchy.

Use this logical contract regardless of serialization:

~~~yaml
ruleId: <STABLE_PROJECT_RULE_ID>
scope: project
title: <SHORT_HUMAN_TITLE>
guarantee: <PRECISE_MUST_OR_MUST_NOT_STATEMENT>
subjects:
  description: <SEMANTIC_DESCRIPTION>
  identification:
    exact:
      - <AUTHORITATIVE_SIGNAL>
    heuristic:
      - <OPTIONAL_LOWER_CONFIDENCE_SIGNAL>
acceptedEvidence:
  compliant:
    - <PROOF_OF_COMPLIANCE>
  violation:
    - <PROOF_OF_VIOLATION>
  uncertainty:
    - <WHEN_EVIDENCE_IS_INSUFFICIENT>
exceptions:
  - condition: <NARROW_EXPLICIT_CONDITION_OR_NONE>
    authority: <WHO_CAN_DECLARE_IT>
    evidence: <HOW_THE_EXCEPTION_IS_RECORDED>
result:
  violation: <FAIL|NAMED_TOOL_FAILURE>
  uncertainty: <REVIEW_REQUIRED|FAIL_CLOSED|NOT_APPLICABLE>
enforcement:
  mechanism: <ANALYZER|ARCHITECTURE_TEST|BUILD_CHECK|AAK_EXTENSION|REVIEW>
  localCommand: <EXACT_COMMAND>
  ciGate: <WORKFLOW_OR_AGGREGATE_COMMAND>
reviewTriggers:
  - <WHEN_RULE_OR_ACCEPTANCE_MUST_BE_REVISITED>
~~~

The persisted format may be Markdown, analyzer configuration, or a project test
contract. Do not introduce a new machine-readable format unless a current tool
consumes it. Keep the human-readable guarantee and the executable diagnostic
linked by the stable rule id.

## 5. Evidence and uncertainty rules

Reliable subject identification is part of the rule, not an implementation
detail. Prefer semantic markers, compiler symbols, explicit interfaces,
attributes/annotations, manifest roles, or owned paths already established by
project architecture. Names and folders may be exact only when the project has
explicitly made that convention authoritative and the analyzer covers all
relevant source.

For each evidence source classify coverage as:

~~~text
EXACT
  authoritative parser or semantic model proves the fact

HEURISTIC
  useful signal with known false-positive or false-negative risk

UNSUPPORTED
  relevant construct cannot currently be evaluated

OUT_OF_SCOPE
  explicitly excluded by the authorized subject contract
~~~

Never treat `HEURISTIC` or `UNSUPPORTED` as automatic compliance. Use the rule's
declared uncertainty outcome. If the chosen tool cannot represent
`REVIEW_REQUIRED`, fail closed with a clear diagnostic and report the required
review path rather than silently passing.

Generated, vendor, test, migration, compatibility, or external code is not
automatically exempt. Each exclusion must be part of the subject or exception
contract and supported by reliable evidence.

## 6. Exception and authority model

An exception is a narrow part of the rule definition or an explicitly recorded
project authorization. It must identify condition, scope, reason, authority,
evidence, and review/expiry trigger. The evaluator still observes the subject
before applying the exception.

Do not add an unknown project rule to AAK `waivers.json`; WVR001 waivers apply
to known rules in the pinned AAK catalog. Project-rule exceptions need their
own evaluator-supported mechanism unless the rule is formally added to that
catalog. Do not use comments, filename tricks, or broad ignore globs as hidden
exceptions.

The agent may implement an already authorized exception mechanism. It must not
grant itself an exception merely because a new negative test fails.

## 7. Implementation and test sequence

~~~text
1. Read repository instructions, current architecture context, project policy,
   contracts, relevant ADRs, build/test commands, and CI gates.
2. State the four decisions and classify any missing one as derivable or
   materially unresolved.
3. Inventory every language/build construct that can represent an affected
   subject, including aliases, partial/generated forms, nested types, top-level
   constructs, multiple build units, and mixed-language areas where applicable.
4. Choose the smallest enforcement boundary and document why weaker evidence
   is insufficient.
5. Assign a stable project rule id without colliding with AAK portable ids or
   pretending the rule is portable.
6. Implement read-only deterministic subject discovery and evaluation using an
   authoritative parser or semantic API where available.
7. Emit a diagnostic containing rule id, exact subject/scope, violated
   guarantee, evidence, and remediation or review instruction.
8. Add minimal positive fixtures and one isolated negative mutation for every
   prohibited form. Prove that the negative test fails for this rule id.
9. Test permitted exceptions, malformed inputs, unsupported constructs,
   generated/vendor boundaries, false positives, false negatives, deterministic
   repetition, and repository-root confinement where relevant.
10. Run the check against current project code and correct real violations; do
    not weaken the rule or broaden exceptions to make the baseline green.
11. Add the exact check to the authoritative local test/build aggregate and CI
    required gate. Ensure a deliberately violating mutation makes that gate fail.
12. Update the smallest architecture rule document, applicable ADR or invariant,
    and AGENTS.md command/router through
    `aak guide architecture-context-authoring-prompt` when their meaning changes.
13. Run project tests, the new negative suite, `aak validate`, and strict
    architecture validation. Report AAK and project-rule results separately.
~~~

Implementation is incomplete if the analyzer exists but no normal developer or
CI path invokes it.

## 8. Language-agnostic acceptance protocol

The rule is accepted only when all applicable checks hold:

- the guarantee, subjects, exceptions, and evidence are explicit and agree with
  current project authority;
- every governed construct in the supported language boundary is parsed,
  explicitly unsupported, or explicitly out of scope;
- compliant code passes and each minimal prohibited mutation fails with the
  stable rule id and exact subject;
- exception tests prove both the allowed case and rejection of a near miss;
- heuristic or unsupported evidence never becomes silent `PASS`;
- output is deterministic and paths/scopes are stable;
- the check runs through the documented local command and required CI path;
- disabling, deleting, or bypassing the check is itself visible in review;
- current repository violations were fixed or remain explicitly reported;
- documentation names the actual enforcement mechanism without claiming that
  the portable AAK validator executes it;
- a fresh agent can change governed code and discover the rule before completion.

For a rule such as “every DTO must be a record,” acceptance must prove both how
DTOs are identified and how the language proves a record declaration. A test
that checks only `*Dto` filenames is insufficient unless that naming convention
is explicitly authoritative and all DTO forms are covered.

## 9. Promotion and evolution

Keep the rule project-owned while it expresses one project's policy. Consider
organization or portable promotion only when multiple real consumers share the
same language-independent guarantee and evidence contract.

Promotion that requires new AAK-observed facts must explicitly update the common
model, serialization, adapter contracts, context index, evaluator, catalog,
normative reference, schemas where applicable, compatibility policy, and
conformance tests. Run `aak guide adapter-authoring-prompt` for technology
observation work. Do not rename a project test as an AAK rule without building
that complete execution path.

When updating a rule, preserve its stable id if the guarantee remains compatible.
Create a new id or versioned decision when subjects, exceptions, evidence, or
result semantics change incompatibly. Re-run all negative mutations and review
existing exceptions.

## 10. Completion report

~~~text
Rule id and title:
Plain-language guarantee:
Affected subjects and exact identification:
Exceptions and authority:
Accepted evidence and coverage classification:
Chosen enforcement mechanism and why:
Files created or changed:
Local enforcement command:
CI gate:
Positive fixtures and negative mutations:
Current repository violations found and resolution:
Uncertainty and unsupported constructs:
Architecture context or ADR changes:
AAK validation result:
Project-rule validation result:
User decisions requested, if any:
Remaining risks or review triggers:
~~~

Do not declare completion while the rule relies on an unexplained naming
heuristic, silently ignores relevant constructs, lacks a negative mutation,
contains an unauthorized exception, is absent from the normal CI path, or is
reported as enforced by AAK when only an external project check executes it.
