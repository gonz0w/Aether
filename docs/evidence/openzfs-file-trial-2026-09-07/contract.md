# One-worker file-vdev trial

Recorded before implementation, 2026-09-07. Keep serial ARC and 1/1 system/delay
queues. Privately replace only file-vdev worker count MAX(boot_ncpus,16) with one;
keep queue flags, allocation hints, lifetime, synchronous file operations and
separate ZIO completion unchanged. Original sources/notices/archives, native
budgets, siblings and release pins remain fixed. Linux host evidence only.

Read/write/fsync callbacks get atomic success/error counters. Targeted physical
read/write requests carry a private marker and inject EIO before backend I/O;
there are no experimental writes to label bytes. Require zio_wait == EIO with
CANFAIL/DONT_RETRY. A marked parent flush causes only its child to inject EIO;
upstream zio_flush deliberately sets DONT_PROPAGATE, so require parent result zero
AND recorded child EIO. Do not mistake that internal helper for durable user sync.
Counter reads are atomic; marked parent/child lifetimes remain held until wait.
Physical read buffers are initialized and owned through completion; no pointer
survives completion. Existing unmarked engine I/O keeps its original path.

Hide-read, hide-write and hide-flush error controls must fail exact assertions,
without performing the injected backend operation. Require nonzero real successful
read/write/fsync counts from the complete storage workload. Preserve ARC progress,
export/reimport and payload checks; all normal exits must have no live registered
workers. Compare baseline/one-worker in both CPU views, one warmup plus ten samples
per cell. Retain earlier live/role validators and reject baseline as one-worker.
This does not qualify arbitrary blocked devices, saturation, higher-level fsync,
full observer-mutant regression, native filesystem or pressure/soak.

Pinned offline container, no network/devices, fresh owned regular-file vdevs and
bounded watchdogs. Preserve failed attempts and frozen hashes. Foundations I/E,
DEVELOPMENT and retained upstream CDDL terms apply; copied first-party fixtures
remain BSD-2-Clause. No new dependency or shared API. Update STATE and filesystem
feasibility with results, evidence limitations and next native-capacity decision.

Attempt 1 exposed the mandatory SCL_STATE_ALL reader hold in zio_create.
The test now enters that configuration lock before reading the leaf pointer and
retains it through all waits, then releases it before spa_close. The original
failed source, executables, receipt and log are retained in attempt-1.tar.gz.
