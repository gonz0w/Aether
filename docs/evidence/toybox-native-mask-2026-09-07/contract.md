# Native real toy_singleinit mask witness

Before code, 2026-09-07. Add a private native startup probe, not a public libc mask
API. Complete AECAT001 bootstrap and exact argc1/cat/env first; initialize private
single-thread process mask0077. umask exchanges only low0777 bits and returns the
previous value; before initialization it rejects, never a successful ENOSYS stub.
Verify masking/high bits and restoration before resetting observation counters.
Invoke unmodified upstream toy_singleinit on actual cat descriptor, without
NOFORK. Observe exactly two calls (0→old0077,0077→old0), restored0077 and
Toybox.old_umask0077, real UTF-8 locale result and stdout buffer from real allocator.
Stop before cat_main/callback/flush/exit integration. Three closes, empty input/
output/diagnostic, terminal0, backend stale denial and four native reclaims.
Wrong-old-mask and skipped-init controls return115/owner1501 before copy; no generic
panic acceptance. Reuse source-matched qualified empty-cat owner/backend artifacts
with recorded input identities; rebuild actual Toybox main with symbol rename only,
link probe + existing scoped transport + native memory adapter. No global musl
patch, kernel ABI/quota/pin/sibling modification or ambient file authority.

Test explicit process-local proposal only, not creation-mode enforcement, concurrency,
signals or userland acceptance. Pointer lifetimes remain synchronous; no new asm
or unsafe boundary. BSD-2-Clause probe; preserve upstream Toybox/musl terms.
Pin all artifacts/source/tools; freeze during QEMU. Retain every attempt. Native
probe cases, full prior command regression, connections/inherited, host/Zig/pin/
workflow and scoped Clang21 formatting. Record recipes/evidence/NATIVE-CAT/STATE.

Observed integration requirements: nonempty native TLS is mandatory, so observe a
real TLS sentinel before/after init. Enable existing bounded native-memory profile
explicitly; no-memory-grant must reject116 before Toybox. This intentionally composes
existing per-instance memory authority, not a quota increase or ambient creation.
Upstream includes use -isystem; new probe retains strict warnings.
