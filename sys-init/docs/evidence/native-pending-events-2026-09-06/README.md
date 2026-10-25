# Native pending events — 2026-09-06

[Decision 0057](../../decisions/0057-native-pending-events.md) and
[fresh consuming witness](witness/README.md).

Decision 0057 passes 38 native cases. Admitted launch, terminal observation and
complete cleanup produce generation-tagged pending events. Full inbox retains
ownership; terminal supersedes undelivered launch; cleanup requires terminal
delivery; retirement eligibility waits for Cleaned delivery. Controls hit exact
994/0 and 995/0. This is a bounded in-process inbox, not journal execution or
complete lifecycle policy. All 177 frozen inputs are unchanged; 27 of 35 prior
clients match and changed clients pass prior oracles. Initial passing run before
explicit terminal-delivery guard is retained; final strengthened run passes.
BG-058 next routes known launch rejections and cleanup notifications; BG-057
retains full journal/cut integration and BG-033 unknown recovery.

Both initial and final native runs passed. Source review strengthened the guard
before final acceptance; initial evidence is retained under attempts/.

## Validation — 2026-09-06

All 38 final native cases pass; all 177 frozen inputs unchanged. Twenty-seven of
35 preceding clients are byte-identical. Eight changed Attempt clients pass their
previous semantic oracles; witness/comparison.json identifies each. New clients:
native-events 2,376 bytes, event-drop-busy 384, event-keep-launch 2,344, all under
4 KiB. Both initial and final native runs passed. Source review added explicit
terminal-delivery acknowledgment and the Launched-only denial probe before final
acceptance; the initial run remains separately retained.

All eight development gates pass in out/checks/run-3gt845lb: 228 model tests,
23 negative controls, 48 host tests and 37 harness tests. Native catalog audits
406 outcomes across 24 bundles and 7,298 files. Development sources unchanged;
current native consumer bytes match the executed snapshot. git diff --check passes.
Only decision/planning validation notes were appended after checks; no native
source changed. Retained evidence: docs/evidence/native-pending-events-2026-09-06/.
