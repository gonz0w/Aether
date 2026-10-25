# Native routed live stop — 2026-09-06

[Decision 0061](../../decisions/0061-native-routed-live-stop.md) and
[fresh consuming witness](witness/README.md).

Decision 0061 passes 51 native cases. Routed live stop preserves worker/reader/wait
and pending state, without fabricating Terminal or delivery acknowledgment. Native
terminal 144 supplies the event; accepted delivery gates complete cleanup, and
Cleaned delivery still leaves cancelled retry denied. Both launch-delivery orders
pass. Controls hit 1006/0 and 1007/0. All 177 frozen inputs unchanged; 35 of 48
prior clients match and changed clients pass prior oracles. BG-058 next qualifies
routed stop-error preservation of pending evidence and intent. BG-057 full journal
integration and BG-033 recovery remain open. No external control or POSIX signal
semantics are claimed.

No failed native attempt occurred. Three stopped workers account for final three
reclaims; all owned readers and waits are explicitly released.

## Validation — 2026-09-06

All 51 native cases pass, with all 177 frozen inputs unchanged. Thirty-five of 48
preceding clients match; thirteen changed clients pass their previous semantic
oracles, individually recorded in witness/comparison.json. New raw clients:
live-stop 2,544 bytes, stop-event 2,400 and stop-ack 624, within the 4 KiB bound.
No failed native attempts occurred.

All eight development gates pass in out/checks/run-4tp2khc2: 228 model tests,
23 negative controls, 48 host tests and 37 harness tests. Native catalog audits
591 outcomes across 28 bundles and 9,393 files. Development sources unchanged;
current native consumer bytes match the executed snapshot. git diff --check passes.
Only decision/planning validation notes were appended after checks; native source
unchanged. Retained evidence: docs/evidence/native-routed-live-stop-2026-09-06/.
