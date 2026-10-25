# OpenZFS supported-host baseline — 2026-09-06

[Assessment](../../OPENZFS-FEASIBILITY.md#supported-host-result--2026-09-06).
The upstream user-space build and create/check workload pass. Fresh-container
read-only import/checksum verification passes. **Writable ztest -E reopening fails**;
this baseline does not close the planned deterministic writable export/import test.
No Aether boot, mounted filesystem, namespace workload or engine adoption is claimed.

## Inputs and confinement

Source commit: 71a9f9578616a90c3c14bb59629fb4d31bfd68d1, from the unchanged
[retained OpenZFS archive](../openzfs-review-2026-09-06/README.md).
`source-comparison.json` verifies every original regular source file still matches
that archive after building. Generated build files and products are retained in
`build-and-workloads.tar.gz`, together with all disposable disk bytes and raw logs.
Upstream licenses/notices are preserved; no original source is relicensed.

The image recipe extends the existing userland Linux/arm64 image ID
8d0dff22866c67ea5de1d66ff04a54f17e610a11e3a5c970414820663c7649a4.
Network-enabled setup installs build tools only inside the new image. Final image:
ef2164012fa1c3a315d34091c6ed8951d3eac37c7192d5adbb5bf4c1a30d916f.
`image.json` and `packages.txt` bind installed bytes/versions; GCC is 14.2.0.
The image remains local as localhost/aether-openzfs-review:20260906. The recipe's
package repository is mutable: rebuilding it elsewhere is not a byte-reproduction
claim. The image itself is not exported in this evidence set.

Builds and workloads used `podman run --rm --pull=never --network=none --read-only
--cap-drop=all --security-opt=no-new-privileges --memory=2g --pids-limit=512`, with
only the private work directory writable, scripts mounted read-only, and a 256-MiB
/tmp tmpfs where needed. No privileged mode, host devices, /dev/zfs or module
loading. Only these owned containers were removed automatically; no shared VM,
other container, service or sibling source was changed. Podman access needed
sandbox escalation; the first machine-list probe could not write its lockfile.
An initial image-inspection command also had an incorrect shell entry point;
correcting --entrypoint /bin/sh resolved it. Neither was an engine test.

## Attempts and exact outcomes

1. `build.sh`: autogen/configure succeeded; selecting libzpool/ztest/zdb directly
   failed compiling spa_history.c because zfs_gitrev.h had not been generated.
   `make-attempt-1.log` retains the failure.
2. `build-2.sh`: the guessed include/zfs_gitrev.h make target did not exist;
   `generated-header.log` retains that build-sequence failure.
3. `build-3.sh`: upstream `make gitrev`, then the three targets, passed under a
   600-second watchdog. `make-3.log` and configuration logs are retained. OpenZFS
   libraries are static; host system dependencies remain dynamic as `ldd.txt` shows.
4. `workload.py`, run-1: -C off was rejected before pool work. The pinned source
   accepts -C special=off despite its older help/man syntax. Input and exit 1 retained.
5. `workload-2.py`, run-2 create: passed, one regular 256-MiB vdev remained. Upstream
   checks report 0 killed/1 completed. The requested runtime was 3 seconds, while
   the complete operation took 30.47 seconds including initialization/checking.
6. run-2 reopen: exit 3 after child SIGABRT. `ztest_import_impl` could not discover
   the pool. Linux libzpool `pool_active` opens /dev/zfs and returns failure when
   unavailable; no unconditional inactive stub or host kernel module was added.
7. `verify.py`, verify-1: a fresh container's zdb -bcc -G -d -Y -e -y traversal of
   pool GUID 6003706383351255937 passed with no checksum/leak failure. The complete
   vdev hash matches the create result and remained unchanged after verification:
   9b3224ce1c2c57618aed76f8de4ff6f8419dd0137ba4520f6623acd9fbcdf545.
8. `zdb -l /work/corrupt.raw`: an explicitly all-zero 256-MiB image exits 2 and
   rejects each of four labels. This tests invalid-media recognition, not a payload
   corruption/checksum injection or uncertain-write recovery.

Per-workload results record exact argv, start/end UTC, exits, disk hashes and
sample counts. The runners impose 90-second process-group watchdogs, with outer
container commands bounded to 200/100 seconds. No workload watchdog fired.
Setup/initial build probes did not retain individual UTC/structured receipts;
this provenance gap is explicit, not retroactively treated as complete qualification.
No failed log or disk was discarded. Use fresh private output directories to rerun
these experimental scripts; do not run them against retained evidence directories.

## Measurements and limits

GNU time maximum RSS: 215248 KiB for the create/test invocation. The 20-ms monitor
saw combined ztest/zdb RSS up to 218644 KiB and 257 combined threads; verification
saw 29112 KiB and 227 threads. RSS sums can double-count shared pages, polling can
miss peaks, and GNU time has different child-accounting semantics. These are one
randomized workload's observations, not minimum requirements, a performance
baseline or per-thread stack high-water marks. The single selected ztest worker
is not the engine's total thread count.

`size.txt` records Linux/arm64 text/data/BSS; `ldd.txt` records host dynamic
closure. `libzpool-undefined.txt` is raw archive nm output with inter-object
references, not an isolated platform-import list. Source/generated configuration,
static archives and executables are retained for follow-up analysis. No x86_64
build, deterministic application payload workload or writable-reimport pass yet.

`zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`
passes: kernel/standards/workflow plus 85 Python tests (`host.log`). Aether runtime
sources/build dependencies were unchanged, so no native QEMU suite was repeated.
The next experiment must close controlled writable export/import and then establish
x86_64/resource closure before adopting native memory/thread budgets.
