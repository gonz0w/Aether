# Registered-worker role attribution

Attribute existing LIVE_THREADS intervals at creation, before a child can run.
Wrap the pinned zk_thread_create signature, carrying its requested name through
parent-local TLS only for the synchronous create call. Copy/validate that label
under the observer lock when registering the worker; do not infer identity from
late pthread_setname_np or recycled pthread tokens. Direct/unwrapped creation is
explicitly unattributed. No changes to engine scheduling, thread counts, clocks,
kernel budgets, sibling files or immutable pins.

Record role create/active/cleanup/individual peaks and a simultaneous role census
at the first aggregate high-water event. Individual role maxima must not be summed
as a simultaneous total. Reconcile every active/created/finished count; reject
unattributed engine creation in the qualified workload. Use the gated two-worker
check with distinct labels and an exact dropped-label control. Retain all existing
observer/storage/rejection/zdb checks and two CPU views, warmup plus ten samples.

Inspect the unchanged taskq teardown source for its notification/exit ordering.
Report open intervals at each finalization snapshot by role if observed, without
calling them leaks or OS-live census. Outer cleanup still precedes TLS destruction
and kernel stop. This is attribution, not a concurrency requirement proof or a
proposal to enlarge native resources. Freeze all qualified sources and retain
attempts. Update feasibility, STATE and workflow; run host/pins/format checks.
