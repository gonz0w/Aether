# Remaining worker dependencies — 2026-09-07

**Select ARC's existing serial eviction path for the next private host trial.**
Keep the qualified 1/1 system/delay profile and every other pool unchanged. This
review selects a test, not a native worker budget or a newly qualified profile.

The exact OpenZFS inputs are retained under inputs/ and bound by identity.json.
All 4,063 original source files and 13 link archives match the preceding identity.
The [two-pool qualification](../openzfs-two-pool-2026-09-07/README.md) supplies the
runtime observations; no new engine or native execution is claimed here.

## Sizing and dependencies

| Pool or family | Retained one-CPU peak | Sizing and progress constraint | Disposition |
| --- | ---: | --- | --- |
| ARC eviction label | 9 | Eight parallel workers plus a separate eviction coordinator; static max_ncpus is 64 | Trial upstream serial eviction, retaining the coordinator |
| File-vdev | 16 | MAX(boot_ncpus, 16); synchronous host file operations dispatch completion to ZIO | Keep for this trial; review a distinct one-worker backend later |
| ZIO issue/completion families | 55 | Read issue 8, free issue minimum 32, trim issue 4, remaining separate queues | Retain; queue roles encode deadlock avoidance |
| System/delay | 2 | Already qualified private 1/1 profile | Keep unchanged |
| Other named workers | 23 | Mixed independent service, transaction and pool roles | No blanket reduction |
| Total | 105 | First simultaneous registered peak | Not required concurrency or native thread capacity |

[peak-census.json](peak-census.json) reconciles all ten measured samples per CPU
view with the aggregate peaks, including zero-at-peak labels. A shared label can
combine a queue and a coordinator; it is not itself an executor ownership boundary.

### ARC: use its explicit serial algorithm

In [arc.c](inputs/module/zfs/arc.c), lines 483–492 document value 1 as disabling
parallel eviction. Lines 4099–4126 compute automatic sizing from max_ncpus and only
create the parallel taskq/argument array when the selected count exceeds one.
The [libzpool header](inputs/include/sys/zfs_context.h), lines 612–624, fixes
max_ncpus at 64 while boot_ncpus queries sysconf. Therefore the one-CPU observer
never changed this ARC input: floor(log2(64)) + 64/32 = eight parallel workers.
The separate arc_evict zthr is created at arc.c:8086–8087, explaining the ninth
worker with the same observed label.

arc_evict_state (4150–4340) has both algorithms. Parallel work dispatches per-sublist
entries and waits for the entire taskq before reading result fields. Serial work
calls arc_evict_state_impl directly, retaining markers, sublist locks, progress
accounting and rescan behavior. This is an existing implementation branch; setting
one must not mean queuing work to a nonexistent pool or disabling eviction.
The separate coordinator's callbacks (4811–4907) retain wakeup/eviction-waiter
coordination. Its lock-order commentary forbids casually replacing the notification
protocol. Keep arc_prune, arc_flush, arc_reap and that coordinator separate.

arc_fini (8140–8182) waits for background flushes, flushes all buffers, drains prune,
conditionally drains/destroys the parallel taskq, and cancels eviction/reap zthrs.
The serial profile must enter this mode before the first initialization and keep
it across all three lifecycles; switching after parallel initialization could leave
persistent static state requiring separate cleanup analysis. Do not turn this
experiment into a runtime configuration API.

Do not change max_ncpus globally to obtain this result. The same header also uses
it for CPU_SEQID, so a platform-wide constant change would have broader effects.
The narrow trial is an exact private initializer change from 0 to 1 in arc.c,
with original notices retained, a freshly compiled object and link-map verification.
The kernel module parameter declaration is not a verified host configuration API.

### File-vdev: independent blocking I/O remains necessary

