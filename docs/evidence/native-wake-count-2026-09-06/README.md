# Bounded native wake count — 2026-09-06

Pair-only operation 0x2800c wakes at most the supplied count of current-domain
registrations. It validates capability, writable aligned address, count and
reserved inputs before mutation. Zero wakes none; expired waits complete with
timeout without consuming the wake count. Existing wake-all and clear-TID retain
their behavior. No requeue or libc adapter adoption is included.

## Qualification

`final/results.json` records frozen inputs and all passing commands. The 265
target cases across 30 suites include 16 pair, 176 older thread (including the
44 musl lifecycle cases), 25 memory, nine image, seven M4 and 32 init cases.
Zig host tests, 97 Python tests, standards/workflow and scoped formatting pass.
The new host test checks zero/one/all counts, unmatched registrations and timeout
precedence. All 28 lifecycle producers were verified against pinned musl sources
and the unchanged documented two-file adaptation.

Two real children park on one word. Invalid calls and count0 leave both parked;
count1 wakes exactly one, a second wake releases the other and an empty wake
returns0. The unlimited-wake mutant must fail at assertion201. Existing pair
retirement/reuse, fault, parent-exit and supervisor cases remain. Initial target
and host attempts and the final run pass; no failed development attempt occurred.

`target-attempts.tar.gz` retains initial/final binaries, logs and producer records;
`target-directories.json` indexes them. `final/sources.tar.gz`, `before.tar.gz`,
`implementation.diff`, `contract.md` and `review.md` retain source and self-review.
Upstream archive, SDK receipt and source-verification records are included.
Reproduce with the existing `scripts/thread_smoke.py --pair` and `--pair --large`
commands and pinned SDK/tool-lock arguments in [NATIVE-C](../../NATIVE-C.md).
All exact regression commands are in `final/results.json`.

## Scope

Owner-local fixed-context scan; deterministic order without FIFO/fairness promise.
No new queues, grants, wait slots, dependency, sibling edits or pin changes.
Independent review and consumer acceptance remain open. The libc adapter still
uses its previous wake translation. Next: bounded requeue with destination pinning,
then actual multiple musl condition waiters. This is not full futex conformance,
filesystem-engine acceptance or release readiness.
