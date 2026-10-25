# Bounded concurrent native children — 2026-09-06

Opt-in `native-thread-pair` admits two owner-local child contexts. Default kernels
retain one child, and both modes retain four lifetime admissions. Exact-ID
inspection/retirement, all-child pinning, rotation, stop and reclaim are exercised.
The fixture runs two batches: selective wake first, then both children runnable,
with independent stack/TLS, FS/SIMD preservation and slot reuse.

## Qualified evidence

`final/results.json` records the frozen source identities, commands and outcomes.
All 255 target cases across 30 suites pass: 14 pair, 168 older thread, 25 memory,
nine image, seven M4 and 32 init cases. Host validation passes 59 Zig tests and
97 Python tests, offline standards/workflow and scoped formatting. The 26 existing
musl lifecycle producers were independently checked against the pinned upstream
source; this does not claim concurrent musl lifecycle support.

`target-attempts.tar.gz` retains all initial and final target directories with
binaries, build records and serial logs. `target-directories.json` indexes them.
`final/sources.tar.gz`, `before.tar.gz` and `implementation.diff` identify the change.
`consumer-source-review.tar.gz`, `libc-receipt.json`, `source-verification.json`
and the nested producer records retain the existing upstream/SDK provenance.
`contract.md` and `review.md` record requirements and scoped self-review.

## Retained failures

The first fixture lacked the required ELF TLS segment and was rejected at load.
The second used argc=1 instead of the launch contract's argc=2 and exited at
assertion 180. Both were fixed in the fixture. The first qualification attempt
misclassified the thread-only `--pair` option in the launch inventory; the host
checker rejected it. `failed-host/` retains that run. The corrected frozen run
passes. Disabled pair and bypassed pins intentionally fail at assertions 190 and
191; child UD2 produces the exact fault terminal while the peer completes.

## Limits and next work

This qualifies two raw native children, not concurrent musl pthreads, a thread
pool, multiple condition waiters, wake-one/requeue, cross-core migration or general
POSIX behavior. Independent reader/consumer review and full release acceptance
remain open. No sibling files, consumer pins or shared standards changed.
Next: an actual bounded concurrent musl pthread create/join fixture, followed by
needed multiple-waiter semantics for the filesystem-engine path.

Reproduction commands are in [NATIVE-C](../../NATIVE-C.md); exact commands and
pinned local input paths are in `final/results.json`. Post-run planning/reference
updates are retained separately; the qualified source archive stays unchanged.
