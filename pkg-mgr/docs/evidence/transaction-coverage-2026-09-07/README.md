# Transaction coverage mapping

2026-09-07 UTC. ADP04-02 documentation-only continuation: ten existing transaction
case groups bring the inventory to 37. No runtime, fixture, pin or sibling changes.

Oracle: every new anchor resolves exactly once, descriptions match surrounding
assertions, and the prior passing full-suite inputs remain identical in all runtime,
recipe, fixture and test trees. Missing/ambiguous anchors or upgraded evidence claims
are forbidden. Selected fresh checks: development/inventory, coverage-checker
positive and ten negative controls, all pinned standards and whitespace.

The prior runner-handoff attempt-02 suite passed under its 600-second watchdog.
This review reuses that execution only after comparing complete input names, bytes,
modes and sizes in bin, mk, recipes, fixtures, manifests and tests. source-match.json
records that comparison and hashes the original suite result/log. The original
manifest retains exact dirty Origins inputs; no current HEAD-only identity is claimed.
No additional full-suite run or new target qualification is asserted here.

## Findings that remain open

- The stale-plan fixture checks nonzero rejection, retained changed payload and no
  displacement. It does not assert the exact failure diagnostic or compare a full
  target snapshot after each rejection. Its mapping states this narrower oracle.
- Publication interruption checks successful idempotent retries and retained old
  bytes, but the initial reject helper accepts any nonzero status. Exact signal
  status needs a focused assertion before claiming the intended interruption cause.
- These groups cover existing host faults, not all parser fields, concurrent writers,
  real disk exhaustion, power loss or native package persistence. Mapped locations
  are not executed case counts or an independent reviewer approval.

The next bounded task is to strengthen those two rejection oracles with semantic
controls and fresh transaction execution. Prior failed evidence and release pins
remain unchanged. checks.json records this update's actual validation.
