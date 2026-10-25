# Native cut storage study — 2026-09-07

Decision 0166 defines the first native reservation/storage slice: six retained
cut records and one twenty-entry full-token effect pool. Checked source indices
avoid self-referential pointers into movable History; they confer no native
resource authority. Reservation/cancellation must retain consumed serials and
membership. No Applied receipt or effect acknowledgment is exposed by this slice.

The proposed repr(C) layout measures 1976 bytes aligned to 8 on the host, with the
same compile-time assertions passing for x86_64-unknown-none under Rust 1.98.0.
This excludes History, Driver, source/lifecycle/call records, stack and code; it
is not a total memory budget or runtime witness. All ten local gates pass in
`run-coqgyxx9`, including 287 unchanged model tests. Native consumers, release
pins and catalog bytes remain unchanged. Evidence: `docs/evidence/native-cut-storage-2026-09-07/`.

Next BG-057: implement the private fixed-storage reservation/cancellation owner
and qualify its bounds, identity and exhaustion with source omission controls.
Native source integration and QEMU acceptance follow separately. Explicit effect
record retirement is required before credit reuse; the first slice denies an
occupied pool rather than importing Python eviction semantics. BG-058 retains
cleanup provenance, BG-060 sustained reuse and BG-033 recovery. The 190-case native
checkpoint and BG-056 producer source-closure limitation remain unchanged.

layout/ retains the standalone source, compiler commands/version, raw stdout/stderr, host executable and target library. This source defines only a proposed representation; no constructor, state machine or native operation executes. validation/ retains all local gates. adoption/ retains the contract and handoff. sha256.json seals the package. No independent sign-off is claimed.
