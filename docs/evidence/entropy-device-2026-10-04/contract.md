# Bounded entropy transport requirement (before implementation)

Aether needs a real entropy source before enabling OpenZFS startup. This step
qualifies only an opt-in BSP-owned legacy virtio-rng transport in QEMU11.1.1.
It exposes no syscall, device grant or service API. The normal boot path and
released standards pins remain unchanged. No sibling changes are required.

One authoritative BSP owns a statically reserved 12KiB split queue and 256-byte
DMA buffer. Interrupts remain disabled. Exactly one bus-zero legacy entropy
function is accepted; absent, duplicate, modern-only, invalid BAR/capability,
queue geometry or device state fails explicitly. Only one device-writable
buffer is outstanding. Negotiate no optional features. Bound polling and
require exactly one used-index advance, descriptor0, and written length1 through
requested length. Partial completions must fill only their written prefix and
advance until the exact kernel-owned destination is filled. Volatile zeroing
clears completed DMA bytes after copying; unknown DMA remains reserved until VM
teardown. No backing is freed on timeout or malformed completion. No source
bytes, digests, pointers or authority values are emitted.

Forbidden: boot seeds, fixed fallback bytes, trusting a full-buffer write,
unbounded polling, untrusted DMA pointers, accepting malformed completions,
SMP/global caller access, inferred entropy quality or physical-hardware/IOMMU
isolation. Host /dev/urandom is the explicitly selected QEMU backend; its trust
and strength are external assumptions. Real userland capability binding, failure
semantics, secure pool health/reseed policy and service restart remain subsequent
work before OpenZFS can consume this transport.

Tests: actual-device 300 draws, rate-limited partial fills, absent/duplicate/
modern-only devices, injected completion head/length/index/timeout rejection;
portable validator tests include u16 sequence wrap and zero/oversized lengths.
An intentionally omitted length check must fail the named length oracle.
Build must reject invalid/mixed modes and every lab mode in a release-designated
artifact. Run full host checks, existing M4 and block regressions after the shared
boot-entry change; freeze all input bytes and preserve all attempts. Bind tool,
source, firmware, commands/times, ISO and logs in retained evidence; verify all
archive members before deleting only verified owned temporary duplicates.

Unsafe obligations: port I/O accesses only validated legacy I/O BARs; physical
translation applies only to static kernel image storage. Queue addresses and
lengths are bounded. MFENCE and volatile indices/used entries establish x86
publication/observation in the documented coherent QEMU environment. No locks
are needed under BSP-only CLI ownership. A malicious DMA device is outside this
POC isolation boundary; capability exposure/real hardware triggers IOMMU and
lifetime review before broader use.

Simplicity SE-01–SE-05: the simpler RDRAND-only option is insufficient for the
baseline qemu64 target and would introduce CPU-specific entropy trust. Borrow
only the existing block driver's bounded legacy split-ring pattern and OASIS
Virtio1.2 entropy rules. Keep a separate cohesive transport; do not create a PCI
framework, registry or policy service without a consumer requirement. No obsolete
path is removed now. The added costs are one isolated driver, small completion
validator and test harness. Reference/output/workflow/STATE/ROADMAP updates cover
scope and follow-up. New original work is BSD-2-Clause; no runtime dependency or
standards release is imported. Fixed ASCII proof markers extend the existing
experimental Experience exception, without product presentation claims.
