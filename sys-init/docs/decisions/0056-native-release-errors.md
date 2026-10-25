# 0056 — Native reader-close and wait-release error retention

Accepted 2026-09-06, BG-058. Preserve the existing success-only removal of owned
resources. No new runtime ABI, dependency or unsafe primitive is needed.

## Required behavior and consuming cases

A failed reader close must preserve its reader reference and stop cleanup before
worker reclaim or wait release. A failed wait release must preserve the wait even
when reader close and worker reclaim already succeeded. Neither failure proves
Attempt clean or permits retry. Exact operation/errno must survive propagation.

Reader-error fixture: complete two ordinary workers, then launch/observe a third
terminal worker and register its wait. Close the reader through Adapter outside
Attempt, deliberately leaving the stale reference in Attempt. cleanup must return
actual kernel 0x24003/13, retain reader/worker/wait, remain unclean and deny retry
locally with 0/16. The adapter must still own worker/wait. Only after assertions,
fixture teardown reclaims/releases them outside Attempt; the Attempt remains
unresolved. No further acquisition occurs. A control forgetting reader on close
error must reach exact assertion 992/reclaimed=2.

Wait-error fixture: complete two ordinary workers, then launch/observe a third
and register its wait. Release that wait through Adapter outside Attempt, leaving
its stale reference in Attempt. cleanup closes reader and reclaims worker, then
fails the adapter's ownership guard with 0x25005/9 before native release. Retain
wait, remain unclean and deny retry with 0/16; repeated explicit release preserves
the same error and reference. The adapter is clean, the Attempt unresolved. A
control forgetting wait on release error must hit assertion 993/reclaimed=3.
This tests local adapter denial, not a kernel wait-release syscall rejection.

Both positives finish 100/3 only after retention assertions and actual fixture
resource cleanup. Neither means reconciliation or successful Attempt cleanup.
Out-of-band disposal is deliberate trusted test setup/teardown, not a runtime
recovery algorithm. No acquisitions after either error. Negative cases require
exact designated profile panic/context, never timeout or generic build failure.

Run all 31 prior cases plus these four on unchanged pinned SI-04 inputs, Rust
1.98.0/2024, BSP-only and the 4 KiB client bound. Preserve source/artifact/log
identities and prior-client comparisons, then run all development checks.
Foundations O-04, I-03–06 and E-01–08 apply; marker/stream and shared pins stay
unchanged. Review partial effects, ownership, exact error origin and fixture
teardown separately. This is bounded native evidence, not POSIX conformance.

BG-058 retains complete driver composition and native wait-release syscall-error
coverage if a real consumer needs that distinction. BG-033 retains unknown-effect
reconciliation and supervisor recovery. Timed restart and wider control remain open.

## Initial oracle correction

The first run failed reader-error at 992/2: the test expected EBADF for stale
endpoint authority. The pinned producer NATIVE-CHANNEL.md and native_channel.zig
specify EACCES (13). Corrected expected operation/errno to 0x24003/13 without
changing producer behavior. Retained failed source, artifacts and logs under
native-release-errors-2026-09-06/attempts/reader-errno; fresh acceptance required.

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
