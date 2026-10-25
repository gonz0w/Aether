# UL-044 package transport evidence — 2026-09-05

27 QEMU outcomes cover the current accepted bundle: four stdio, seven failure,
four libc, four descriptor, four writable and four read-only cases. Host is arm64
macOS; target is Aether x86-64. Results establish bounded artifact transport and
native consumer execution, not native shell or persistent package installation.

The stdio run uses `files-writable-memory` / `userland-stdio`. This explicit
AENFS001 transport variant declares native-memory=true, smp=false and the existing
volatile scratch service mode. Other profiles and historical receipts are unchanged.
No sibling implementation, shared ABI, musl archive or standard pin was modified.

`invocations.json` records all six exact commands, external producer/tool pins,
original sibling evidence paths and matching captured kernel directories. Original
reports are under Aether-userland/docs/evidence/native-stdio-files-2026-09-05.
Normalized report copies here preserve data; external pins apply to original bytes.
Each result records the package helper closure and payload/receipt/image/serial
identities. Source snapshots preserve this harness and transport implementation.

Large images, exact staged payloads and frozen tool/dependency copies remain in
`/Users/cam/DEV/pkg-mgr/.pkg-mgr-live-ul044-RUN-2026-09-05`, substituting stdio,
failures, libc, descriptors, writable or read-only. Small logs, receipts and result
inventories are copied here and hash-checked. Reproduction needs the pinned inputs
and a fresh --root; published destinations are not overwritten.

Seven input controls reject before output creation: missing/integer stdio mode,
missing client define, missing/conflicting native-memory build options, the legacy
memory-disabled writable profile, and incomplete cases. `input-controls.json`
records specific expected validation errors. Ordinary fixtures also reject integer
memory options and a memory-enabled receipt relabelled as the legacy profile.

StdIO semantic controls require client 189/186/196 for baseline-flush,
corrupt-vector and leak-poll-errno respectively, supervisor 611 and exact profile
panic. Positives require the file-service pass marker and supervisor 100/reclaimed
3. The 23 regression cases retain their independently specified statuses.
A timeout or unrelated panic cannot count as rejection evidence.

This is one 27-outcome bundle with overlapping regressions, not 27 new features.
Dynamic FILE allocation, buffered seek/bytes, failed input sync preservation/retry,
flush errno and final descriptor/FILE cleanup remain a bounded single-thread,
valid-local-buffer witness. Formatted I/O, automatic exit flushing, all modes,
threads/cancellation, exec/inheritance, TTY and persistent installation are open.
[Transport and owner references](../../NATIVE-LAUNCH-TRANSPORT.md).

`macos-fixtures.log` records all three pinned standards checks and sixteen
ordinary fixture scripts passing after this change.
