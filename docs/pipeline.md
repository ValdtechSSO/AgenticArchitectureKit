# Implementing AAK in a delivery pipeline

[Español](es/pipeline.md)

This is the web rendition of the version-matched guide printed by
`aak guide pipeline`. It connects Agentic Architecture Kit to continuous
integration from checkout through merge protection.

## 1. Required outcome

The pipeline must execute the exact kit and adapter-extension versions declared
by the project, observe the candidate source, evaluate portable and local gates,
retain revision-bound evidence on success and failure, and expose a required
check that can really block delivery.

CI does not choose architecture. It proves that declared decisions, observed
code, accepted exceptions, review evidence, and the current revision agree.

## 2. Execution model

The central command is:

```bash
aak validate --base-ref BASE_REVISION --fail-on-review --task-id architecture-ci
```

Its internal flow is:

```text
toolchain and catalog
→ policy, waivers, reviews, and authorities
→ trusted base policy
→ adapters.observe(policy["adapter"], root, policy)
→ ObservedArchitecture
→ module contracts and 17 portable rules
→ revision-bound result and exit code
```

The adapter only returns facts. The rules, waivers, and semantic reviews decide
their architectural result.

## 3. Prerequisites

The repository needs a valid `.agentic/toolchain.json`, architecture policy,
waivers, reviews, authorities, real CODEOWNERS routing, an installable selected
adapter, and stable commands for project-specific architecture rules. Run
`aak core`, `aak guide bootstrap`, and `aak guide github-governance` first.

## 4. Fast path: let adoption connect GitHub Actions

Preview without writes and then apply:

```bash
aak adopt --root . --codeowner @your-org/architecture --ci github --dry-run
aak adopt --root . --codeowner @your-org/architecture --ci github
```

Adoption adds the packaged workflow only when it will not overwrite an existing
CI file. Otherwise it reports the integration work. For a new repository,
initialize the truthful minimum architecture and obtain the workflow with:

```bash
aak template github-architecture.yml
```

## 5. Reference GitHub Actions workflow

The pinned template performs a full checkout, installs AAK, selects a trusted
base, validates, and always uploads evidence:

```yaml
name: Architecture conformance

on:
  push:
  pull_request:

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v7
        with:
          python-version: "3.11"
      - name: Install pinned architecture kit
        run: python3 -m pip install --no-deps agentic-architecture-kit==0.4.9
      - name: Validate architecture
        env:
          BASE_REVISION: ${{ github.event_name == 'pull_request' && github.event.pull_request.base.sha || github.event.before }}
        run: |
          if [ -n "$BASE_REVISION" ] && git cat-file -e "$BASE_REVISION:.agentic/policies/architecture/project-policy.json"; then
            aak validate --base-ref "$BASE_REVISION" --fail-on-review --task-id architecture-ci
          else
            aak validate --fail-on-review --task-id architecture-ci
          fi
      - name: Retain architecture evidence
        if: always()
        uses: actions/upload-artifact@v7
        with:
          name: architecture-evidence-${{ github.run_id }}
          path: .agentic/runtime/evidence/
          if-no-files-found: error
```

Update the workflow pin and `toolchain.json` atomically during an explicit kit
upgrade. Use the action versions emitted by the pinned template as the starting
point rather than copying an old web example blindly.

## 6. Why every workflow element exists

| Element | Guarantee |
|---|---|
| Full Git history | The base revision and reviewed ancestor commits are reachable. |
| Exact kit and extension pins | Rules, schemas, CLI, and observation do not drift silently. |
| Event-specific base SHA | `CHG001` sees the real policy delta. |
| `--fail-on-review` | Unresolved semantic uncertainty cannot masquerade as green. |
| `--task-id` | JSON evidence and its manifest are retained for the revision. |
| `if: always()` | Failed runs retain their diagnostics. |
| Required branch check | A failing report actually blocks delivery. |

## 7. Selecting the base revision

