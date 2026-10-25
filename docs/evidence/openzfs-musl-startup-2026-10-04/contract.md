# Private OpenZFS musl startup audit

Before-code scope, 2026-10-04; R1-03. Attempt the retained OpenZFS2.4.4
libzpool startup closure with the pinned x86_64 native musl SDK. Object generation
and a strict static link are build evidence only. Record actual compiler/linker
barriers separately from absent native runtime operations. No runnable engine,
filesystem acceptance, numeric capacity proposal or companion acceptance is claimed.

Use a fresh owned output tree; verify the original source archive, selected host
trial inputs, SDK receipt/archive/header inventory and compiler/linker identities
before consumption and again after builds. Preserve all commands, timestamps,
attempts and diagnostics. Existing Linux configuration is an explicitly labelled
comparison input, not native feature detection. Private adaptations must identify
exact differences and retain upstream CDDL notices. No host headers or Linux/glibc
archives may enter native objects; no successful platform stubs, fake entropy,
file/flush operations, no-op locks or silent synchronous task queues.

Aether owns this private port audit, userland owns the SDK and production libc,
and a future Rust filesystem service owns pool policy. Do not edit siblings,
kernel/runtime code, grants, quotas, pins or historical packets. No devices,
writable pools or engine execution are part of this build audit. Unknown imports
remain named missing work. Any eventual adapter must preserve scoped I/O authority,
pointer/allocator ownership, same-address-space synchronization, thread stop/reap,
clock identity and honest uncertain durability outcomes before native execution.

Tests: isolated native compilation and strict unresolved-symbol link; object
architecture/import inspection; SDK-export comparison explicitly separated from
native syscall support; reject accidental host-header leakage and an unreviewed
import; full host/pin/workflow checks. No unrelated QEMU run is justified for this
private build-only experiment. Keep resource measurements and runtime qualification
open if no executable can be produced. Freeze sources during qualified checks.

Simplicity: the simpler alternative is source review alone, but it cannot reveal
the actual musl compile/link closure. Retain the proven upstream engine and selected
separate queue policies; do not add a parallel filesystem or kernel compatibility
layer to get a successful link. This audit adds no active product mechanism and
can remove unsupported assumptions from the next runtime proposal. Foundations
O-01–05, I-01/03/05/08, E-01–08 and the local simplicity process apply. Documentation
impact is evidence, OPENZFS-FEASIBILITY and STATE; private recipes are not maintained
developer entry points. BSD-2-Clause applies only to original audit tooling.

After the first14-file comparison: kernel.c uses no zlib declarations and
abd_os.c uses no znode declarations. Try private copies with only those unused
includes removed, preserving the originals and exact diffs. This removes no
runtime operation or successful fallback. Compile the complete declared libzpool
C source list from the retained generated Makefile (parse data, do not run make).
Attempt a strict static startup link from generated native objects and native musl
only. Incomplete dependencies must fail; a partial relocatable link is explicitly
labelled partial. Also compile the exact selected queue/ARC/file trial copies,
keeping their observer imports visible rather than inventing implementations.

The complete178-source comparison identifies33 compile barriers. A second private
header comparison will supply the actual pinned compiler's cpuid.h and the retained
generated include/zfs_gitrev.h, and remove only linux/fs.h from a private copy of
the userspace sys/vfs.h wrapper while retaining the real musl sys/statfs.h. This
does not define Linux filesystem ioctls or implement VFS operations; a genuine
use of a missing declaration must still fail. Recompile the failed sources, link
only successful objects and keep missing gzip/zlib and transitive libraries open.
The inherited Linux feature macros are still comparison inputs: AVX/XSAVE and
hardware capability selection require separate native review before execution.
