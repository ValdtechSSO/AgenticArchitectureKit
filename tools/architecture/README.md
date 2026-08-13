# Portable architecture validator

This tool turns the repository architecture manifesto into an executable
conformance check. It deliberately separates:

1. the portable rule catalog in `rules.json`;
2. the project policy in
   `.agentic/policies/architecture/project-policy.json`;
3. explicit project waivers in
   `.agentic/policies/architecture/waivers.json`;
4. technology observation in `validator/adapters/`.

The validator has no third-party runtime dependencies. Python 3.9 or newer is
required. The first adapter supports SDK-style .NET project files.

## Commands

```bash
./tools/scripts/validate-architecture.sh
./tools/scripts/validate-architecture.sh --format json
./tools/scripts/validate-architecture.sh --output .agentic/runtime/architecture.json
./tools/scripts/validate-architecture.sh --fail-on-review
./tools/scripts/validate-architecture.sh --list-rules
python3 -m unittest discover -s tools/architecture/tests -v
```

`FAIL` returns exit code 1. `REVIEW_REQUIRED` is reported but returns zero unless
`--fail-on-review` is used. Invalid policies, catalogs, schemas, or unsupported
adapters return exit code 2.

## Extension boundary

A technology adapter only observes a repository and emits the common model:
modules, hosts, projects, and project dependencies. It does not redefine rule
semantics. New project-specific decisions belong in project policy; a necessary
exception belongs in the waiver file and remains visible as `WAIVED`.

Rules that cannot be demonstrated mechanically return `REVIEW_REQUIRED` rather
than a fabricated `PASS`. The structured result records the repository revision
and conforms to `architecture-result.schema.json`.
