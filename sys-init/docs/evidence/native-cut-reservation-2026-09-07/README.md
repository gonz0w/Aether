# Fixed Rust reservation owner — 2026-09-07

Decision 0167 implements a private fixed Rust reservation/cancellation owner.
One exclusive owner anchor binds lifetime-bearing keys; foreign keys deny even
when serials match. One/two ordered Launched indices reserve a retained record and
twenty credits atomically. Exact duplicates are inert, different active requests
are Busy, and cancellation retains membership and both consumed serials. Six
cancelled records exhaust storage; occupied effects, closure and u64 exhaustion
deny without mutation. There is no application, acknowledgment or reset API.

Five host Rust tests and three source omission controls pass through the required
sample-receipts gate. The same code compiles for x86_64-unknown-none, asserting
1976-byte storage and a 1984-byte owner including its identity reference. These
exclude native History/resources/stack and are not target execution. All ten local
gates pass in `run-k_1qkpg_`, including 287 unchanged model tests. All twelve
existing native consumer sources, release locks and catalog bytes remain unchanged.
Evidence: `docs/evidence/native-cut-reservation-2026-09-07/`.

Next BG-057: bind reservation source selection to the actual native Driver/History
path and consume a fresh Aether witness before claiming native reservation.
Lifecycle application/effect capture, explicit effect-record retirement and exact
receipt publication follow separately. BG-058 retains cleanup provenance, BG-060
sustained reuse and BG-033 recovery. The 190-case native checkpoint and BG-056
producer source-closure limitation are unchanged.

rust/ retains compiler identity, exact copied source inputs, host binaries/logs, three designated control failures and native-target library. validation/ retains all ten local gates. focused-before-input-list-update/ retains the earlier successful Rust run before aggregate source-list/documentation updates. interrupted-before-inventory-update/ retains the non-accepting aggregate attempt. No QEMU execution or native source provenance is established by these host tests. sha256.json seals the package.
