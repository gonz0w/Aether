# Aggregate source snapshots — 2026-09-07

Decision 0143 / BG-056. `python3 -m unittest discover -s tests -p
'test_harness_source_snapshot.py'` passes five tests. Controls compare the exact
current map with legacy discovery/hashing; test chunk/file/total/traversal/count
bounds, symlinks/FIFO, file growth, read errors, pre-open replacement, descriptor
cleanup and changed selected membership. Temporary fixtures do not change retained
evidence. All test attempts passed.

All ten `python3 scripts/check-all.py` gates pass in run-9dv0gmtb with sources
unchanged. Exact commands/hashes are in validation/results.json. Earlier
run-9owdkqzb also passed while documentation was incomplete: an editing script
used the wrong manual filename and stopped. Documentation/inventory were completed
and aggregate checks rerun; both runs are retained. Initial mandoc lint found one
long source line; final lint/ASCII 78/ASCII 60/HTML commands pass after reflow.
Independent reader/HTML visual/narrow-layout review remains pending.

Native audit stdout equals decision 0142; catalog, 24 native inputs and release
locks match baseline. Snapshot limits are 200,000 traversed entries, 10,000 selected
files, 4 MiB/file, 64 MiB total and 64 KiB chunks. No-follow ordinary-file checks
and identity/membership comparisons are sequential, not atomic or filesystem I/O
deadlines. Ancestors above checkout root are outside scope. Existing snapshot
failure/report-publication behavior remains the next review.

No native/sibling/release-pin/historical-evidence changes; RC1 remains unpublished.
Source copies identify this slice within the pre-existing dirty tree. Manual
reflow, planning/decision validation notes and evidence followed final checks;
tested Python/inventory bytes stayed fixed.
