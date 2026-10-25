# Native partial cleanup and stop-error retention — 2026-09-06

[Decision 0055](../../decisions/0055-native-attempt-errors.md) has a
[fresh 31-case witness](witness/README.md).

Decision 0055 passes 31 native cases. Partial cleanup retains worker/wait after
reader close and adapter reclaim-precondition failure; explicit stop/observation
allows completion. Actual stale-target stop error preserves cancelled intent and
an unresolved Attempt, denying retry. Controls hit exact 990/0 and 991/3 assertions.
All 177 inputs are unchanged; 23 preceding binaries match and four changed Attempt
clients pass their previous oracles. An initial passing run is retained; review
added a readiness wait before deliberate reader close and the final rerun passes.
BG-058 next covers reader-close and wait-release failure retention; BG-033 recovery,
timed restart and wider graph/control integration remain open.

The stop-error fixture remains unresolved at Attempt level; adapter cleanup in
fixture setup is not reconciliation. Both initial and final native runs passed.
The initial run is retained under attempts/before-readiness/.

## Validation — 2026-09-06

Final native witness: 31/31 cases pass, 177 frozen inputs unchanged. Twenty-three
of 27 preceding raw binaries match; attempt-retry, attempt-bad-writer,
attempt-intent and attempt-bad-intent changed and pass their existing oracles.
New raw sizes are 2,800/2,816 bytes (partial cleanup/control) and 1,216/1,152 bytes
(stop error/control). The initial passing run is retained; source review added
readiness ordering before deliberate reader close, then all 31 cases reran.

All eight gates pass in out/checks/run-39a0a6jr: 228 model tests, 23 negative
controls, 48 host tests and 37 harness tests. Native catalog audits 333 outcomes
across 22 bundles and 6,387 files. Development sources remain unchanged; native
consumer files match the executed snapshot. git diff --check passes. Decision
and planning validation notes were appended after checks; no native code changed.
Evidence: docs/evidence/native-attempt-errors-2026-09-06/README.md.
