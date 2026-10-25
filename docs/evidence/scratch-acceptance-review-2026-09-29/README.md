# Scratch session acceptance intake — 2026-09-29

Requirement: verify independent userland SCRATCH-SESSION-01–06 acceptance against
our sealed producer delivery and update existing progress and interface references.
Foundations E-01/E-04/E-05/E-08 apply. Forbidden: changing sealed evidence, treating
this volatile fixture as persistent storage, or claiming serial/SI-07/SDK/R1
completion. No runtime, ABI, resource, authority or sibling changes are needed.

Before changes: verify full manifests, producer identity, delivered runtime hashes,
case results, rebuilt owner identities and scoped claims. Use a selected receipt
snapshot plus existing STATE/ROADMAP; no new mechanism or unsafe boundary is needed.
Run the local host and documentation checks. Native execution is attributed to
userland's matched replay; this documentation intake needs no new QEMU run.

## Verified acceptance

The complete529-member consumer seal verifies with manifest SHA256
`0f50c8ede2a2f9ba72281a4d73ff020ab17b4295bbfc80ebbbae06e7a99fef06`.
Its preparation names our unchanged166-member producer seal
`7d72d2a0b3c6cf3b1458a17e22341d5f630f648561c56373d39739f27c623958`.
All303 delivered runtime hashes match this checkout. All26 rebuilt raw and ELF
owner pairs were read back from the hash-verified retained consumer archive and
match our delivered owner bindings. Stack estimates remain contributor-reviewed,
not independent human approval or formal proof.

Userland passes149 capacity plus five legacy native cases,127 Python/configured
Rust/Zig checks,12 independent trace comparisons and100 checker controls.
SCRATCH-SESSION-01–06 is independently accepted for private AENMX007/ABI21.
The exact three-parent totals are21 copies,15 helper replacements,18 admissions
and24 terminal/reclaims; stdout52/stderr19 bytes per parent. Owner-local data and
authority assertions supplement the serial traces; neither alone proves a general
filesystem. The consumer reconciles the old receipt’s host oracle with the stronger
delivered version. Runtime source bytes did not change between them.

consumer/ contains selected receipt copies. Its SHA256SUMS describes the full
original consumer packet, not this selected subset; review.json pins the selected
copies and complete manifest verification. Full native runs are attributed to
userland. This intake changes documentation only; the local127-test host suite,
workflow and offline standards checks pass without rerunning unchanged native code.
No sibling, released pin or prior sealed packet was modified.

## Remaining dependency

Userland still owns the real serial-session composition and its frozen stream,
authority, lifetime/cleanup and negative controls. Those inputs are not delivered.
SI-07 separately awaits its complete versioned bootstrap/transport and rebuilt
runner/bytecount, rather than only decoder tests. Shared SDK adoption, reader
reviews, persistent filesystem, packages and R1 assembly remain separate gates.
The completed scratch replay is no longer a blocker; this acceptance is not a
full interactive-shell or release-readiness claim.
