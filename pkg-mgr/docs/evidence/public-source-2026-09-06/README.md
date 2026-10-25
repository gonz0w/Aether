# Public source candidate witness — 2026-09-06

Scope: locally assembled unpublished candidate, not release approval. The explicit
allowlist selects 187 files. Archive SHA-256:
`7a09ad7b9689568b253db6a573cbe577a3238a59face27bedecd22722159af42`.
The retained root is
`/private/var/folders/2k/hbwvd2qn4cb988kpjk1wcn800000gn/T/pkg-public-source-uq8kxmnb`.
It contains source.tar, repeat.tar and extracted/pkg-mgr. Both archives match;
host tar extraction matches exact file bytes/modes and the embedded output manifest.

The oracle is the explicit destination/source map, preserved runtime/vendor bytes,
marked omitted development references and existing host-test semantics. Unsafe
paths, included history, duplicate destinations, missing/link inputs and unexpected
broken documentation links must reject. No network fetch or publication action.

input-files.json binds original dirty-tree inputs, including the README overlay,
allowlist and assembler. documentation-edits.json records 81 links converted to
plain-text omitted references; edition notices are added to first-party docs.
The three manuals, all immutable standards and other non-Markdown inputs remain
unchanged: 159 selected files, checked in unchanged-inputs.json. Vendor snapshots
retain historical references by design; they are never transformed or used as a
current-state index. Independent prose/reader review remains required.

From the extracted candidate, `sh tests/check.sh` passes all sixteen fixtures,
three pinned standards checks, whole-shell lint, watchdog controls and live
minisign fixture verification in 147.048 seconds under a 600-second deadline.
suite.log/result.txt retain the run. The extracted host preflight and
`python3 tests/check-manuals.py --render-required --binary-example` pass; setup and
manual receipts, bytecount log and post-test source preservation check are retained.
These checks do not establish network confinement or independent reviewer approval.

Six negative controls reject traversal, excluded history, duplicates, missing
inputs, input symlinks and unknown broken links. The initial control harness used
a noncanonical macOS /var alias, causing the parent-link guard to reject before
the intended missing-input assertion. initial-controls.py/log preserve that failed
harness assumption. Canonicalizing the temporary control root, as the production
entry point already does, exercises all six intended rejections. No product bypass
or relaxed guard was introduced.

Later tracking/documentation updates are checked separately in development.log,
standards.log and whitespace.log. This candidate predates those updates; its hash
must not be used as the identity of the subsequent checkout. Public content/reader
review, broader boundary/failure work, pinned setup acquisition, independent build
review, a monitored security contact and publication decision remain open. The
archive has not been signed, tagged or uploaded.
