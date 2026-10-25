# Client mutation evidence — 2026-10-24

[FS-CLIENT-MUTATIONS](../../proposals/FS-CLIENT-MUTATIONS.md) owns requirements,
status and continuation. These are actual Rust owner/service/client host executions
over synthetic storage and no_std builds. No native transport, guest, whole-owner
fit, durability or persistent shell acceptance was performed.

Command from `userland/`:
`PYTHONOPTIMIZE=1 python3 -B experiments/filesystem-service/check-client-mutations.py`.
[Run context](run-context.json) binds the qualified command to attempt07.
The runner freezes source/tool/native-library/sealed-producer identities, uses the
pinned owned-process helper and one300-second deadline, and removes all owned
build/mutant trees after compact readback. No SDK, image or build archive is kept.

## Attempts and triage

| Attempt | Outcome |
| --- | --- |
| [01](attempt-01.json) | Tests-before-code compiler red: missing mutation types and methods. This is not a semantic runtime result. |
| [02](attempt-02.json) | Initial19 tests and existing checks pass; suite intentionally fails because semantic controls were not registered. Two direct service cases were added afterward; no retrospective test-first claim for those cases. |
| [03](attempt-03.json) |21 tests and builds pass. Completion-count control returns unexpected success, but unwrap_err panics before its required marker. Checker rejects that generic failure. |
| [04](attempt-04.json) | Same marker issue retained: initial edit matched an earlier progress assertion instead of the malformed-reply loop. Corrected the exact loop. |
| [05](attempt-05.json) | Completion/progress/retirement controls qualify. Rename-order assertion holds a fixture lock during panic; poisoned-lock cleanup double-panics and aborts. Copy observations before asserting. |
| [06](attempt-06.json) | Five controls qualify. Namespace-errno mutant fails strict compilation because it removes the only use of a parameter. Widen its errno threshold while retaining the parameter; require semantic rejection. |
| [07](attempt-07.json) | Final pass under Python optimization1:197 children,21 AF09 tests, six mutation controls plus six unchanged binding controls, affected compatibility/build/layout checks and final frozen-input verification. |

No failed result is reset or discarded. Production mutation code did not change
while correcting these test/checker oracles. Every attempted build tree reports
complete disposal. Minimum Python3.10, native execution and release acceptance
remain untested here; actual interpreter/tool versions are in each receipt.

## Acceptance mapping

Thirteen mutation tests plus eight existing AF09 binding tests exercise write and
readback, all five namespace operations, actual server hole denial and exact
Unassigned/Committed/Completed/Unknown errors. A real service write with a lost
reply produces one backend effect, Unknown and no replay. Scripted cases cover
all65 write send positions and response loss, nine namespace send positions,
1/64/65/4096-byte writes,255+255 contiguous rename bytes, signed-offset/name/rights
preflight, malformed reply fields and caller-owned receipts after abort/drop.

Six compiling controls target completion byte count, COMMITTED TXG0 retention,
error retirement/close receipt, rename order, write rights and namespace errno.
Each must fail one exact test with its required marker; generic failure, timeout
or compilation failure cannot qualify.

The shared baseline retains its eight AF09 tests, six binding controls and65 old
host cases across AF07/08, legacy and the exact sealed AF07 producer. AF05/06 and
matching old consumers still build; AF09 activation/remote consumers and mismatched
client/service versions reject. New mutation methods are absent from AF07/08 and
sealed host/target clients. Strict Rustfmt, warnings, Clippy and host/no_std library
checks apply. Client remains680 bytes/alignment8, equal to AF08 on host and target.
Owner1080/8 is prior unchanged evidence, not a fresh measurement in this slice.

[CLI controls](cli-controls.json) check both existing/default and new checker
help/version, escaped usage64, missing/mismatched prerequisites2, syntax and explicit
false-oracle rejection under Python -O. [Process checks](process-checks.json) verify
root Foundations, Experience, Distribution and method/simplicity pins. [Separate peer review](peer-review-checks.json) verifies final source/evidence
identities and records passing workflow, userland quality, scoped links/anchors
and whitespace gates with complete owned-output cleanup. Actual review scope and
integration observations are recorded in the owning record.
