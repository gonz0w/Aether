# Real native Toybox startup and mask — 2026-09-07

The probe runs actual unmodified toy_singleinit for the standalone cat descriptor
in Aether QEMU after complete AECAT001 bootstrap and exact copied cat/LC_ALL=C
startup. It stops before cat_main and does not exercise Toybox's terminal hook.

Observed checks: private initial mask0077; calls umask(0) then umask(0077), returning
0077 then0; restored state and toys.old_umask0077. High requested bits are removed;
uninitialized/retired state rejects EINVAL. A thread-local sentinel survives real
startup. Wrappers delegate to real xmalloc/setvbuf and require one4096-byte stdout
buffer successfully installed. Real locale setup produces UTF-8. No syscall failure
is turned into a successful initialization stub.

Existing bounded native-memory support is explicitly enabled. Its grant is checked
before initialization; no-memory mode rejects116/owner1501. Wrong old mask and
skipped initialization reject115/owner1501. These controls cannot pass on a generic
panic. The positive owner verifies zero stream positions, empty sinks, three
closes, backend EOF/stale denial and four native reclaims across two generations.

This is probe-local process state, not a public userland API, signal/thread-safe
mask implementation or creation-mode enforcement. It supplies no filename authority.
Memory limits and kernel interfaces are unchanged. Callbacks/flush/exit, locale
fallback and allocator failure are not qualified by this startup witness.

## Reproduction and source identity

Run `python3 docs/evidence/toybox-native-mask-2026-09-07/run-native.py` with the
installed pinned tools. It verifies the retained link-audit source/SDK/object
baseline, rebuilds upstream main with a symbol rename (toybox_original_main),
rebuilds the existing memory adapter under a distinct raw-I/O symbol, and links
user/native-command/toybox-mask-probe.c. The probe's umask is local to this image;
no global musl syscall/exit change or upstream source patch is introduced.

The owner/backend envelope comes from the qualified cat-admit-empty archive and
is checked against its recorded digest. Native output markers/resource inventory
remain unchanged. Actual resolved Toybox generated headers/config remain captured
inputs, not fresh generator reproduction; original licenses/notices are retained
in the link baseline and archived extracted source. Strict probe diagnostics remain
enabled; upstream headers alone are system includes.

## Attempts

1. [Compile failure](attempt-1-triage.md): upstream inline headers triggered strict
unused-parameter diagnostics. Classify only upstream includes as system headers.
2. [Loader rejection](attempt-2-triage.md): probe ELF lacked required PT_TLS. Add a
real observed TLS sentinel; preserve parser constraints.
3. [Initialization failure](attempt-3-triage.md): the plain command profile had no
memory grant. Compose existing native-memory support and add explicit denied-grant
coverage. No quota increase or hidden success.
4. Final native run passes startup plus wrong-old/skip-init/no-memory controls.

All three failed attempts retain matching source/recipe snapshots and build/raw
logs. No failure is waived. Native run sources remain frozen during qualification.
Full prior command, connections/inherited, host/Zig/pins/workflow and format checks
accompany the probe. Per-case run timings, independent review and extended coverage
remain unavailable. No sibling, release pin or prior UL-059 bundle changes.

## Qualification

Final attempt4 passes all four native cases; 211 prior command cases, six
connections and nine inherited-launch regressions also pass. All 98 host tests,
Zig tests, offline pins, workflow and scoped formatting checks pass. Four final
receipts match frozen runtime sources. Every prior runtime input is unchanged;
only the new probe is added. Kernel/build and SDK/libc/tool identities are unchanged.
The startup ELF is83,896 bytes with21 load pages and a real4-byte TLS segment.
The existing memory profile is explicitly composed; its limits are unchanged.

final-artifacts.tar.gz retains final source/recipe snapshots, upstream build inputs,
objects/ELFs, native envelopes and raw logs for the native and regression suites.
ISOs, installed boot duplicates and kernel.elf are omitted with hashes in receipts.
Three failed attempt archives remain intact. Qualification, archive checks and
manifest bind the evidence. Real applet copy/private stdio and terminal adaptation
plus independent CAT consumer acceptance remain open.
