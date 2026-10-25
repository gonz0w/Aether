# OpenZFS native-musl startup build audit — 2026-10-04

**No complete native engine link or runtime yet.** This private R1-03 audit produces
177 of178 declared libzpool C objects against the existing x86_64 native musl SDK.
No engine execution, allocation/stack budget, filesystem acceptance or release gate
is claimed. [Contract](contract.md) records scope before each stage. Kernel/runtime,
released pins and sibling sources are unchanged.

| Stage | Result |
| --- | --- |
| Initial setup | Runner assumed ld.lld lived in LLVM's bin directory; failed receipt/runner retained. Use the separately pinned LLD path. No engine build ran. |
| Fourteen-file baseline | Twelve objects; two missing Linux fs/zlib headers. Host-header control rejects missing mach/mach.h. |
| Complete declared C list | 145/178 objects;19 Linux fs,11 cpuid,2 zlib and1 gitrev header failures retained. |
| Private unused-include changes | kernel.c uses no zlib declaration; abd_os.c uses no znode declaration. Removing those includes produces two objects without warnings; exact patches retained. |
| Private real-header comparison | Actual compiler resource headers, retained gitrev header and a vfs wrapper retaining real musl statfs while removing linux/fs.h produce30 more objects. No Linux filesystem operation/constant or successful platform stub added. |
| Partial closure | 177 distinct source objects; gzip.c still fails. ELF64 x86_64 relocatable link succeeds; strict static kernel_init/kernel_fini link fails with175 unresolved names and no executable. |
| Selected trial copies | Exact 1/1 system/delay taskq, serial ARC and one-worker file-vdev compile separately. Imports remain visible, including the file fault observer; these are not substituted into the baseline aggregate. |

The178-file list is dist/nodist libzpool C sources parsed from the retained Makefile,
not the engine's transitive libraries/assembly. No make commands or Linux/glibc
archives are used. Linux-generated feature config is an explicit comparison input,
not native feature detection. Compiler headers are inventoried; host-header denial
still passes. AVX/XSAVE feature selection needs native review before execution.

## Missing work

The final aggregate imports300 symbols:122 SDK exports and178 other imports.
Availability does not establish native syscall support. Four weak tunable imports
do not cause linker errors; musl introduces __aether_io, giving175 unresolved names.
Exact names are in [header results](headers-results.json).

| Missing family | Symbols | Work |
| --- | ---: | --- |
| AVL/list/nvpair | 119 | Rebuild upstream native supporting libraries. |
| ICP/checksum crypto | 24 | Rebuild C/selected assembly and audit CPU-state dispatch. |
| SPL primitives/assertions/tunables | 23 | Actual atomics/barriers, page configuration, failing assertions and weak-import semantics. |
| Gzip/Zstd | 8 | Real pinned native zlib/header and bundled Zstd; unused-include removal does not implement gzip. |
| Unicode | 1 | Upstream text-preparation build. |
| Zutil identity/formatting | 3 | Separate pure formatting from host identity/device discovery. |
| Musl I/O adapter | Extra strict-link import | Reviewed native adapter; bounded descriptor transport does not implement filesystem/entropy. |

Actual kernel_init calls page discovery, random_init, uname, queues, ICP/Zstd,
SPA/config loading, checksums and TSD. Random init opens /dev/random and /dev/urandom;
config loading attempts host paths. Existing bounded memory, pthread/TSD, wait/reap
and taskq witnesses are starting points, not full-engine acceptance. File/config/
entropy access needs capabilities; clocks/topology/identity need explicit semantics.
Thread admission and backing/stack measurements remain open. No successful file,
flush, entropy, lookup, threading or discovery stubs are introduced.

Next rebuild native supporting libraries/compression with reviewed native feature
configuration. Obtain a genuine static startup closure and actual image/allocation/
stack evidence before proposing admission. Startup/fini/restart precedes grant-bound
storage and Rust filesystem composition. Sys-init owns its recipe/qualification;
this does not independently accept its latest repair.

## Checks and retention

Full `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`
passes133 Python tests plus configured Zig/Rust, three offline pins and workflow.
Host-header and unknown-import controls reject for exact named reasons. Source/SDK/
tool inventories match before/after each stage. No unrelated QEMU run is selected
for this private build audit; no native engine result is claimed.

All4063 upstream source files match the prior verified identity. Source archive
SHA256 bd042e3e172d3194c5c5230bf427a54acaf8718f9981789ddd81ad18e8ab46a8;
musl archive SHA2568f66b2b383eabd08b8f27c4913f36a91071c4cfb6373cedebd2e69cabfaaeecc.
CDDL LICENSE/COPYRIGHT remain attached; original tooling is BSD-2-Clause. No engine
payload is added to the default ISO or approved for distribution.

Private recipes [audit.py](audit.py), [closure.py](closure.py), [headers.py](headers.py)
run in order with exact local prerequisites and absent output directories. Reproduce
from copied recipes using fresh output constants, never into this sealed packet.
artifacts.tar.gz preserves objects, logs, argv/timestamps, patches, config, every
compile/link failure and stage input snapshots. Every generated regular file is
read back before the two new unpacked roots are removed; archive-check.json records
verification. Initial setup retains its exception receipt/runner; its console
traceback was not redirected. Check receipts are retained separately.
