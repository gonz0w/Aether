# Experimental entropy device transport

This opt-in BSP-only QEMU experiment is a prerequisite for a real entropy
provider. It is not available to native callers or OpenZFS yet. Normal boot and
released ABI/pins are preserved. No entropy quality, hardware support or malicious
DMA isolation is claimed. The host /dev/urandom backend is an explicit trust
assumption; passing transport tests is not randomness certification.

The driver borrows only the bounded legacy split-queue pattern in BLOCK-DEVICE.
[OASIS Virtio1.2 section5.4](https://docs.oasis-open.org/virtio/virtio/v1.2/virtio-v1.2.html#x1-3050004)
requires device-writable buffers and checking the actual written length; partial
completion is permitted. Exactly one bus-zero legacy entropy device is required.
Queue0 has1–256 power-of-two entries, no optional features, no interrupt delivery
and one outstanding descriptor. The BSP owns12KiB queue storage and256-byte DMA
storage until VM teardown. Bounded polling, exact index/head/length validation,
partial fills and volatile clearing protect the supported coherent QEMU path.
Kernel-owned destinations are never DMA destinations. Malformed completion or
timeout panics with storage retained; no backing is recycled under unknown DMA.

```sh
python3 scripts/entropy_smoke.py
zig test kernel/entropy_completion.zig --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The suite builds isolated modes with `-Dsmp=false -Dentropy-test=<mode>`; rejects
mixed/unknown/release-designated modes before build; checks300 full draws and12
rate-limited partial fills; and verifies absent/duplicate/modern-only, malformed
head/length/index, injected timeout and actual stalled-backend rejection. A broken
length validator must be rejected by the exact panic oracle. Each owned VM has a
30-second watchdog and3-second teardown bound; forced teardown fails. No random
bytes/digests or addresses are logged. All source/tool/firmware/artifact identities,
commands, UTC times, logs and failed attempts are retained under zig-out/entropy-*.
The fixed ASCII readiness/partial/PASS markers are private machine oracles.

Before consumer binding: define explicit device/provider capability, caller
buffer validation, quotas, lifetime/failure/partial-progress contracts and service
placement. Broader callers/SMP/physical hardware require ownership, IOMMU and
restart review. Entropy health/reseed policy belongs outside this transport. No
fallback seed, RDRAND-only assumption or ambient syscall is introduced. See
STATE/ROADMAP for progress and the next executable consumer experiment.
