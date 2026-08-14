# GitHub authority enforcement

The local validator can prove that authority is declared consistently, that a
review names an allowed CODEOWNERS principal, and that `reviewedAtRevision` is a
reachable ancestor commit. It cannot prove that GitHub actually recorded the
approval or enabled branch protection. Those are platform facts.

For repositories using the bundled GitHub authority model, configure every
branch named in `.agentic/policies/architecture/authorities.json` with:

- require a pull request before merging;
- require at least one approving review;
- require review from Code Owners;
- dismiss stale approvals when new commits are pushed;
- require the `Architecture conformance / validate` status check;
- prevent bypass and direct pushes, including for administrators unless the team
  has explicitly accepted that exception.

The principals in `authorities.json` must be valid users or teams in
`.github/CODEOWNERS`. Replace the bundled principal if the repository owner or
maintaining team differs.

## Review record workflow

1. Commit the subject that requires semantic review.
2. Obtain the required CODEOWNER approval through a pull request.
3. Record the exact subject fingerprint emitted by the validator.
4. Set `reviewedAtRevision` to the full 40-character SHA containing the reviewed
   subject.
5. Set `reviewedBy` to the approving CODEOWNER principal and
   `approvalEvidence` to `github-pr-review:<URL-or-review-id>`.
6. Add the review record in a later commit and rerun strict validation.

Reachability and fingerprints prevent accidental reuse. CODEOWNERS plus protected
branches prevent an agent from accepting its own review. JSON alone is not proof
of human approval.

## Push checks

The workflow compares pull requests with their base SHA and pushes with
`github.event.before`. A direct push that changes policy will therefore produce
a failing check, but only branch protection prevents that mutation from landing
in the first place.
