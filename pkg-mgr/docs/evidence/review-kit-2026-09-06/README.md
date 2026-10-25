# Review kit and Aether scope correction — 2026-09-06

A private 327-file review kit was assembled from the unchanged host-tested archive
and its retained qualification/publication/repetition evidence. result.json binds
its digest and path. Repeated tar assembly and member-byte checks passed; all three
included evidence checksum manifests verified after relocation. Nothing was sent
or published. This was completed before the maintainer clarified the release scope.

The maintainer then instructed: “skip macos, we are working only on aether, I will
do reviews.” The kit's macOS-oriented release instructions are therefore superseded,
not an outstanding gate. Preserve the kit as historical work; use the current
[Aether release acceptance](../../AETHER-RELEASE.md) for review and next actions.
Cam is assigned to review; no review or native acceptance is claimed complete.

Active project/architecture/release documents now distinguish Aether-only release
acceptance from host development evidence. Old Apple installer reconstruction is
removed as a gate. Sibling tracking was read for current UL-058/UL-059 and BG-058
boundaries; no sibling source was edited or executed. Sibling identities are recorded
in source-inputs.json as observations, not immutable adopted release pins.

The new local release reference is added to the source mapping to keep documentation
links closed. Source assembly is checked only for document/inventory integrity;
a newly assembled source edition is not qualified as an Aether release. Existing
frozen archive bytes, release pins and runtime code remain unchanged. Documentation,
standards and source-assembly checks apply; unrelated runtime/native tests are not
rerun for this scope/documentation change. A security contact remains unspecified.
