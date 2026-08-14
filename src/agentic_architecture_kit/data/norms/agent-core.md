# Architecture decision core

This is the complete preventive bootstrap for an implementation agent. Read it
before choosing or changing product structure. Detailed mechanical rules are
loaded through validator findings.

## Governed autonomy

Work autonomously inside decisions, ownership, risk boundaries, and authority
already declared by the team. Escalate only when proceeding would invent a
material product, risk, ownership, or authority decision.

Use repository evidence rather than conversational memory. Distinguish declared
facts, observed facts, inferences, assumptions, and unresolved questions.

## Reversal-cost rule

Prevent a violation before implementation when discovering it later would
require restructuring completed work, undoing an external effect, or assuming
authority. A mechanical constraint whose repair is local, cheap, and reversible
may be discovered by the validator.

Human guidance is explanatory, not a fallback classification for an unenforced
obligation. If a requirement affects agent behavior, it belongs here or in a
validator rule.

## Architecture follows current evidence

Create the smallest architecture justified by current requirements and
observable evidence. Do not create modules, projects, abstractions, shared
components, directory levels, or placeholders solely for anticipated use.

Unknown future needs remain assumptions, risks, or questions until a real
consumer or enforceable boundary exists.

## Capability and feature ownership

Organize product behavior by functional capability, vocabulary, state,
invariants, ownership, and lifecycle. Technical categories such as Git,
Providers, Validation, Persistence, or Services are not product modules unless
they form an independently owned platform with its own contract and lifecycle.

New behavior starts in the existing module and smallest cohesive feature area
that owns it. A command, endpoint, handler, or use case does not by itself
justify a root feature. Create a root feature only when vocabulary, state,
invariants, risk, ownership, or lifecycle is independently meaningful.

## Placement before implementation

Keep orchestration, input/output transformation, feature validation, and port
coordination in `Features/{FeatureArea}`. Promote behavior to `Domain/` only when
it expresses infrastructure-independent domain meaning used by current
behavior. Promote it to `Contracts/` only when another current module or host
consumes it as a public API. Put filesystem, network, persistence, process,
messaging, SDK, and external-service implementations in `Infrastructure/`.

Hosts adapt input/output and compose dependencies. They do not own application
behavior. Modules never depend on hosts.

## Justified boundaries

Create an assembly or package only when it enforces dependency, deployment,
runtime, language, publication, distribution, or ownership boundaries. Create
shared code only for current consumers, with cohesive responsibility and
explicit ownership. Prefer small duplication to a premature shared abstraction.

Before creating a new boundary, locate the owning module, feature, contracts,
invariants, data, dependencies, consumers, and tests. Extend an existing
cohesive boundary by default.

## Atomic boundary changes

A boundary change is incomplete until code, declared policy, module contracts,
local routing, decisions, validation, generated context, and evidence agree.
Plans and requests may supply missing product intent, but they do not silently
waive architecture rules.

## Deterministic gate moments

For an existing repository, run the architecture gate before modifying it. For
a new repository, initialize and declare the minimum architecture, then run the
gate before creating product structure or implementation. Run the gate again
before declaring the task complete.

If a finding provides a normative reference, follow it and load only the
required rule context. A reference that does not resolve is a failure, never
permission to reconstruct the rule from memory.
