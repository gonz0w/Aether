# Fixed-pool callers and wait boundaries

Review inputs are exact OpenZFS 2.4.4 source files copied under review-inputs and
verified against engine-identity.json. The original 4063 source files and 13 static
link archives were checked before/after the run. No upstream bytes were changed.

- lib/libzpool/taskq.c:400–415 creates 64 system workers and 4 delay workers,
  initializes taskq TSD, then destroys the two distinct queues and deletes the key.
  Observation registers pointers after initialization and retires them only after
  finalization. Queue bookkeeping is still not native thread-stop confirmation.
- taskq.c:105–134 enqueues normal dispatch and returns constant 1 (or 0 on allocation
  failure). Normal acceptance is not callback completion or a unique task identity.
  Preallocated dispatch has no returned acceptance result; its counter records
  calls only. Original callback and argument pointers are passed unchanged.
- taskq.c:138–143 returns 0 for delayed dispatch without executing or queuing work.
  Cancellation returns ENOENT. The synthetic check confirms no delayed callback
  through four actual normal/preallocated completions and real queue draining.
- taskq.c:193–212 drains the entire queue for wait, wait_id and wait_outstanding.
  The ID is ignored by the latter two. Destroy's taskq_wait call is in the same
  object and is outside the external link-wrap observation. Zero observed waits
  therefore does not mean no waiting/draining happened.
- module/zfs/spa.c:10904–10908 cancels and requests a deadman timer during sync;
  its 10961 cancellation and 1937 teardown cancellation are consistent with the
  measured 113 = 2*55+3 pattern over three lifecycle cycles. Callsite-specific
  counts were not recorded, so that relationship is not exclusive attribution.
- spa_misc.c:728 would rearm spa_deadman after a callback. It is present in the
  compiled archive, but the retained delayed-dispatch implementation schedules
  no callback. Owned-file success does not qualify the deadman watchdog.
- zio.c:2235–2288 explicitly disables the I/O-delay path in userspace; its
  system_taskq delayed zio_interrupt dispatch is guarded by _KERNEL.
- zfs_fm.c's cleaner scheduling and cancellation paths are kernel-only in the
  relevant conditional sections. zvol.c contains system-queue prefetch callers
  and a wait-outstanding path. The original linked archive exports spa_deadman,
  but not zfs_ereport_cleaner, zfs_ereport_taskq_fini or zvol_prefetch_minors_impl;
  these source callers must not be assumed part of this libzpool workload.
- spa.c:1880–1888 deliberately uses a separate prefetch queue to avoid monopolizing
  system_taskq with long-running traversal. Per-pool issue/completion, prefetch,
  reclaim and timer paths must remain distinct until their dependency progress is
  reviewed. Zero activity in these fixed pools says nothing about other queues.

Observer scope is external references to the wrapped entry points only. It neither
wraps callbacks nor changes the original function/argument/lifetime, allocation,
thread count or scheduling. Counters are cumulative across three queue lifecycles;
returned-result fields can lag call fields at an in-progress snapshot. The private
mutex is released before every engine call. Only main-thread snapshots print.
Synthetic controls call the wrappers explicitly; build logs retain actual engine
link-wrap flags and signature assertions cover all nine wrapped function types.
This is scoped observation, not whole-engine callback concurrency instrumentation.

Next trial: reduce only the two fixed host pool counts to one worker each in a
private source adaptation, keeping distinct queues and TSD lifecycle, all other
worker defaults and the unsupported delayed/cancel semantics explicit. Re-run the
synthetic dispatch/drain controls and the full owned-file/CPU-view measurement.
Do not infer native resource sizing or remove watchdog requirements from this
workload. Wider queue dependency, memory/stack and native service work remain.