[vdev_file.c](inputs/module/zfs/vdev_file.c), lines 60–73, creates at least 16
workers and destroys the queue at finalization. Its strategy callback borrows an
ABD buffer, performs a synchronous read/write and returns the buffer before calling
zio_delay_interrupt. Flush and deallocate callbacks also perform their operation
before zio_interrupt. Dispatch sites in vdev_file_io_start retain the zio pointer
until that callback/completion path consumes it; dispatch is not completion.

The [host adapter](inputs/lib/libzpool/kernel.c) uses pread64, pwrite64, fsync and
platform deallocation calls. In this host implementation, these operations do not
obtain progress from the same Aether service queue. A future native adapter can
wait on a capability-scoped block service and must preserve its independent progress
and buffer lifetime. A one-worker file queue is a plausible later serialization
trial, not established by this review. It needs actual read/write/flush progress,
backlog and error outcomes; tiny successful files do not cover saturation or
arbitrary blocked devices. The source contains a fixed floor, not a demonstrated
libzpool worker-count setting. Do not merge this queue into ZIO completion.

### ZIO: the split is part of correctness

[spa.c](inputs/module/zfs/spa.c), lines 162–196 and 1166–1250, distinguish fixed,
scaled and synchronous pools. Lowering the percentage cannot remove the fixed read
and trim counts or the free-issue minimum. The configurable read/write row parser
at 1322 onward is guarded by _KERNEL; it is not an available libzpool control here.

[zio.c](inputs/module/zfs/zio.c) makes the dependencies explicit:

- Lines 2164–2196 route config-writer/probe work to separate NULL-type queues when
  normal workers may be blocked on the config lock. L2ARC auxiliary writes also
  use that escape route. Preserve these queues even when the current workload
  rarely uses them.
- Lines 2227–2229 dispatch completions to interrupt queues. In userspace the
  delayed-completion path reaches this route without the kernel-only timer branch.
- Lines 2458–2483 move potentially blocking pipeline stages from interrupt to issue
  context so completion workers remain available; stack-dependent redispatch is
  another separate constraint. A merged executor defeats that distinction.
- zio_wait (2508 onward) executes a pipeline and waits on its condition variable.
  Its completion may require other tasks; task registration counts cannot prove
  how many threads suffice for nested I/O or config-lock progress.

Reducing ZIO counts needs targeted nested-I/O/config-writer/probe and completion
witnesses with exact failure controls. Preserve the existing taskq TSD membership
used by zio_taskq_member. Do not equate a Linux userspace worker pool with native
interrupt context, nor implement kernel scheduling priority from these host labels.

## Next executable acceptance

Build a private ARC-serial object on the retained two-pool profile, leaving all
other engine objects and limits unchanged. The next experiment should:

1. Validate one arc_evict-labelled coordinator per lifecycle and no parallel ARC
   queue, while the original object control is rejected by the same profile oracle.
2. Witness actual serial eviction and nonzero progress on cache populated by the
   owned-file workload, including teardown flush. A worker-count change alone is
   insufficient; preserve callback/flush results and reject an omitted-eviction
   control for the named reason. Document if pressure-driven eviction is untested.
3. Repeat both CPU-view workloads, exact prior observer/storage controls and
   read-only media verification. Compare resource observations to the two-pool
   baseline without assuming an eight-worker peak saving in advance.
4. Retain all attempts, source/patch/object/link identities and host checks. Keep
   the three lifecycle cycles and native exact-stop requirements. Do not claim
   production cache pressure, watchdog support or native capacity from this trial.

The direct serial branch makes this a smaller semantic change than redesigning
ZIO queue progress. Native full-engine memory/stack sizing, the Rust filesystem
service, and complete R1 shell/runner/persistent package composition remain open.

## Review checks and limits

This is a source/dependency review, not an independent maintainer sign-off or
runtime conformance result. Identity and census checks bind the unchanged inputs
and prior observations. `zig build test --cache-dir .zig-cache --global-cache-dir
.zig-cache/global` is the selected local check; checks.json and host.log retain its
result and timing. No new source/build entry point or runtime output is introduced.
No sibling, native ABI/grant, immutable release pin or earlier evidence is changed.
