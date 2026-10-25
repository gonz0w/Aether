# Bounded native requeue — 2026-09-06

Pair-only 0x2800d validates a domain grant, two distinct writable wait addresses,
wake/requeue limits and reserved input before mutation. It wakes at most the first
limit, then moves at most the second limit of remaining source registrations.
Moving preserves start time, deadline and saved frame; pending-wait mapping
protection follows the destination. No user word is changed or queue allocated.

## Qualification

`final/results.json` records frozen sources and passing commands. All 269 target
cases across 30 suites pass: 20 pair, 176 older thread (including 44 musl lifecycle),
25 memory, nine image, seven M4 and 32 init. Zig host tests, 97 Python tests,
standards/workflow and scoped formatting pass. All 28 lifecycle producers were
verified against pinned upstream source and existing adaptations.

The host test covers mixed wake/move limits, preserved frame/start/deadline and
timeout on the original deadline. Target tests park two actual children on a
dedicated source page; invalid calls requesting a wake leave them parked. After
moving both, the source can be protected while destination protect/unmap reject.
Moving one back keeps destination pinned until the final waiter leaves. Supervisor
stop/reclaim with moved waiters must reach fresh replacement completion. The
skip-move mutant fails at assertion205. Initial and frozen final attempts pass;
all are retained.

`target-attempts.tar.gz` contains binaries, build/producer records and serial logs;
`target-directories.json` indexes it. `final/sources.tar.gz`, `before.tar.gz`,
`implementation.diff`, `contract.md` and `review.md` retain implementation and
self-review. Upstream archive, SDK receipt and source verification are included.
Reproduce with the existing `scripts/thread_smoke.py --pair` / `--pair --large`
commands and pinned SDK/tool-lock arguments in [NATIVE-C](../../NATIVE-C.md).
Exact full regression commands are in `final/results.json`.

## Boundaries

The operation is owner-local, bounded and deterministic, without FIFO/fairness
or general futex claims. Existing park/wake operations and libc adapter are
unchanged. No dependency, upstream patch, sibling, release or consumer pin changed.
Independent review/consumer adoption remains open. Next: actual multiple musl
condition waiters using the bounded wake/requeue primitives. Requeue alone is not
filesystem-engine acceptance or release readiness.
