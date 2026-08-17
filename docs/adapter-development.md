# Writing a technology adapter

[Español](es/adapter-development.md)

A technology adapter observes repository facts for a language or build system.
It does not decide whether the architecture is valid: portable rules remain in
Agentic Architecture Kit.

## 1. Create a separate distribution

Build the adapter as a separately versioned Python package. Pin the compatible
kit version and register one lowercase adapter name:

```toml
[project]
name = "aak-rust-adapter"
version = "0.1.0"
dependencies = ["agentic-architecture-kit==0.4.6"]

[project.entry-points."agentic_architecture_kit.adapters"]
rust = "aak_rust_adapter:observe"
```

The entry-point name must match `[a-z][a-z0-9_]*` and must equal the consumer
policy's `adapter` value. Exactly one installed entry point may use that name.

## 2. Implement the observation contract

The entry point is a callable with this contract:

```python
from pathlib import Path

from agentic_architecture_kit.model import (
    ObservedArchitecture,
    Project,
    SourceDependency,
    SourceNamespace,
)


def observe(root: Path, policy: dict) -> ObservedArchitecture:
    config = policy.get("adapterConfig", {})
    # Read manifests and sources under root. Never write to the repository.
    projects = (
        Project(
            path="crates/planning/Cargo.toml",
            name="planning",
            references=(),
            namespaces=("planning",),
        ),
    )
    return ObservedArchitecture(
        modules=("crates/planning",),
        hosts=("crates/cli",),
        projects=projects,
        source_files=("crates/planning/src/lib.rs",),
        source_dependencies=(
            SourceDependency(
                source_path="crates/planning/src/lib.rs",
                source_namespace="planning",
                target_namespace="contracts",
                kind="use",
                confidence="exact",
            ),
        ),
        directories=("crates/planning/src",),
        source_namespaces=(
            SourceNamespace(
                source_path="crates/planning/src/lib.rs",
                namespace="planning",
                project_path="crates/planning/Cargo.toml",
                confidence="exact",
            ),
        ),
    )
```

The static values above illustrate the model only. A real adapter derives them
from current manifests and source files.

## 3. Populate the model honestly

- `modules` and `hosts` are observed repository-relative roots.
- `Project.path` is the repository-relative manifest or build-project path;
  `references` contains exact paths to other observed projects.
- `role_hint="test"` is allowed only when build metadata or another mechanical
  signal proves that role.
- `root_namespace` and `namespaces` describe import identities declared by a
  project. For languages without namespaces, use the stable package, crate, or
  module identity used by imports.
- `source_files` lists relevant source paths.
- `SourceNamespace` associates a declared import identity with its source and,
  when known, its project.
- `SourceDependency` records a directed source-level edge. `kind` names the
  observed construct, such as `use`, `import`, or `require`.
- `directories` supplies structural observation for portable structure rules.

All paths use repository-relative POSIX form, never escape `root`, and exclude
generated, vendor, cache, and build-output directories. Return sorted tuples so
the observation digest is deterministic. Use `confidence="exact"` for parsed
build/source facts and a clear lower-confidence value for heuristics.

## 4. Keep policy and rules outside the adapter

The adapter may read `roots`, `projectSearchRoots`, `structureSearchRoots`, and
its namespaced `adapterConfig`. It must not:

- write project policy, waivers, reviews, contracts, or source files;
- invent modules from hoped-for future structure;
- allow or reject a dependency;
- redefine `DEP001`, `DEP002`, or another portable rule;
- turn missing or ambiguous evidence into a claimed exact observation.

When the technology cannot prove a fact, omit it or mark its confidence
honestly. The validator decides whether that gap is `NOT_APPLICABLE`,
`REVIEW_REQUIRED`, or a failure.

## 5. Configure a consumer repository

Install the adapter distribution beside the pinned kit. Add it to
`.agentic/toolchain.json` so version drift blocks validation:

```json
{
  "version": 1,
  "distribution": "agentic-architecture-kit",
  "toolVersion": "0.4.6",
  "catalogVersion": 2,
  "extensions": [
    {"distribution": "aak-rust-adapter", "version": "0.1.0"}
  ]
}
```

The project policy selects the same entry-point name and supplies only
technology-specific observation settings under `adapterConfig`:

```json
{
  "adapter": "rust",
  "adapterConfig": {"workspaceManifest": "Cargo.toml"},
  "roots": {"modules": "crates", "hosts": "apps"},
  "projectSearchRoots": ["crates", "apps"],
  "structureSearchRoots": ["crates", "apps"]
}
```

That excerpt is not a complete project policy; start from
`aak template project-policy.template.json` and validate the complete document.
External adapters are loaded by `aak validate`. Automatic technology detection
and observed-policy seeding in `aak init` and `aak adopt` currently cover the
built-in adapters, so an external adapter's initial policy must be prepared and
reviewed explicitly.

## 6. Test both observation and failure detection

Use a minimal fixture repository and test:

1. exact observed modules, hosts, projects, source identities, and edges;
2. deterministic output across repeated runs;
3. ignored build/cache/vendor paths;
4. malformed manifests and paths escaping the repository;
5. a negative mutation for every automatic rule the new observation feeds.

Install the extension in the test environment so entry-point discovery is also
exercised, then run `aak validate` against a complete fixture policy. Include at
least one forbidden source edge with no build-project reference; a green result
must prove that the adapter looked, not merely that it returned no edges.

## 7. Release checklist

- The adapter package and compatible kit version are exact pins.
- The entry-point name is unique and matches policy.
- Observation is read-only, deterministic, repository-bounded, and factual.
- Every emitted path and project reference resolves inside the fixture.
- Exact and heuristic evidence use distinguishable confidence values.
- Positive and negative integration fixtures pass with `--fail-on-review` as
  intended.
