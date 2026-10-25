# Native entropy binding (before implementation)

Requirement: let bounded native workers consume the qualified real QEMU entropy
transport with explicit per-domain authority. No SDK/sibling/public ABI adoption.
Add one opt-in native-entropy flag requiring the existing memory/thread profile,
AENATC01 or AENSUP01 only (no launch/copy/exec/SMP composition). The boot owner
chooses this grant explicitly; only loaded workers get an auxv0xa002 selector bound
to exact slot/generation. It is not global authority. Threads in that domain share
its4KiB lifetime byte quota and close state. No move/regrant/query API is needed.

Private int0x81 draw0x2b000: RDI grant, RSI writable destination, RDX1–256 bytes,
R10/R8/R9 zero. Success exact count; close0x2b001 has remaining fields zero,
success0 permanently closes this lifetime. Deny disabled route -38; foreign/stale/
unbound -13, closed -9, invalid/reserved -22, invalid/read-only/overflow span -14,
quota exhaustion -28. Validate authority/fields/full span/quota before DMA or any
caller-buffer write; failed preflight preserves bytes/quota. One BSP operation
runs IF clear, through static device buffer and bounded copied stack buffer; then
clear the stack copy. No unmap/stop/reuse overlaps synchronous completion. Hardware
failure halts with DMA retained, never succeeds with fallback or partial bytes.
Termination/reclaim invalidates the binding; fresh explicit-profile admissions
receive a new generation selector, never the old one. Scope is Debug QEMU transport
and authority, not quality/reseed, side-channel or general scheduler-latency approval.

Tests: actual strict SDK intake, old TLS/memory/thread/yield fixture retained;
real exact boundary draws, full-span/read-only/unmapped/overflow/reserved rejection,
foreign and old-generation selectors, quota preservation/exhaustion, close and
disabled route. Omitted quota enforcement must fail exact terminal oracle. Portable
core models cover permanent close, generation mismatch and quota exhaustion.
Full host, entropy-device and M4 regressions, scoped format/pins/source freeze and
archive readback before only owned verified duplicate cleanup. New original code
BSD-2-Clause. Guarded SDK stays sealed; no public getentropy replacement yet.

Simplicity: use a single grant record in the authoritative per-domain State and
existing auxv/trap/byte-validation paths; a daemon/IPC framework is unnecessary
for this bounded provider. Borrow synchronous copied block transport, but add no
transfer/rights lattice without a requirement. Added cost: one grant core and two
private trap operations. Complex entropy health/reseed policy stays outside kernel.
Remove no unrelated mechanism. Broader service/copy/exec/hardware use triggers
new ownership, admission, recovery, IOMMU and latency review before adoption.
