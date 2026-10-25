# Linux reference UAPI export (UL-068)

Contributor experiment, 2026-09-06. Linux 6.18.49 x86 userspace headers supplement
the existing musl reference SDK through a separate include directory. They do not
define Aether's ABI or add Linux kernel services to Aether. Source authentication,
security review and native compatibility remain separate work.

[Source pins](source.lock.json) bind the official Linux and GNU make archives
before extraction. GNU make 4.4.1 is built locally using pinned Clang 21.1.8 as a
host helper; the host's make 3.81 is used only to bootstrap it. GNU sed, rsync,
shell and awk identities are recorded in [host tools](host-tools.lock.json).
No helper is installed into a host prefix. Host SDK/path/flags, commands, helper
bytes and exported header inventory are retained with the build.

The standard upstream `headers_install ARCH=x86` path builds fixdep/unifdef,
generates syscall/asm/version headers, sanitizes and exports UAPI headers. The
[upstream documentation](https://www.kernel.org/doc/html/latest/kbuild/headers_install.html)
defines this export boundary. Linux UAPI headers retain their per-file licenses,
including applicable Linux-syscall-note exceptions. GNU make retains its GPL
terms. Our BSD-2-Clause code does not relicense either dependency.

## Filesystem and failed attempts

The macOS checkout is case-insensitive. Linux 6.18.49 has thirteen source-file
pairs differing only in case; extracting directly here loses distinct bytes.
The initial 1,020-header export is therefore rejected, despite upstream make
returning zero. It must not be used as an SDK. The corrected build requires a
case-sensitive work root and verifies every extracted regular file against its
archive; its 1,028 exported headers retain eight additional case-distinct names.
The other source collisions are outside the exported header inventory.

An earlier 6.6.156 attempt failed because its x86 header target also builds
archscripts/relocs and requires unavailable macOS host ELF headers. Linux 6.18's
upstream export no longer depends on archscripts. Both old attempts and the
original 6.6 pin remain evidence; no upstream build rule or header was patched.
An initial disk-image command used the unsupported filesystem alias APFSX; the
successful command uses the documented name `Case-sensitive APFS`.

Unifdef legitimately leaves compound conditions containing __KERNEL__ where
other macros remain unknown. Five headers contain such conditions (asm-generic
fcntl/swab, linux input/stat and sound asound). A lexical absence test is not
an export-correctness oracle. Standalone kernel-only guards are checked separately;
full independent semantic review remains pending. The plan records this refinement.

## Reproduction

The private case-sensitive data image is `build/aether-uapi.sparseimage`. Mount it
at the same path before rebuilding consumers; do not extract its header archive
onto a case-insensitive filesystem. From this checkout, after separately acquiring
the exact archives/tools:

```
hdiutil attach -nobrowse -mountpoint "$PWD/build/uapi-volume" build/aether-uapi.sparseimage
python3 -B experiments/linux-uapi/build.py --work-root build/uapi-volume
python3 -B experiments/tr-stty-reference/build-gnu.py --uapi UAPI_BUILD_DIRECTORY
python3 -B experiments/tr-stty-reference/test-gnu.py GNU_BUILD_DIRECTORY
python3 -B docs/quality/check.py
hdiutil detach "$PWD/build/uapi-volume"
```

Substitute each printed build directory. Image creation for a new checkout:
`hdiutil create -size 4g -type SPARSE -fs 'Case-sensitive APFS' -volname AetherUAPI build/aether-uapi.sparseimage`,
then create `build/uapi-volume` before attaching. These are data-image operations,
not formatting the host disk. Reattachment does not repin contents: the consumer
checks the export inventory and extraction receipt each time. Updating headers
requires a new source pin/view and fresh consumer build/test evidence.

See [PLAN.md](PLAN.md) for bounds, expected rejections and scope. This is not a
reproducible-bit-for-bit build claim or a full host dependency audit. The retained
image is a development artifact; release packaging remains UL-012/016.

## Accepted reference scope

The corrected export verifies 91,515 extracted regular files (Linux and GNU make)
and 1,028 exported headers. Empty exports, altered headers, the earlier invalid
export and case-insensitive work roots are rejected. The original musl SDK still
matches its complete pinned inventory. GNU tr/stty builds and all seventeen
Linux-QEMU fixtures pass using this view. UL-068 is complete within this reference
scope; UL-066/008/012/016 and independent quality reviews retain broader work.

[Evidence](../../docs/evidence/linux-uapi-2026-09-06/summary.json) includes original
archives, source verification inventory, helper identities, export.tar.gz preserving
case-distinct names, rejected attempts and controls. The private image is retained
under build/ and detached after validation; reattach before rebuilding consumers.
