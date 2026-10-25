# Worker-role overlap attribution — 2026-09-07

The [contract](contract.md) qualifies creation-time labels and the first aggregate
peak census for the unchanged owned-file workload. Build, signature assertion,
qualification and exact controls pass first attempt. The runner is started only
if stopped and kept with the build/qualification in one command. No engine,
kernel, sibling or release-pin changes are made.

## Simultaneous census at the first measured peak

All ten measured processes in each view have these grouped totals. Individual
requested labels and every sample are retained in [attribution.json](attribution.json).

| Worker role/family | Modeled one CPU | Nine-CPU host view |
| --- | ---: | ---: |
| system_taskq | 64 | 64 |
| delay_taskq | 4 | 4 |
| File-vdev workers | 16 | 16 |
| arc_evict label (queue plus coordinator) | 9 | 9 |
| ZIO issue/completion families | 55 | 72 |
| Other named workers | 23 | 70 |
| Total registered workers | 171 | 235 |

The same 42.75/58.75 MiB of overlapping requested stack space is reproduced.
This is not resident memory, touched-stack high-water or a selected native budget.
The 68 fixed system/delay workers remain despite changing the modeled online-CPU
query. CPU-dependent ZIO and other groups account for the 64-worker difference.
Labels can combine roles and queues; the full per-label record prevents treating
this table as permission to merge distinct progress paths.

## Finalization findings

Three measured after-fini snapshots per view retain open intervals. All belong
to system_taskq/delay_taskq: counts are respectively 48+4, 51+3 and 52+3 in the
one-CPU view; 52+4, 53+2 and 51+4 in the host view. Every measured completed
snapshot in this series has zero registered intervals. These are snapshots of
outer-cleanup accounting, not full pthread/kernel exit or a leak detector.

[Source review](source-review.md) establishes why: taskq workers decrement their
queue count and notify destruction before pthread_exit reaches outer cleanup.
Native backing reuse must retain exact stop/unmap/retire. The earlier unlabelled
48-interval final snapshot cannot be assigned retroactively to these roles.

## Coverage and reproduction

Warmup plus ten measured processes per view pass (22 processes, three engine
lifecycle cycles each). Every registered creation is attributed; role creates,
active/finished counts and simultaneous peak census reconcile exactly. Final
per-label creates also equal the independent requested-name counters. A gated
return/pthread_exit check proves distinct labels and role cleanup. Dropping role
labels rejects with exact `live role label`, exit 2. Prior count/name/CPU/peak/
cleanup controls, existing-file no-write denial, wrong-byte failure and read-only
zdb traversal all pass. No failed runs were counted as samples.

All 98 Python tests plus Zig/pin/workflow checks and scoped Clang formatting pass.
This modifies only a host observer; prior native runtime qualification remains
retained coverage, with no new QEMU kernel run claimed. Sources/artifacts are
frozen and original engine files/static libraries match engine-identity.json.

Use the same pinned image/engine and confinement as the preceding
[live observation](../openzfs-live-2026-09-07/README.md), with this directory's
build.mk and qualify.py. Freeze host-runtime.c, host-owned.c, signature.c and the
recipe under /inputs; mount the engine read-only at /work and a fresh owned /out.
Build with `timeout 120 make -f /inputs/build.mk observe`; the log retains expanded
flags and the added --wrap=zk_thread_create link boundary. Run qualify.py from the
repository root against its explicit local paths, with an absent qualified output.
Keep existing VM start and qualification in the same command if this environment
otherwise stops the VM with its launch session. Do not restart an active VM.

artifacts.tar.gz retains producer sources, objects and nine executables. Qualified
logs/receipts bind exact artifacts, sources, tool image, media and commands. Private
vdev.raw files remain in zig-out with hashes; evidence copies omit media. Builds
and workloads stay offline, capability-free, read-only except fresh outputs/media
and bounded tmpfs, with 2 GiB/512-pid limits and 90/120-second run bounds. Observer
code uses BSD-2-Clause; copied upstream review inputs retain their own notices,
LICENSE and COPYRIGHT. No production filesystem or independent-owner acceptance
is implied.

Next: measure fixed system/delay dispatch activity and review callback/wait
relationships before trialling a smaller explicit host profile. Keep independent
issue/completion, reclaim and timer progress; do not enlarge native limits or
assume concurrency requirements from worker-registration counts alone.
