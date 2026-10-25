# Scoped self-review

Independent review and companion acceptance remain outstanding.

- Four condition translation units are unchanged upstream musl source. The
  signedness exception applies only to upstream condition/internal timedwait.
- Predicate changes occur under the normal mutex. Atomics observe attempted wait,
  wait calls and return; they do not replace the predicate lock.
- The parent can acquire the mutex released by condition wait. After signal or
  broadcast it retains that mutex until renewed contention is observed; the child
  cannot return from condition wait before actual reacquisition.
- Upstream stack-owned waiter remains in pinned live child backing. Successful
  join/reap precedes list/lock cleanup and quota checks, then the next lifecycle.
- Bypass must fail at exact 252. Each cycle allows eight initial mutex yields,
  four condition coordination yields and four relock yields; at most 64 total.
- Signal and broadcast each run twice per four-child fixture, with only one
  waiter. No multiple-waiter FUTEX_REQUEUE or wake-all evidence is claimed.
- Kernel and build identity reuse the previous native-pthread-reuse baseline for
  memory/image/M4; all thread families are freshly qualified. No ABI/pin/sibling
  changes, complete pthread compatibility or native filesystem claim follows.
