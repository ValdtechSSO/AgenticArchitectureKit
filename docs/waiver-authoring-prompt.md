# Agent prompt for architecture waivers

Use this prompt to instruct an agent to create, update, review, or remove a
bounded waiver for one concrete violation of a portable AAK rule. The user or
declared project authority accepts the architectural risk; the agent owns
finding discovery, exact field derivation, JSON editing, validation, tests, and
reporting.

A waiver records an exceptional decision. It never proves conformance, changes
portable rule semantics, or turns a finding into `PASS`.

## 1. Mission and minimum user request

~~~text
Repository root: <DISCOVER_FROM_WORKSPACE_OR_SUPPLY>
Mode: <CREATE|UPDATE|REVIEW|REMOVE>
Deviation: <PLAIN_LANGUAGE_DESCRIPTION_OR_CURRENT_FINDING>
Why it cannot be corrected now: <CONSTRAINT_OR_UNKNOWN>
Accepted risk: <CONCRETE_CONSEQUENCE_OR_UNKNOWN>
Authority: <EXISTING_ADR_OR_DECLARED_DECISION_MAKER_OR_UNKNOWN>
Removal or review trigger: <EVENT_DATE_OR_UNKNOWN>

Determine whether a waiver is the correct mechanism. If it is, derive the exact
rule, current rule digest, narrowest matching scope, stable id, and JSON shape
from repository evidence. Ask me only for a material acceptance of risk,
authority decision, or removal condition that is not already delegated. Never
ask me to write JSON, copy a digest, choose a path, or implement validation.
~~~

The minimum useful brief can be one sentence: “Keep this host-to-module
dependency during the migration approved by ADR-014, and remove it when the
public contract is available.” The user supplies exceptional intent and
authority, not serialization.

## 2. Waiver eligibility decision

Classify the underlying finding before editing `waivers.json`:

| Cause | Required response |
|---|---|
| Accidental implementation or dependency violation | Correct the code. `NOT_A_WAIVER`. |
| Stale policy, contract, ADR, invariant, or router | Reconcile the maintained declaration. `NOT_A_WAIVER`. |
| The adapter cannot observe reliable evidence | Extend or correct observation. `NOT_A_WAIVER`. |
| Semantic truth cannot be proven mechanically | Keep `REVIEW_REQUIRED` and use semantic-review authority. `NOT_A_WAIVER`. |
| Intended new boundary lacks an authorizing decision | Record and authorize the decision; do not waive normal growth. `NOT_A_WAIVER`. |
| A known portable-rule violation cannot safely be removed now and current authority explicitly accepts its bounded risk | `WAIVER_ELIGIBLE`. |

Do not create a waiver merely because validation is red, a deadline is near, or
the agent can edit governance. A project rule absent from the pinned AAK catalog
needs its own exception mechanism.

## 3. Authority boundary

The agent may discover the finding, propose the smallest scope, explain risk,
draft the decision, edit the record, and prove its behavior. It must not
authorize its own proposal or infer acceptance from silence.

Authorization must already be delegated by repository policy or supplied by the
applicable human/team authority. Record it in a resolvable decision document,
normally an ADR. “Make validation pass” is not authority to accept risk.

For `UPDATE`, a broader scope, longer lifetime, changed risk, changed rule
meaning, or changed deviation requires fresh authorization. Never replace a
stale `ruleDigest` automatically: `STALE_RULE_DIGEST` requires reconsideration
under current rule semantics.

## 4. Property evidence contract

Populate every property from authoritative evidence:

| Property | Source and rule |
|---|---|
| `version` | Preserve schema version `1`. |
| `id` | Stable unique project identifier; never recycle it for another decision. |
| `rule` | Exact known portable rule id from the current finding. |
| `ruleDigest` | Exact current digest emitted by the pinned AAK version; never recall it from memory. |
| `scope` | Narrowest stable scope matching the finding; repository-wide scope remains review-visible. |
| `decision` | Specific accepted deviation, without claiming compliance. |
| `reason` | Current constraint preventing correction; convenience is insufficient. |
| `risk` | Concrete architectural, product, security, operational, or evolution consequence accepted. |
| `authorizedBy` | Resolvable decision references proving applicable authority. |
| `expiresOn` | Optional ISO date for a time-bound grant; it does not replace an event trigger. |
| `reviewWhen` | At least one concrete reconsideration or removal event. |

