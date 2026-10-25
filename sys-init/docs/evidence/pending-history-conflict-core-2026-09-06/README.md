# Pending-history conflict core — 2026-09-06

Decision 0086 qualifies the pure pending-history conflict core on the host.
An independently qualified equal sample is Duplicate without replacing the first.
A different qualified sample retains both immutable views and closes the local
store. Wrong request identity denies before invoking the synthetic producer;
produced-view identity is rechecked. Once closed, even an equal offer cannot
invoke the producer or replace retained history. No native read or effect exists
in this core.

Nine named view/conflict tests and nine existing sample tests pass. Four new
omission controls fail their exact assertions for replacing the first history,
skipping closure, producing after closure and ignoring content. The three previous
controls still pass. An initially invalid synthetic fault pair was rejected before
its intended assertion and is retained as failed evidence; corrected tests include
equal-result normal/fault and normal/stop collisions.

All 151 current native configurations rebuild byte-identically to decision 0085,
with unchanged tools/profile and maximum 4096-byte image. The native call sites
are unchanged and the new core is not consumed by them; this is build equivalence,
not native conflict execution. The previous 151-case target witness remains the
runtime checkpoint. Ten consumer sources are unchanged; pending_history.rs has
only the new unconsumed core appended.

Next BG-058: a private guard that owns the exclusive Driver borrow and both sample
storage associations, propagates Conflict to Driver.closed and prevents views
escaping. Reserve the diagnostic slot before synthetic production; qualify both
histories, resources, pending state and generation in a fresh native witness.
This host core's one-diagnostic-view bound does not establish the full physical
nine-triple allocation or storage after guard destruction. PH-05/06 capacity and
sealing, BG-057 PH-07 retirement, full launch composition, additional O1 injections
and BG-033 recovery remain open. No new kernel blocker is identified.

`host-attempt-1/` preserves the rejected fixture and semantic-control failures;
`host/` retains corrected source snapshots, compiler identity and exact commands.
`native-build-comparison/` retains all 151 builds, source comparisons, tools and
raw images. It records build equivalence only; no new QEMU run or native coverage
bundle is registered. Validation and adoption snapshots follow; the root manifest
seals every retained file except itself. Historical witnesses remain unchanged.

Validation: all nine development gates pass in `out/checks/run-o0vylm5y`,
with no skipped gates and unchanged checked sources. The nine wrapper cases
exercise nine sample tests, nine view/conflict tests and seven exact omission
controls. Native audit remains 2209 historical outcomes across 45 bundles; no new
native execution is added. All 151 rebuilt native clients match decision 0085
byte-for-byte, with unchanged tools and a 4096-byte maximum. Exact validation,
source/adoption snapshots and failed-fixture evidence are retained and sealed.
