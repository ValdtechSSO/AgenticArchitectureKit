# Architecture tools

The reference tools separate five inputs:

1. portable rule semantics in `rules.json` and `validator/engine.py`;
2. project architecture in `.agentic/policies/architecture/project-policy.json`;
3. explicit exceptions in `waivers.json`;
4. fingerprint-bound semantic acknowledgements in `reviews.json`;
5. technology observation in `validator/adapters/`.

Python 3.9 or newer is required. There are no third-party runtime dependencies.
The included adapters support SDK-style .NET repositories and Python packages.

## Validation

```bash
./tools/scripts/validate-architecture.sh
./tools/scripts/validate-architecture.sh --format json
./tools/scripts/validate-architecture.sh --base-ref origin/main
./tools/scripts/validate-architecture.sh --write-review-template /tmp/reviews.json
./tools/scripts/validate-architecture.sh --task-id TASK-123 --fail-on-review
./tools/scripts/validate-architecture.sh --list-rules
python3 -m unittest discover -s tools/architecture/tests -v
```

`FAIL` returns exit code 1. An unresolved `REVIEW_REQUIRED` also returns 1 with
`--fail-on-review`. A matching semantic acknowledgement changes that finding to
`REVIEWED`; it does not claim mechanical proof. Invalid configuration returns 2.

CI should supply `--base-ref` so adding a module, host, project, exact dependency
permission, or scalable dependency rule requires an existing `decisionRefs`
document. Every result records canonical SHA-256 digests of policy, waivers,
reviews, rule catalog, and observed architecture. This makes “green by editing
the exam” visible and makes unrecorded architecture growth fail.

`--task-id` retains `architecture.json` and `manifest.json` under
`.agentic/runtime/evidence/{task-id}/{revision}/`.

## Progressive context

```bash
python3 tools/architecture/context.py index
python3 tools/architecture/context.py locate "order lifecycle"
python3 tools/architecture/context.py symbol CreateOrder
python3 tools/architecture/context.py references CreateOrder
python3 tools/architecture/context.py tests CreateOrder
python3 tools/architecture/context.py impact src/Modules/Orders
```

The generated index is revision tagged. Locate results are declared starting
points. Reference results are observed exact-text matches and state that limited
confidence explicitly. They are not represented as compiler-grade semantics.

## Guarantees and limits

- A waiver produces `WAIVED`, never `PASS`.
- An unused waiver produces `REVIEW_REQUIRED`; invalid, expired, or missing-scope
  waivers fail. A repository-wide or multi-owner scope requires review.
- A semantic review matches the rule, exact scope, and subject fingerprint. When
  evidence changes, the old review becomes stale.
- `HOST001` proves source path placement only. It does not prove that a file
  named `Endpoints/OrderService.cs` lacks domain behavior.
- `DEP001` and `DEP002` use project references plus namespace/import evidence.
  C# parsing is intentionally lexical; Python imports use the standard AST.
- Observed data writes and compiler-grade symbol identity remain roadmap items.

See [`../../docs/capabilities.md`](../../docs/capabilities.md) for the complete
status matrix.

## Supported contract subsets

JSON Schema validation implements the subset used by the bundled schemas:
`type`, `required`, `properties`, `additionalProperties`, `items`, `minItems`,
`minLength`, `enum`, and local `#/$defs/...` references. It is not a general
Draft 2020-12 implementation.

The YAML reader for `module.contract.yml` accepts indentation-based mappings,
scalar sequences, quoted and plain scalars, booleans, null, inline JSON arrays
and objects, and folded/literal scalar blocks. It deliberately rejects sequence
items that contain nested mappings. Projects that need general YAML or JSON
Schema support should replace only the contract-loading implementation while
preserving the public schemas and rule semantics.
