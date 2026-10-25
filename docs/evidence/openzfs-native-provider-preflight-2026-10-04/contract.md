# Granted provider and CPU-selection preflight

Before implementation, 2026-10-04; R1-03. Reuse the independently qualified guarded
SDK and verified OpenZFS headers. No kernel/ABI, existing SDK/pin, sibling, quota
or normal-image changes. Keep engine entry unavailable until its remaining real
providers, profile and admission are qualified.

Implement only private engine-adapter functions taking explicit grants: virtual
hrtime through existing pair-only0x2800e, and available pages through existing
memory0x22000. The former is exactly10,000,000 virtual nanoseconds per delivered
BSP interrupt, boot-local and coarse; it is not calibrated elapsed time/UTC or a
production POSIX clock. The latter is current unallocated caller-granted pages,
not host physical RAM, total engine budget or reserved heap capacity. Neither
function allocates, caches authority, creates capabilities or substitutes success
for a missing operation. Preserve raw negative errors. Userland owns production
SDK bindings; filesystem engine/service policy remains outside the kernel.

Native probe checks missing/foreign/future/wrong-type grants, reserved-input
denials, resource decrement/recovery for one mapped page, nondecreasing/quantized
virtual time and actual timer progress while user work runs. Keep the existing
memory/TLS/64-yield/output/terminal fixture checks. Deliberately freeze only the
private successful clock result: exact253 elapsed/progress rejection is required.
Disabled pair mode must reject251; it cannot become a passing clock.

Compile the unchanged upstream sys/simd.h and real supporting headers, not a
handwritten replacement. Test native OSXSAVE absence, SSE2 availability and denied
AVX/AVX2/AVX512 availability with qemu64 and an AVX-advertising QEMU max CPU, while
the kernel retains its x87/SSE-only context contract. A probe expecting AVX enabled
must reject254 at its named check. No accelerated algorithm or engine initialization
is invoked; selector evidence alone does not qualify all dispatchers/manual tunables,
interrupted crypto or SIMD algorithms. No XSAVE support is added for this witness.

Security/ownership: kernel remains the enforcing boundary for each current domain
grant. Caller-controlled numeric values cannot observe another owner's resources.
One-page map/unmap follows existing authority, range and zeroing semantics. No
secret, random output, path or capability value is logged. Existing unsupported
SDK clocks/resources/identity/entropy remain unsupported. Buffer ownership and
engine callbacks/concurrency are unchanged and still require later service review.

Simplicity SE-01–05: use two existing read operations plus upstream selectors,
instead of introducing a kernel POSIX server, global resource discovery or extended
CPU-state machinery. A direct trap wrapper is enough; no new clock registry or
provider framework. Added cost is private port preflight; none of the maintained
compatibility paths is removed. Real calibrated time/entropy/configuration/identity
and engine resource/thread admission remain explicit next work, not stubs.

Verify complete prior seals/archives, stage/header/tool inventories and selected
source bytes before copying. Keep all attempts, exact commands/times/ELF/ISO/logs;
freeze inputs throughout qualified runs. Full host/pin/workflow, scoped C/Python/
simplicity and exact target controls before retention. Preserve upstream notices.
Update STATE/ROADMAP/FEASIBILITY with results and next work. Private recipes are
evidence, not new maintained script entry points. Read back all new artifacts and
verified reused duplicates before only this turn's owned workspace is removed.

## Private OpenZFS time helper binding, before implementation

The original libspl sys/time.h discards clock/gettimeofday failures in all four
inline helpers. Guarded libc alone cannot make those callers safe. Derive a private
copy from sealed original bytes, retaining CDDL notices and an exact unified diff.
Bind only gethrtime to the explicit bootstrap thread grant and declared virtual
clock. A negative provider result terminates125 before returning time. The three
wall-time helpers terminate125 unconditionally while real wall time is absent;
no fake epoch or zero-filled timestamp. This copy is private evidence, not a
public SDK clock or complete engine port. Public guarded libc and original upstream
headers remain byte-identical.

Compile actual helper consumers with this private header first in the existing
include chain. Exercise advancing virtual gethrtime on qemu64/max, invalid grant,
disabled pair, all three wall helpers and frozen-clock progress controls. Keep
native fixtures and exact terminal/panic oracles. A denied-call mutation changes
only the private selected grant for testing. No full engine invocation, resource
reservation, new syscall or production time claim. This removes one unsafe caller
pattern without creating an ambient time service or broader compatibility layer.
