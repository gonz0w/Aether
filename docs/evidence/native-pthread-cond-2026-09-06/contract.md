
## Actual bounded pthread condition contract — 2026-09-06

Before implementation: rebuild unchanged musl 1.2.6 condition wait, timedwait
implementation, signal and broadcast sources through the existing private syscall
adapter. Test process-private untimed condition waits with one waiter and a normal
mutex, across four child lifecycles and supervised replacement in both memory
profiles. No kernel/ABI or production userland change is required or claimed.

The child first passes the existing mutex contention check, then waits in a
predicate loop under that mutex. Observe a wait call while the predicate is false;
the parent must acquire the released mutex, change the predicate, signal (even
cycles) or broadcast (odd cycles), and keep holding the mutex. The child must not
return until mutex reacquisition succeeds. Observe renewed mutex contention before
unlock; join/reap must clear condition list/lock state and recover all backing.
A fixture that skips condition waiting must reject exactly at assertion 252;
timeout or unrelated panic cannot satisfy the oracle. Count bounded coordination
yields toward the unchanged total of 64. Preserve older lifecycle and thread
regressions; freeze sources and run host/standards/workflow and pinned formatting.

The condition waiter is upstream stack-owned; child backing stays pinned while
live. The mutex owns predicate synchronization; atomic counters only observe the
fixture. Native wait/wake authority remains the domain thread capability. No new
resource allocation, timed clock translation, cancellation, process-shared wait,
multiple-waiter requeue, fairness, or concurrent child pool is introduced. Signal
and broadcast with one waiter do not qualify multiple-waiter ordering/wake-all.
Retain exact upstream/object identities and all failed attempts. Independent
consumer acceptance and extended coverage remain separate from this witness.
