# Native rejected-launch events — 2026-09-06

[Decision 0058](../../decisions/0058-native-rejected-events.md) and
[fresh consuming witness](witness/README.md).

Decision 0058 passes 41 native cases. Received native busy launch queues its exact
error and generation in LaunchFailed, retaining both endpoints. Failure delivery
precedes cleanup; Cleaned survives full inbox until acceptance. Duplicate launch
is local denial without another event. Controls hit 997/0 and 998/0. This is the
selected 0x23001/16 path and in-process inbox, not general error/recovery support.
All 177 frozen inputs unchanged; 28 of 38 preceding clients match and changed
clients pass previous oracles. BG-058 next gates routed replacement on accepted
Cleaned delivery with fresh generation events; BG-057 full journal/cut integration
and BG-033 unknown recovery remain open.

No failed native attempt occurred. The rejected attempt performs endpoint cleanup
only; blocker and two separate ordinary workers account for final three reclaims.

## Validation — 2026-09-06

All 41 native cases pass with 177 frozen inputs unchanged. Twenty-eight of 38
preceding clients are byte-identical; ten changed clients pass their previous
semantic oracles, individually recorded in witness/comparison.json. New clients:
rejected-events 2,512 bytes, event-wrong-error 544, event-failure-early 2,464,
all within 4 KiB. No failed native attempts occurred.

All eight development gates pass in out/checks/run-12xq_vzo: 228 model tests,
23 negative controls, 48 host tests and 37 harness tests. Native catalog audits
447 outcomes across 25 bundles and 7,785 files. Development sources unchanged;
current native consumer bytes match the executed snapshot. git diff --check passes.
Only decision/planning validation notes were appended after checks; no native
code changed. Retained evidence: docs/evidence/native-rejected-events-2026-09-06/.
