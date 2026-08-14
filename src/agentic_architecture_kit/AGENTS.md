# Agentic Architecture Kit module

## Purpose

Own the installable portable distribution: rule evaluation, repository
observation adapters, bundled schemas/catalog/templates, bootstrap, deterministic
results, and progressive context retrieval. `tools/aak.py` is the repository's
thin dogfooding host; installed users invoke the `aak` console entrypoint.

## Start here

- Read `module.contract.yml`.
- Read `data/rules.json` before adding or changing an evaluator.
- Keep technology-specific discovery under `adapters/`.

## Local rules

- Portable evaluators must not contain product-specific module names or paths.
- Observed facts include their source and confidence when exact proof is not possible.
- A waiver produces `WAIVED`, never `PASS`.
- Semantic acceptance is bound to the finding fingerprint and produces `REVIEWED`.