Obtain rule, digest, scope, message, evidence, and references from current JSON
validation output or `aak explain <RULE> --format json`. Verify every
`authorizedBy` reference resolves. Preserve unrelated waivers.

## 5. Mode-specific procedure

### `CREATE`

Run validation and select exactly one eligible finding. Establish deviation,
reason, risk, authority, narrow scope, and removal condition. Add one record and
retain the original violation as `WAIVED`.

### `UPDATE`

Compare record, finding, digest, decision, authority, scope, expiry, and
triggers. Apply only the authorized delta. Treat semantic expansion or a new
digest as a new risk decision, not a clerical refresh.

### `REVIEW`

Check whether reason, risk, minimal scope, authority, expiry, digest, and
`reviewWhen` remain valid. Choose `KEEP`, `REAUTHORIZE`, `NARROW`, or `REMOVE`;
do not edit merely to reset a review clock.

### `REMOVE`

Confirm the deviation was corrected, disappeared, or lost authorization. Delete
only the obsolete record, validate, and require the finding to be `PASS`,
`NOT_APPLICABLE`, legitimately reviewed, or visibly failing. Deleting a record
does not fix nonconforming code.

## 6. Scope and lifecycle rules

Prefer the exact project, source, dependency edge, module, host, or artifact
scope emitted by the finding. Do not use `.` or a broad glob when a smaller
stable scope suffices. Prove a near miss outside the scope is not waived.

Review or remove a waiver when it expires, a trigger occurs, its digest becomes
stale, authority no longer applies, scope no longer matches, compliance becomes
safe, or accepted risk changes. An unused, expired, broad, invalid, or stale
waiver remains visible. Never waive the waiver-governance finding itself.

## 7. Editing and validation sequence

~~~text
1. Read repository instructions, pinned core, applicable rule explanation,
   policy, authority declaration, decisions, and current waivers.
2. Run current validation as JSON and preserve the complete target finding.
3. Apply the eligibility decision; stop waiver authoring for NOT_A_WAIVER.
4. Resolve only material risk, authority, or lifecycle unknowns.
5. Derive mechanical fields and edit only the target record in
   .agentic/policies/architecture/waivers.json.
6. Validate the JSON through normal AAK validation.
7. Confirm the original rule and scope report WAIVED, never PASS.
8. Confirm an adjacent nonmatching scope remains unwaived.
9. Test expiry, stale digest, missing authority, and removal behavior when
   waiver tooling or conventions changed.
10. Run strict validation and report every FAIL, WAIVED, and REVIEW_REQUIRED.
~~~

Do not weaken code, policy, adapters, catalog rules, or validation to make the
waiver apply. Do not invent an ADR that falsely claims prior authorization.

## 8. Acceptance protocol

A waiver change is complete only when:

- the target is a current violation of a known portable rule;
- correction is currently unsafe or infeasible for a recorded reason;
- applicable authority explicitly accepts a concrete risk;
- every required field has current evidence;
- scope is the narrowest stable match and a near miss is not waived;
- the exact current `ruleDigest` was authorized and stored;
- decision references resolve and lifecycle triggers are actionable;
- the original finding is `WAIVED`, not `PASS`;
- stale, expired, missing-authority, and obsolete states remain visible;
- the completion report explains how to remove the deviation.

## 9. Friendly completion report

~~~text
Outcome: <CREATED|UPDATED|KEPT|REAUTHORIZED|NARROWED|REMOVED|NOT_A_WAIVER>
Underlying architectural deviation:
Why a waiver is or is not appropriate:
Accepted risk and authority:
Exact rule and scope:
Expiry and review/removal conditions:
Fields derived automatically:
Validation result, including visible WAIVED status:
Remaining FAIL, WAIVED, or REVIEW_REQUIRED findings:
Required follow-up:
~~~

Lead with the architectural consequence, not the JSON diff. If material
authority remains unresolved, leave the failure visible and ask one concise
decision-level question.
