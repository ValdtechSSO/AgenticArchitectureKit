# ADR-001: Portable validator boundary

## Status

Accepted.

## Decision

The kit contains one functional validation module and thin command-line hosts.
Technology-specific repository observation belongs to adapters inside that
module. Portable rules, project policy, waivers, and semantic review records are
separate inputs. A new module, host, project, or dependency permission requires
a reference to an accepted architecture decision when compared with a Git base.

## Authority

The maintainers of Agentic Architecture Kit own this boundary and may accept
semantic review records for it. An accepted review records its exact finding
fingerprint and must be renewed when that subject changes.

## Consequences

The kit can validate itself using the same public contracts it distributes.
Additional technology adapters extend observation without changing portable rule
meaning. A second assembly or package is introduced only when it creates a useful,
enforceable boundary.
