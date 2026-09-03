# Implementing AAK in a delivery pipeline

This guide connects Agentic Architecture Kit to continuous integration from
checkout through merge protection. It is operational guidance for the pinned
distribution, not a second definition of portable rule semantics.

## 1. Required outcome

An effective AAK pipeline must:

1. execute the exact kit and extension versions declared by the project;
2. fetch enough Git history to compare the candidate with its real base;
3. run the project's selected technology adapter against the candidate source;
4. evaluate portable rules and any separately connected project rules;
5. fail on mechanical violations, invalid configuration, and unresolved reviews
   when strict delivery policy requires them to be resolved;
6. retain revision-bound evidence even when validation fails; and
7. expose one required status check that protected branches actually enforce.

CI does not decide architecture. It proves that declared decisions, observed
code, accepted exceptions, review evidence, and the current revision agree.

## 2. Execution model

The pipeline invokes one public command:

```bash
aak validate --base-ref BASE_REVISION --fail-on-review --task-id architecture-ci
```

That command performs this sequence:

```text
load pinned catalog and toolchain
→ validate kit and extension versions
→ load policy, waivers, reviews, and authorities
→ load the base policy when --base-ref is available
→ call adapters.observe(policy["adapter"], root, policy)
→ load module contracts
→ evaluate the 17 portable rules
→ apply valid waivers and fingerprint-bound reviews
→ write revision-bound evidence
→ return a process exit code
```

`adapters.observe(...)` loads a built-in adapter or the uniquely installed
`agentic_architecture_kit.adapters` entry point selected by the project policy.
The adapter returns observed facts. Rules decide whether those facts conform.

## 3. Prerequisites

Before adding the gate, the repository needs:

- a valid `.agentic/toolchain.json` with exact kit and extension versions;
- project policy, waivers, reviews, and authorities under
  `.agentic/policies/architecture/`;
- a real `.github/CODEOWNERS` or the equivalent authority routing for the CI
  platform;
- every selected external adapter installable in the CI environment;
- project-specific architecture checks exposed through a stable command; and
- a protected target branch whose settings can require the AAK check.

Run `aak core`, `aak guide bootstrap`, and `aak guide github-governance` before
inventing or changing any of those controls.

## 4. Fast path: let adoption connect GitHub Actions

For an existing repository, preview the complete adoption without writes:

```bash
aak adopt --root . --codeowner @your-org/architecture --ci github --dry-run
```

Review `projectPolicy`, `plannedFiles`, and `requiredActions`, then apply it:

```bash
aak adopt --root . --codeowner @your-org/architecture --ci github
```

The command adds the packaged workflow only when it can do so without replacing
an existing CI file. If a workflow already exists, adoption reports the required
integration instead of overwriting it. It does not configure GitHub branch
protection; apply the platform controls from `aak guide github-governance`.

For a new repository, run `aak init` first, complete the minimum truthful policy
and contracts, then copy the neutral workflow with:

```bash
aak template github-architecture.yml
```

## 5. Reference GitHub Actions workflow

Use the template emitted by the pinned distribution. Its essential shape is:

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

Replace `0.4.9` only through an explicit kit upgrade, and update
`.agentic/toolchain.json` in the same change. Treat third-party action major
versions as examples from this kit release and update them deliberately.

## 6. Why every workflow element exists

| Element | Reason | Unsafe simplification |
|---|---|---|
| `fetch-depth: 0` | Makes the base revision and reviewed ancestor SHAs reachable. | A shallow checkout can make comparative policy and review checks impossible. |
| Exact package version | Keeps CLI, schemas, rules, templates, and built-in adapters coherent. | `latest`, an unbounded range, or a global install can silently change semantics. |
| Exact extension versions | Makes external adapter selection fail closed on drift. | Installing an arbitrary adapter version makes observation non-reproducible. |
| Real base SHA | Activates `CHG001` against the target branch actually being changed. | Comparing against the candidate itself hides policy growth. |
| `--fail-on-review` | Prevents unresolved semantic uncertainty from being delivered as green. | Omitting it is valid only when another declared process resolves reviews before delivery. |
| `--task-id` | Persists the JSON result and evidence manifest for this run and revision. | Console text alone is a weak audit artifact. |
| `if: always()` | Uploads evidence for failures as well as passes. | Uploading only on success discards the most useful diagnostics. |
| Required branch check | Turns a report into an enforced merge gate. | A workflow that may be ignored is advisory only. |

## 7. Selecting the base revision

For pull requests, compare with the pull request base SHA. For pushes, compare
with the event's previous SHA. Do not assume that `origin/main` names the correct
target for every branch or event.

During first adoption, the base revision may predate AAK policy. Test whether the
base contains `project-policy.json`; if it does not, run strict validation
without `--base-ref`. After the first governed revision lands, comparative
validation should be the normal path.

The base must be a trusted repository revision, not user-controlled arbitrary
input passed from an untrusted build parameter.

## 8. Built-in, external, and local adapters

Built-in `dotnet` and `python` adapters need no additional install. The policy
selects one through its `adapter` field.

An external adapter must be installed beside AAK and pinned in the toolchain:

