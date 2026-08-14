# Language policy

English is the canonical language for the packaged architecture decision core,
operational agent guides, portable rule references, tooling, contracts,
schemas, rule identifiers, templates, and machine-readable output. The root
manifesto is a human-facing map, not a second normative source.

Spanish translations are maintained under [`docs/es/`](es/). They exist to make
the architecture accessible, but they do not define independent semantics. If a
translation conflicts with its English source, the English source is
authoritative.

Changes to `README.md`, `MANIFESTO.md`, `docs/team-guide.md`,
`docs/create-project-from-zero.md`, `docs/capabilities.md`, or
`docs/github-governance.md` should update the corresponding Spanish
translation in the same change. A translation that cannot be updated atomically
must be marked as out of date at its beginning; silent divergence is prohibited.

The packaged bootstrap and GitHub governance guides under
`src/agentic_architecture_kit/data/guides/` are the version-matched operational
copies exposed by the CLI. Their web renditions under `docs/` must preserve the
same procedure and may add only navigation or web-specific context.

Code identifiers and configuration keys remain in English in every language so
examples are directly executable and searchable.
