# First persistent block transport

R1-03 pre-implementation scope, 2026-09-06: a BSP-only polling driver for QEMU's
transitional virtio-blk PCI I/O transport. Follow the legacy interface described
in [OASIS Virtio 1.2](https://docs.oasis-open.org/virtio/virtio/v1.2/virtio-v1.2.html),
sections 2.7.2, 4.1.4.10 and 5.2. No upstream source or new runtime dependency.

This hardware bring-up is opt-in with -Dblock-test=write or verify, -Dsmp=false,
and no native-C image. It never runs in normal boot. The harness creates its own
raw disk; no path to an existing disk is accepted. Sector 7 is the sole write
scope. Sector 8 and all other bytes are canaries checked by the host. The driver
requires FLUSH support and a writable device; missing, duplicate, unsupported or
read-only devices fail before writes. One outstanding 512-byte request is allowed.

The BSP owns PCI configuration, descriptors and fixed DMA memory until VM teardown.
No task or service receives device authority in this slice. Before exposing an
ABI, add a caller-bound block grant and validate sector scope/direction at the
kernel boundary; user pointers must never become device descriptors. Filesystem
policy remains behind a Rust service and a mature engine. No filesystem or durable
package-operation claim follows from this hardware experiment.

Unsafe boundary: physical addresses derive only from the bootloader's contiguous
kernel image mapping. Queue/header/data/status are static kernel-owned backing,
not stack/user/reclaimable memory. x86 memory barriers order descriptor publication,
available indices, notification and completion reads. Polls have a fixed budget;
timeout or invalid completion halts and retains all DMA backing rather than
reusing it. No interrupt handler, allocator, cross-core access or concurrent caller.
No IOMMU or protection against a malicious device is claimed.

Acceptance: read seeded data, reject out-of-range requests before submission,
write one sector, issue FLUSH and verify data after a fresh QEMU process boots the
same disk. Host checks the complete image against the exact expected result.
Exercise ring wrap, absent device, read-only device and corrupted input. Preserve
all attempts, source/tool/artifact identities and default boot regressions. This
proves persistence across a VM restart on the test host, not power-loss durability.
The filesystem engine and snapshot/rollback extent remain undecided implementation
work. Run `python3 scripts/block_smoke.py`; see STATE for executable evidence.

Producer validation: seven disk cases pass, including duplicate devices and an
unsupported queue size. A wrong-data mutation with a successful guest marker is
rejected by the host. [Retained evidence](evidence/block-transport-2026-09-06/README.md)
records all attempts and default/console regressions. The block-only build omits
unused protection interrupt assembly; no user execution or interrupts are enabled.

Limits: bus zero only, legacy I/O BAR, MSI-X disabled, power-of-two queue size
4..256, 12 KiB queue backing, 512-byte data buffer, 16-byte header and status byte.
Timeout/completion-corruption and missing-FLUSH injection remain pending. QEMU
shutdown can flush host caches, so the reboot witness is not an independent proof
of flush efficacy or power-loss durability. No full Distribution DS acceptance.

[Native block v1](NATIVE-BLOCK.md) now exposes this transport through an opt-in,
caller-bound one-sector grant with copied buffers and reduced-rights handoff.
The original hardware-only mode and its limits remain unchanged.