For pull requests use the PR base SHA; for pushes use the event's previous SHA.
Do not assume every event targets `origin/main`. During first adoption the base
may not contain AAK policy, so test for the policy file and run without
`--base-ref` only in that bootstrap case. Subsequent governed changes should use
comparative validation.

## 8. Built-in, external, and local adapters

The `dotnet` and `python` adapters are included. An external adapter must be
installed beside AAK and pinned in `toolchain.json`:

```bash
python3 -m pip install --no-deps \
  agentic-architecture-kit==0.4.9 \
  aak-rust-adapter==1.2.3
```

The project selects the entry-point name in `project-policy.json`. A
`LOCAL_UNCOMMITTED` adapter can be used on its local machine, but CI must fail
closed until that exact distribution is available through an authorized
private or public artifact channel. Never commit an absolute local source path
or silently fall back to another adapter.

## 9. Exit codes and gate policy

| Exit | Meaning |
|---|---|
| `0` | Validation satisfied the selected strictness. |
| `1` | A rule failed, or strict mode found unresolved `REVIEW_REQUIRED`. |
| `2` | Configuration, schema, version pin, path, or adapter contract is invalid. |

`WAIVED` and `REVIEWED` remain visible accepted states, not mechanical `PASS`.
An expired or stale grant does not apply.

## 10. Evidence and artifacts

`--task-id architecture-ci` writes:

```text
.agentic/runtime/evidence/architecture-ci/{revision}/
  architecture.json
  manifest.json
```

The result records revision, base, adapter, findings, evidence, and canonical
digests for toolchain, policy, waivers, reviews, authorities, catalog, and
observed architecture. Upload it with retention appropriate to risk. Regenerate
runtime evidence; do not maintain it manually in Git.

## 11. Project-specific architecture rules

AAK evaluates the 17 portable rules. A project rule needs a separately connected
analyzer, architecture test, compiler check, or linter. Create it through
`aak guide project-rule-authoring-prompt` and run its stable command in the same
job or another required job, for example:

```yaml
- name: Project architecture rules
  run: dotnet test tests/Architecture/Architecture.Tests.csproj
```

Do not present a local analyzer as a portable AAK result.

## 12. Branch protection and review authority

Require the exact `Architecture conformance / validate` check on the protected
branch. Apply the authority mode from `authorities.json`: team mode requires an
independent CODEOWNER approval; solo-maintainer mode requires the check, no
direct pushes, and durable external attestation for semantic judgments. See
`aak guide github-governance` for the complete platform settings.

## 13. Other CI platforms

On another platform, preserve the same contract: full checkout, exact installs,
trusted base calculation, project checks, strict AAK validation, unconditional
evidence upload, and a mandatory merge or deployment gate. Platform YAML may
change; AAK inputs, adapter behavior, exit codes, and evidence semantics do not.

## 14. Failure diagnosis

1. For exit 2, check pins, installed extensions, schemas, paths, and entry-point
   uniqueness.
2. For `FAIL`, run `aak explain RULE_ID` and repair code or an inaccurate
   declaration.
3. For `REVIEW_REQUIRED`, resolve the semantic judgment under declared
   authority; do not manufacture certainty in the adapter.
4. For stale waivers or reviews, reassess the current fingerprint and digest.
5. For a missing base, verify full history and event-specific SHA selection.
6. For missing artifacts, verify `--task-id` and unconditional upload.

Never broaden policy, replace the adapter, disable strict mode, or add a waiver
merely to regain green.

## 15. Completion checklist

- Exact kit and extension pins are installed.
- The selected adapter is available without fallback.
- Pull request, push, and bootstrap bases are handled correctly.
- Portable and project-specific checks execute.
- Evidence uploads on pass and failure.
- Branch protection requires the exact status check.
- Platform review controls match `authorities.json` and CODEOWNERS.
- A deliberate invalid mutation makes the pipeline fail.
- A valid candidate produces evidence for its exact commit.

The pipeline is complete only when a failing check actually prevents delivery;
the workflow file alone is not enforcement.
