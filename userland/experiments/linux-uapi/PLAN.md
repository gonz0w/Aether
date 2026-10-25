# UL-068 Linux-reference UAPI export plan

2026-09-06. Export x86 userspace headers from Linux 6.6.156 with its own
headers_install rules. Build GNU make 4.4.1 as a private host helper with pinned
Clang because the host make is 3.81. Pin both HTTPS source archives before
extraction. This is a Linux reference dependency, not Aether ABI or kernel code
adoption. Preserve upstream UAPI licensing/exception and all notices.

Apply E-01–08, CD/CP, TD/TE and DP. All source/helper/build/export files remain in
private build roots. No installation into host prefixes or change to the prior
musl SDK. Verify prior compiler/tool/wrapper/SDK identities. Expose exported headers
as a separate include root after musl headers; do not overwrite libc headers.
Use Python 3.12+, bounded 240-second build process groups and retained logs.
Record host SDK and helper identity; host tool transitive closure is not fully
hermetic. Source authentication and independent review remain UL-016/061–063.

Acceptance: exact header inventory, x86 generated asm headers/version, no standalone
kernel-only guards (review residual compound conditions), clean export command, preserved musl baseline; compile
GNU tr/stty against this separate view and execute prepared Linux-QEMU cases.
Reject changed export bytes and empty export. Missing tests remain incomplete.
Record all failures and exact changes before marking complete. Run local quality
gate; no unrelated native suite is affected. Header updates/removal require a
new pin/view and rerun of consuming builds; no automatic upstream update.

The 6.6.156 attempt failed before export: headers depends on archscripts, which
builds x86 relocs and requires host elf.h/byteswap/endian interfaces unavailable
on macOS. The current 6.18 longterm export removes archscripts from this dependency.
Select 6.18.49 as a new explicit input, retain the original pin/attempt, and export
using unchanged upstream rules. Header age does not guarantee older-runtime
compatibility; Linux execution must still exercise consuming commands.

The macOS checkout is case-insensitive; source inspection found 13 case-fold
collisions in Linux 6.18.49. The apparent 1020-file export is invalid and must not
be consumed. Use a private case-sensitive APFS data image under build/, require a
case-sensitivity probe before extraction, and compare every extracted regular
file to its archive bytes. Keep source and exported headers on that volume.
The image is a local development prerequisite, not a target disk or installation.
Record mount identity; retain the image for reproducible input use, with explicit
unmount/re-attach instructions. No host/system filesystem formatting occurs.
