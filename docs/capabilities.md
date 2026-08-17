# Implementation status

Agentic Architecture Kit is currently a **0.4 preview**. The packaged decision
core and portable rule references are the normative target; this page states
what the reference implementation can prove today. Documentation alone is not
represented as implemented.

| Capability | Status | Current guarantee |
|---|---|---|
| Portable rules / project policy / waivers | Implemented | Separate schema-validated inputs; waivers produce `WAIVED`, never `PASS` |
| Versioned distribution | Implemented | One Python package bundles CLI, agent core, operational guides, rules, schemas, templates, and adapters; consumer toolchain pins are enforced and an explicit digest-manifested offline export is available |
| Self-contained agent bootstrap | Implemented | `aak core`, `aak guide`, and `aak template` expose the version-matched decision context, operating procedure, GitHub governance, and neutral assets without source-repository access |
| Existing-repository adoption | Implemented | `aak adopt` provides a no-write preview and idempotently orchestrates observed policy, governance, optional GitHub CI, context indexing, strict validation, and explicit semantic follow-up without overwriting existing files |
| Self-validation | Implemented | Structural smoke test plus authorization of real CLI-host → validator imports; every automatic rule is mapped to a negative mutation test, and prohibited/cross-module cases are exercised rather than inferred from a green pass |
| .NET observation | Implemented | SDK-style projects, test-project signals, `RootNamespace`, source-declared namespace ownership, `ProjectReference`, and C# `using` directives |
| Python observation | Implemented | `pyproject.toml`, direct packages/CLI files and AST import directives |
| Intra-assembly dependency checks | Initial | Exact namespace/import matching for C# and Python; unresolved or ambiguous repository-local namespace ownership requires review rather than becoming an empty pass; not a full compiler semantic model |
| Policy-growth protection | Implemented | `--base-ref` detects new boundaries and dependency permissions; CI compares PRs with their base and pushes with their previous SHA |
| Policy/result input integrity | Implemented | Results contain canonical digests for toolchain, policy, waivers, reviews, authorities, catalog and observations |
| Normative-reference integrity | Implemented | Every finding carries a packaged reference and per-rule semantic digest; `DOC001` verifies catalog headings, enforcement classification, module references, and complete validator-heading coverage |
| Contextual rule diagnosis | Implemented | `aak core` exposes preventive context and `aak explain RULE` combines definition, digest, current findings, scope, evidence, and applied grants |
| Persistent semantic reviews | Implemented | Local integrity requires exact fingerprint, reachable ancestor SHA, declared authority, CODEOWNER principal and mode-specific platform evidence; team review and solo-maintainer attestation are externally enforced |
| Semantic grant invalidation | Implemented | The schema rejects a missing rule digest; a valid but stale digest cannot apply and becomes review-required; unrelated catalog changes do not invalidate other rules |
| Authority enforcement | Split guarantee | Every protected scope requires real CODEOWNERS coverage; team mode requires independent review, while solo-maintainer mode makes its single-principal limitation and attestation explicit; GitHub enforcement remains a platform fact |
| Waiver hygiene | Implemented | Unmatched, invalid, expired and overly broad waivers remain visible |
| Generated repository index | Initial | Revision-tagged module, project, dependency, document and test JSON indices |
| Progressive context commands | Initial | Locate, exact-text symbol/reference/test search and direct impact queries with provenance |
| Task evidence | Initial | Architecture results and a digest manifest can be retained by task and revision |
| Host behavioral purity | Roadmap | `HOST001` proves source location only; behavioral ownership needs a language semantic analyzer |
| Observed data-write ownership | Roadmap | Declared ownership uniqueness is checked; actual writes remain reviewable |
| Compiler-grade symbol graph | Roadmap | Current reference search is exact text, explicitly labelled with that confidence |
| Complete build/test/evidence ledger | Roadmap | The kit retains architecture evidence; orchestration of every project tool is not yet included |

“Initial” means usable with a deliberately bounded guarantee. It does not mean
the broader semantic capability described by the manifesto has been completed.

## Release criterion

A capability moves to **Implemented** only when it has a public command or
contract, automated tests, and a working example where appropriate. Dogfooding
is used when the kit has a legitimate real subject; prohibited scenarios are
proved by executable fixtures rather than artificial production boundaries.
Documentation-only behavior remains **Roadmap**.

## Evidence layers

- **Self-validation** proves that the Python adapter runs against the kit, that
  declared and observed structure agree, and that real host → module imports are
  authorized. It does not manufacture a second module merely to exercise a
  cross-module rule.
- **Conformance tests** prove rule mechanics, including stale reviews,
  unreachable review revisions, invalid authority, policy growth, broad waivers,
  and permitted or forbidden dependency edges.
- **Examples** prove consumption without vendoring: one .NET repository passes;
  a compiling single-assembly repository fails on a source-level module → host
  dependency.
- **Platform controls** prove who approved and whether direct mutation was
  prevented. The local repository declares these controls but cannot observe
  GitHub branch protection by itself.
