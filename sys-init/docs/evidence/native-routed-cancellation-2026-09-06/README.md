# Native routed cancellation — 2026-09-06

[Decision 0060](../../decisions/0060-native-routed-cancellation.md) and
[fresh consuming witness](witness/README.md).

Decision 0060 passes 48 native cases. Cancellation before failure delivery, during
pending Cleaned and after cleanup transfer preserves intent and queued evidence.
Retirement eligibility never grants cancelled retry permission: pending cleanup
denies 0/16; completed delivery still denies retry/launch 0/13 with allowance unused.
Controls hit 1005/0 and 1004/0. All 177 frozen inputs unchanged; 32 of 45 prior
clients match and changed clients pass previous oracles. BG-058 next consumes
routed cancellation for a live admitted worker and observed terminal event;
routed stop errors, BG-057 journal/cut integration and BG-033 recovery remain open.
This is in-process rejected-route cancellation, not external control delivery.

No failed native attempt occurred. Three blockers account for final three reclaims;
rejected routes close their endpoints without retrying.

## Validation — 2026-09-06

All 48 native cases pass with 177 frozen inputs unchanged. Thirty-two of 45 prior
clients match; thirteen changed clients pass their previous semantic oracles,
individually recorded in witness/comparison.json. New raw clients are 992 bytes
(routed-cancellation), 544 (cancel-drop) and 608 (cancel-reset), within 4 KiB.
No failed native attempts occurred.

All eight development gates pass in out/checks/run-dnzy4kn8: 228 model tests,
23 negative controls, 48 host tests and 37 harness tests. Native catalog audits
540 outcomes across 27 bundles and 8,836 files. Development sources unchanged;
current native consumer bytes match the executed snapshot. git diff --check passes.
Only decision/planning validation notes were appended after checks; native source
unchanged. Retained evidence: docs/evidence/native-routed-cancellation-2026-09-06/.
