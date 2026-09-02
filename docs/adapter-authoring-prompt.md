# Agent prompt for a technology adapter

[Español](es/adapter-authoring-prompt.md)

Use this prompt to instruct a coding agent to create a new Agentic Architecture
Kit technology adapter or extend an existing one. Replace every bracketed value
before sending it. This prompt is operational guidance, not a second normative
source. The pinned AAK decision core, catalog, rule references, schemas, and
adapter contract remain authoritative.

## 1. Mission and supplied decisions

~~~text
Adapter source directory: <ADAPTER_DIRECTORY>
Adapter distribution name: <DISTRIBUTION_NAME>
Adapter entry-point name: <ADAPTER_NAME>
Language or source ecosystem: <LANGUAGE>
Build or package system: <BUILD_SYSTEM>
Compatible AAK version: <AAK_VERSION>
Initial support boundary: <SUPPORTED_VERSIONS_AND_CONSTRUCTS>
Generated, vendor, cache, and build paths: <IGNORED_PATHS>
Repository composition: <SINGLE_TECHNOLOGY|MIXED_TECHNOLOGY|UNKNOWN>
Acceptance repository, if any: <TARGET_REPOSITORY_OR_NONE>
Blind acceptance required: <YES|NO>
Additional organization or project rules: <EXTENSION_RULES_OR_NONE>

Create or extend a separately versioned AAK observation adapter. The adapter
reports repository facts; it does not decide whether those facts are permitted.

Treat the base AAK rule semantics as invariant across technologies. Translate
only the evidence required by those rules. Do not inject language-specific
concepts into portable rule meaning. Do not infer product semantics from names
or paths unless project policy explicitly declares that classification.
~~~

The person supplying the prompt owns the guarantee, subject-identification
contract, explicit exceptions, and acceptable evidence for extension rules. The
implementation agent owns adapter code, packaging, fixtures, positive and
negative tests, documentation, and verification evidence.

## 2. Mandatory context and discovery

~~~text
Before editing files:

1. Run and read completely from the pinned distribution:

   aak core
   aak guide adapter-development
   aak validate --list-rules

2. Read the public observation model, adapter loader, relevant schemas, and
   every normative reference required by the matrix below. Never reconstruct a
   missing rule from memory.

3. Inspect authoritative specifications for the target language and build
   system. Identify exact syntax or metadata for build units, source identities,
   dependencies, test roles, and generated output. Prefer parsed manifests and
   syntax trees over names, conventions, and regular expressions.

   Explicitly investigate the negative space: source files with no declared
   namespace or module, top-level statements, implicit or global imports,
   aliases, conditional compilation, generated partial source, dynamic build
   expressions, multiple build units in one directory, and test projects outside
   production roots. A construct is not absent merely because the easiest parser
   cannot assign it an identity.

   Build an output-path catalog for every supported ecosystem. In a mixed
   repository, distinguish paths parsed by this adapter from paths merely
   traversed for structural evidence. Do not claim complete repository coverage
   when another ecosystem needs its own adapter or analyzer.

4. For an existing adapter, inspect its entry point, fixtures, limitations,
   version compatibility, and consumer-visible behavior before proposing edits.

5. Before implementation, produce a coverage matrix. Classify every evidence
   capability as EXACT, HEURISTIC, UNSUPPORTED, or CORE_ONLY; name its source
   and every base or extension rule that consumes it.

6. If blind acceptance is required, deny the implementation phase access to the
   acceptance repository, its policy, filenames, layout, history, generated
   indexes, and reference adapter output. Use only AAK contracts, authoritative
   technology specifications, and synthetic fixtures until the candidate is
   tested and content-frozen. Record this boundary in the completion evidence.
~~~

Do not ask the user to design Python packaging, observation dataclasses, parser
helpers, safe paths, sorting, deduplication, or tests. Derive those details from
the pinned AAK contract. Ask only when a missing answer changes a guarantee,
subject classification, accepted evidence, exception, risk, ownership, or
release boundary.

## 3. Separation of responsibilities

Preserve this boundary:

~~~text
Technology adapter
  observes manifests, source constructs, identities, edges, roles, and paths

Project policy and module contracts
  declare modules, hosts, ownership, public contracts, allowed dependencies,
  authoritative data, risks, invariants, and decisions

Portable or extension rule
  evaluates whether declared and observed facts conform

Waiver
  accepts one bounded violation without converting it to PASS

Semantic review
  accepts one exact REVIEW_REQUIRED fingerprint under declared authority
~~~

