# 0062 — Routed stop-error preservation

Accepted 2026-09-06, BG-058/BG-057. Qualify the existing route's delegated failure
behavior using decision 0055's deliberate stale-target ownership-loss fixture.
No new success behavior, ABI, dependency, allocation or unsafe primitive.

## Contract and fixture

A received native stop error must remain its exact operation/errno. Keep cancelled
intent, the unresolved worker reference, the pending event and its undelivered
status. Do not replace prior terminal evidence with stop completion, clear it, or
report successful stop. Repeated failed stop must preserve the same facts.

First dispose two ordinary workers. Launch a third exit worker through the route,
observe terminal 18 and retain its generation-one Terminal event. Explicit fixture
setup closes its reader through Adapter and clears the reader field, then reclaims
the worker outside Attempt while retaining its worker reference. This is deliberate
ownership loss, not a supported runtime reclamation path. The adapter is actually
clean; the route is unresolved and remains so throughout the case.

Cancel twice through route: actual kernel 0x20007/9, cancelled=true, same worker and
pending Terminal(18), outcome_delivered=false. Cleanup and retry are locally denied
with 0/16 while pending. Deliver the previously observed historical Terminal;
this is valid retained evidence, not reconciliation. Explicit cleanup then fails
on Adapter::reclaim's native observe with 0x25001/9 before reclaim itself. Keep
worker, no Cleaned event, no eligibility and no retry acquisition. Final 100/3 means
retention assertions passed and fixture resources were disposed, not that Attempt
cleanup or recovery succeeded. No acquisitions occur after the stop error.

Controls: discard the pending event on stop error -> exact 1009/reclaimed=3;
convert native stop failure into Ok -> exact 1010/reclaimed=3. Require designated
profile context; generic panic/timeout/build failure cannot pass. Run all 51 prior
cases plus three new ones on pinned SI-04, Rust 1.98.0/2024, BSP-only and 4 KiB
clients; retain source/artifact/log identities and comparisons, then full checks.

Review exact error origins (stop versus observation during reclaim), partial
ownership, retained historical facts and ineligible unresolved state. Foundations
O-04/I-03–06/E-01–08 apply; shared pins and machine/CLI contracts unchanged.
No external control, unknown reconciliation or full native driver claim.

BG-058 next qualifies routed partial cleanup: failure must preserve remaining
resources and never queue Cleaned. BG-057 journal/cut identity and BG-033 unknown
reconciliation/recovery remain open.

## Validation — 2026-09-06

All 54 native cases pass, with all 177 frozen inputs unchanged. Thirty-eight of
51 prior clients match; thirteen changed clients pass their previous semantic
oracles, individually recorded in witness/comparison.json. New raw sizes are
2,784 bytes (stop-error), 1,264 (error-drop) and 1,248 (error-swallow), within 4 KiB.
No failed native attempts occurred.

All eight development gates pass in out/checks/run-y03cibpd: 228 model tests,
23 negative controls, 48 host tests and 37 harness tests. Native catalog audits
645 outcomes across 29 bundles and 9,971 files. Development sources unchanged;
current native consumer bytes match the executed snapshot. git diff --check passes.
Only decision/planning validation notes were appended after checks; native source
unchanged. Retained evidence: docs/evidence/native-routed-stop-error-2026-09-06/.
