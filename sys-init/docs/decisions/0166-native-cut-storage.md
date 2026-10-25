# 0166 — Native cut storage and reservation boundary

BG-057, 2026-09-07. Define the first native ownership slice in
[NATIVE-CUT-STORAGE-V0.md](../specs/NATIVE-CUT-STORAGE-V0.md), following decision
0165's actual launch-to-history witness. Choose one twenty-entry effect pool and
six retained cut records; do not multiply the effect bound by retained history.
Use owned source indices rather than self-referential pointers into movable Rust
storage. Native source and resource authority remain in the original Driver.

The first reservation implementation must fail closed when occupied effect
storage cannot be retired under an accepted contract. It may not import Python
history eviction as native permission to forget reclaim evidence. Reservation
and cancellation can be qualified before application, but cannot publish an
Applied receipt or silently acknowledge effects. Preserve serials and cancelled
records. Later disposition/credit retirement is explicit BG-057 work.

Measure a standalone proposed Rust layout on the host and compile the same size
assertions for x86_64-unknown-none with installed Rust 1.98.0. This is a layout
study only: no native consumer source, syscall, runtime state or smoke marker is
changed. Run full local checks and retain inputs/commands. Foundations O-02/04,
I-01/04–06 and E-01–08 apply; no shared standard, release pin, Distribution or
Experience adoption change is required. No independent sign-off is claimed.

## Validation and handoff

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

Review: representation size is separated from total memory and code-size limits. Serial/cancellation retention and an unavailable application interface prevent reservation from masquerading as completion. Unknown effect disposition is never waived into reusable capacity. Documentation impact: native storage contract, standards/quality references and the BG-057 handoff; no CLI or native behavior changes.
