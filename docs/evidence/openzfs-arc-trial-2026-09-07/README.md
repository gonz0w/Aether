# ARC serial eviction trial — 2026-09-07

**The private serial ARC profile passes the scoped host trial.** On top of the
qualified 1/1 system/delay profile, upstream's serial branch removes eight
parallel eviction workers while retaining its coordinator and every other queue.
No upstream default, native kernel budget, sibling or release pin changed.

| CPU view | Auto peak workers | Serial peak workers | Difference |
| --- | ---: | ---: | ---: |
| Modeled one CPU | 105 | 97 | 8 |
| Host view (9 online CPUs) | 169 | 161 | 8 |

These peaks repeat in all ten measured processes per cell. Four additional
warmups also pass. Each process runs three engine lifecycles and preserves the
owned-file export/reimport and verified payload workload. All normal runs finish
with zero registered live workers. Concurrent requested stacks fall by 2 MiB;
this is not resident memory, native capacity, latency or throughput measurement.
ARC creates 27 workers across the three auto lifecycles versus three serial
coordinators. Other roles have identical creation counts. Live/role/fixed-pool
validators and dispatch pair accounting pass.

## Progress evidence and controls

A private thread-local counter in arc.c counts returned resident MRU/MFU/uncached
eviction bytes for the calling thread. The trial explicitly calls nonretry
arc_flush after the first write and both verified reads. Other threads and ghost
state transitions cannot satisfy its delta. Every call in all four initial
positive runs and all 44 matrix runs makes nonzero progress. Measured deltas range
from 2,560 to 27,136 bytes; timing-dependent amounts are not compared as performance
or equivalent cache-state results.

Two omitted-call binaries return zero and exit3 at the exact
`ARC TRIAL FAIL: no resident eviction progress` assertion. They intentionally
terminate before normal engine cleanup; container teardown and private files
remain separately bounded, not a native cleanup witness. Real auto-mode output
also fails the serial executor-count oracle in both CPU views. Neither timeout
nor a generic process failure counts as these controls.

[Contract](contract.md), [six initial executions](execution.json),
[44-process matrix](matrix.json), [comparison](comparison.json) and all raw logs
are retained. The initial matrix attempt failed before engine execution because
its Podman connection was refused after the VM stopped. Its report, driver and
log remain as attempt-1-matrix.json, attempt-1-matrix.py and matrix-1-auto-00.log.
The retry starts the stopped existing VM within the execution session; input
sources and binaries remain identical. No engine failure was hidden.

## Inputs and reproduction

[inputs.json](inputs.json) pins all private copied inputs; arc.patch records the
upstream delta and arc.c retains its original notices. The only behavioral engine
selection is initializer 0 or 1 at compilation, plus the explicit omitted-call
control. Instrumentation and the three flush calls are private test additions.
[Link checks](link-check.json) confirm explicit arc objects replace the original
archive member. [Artifact checks](artifact-check.json) verify all archived build
outputs and unchanged 4,063 original sources / 13 archives. Original CDDL terms
and COPYRIGHT/LICENSE remain here. No new dependency is added.

The exact pinned offline image, compiler commands, private regular-file mounts,
network/device restrictions and timeouts are recorded in driver.py, build.mk,
execution.json and matrix.py. These are retained one-off recipes using private
output directories, not idempotent installation tools. Reproduce in fresh output
roots with the verified engine/archive set; do not overwrite retained attempts.
The matrix reuses three unchanged validators from the prior two-pool qualify.py;
that source remains in the immutable preceding packet.

artifacts.tar.gz contains the six executables, explicit objects and link maps.
The raw vdev files remain in the recorded zig-out/openzfs-arc-trial-2026-09-07
execution directories, with measured disk hashes in matrix.json; they are not
duplicated in this archive. Source and artifact hashes stayed fixed throughout
qualification. Host tests (98 Python tests plus Zig/pins/workflow) and scoped C
format checks pass. No unrelated native QEMU run was necessary for these private
Linux-only changes. Full observer-mutant regression, pressure/soak, native engine
integration and an independent review remain separate coverage.

Next: review the one-worker file-vdev experiment with actual read/write/flush and
failure controls, preserving its separation from ZIO completion. Then reassess
native capacity; this result does not establish a native OpenZFS filesystem.
