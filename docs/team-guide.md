# Team Guide

[Español](es/team-guide.md) · [Manifesto](../MANIFESTO.md) ·
[Agent bootstrap guide](create-project-from-zero.md)

This guide is for project owners, architects, maintainers, and reviewers using
Agentic Architecture Kit. It explains what the kit places in a repository, why
each artifact exists, who may change it, and how a team governs autonomous agent
work without becoming an approval bottleneck.

It is not a second manifesto. The [manifesto](../MANIFESTO.md) is normative. This
guide translates that standard into everyday team practice.

## 1. The operating model

The kit turns team decisions into durable, executable repository context:

```text
Team intent
    ↓
Architecture documents, contracts, ADRs, and project policy
    ↓
Agent navigation and implementation
    ↓
Observed source and dependency structure
    ↓
Architecture validator and project tests
    ↓
Revision-bound evidence
```

The objective is governed autonomy:

- the team decides product direction, risk appetite, ownership, and authority;
- the repository makes those decisions discoverable and enforceable;
- the agent handles routine implementation and architectural maintenance inside
  that authority;
- people intervene only when a material decision has not been delegated.

The repository is the shared memory. A prior conversation with an agent is not
required to understand why the current architecture exists.

## 2. Three kinds of information

Understanding the repository is easier when every artifact is classified as
portable, project-specific, or generated.

### 2.1 Portable kit assets

These come from Agentic Architecture Kit and have the same semantics in every
project:

```text
tools/architecture/
tools/scripts/validate-architecture.sh
.agentic/contracts/schemas/
```

They include the rule catalog, validation engine, technology adapters, schemas,
and validator tests. A project consumes them; it does not reinterpret them.

Portable rule changes belong in the kit and should be brought into projects as
an explicit kit update. A project-specific need is not a reason to edit the
meaning of a portable rule.

### 2.2 Project-specific maintained assets

These describe the actual product and evolve with it:

```text
AGENTS.md
architecture/
domain/
src/Modules/*/AGENTS.md
src/Modules/*/module.contract.yml
.agentic/policies/architecture/project-policy.json
.agentic/policies/architecture/waivers.json
.agentic/policies/architecture/reviews.json
tests/Architecture/
```

They may be updated by a person or by an agent acting inside delegated
authority. Changes to policy, ownership, ADRs, invariants, or waivers are
architectural changes and deserve explicit review visibility.

### 2.3 Observed and generated assets

These are derived from source, build configuration, or validation runs:

```text
.agentic/generated/
.agentic/runtime/evidence/
```

They may contain project graphs, symbols, dependencies, test relationships, and
validation results. They are regenerated rather than maintained manually.

Generated data is useful evidence but not semantic authority. If a generated
index disagrees with current source or revision, it is stale.

## 3. Artifact reference

| Artifact | Purpose | Maintained by | Team review focus |
|---|---|---|---|
| `README.md` | Introduces the product and its normal entry points | Team or agent | Accuracy for new contributors |
| Root `AGENTS.md` | Small router with commands, map, critical rules, and prohibited operations | Team or authorized agent | Whether authority and safety boundaries are clear |
| `architecture/system-overview.md` | Current high-level capabilities, hosts, integrations, and dependency direction | Team or authorized agent | Whether it describes the system that exists now |
| `architecture/decisions/ADR-*.md` | Records why a material architectural decision was made | Decision owner; agent may draft | Context, alternatives, consequences, review triggers |
| `domain/global-invariants.md` | Product rules that apply across several capabilities | Product/domain owners; agent may update from approved requirements | Correctness and scope of every invariant |
| `domain/contexts/*.md` | Vocabulary and invariants owned by one capability | Owning team or authorized agent | Domain meaning and ownership |
| Module `AGENTS.md` | Local reading path, commands, and critical rules | Owning team or authorized agent | Whether an unfamiliar agent can start safely |
| `module.contract.yml` | Non-derivable purpose, vocabulary, ownership, risk, invariants, and ADR links | Owning team or authorized agent | Semantic truth, not structural duplication |
| `project-policy.json` | Declares the project's modules, hosts, projects, feature roots, and allowed dependencies | Authorized agent or architecture owner | Whether a changed boundary is justified rather than merely observed |
| `waivers.json` | Records bounded, authorized deviations from portable rules | Authority named by team policy | Exact scope, risk, owner, expiry, and removal condition |
| `rules.json` | Stable portable rule catalog | Kit maintainers | Cross-project semantics and compatibility |
| Technology adapter | Converts technology-specific structure into the common observed model | Kit maintainer or adapter contributor | Observation accuracy; no policy decisions |
| Architecture tests | Enforce project-specific decisions the common validator cannot express | Team or authorized agent | Whether they protect behavior rather than implementation trivia |
| Validation result | Reports conformance for one repository revision | Generated | Failures, waivers, semantic reviews, revision identity |

