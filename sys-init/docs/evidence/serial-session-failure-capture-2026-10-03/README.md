# Private serial-session failure capture

2026-10-03, BG-067, decision0183 continuation. This adds bounded private failure
capture; maintained runtime, ABI22 recipe, released pins and sibling sources are
unchanged. The initial delayed failure remains unclassified. Successful diagnostic
reruns do not qualify the complete composition or fix that finding.

Selected source and kit members were verified against the prior
[owned packet](../owned-serial-session-2026-10-03/README.md) before copying. Only
private owner images change; existing clients, kernel, entropy and boot modules
remain selected from its sealed artifacts. Build commands/options and selected
input hashes are retained. This is not a fresh complete producer/SDK audit.

`source` emits a fixed31-byte ASCII `SYSINIT-FAIL <code> <line>` record before the
existing failed-owner diagnostic and deliberate ud2. Direct failure calls and
unwrap closures carry compile-time numeric source lines. Its ordinary failed
checks report the check function line. `source-full` additionally uses a small
macro/function to carry every check call's numeric line; it avoids compiler-generated
file/location metadata. Panic emits distinct codeffff0001 and line0 before the
normal failure path; its exact panic caller/file is deliberately unavailable.
These codes/lines are private image diagnostics, not a published machine ABI.
No resource release, recovery, authority or replay policy changes. UART emission
is fixed-size/bounded calls and best effort, with no diagnostic retry loop.

Fresh forced controls qualify direct failure (code2820/line1237), panic marker,
and a full-macro failed check at its actual source line. All three reject before
child admission, terminal or successful halt and reach the existing failure/fault
path. Nine independently mutated traces (missing/malformed diagnostic or fake
halt) reject. `check-session-caller.py` keeps these semantic checks distinct from
emulator startup/timeout and verifies exact marker counts/order/identity.

Eight delayed real shell workloads pass: three direct-location image cases,
three full-check image cases, and two additional full-check cases with7-byte writes
spaced20ms and single-byte writes spaced2ms. All wait35 seconds at the first prompt
and two seconds at subsequent prompts. Gaps are requested host-side pacing,
not a guest scheduler/performance guarantee. Each group uses independent one-CPU
TCG guests and variable-flash files. Drivers bound native runs90s, UART1MiB and
stderr4MiB and reap emulator groups. These are local Aether cases, not other-OS
qualification or exhaustive scheduling coverage.

The retained unchanged producer oracle verifies all eight exact90-byte UART
streams, eight admission identities, ten terminal/reclaim identities, prompt/phase
cleanup, fragmented input and final authorized halt. Only copied receipt labels
are normalized to delayed for its delay/idle contract. No raw data or events change.

Linked raw/ELF equality and scoped inspection pass. Direct-location image15632
bytes; full-check image15984 bytes; both estimate3912/4088 stack and34 inspected
immutable memcpy/memset/memcmp sites. Controls use311/414/385 bytes and144/176/160
stack. The16KiB linker guard remains stricter than the24KiB target allowance.
This is a conservative aid/manual boundary inspection, not a formal CFG, kernel
stack or memory-corruption proof. Panic-control inspection excludes adjacent
rodata using exact ELF function-symbol extents; its first naive traversal wrongly
decoded data after the no-return panic call. Both attempts are retained.

Five large-metadata/code variants failed the16KiB linker guard and were rejected.
Full panic location access retained substantial location data; compact numeric
check/direct lines plus a location-free panic marker fit. An intermediate formatter
had an inferred panic/diagnostic recursion path; it was rejected, then changed to
fixed slices whose iteration needs no panic-producing bounds path. Failed source
snapshots, compile logs and inspection attempts remain separate; none were run as
accepted native images. No budget increase or generic tracing framework was added.

The original failure remains in the prior packet, at normal end-path ud2 before
parent completion. These witnesses did not reproduce it. Next use this qualified
private capture for a focused reproduction/transport and cleanup investigation;
do not infer runtime repair, release review or complete integration from retries.
`artifacts.tar.gz` retains newly linked images and the rejected recursion image;
its manifest was checked by extraction/readback. Unchanged input artifacts and
third-party firmware/boot notices remain in the explicitly linked prior packet.

All ten repository gates pass in `out/checks/run-t8bqwtqv`, with checked sources
unchanged; aggregate and raw gate logs are retained in `validation/`. Documentation
impact is limited to the existing serial guide, decision0183, BG-067/state and
quality surface. No new operator command or maintained unsafe boundary is added.

`tools-observed.json` records explicit compiler/LLVM identities after the first
builds, not retrospective pre-pins. They were frozen in `tools-frozen.json` before
a fresh bounded reproduction of all five qualified owner raw/ELF pairs, after
reverifying the final source snapshots. All five pairs are byte-identical to the
exact owners already consumed by the fresh native traces. Reproduction logs and
commands are retained; compiler/sysroot dependency closure is not newly audited.
