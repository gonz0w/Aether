# Owned-file writable OpenZFS qualification — 2026-09-06

[Contract and result](../../OPENZFS-FEASIBILITY.md#owned-file-result--2026-09-06).
This Linux/arm64 C fixture performs real libzpool/DMU I/O on a newly created private
256-MiB regular file. It does not accept an existing device, foreign configuration
or pool-discovery path. It does not implement a filesystem namespace or native
Rust service. Original source is BSD-2-Clause; linked upstream terms remain intact.

## Inputs and results

Uses the unchanged OpenZFS commit and Linux image/build products recorded in
[the supported-host baseline](../openzfs-host-2026-09-06/README.md). Image ID:
ef2164012fa1c3a315d34091c6ed8951d3eac37c7192d5adbb5bf4c1a30d916f.
`owned.mk` uses the configured upstream compiler/link flags and static engine
libraries. Host system libraries remain dynamic. `host-owned.c` is the final
source; the good and intentional wrong-byte binaries/objects are retained.

`qualified/results.json` binds source and binary hashes, the full Aether source
inventory, image ID, exact commands, UTC intervals and expected exits. All final
checks pass, including intentional exit-1 controls:

- Positive: two distinct 4096-byte patterns survive two sync/export/engine-shutdown/
  reinitialize/writable-import cycles. Duplicate imports reject with EEXIST.
- Independent-open exclusive-lock acquisition fails while the original file
  descriptor holds the lock. This is a cooperating-owner advisory-lock witness.
- Existing file: exact `new private file required` failure, with unchanged disk hash.
- Wrong expected byte: exact `payload mismatch` after import on separate media.
  Generic panic, startup failure, timeout or unrelated nonzero status cannot pass.
- Fresh container, read-only disk mount: zdb checksum/space-map traversal passes,
  with no leaks and unchanged complete disk hash.
- Host/standards/workflow (85 Python cases plus kernel checks), C formatting and
  source/binary drift checks pass. No Aether runtime change required a QEMU rerun.

Positive final GNU time maximum RSS: 23248 KiB; initial success: 23472 KiB.
These small Linux/arm64 observations are not x86_64 requirements, ARC reservations,
stack high-water or an established minimal filesystem budget.

## All attempts and triage

`build-1.log` and `source-attempt-1.c` retain compile errors from mismatched C
prototypes/constants. `build-2.log` and `source-attempt-2.c` retain the partial
correction. After consulting the pinned headers, build-3 succeeds without warnings:
DMU_TX_WAIT, DMU_OT_PLAIN_OTHER, explicit write flags, DSL-pool sync argument and
correct nvlist pointer qualifiers are used. No upstream source was patched.

Initial positive, existing-path, wrong-byte and zdb logs are retained. The final
qualified run repeats on new private files with complete command timestamps and
frozen-input checks. `attempts.tar.gz` includes all private disk bytes and raw
attempt inputs/logs; no failed attempt was discarded. Earlier build attempts have
raw commands/logs/source snapshots but lack individual structured UTC receipts;
only the final qualification has that complete per-command record.

`qualify.py` is the retained one-off experiment runner. It requires the exact local
image and matching prior build workspace, fresh output paths and Podman access;
its captured invocations are not a portable dependency installer. All containers
use no network, a read-only root, dropped capabilities, no-new-privileges, 2-GiB
memory/512-PID limits, a private /tmp and only the owned file directory writable
during qualification. No host devices or /dev/zfs are exposed. Commands have both
container and host watchdogs. Successful/failed container exits release host file
locks; no unrelated process, VM or service was modified.

## Boundaries and next work

The previous generic ztest -E discovery failure remains unchanged. This experiment
uses only spa_export's own configuration in host memory, rather than suppressing
active-pool checks. Packed configuration uses this pinned host allocator and no
engine object pointer survives kernel_fini. Object-set holds end before export.

Writable cycles reinitialize the engine inside one process. Independent read-only
verification is a fresh process/container; fresh-process writable import, power
loss and interrupted export/recovery are not qualified. Advisory locking cannot
exclude noncooperating writers or a mounted host kernel pool; exclusive private
file creation/ownership is essential to this fixture. Fatal assertion paths leave
images for analysis and rely on process exit, not a production recovery protocol.

Next: x86_64 engine/fixture build and resource/interface measurement before native
memory/thread contracts. Namespace porting, Rust service integration, consumer
review and the assembled shell/package release remain open. SHA256SUMS covers
all retained files except itself; the earlier engine build is referenced separately.