## 4. What happens when a project is created

The agent does not begin by copying a complete tree. It first records what is
known, assumed, and unknown, then proposes the smallest architecture supported by
current requirements.

The team should expect to see:

1. a capability and ownership proposal;
2. only currently required hosts;
3. only projects or packages that enforce a real boundary;
4. initial invariants and risks;
5. a project policy matching the created structure;
6. an empty waiver file unless a deviation is already authorized;
7. passing automatic validation plus explicitly identified semantic reviews.

The proposal does not require a meeting when the initial product brief already
delegates the relevant choices. Human direction is required when the brief
leaves a material product, risk, or ownership decision genuinely open.

## 5. Routine development

For an ordinary request, the agent follows the existing architecture:

```text
Locate owning module
→ Locate cohesive feature area
→ Read contract, invariants, ADRs, policy, and waivers
→ Inspect relevant source, dependencies, data, and tests
→ Implement
→ Run targeted and required validation
→ Report evidence
```

Most requests should not modify project policy. Adding an operation to an
existing feature area, implementing a port, adding a test, or changing an
internal algorithm normally stays inside an established boundary.

The team should not have to approve routine file placement. That decision is
already delegated through the repository.

## 6. When architecture legitimately changes

Project policy evolves as the product grows. Legitimate examples include:

- a new functional capability with independent vocabulary and ownership;
- a new host required to expose or execute the product;
- a new assembly or package that enforces deployment or dependency isolation;
- a new public contract between current modules;
- removal of a dependency, module, host, or obsolete waiver;
- a feature area whose lifecycle has become observably independent.

A boundary change should arrive as one coherent change:

```text
Implementation
+ project policy
+ module contracts or routers
+ ADR when the decision is material
+ domain documents when meaning changes
+ architecture tests or adapter support
+ waiver changes when applicable
+ validation evidence
```

Policy must not be changed merely to make a validator failure disappear. The
agent should be able to state the current requirement and evidence that justify
every new boundary.

## 7. Agent authority and human intervention

The distinction is not “agent changes” versus “human changes.” It is delegated
versus undelegated authority.

### The agent normally continues when

- behavior clearly belongs to an existing module and feature area;
- the change is reversible and follows established contracts;
- tests, validation, and existing ADRs determine the correct implementation;
- an implementation request clearly requires a new boundary and the decision
  stays inside already delegated product and ownership scope;
- a semantic review can be completed from repository evidence and team rules;
- an obsolete waiver can be removed because its recorded condition is met.

### The agent escalates when

- different options materially change product behavior;
- ownership would move between teams or capabilities;
- proceeding accepts a risk the team has not authorized;
- a portable rule must be deviated from and no authority can approve a waiver;
- the request conflicts with an invariant or accepted ADR and no compatible
  solution exists;
- external, destructive, financial, legal, privacy, or security authority is
  required and not already granted.

An aesthetic preference, minor naming choice, or `REVIEW_REQUIRED` result is not
automatically a reason to ask the user.

## 8. Understanding validator results

| Status | Meaning | Expected response |
|---|---|---|
| `PASS` | The validator demonstrated the rule for the current scope and revision | No action beyond retaining evidence |
| `FAIL` | Observed architecture violates a rule or declaration | Correct code or declaration; do not suppress the check |
| `WAIVED` | A valid explicit waiver authorizes the deviation | Confirm scope and review condition remain correct |
| `REVIEWED` | Delegated authority accepted this exact semantic finding fingerprint | Keep the acknowledgement; changed evidence will make it stale |
| `NOT_APPLICABLE` | The rule has no relevant subject in this project | No action unless architecture changed |
| `REVIEW_REQUIRED` | The tool cannot prove a semantic decision | Agent or person reviews the evidence according to delegated authority |

`PASS` is not a claim that the whole architecture is good; it applies to a rule,
scope, and repository revision. Likewise, `REVIEW_REQUIRED` is not failure. It
prevents semantic uncertainty from being presented as mechanical certainty.

Use strict mode when team policy requires every semantic review to be resolved
before delivery:

```bash
./tools/scripts/validate-architecture.sh --fail-on-review
```

For CI or retained evidence, prefer structured output:

```bash
./tools/scripts/validate-architecture.sh --format json
./tools/scripts/validate-architecture.sh --base-ref origin/main --task-id CI
```

CI should use `--base-ref` whenever it can compare with the target branch. This
makes newly permitted boundaries and dependencies require an existing ADR
instead of allowing an agent to obtain green by merely expanding the policy.

## 9. Waiver governance

A waiver is not a convenient ignore list. It is a visible team decision to
accept one bounded deviation.

