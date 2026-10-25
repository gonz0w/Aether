# FILE/C write receipt evidence — 2026-10-24

[FS-FILE-WRITES](../../proposals/FS-FILE-WRITES.md) owns requirements, status and
continuation. This evidence covers synthetic-storage Rust service/process/FILE
host execution, real C client/facade pipes, scripted loss and freestanding library
objects. It does not supply native placement, complete owner fit, guest execution,
durability, libc/routed writer activation or persistent shell acceptance.

From `userland/`:
`PYTHONOPTIMIZE=1 python3 -B experiments/filesystem-service/check-file-writes.py`.
The suite uses one300-second cumulative deadline including the preceding process,
client and binding suites. Frozen sources/tools/native libraries, actual per-unit
C header closures, pinned native SDK headers and UBSan runtime are rehashed before
owned build/control output deletion. No per-run binary/source/SDK bundle is kept.
Disposed C control copies are identified by their retained original and mutation
recipe; final identity readback must reconstruct them rather than claim retention.

## Attempts and triage

| Attempt | Observation |
| --- | --- |
| [01](attempt-01.json) | Clang header scan fails because Rust's LLVM library path leaked into the C tool. Isolate C-tool environment. |
| [02](attempt-02.json) | Planned pre-code compiler red: new C receipt types/API are absent. No semantic runtime-red claim. |
| [03](attempt-03.json) | New C matrix passes; Rust harness compilation fails on a fixed-array/slice decoding helper mismatch. Correct test helper. |
| [04](attempt-04.json) | Existing C schedules reproduce a newly introduced legacy name-validation inversion. Replace conditional nesting with a small shared name-staging helper. |
| [05](attempt-05.json) | Initial scope passes354 children including28 Rust cases and1631 legacy C schedules. Deliberately fails at the unimplemented remaining-gates placeholder. Header closure was incomplete; no qualification pass claimed. |
| [06](attempt-06.json) | Expanded malformed-receipt test incorrectly treats maximum nonzero TXG as invalid. Replace that mutation with forbidden TXG0; production behavior was correct. |
| [07](attempt-07.json) |29 Rust cases, actual C terminal receipt interoperability and predecessor checks pass; native dependency scan rejects unused -c under -M/-Werror. Keep compile action out of dependency scan only. |
| [08](attempt-08.json) | Freestanding C objects compile; linker fails from the same Rust LLVM path leak. Isolate linker and inspection tools too. |
| [09](attempt-09.json) | Rust/native/profile/predecessor gates and seven new controls pass. A source-close mutation is rejected by the earlier inactive-field codec matrix rather than its required named active-close marker. Narrow the mutant to active cleanup fields; no production change. |
| [10](attempt-10.json) | Final pass:452 bounded children,29 Rust cases,11 new controls, all old consuming suites/guards, freestanding objects/link/inspection, formats, final input verification and complete disposal. |

The [first CLI/process gate attempt](cli-process-attempt-01.json) preserves an
incomplete script run: CLI controls and root pin/method checks pass, then an
incorrect simplicity-manifest path prevents completion. The [second CLI/process run](cli-process-attempt-02.json) passes before a later
control-recipe adjustment; the final exact-source
[CLI/process checks](cli-process-checks.json) pass17 children with complete owned
cleanup: changed/new entry help/version, escaped usage64, missing/mismatched pin2,
optimized false-oracle rejection, root standards/Experience/Distribution and
method/simplicity manifests. Current Python3.14.7 is tested; minimum3.10 execution
is not established. The temporary gate script is disposed after its source hash
and commands are recorded; it is not a retained reusable runner.

[Run context](run-context.json) binds final attempt10 to its command and digest.
The nine FILE cases exercise successful real writes/readback and copied receipts,
all terminal reported progress states, dropped/forgotten delivery guards without
replay, local denials, malformed request/padding/old versions, real C-produced
requests/Rust-produced replies and live C facade success/error pipes. The terminal
C test keeps COMMITTED TXG0/staged4 as an error with distinct raw source/FILE closes.
The C matrix checks every header/receipt lane, all state/cause mappings, raw signed
extremes,4096-byte success,4160 outgoing and128 incoming loss prefixes, malformed
callback replies, partial transfers,16384 attempts, invalid no-I/O and generic
write refusal. Failed decoding leaves caller output unpublished.

Eleven compiling controls target terminal-receipt discard, missing owned copy,
guard clear/retirement, padding, committed TXG0 rejection, premature publication,
source-close corruption, loss classification, separate FILE closes and generic
write admission. Every one fails its named semantic marker. Compile failure,
timeout or generic panic does not qualify. The predecessor320 checks include18
existing controls, client/process/binding cases, old13-/16-slot process and FILE
consumers, profile guards and unchanged ProcessFiles1464/8 layout.

Strict C17/warnings/UBSan and Rust warnings/Clippy/Rustfmt pass. Both new C units
compile for x86_64-unknown-none with the exact relocated217-header SDK pin, link
relocatably and inspect as ELF64/x86-64. Only libc memory symbols remain unresolved;
maximum individual C frame328 bytes is not whole-owner/call-stack fit. The selected
Rust libraries also build for that no_std target. Old C1631 schedules execute
against exact retained request/reply fixtures. The union of25 per-unit/profile C
header closures is frozen along with the formatting input, LLVM resources and
runtime. Final919 source/header/runtime entries verify before disposal; disposed
control paths require reconstruction during later identity review.

Separate peer-agent source/evidence/reader review is recorded in
[peer-review-checks.json](peer-review-checks.json); integration observations belong
to the owning record. No human, specialist, native or release acceptance is claimed.
