# Scoped self-review

The new operation validates current domain capability, pair profile, source and
destination shape, both writable words, counts and reserved input before touching
any wait. The owner runs with IF=0 across validation/commit. No user memory is
written and no new object is allocated. Wake helper first handles expiration and
bounded wake; moving changes only the remaining wait address. Started/deadline and
saved frame remain unchanged. Existing pending-wait pin logic follows the new key.
No cross-domain selection or fairness promise is added.

Host test covers wake-one plus move-one with another waiter left behind,
zero-count, preserved frame/start/deadline, original timeout and indefinite wake.
Target tests put two real children on a dedicated source mapping. Rejected calls
requesting a wake leave both parked. A move transfers pins: source protect works,
destination protect/unmap reject. Move-back-one keeps destination pinned until
the final waiter leaves. Supervisor stop begins with both moved waiters pending;
new generation completion and cleanup remain required by the existing harness.
The skip-move mutant must fail exactly at the destination-pin check (205).

Full older thread/musl, memory/image/M4/init suites selected for regressions. No
new dependency, upstream/libc adaptation, sibling edit or pin. This is self-review,
not independent reader or consumer acceptance. General futex semantics, actual
musl multiwaiter condition behavior and filesystem-engine composition remain open.
