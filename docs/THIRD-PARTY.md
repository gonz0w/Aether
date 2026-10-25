# Third-party binary inventory

Owner comparison experiment,2026-10-22: the explicit
`sys-init/scripts/check-broker-init.py --compact-compare` selection compiles only
unchanged musl1.2.6 `src/string/memcmp.c` from the already pinned SDK archive. Exact
source, three headers and full MIT COPYRIGHT are verified before use; no libc
archive or dynamic dependency is linked. The COPYRIGHT accompanies the temporary
object; any future shipped owner must retain it in the image/package notice set.
See [dependency review](../sys-init/docs/decisions/0208-owner-compare-fit.md) and
[measurements](evidence/fork-publication-2026-10-22/README.md). No new distributed
binary, BSD relicensing, runtime admission or general clearance is claimed.

Private maintained service-runtime intake,2026-10-06: the opt-in supplement in
`.deps/native-service-runtime-v2` is userland-owned original BSD-2-Clause backend
and build code plus selected musl1.2.6 units. Its source/patch/tool inventory is
retained in `runtime/build.json`, original LICENSE in `source/LICENSE`, and musl
COPYRIGHT/source archive remain in the unchanged guarded `.deps/native-current/sdk`.
Seal/source rebuild and actual link-map scope are in the
[compact intake](evidence/service-runtime-intake-2026-10-06.json). Do not relicense
upstream musl, silently promote this private candidate or treat it as a new
default image audit/redistribution clearance. No NVIDIA/firmware dependency added.

Audit date: 2026-09-05. This is an Aether implementation inventory under the
[shared licensing policy](../../Aether-standards/docs/LICENSING.md), not a new
cross-project standard or a completed redistribution clearance.

Inspected the current default `zig-out/aether.iso`, its kernel and four installed
Rust modules, the installed Zig 0.16.0 and Rust 1.98.0 toolchains, and one separately
identified native musl artifact. Exact hashes, paths, maps, upstream notices and
source-change records are retained in
[evidence](evidence/third-party-2026-09-05/inventory.json). Generated outputs can
change; these findings apply to those hashes, not every subsequent build.

## Confirmed default image contents

The extracted ISO has eleven ordinary files: kernel, protection/display/lifecycle/
SMP-supervisor modules, Limine EFI executable and boot image, Limine configuration,
El Torito catalog, and the Aether/Limine license files. The Limine executable, boot
image and notice match the verified local dependency bytes. No musl native-C
module, OVMF image, NVIDIA component, OpenZFS or DTrace payload appears in this
image inventory. This is file-level inventory, not an inference from filenames
that linked code has no upstream provenance.

| Component | Evidence of inclusion | Terms and current notice status |
| --- | --- | --- |
| Original Aether work | Kernel and four modules | BSD-2-Clause; `/boot/LICENSE-Aether.txt` is present |
| Limine 12.7.0 | Both boot artifacts match `.deps` inputs | BSD-2-Clause; full notice present at `/boot/LICENSE-Limine.txt` |
| Limine protocol definitions | `kernel/limine.zig` and pinned protocol provenance in boot docs | 0BSD; notice retained in `boot/LICENSE-Limine-Protocol.txt`; not separately included in ISO |
| Zig standard/runtime code | Defined kernel symbols include `debug.FullPanic`, compiler runtime operations and memory/division helpers | Installed Zig's MIT license retained in audit evidence; **missing from ISO** |
| Musl-derived Zig math | Eighteen linked compiler-runtime module names match installed source files identifying musl provenance | Requires provenance/notice closure beyond Zig's top-level MIT text; **not covered by the current ISO notices** |
| Rust library contributions | All four map-enabled rebuilds match installed raw/enveloped bytes exactly | Maps show no separately linked `.rlib` members; this does not exclude inlined `core` code. Rust default is Apache-2.0 OR MIT with exceptions; **no Rust notice bundle currently shipped** |

The kernel contains math runtime symbols even though the fixture is not intended
to use floating-point operations. Reachability or intended use is not a reason to
ignore code present in a distributed binary. This audit does not remove runtime
code or change kernel behavior.

