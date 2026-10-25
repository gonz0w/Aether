# Native reader and wait release errors — 2026-09-06

[Decision 0056](../../decisions/0056-native-release-errors.md) and
[fresh consuming witness](witness/README.md).

Decision 0056 passes 35 native cases. Reader-close error retains reader/worker/wait
and stops cleanup; wait-release error retains wait after other cleanup succeeds.
Retry remains denied. Exact controls hit 992/2 and 993/3. Reader error is kernel
EACCES; wait release is adapter ownership denial. Both Attempt records remain
unresolved despite deliberate fixture disposal/teardown. All 177 frozen inputs
remain unchanged; 25 of 31 preceding raw clients match and changed clients pass
prior oracles. Initial wrong reader errno expectation is retained separately.
BG-058 next defines native effect-to-event routing with retained pending events;
complete driver composition and BG-033 recovery remain open.

The failed initial errno oracle is retained in attempts/reader-errno/.
No producer behavior was changed to satisfy the fixture.

## Validation — 2026-09-06

Fresh final run passes all 35 native cases; 177 frozen inputs unchanged. Twenty-five
of 31 earlier raw binaries match. Changed attempt-retry, attempt-bad-writer,
attempt-intent, attempt-bad-intent, attempt-partial-cleanup and attempt-partial-forget
pass their previous oracles. New client sizes: reader-error 3,064, reader-forget
3,080, release-error 2,560 and release-forget 2,592 bytes, within the 4 KiB bound.
The initial wrong reader errno oracle and all its logs/artifacts are retained.

All eight development gates pass in out/checks/run-ards_yc7: 228 model tests,
23 negative controls, 48 host tests and 37 harness tests. The native catalog audits
368 outcomes across 23 bundles and 6,832 files. Development sources are unchanged;
current native consumer bytes match the executed snapshot. git diff --check passes.
Only decision/planning validation notes were appended after checks. No native code
changed. Complete evidence: docs/evidence/native-release-errors-2026-09-06/README.md.
