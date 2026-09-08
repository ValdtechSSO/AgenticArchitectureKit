# ADR-003: Long-running agent execution uses content-bound checkpoints

## Status

Accepted.

## Context

Long-running agent work can cross context compaction, handoff, process restart,
or machine boundaries. Git preserves source history but does not preserve the
operational meaning needed to resume safely: objective, active invariants,
decisions and rationale, plan deviations, test state, open risks, and the next
bounded objective. Conversational memory is not durable repository evidence.

## Decision

AAK provides an opt-in execution-checkpoint protocol inside its existing
architecture-governance module. Checkpoints are immutable JSON artifacts under
the ignored `.agentic/runtime/checkpoints/` boundary. Each checkpoint is
content-digested, chained to its predecessor, and bound to the unchanged
repository-relative original plan, Git revision, and content fingerprint of the
non-ignored worktree.

State is cumulative where forgetting would be unsafe. Decisions, rationale,
plan deviations, and risk resolutions cannot disappear or be rewritten.
Removing or changing an invariant requires a new named decision. Closing a risk
requires a retained resolution and evidence.

AAK records test evidence by executing an explicit argument vector without a
shell and retaining its exit code, timestamps, before/after workspace
fingerprints, and content-digested stdout and stderr artifacts. Absence of tests
must have an explicit reason; failed and stale evidence remains visible.

Before continuation, `aak checkpoint resume` verifies and emits the complete
original plan together with the latest checkpoint, then writes a receipt bound
to their digests and workspace. Later checkpoint creation requires that receipt.
The receipt proves input delivery, not private model cognition.

Execution checkpoints remain separate from project policy, architecture
decisions, waivers, semantic reviews, and validation evidence. Their contents
do not authorize architecture, approve a decision, accept risk, or replace the
repository's real build and tests.

## Alternatives rejected

- Git commits alone omit task meaning and can preserve an implementation while
  losing the rationale and risks required to continue it.
- A prose handoff file has no schema, chain, current-worktree binding, or
  mechanical way to detect forgotten state.
- Conversational summaries remain vulnerable to compaction and cannot provide
  repository-verifiable provenance.
- Claiming that a receipt proves comprehension would assert internal model state
  that AAK cannot observe.

## Consequences

Long-running tasks gain a fail-closed resumption path and auditable state
continuity without changing ordinary short-task validation. Runtime artifacts
may contain sensitive product reasoning and require explicit secure retention
when execution moves between environments. Full-worktree content fingerprinting
adds checkpoint-time I/O proportional to non-ignored repository content.

## Review triggers

- Checkpoints begin granting architecture permission or accepting risk.
- Resume no longer supplies both the original plan and complete latest state.
- A later segment can checkpoint without a valid receipt from its predecessor.
- Test success is accepted without revision- and content-bound execution
  evidence.
- Checkpoint artifacts are moved into tracked architecture policy or treated as
  permanent product semantics.