The adapter must never hide an observed fact because an exception or waiver may
apply. It reports the fact; policy, rule evaluation, waiver processing, or
semantic review determines its architectural meaning.

Keep common traversal, root confinement, POSIX path normalization,
deduplication, deterministic ordering, and ignored-output behavior consistent.
Technology-specific code should only parse constructs that prove facts.

Observation scope comes from project policy. The adapter must obey configured
search roots, but its report must make clear that files outside those roots were
not examined. A policy-scoped empty result is not proof that the repository has
no matching files.

## 4. Base rule evidence contract

Use this matrix as the mandatory starting contract. Adapter responsibility
describes evidence expected by the current AAK model. CORE_ONLY means the
adapter must not duplicate that rule in technology code.

| Rule | Invariant guarantee | Adapter responsibility and reliable evidence | Exceptions and uncertainty |
|---|---|---|---|
| POL001 | Project policy is valid and material decision references resolve. | CORE_ONLY: policy loading, schemas, paths, and decision resolution belong to AAK. | Never compensate for invalid policy in the adapter. |
| ARC001 | Declared and observed modules, hosts, build units, names, test roles, and source ownership agree. | Observe roots from configured locations; discover every in-scope build unit and name from manifests; obtain test roles from mechanical metadata; parse source identities; keep identity-less but relevant source files visible and associate them with a build unit only when that association is mechanically reliable. | Names are heuristic unless the technology defines them. Missing, implicit, or ambiguous local ownership remains visible. Configured roots can exclude real build units and must be reported as an evaluation-scope limitation. |
| MOD001 | Every observed module has a semantic contract and local agent router. | Report every actual module root under the configured module root. Contract and router validation are CORE_ONLY. | Never omit a module because its contract or router is missing. |
| MOD002 | Module contract identity matches its root. | Report actual module roots. Identity comparison is CORE_ONLY. | No technology-specific exception. |
| MOD003 | Product modules represent functional capabilities, not configured technical categories. | Report module roots without judging whether their names are functionally meaningful. | Technical-name classification comes from policy. |
| FEAT001 | Application behavior has a cohesive feature owner and observed feature roots agree with policy. | Report relevant directories and source paths beneath declared feature roots. | Filesystem agreement cannot prove semantic cohesion; uncertainty requires review. |
| HOST001 | Host source stays in declared adaptation and composition locations. | Report host roots and every relevant host-owned source file, including disallowed paths and source without an explicit namespace or module declaration. | Never filter a source merely because it violates an allowed pattern or lacks a source identity. |
| DEP001 | Production modules do not depend on hosts. | Report build edges, source edges, source and target identities, project association, and mechanically proven test roles. Exercise both explicitly namespaced/module source and identity-less forms such as top-level entry points. | Only proven test projects receive the verification-consumer exception. If the public model cannot express an edge from identity-less source, declare the blind spot or propose a core change; never drop the edge silently. Ambiguous ownership requires review. |
| DEP002 | Cross-module access targets an explicitly declared public contract. | Report complete cross-boundary edges with target identity precise enough for contract-pattern matching, including aliases and implicit forms inside the declared support boundary. | The adapter never decides what is public. Parse, mark heuristic, or document unsupported aliases, reflection, wildcards, implicit/global imports, dynamic loading, conditional source, and generated code. |
| DEP003 | Every observed owned dependency is permitted by policy. | Report all supported repository-local build and source dependencies with source, direction, construct kind, confidence, and the evidence used to resolve each endpoint. | Never silently classify a local edge as external or omit it because an endpoint lacks an explicit source identity. |
| OWN001 | Authoritative data has exactly one declared owner. | Report only evidence representable by the current contract. If reliable write evidence needs a new field, propose a core model change. | Missing analyzer or model support requires review. The adapter never assigns semantic data ownership. |
| CHG001 | Material architecture growth and reduced enforcement have recorded decisions and review. | CORE_ONLY: Git-base comparison and normative classification belong to AAK. | Newly observed facts are not permission to expand policy. |
| STR001 | Catch-all structure and duplicated structural inventories are prohibited. | Report relevant directories while excluding proven generated, vendor, cache, and build output. Build exclusions from authoritative defaults and explicit configuration for every supported ecosystem, not only the primary language. | Forbidden product names come from policy; never hide them. In mixed repositories, unknown output from another ecosystem remains visible and is reported as a coverage limitation rather than guessed away. |
| DOC001 | Normative and architectural references resolve with complete rule coverage. | CORE_ONLY: reference and catalog validation belong to AAK. | Missing references fail; do not infer them. |
| WVR001 | Waivers are explicit, bounded, authorized, current, and tied to rule semantics. | CORE_ONLY: always report the underlying fact. | Never implement ignore lists or waiver matching in the adapter. |
| AUT001 | Architecture authority is declared and repository-protected. | CORE_ONLY: authorities and CODEOWNERS evaluation belong to AAK. | Platform enforcement remains external evidence. |
| REV001 | Semantic reviews bind the exact finding, digest, scope, authority, revision, reviewer, and platform evidence. | CORE_ONLY: review validation belongs to AAK. | Never convert uncertainty to PASS inside the adapter. |

