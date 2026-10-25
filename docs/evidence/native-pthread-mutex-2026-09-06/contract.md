
## Actual bounded pthread mutex contract — 2026-09-06

Before implementation: exercise upstream musl normal process-private mutex
lock/trylock/unlock through the existing capability-scoped wait/wake adapter.
Rebuild the four relevant upstream mutex translation units from the verified
musl 1.2.6 archive; preserve upstream bytes and existing admission patch. Kernel
and native ABI remain unchanged. This is kernel conformance evidence; production
POSIX adapter adoption stays with userland and libzpool integration remains pending.

In each of four actual pthread lifecycles, the parent holds a normal mutex while
the child attempts entry. Observe a real wait on that mutex word, reject successful
trylock while held, and prove the child has not entered. Unlock must wake the child;
it then updates protected data and unlocks before join/reap. Verify final state,
no residual waiters, full memory quota, and reuse of the same mutex across cycles.
A fixture that skips child lock must fail specifically at assertion 242, not via
a timeout. Both backing profiles and supervised replacement must pass. Preserve
older lifecycle cases and thread regressions on frozen sources; run host/standards,
workflow and pinned C formatting. Retain failed attempts and source/object identity.

No new allocations, kernel state or authority: mutex storage belongs to its domain;
wait pins and child backing retain existing teardown rules. Atomic observation
coordinates the test; it must not substitute for the protected update. This does
not qualify robust/PI/process-shared/timed mutexes, cancellation, condition variables,
multiple children, fairness, optimized/stress/hardware or all scheduling races.
