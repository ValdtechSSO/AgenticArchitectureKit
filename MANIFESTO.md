# Repository Architecture Manifesto for Coding Agents

[Español](docs/es/MANIFESTO.md) · [Architecture decision core](src/agentic_architecture_kit/data/norms/agent-core.md) · [Portable rules](src/agentic_architecture_kit/data/norms/portable-rules.md)

> **Status:** human-facing rationale and map. The executable normative sources
> are the packaged architecture decision core and portable rule references.

## Purpose

Agentic Architecture Kit exists so a coding agent can create, modify, and evolve
a project autonomously inside boundaries decided by a team. A repository should
provide enough context, policy, authority, and validation for the agent to know
what it may change, where behavior belongs, and how to prove completion without
asking a human to repeat decisions already recorded.

The architecture is not an exhaustive tree. It is the smallest coherent set of
capability boundaries, ownership, contracts, code, validation, navigation, and
evidence justified by current knowledge.

## Enforcement-oriented documentation

The kit separates guidance by who enforces it:

| Enforcer | Content | Loading model |
|---|---|---|
| Agent | Decisions that are expensive to undo after implementation | Read completely before structural decisions |
| Validator | Observable constraints whose repair is local and reversible | Load through a finding reference |
| Human | Rationale, adoption guidance, and falsifiable evaluation | Excluded from agent bootstrap |

The distinction is based on reversal cost, not topic. Structural economy remains
in the agent core even though the validator can detect some symptoms, because a
late correction may require rewriting completed work. A forbidden directory
name can remain validator-owned because renaming it is cheap.

Human guidance is not an escape hatch for an unenforced obligation. Reducing a
document from agent or validator enforcement to human-only guidance is an
architectural change protected by decision references and authority review.

## Governed autonomy

Autonomy is the default inside declared product intent, ownership, risk, and
authority. Escalation is reserved for a material decision that has not been
delegated: changing product meaning, accepting risk, transferring ownership,
weakening a rule, or acting outside authorized scope.

The repository, not conversation history, carries architectural memory. Context
is retrieved progressively from a deterministic bootstrap through module
contracts, invariants, decisions, dependencies, consumers, data, tests, and
revision-bound evidence.

## Conformance model

Three project-owned layers specialize the portable distribution:

1. Project policy declares modules, hosts, projects, boundaries, and allowed
   dependencies.
2. Waivers record bounded and authorized acceptance of a known violation.
3. Reviews record an accepted semantic judgment for an exact finding.

Portable rules cannot be silently weakened through project policy. Waivers and
reviews bind the digest of the rule semantics under which they were granted, so
an upgrade cannot reuse old authority against a changed rule.

Declared architecture expresses intent; adapters observe source and build
artifacts. Conformance compares both. Syntax validation alone is not an
architecture check.

## Operational loop

```text
Task
  → read the preventive decision core
  → locate ownership and current boundaries
  → validate before modifying an existing repository
  → declare and validate the minimum architecture for a new repository
  → implement inside the smallest cohesive boundary
  → follow normative references only when findings require them
  → update code, declarations, decisions, enforcement, and evidence atomically
  → validate again before declaring completion
  → PASS / FAIL / WAIVED / REVIEWED / NOT_APPLICABLE / REVIEW_REQUIRED
```

A missing normative reference is a failure. It is never permission to recreate
a rule from memory.

## Distribution and project ownership

The versioned Python distribution carries the validator, schemas, rule catalog,
normative documents, neutral templates, and technology adapters. A consumer
repository pins the distribution and owns only its policy, authorities, waivers,
reviews, contracts, decisions, generated context, and evidence.

Vendoring the validator is an explicit offline exception, not the default
installation model.

## Authority and evidence

Deterministic checks can prove repository facts. Semantic judgments remain
`REVIEW_REQUIRED` until an authorized review binds their fingerprint, rule
digest, scope, revision, reviewer, and platform approval evidence.

Repository declarations and CODEOWNERS are only one half of enforcement. Branch
protection and recorded approvals are platform facts and need platform controls.

Completion comes from build, tests, architecture validation, risk-specific
checks, approvals, and retained evidence. An agent's assertion is not evidence.

## Falsifiable evaluation

The architecture should be evaluated by comparing outcomes with and without the
kit: placement accuracy, speculative structure, dependency violations,
navigation effort, unnecessary escalation, and evidence completeness.

Semantic search, external context services, and multi-agent workflows are
optional. Their complexity is justified only by measured improvement over
deterministic indexes and repository search.

## Success criterion

The kit succeeds when a new agent can create the smallest justified
architecture, locate ownership, retrieve minimum sufficient context, evolve
boundaries without speculative structure, recognize decisions outside its
authority, validate its work, and hand the repository to another agent without
relying on conversational memory.

The directory tree is a consequence. The architecture is the protected and
explainable relationship between decisions, ownership, code, validation,
context, authority, and evidence.
