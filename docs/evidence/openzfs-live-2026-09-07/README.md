# Registered worker overlap and allocator samples — 2026-09-07

The [contract](contract.md) extends the unchanged owned-file OpenZFS workload with
LIVE_THREADS observation. Qualification passes one warmup plus ten measured
processes per CPU view (22 processes total, three initialization/finalization
cycles each). Each process uses fresh private media. No native capacity, engine
worker policy, source archive, static engine library, sibling or pin changed.

## Findings

| Metric | Modeled one CPU | Host view: nine CPUs |
| --- | ---: | ---: |
| Peak registered workers, all ten measured samples | 171 | 235 |
| Corresponding overlapping stack requests | 44,826,624 bytes (42.75 MiB) | 61,603,840 bytes (58.75 MiB) |
| Corresponding guard requests | 700,416 bytes | 962,560 bytes |
| Cumulative successful creates | 548 | 740 |
| Maximum sampled glibc used heap | 4,882,304 bytes | 5,302,976 bytes |
| Maximum sampled glibc mmap allocation | 2,981,888 bytes | 2,981,888 bytes |
| Registered workers at final snapshot | 0 in all ten | 0 in nine; 48 in baseline-06 |

[comparison.json](comparison.json) reports min/median/nearest-rank-p95/max for
process peaks, allocator samples and completion counters. Raw stage observations
and exact environment facts are retained in qualified/results.json and logs.
Do not add separately observed allocator maxima as though they occurred together.
These data do not select a production memory budget.

A registered interval begins when pthread_create succeeds and ends in the outer
cleanup handler around the start routine. Registration is locked across create;
children cannot finish before being counted. Return and explicit pthread_exit
both invoke cleanup. There are 512 fixed observer records; failure rejects instead
of losing counts. Cleanup releases a record only after its final data access.
Counters include registered workers that have not started yet, but exclude the
main thread, later TLS destructors, final pthread/kernel exit and hidden dynamic
library calls not reached through executable wrapping. They are not an OS thread
census or proof that stack mappings can be reclaimed. Requested stack/guard sizes
are not resident memory or touched-stack high-water.

Allocator maxima are event-sampled mallinfo2 fields: successful creation, cleanup
and lifecycle snapshots. Sampling misses intermediate peaks and includes guest
libc/observer overhead. It is not native allocator usage or emulator RSS. The
observer lock and allocator inspection perturb scheduling. No performance or
cold-cache comparison is claimed.

In baseline-06, final kernel_fini returned with 53 registered intervals remaining;
five cleanup handlers ran before the completed snapshot, which still showed 48.
The other nine measured host-view samples showed zero there. This is not a leak
finding: the snapshot does not wait for those handlers, and process exit follows.
It demonstrates that this library boundary alone does not prove native stop or
safe backing reuse. Aether's explicit stop/unmap/retire contract remains required.

## Checks and attempts

A gated two-worker self-check proves overlap, exact 512-KiB stack/8-KiB guard
requests and cleanup through both return and pthread_exit. Peak-bypass and
cleanup-bypass controls reject exactly with `live peak` and `live cleanup`, exit
2. Existing count/name/CPU controls, no-write existing-file rejection, wrong-byte
failure and a fresh read-only zdb checksum/space-map traversal also pass. Media
hashes remain unchanged for rejected writes and zdb. All 98 Python tests plus Zig,
offline pins, workflow and scoped Clang formatting pass.

The build passes first attempt. Qualification attempts 1–3 stopped at container
image inspection: the VM connection was refused; no workload was run. The VM was
observed stopped after standalone launch commands exited. Attempt 4 keeps the
existing VM launch and qualification in one command; all checks pass. Retain the
failed receipts and launch logs. No runner or negative-control failure was counted
as a measured sample. Final repository sources/artifacts remain hash-identical
throughout qualification, as do all 4063 original engine source files and pinned
link archives in engine-identity.json.

## Reproduction and retained inputs

Use the exact pinned local image and engine work tree from the preceding
[CPU-view experiment](../openzfs-one-cpu-2026-09-06/README.md). Build with build.mk:
read-only engine at /work and frozen source/recipe copies at /inputs; a fresh owned
output at /out. From the engine directory run `timeout 120 make -f /inputs/build.mk
observe`. The retained build log contains expanded GCC/link commands. Additions
are BSD-2-Clause observation code; upstream notices and engine bytes are preserved.
artifacts.tar.gz contains producer source copies, objects and all eight executables.

Run the one-off `qualify.py` from the repository root against those local inputs.
It requires an absent qualified output; retain prior attempts under distinct names
before retrying. For this execution environment the concrete working invocation
was `podman machine start podman-machine-default && python3
 docs/evidence/openzfs-live-2026-09-07/qualify.py` when the VM was stopped. Do not
restart an already running shared VM. No host service installation is needed.

Every container is offline, read-only apart from private media/output and bounded
tmpfs, with no capabilities, no-new-privileges, 2-GiB memory and 512 pids. Each
workload has a 90-second guest timeout and 120-second outer bound. No host block
device or /dev/zfs is exposed. The local image itself remains a prerequisite, not
an exported toolchain. Generated media stay in zig-out with hashes in receipts;
evidence copies omit vdev.raw. Neither setup nor warmup enters measured summaries.

Next: attribute overlapping worker demand and the finalization boundary to actual
queues/roles before selecting executor policy or growing native resources. A
modeled one-CPU query alone leaves 171 overlapping workers. Full exit quiescence,
stack high-water, true allocator peaks, independent consumer acceptance and the
production Rust filesystem service remain open.
