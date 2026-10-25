# Actual taskq dependency and drain witness

Run unchanged libzpool taskq code in the pinned Linux/x86_64 container. Initialize
its real system taskqs/TSD, then create two distinct one-worker queues, A and B.
A has two entry slots, B one; use TQ_NOSLEEP only. Three create/work/drain/destroy
cycles prove bounded fixture reuse, not safe thread-memory reclamation or a global
engine capacity policy. Keep taskq_now zero; no inline-dispatch shortcut.

A's callback dispatches gated work on B and waits for B. Queue a second gated
callback on A. A separate pthread calls actual taskq_wait_id(A, first_id); a
cv_wait observer marks entry into the real queue predicate wait without changing
it. It must remain unfinished while B is gated and while A's later callback is
gated. Release in order; both callbacks must finish before the drainer joins.
IDs are the existing constant 1, not unique identities. Observe actual owner TSD
inside callbacks. A deliberately immediate wait_id must fail exact premature-drain
exit 2; a fake successful delayed dispatch must fail exact unsupported-delay exit
2. Watchdog expiry is failure, never an accepted negative oracle.

While active/queued entries are held, extra TQ_NOSLEEP dispatch rejects with zero
and unchanged allocation/list state. After drain, a new B dispatch succeeds and
both queues have zero active/queued/allocated entries before destruction. Delayed
dispatch must return zero and never run its callback; cancel remains ENOENT.
Do not infer that maxalloc bounds TQ_SLEEP: upstream may exceed it after throttling.

All gates use atomics and bounded monotonic waits. The cv observer uses an atomic
watched pointer and clears it before destruction; it never dereferences freed
queues. No changes to upstream, kernel, siblings or release pins. System defaults
still start their workers; two fixture queues do not mean the whole process uses
two threads. Keep Linux execution distinct from native Aether and full engine
semantics. Record source identities, exact commands and all failures; freeze
inputs during qualification. Run repeated positives, both exact controls, host/
pin/workflow and pinned C formatting. No media or host devices are needed.
