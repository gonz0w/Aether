# Bounded native requeue contract

Pair-only 0x2800d: RDI current domain thread capability, RSI source wait address,
RDX maximum wakes, R10 maximum requeues, R8 destination address, R9 zero. Both
addresses must be distinct nonzero aligned writable u32 mappings even for zero
counts. Both counts 0..INT_MAX. Capability -13; off-pair -38 after capability;
address shape/same-address/count/reserved -22; invalid mapping -14. All validation
precedes mutation. Any context holding the current domain grant may call.

Under existing IF=0 owner execution, expire old waits first, wake at most RDX on
source, then move at most R10 remaining source registrations to destination.
Return number woken plus moved. No comparison or write of user words, queue
allocation, FIFO/fairness promise or cross-domain access. Deterministic context
scan only. Moving preserves start/deadline and saved frame; destination is pinned
by the existing pending-wait mapping rule, source loses that pin after last move.
Stop cancels moved waits before reclaim. Existing wake/park APIs remain unchanged.

Host coverage: mixed wake/move, bounded counts, unmatched registrations, preserved
deadline/start/frame and timeout at original deadline. Target: two actual children,
invalid destination with wake requested changes nothing, zero-count no-op, source
and destination pins, move there/back, same-address rejection, stopped requeued
children and fresh replacement. Skip-move mutant must fail destination-pin check.
Full older thread/memory/image/M4/init regressions on frozen sources; retain every
attempt. Document API, workflow, STATE. No new dependency, libc adaptation,
sibling or pin. Requeue primitive alone is not musl multiwaiter acceptance.