A good waiver answers:

```text
Which portable rule is affected?
Where exactly does the exception apply?
Why is it necessary now?
Which risk is accepted?
Who or which ADR authorizes it?
When does it expire or require review?
What event allows its removal?
```

Reviewers should reject waivers that:

- cover an entire repository without necessity;
- have no named authority or ADR;
- describe convenience instead of a real constraint;
- contain no review or removal condition;
- redefine a portable rule for the whole project;
- are added only to turn red validation green.

When a valid waiver no longer matches a violation, the validator reports it for
review so it can be removed.

## 10. Reviewing an agent change

### Routine-change checklist

- Does the change stay in the owning module and cohesive feature area?
- Does it preserve module and host dependency direction?
- Are relevant invariants and ADRs respected?
- Are targeted tests present and passing?
- Does validation evidence match the reviewed revision?
- Did the agent avoid unrelated structural growth?

### Architectural-change checklist

- Which current requirement justifies the new or changed boundary?
- Is ownership explicit?
- Could the change remain inside an existing cohesive boundary?
- Does the policy describe intent rather than hide observation?
- Are code, contracts, ADRs, tests, and policy updated atomically?
- Are new dependencies minimal and directional?
- Is a waiver truly necessary, bounded, and authorized?
- Are semantic reviews resolved within the correct authority?

### Context-quality checklist

- Can a new agent locate the owning area from the root router?
- Do module contracts use current domain vocabulary?
- Do links to invariants and ADRs resolve?
- Is structural data derived rather than duplicated manually?
- Is generated evidence tied to the current revision?
- Can another agent continue without the previous conversation?

## 11. Common mistakes

### Treating the kit as a folder template

Creating every optional directory makes navigation worse and invents boundaries.
Only materialize current responsibilities.

### Editing policy to mirror every code change

Policy describes architectural boundaries, not every file or class. Most code
changes should leave it untouched.

### Creating technical modules

`Git`, `Providers`, `Validation`, or `Repositories` are normally implementation
details inside a functional owner, not product capabilities.

### Making each command a root feature

Commands sharing concept, state, invariants, and lifecycle belong together.

### Treating generated data as maintained truth

Generated indices describe one revision. Semantic ownership remains in
maintained contracts and policy.

### Asking people to decide routine implementation

If the answer is already derivable from repository authority, the agent should
decide, implement, validate, and continue.

### Letting the agent silently assume authority

Autonomy does not permit changing product direction, accepting undelegated risk,
or moving ownership without an explicit basis.

## 12. Updating the kit in a project

Treat the portable validator, schemas, rule catalog, and adapters as a versioned
dependency even when they are vendored into the repository.

Recommended update flow:

1. identify the current and target kit versions;
2. review portable rule and schema changes;
3. update the portable payload without overwriting project policy;
4. migrate project policy only when the new schema requires it;
5. run the validator's own tests;
6. run project architecture validation;
7. review new `FAIL` or `REVIEW_REQUIRED` results;
8. record material adoption decisions in an ADR.

Never replace these project-specific files with kit templates during an update:

```text
AGENTS.md
architecture/
domain/
src/Modules/*/module.contract.yml
.agentic/policies/architecture/project-policy.json
.agentic/policies/architecture/waivers.json
```

Templates are for initialization and reference, not upgrades.

## 13. Suggested team governance

A lightweight operating agreement is enough:

- product or domain owners approve new invariants and material behavior changes;
- architecture owners approve cross-capability ownership changes and waivers;
- agents may maintain policy and ADRs when implementing already authorized work;
- reviewers require evidence for architecture changes, not extra ceremony;
- CI runs automatic conformance checks;
- unresolved semantic reviews are assigned according to risk and authority;
- the team periodically removes expired waivers and stale decisions.

The objective is not centralized architectural permission. It is to make team
decisions durable enough that routine work no longer needs permission.

## 14. First review of a generated project

When an agent creates a repository with this kit, a team member can review it in
this order:

1. read root `AGENTS.md` for purpose, commands, and critical boundaries;
2. read `architecture/system-overview.md` for capabilities and hosts;
3. inspect `domain/global-invariants.md` and capability contexts;
4. inspect each `module.contract.yml` for vocabulary, ownership, and risk;
5. inspect `project-policy.json` for declared modules, projects, and dependencies;
6. confirm `waivers.json` is empty or every entry is explicitly authorized;
7. run `./tools/scripts/validate-architecture.sh`;
8. review all `FAIL`, `WAIVED`, and `REVIEW_REQUIRED` results;
9. confirm build and project tests pass;
10. confirm another agent could continue from repository content alone.

If those checks succeed, the repository is not merely arranged according to a
style. It contains an executable agreement between the team and the agents that
will evolve it.
