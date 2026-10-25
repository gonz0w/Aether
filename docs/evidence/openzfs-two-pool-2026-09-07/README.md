# Private two-pool host qualification — 2026-09-07

The [contract](contract.md) passes on the first build and qualification attempt.
A private [two-line patch](taskq.patch) changes only system_taskq workers from
64 to 1 and delay_taskq workers from 4 to 1. The queues stay distinct, with the
same TSD lifecycle, allocation flags/limits, callback and unsupported timer behavior.
This profile is a host port experiment; native defaults have not changed.

## Observed resource reduction

All ten measured processes in each CPU view have these values. Both profiles use
the same owned-file workload and observer; the original comparison is retained in
[dispatch evidence](../openzfs-dispatch-2026-09-07/README.md).

| Observation | Original one CPU | Trial one CPU | Original nine CPUs | Trial nine CPUs |
| --- | ---: | ---: | ---: | ---: |
| Peak registered workers | 171 | 105 | 235 | 169 |
| Overlapping requested stack MiB | 42.75 | 26.25 | 58.75 | 42.25 |
| Cumulative creates, three lifecycles | 548 | 350 | 740 | 542 |

[comparison.json](comparison.json) retains ranges, sampled heap fields, per-process
dispatch counts and finalization observations. The reduction is 66 simultaneous
registered workers and 16.5 MiB of requested stack space. These are instrumented
intervals ending at outer pthread cleanup, not native stopped-thread counts or
committed/touched memory. Sampled glibc heap fields can miss peaks. No performance
or native resource ceiling is selected from this run.

Every lifecycle snapshot has exactly the expected cumulative fixed-pool creations:
one per queue per initialization, three each at completion. The final and all
measured after-fini snapshots have no open registered intervals in this series;
this does not remove the previously demonstrated gap between queue destruction
and actual thread stop. Native backing reuse still requires exact stop/reclamation.
External system dispatch stays zero; every measured process has 55 rejected delayed
requests and 113 ENOENT cancellations. The libzpool delayed-dispatch stub remains
unsupported, so storage success does not qualify a deadman watchdog.

## Qualification and negative controls

One warmup plus ten measured storage processes per CPU view pass (22 total, each
with three engine lifecycles). The real synthetic check runs four normal/preallocated
callbacks on the separate queues and drains through all three wait APIs. Existing
count/name/CPU/overlap/cleanup/role and dispatch mutants reject for their exact
reasons. A twelfth executable recompiles the original taskq source: it passes the
same storage workload but the profile oracle rejects it with exact
`fixed-pool worker count mismatch`, proving that default-count fallback is caught.
That additional process is a control, not a measured trial sample.

Existing-file rejection preserves media bytes; wrong expected payload rejects;
read-only zdb reports matching space maps without changing media. All 98 Python
tests plus Zig, offline pins, workflow (40 groups), and scoped C formatting pass.
The driver records 41 qualification commands in approximately 81 seconds. There
were no failed build or qualification attempts. No native Aether QEMU kernel run
is claimed for this private host adaptation.

## Inputs, reproduction and retention

The original 4,063 engine source files and 13 static archives verify unchanged
before/after execution against engine-identity.json. taskq-original.c is the exact
reviewed upstream source; taskq.c is the adapted copy. Both retain upstream CDDL
notices; LICENSE and COPYRIGHT here are upstream materials, not a relicensing of
Aether recipes. No upstream file is reformatted. Existing first-party observers
are unchanged and pass the pinned Clang 21.1.8 format check.

build.mk compiles the complete adapted object and links it before immutable engine
archives. The retained runtime-probe.map identifies /out/taskq.o as the implementation
and contains no extracted original taskq archive member. Original-profile control
uses a freshly compiled taskq-original.o. Expanded compiler/linker flags and pinned
image identity are retained; there are no downloads or new dependencies.

Use driver.py with its explicit local engine/output paths on a fresh owned output
root, preparing /inputs with host-runtime.c, host-dispatch.c, host-owned.c,
signature.c, taskq.c, taskq-original.c and build.mk. Copy build.mk to the output
root as expected by qualify.py. The driver starts the existing Podman VM only if
stopped, then builds and qualifies in one launch session. Its source archive and
execution.json retain the exact invocation used. The underlying commands are
`timeout 120 make -f /inputs/build.mk observe` in the pinned engine container and
`python3 docs/evidence/openzfs-two-pool-2026-09-07/qualify.py` from this repository.
Reproduction requires absent qualified outputs; retain each attempt before editing.

Containers have no network or capabilities, read-only engine/image/input mounts,
private output/media and tmpfs, 2 GiB memory and 512-pid limits. Workload bounds
remain 90 seconds inside and 120 seconds outside; the suite has an 1800-second
outer bound. No real disk/device or sibling repository is modified. Existing
native handoffs and immutable release pins remain unchanged.

artifacts.tar.gz retains twelve executables, objects, link map, exact runtime
sources, inputs and recipes. qualified/ retains every top-level receipt/log/source
snapshot. Private vdev.raw files remain in zig-out with receipt hashes and are not
copied into this evidence directory. archive-check.json verifies both source
archives and final artifact archive; manifest.json binds retained evidence files.

**Next:** review remaining file-vdev, ARC and ZIO worker creation/wait dependencies
and supported sizing controls for the one-CPU service profile, then choose the
next narrowly scoped host reduction. Keep issue/completion and reclaim progress
independent. Full-engine native memory/stack/stop qualification, Rust filesystem
service and the complete R1 shell/runner/persistence/package release remain open.
