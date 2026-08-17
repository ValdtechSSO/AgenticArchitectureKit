# Portable validator rules

Each second-level heading is the normative reference for exactly one portable
rule. Findings link here so an agent can load rule details only when needed.

## POL001 — Project policy is valid

Project policy must conform to the bundled schema, use resolvable repository
paths, declare unique identities, and reference existing architectural
decisions where a material boundary is introduced.

## ARC001 — Declared and observed architecture agree

Declared modules, hosts, projects, names, mechanically observable test roles,
and dependencies must agree with what the selected technology adapter observes
in source and build metadata.

## MOD001 — Modules have semantic contracts

Every observed module must have a schema-valid `module.contract.yml` and a local
`AGENTS.md` router. The contract owns non-derivable semantics, not generated
structural inventories.

## MOD002 — Module identity matches its root

The normalized module contract identifier must match its module directory so
ownership and navigation remain deterministic.

## MOD003 — Modules represent functional capabilities

Product modules must represent functional capabilities. A configured technical
category must not appear as a product module.

## FEAT001 — Application behavior has a cohesive feature owner

Observed root feature areas must match policy. Mechanical agreement does not
prove semantic cohesion, so uncertain ownership remains reviewable.

## HOST001 — Host source stays in declared adapter locations

Host source must remain within declared adapter and composition paths. This path
rule does not by itself prove that every behavior is pure composition.

## DEP001 — Modules do not depend on hosts

No production module-owned project or source namespace may depend on a
host-owned project or namespace. A project classified with role `test` and
matched by observed test-project evidence is a verification consumer excluded
from this direction rule; it may depend on the host or module behavior it
verifies.

## DEP002 — Cross-module access uses public contracts

Cross-module dependencies must target an explicitly declared public contract
boundary rather than another module's implementation.

## DEP003 — Project dependencies are authorized

Every observed project and owned source dependency must be permitted by exact
project edges or scalable dependency selectors in project policy.

## OWN001 — Authoritative data has one owner

Authoritative data must have one declared owner. When the adapter cannot prove
write ownership, the remaining semantic judgment requires review.

## CHG001 — Architecture changes have a recorded decision

New or materially changed modules, hosts, projects, dependency permissions, and
reductions in normative enforcement relative to a Git base require resolvable
decision references and explicit authority review.

## STR001 — Speculative structure is prohibited

Configured catch-all directories and duplicated structural inventories in
semantic contracts are prohibited. Material structural changes are governed by
CHG001 rather than inferred from directory count.

## DOC001 — Normative and architectural references resolve

Rule references, normative document classifications, module invariants, and
architecture-decision links must resolve to existing documents and headings.
Every validator-rule heading must be referenced by exactly one catalog rule.

## WVR001 — Waivers are explicit, bounded, and current

A waiver must identify a known rule and scope, record decision, reason, risk,
authority, review conditions, and the exact rule digest under which it was
granted. A stale digest cannot silence a current violation.

## AUT001 — Architecture authority is declared and protected

Every declared protected scope must be covered by a real CODEOWNERS pattern
owned by its authority principals. A narrower pattern cannot remove that
authority inside its scope. Team mode declares pull-request, code-owner,
stale-review, no-direct-push, and status-check enforcement. Solo-maintainer mode
requires exactly one principal and declares pull-request, no-direct-push, and
status-check enforcement without pretending that self-review is independent.
Platform configuration remains external evidence.

## REV001 — Semantic reviews are explicit and current

A semantic review must bind the exact finding fingerprint, rule digest, scope,
authority, reviewer, approval evidence, and reachable repository revision. A
semantic change invalidates the acknowledgement. GitHub team mode requires pull
request review evidence. GitHub solo-maintainer mode requires a durable
maintainer attestation URL outside the review record itself.
