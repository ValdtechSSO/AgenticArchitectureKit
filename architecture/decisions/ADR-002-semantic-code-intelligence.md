# ADR-002: Semantic code intelligence is advisory to agents and evidence-bound for validation

## Status

Accepted.

## Decision

Semantic code intelligence has two separate planes. Coding agents may use a
configured compiler-semantic provider interactively to navigate symbols,
references, callers, implementations, hierarchies, and diagnostics. AAK uses
semantic results for validation or retained evidence only through its
provider-neutral, read-only observation contract. Such evidence identifies the
provider and version, declares coverage and truncation, and is bound to the
exact repository revision and a content-hashed input manifest.

Roslynk is the recommended interactive provider for C# and Razor, but it is not
a runtime dependency of AAK. A separately distributed bridge may register an
`agentic_architecture_kit.semantic_observers` entry point once Roslynk exposes a
complete, stable, machine-readable dependency export. A live daemon or compact
interactive outline alone is not exhaustive, deterministic CI evidence.

AAK remains authoritative for ownership, dependency permissions, rules,
waivers, and findings. Semantic observation cannot grant an architectural edge
and validation never invokes provider mutation operations. Compiler diagnostics
shorten the edit loop; real builds and tests remain completion evidence.

## Alternatives rejected

- Replacing the .NET adapter with live MCP calls would make ordinary validation
  dependent on a daemon and would discard structural fallback.
- Parsing outlines from individual symbol queries would hide incompleteness and
  truncation.
- Copying or forking Roslynk into AAK would couple the lightweight Python
  distribution to .NET and duplicate upstream ownership.
- Treating every C# `using` directive as a resolved reference would preserve
  false positives and miss fully-qualified, alias, generated, and conditional
  references.

## Consequences

Projects without semantic configuration behave as before. Advisory projects
degrade explicitly to syntactic or textual evidence. Required projects cannot
complete strict validation when evidence is missing, partial, truncated, stale,
or malformed. Complete per-file semantic coverage may replace lower-resolution
source-dependency candidates, while uncovered files retain their fallback.

## Review triggers

- A provider is allowed to mutate repositories during observation.
- AAK begins wrapping general language-service operations.
- Provider evidence no longer declares complete coverage and exact inputs.
- Build or test execution is proposed to be replaced by semantic diagnostics.
