# 0167 — Fixed Rust reservation owner

BG-057, 2026-09-07. Implement decision 0166's reservation-only slice as private,
allocation-free Rust logic, not yet imported by the native consumer. A nonzero-size
owner anchor is exclusively borrowed at construction; reservation keys retain that
borrowed identity and serial. No Clone owner, imported nonempty storage, application,
acknowledgment, native source constructor or reset API is provided.

Accept only one/two canonically ordered Launched member indices in this empty-
lifecycle slice. Reserve one of six retained records and twenty credits together.
Duplicate reservation is inert; cancellation retains membership/serials and frees
unused credits. Occupied effects, closed state, record or u64 exhaustion deny before
mutation. Last u64 serial is conservatively unavailable to avoid a wrapped next ID.
Later phases require the separate native application/provenance integration.

Host Rust tests must cover canonical/invalid membership, foreign owner/key,
duplicate/Busy behavior, six cancelled records, serial and effect exhaustion,
closed owner and no partial reservation. Three omission controls reset serials,
erase cancelled records or reserve credits before denial. Compile the same module
for x86_64-unknown-none and assert layout. Add it to the required existing host Rust
logic gate and run all local checks. No fresh native behavior is claimed: none of
the twelve current native consuming sources change. BG-057/BG-058 retain binding,
application, disposition retirement and fresh QEMU acceptance.

## Validation and handoff

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

Review: the module allocates no heap storage, owns no native handle and has no unsafe code. All fallible validation precedes the reservation write; cancellation cannot recycle records or serials. Tests mutate private exhausted state only inside the module. The first aggregate run was interrupted after the inventory-update helper failed to match a multiline declaration; the corrected final run and original attempt are retained. The subsequent full run caught the source-selection regression test still expecting the old list; its expected inputs now include both new Rust files, and the failed run is retained. The next run passed all ten Rust groups but rejected the old aggregate count of nine; the explicit required count is now ten, with that failed aggregate and successful Rust inputs retained. Documentation impact: storage reference, quality coverage, aggregate source capture and source-matched command inventory. No independent sign-off is claimed.
