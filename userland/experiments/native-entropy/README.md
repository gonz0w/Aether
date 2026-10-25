# Explicit private native entropy adapter

UL-003/015/081. `entropy.c` binds Aether's pinned private per-domain entropy grant.
Callers supply an actual owner-issued selector; names, PID or metadata convey no
native authority. This opt-in experiment does not interpose POSIX getentropy,
change libc/default SDK pins or acquire authority from auxv on the caller's behalf.

`aether_entropy_draw(grant, buffer, count)` performs one native draw with all
reserved fields zero. Success returns the exact requested count (1–256); known
negative errno values remain negative, while unexpected results return-EIO.
`aether_entropy_close(grant)` closes that supplied grant permanently; success0,
known negative errors otherwise. Neither function changes POSIX errno, retries,
reopens or falls back to bytes from another source. Buffer/span validation and
4096-byte lifetime quota are enforced by the kernel, not caller metadata.

[Independent qualification](../../docs/evidence/native-entropy-consumer-2026-10-05/README.md)
source-builds this adapter/probe against sealed inputs and runs five fresh native
cases: draw, disabled API, actual kernel quota mutant, private false-success adapter
and real supervised replacement. Protected-page/foreign/stale/size/span failures,
canaries, exact quota/close and preserved errno are checked. Returning counts does
not establish statistical entropy quality or certify the QEMU host-random backend.

Reproduction uses the packet's prepare/build/run/check recipes in a fresh owned
output/packet location with the recorded producer/SDK/tool seals. Do not rerun into
sealed evidence. Guest/host builds, links, native execution and production adoption
are separate evidence. No direct real-prefix installation or ambient device path
is provided. Physical entropy/IOMMU, health/reseed, service latency, copy/exec,
public SDK/reader review and complete shell/storage integration remain open.
