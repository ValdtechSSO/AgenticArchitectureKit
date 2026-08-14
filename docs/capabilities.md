# Implementation status

Agentic Architecture Kit is currently a **0.2 preview**. The manifesto is the
normative target; this page states what the reference implementation can prove
today. A manifesto requirement is not represented as implemented merely because
it is documented.

| Capability | Status | Current guarantee |
|---|---|---|
| Portable rules / project policy / waivers | Implemented | Separate schema-validated inputs; waivers produce `WAIVED`, never `PASS` |
| Self-validation | Implemented | The kit has a Python policy and validates its own compact module/host boundary |
| .NET observation | Implemented | SDK-style projects, `ProjectReference`, C# namespaces and `using` directives |
| Python observation | Implemented | `pyproject.toml`, direct packages/CLI files and AST import directives |
| Intra-assembly dependency checks | Initial | Exact namespace/import matching for C# and Python; not a full compiler semantic model |
| Policy-growth protection | Implemented | `--base-ref` detects new boundaries and dependency permissions and requires decision references |
| Policy/result input integrity | Implemented | Results contain canonical digests for policy, waivers, reviews, catalog and observations |
| Persistent semantic reviews | Implemented | An acknowledgement applies only to the exact finding fingerprint and becomes stale when the subject changes |
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
contract, automated tests, a working example where appropriate, and the kit can
exercise it against itself. Documentation-only behavior remains **Roadmap**.