For every non-CORE_ONLY row, map abstract evidence to authoritative technology
constructs. An MSBuild project may map to a build unit, ProjectReference to a
build edge, a C# namespace to a source identity, and a C# using directive to a
source dependency. These examples do not redefine portable semantics.

## 5. Extension rule contract

Append one block for every organization or project rule. Do not implement the
rule until every required field has an explicit value.

For a project-owned rule, first run `aak guide project-rule-authoring-prompt`.
It decides whether adapter observation is needed at all and keeps validation
semantics in the evaluator rather than the technology observer.

~~~yaml
ruleId: <STABLE_RULE_ID>
scope: <portable|organization|project>
title: <SHORT_TITLE>
guarantee: <WHAT_MUST_ALWAYS_BE_TRUE>
subjects:
  description: <WHAT_ELEMENTS_THE_RULE_APPLIES_TO>
  identification:
    exact:
      - <AUTHORITATIVE_IDENTIFICATION_SIGNAL>
    heuristic:
      - <OPTIONAL_HEURISTIC_SIGNAL_OR_NONE>
acceptedEvidence:
  - <FACT_REQUIRED_TO_EVALUATE_THE_RULE>
exceptions:
  - condition: <EXPLICIT_EXCEPTION_OR_NONE>
    authority: <WHO_MAY_DECLARE_IT>
observation:
  technologyConstructs:
    - <LANGUAGE_OR_BUILD_CONSTRUCT>
  modelMapping: <EXISTING_MODEL_FIELD_OR_REQUIRED_CORE_CHANGE>
  minimumConfidence: <exact|NAMED_LOWER_CONFIDENCE>
uncertaintyResult: <REVIEW_REQUIRED|NOT_APPLICABLE>
positiveFixtures:
  - <EXAMPLE_THAT_MUST_PASS>
negativeMutations:
  - <ONE_MINIMAL_CHANGE_THAT_MUST_FAIL>
reviewTriggers:
  - <WHEN_EVIDENCE_OR_ACCEPTANCE_BECOMES_STALE>
~~~

If evidence fits the public observation model, extend the adapter and evaluator
as applicable. If it does not fit, propose explicit model, serialization,
schema, context-index, evaluator, catalog, normative-reference, and compatibility
changes. Never overload an unrelated field to avoid a core contract change.

Use native project architecture tests or a language analyzer for project-only
constraints when portability provides no current benefit. Promote a rule to an
organization or portable extension only when its semantics remain stable for
multiple real consumers.

## 6. Implementation sequence

~~~text
1. Record the support boundary and exclusions.
2. Build the rule-to-evidence-to-technology coverage matrix.
3. Create the separately versioned Python distribution and unique entry point.
4. Implement read-only observation with repository-confined POSIX paths.
5. Return sorted, deduplicated facts with honest confidence.
6. Create minimal synthetic fixture repositories; do not require a real product
   repository or copy an example architecture as a prescribed template.
7. Make the fixtures cover source with explicit identity and source without it,
   including top-level entry points, implicit/global imports, aliases, tests
   outside production roots, and multiple build units where the ecosystem
   permits them.
8. Add a positive fixture and a negative mutation for every automatic rule fed
   by the adapter.
9. Include a forbidden source edge without a build-project edge so tests prove
   source observation actually runs. Repeat it for identity-less source or mark
   that form UNSUPPORTED with the resulting rule blind spot.
10. Include nested generated, vendor, cache, and build paths for every supported
    ecosystem. In mixed-repository fixtures, prove which paths remain visible
    because they belong to an unsupported ecosystem.
11. Test malformed manifests, ambiguity, path escape, ignored output,
    deterministic repetition, overlapping search roots, search-root omissions,
    and unsupported constructs.
12. Install through the real entry point and run the pinned AAK validator
    against complete fixture policies.
