# Native bundle consistency — 2026-09-07

Decision 0131 / BG-056. `python3 -m unittest discover -s tests -p
'test_harness_native*.py'` passes 50 tests. New controls cover extra/FIFO/link
entries, a file added during hashing, the 20,000-entry traversal cap, and mutation
of an earlier bundle during later auditing. Updated catalog/metadata/verified-
content tests require final rejection of changes previously allowed after capture.
The first focused run failed three old expectations; review also found and fixed
a missing post-hash insertion before the final passing run. Both logs are retained.

`python3 scripts/check-all.py` passes all ten gates in run-djhnko6x; exact commands
and source hashes are in validation/results.json. Four manual commands pass. The
initial retained-tree review found no extras and at most 1,736 entries per bundle,
so no immutable evidence was edited. Editorial follow-up notes in the reference
were reconciled after the aggregate to distinguish completed work from open gaps.

Manifest verification checks full ordinary-file membership before/after hashing
and compares manifest bytes again. Semantic auditing is followed by bundle
reverification. The CLI makes a final full pass and compares catalog bytes before
printing success. These sequential comparisons detect tested persistent mutations,
not restored changes, hostile directory races or changes after final comparison.
Strict receipt JSON/field validation, I/O deadlines and independent review remain
open. No atomic snapshot or new native execution is claimed.

Native audit stdout matches run-718_ig3c; catalog and 24 tracked native inputs
remain unchanged. Released standard gates pass with existing pins; RC1 remains
unpublished. No sibling/retained evidence mutation. Independent reader/HTML visual/
narrow-layout review remains pending. Source copies/diff record this slice within
the pre-existing dirty checkout.
