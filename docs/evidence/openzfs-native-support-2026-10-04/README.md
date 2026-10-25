# OpenZFS native supporting-library build — 2026-10-04

**All 178 declared engine C files now have native objects; startup still does not
link.** This R1-03 build-only experiment extends the sealed
[startup audit](../openzfs-musl-startup-2026-10-04/README.md), using its unchanged
177-object baseline and private include/header comparisons. No engine execution,
CPU-state qualification, memory/stack budget, filesystem or release gate is claimed.
Kernel/runtime, sibling sources and released pins are unchanged.

[Contract](contract.md) records each stage before implementation. The prior19-file
packet and every5037-member archive entry are verified before extraction into a
new private root. Source, SDK, compiler-header and executable inventories stay
unchanged during qualified builds. No host headers or Linux/glibc objects enter
the link, and no successful runtime stubs are provided.

| Build stage | Result |
| --- | --- |
| Supporting C group | 78/81 sources compile: AVL1, SPL14, assertions1/2, nvpair4/6, Unicode1, ICP33, bundled Zstd22, zutil2. |
| Retained C failures | backtrace.c needs execinfo.h; nvpair.c and nvpair_alloc_system.c need rpc/types.h. Nothing disables their semantics to pass. |
| First compression runner | Infrastructure failure: compression.py shadows Python3.14's standard compression package during shutil/bz2 import. No compiler command ran; source, cache, traceback and receipt retained. Renaming the private runner resolves the collision. |
| x86_64 ICP additions | All13 declared additions (C and real assembly) compile without warnings. No AVX/XSAVE execution or native dispatch policy is qualified. |
| Native zlib compression core | All11 upstream core files compile; optional gz file wrappers are not included. No file-operation fallback is added. |
| Engine gzip | Real gzip.c compiles unchanged with the verified zlib headers, completing the declared178 engine C files. |
| Final link | Partial ELF64 x86_64 aggregate links; strict static startup fails with102 named unresolved symbols and produces no executable. |

## Remaining closure and runtime work

The first stage resolves119 old non-SDK imports, while exposing further dependencies
from the newly compiled units. Final aggregate imports273 names:170 exist in the
native musl archive and103 do not. Those103 comprise98 nvpair symbols, backtrace,
two tunable section-boundary symbols and two zutil platform/discovery imports.
The final linker supplies the two actual section boundaries, while musl introduces
the explicit __aether_io hook:102 unresolved names remain. Exact inventories and
all compile diagnostics are in [support results](support-results.json) and
[compression results](compression-results.json).

Whole-object linking includes paths beyond kernel_init/fini; these counts are not
minimal startup reachability or necessary kernel operation counts. The selected
zutil units contain basename/numeric formatting **and** host-facing paths, exposing
zfs_append_partition/zpool_default_search_paths. Review that boundary rather than
copying host discovery or faking successful device access. XDR encoding must stay
real: dropping the format or inventing RPC declarations is not a valid port.
Backtrace configuration needs an explicit native diagnostic decision; assertions
remain failing invariants, not successful no-ops.

The old Linux feature config remains a comparison input. Linking real crypto
assembly does not make AVX/XSAVE safe on Aether. Native CPU-state selection, clock,
entropy, identity/topology, scoped volume/config access, pthread admission and
stop/reap require independent contracts and target evidence. A Rust service remains
the policy owner. Native libc symbol availability establishes none of these.

**Next:** qualify a real memory-XDR/nvpair dependency and native diagnostic profile,
review zutil discovery linkage and bind the existing SDK I/O hook through an honest
adapter. Obtain a genuine static startup image before allocation/stack measurements
and owner-local admission. Startup/fini/restart still precedes grant-bound storage,
persistent filesystem and package/shell integration.

## Dependency and licensing scope

OpenZFS2.4.4 uses the preceding pinned source archive and retains CDDL/bundled
notices. Zlib1.3.2 archive is read from pkg-mgr's existing local distfile, compared
with its inert source metadata, then copied into the private root. Size1502830;
SHA256 bb329a0a2cd0274d05519d61c667c062e06990d72e125ee2dfa8de64f0119d16;
recorded origin https://zlib.net/zlib-1.3.2.tar.gz. That metadata defers source
authenticity: byte matching is not signer authentication. No package recipe,
host-staged library, sibling script, network fetch or dependency pin is followed
by normal builds. This is a private audit input, not a production dependency adoption.

[Zlib license](LICENSE.zlib), [OpenZFS license](LICENSE.OpenZFS) and
[copyright](COPYRIGHT.OpenZFS) remain attached. Full source trees and their bundled
notices remain in the bound archives. Original audit tools use BSD-2-Clause;
third-party sources retain their terms. No default ISO payload/distribution approval.

## Checks and retention

Full host/pin/workflow checks, simplicity snapshot checks, exact missing host-header
and unknown-import denial, private Python syntax and packet links pass. Relevant
builds are fresh optimized native objects; no QEMU/engine runtime pass is inferred.
There are no kernel or ABI changes requiring unrelated target regressions.

Private recipes [build.py](build.py) and [compress-build.py](compress-build.py)
use exact local prerequisites and reject existing output directories. Reproduce
using copied recipes with fresh output constants; never write into sealed packets.
Sources, patches, objects, argv/timestamps, all failures and logs are retained.
Previously sealed inputs are reused by verified archive identity instead of copied
into another evidence archive; new outputs have their own archive/member readback.
The newly owned unpacked root and redirected temporary logs are removed only after
both preservation paths verify. No older temporary root or evidence is removed.
