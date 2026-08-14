# Architecture validator module

## Purpose

Own portable rule evaluation, repository observation adapters, contract loading,
deterministic result construction, and progressive context retrieval. The
top-level `validate.py` and `context.py` files are CLI adapters and remain thin.

## Start here

- Read `module.contract.yml`.
- Read `../rules.json` before adding or changing an evaluator.
- Keep technology-specific discovery under `adapters/`.

## Local rules

- Portable evaluators must not contain product-specific module names or paths.
- Observed facts include their source and confidence when exact proof is not possible.
- A waiver produces `WAIVED`, never `PASS`.
- Semantic acceptance is bound to the finding fingerprint and produces `REVIEWED`.
