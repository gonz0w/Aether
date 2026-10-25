# BSP entropy transport qualification — 2026-10-04

The [before-code contract](contract.md) and [reference](../../ENTROPY-DEVICE.md)
define scope: isolated QEMU BSP hardware transport, not a userland entropy API.

Attempt1:9 device cases and11 build guards pass; stalled-backend setup exhausts
firmware RNG quota before kernel boot, external30-second watchdog fails. All
sources/logs/results retained. [Triage](triage.md) explains the corrected quota.
Attempt2: all11 cases and11 guards pass, including300 draws,12 actual partial-fill
samples, exact head/length/index and injected timeout; actual backend exhaustion
reaches the kernel timeout after readiness. The deliberately broken length check
reaches success and is correctly rejected by the expected-length panic oracle.
The driver never submits user pointers or emits entropy bytes/digests. Volatile
clear checks pass; there is no statistical quality/health/security certification.

Full host checks pass137 Python cases plus Zig/Rust/offline pins/workflow, including
four new oracle counterexample tests and portable completion/sequence-wrap tests.
All7 existing block cases pass. First M4 attempt fails because the sandbox prevents
its private local QMP socket bind; retained authorized retry passes all7 cases.
The prior AES-NI/public-dispatch packet remains sealed and immutable. Every run
uses owned VMs/output roots, external watchdogs and checked termination. No sibling,
public SDK/ABI, normal image selection or standards pin change is made.

New original Zig/Python is BSD-2-Clause. No upstream runtime code/dependency is
imported. OASIS Virtio1.2 rules and existing block-driver split-ring mechanics are
borrowed deliberately. Port I/O, coherent DMA publication and static pointer/queue
bounds are documented in the contract. Evidence hashes observe inputs; they do not
provide malicious-host/device attestation. A physical device can DMA outside these
buffers without an IOMMU; broader hardware/caller use requires that review.

Reproduce with pinned setup: `python3 scripts/entropy_smoke.py`, `zig build test
--cache-dir .zig-cache --global-cache-dir .zig-cache/global`, `python3
scripts/block_smoke.py`, `python3 scripts/regression.py` (private QMP socket must
be permitted). Per-build180 seconds, VM30 seconds and teardown3 seconds. No
external network or persistent disk is used. All attempts, commands/UTC times,
source snapshots, source/tool/firmware/artifact identities, raw logs and final
checks are retained in artifacts.tar.gz and the readback receipt. Only verified
owned duplicates are removed after all members are checked.

Next: capability-bound native draw/close with complete buffer, reserved-field,
quota, owner/lifetime rejection before DMA, followed by a checked engine consumer.
Recovery and health policy remain outside the minimal transport. Engine resource/
thread admission and full startup/fini/restart still precede persistent filesystem.
