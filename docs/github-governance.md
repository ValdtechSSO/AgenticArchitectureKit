# GitHub authority enforcement

The local validator can prove that authority is declared consistently, that a
review names an allowed CODEOWNERS principal, and that `reviewedAtRevision` is a
reachable ancestor commit. It cannot prove that GitHub actually recorded an
approval or maintainer attestation, or enabled branch protection. Those are
platform facts.

Set `enforcement.mode` to the repository's real ownership model. Absence of the
field means `team` for compatibility with earlier releases.

## Team mode

For `team`, configure every branch named in
`.agentic/policies/architecture/authorities.json` with:

- require a pull request before merging;
- require at least one approving review;
- require review from Code Owners;
- dismiss stale approvals when new commits are pushed;
- require the `Architecture conformance / validate` status check;
- prevent bypass and direct pushes, including for administrators unless the team
  has explicitly accepted that exception.

Team mode requires at least two people in practice: the pull-request author
cannot supply the independent approval. Its review records use
`github-pr-review:<URL-or-review-id>`.

## Solo-maintainer mode

Use `solo-maintainer` only when exactly one person owns the repository. The
validator requires exactly one unique declared principal and rejects team-only
`code-owner-review` and `dismiss-stale-reviews` requirements that the principal
could not satisfy independently.

Configure each protected branch with:

- require changes to arrive through a pull request;
- require the architecture status check;
- prevent direct pushes and force pushes;
- do not claim an independent approving review or CODEOWNER approval.

The maintainer accepts a semantic judgment by posting a durable GitHub issue,
discussion, or manually approved workflow record outside the candidate diff.
The record should contain the rule ID, scope, rule digest, subject fingerprint,
reviewed commit SHA, and decision. `approvalEvidence` then uses:

```text
github-maintainer-attestation:https://github.com/OWNER/REPOSITORY/issues/NUMBER#issuecomment-ID
```

The agent may prepare the attestation text but must not post or invent the
maintainer's approval. Solo mode explicitly has less reviewer independence than
team mode; its value is a durable human decision and an honest audit trail, not
a fictional self-review.

Every `protectedScope` in `authorities.json` must have a real covering pattern in
`.github/CODEOWNERS` owned by all principals of that authority. A narrower
pattern inside the protected scope cannot remove those principals. For the root
scope (`.`), use a repository-wide entry such as `* @team/architecture`; this
also protects `.github/workflows/` and `CODEOWNERS` itself. Replace the bundled
principal if the repository owner or maintaining team differs.

## Team review record workflow

1. Commit the subject that requires semantic review.
2. Obtain the required CODEOWNER approval through a pull request.
3. Record the exact subject fingerprint and `ruleDigest` emitted by the validator.
4. Set `reviewedAtRevision` to the full 40-character SHA containing the reviewed
   subject.
5. Set `reviewedBy` to the approving CODEOWNER principal and
   `approvalEvidence` to `github-pr-review:<URL-or-review-id>`.
6. Add the review record in a later commit and rerun strict validation.

Reachability and fingerprints prevent accidental reuse. CODEOWNERS plus protected
branches prevent an agent from accepting its own review. JSON alone is not proof
of human approval.

## Solo-maintainer review record workflow

1. Commit the reviewed subject and obtain its full SHA.
2. Run validation or `aak explain` and capture the fingerprint and `ruleDigest`.
3. The sole declared principal posts the durable GitHub attestation described
   above.
4. Generate a review template with `--write-review-template`, record the
   attestation URL, and keep `reviewedBy` equal to that sole principal.
5. Commit `reviews.json`, rerun strict validation, and let the required status
   check protect the merge.

The validator checks the evidence prefix and GitHub URL shape but does not query
GitHub. Platform permissions and the maintainer's operational separation from
the agent remain external controls.

A missing `ruleDigest` is rejected by the review contract. A valid but changed
digest prevents the acknowledgement from applying and produces
`REVIEW_REQUIRED`, even when its older finding fingerprint still appears to
match.

A review is checked for staleness only when its target rule is applicable. For
example, a `CHG001` review is retained without a stale-review finding during a
self-validation run that has no `--base-ref`; the comparative run remains
responsible for matching its exact fingerprint.

## Push checks

The workflow compares pull requests with their base SHA and pushes with
`github.event.before`. A direct push that changes policy will therefore produce
a failing check, but only branch protection prevents that mutation from landing
in the first place.
