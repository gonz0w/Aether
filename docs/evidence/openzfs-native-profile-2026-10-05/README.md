# Selected OpenZFS native startup profile

2026-10-05,R1-03. The selected queue policy is now linked into an actual native
static startup image. This is private build/loader-model evidence; **engine entry
has not executed**. [Contract](contract.md) records scope and retry decisions.
Kernel, default image, public ABI/SDK, quotas, siblings and released pins remain.

Verified sources are OpenZFS2.4.4, commit71a9f9578616a90c3c14bb59629fb4d31bfd68d1.
Four expressions change in three original C files: system64→1, delay4→1, ARC
eviction auto→1 and file-vdev MAX(boot_ncpus,16)→1. Separate queues, ARC coordinator,
ZIO issue/completion and other workers remain. These are four queue selections,
not a four-thread engine or a safe global executor. Upstream I/O, residual-byte,
flush/error handling and synchronization bodies are unchanged. No host observers,
fault injectors, callbacks or successful platform stubs are copied from the trials.

The ordered177-object baseline libzpool and113-input supporting aggregate rebuild
byte-identically. Relinking the guarded SDK produces the exact prior baseline ELF,
SHA2568ff2ac05257f2176f3b2e2de3c9993174f1395a555b904b728c35c6948555e80.
Each of the three original queue objects also rebuilds byte-identically; explicit
macro-prefix mapping preserves their historical __FILE__ diagnostics while input
paths point only at this private tree. Compiler resource headers and SDK headers
match their prior inventories. Exactly three ordered object substitutions produce
the selected image; all other objects and SDK bytes remain unchanged.

Selected ELF SHA25603de1e4cbad1bbe3f20cce5963ad31de39fbe299b4bc9d67b685da4b704571d7.
Its4,371,768 file bytes and1309 initial pages including64-KiB main stack equal the
baseline geometry; four load segments and4-byte ELF TLS remain. Fresh current
loader models pass large layout and reject ordinary limits, W+X and oversized TLS
for both images. Neither model runs ring3 or establishes resource/stack/heap fit.

Actual object and final-ELF instructions prove system/delay/file call arguments1;
the object and ELF ARC scalar is1. Provider imports for each changed object are
unchanged; the static ELF has no relocations or unresolved provider symbols other
than the existing local inert _DYNAMIC marker. Host observer symbols are absent.
These facts establish build selection, not availability of those SDK operations.

Controls retain real artifacts: an actual old-taskq substituted ELF exposes64/4
and rejects the selected-count oracle; a compiled observer-reference object fails
the symbol gate and linking rejects exactly aether_file_fault_tag. A strict
whole-object link still rejects zfs_append_partition/zpool_default_search_paths;
no fake discovery is added to pass. Final attempt3 records42 bounded commands.

Setup verifies all five prior packet manifests and every archive member before
selecting regular files; no link is extracted or followed. Attempt1 rejects whole-
tree equality because62 command/manual/RPM/test aliases were deliberately omitted,
before any compile. Attempt2 verifies exactly those sealed non-build aliases are
absent and every regular source matches, then passes the build/object checks.
Its observer-string control is narrower than final attempt3's actual object/link
control. All attempts, recipes, patches, argv/times, ELF/object bytes and logs remain.
Full137 host/pin/workflow, scoped syntax/format/link and simplicity checks pass.

Unadapted inline engine time helpers still ignore unavailable clock errors; the
guarded libc does not fix those callers. Real scoped CPU/memory/identity/config,
calibrated monotonic/required UTC, production pthread/helper admission and native
heap/ARC, remaining CPU-state/feature closure and granted volume I/O remain before
engine startup/fini/restart. The reduced host82-worker observation remains historical
and cannot size this new native image. One additional reaper would exceed the82-
child profile if that population were reproduced. No quota or production helper
placement is chosen here. Rust filesystem/packages, wider SESSION, independent
SDK/reader/consumer and assembled R1 acceptance remain separate; local work remains.

Private recipes setup.py, build.py, geometry.py and checks.py reproduce into fresh
owned output constants; build.py takes a fresh attempt number and rejects reuse.
Use copied recipes rather than overwriting sealed outputs. Build commands keep
upstream GNU C99, Clang/LLD21.1.8 and the verified guarded musl SDK; original control
C uses the reviewed formatter. All builds stay offline and never use sibling
recipes or host headers. Archive/member readback precedes removal of only this
review's owned duplicate tree; shared caches and earlier packets remain.

CDDL OpenZFS, MIT musl, zlib and BSD-style libtirpc notices accompany the inputs;
bundled/per-file notices remain in bound source archives. Original recipes and
loader geometry use BSD-2-Clause. Build evidence grants no redistribution approval,
independent owner sign-off, runtime conformance or release readiness.
