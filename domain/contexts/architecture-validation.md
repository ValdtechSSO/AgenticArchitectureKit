# Architecture validation

## Purpose

The validator compares declared architecture with repository observations and
emits evidence-bearing results suitable for local use and CI.
It also builds revision-tagged indices and retrieves starting paths, references,
tests, and direct impact without erasing provenance or confidence.

## Invariants

- Portable rules never encode the module names or approved dependencies of one product.
- Waivers never turn a violation into a pass.
- Semantic reviews are valid only for the exact subject fingerprint they accepted.
- Every result identifies the digests of policy, waivers, reviews, catalog, and observation.
- A change that expands architecture policy relative to a supplied base requires a recorded decision.
- Required semantic evidence is content-fingerprinted, complete, non-truncated,
  and read-only; observation never grants architecture permission.
- Long-running execution checkpoints retain the original plan identity, global
  objective, active invariants, cumulative decisions and deviations, test
  evidence, risks, and next objective; continuation requires a content-bound
  resume receipt.
