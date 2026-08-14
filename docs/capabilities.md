# Implementation status

Agentic Architecture Kit is currently a **0.2 preview**. The manifesto is the
normative target; this page states what the reference implementation can prove
today. A manifesto requirement is not represented as implemented merely because
it is documented.

| Capability | Status | Current guarantee |
|---|---|---|
| Portable rules / project policy / waivers | Implemented | Separate schema-validated inputs; waivers produce `WAIVED`, never `PASS` |
| Self-validation | Implemented | Structural smoke test plus authorization of real CLI-host → validator imports; prohibited and cross-module cases are exercised by tests/examples, not invented in the kit |
| .NET observation | Implemented | SDK-style projects, `ProjectReference`, C# namespaces and `using` directives |
| Python observation | Implemented | `pyproject.toml`, direct packages/CLI files and AST import directives |
| Intra-assembly dependency checks | Initial | Exact namespace/import matching for C# and Python; not a full compiler semantic model |
| Policy-growth protection | Implemented | `--base-ref` detects new boundaries and dependency permissions; CI compares PRs with their base and pushes with their previous SHA |
| Policy/result input integrity | Implemented | Results contain canonical digests for policy, waivers, reviews, authorities, catalog and observations |
| Persistent semantic reviews | Implemented | Local integrity requires exact fingerprint, reachable ancestor SHA, declared authority, CODEOWNER principal and approval evidence; actual approval is externally enforced |
| Authority enforcement | Split guarantee | Repository declarations and CODEOWNERS are validated; GitHub branch protection and recorded approval remain platform facts and must be configured externally |
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
- **Examples** prove the portable installation path: one .NET repository passes;
  a compiling single-assembly repository fails on a source-level module → host
  dependency.
- **Platform controls** prove who approved and whether direct mutation was
  prevented. The local repository declares these controls but cannot observe
  GitHub branch protection by itself.
