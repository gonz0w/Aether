# Public source candidate assembly

> Scope update, 2026-09-06: Aether is the only release target. This document
> preserves the earlier host-preview work; its macOS release/setup gates are
> superseded by [Aether release acceptance](AETHER-RELEASE.md). Host results remain
> development evidence and are not native package-manager acceptance.

Run `python3 tests/check-public-source.py` from the full development checkout.
This creates a local unpublished candidate; it never tags, signs or uploads it.
release/files.tsv is an exact sorted destination/source mapping with no globbing.
New files enter only through review of that list. The candidate README comes from
release/README.md. Runtime files, fixtures, mdoc pages and all vendored standard
bytes are copied unchanged. Link/special files, unsafe paths, missing sources,
duplicate destinations and unexpected broken documentation links fail.

For first-party Markdown, links to explicitly excluded history/planning/research
or sibling repositories become labeled plain-text omitted references. A short
edition notice distinguishes retained development observations from acceptance
for the candidate. Other prose is preserved. Each link change is listed in
 documentation-edits.json under the printed run root. Immutable vendored Markdown
is never edited, including historical relative references within pinned snapshots.
This mechanical edition still requires independent technical and reader review.

source.tar and repeat.tar must be byte-identical; host tar extraction must match
all file contents and ordinary modes. SOURCE-MANIFEST.json identifies output bytes,
while input-files.json records the exact original inputs and documentation overlay.
Run the normal full suite and required manual/compiler checks from extracted/pkg-mgr
before making any candidate acceptance claim. Assembly does not supply that evidence.

The selected package retains the normal development inventory and synthetic native
fixtures. Native integrations and zlib workflows remain explicitly outside preview
qualification. No external zlib archive or host tool is bundled. The package omits
plans, agent instructions, research guidance, historical evidence and generated roots.

Source assembly tools and the source-review documents describe full-checkout work;
they are retained for inspection and are not standalone assembly entry points from
the public package, which lacks excluded development inputs and the README overlay.
Use the candidate README for supported extracted-tree validation commands. Actual
security contact, pinned acquisition/setup, broader boundary/failure qualification,
independent reviews and publication approval remain release gates.
