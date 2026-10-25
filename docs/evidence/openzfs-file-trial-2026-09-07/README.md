# One-worker file-vdev trial — 2026-09-07

The private one-worker file backend passes the scoped host trial. Separate ZIO
completion queues remain intact. The trial builds on the qualified 1/1
system/delay and serial ARC profile; no upstream default or native limit changes.

| CPU view | Default file workers: peak | One file worker: peak | Reduction |
| --- | ---: | ---: | ---: |
| Modeled one CPU | 97 | 82 | 15 |
| Host view (9 online CPUs) | 161 | 146 | 15 |

All ten measured processes per cell repeat these peaks; four additional warmups
pass. Concurrent requested stacks fall by 3,932,160 bytes (3.75 MiB). These are
registered host worker and stack-request observations, not resident memory,
throughput, latency or a native resource budget. All other role creation counts
match. Each process preserves three engine lifecycles, verified payload data,
export/reimport, resident ARC eviction progress and zero final registered workers.

## I/O and failure coverage

The actual file backend records successful reads, writes and fsync callbacks in
every positive run. Explicit tagged requests inject EIO before backend access:
read/write EIO reaches the waiting caller. The flush helper deliberately creates
a child with DONT_PROPAGATE; its injected child EIO is observed while its waiting
parent returns zero. The fixture requires both outcomes. This internal helper
result does not establish a caller-visible durable-sync contract.

Ten targeted cases pass: four normal profiles and six error-hiding controls.
Controls must exit 4 at the exact read, write or flush-child assertion in both CPU
views. Injection skips physical access even when a control hides the error, so
experimental label writes never reach the vdev. These abnormal controls terminate
before normal engine cleanup; bounded container teardown is separate coverage.
The 44-process matrix requires all three success counters positive and exactly
one injected error of each type. Real default-mode output also rejects the
one-worker count oracle in both CPU views. Separate issue/completion and escape
queues retain their original counts and ownership.

The first targeted attempt failed at zio_create's configuration-lock assertion.
The private fixture was corrected to hold SCL_STATE_ALL for reading across leaf
selection and all waits. The original sources, build outputs and failed log are
preserved in attempt-1.tar.gz and 1-auto.log. Retry cases have distinct names.
No failed attempt was replaced by the successful retry.

## Evidence and reproduction

[Contract](contract.md), [targeted execution](execution.json),
[matrix](matrix.json), [comparison](comparison.json), and raw logs retain the
scope and results. inputs.json pins the private sources; vdev_file.patch records
the backend change. The upstream CDDL notices, LICENSE and COPYRIGHT are retained.
The original 4,063 engine source files and 13 link archives remain unchanged.

The exact offline container image, compiler commands, resource bounds and private
regular-file mounts are in driver.py, build.mk and matrix.py. No network, devices
or imported pools are used. These are retained one-off recipes; reproduction
requires fresh output roots and the verified engine/archive set. The matrix uses
the unchanged validators retained in the prior two-pool packet. No new dependency
or active script entry point is introduced.

artifacts.tar.gz retains ten executables, explicit objects and link maps.
[Artifact checks](artifact-check.json) verify archive contents and frozen inputs;
[link checks](link-check.json) verify the private file and ARC objects replace the
original members. Raw vdev files remain at execution paths under
zig-out/openzfs-file-trial-2026-09-07, with measured hashes in matrix.json; they are
not duplicated in the archive. Host tests (98 Python tests plus Zig/pins/workflow)
and scoped C format checks pass. Private Linux-only changes do not require an
unrelated QEMU rerun. Original release pins and sibling repositories are unchanged.

Next: reassess the remaining native worker, stack, memory and execution-service
capacity gap before proposing a bounded native engine experiment. Saturation,
short I/O, pressure/soak, caller-visible durable sync, independent review and native
filesystem/service composition remain open. This is not a native filesystem or
release-readiness result.