For the Rust modules, the maps show contribution from the fixture's codegen object
and linker-generated data. They are evidence against a separately linked archive
member in these exact builds, not a complete source-level attribution proof.
The installed `COPYRIGHT-library.html` describes Rust's default license and
per-file exceptions; its hash/path is recorded. Do not ship that entire toolchain
inventory as if every listed dependency were part of Aether. Close the actual
inlined-source scope or supply a clearly scoped conservative notice set.

## Optional native musl image

The separately inspected artifact is Aether-userland's
`build/native-c-5olokhku/native-c.bin`, variant **io**. Companion work has progressed
beyond the earlier startup-only evidence; this audit does not substitute the new
artifact for that historical target witness. Its envelope hash matches its own
build receipt, and bytes after the 40-byte envelope match the recorded
`startup.elf`. This artifact is not in the audited default ISO. No native execution
was performed in this audit.

The pinned musl 1.2.6 source archive hash is
`d585fd3b613c66151fc3249e8ed44f77020cb5e6c1e635a616d3f9f82460512a`.
The local archive was rehashed, and every upstream regular file was compared with
the source tree used for the probe. Eight files differ: the x86_64 syscall header,
mallocng allocation code, and six x86_64 process/signal/thread assembly files.
The record retains paths and before/after hashes; the strict allocator patch
receipt alone is not the complete modification inventory.

The linked libc archive matches its build receipt. The retained map identifies
22 libc archive members plus CRT objects, the probe and native-I/O adapter.
No compiler-runtime archive is shown in that map; the build receipt also records
that missing 128-bit helpers deliberately fail. This finding applies to this
probe, not every native program or later compiler-runtime experiment.

Musl's full COPYRIGHT file is retained verbatim in the evidence directory. It
states MIT licensing for musl as a whole and describes additional source-level
notices and exceptions. Before shipping this optional module, include the full
COPYRIGHT and any applicable notices from the linked implementation files. Keep
our transport/allocator modifications identifiable. MIT itself does not require
publishing modified source, but preserving the exact patches is our provenance
practice. This audit does not relicense modified upstream files as BSD-2-Clause.

## Development-only components and unresolved scope

OVMF code/variables are local QEMU inputs, not files in the ISO. QEMU, LLVM/LLD,
Zig, Rust and xorriso executables are host tools, not bundled executables. A future
SDK/emulator/firmware distribution requires its own complete inventory and terms;
the tools' runtime/library contributions must be considered separately, as above.
The permission to include proprietary drivers does not approve any particular
NVIDIA binary; none is included here.

Vendored standards, archived research, copied examples and documentation excerpts
need a source-distribution inventory before publishing the repository. They are
outside this binary audit. Original first-party content being BSD-2-Clause does
not establish rights to third-party excerpts within it.

## Required follow-up before binary distribution

1. Add a versioned notice bundle for the default image: Zig's MIT notice, resolved
   upstream notices for its included math/runtime code, and scoped Rust notices.
   Keep existing Aether and Limine notices. Trace the musl-derived Zig routines to
   their upstream notices; the musl 1.2.6 COPYRIGHT collected for the native probe
   is not proof of the exact version from which Zig ported each routine.
2. Give the optional musl artifact a matching notice/provenance bundle owned by
   its producer. Recheck after changing its library, adapter or runtime inputs.
3. Make packaging retain and verify the matching notices alongside binaries,
   including boot-artifact exports consumed by pkg-mgr. Check the actual exported
   bundle; successful ISO inclusion alone is not package-transport evidence.
4. Audit any separately distributed firmware/toolchain and source archive. Preserve
   immutable standards releases; attach licensing metadata through versioning or
   an external distribution manifest rather than editing pinned release bytes.

No copyleft source-publication obligation was identified for the confirmed
Limine/MIT components themselves. That is not blanket clearance for unresolved
runtime provenance, future imports, or separately distributed tools. In particular,
OpenZFS/DTrace and proprietary NVIDIA components require separate exact-version
reviews when introduced.

