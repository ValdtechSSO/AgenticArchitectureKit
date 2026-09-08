# Using semantic code intelligence

Semantic code intelligence improves discovery; it does not change architecture
authority. Keep these responsibilities separate:

```text
AAK: architectural authority and conformance
semantic provider: compiler-semantic discovery
Git/build/tests: repository state and executable proof
```

## Recommended .NET workflow

1. Run the AAK preflight and locate the owning module.
2. Discover the applicable solution path; do not create one speculatively.
3. If Roslynk is available, call `open_solution` once.
4. Wait for ready status. `Indexing` is an explicit incomplete state, not
   permission to fall back silently.
5. Use semantic navigation for symbols, references, callers, implementations,
   and hierarchy.
6. Record whether evidence is semantic, syntactic, textual, inferred, or
   unknown, including provider and coverage.
7. Implement the smallest authorized change.
8. Use `get_diagnostics` for rapid feedback during editing.
9. Run the real build, tests, and AAK validation before completion.

Useful read-only Roslynk tools include `open_solution`, `get_solution_status`,
`search_symbols`, `get_symbol`, `get_members`, `find_definition`,
`find_references`, `get_callers`, `find_implementations`,
`get_type_hierarchy`, and `get_diagnostics`.

## Safety and evidence rules

- AAK guidance and validation depend only on read-only provider operations.
- Never infer dependency permission from a semantic result.
- Do not call `reload_solution` proactively when the file watcher maintains the
  model.
- `get_diagnostics` does not replace builds, generators, packaging, migrations,
  integration tests, browser tests, or other authoritative project checks.
- Treat `Indexing`, `Ambiguous`, `NotFound`, `Stale`, `Conflict`, and
  `truncated` as explicit states.
- Store only repository-relative POSIX paths; never persist workstation paths,
  tokens, secrets, or unredacted provider logs.
- The intended provider connection is local or loopback and read-only. Do not
  send source or secrets to external services.

## Fallback

When semantic intelligence is unavailable, use the selected technology adapter
and existing `aak context` commands. Label evidence as syntactic or textual and
report the reason and reduced confidence. Never claim compiler-resolved
references. If a material decision requires semantic exactness, classify it as
`TECHNOLOGY_OBSERVATION_GAP`.

Interactive Roslynk queries are not automatically a complete validation
snapshot. Evidence consumed by AAK must use the provider-neutral semantic
observer contract, declare coverage and truncation, and match the current
content-hashed input manifest.
