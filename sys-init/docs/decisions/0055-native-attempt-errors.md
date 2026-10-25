# 0055 — Native partial cleanup and stop-error retention

Accepted 2026-09-06, BG-058 bounded native error paths.

## Required behavior

Attempt cleanup may partially succeed. If closing the reader succeeds but worker
reclaim fails, retain the worker and any unprocessed wait, keep clean() false and
deny retry. The adapter's live-worker terminal precondition returns 0x20002/16
before invoking native reclaim. After separately requested stop and observed terminal
evidence, an explicit second cleanup may finish; no automatic retry is introduced.

Service cancellation sets cancelled intent before stop. A stop error returns its
exact operation/errno while preserving intent and the worker handle. A stale target
is not evidence that the attempt completed cleanup. Retain the unresolved record,
deny retry and do not issue more acquisition work. No reconciliation is invented.
The existing code already preserves these paths; add explicit consuming witnesses
and controlled omissions, without changing successful operation semantics.

## Witnesses

partial-cleanup: acquire/launch a live worker, wait for its historical-ready evidence
(the frozen helper writes its initial byte before readiness), register a wait, call cleanup and
require 0x20002/16. The reader is now absent, worker/wait remain owned, cancellation
has not been requested and retry is locally denied. Request service stop, observe
terminal 144, clean retained resources, then clean two normal workers to complete
result=100/reclaimed=3. This witnesses adapter precondition failure, not a kernel
reclaim syscall rejection. Clearing worker before the failed reclaim must trigger
assertion 990/reclaimed=0.

stop-error: first complete two normal workers. Launch/observe a third normal worker,
close its reader explicitly and reclaim it through the adapter outside Attempt.
This is a deliberate fixture ownership-loss probe: leave the old worker reference
in Attempt. Now cancel_service must return the actual kernel 0x20007/9 and retain
cancelled intent/worker, keep clean() false and reject retry locally. Perform no
further acquisitions. The adapter itself is clean because the probe explicitly
reclaimed the target, but the Attempt stays unresolved. result=100/reclaimed=3
means the error-retention assertions passed, never that this Attempt became clean.
Clearing intent/worker on the stop error must trigger assertion 991/reclaimed=3.

Both controls require the exact designated profile panic; timeout/generic failure
cannot satisfy them. The raw native forcing mechanism remains the existing adapter;
no forged handles or new unsafe primitive are added. This is trusted fixture work,
not safe out-of-band reclamation or a production recovery recipe.

Use pinned SI-04/Rust 1.98.0/4 KiB/BSP-only inputs, unchanged helper images and
existing offline runner. Run all 27 earlier cases plus four new cases, retain source/
artifact/log identities and binary comparisons, then full development checks.
Foundations O-01/O-04, I-03–06/E-01–08 and scoped partial-error review apply; preserve
Experience marker/stream contracts, shared releases/pins and native ABI.

Unresolved reader-close/wait-release failures, complete reconciliation and supervisor
recovery remain BG-058/BG-033. Timed restart and wider graph/control integration
remain separate. No full driver equivalence or POSIX process semantics are claimed.

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
