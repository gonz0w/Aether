# OpenZFS Linux/x86_64 baseline — 2026-09-06

[Contract and assessment](../../OPENZFS-FEASIBILITY.md#x86_64-baseline-result--2026-09-06).
This is an offline Linux guest workload under QEMU user emulation, not native
Aether execution, a filesystem namespace or a production Rust service.

## Inputs and reproduction

Engine: OpenZFS 2.4.4, commit 71a9f9578616a90c3c14bb59629fb4d31bfd68d1.
The [original source archive](../openzfs-review-2026-09-06/source.tar.gz) has SHA256
bd042e3e172d3194c5c5230bf427a54acaf8718f9981789ddd81ad18e8ab46a8.
Original source files compare unchanged after building; see source-comparison.json.
Upstream licenses/notices remain in the retained source. fixture.c is the unchanged
BSD-2-Clause owned-file producer fixture, not a production filesystem service.

Cross-tool image ID:
c48ba36c2b92494aa7ebfb957cce38a26792507e26ed24ae1fa010038da53c74.
Containerfile derives a separate multiarch cross-tool image from the preceding
arm64 tool image. Setup alone used package-network access; the final package
inventory and image metadata are retained. The image ID pins this local tool
closure; the recipe against mutable package repositories alone is not reproducible.
The image itself is not exported here. No host tools or prior images were replaced.

build.sh, owned.mk and mutant.mk retain the exact cross configure/compiler/link
commands. GCC is 14.2.0. Build libzpool, ztest and zdb after make gitrev, then the
unchanged fixture and intentional WRONG_EXPECTED variant. build-and-disks.tar.gz
contains the complete work directory (source, configuration, objects, executables,
compiler/package/emulator identities and build logs), both qualified disks and
separate trace disk. Original engine sources are not patched. The initial setup
and build succeeded; their raw logs lack individual structured UTC receipts.

qualify.py records the one-off experiment runner for this workspace and exact
local image. qualified/results.json contains the final frozen source inventory,
artifact hashes, exact argv, UTC start/end and exit codes. qualified/sources.tar.gz
retains the Aether runtime/build sources for those checks. Reproduction requires
the pinned local image, the extracted matching /work build products and new output
directories; this runner is not a portable dependency installer or native profile.

## Results

All qualified commands pass, including the expected exit-1 controls:

- Two deterministic 4096-byte payloads survive separate writable export/import
  cycles, with engine shutdown/reinitialization inside the same process.
- Independent-open advisory-lock acquisition and duplicate import reject.
- Existing file rejects with exact `new private file required`; disk hash unchanged.
- Wrong expected byte rejects specifically with `payload mismatch` on separate media.
- A fresh container mounts the positive disk read-only; zdb -bcc traverses checksums
  and reports no space-map leaks. The complete disk hash remains unchanged.
- Host tests (85 Python cases plus kernel/standards/workflow), format and frozen
  source/binary checks pass. Native QEMU regressions are unaffected by this host-only work.

Positive GNU time: elapsed 2.60 seconds, maximum RSS 74728 KiB. Both include QEMU
emulation overhead, not native service requirements. qemu-x86_64 10.0.11 uses
`-cpu qemu64 -L /` and the image's target amd64 loader/system libraries.

elf-layout.json and work/elf.txt distinguish file bytes from mapped memory:
the 18,608,720-byte executable has four load segments totaling 1,287 pages
(5,271,552 bytes), excluding shared libraries, heap and stacks. It is ET_DYN PIE
with an interpreter and dynamic system dependencies despite static engine linkage.
target-libraries.log records the loader's actual dependency resolution.
work/undefined.txt is raw archive nm output, not resolved platform import closure.

## Separate trace and limits

The additional diagnostic command exited 0 and emitted the positive marker:

```sh
podman run --rm --pull=never --network=none --read-only --cap-drop=all \
  --security-opt=no-new-privileges --memory=2g --pids-limit=512 \
  --tmpfs /tmp:rw,size=256m \
  --volume /Users/cam/DEV/Aether/zig-out/openzfs-x86-2026-09-06/work:/work:ro \
  --volume /Users/cam/DEV/Aether/zig-out/openzfs-x86-2026-09-06/trace-disk:/work/owned:rw \
  --entrypoint /bin/sh \
  c48ba36c2b92494aa7ebfb957cce38a26792507e26ed24ae1fa010038da53c74 \
  -c 'timeout 90 qemu-x86_64 -strace -cpu qemu64 -L / /work/owned-probe'
```

Raw guest-trace.log and trace-summary.json retain its observations. The summary
counts line-leading syscall starts only; thread output interleaves. It does not
prove complete syscall/import closure or peak live thread count. This auxiliary
trace lacks the qualification runner's structured UTC receipt and is not used as
an exact negative-test oracle or performance measurement.

Build and execution use restricted, disposable containers, no host devices or
/dev/zfs, and no network after setup. The private regular file and cooperating
advisory lock are the ownership boundary, not general noncooperating-writer
exclusion. The earlier generic ztest -E failure remains unchanged. Fresh-process
writable import, interrupted export, power loss, native allocator/threads and a
filesystem namespace remain unqualified. No kernel ABI or companion pin changed.

Next: bounded native memory/thread/runtime contracts, followed by the C platform
port and Rust service/namespace integration. SHA256SUMS covers every retained file
except itself; referenced preceding source/evidence has its own digest inventory.
