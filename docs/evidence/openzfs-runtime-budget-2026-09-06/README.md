# OpenZFS runtime demand baseline

[Contract](contract.md) precedes the observer implementation; the current
[assessment](../../OPENZFS-FEASIBILITY.md#observed-startup-and-storage-demand--2026-09-06)
defines measurements and limitations. This is Linux/glibc under QEMU x86_64 user
emulation, not a native Aether engine or a selected memory/thread budget.

Results: one warmup plus ten measured fresh-process storage workloads pass.
Each observed 102 detached creates by first initialization and 740 over the full
three lifecycle cycles, all with 256-KiB stack requests. These are cumulative
requests, not live-thread peaks. Allocator snapshots and every raw sample,
min/median/nearest-rank-p95/max are retained in qualified/results.json. Startup
and final snapshots must not be interpreted as peak heap or resident stack use.
No comparative latency claim is made from container wall times.

Controls pass: exact two-thread observer attributes; count-bypass exit 2 with
`RUNTIME FAIL: observer count`; test-only create ceiling rejection; unchanged
existing media on rejection; wrong-byte payload failure; fresh read-only zdb
checksum/space-map traversal with unchanged disk digest. Host checks pass with
98 Python tests, Zig checks, three standards pins and workflow inventory. Scoped
Clang 21.1.8 formatting passes. Native kernel sources and pins are unchanged;
no fresh native QEMU regressions are claimed for this host-only observer.

## Retained inputs and reproduction

Engine source archive and pinned container are those in the
[preceding build](../openzfs-x86-2026-09-06/README.md). engine-inputs.json verifies
all 4063 original files and identifies the static link archives. The container
image ID fixes the local cross-tool closure (GCC 14.2.0, QEMU 10.0.11); its full
inspection is retained. The image itself remains a local prerequisite, not an
exported toolchain. The previous evidence retains compiler/packages/emulator facts.

artifacts.tar.gz retains the source copies, build recipe, objects and three
executables. Original engine source/notices are unchanged; the observer is
BSD-2-Clause. qualified/sources.tar.gz and results.json bind frozen repository
inputs and exact artifact hashes. Input source copies match the current files.
All sample media remain in the private zig-out output tree, with hashes in the
receipt; these media are not required to interpret the counters. Reproduction
creates new files and must never reuse a sample directory as fresh media.

Build using build.mk with the retained engine work tree mounted read-only at
/work, source copies/recipe read-only at /inputs, and a fresh owned output at
/out. From /work/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1 run
`timeout 120 make -f /inputs/build.mk observe` in the exact pinned image. The
build logs retain expanded compiler/link commands, including all four --wrap
symbols. Container restrictions match qualify.py: --pull=never, --network=none,
--read-only, --cap-drop=all, no-new-privileges, 2-GiB memory, 512 pids and bounded
tmpfs. No host device or /dev/zfs is passed through.

The one-off `qualify.py` records exact local paths and runtime argv. It requires
the matching retained build and an absent qualified output directory. For a new
attempt retain the existing directory under a distinct attempt name before
running; do not overwrite it. Runtime runs use new private media, 90-second guest
and 120-second subprocess limits. Setup/build is outside the measurement samples;
one explicit warmup is excluded from the ten-sample summaries. The ten later
processes start fresh; host filesystem/page caches are not flushed or called cold.

## Attempts and remaining work

Build attempt 1 failed strict missing-prototype diagnostics. Its source and log
are retained; explicit declarations fixed it without suppressions. Build attempt
2 passes. Qualification attempt 1 was infrastructure failure at Podman inspection
because sandbox socket access was unavailable; no workload ran. Its complete
receipt is retained under attempt-1-sandbox. The same frozen inputs then passed
with authorized socket access in qualification attempt 2. No failed observation
was discarded or counted as a fast result.

The observer interposes executable references, not hidden calls within dynamic
libraries, and uses guest glibc mallinfo2 rather than emulator RSS. No live-thread
census, stack high-water, allocator peak, orphan recovery, native port or release
readiness claim follows. Next is attribution by task queue and a measured explicit
service policy before any kernel capacity change. Independent owner acceptance,
platform/vdev adaptation and Rust namespace/service integration remain open.