13. Document exact, heuristic, and unsupported coverage. Never present an
    unsupported or out-of-scope empty collection as proof that no facts exist.
14. Run package tests, syntax checks, and strict architecture validation.
15. If blind acceptance is required, freeze the candidate before inspecting the
    target by recording a sorted content manifest and digest. Keep fixtures
    writable in a content-identical test copy; file permissions are not evidence
    of source immutability.
~~~

Do not add another language, build system, framework, or speculative observation
capability without a current requirement and test consumer.

## 7. Required tests and evidence

The completed adapter must demonstrate:

- its entry point is installed, unique, callable, and returns the exact public
  AAK observation model;
- authoritative inputs yield the expected build units, source identities,
  dependencies, roles, and directories within the declared support boundary;
- relevant source without an explicit namespace or module remains in
  `sourceFiles`; dependencies from that source are either represented through a
  mechanically justified identity or declared as an explicit model blind spot;
- implicit/global imports, aliases, conditional constructs, and generated
  source are each parsed, rejected, or named as unsupported rather than omitted
  accidentally;
- generated, vendor, cache, and build output are excluded without hiding product
  source, including nested output for every supported ecosystem;
- emitted paths are repository-relative POSIX and cannot escape the root;
- project references resolve to observed build units;
- test projects are covered both inside and outside common production roots, and
  a test proves that policy search roots can intentionally exclude them;
- mixed-technology fixtures distinguish complete technology observation from
  generic structural traversal and unsupported ecosystems;
- output and digests are deterministic across repeated executions;
- malformed authoritative inputs fail clearly rather than producing partial
  success;
- exact evidence and heuristics have distinguishable confidence;
- every supported automatic rule has a negative mutation with the expected rule
  id and scope;
- unsupported evidence is documented and never represented as an exact empty
  observation;
- consumer toolchain configuration pins the exact adapter version.

The current AAK contract cannot explicitly express complete versus unsupported
observation capabilities. Record this limitation in the adapter coverage matrix
and completion report. Absence of findings alone is not proof of complete
coverage.

## 8. Blind acceptance protocol

Use this protocol when an acceptance repository is supplied and the adapter
must be generated without learning from it:

~~~text
1. Before target access, record the candidate version, file manifest, content
   digest, test results, coverage matrix, and explicit unsupported constructs.
2. Freeze the candidate. Do not inspect the target policy, tree, filenames,
   history, generated indexes, or any existing/reference adapter before this
   point.
3. After the freeze, inspect repository instructions and run the candidate
   read-only with the target's actual policy scope. Do not modify the target.
4. Reconcile the observation against an independent inventory: build units,
   references, source counts, identity-less source, test projects, relevant
   directories, and representative source-only edges.
5. Repeat observation with deliberately widened search roots in memory or in a
   temporary policy. This separates adapter blind spots from policy scope.
6. If a reference adapter exists, compare normalized facts only after freeze.
   Explain every difference; a match is supporting evidence, not the oracle.
7. Run the full pinned AAK pipeline. When target and candidate pin different AAK
   versions, use temporary policy/toolchain copies and disclose the difference.
8. Classify every discrepancy as ADAPTER_GAP, POLICY_SCOPE_GAP,
   CORE_MODEL_GAP, UNSUPPORTED_ECOSYSTEM, or TARGET_CONFORMANCE_FINDING.
9. Do not patch the frozen candidate during the acceptance run. A corrected
   version is a new candidate, new version, new digest, and a fresh blind run.
10. Re-run the synthetic suite from a writable content-identical copy, verify
    the original digest is unchanged, and show that target Git status was not
    changed by the evaluation.
~~~

A successful target validation demonstrates conformance only for the declared
and reconciled coverage. It does not erase reported blind spots.

## 9. Completion report

Return a concise evidence-backed report:

~~~text
Adapter distribution and version:
Entry-point name:
Supported language/build-system boundary:
Repository-composition boundary:
Files created or changed:
Base-rule coverage:
Extension-rule coverage:
Exact observations:
Heuristic observations:
Unsupported observations and blind spots:
Core-contract changes, if any:
Positive fixtures:
Negative mutations:
Commands executed and results:
Consumer installation and toolchain pin:
Blind-boundary attestation and pre-target digest:
Acceptance repository and policy scope:
Independent inventory reconciliation:
Reference-adapter comparison, if used:
Discrepancies by category:
Post-acceptance digest and target Git status:
Remaining risks or REVIEW_REQUIRED cases:
~~~

Do not declare completion while a required test, reference, model change, or
strict validation remains unresolved.
