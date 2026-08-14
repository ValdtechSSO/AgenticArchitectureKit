# Architecture tooling and distribution

The reference implementation is published as the versioned Python distribution
`agentic-architecture-kit`. The package keeps seven concerns separate:

1. portable rule semantics, normative references, and their evaluation engine;
2. bundled decision core and JSON contracts;
3. project architecture in `.agentic/policies/architecture/project-policy.json`;
4. explicit waivers and fingerprint-bound semantic reviews;
5. review authority and external enforcement declarations;
6. built-in or plugin-provided technology observation adapters;
7. version-matched operational guides and neutral templates exposed through
   public CLI commands.

Python 3.9 or newer is required. The package has no third-party runtime
dependencies. Built-in adapters support SDK-style .NET repositories and Python
packages.

## Consumer installation

A consumer repository owns `.agentic/toolchain.json`. It pins the distribution,
catalog, and any adapter extensions exactly:

```json
{
  "version": 1,
  "distribution": "agentic-architecture-kit",
  "toolVersion": "0.4.2",
  "catalogVersion": 2,
  "extensions": []
}
```

Run that exact version without installing it globally:

```bash
uvx --from agentic-architecture-kit==0.4.2 aak validate --fail-on-review
uvx --from agentic-architecture-kit==0.4.2 aak context locate "order lifecycle"
```

The same distribution contains everything an agent needs to bootstrap a new
project or bring an existing repository under governance; source-repository
access is not required:

```bash
aak core
aak guide bootstrap
aak guide github-governance
aak template
aak template AGENTS.md
```

`aak` refuses to run validation or context retrieval when its installed version,
catalog version, or installed extension versions differ from the project pin.
Thus an upgrade is an explicit project change rather than an accidental change
in CI or on a developer machine.

`aak init --root . --codeowner @team/architecture` creates only project-owned
governance files and a CODEOWNERS entry. It also asks the selected adapter to
observe the repository and writes a `project-policy.json` proposal containing
the modules, hosts, projects, and exact project-reference edges it found. The
proposal is factual scaffolding: the agent or team must remove accidental or
unjustified boundaries instead of treating observation as architectural approval.

Adapter selection is automatic when `.csproj`, `pyproject.toml`, or Python
sources exist. Before technology artifacts exist, pass `--adapter dotnet` or
`--adapter python`; the generated policy contains empty architecture arrays and
remains valid until product artifacts are introduced.

## Validation

```bash
aak validate
aak validate --format json
aak validate --base-ref origin/main
aak validate --write-review-template /tmp/reviews.json
aak validate --task-id TASK-123 --fail-on-review
aak validate --list-rules
aak core
aak guide bootstrap
aak guide github-governance
aak template AGENTS.md
aak explain DEP001
aak explain CHG001 --base-ref origin/main --format json
```

`FAIL` returns exit code 1. An unresolved `REVIEW_REQUIRED` also returns 1 with
`--fail-on-review`. A matching semantic acknowledgement changes that finding to
`REVIEWED`; it does not claim mechanical proof. Invalid configuration or a pin
mismatch returns 2.

CI supplies `--base-ref` so adding a module, host, project, exact dependency
permission, or scalable dependency rule requires an existing `decisionRefs`
document. Every result records canonical SHA-256 digests of the toolchain,
policy, waivers, reviews, authority declaration, bundled catalog, and observed
architecture.

Every finding carries a resolvable normative `reference` and a `ruleDigest`.
`aak explain` combines that definition with the rule's current repository
status, scopes, observed evidence, and applied waiver or review. A missing
reference is a validation failure.

Every waiver and semantic review must persist that exact `ruleDigest`. A valid
but different digest degrades the grant to `REVIEW_REQUIRED` and prevents it
from applying to the current rule semantics.

`--task-id` retains `architecture.json` and `manifest.json` under
`.agentic/runtime/evidence/{task-id}/{revision}/`.

## Progressive context

```bash
aak context index
aak context locate "order lifecycle"
aak context symbol CreateOrder
aak context references CreateOrder
aak context tests CreateOrder
aak context impact src/Modules/Orders
```

The generated index is revision tagged. Locate results are declared starting
points. Reference results are observed exact-text matches and state that limited
confidence explicitly; they are not compiler-grade symbol semantics.

## Technology extensions

Third-party adapters use the Python entry-point group
`agentic_architecture_kit.adapters`. An extension distribution exposes an entry
named after the policy adapter and is pinned in `.agentic/toolchain.json`:

```toml
[project.entry-points."agentic_architecture_kit.adapters"]
rust = "my_aak_rust_adapter:observe"
```

Portable rules remain owned by this distribution. An adapter observes facts; it
does not silently redefine rule meaning. Project-only semantic checks remain in
the consumer repository's architecture test suite.

## Offline export

Network-isolated environments may explicitly export the package payload:

```bash
aak export-offline --output ./offline
```

The command writes `agentic-architecture-kit-{version}/` and an
`OFFLINE-MANIFEST.json` containing each file's SHA-256 digest. The payload
includes the same operational guides and templates as the installed wheel.
Offline exports must keep their version identity and should be replaced as a
whole, never edited into an untracked fork.

## Guarantees and limits

- A waiver produces `WAIVED`, never `PASS`.
- Invalid, expired, unused, or overly broad waivers remain visible or fail.
- Waivers and semantic reviews bind to the current rule digest; changed rule
  semantics make the previous grant inapplicable and require review.
- Semantic reviews also bind to rule, exact scope, subject fingerprint, reachable
  Git revision, declared authority, CODEOWNER, and platform evidence.
- `AUT001` checks repository declarations, not live hosting-platform settings.
- `HOST001` proves source placement, not behavioral purity.
- Dependency rules use project references plus lexical C# namespace/import
  evidence or Python AST imports.
- Observed data writes and compiler-grade symbol identity remain roadmap items.

See [`capabilities.md`](capabilities.md) for the complete status matrix.

## Supported contract subsets

The zero-dependency JSON Schema and YAML readers implement only the documented
subset used by bundled contracts. See the source tests before extending these
formats; projects needing general parsers should replace contract loading while
preserving public schemas and rule semantics.
