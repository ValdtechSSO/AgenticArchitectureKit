# Semantic code intelligence

[Español](es/semantic-code-intelligence.md)

AAK separates interactive compiler discovery from deterministic architecture
evidence. AAK owns architecture authority and conformance; a semantic provider
such as Roslynk discovers compiler-resolved code relationships; Git, builds, and
tests prove repository state and executable behavior.

## Agent workflow

For .NET, discover an existing solution and, when Roslynk is configured, open it
once and wait until it is ready. Prefer its read-only symbol, definition,
reference, caller, implementation, hierarchy, and diagnostic operations over
text search. Record provider, coverage, and whether each conclusion is
semantic, syntactic, textual, inferred, or unknown. Diagnostics speed up edits
but never replace the real build and test suite.

If Roslynk is absent or incomplete, use the technology adapter and `aak context`
fallback, label the lower resolution, and keep `Indexing`, `Ambiguous`,
`NotFound`, `Stale`, `Conflict`, partial coverage, and truncation visible.

## Validation contract

Semantic validation is opt-in in project policy:

```json
{
  "observation": {
    "semantic": {
      "provider": "roslynk",
      "mode": "advisory",
      "solution": "Product.slnx",
      "capabilities": ["source-dependencies"]
    }
  }
}
```

The provider name selects exactly one
`agentic_architecture_kit.semantic_observers` entry point whose distribution is
pinned in `.agentic/toolchain.json`. `advisory` uses semantic evidence when
available and reports explicit fallback. `required` makes missing, partial, or
truncated evidence review-required and makes stale, malformed, mismatched, or
repository-escaping evidence fail.

An observation declares provider/version, repository revision, subject,
coverage, configurations, exclusions, structured diagnostics, semantic source
edges, and a repository-relative input manifest with SHA-256 content hashes.
AAK recalculates the canonical workspace fingerprint before accepting it.

Complete coverage may replace lower-resolution candidates only for covered
files. Partial or unavailable coverage preserves syntactic fallback. An
observed edge never modifies policy or grants permission.

Use `aak context status` to inspect provider, coverage, resolution, fingerprint,
fallback, and degradation reason. `aak context index` includes the same
provenance without duplicating a large symbol graph.

Machine-readable degradation uses stable codes: `PROVIDER_NOT_CONFIGURED`,
`PROVIDER_NOT_INSTALLED`, `PROVIDER_NOT_PINNED`, `PROVIDER_AMBIGUOUS`,
`PROVIDER_UNAVAILABLE`, `SUBJECT_NOT_FOUND`, `SUBJECT_AMBIGUOUS`,
`INDEXING_INCOMPLETE`, `UNSUPPORTED_CONFIGURATION`, `PARTIAL_COVERAGE`,
`TRUNCATED_RESULT`, `STALE_INPUT`, `INPUT_HASH_MISMATCH`, `PATH_ESCAPE`,
`INVALID_PROVIDER_OUTPUT`, and `CAPABILITY_NOT_PROVIDED`. Providers should use
structured diagnostics rather than converting operational errors into an empty
dependency set.

## Roslynk boundary

Roslynk is not a dependency of the core package. A real bridge belongs in a
separate `aak-dotnet-roslynk` distribution and must consume a stable, bulk,
non-truncated machine-readable export. Interactive outlines or one
`find_references` call per symbol are not exhaustive CI evidence. Until that
export exists, the core contract is tested with deterministic fake providers.