```json
{
  "extensions": [
    {"distribution": "aak-rust-adapter", "version": "1.2.3"}
  ]
}
```

Install both exact versions from an authorized registry or artifact source:

```bash
python3 -m pip install --no-deps \
  agentic-architecture-kit==0.4.9 \
  aak-rust-adapter==1.2.3
```

A `LOCAL_UNCOMMITTED` adapter works on the machine where its distribution is
installed, but cannot support CI until CI can obtain that exact distribution.
Do not copy its absolute local path into tracked workflow, policy, or toolchain
files. Either keep validation explicitly local or publish a built artifact to an
authorized private channel. Missing extensions must remain a configuration
error, never fall back to another adapter.

## 9. Exit codes and gate policy

| Exit | Meaning | Pipeline response |
|---|---|---|
| `0` | No `FAIL`; and no unresolved `REVIEW_REQUIRED` when strict mode is used. | Continue to the remaining delivery gates. |
| `1` | A portable rule failed, or strict mode found unresolved semantic review. | Block delivery and preserve evidence. |
| `2` | Configuration, schema, path, pin, adapter, or other execution contract is invalid. | Block delivery; repair configuration rather than waiving it. |

`WAIVED` and `REVIEWED` are visible accepted states, not `PASS`. A waiver or
review with a stale rule digest, fingerprint, scope, or revision does not apply.
`NOT_APPLICABLE` means there was no subject for that rule in the evaluated
scope.

## 10. Evidence and artifacts

With `--task-id architecture-ci`, AAK writes:

```text
.agentic/runtime/evidence/
  architecture-ci/
    {repository-revision}/
      architecture.json
      manifest.json
```

The architecture result records the repository revision, base revision when
used, adapter name, findings, evidence, and canonical digests for the toolchain,
policy, waivers, reviews, authorities, rule catalog, and observed architecture.
The manifest records the command arguments, intended exit code, result class,
and digest of the JSON artifact.

Upload the complete task directory with retention appropriate to project risk.
Do not commit runtime evidence as maintained architecture truth; regenerate it
for each revision.

## 11. Project-specific architecture rules

`aak validate` automatically evaluates the portable catalog. A project-specific
rule needs its own analyzer, architecture test, compiler check, or linter gate.
Create it with `aak guide project-rule-authoring-prompt`, then run its declared
command in the same CI job or as another required job.

For example:

```yaml
      - name: Project architecture rules
        run: dotnet test tests/Architecture/Architecture.Tests.csproj
```

Keep the check independently visible. Do not report a project-only analyzer as
if it were one of the 17 portable AAK rule results.

## 12. Branch protection and review authority

After the workflow passes at least once, configure the protected target branch
to require the exact `Architecture conformance / validate` check. Also enforce
the review model declared in `authorities.json`:

- `team`: pull request, approving review, CODEOWNER review, stale-review
  dismissal, required check, and no unauthorized bypass;
- `solo-maintainer`: pull request, required check, no direct or force pushes,
  plus durable external attestation for semantic judgments.

The validator can check that declarations and local records are coherent. Only
the hosting platform can prove that the workflow and review controls were
actually enforced.

## 13. Other CI platforms

The same contract applies outside GitHub Actions:

1. perform a full checkout;
2. install pinned AAK and extensions;
3. calculate the trusted merge-target or previous revision;
4. run project-specific architecture checks;
5. run strict AAK validation with a stable task ID;
6. publish `.agentic/runtime/evidence/` even on failure; and
7. make the resulting job mandatory for merge or deployment.

Platform syntax may change. The validation command, input files, adapter
contract, exit codes, and evidence semantics do not.

## 14. Failure diagnosis

Use this order so symptoms are not mistaken for causes:

1. **Exit 2:** verify installed versions, extension availability, schemas,
   repository paths, and adapter entry-point uniqueness.
2. **`FAIL`:** run `aak explain RULE_ID`, inspect the normative reference and
   evidence, then correct code or an inaccurate declaration.
3. **`REVIEW_REQUIRED`:** determine whether current authority and repository
   evidence can resolve the semantic judgment. Do not convert uncertainty into
   `PASS` inside an adapter.
4. **Stale waiver or review:** regenerate the finding and reassess it under the
   current rule digest; never edit fingerprints merely to regain green.
5. **Missing base:** verify full history and event-specific base selection.
6. **Missing evidence artifact:** ensure `--task-id` ran and artifact upload uses
   an unconditional step.

Do not broaden policy, disable strict mode, replace the adapter, or add a waiver
only to make CI green.

## 15. Completion checklist

- The workflow installs the exact versions declared in `toolchain.json`.
- The selected adapter is available and no fallback can hide its absence.
- Pull requests and pushes calculate the correct trusted base revision.
- First adoption handles a base without AAK policy explicitly.
- Portable validation runs with `--task-id` and the intended review policy.
- Project-specific rules run through their own declared gates.
- Evidence uploads on pass and failure.
- The required check name matches branch protection exactly.
- CODEOWNERS and platform controls match `authorities.json`.
- A deliberately invalid architecture mutation makes the pipeline fail.
- A clean candidate produces evidence tied to its exact commit.

The pipeline is complete only when a failing check actually prevents delivery;
a workflow file by itself is not enforcement.
