# Companion priority review — 2026-09-06

The maintainer requested a blocker review before the next concurrency item.
inputs.json and numbered snapshots retain the exact owner records and local
implementation excerpts reviewed. This is source/document inspection, not fresh
consumer execution, verification of their full evidence packets or owner sign-off.

Decision: SI-05 first, UP-02 UL-059 next, UP-02 UL-067 next, then resume R1-03
concurrency/engine work. ROADMAP contains acceptance and compatibility boundaries;
STATE contains the next action. The review changes those planning files only.

Sys-init requests a separate init-compatible 8192-byte supervisor profile because
its best complete guard needs 4528 bytes. Current ABI 6 remains 4096 bytes; ABI 8
is not a compatible substitute. Local loader code already maps supervisor code by
page count for supported profiles, which supports an additive investigation but
is not proof of new-profile correctness or cleanup.

Userland waits on explicit runner-local output/no-child lifecycle and a separate
cat child-diagnostic/admission contract. Review possible common transport once,
then qualify their distinct resource inventories and independent owner verifiers.
pkg-mgr's current native command transport is accepted at 53 cases; actual package
installation needs shell/tools, filesystem namespace/persistence and native
artifact/durable-publication contracts. No small kernel-only change closes R1-05.

No implementation, ABI, consumer pin, sibling file, message or shared standard
changed. Risk is bounded by separate opt-in profiles and regression/consumption
requirements, not eliminated. Host/standards/workflow checks validate the local
planning change; no new QEMU claim follows. Prior kernel evidence remains intact.
