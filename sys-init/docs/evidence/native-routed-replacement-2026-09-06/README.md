# Native routed replacement — 2026-09-06

[Decision 0059](../../decisions/0059-native-routed-replacement.md) and
[fresh consuming witness](witness/README.md).

Decision 0059 passes 45 native cases. Pending Cleaned blocks replacement before
channel acquisition. Accepted delivery permits one generation-two route with fresh
endpoints/worker and reset pending/delivery state. Old inbox contents preserve new
launch backpressure; all replacement events carry two. Duplicate original retry is denied; generation-two budget remains the existing
Attempt rule. Controls hit 1001/0 and 1002/1. All 177 frozen
inputs unchanged; 31 of 41 preceding clients match and changed clients pass
prior oracles. BG-058 next integrates cancellation intent with the routed gate;
BG-057 journal/cut identity and BG-033 unknown recovery remain open. This is
explicit bounded retry, not timed restart or full native driver conformance.

Initial page-bound failure and all size probes are retained under attempts/. Blocker, replacement and one separate worker
account for final three reclaims; the rejected attempt closes endpoints only.

## Validation — 2026-09-06

Final 45-case native run passes with all 177 frozen inputs unchanged. Thirty-one
of 41 preceding clients match; ten changed clients pass their previous oracles,
identified individually in witness/comparison.json. Final runner raw sizes are
3,576 bytes (routed-replacement), 4,008 (replacement-events), 1,280 (skip-delivery)
and 4,024 (old-generation), all within the unchanged 4 KiB bound. These are the
accepted artifacts, distinct from earlier standalone size-probe outputs.
Initial link-bound failure and all failed/passing size probes remain retained.

All eight development gates pass in out/checks/run-ab0s5vrb: 228 model tests,
23 negative controls, 48 host tests and 37 harness tests. Native catalog audits
492 outcomes across 26 bundles and 8,300 files. Development sources unchanged;
current native consumer bytes match the executed snapshot. git diff --check passes.
Only decision/planning validation notes were appended after checks; native source
unchanged. Retained evidence: docs/evidence/native-routed-replacement-2026-09-06/.
