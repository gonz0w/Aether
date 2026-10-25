# 0063 — Routed partial cleanup and withheld Cleaned event

Accepted 2026-09-06, BG-058/BG-057. Qualify the route after partial cleanup, using
decision 0056's deliberately released wait reference. Preserve existing semantics:
propagate the error, retain unresolved resources and emit no Cleaned event.

## Fixture and required outcomes

Dispose two ordinary workers. Launch a third exit worker through the route, observe
terminal 18, register an Attempt-owned wait and deliver the routed Terminal event.
Fixture setup releases the wait directly through Adapter, leaving its reference
in Attempt. This trusted ownership-loss probe is not a runtime recovery procedure.

Route cleanup now closes the reader and reclaims the actual terminal worker, then
fails wait release with 0x25005/9 at the adapter ownership guard before a native
release call. Keep the wait reference, reader/worker absent, outcome-delivered=true,
pending=None, eligible=false. The existing inbox Terminal remains unchanged.
Attempt/route are unresolved even though deliberate setup leaves Adapter clean.
Repeated cleanup returns the same error without discarding the wait. Empty-inbox
delivery yields false and no fabricated Cleaned. Retry is locally denied with
0/16; no further acquisition occurs. Finish 100/reclaimed=3 only as fixture
accounting plus retention assertion success, never successful Attempt cleanup.

Controls: queue Cleaned on cleanup error while still returning Err -> exact
1012/reclaimed=3; discard wait on cleanup error -> exact 1013/reclaimed=3.
Require designated profile panic/context, not generic build failure or timeout.
Run all 54 prior cases plus these three with pinned SI-04/Rust 1.98.0/2024,
BSP-only and 4 KiB clients; retain inputs/artifacts/logs and comparisons, then all
repository checks. No dependency, allocation, unsafe primitive or shared ABI change.

Review partial effects, error origin, outcome acknowledgment versus resource
completion, repeated failure and withheld events. Foundations O-04/I-03–06/E-01–08
apply with unchanged pins, CLI contracts and smoke markers. This is local adapter
denial during native execution, not a kernel wait-release rejection or recovery.

BG-058/BG-057 next review accumulated native route evidence against the model driver
and prioritize the remaining integration gaps. Complete issued-operation identity,
journal/cut delivery, broader errors and BG-033 reconciliation/recovery remain open.

## Validation — 2026-09-06

All 57 native cases pass with 177 frozen inputs unchanged. Forty-one of 54 prior
clients match; thirteen changed clients pass their previous semantic oracles,
individually recorded in witness/comparison.json. New raw sizes: 2,288 bytes
(partial-cleanup), 1,664 (cleanup-event), 1,680 (cleanup-forget), within 4 KiB.
No failed native attempts occurred.

All eight development gates pass in out/checks/run-_zj1fvz8: 228 model tests,
23 negative controls, 48 host tests and 37 harness tests. Native catalog audits
702 outcomes across 30 bundles and 10,570 files. Development sources unchanged;
current native consumer bytes match the executed snapshot. git diff --check passes.
Only decision/planning validation notes were appended after checks; native source
unchanged. Retained evidence: docs/evidence/native-routed-partial-cleanup-2026-09-06/.
