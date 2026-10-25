# Session SDK boundary intake — 2026-09-29

Requirement before changes: verify userland's UL-081 boundary audit and record the
remaining delivery responsibilities in the existing shell roadmap and references.
Foundations O-01/O-03/O-04 and E-01/E-04/E-05/E-08 apply. Verify the entire static
audit seal, its accepted serial seal binding, baseline ELF identity, link outcomes
and memory symbol providers. Copy selected receipts for reproducible local review.
Documentation-only selection: host, workflow/pin, syntax/link and whitespace checks;
no new QEMU run or sibling mutation. No runtime/ABI/grant/unsafe/resource changes.

Forbidden outcomes: treating link success as native qualification, assigning an
unagreed POSIX runtime owner, approving a reader review, changing pins or declaring
SSDK-01–06, SI-07 or R1 complete. Existing private acceptances remain unchanged.

Verified all125 members of the static audit seal
`5266af199a0da884541a77789e1794b2330cf3f445f35c9ac99c653d616a55a5`. The prior serial seal matches the accepted
`485c32579591d9ff3001c82fea6705e1a7a56fdb8d052da94a73ebaeda2d55a4`. The audit baseline ELF matches the retained serial
archive index and accepted identity `7adbe1cff61892bf647c3c28558f364dad9dda2ea664d2bd2a8b5961cc44596c`.
Five reported link outcomes and30 symbol providers in each successful layout match
the claimed static scope. Selected receipts and the consumer boundary/review
checklist are copied under `consumer/`; its copied manifest describes the entire
external audit, while this intake's own seal covers the selected local copies.
No audit commands are executed here and no native run is performed. The earlier
serial intake already verified the retained archive bytes; this review verifies
its index binding and the newly supplied ELF bytes.

The memory-omission link succeeds through upstream musl providers. Native behavior
of that altered ELF remains unqualified. Required component checks must fail closed;
archive packaging alone does not establish a supported runtime. Existing qualified
private artifacts retain their exact scope. Public/internal mask state, libc rebind,
strict memory protection, owner-only UART and generation-bound cleanup remain hard
requirements at the new runtime boundary. No broader security claim follows.

Remaining inputs: an explicitly agreed libc/POSIX runtime owner and sealed buildable
opt-in bundle, then SSDK-01–06 native replay and actual independent reader findings.
The boundary assessment does not transfer runtime ownership. Aether's ABI/grants/
fixture responsibility and userland's SDK experiment/replay responsibility remain.
SI-07 separately lacks complete versioned bootstrap/transport and rebuilt runner/
bytecount. Current active STATE/ROADMAP/reference/workflow now record the delivered
assessment and these concrete remaining gates. No sibling or release pin changed.

Local checks pass:132 Python tests plus configured Rust/Zig and offline pins,
workflow inventory, Foundations, simplicity snapshot, local intake links, verifier
syntax and scoped whitespace checks. See [checks.json](checks.json). No runtime
source changed; no unrelated native suite was rerun.