## Sources and verification

- [Installed Zig license](evidence/third-party-2026-09-05/LICENSE-Zig.txt) and
  installed compiler-runtime source headers recorded in inventory.json.
- [Rust licensing](https://rust-lang.org/policies/licenses/) and the pinned installed
  library copyright metadata identified in the evidence.
- [Musl copyright](https://git.musl-libc.org/cgit/musl/tree/COPYRIGHT), with the exact
  1.2.6 local copy preserved in the evidence directory.
- [Limine and protocol provenance](../boot/DEPENDENCIES.md).

The retained `audit-rebuild.py` is the concrete local experiment recipe, with
explicit host paths; it is not a portable public command or a complete automatic
license scanner. It rebuilds the four Rust modules with LLD maps, verifies byte
identity, extracts the ISO, captures kernel symbols and copies selected evidence.
The inventory additionally records the source/archive and runtime-header inspection.
No QEMU rerun was needed: this audit inspected bytes and linking, and changed no
runtime or build behavior.

## Experimental native taskq sources — 2026-09-06

`user/native-taskq/include/sys/zfs_context.h` derives taskq definitions from
OpenZFS 2.4.4 commit 71a9f9578616a90c3c14bb59629fb4d31bfd68d1 and retains CDDL
notices. Exact upstream [license](../user/native-taskq/LICENSE.OpenZFS) and
[copyright](../user/native-taskq/COPYRIGHT.OpenZFS) accompany it. Original platform
code and helper fragment use BSD-2-Clause; appending that fragment does not
relicense the upstream translation unit. [Object evidence](evidence/native-taskq-build-2026-09-06/README.md)
retains original/adapted hashes and complete source snapshots. These experimental
objects are not part of the previously audited default ISO. Distribution of a
future linked image needs its own matching notices/source and dependency review;
this entry does not extend the earlier ISO audit or grant blanket clearance.

## OpenZFS native-musl build audits — 2026-10-04

The [2026-10-04 OpenZFS startup build audit](evidence/openzfs-musl-startup-2026-10-04/README.md)
reuses the same pinned2.4.4 source archive and native musl SDK. Original CDDL
LICENSE/COPYRIGHT and private header/include diffs remain in the retained packet;
compiler resource headers have a separate inventory. This build-only experiment
adds no linked engine to the default ISO or new distribution clearance. Original
audit tooling is BSD-2-Clause; upstream sources retain their terms. Real native
compression/supporting-library builds and matching notices remain future work.

The [OpenZFS supporting-library audit](evidence/openzfs-native-support-2026-10-04/README.md)
additionally rebuilds bundled ICP/Zstd/Unicode and selected SPL/nvpair/AVL sources,
preserving their upstream notices. It reads zlib1.3.2's existing local pkg-mgr
distfile (SHA256 bb329a0a2cd0274d05519d61c667c062e06990d72e125ee2dfa8de64f0119d16)
and retains its own license/source. Matching source metadata defers authenticity.
No host-staged library, sibling recipe execution, default ISO payload or production
dependency adoption follows; missing XDR/diagnostic/runtime bindings stay open.

The [native memory-XDR/nvpair experiment](evidence/openzfs-native-xdr-2026-10-04/README.md)
uses explicitly fetched libtirpc1.3.6, archive SHA256
bbd26a8f0df5690a62a47f6aa30f797f3ef8d02560d1bc449a83066b5a1d3508, matching the recorded
host baseline. Hash pinning is not signer authentication. Its COPYING/BSD-style
three-clause terms and additional per-file notices remain in the retained source;
OpenZFS and musl keep their existing terms. Real memory-XDR and nvpair execute only
in private bounded conformance images, without RPC networking or an engine/volume.
Original probe/recipes are BSD-2-Clause; deliberate third-party mutation retains its
source notices. No default ISO payload, production dependency adoption, relicensing
or distribution clearance follows. Production diagnostics/runtime work stays open.

The [native startup-link audit](evidence/openzfs-native-startup-link-2026-10-04/README.md)
derives minimal private SPL assertion/no-trace reporting from the same OpenZFS
sources; exact originals/diffs and CDDL notices are retained. Unchanged path/mount
sources are rebuilt with section flags. Original probes/recipes remain BSD-2-Clause.
Two source-reviewed musl1.2.6 translation units and its COPYRIGHT are retained with
archive identity; no production SDK patch or sibling source change follows. The
static engine image is linked/parsed only, with no engine or volume execution.
Private diagnostic/prerequisite conformance images preserve the existing native
SDK terms. Prior bundled-library/libtirpc/zlib terms and source bytes remain in
the three bound sealed packets. No normal ISO engine payload or distribution
clearance is added; unsafe SDK prerequisites still block engine startup.

The [guarded-SDK independent intake](evidence/openzfs-sdk-guards-intake-2026-10-04/README.md)
consumes the exact userland candidate with musl1.2.6 archive/source/COPYRIGHT,
frozen maintained recipe and patch/build metadata preserved as inert inputs.
Original private probe/recipes are BSD-2-Clause; modified musl units retain musl
terms. Selected prior OpenZFS startup objects, unchanged reviewed SIMD/AES/GCM
source and configuration retain CDDL/bundled notices and bound complete earlier
source packets. Corrected-library native denials/old-library controls execute only
in disposable conformance images; the engine is linked/parsed, never invoked.
Default SDKs/pins/kits and normal ISO payload remain unchanged. This closes scoped
guard intake, not real runtime providers or distribution clearance.

## Toybox native-SDK link audit — 2026-09-07

The [build-only baseline](evidence/toybox-native-link-2026-09-07/README.md) retains
Toybox0.8.14 source archive827e4cdfd69f5da973e00e2a59b30b3c9857fb7fae74c362fd0b4f96be7929b0,
its [license](evidence/toybox-native-link-2026-09-07/LICENSE.Toybox) and original
source notices. Original audit tooling remains BSD-2-Clause; Toybox and native musl
retain their own terms. The linked unadapted ELF is not in any boot image or package.
This audit does not extend the default-ISO license inventory, authenticate upstream
sources or establish distribution clearance. Generated headers and resolved config
are separately retained reference inputs; no Toybox source patch is applied.

The [native startup witness](evidence/toybox-native-mask-2026-09-07/README.md) later
executes real Toybox toy_singleinit in the isolated opt-in native profile. It reuses
the retained Toybox archive/config/generated inputs and native SDK above, renaming
upstream main at compilation only. The original BSD-2-Clause startup probe does
not relicense Toybox/musl; archives retain upstream notices. This does not place
Toybox in the default ISO or establish a distributable package/license inventory.

The opt-in [native stdio callback experiment](evidence/native-stdio-2026-09-07/README.md)
retains the musl1.2.6 archive SHA256
`d585fd3b613c66151fc3249e8ed44f77020cb5e6c1e635a616d3f9f82460512a`, including its
COPYRIGHT. It builds the real __stdio_write loop with a private symbol rename and
one writev-call substitution; a separately identified mutant changes its return
count. Internal headers are unmodified. This is a private native witness against
the existing SDK, not an installed libc replacement or distribution approval.
Original probe code uses BSD-2-Clause; upstream musl source retains its MIT terms.

The [public native stdio experiment](evidence/native-public-stdio-2026-09-07/README.md)
reuses the same pinned musl archive and native SDK. It retains __stdio_write's
original symbol for a private image link and replaces only its writev call. Actual
public stdio comes from the unchanged SDK archive; no SDK installation is updated.
Upstream MIT terms/COPYRIGHT remain in the retained archive and generated outputs.
New original probe/recipe use BSD-2-Clause. This is not distribution approval.

The [actual native cat experiment](evidence/toybox-native-cat-2026-09-07/README.md)
executes the retained Toybox0.8.14 cat source unchanged. A private xwrap copy changes
only _xexit's normal _exit argument to invoke scoped cleanup after callbacks/flush;
its rebound and vfork paths are preserved. Deliberate skip-flush source is a separate
negative control. Toybox's existing license/notices and musl COPYRIGHT remain in
retained sources. Original probe code is BSD-2-Clause; no upstream relicensing,
installed SDK update or distribution approval is implied.


## Dash signal fixture objects

`user/native-command/dash-inputs/` captures 32 unchanged dash 0.5.13.5 Linux
reference objects from userland's hash-bound receipt, linked only for the selected
native signal setup fixture. COPYING.dash, build evidence and object hashes are
retained. Upstream licensing and reference source/generator trust limitations
remain; the original-work BSD default does not relicense these bytes. This is
experimental integration, not a release distribution approval or full dash port.


The [native ENV guard build comparison](evidence/shell-main-config-2026-09-09/README.md)
retains upstream dash source/header bytes, generated headers/config, a one-line
portability patch, three main objects and native musl SDK headers. Existing dash
notices and COPYING.dash, plus COPYRIGHT.musl, remain attached. The candidate is
not active or shipped; it does not replace the32 pinned reference objects. Generated
headers are captured, not independently regenerated. Source authentication and
full generator/license review remain under the existing reference limitations.


The first actual-main fixture selects a separate pinned copy at
`user/native-command/dash-main-inputs/main.o`, retaining the enabled build receipt
above and its COPYING.dash. It replaces only the main object in that opt-in link;
the other31 reference objects and every older profile retain their original bytes.
This bounded noninteractive execution is not an ENV/security or full-shell claim.

The [ordinary-command fork configuration](evidence/dash-command-config-2026-09-11/README.md)
adds an opt-in guard to source-built dash jobs.c and retains the original source,
exact patch, disabled/enabled comparisons and upstream notices. Its pinned jobs.o
is in `user/native-command/dash-fork-inputs/` with COPYING.dash. Existing native
main and other30 objects remain unchanged. Shared headers/config and SDK includes
come from the immutable main-config snapshot above and retain its provenance and
license limits. This local producer candidate is not release distribution approval
or independent userland/SDK acceptance. No upstream source is relicensed.

The [native serial input candidate](evidence/dash-console-2026-09-11/README.md)
retains dash input.c, its exact AETHER_NATIVE_NO_TEE patch and COPYING.dash.
`user/native-command/dash-input-native/input.o` selects the existing upstream
one-byte fallback for non-seekable input. Original, disabled and enabled builds
use the pinned main-configuration headers/tools; no new imports or dependencies.
The prior native main/jobs objects and immutable upstream object inventory remain
unchanged. This candidate does not relicense dash or publish a new SDK.

## Private native AES selection experiment — 2026-10-04

[Qualified private packet](evidence/openzfs-native-aesni-2026-10-04/README.md) retains
unchanged OpenZFS2.4.4 selected C/assembly and original source hashes. C callbacks
and dispatcher retain CDDL; aeskey/amd64 tables retain Brian-Gladman-3-Clause;
AES-NI assembly retains OpenSSL-standalone with full per-file notice and mandatory
acknowledgment. No first-party relicense or normal-image dependency adoption.
The packet includes standalone upstream license/description files and full assembly
notice alongside linked experimental artifacts. Production feature/security and
complete transitive redistribution review remain separate from component tests.

This product includes software developed by the OpenSSL Project for use in the
OpenSSL Toolkit (http://www.openssl.org/).

Private libzpool random boundary port (2026-10-04) retains the original OpenZFS2.4.4
kernel.c CDDL-1.0 notices, immutable input identity and exact scoped diff. The derived
selected random helper source stays CDDL-1.0; original probe/recipes are BSD-2-Clause.
Existing musl/OpenZFS copyright/license files are retained in its evidence packet.
This selected component compilation does not relicense or qualify the whole engine.

Private file-vdev/volume port (2026-10-06) replaces the selected libzpool file
helpers and disables unsupported TRIM in actual OpenZFS2.4.4 `vdev_file.c`.
Generated derived kernel/vdev sources retain their upstream CDDL headers/notices;
original Rust volume adapter, C shim/header/probe and builder are BSD-2-Clause.
Rust1.98.0/core/compiler-builtins use their existing upstream terms; compiler and
native target-library hashes accompany the private build. No new third-party
crate, host filesystem dependency or upstream relicensing is introduced.


Private filesystem-service intake2026-10-19 consumes the exact userland candidate
manifest5dd5f492dd2ab2c57321a8fd610f1f6fa488dece4c4b40466a37236bf24144c4,
object dab564abbcc70ca93cebec7fec8d6017c569367dde8419abbf2d2701401150b1.
Its BSD-2-Clause original source and supplied LICENSE/notices remain unmodified;
Rust inlining retains Apache-2.0/MIT/LLVM/NCSA notices in the sealed delivery.
Original OpenZFS CDDL sources remain separately owner-built, not relicensed by
this Rust boundary. The local adaptation is BSD-2-Clause. This is a private native
experiment, not a redistribution/whole-inventory or release-readiness decision.
No new downloaded dependency, SDK refresh or sibling mutation occurs.


Private service lifetime intake2026-10-20 separately selects manifest
0eddb895d8a8d6276834a0d4ec58aa77e13e44be882d5eab46695cf716ff825c,
object35c950f9a8b49df81d85f81e112f99ff2b8215d90140f14985e598735e653c6f.
It preserves the supplied BSD-2-Clause source license and Rust upstream notices;
original CDDL engine sources remain separately built with upstream notices.
The small pristine780248-byte file in `.deps/openzfs-namespace-reference-v1` is a
pinned private upstream fixture dependency extracted by original zdb, with exact
source/image/file hashes and commands in the integration receipt. It is not an
Aether first-party file, evidence archive or approved redistribution payload.
Upstream fixture/payload transitive terms still need release inventory review.
Owned extraction container/source/image outputs were disposed. No released pin,
SDK or whole-inventory/release licensing approval follows from this experiment.

Private namespace-service intake2026-10-19 selects the separate36-member candidate
manifest9d504603cac15be48e6a45dd266baae27c23b1851477a5fa1d27e44a4e0dc7d3,
objectd54182a8758b0e153c6f056460987497e6397c74c6b51c284b148e86fcdf8bdc.
Original Rust/C adapter and host fixture source remains BSD-2-Clause, with the
same supplied Rust Apache-2.0/MIT/LLVM/NCSA notices. Original CDDL OpenZFS engine
source/terms remain separate and unchanged; no additional downloaded dependency,
released pin, SDK refresh, payload relicensing or redistribution decision.

The separate fixed-mixed Rust service candidate has41 sealed members at
`../Aether-userland/build/service-deliveries/filesystem-service-mixed-2026-10-19-v1`.
Manifest SHA256 `e07aeeff522094d4994c90ec63ea68c6fb2ca2f6163d994c6e8a54a3f43181a9`,
object `37c280c2f2d4dcb1f58990743d260c9f61426e795992bf5a9b35ea3832b3cb1d`.
It preserves the original BSD-2-Clause sources, Rust/tool notices and original
OpenZFS C/ABI/typed-retirement inputs; it adds no new upstream dependency or
relicensing. Its generated object is an active candidate dependency, not retained
per-run evidence. Old25/27/36 candidates and released standards/SDK pins stay fixed.

The local filesystem launch candidate combines the unchanged67-member AF06 Rust
object with the resource-aware original OpenZFS/libzpool engine and existing musl
SDK. Original first-party adapters remain BSD-2-Clause. Its sealed current dependency
retains OpenZFS LICENSE/COPYRIGHT/NOTICE and module third-party notices, musl
COPYRIGHT, first-party LICENSE and the supplied Rust/compiler notices, with exact
input/tool hashes and build commands. SOURCE.md identifies the upstream revision
and local transformation owners. No whole-image relicensing, new downloaded
component, immutable pin update or public-distribution approval. A public release
must still provide corresponding modified CDDL source; a local ELF is not that
source publication or independent third-party release clearance.
