# ADR-002: Classify architecture guidance by enforcer

Status: accepted

## Context

A single long manifesto forced an agent to load validator details, preventive
decisions, and human justification with equal prominence. Splitting only by
topic would preserve that attention problem and multiply translation drift.

## Decision

Architecture guidance is classified by who enforces it and by the cost of late
discovery. Expensive-to-reverse decisions belong in the agent core. Mechanical,
cheaply reversible constraints belong in validator rules. Explanatory and
evaluation material belongs in human guidance and is not normative.

Moving material toward human-only enforcement reduces protection and therefore
requires a decision reference and semantic authority review.

## Consequences

The agent reads a small preventive core, runs the gate at deterministic points,
and follows rule references only when needed. Normative references and their
classification become machine-checkable distribution assets.
