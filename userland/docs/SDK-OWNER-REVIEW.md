# UL-005 pkg-mgr owner review packet

Prepared for the pkg-mgr maintainer; not sent or approved. Review
[the proposal](SDK-PACKAGE-HANDOFF.md) and the exact input directory recorded in
[owner-bundle.json](evidence/sdk-package-handoff-2026-09-07/owner-bundle.json).
Verify its manifest digest and each regular file's hash, size and mode before
consumption. Do not execute the captured preparation script as a package recipe.
The directory is inert review material, not a local-binary-directory-v2 bundle.

## Recommended first scope

Transport the existing bounded cross-SDK as data for the provisioned build host,
with an explicit second identity for its produced x86-64/native-profile artifacts.
Keep the compiler external and pinned in the first experiment. Do not bundle a
compiler, add links, install a live prefix, enable a service or infer native
runtime compatibility from the host record. This is a recommendation for owner
review, not a selected package format or production target triple.

The bundle preserves original `stage/usr` paths below `sdk/` for review only.
pkg-mgr chooses the final logical prefix/name and recipe. Include musl COPYRIGHT
and retain the archive/patch/build receipts in source provenance. The reference
consumer inventory's 231 files alone is not license or build dependency closure.

## Decisions required before owner implementation

| Decision | Proposed answer / limit |
| --- | --- |
| Package profile | Host-consumed cross-SDK data; explicitly reject presenting compiler target as native ABI acceptance |
| Target representation | Owner-defined way to bind build host, compiler target and exact native profile/producer; current host-binary-target-v1 alone is insufficient |
| File layout | Owner-selected private stage layout; all selected SDK inputs remain separate from host headers/libraries |
| Dependencies | Bind libc/startup/headers and selected adapter objects to consumer records; external tool prerequisites remain explicit |
| Updates | Identify static reverse consumers and require rebuild/requalification when linked inputs change; retain old artifacts |
| Recovery | Existing single-writer/private-root publication limits; no new crash-atomic or hostile-filesystem claim |
| Trust | Research hashes only; source signer/update policy remains UL-016 and package-owner work |

Return owner decisions plus reviewed implementation scope, not a boolean approval
alone. If a new shared requirement is needed, route it through Aether-standards
rather than promoting this local proposal to a standard.

## Implementation and return evidence

Use existing pkg-mgr source verification, recipe phases, stage/state and transport
machinery. Implement only in that owner's task after the target representation is
agreed. First run SDK-01–04/06: stage/import equality, profile/dependency/integrity
rejections, type/destination denial and publication recovery. Then SDK-05/07 add
an imported-SDK consumer and static rebuild tracking. SDK-08 requires the exact
native producer and a separately scoped userland consumption run.

Return immutable source/recipe/plan identities, package records, both private-root
locations, exact commands/environment/tool hashes, every failed and passed attempt,
and before/after state plus cleanup/recovery receipts. Clearly label NOT RUN and
unknown outcomes. Host linking does not satisfy native execution. Userland then
verifies returned inputs and performs the affected consumer checks. Independent
technical review remains separate from owner design approval.
