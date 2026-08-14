# Releasing the distribution

[Español](es/releasing.md)

Releases are maintainer-authorized external changes. An agent may prepare and
verify a release, but it must not publish one unless the repository authority
has explicitly authorized that release.

## One-time setup

1. Create or reserve the `agentic-architecture-kit` project on PyPI.
2. Configure a PyPI trusted publisher for this GitHub repository, workflow
   `publish.yml`, environment `pypi`.
3. Create the protected GitHub environment `pypi` and restrict deployment to
   authorized maintainers and release tags.
4. Apply the branch and CODEOWNERS controls in
   [`github-governance.md`](github-governance.md).

No long-lived PyPI token is stored in the repository. The workflow requests a
short-lived identity token only in its publish job.

## Release procedure

1. Update the version consistently in `pyproject.toml`, the package, the
   toolchain template, immutable schema URLs, examples, and documentation.
2. Review rule, schema, migration, and compatibility changes.
3. Run the conformance suite, strict self-validation, package build, and an
   isolated wheel validation against the examples.
4. Merge through the protected branch using the configured team review or
   solo-maintainer attestation workflow.
5. Publish a GitHub release whose tag is exactly `v{package-version}`.
   Creating or pushing the tag alone does not trigger publication; the GitHub
   release must transition to the published state.
6. The `Publish Python distribution` workflow builds from that release, checks
   the tag/version match, verifies artifacts, and publishes through PyPI trusted
   publishing.
7. Confirm the published artifact and update consumers through an explicit
   `.agentic/toolchain.json` change.

Never reuse a published version or edit an offline export in place. A portable
rule or schema change requires a new distribution version, even when the catalog
format version itself remains compatible.
