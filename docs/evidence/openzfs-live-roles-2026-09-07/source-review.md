# Finalization ordering and attribution boundary

Inputs are exact retained OpenZFS 2.4.4 files under review-inputs, checked against
engine-identity.json. No upstream adaptation was made in this experiment.

- include/sys/zfs_context.h:210 and 243 define kthread_t as pthread_t and declare
  zk_thread_create. signature.c compiles an exact type-compatibility assertion
  against those pinned definitions, including pointer return and size_t stack.
- lib/libzpool/kernel.c:98–149 sets attributes, allocates the startup wrapper,
  calls pthread_create, destroys attributes and only then calls pthread_setname_np.
  Using the naming callback for live identity could miss a departed worker or
  match a reused token. The new wrapper passes the requested label through
  parent-local TLS for this call and copies it at successful registration.
- lib/libzpool/taskq.c:248–251 decrements tq_nthreads, broadcasts its wait CV,
  unlocks and then calls thread_exit. The predicate becomes true before our outer
  cleanup and before pthread/TLS/kernel exit.
- taskq_destroy at 306–337 clears the active flag, waits for tq_nthreads == 0,
  frees entries/thread-list and destroys synchronization objects. It does not join
  detached workers or wait for the outer observation cleanup.
- system_taskq_fini at 410–415 destroys system_taskq then delay_taskq; kernel_fini
  at kernel.c:961–971 calls it near the end, followed by random_fini. This accounts
  for why these roles can still have registered intervals at the after-fini
  snapshot. This is an ordering explanation, not proof of an upstream defect.

Observed tails in this series name only system_taskq/delay_taskq. The previous
series' 48 intervals had no role identity and cannot retrospectively be assigned
by this result. Native cleanup must still observe each exact child ID stopped
before unmapping/retiring it. No snapshot here establishes that OS-level boundary.

Requested labels may aggregate multiple queues or mechanisms: arc_evict includes
an eight-worker queue and one coordinator; ZIO issue/completion families retain
separate labels/indices in attribution.json. Roles are diagnostic categories,
not unique taskq identity, native handles, required concurrency or executor-sharing
permission. The first aggregate-peak census is simultaneous; separate per-role
peaks may occur at other instants and must not be summed as one resource state.

Next review target is actual dispatch activity and callback/wait dependencies for
the fixed system/delay pools. Their 68 registered workers are measured cost, not
proof that all 68 are required or that replacing them with one executor is safe.
