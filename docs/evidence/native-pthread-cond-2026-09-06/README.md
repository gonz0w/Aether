# Actual bounded pthread condition waits — 2026-09-06

Four unchanged musl 1.2.6 condition translation units now link into the native
conformance adapter: wait, timedwait implementation, signal and broadcast. The
qualified calls are process-private untimed waits with one waiter and a normal
mutex. Existing capability-scoped compare/wait/wake supplies native transport;
no kernel, ABI or production userland change is made.

Each fixture runs four actual 256 KiB pthread lifecycles. After the existing mutex
contention test, the child waits in a protected predicate loop. The parent observes
a condition wait call, acquires the released mutex, updates the predicate and
signals on even cycles or broadcasts on odd cycles. It keeps the mutex locked
until renewed child mutex contention is observed, proving that signalling alone
does not let the condition wait return. Unlock then allows reacquisition and
completion. Join/reap must leave no condition list/lock state or lost backing.
The fixture bypassing condition wait must fail exactly at assertion 252.

## Qualification

The preimplementation contract is retained in contract.md and docs/NATIVE-C.md.
Final results bind exact commands, UTC boundaries and source hashes. Sources are
frozen in final/sources.tar.gz and checked before/after each command and archival.
All 168 selected target cases pass: eighteen lifecycle cases per memory profile
and 132 older thread-family cases. Host checks pass 97 Python tests, Zig tests,
offline standards/workflow and pinned C/Zig formatting.

Both profiles include direct condition use, supervised replacement and the
semantic bypass rejection, plus all older lifecycle cases. Signal and broadcast
each run twice per four-child fixture. Each uses only one waiter: multiple-waiter
requeue, wake-all ordering and fairness are not qualified. Parent coordination
preserves the existing exact 64-yield protocol. Kernel/build hashes match the
native-pthread-reuse qualification; its 25 memory, 9 image and 7 M4 passes are
reused by identity, not rerun or counted as fresh cases here.

## Retention and limits

The initial compile failed on upstream pthread_cond_timedwait.c's signed/unsigned
nanosecond comparison under -Werror. A source-specific -Wno-sign-compare exception,
already used for internal timedwait, leaves upstream bytes and first-party warning
policy unchanged. The failed compile, corrected initial eighteen-case pass and
final runs are retained in 24 target directories (22 final). Source verification
covers 26 lifecycle producers, original/adapted manifests, upstream object hashes
and the existing admission patch. The four condition sources compare unchanged
against the verified archive. Disassembly, before snapshot, implementation diff
and SHA256SUMS are retained.

No timed waits, cancellation, process-shared condition variables, concurrent child
pool or complete POSIX support is claimed. The condition waiter is stack-owned
upstream state in pinned live child backing; the predicate is mutex-protected.
No sibling or immutable pin changed. Independent review, companion adoption and
optimized/stress/hardware coverage remain outstanding. Next: bounded concurrent
thread resources and multi-waiter semantics required by libzpool. The native
filesystem and assembled serial shell/package release remain unfinished.
