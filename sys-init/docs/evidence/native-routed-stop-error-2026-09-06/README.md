# Native routed stop error — 2026-09-06

[Decision 0062](../../decisions/0062-native-routed-stop-error.md) and
[fresh consuming witness](witness/README.md).

Decision 0062 passes 54 native cases. Actual stale-target stop error preserves
exact errno, intent, unresolved worker and pending historical terminal evidence.
Its later transfer is not recovery: cleanup fails on native observation, queues
no Cleaned and keeps retry denied. Controls hit 1009/3 and 1010/3. All 177 frozen
inputs unchanged; 38 of 51 preceding clients match and changed clients pass
prior oracles. BG-058 next qualifies routed partial cleanup retaining remaining
resources without Cleaned. BG-057 journal identity and BG-033 recovery remain
open. Final fixture accounting does not establish successful Attempt cleanup.

No failed native attempt occurred. The adapter is clean only because fixture setup
disposed the target outside Attempt; the route remains unresolved at finish.

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
