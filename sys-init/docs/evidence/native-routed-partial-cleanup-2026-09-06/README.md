# Native routed partial cleanup — 2026-09-06

[Decision 0063](../../decisions/0063-native-routed-partial-cleanup.md) and
[fresh consuming witness](witness/README.md).

Decision 0063 passes 57 native cases. Reader close and worker reclaim precede a
wait-release ownership denial; the route retains unresolved wait, emits no Cleaned
and denies retry. Repeated failure preserves the same state. Controls hit 1012/3
and 1013/3. All 177 frozen inputs unchanged; 41 of 54 preceding clients match
and changed clients pass prior oracles. Deliberate fixture wait disposal leaves
Adapter clean but never qualifies route cleanup/recovery. BG-058/BG-057 next
review accumulated native evidence against model driver integration gaps;
complete operation identity, journal/cut delivery and BG-033 recovery remain open.

No failed native attempt occurred. The adapter is clean due to deliberate fixture
wait disposal; the route still owns an unresolved reference at finish.

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
