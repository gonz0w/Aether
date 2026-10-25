# Producer source correspondence — 2026-09-07

Decision 0141 / BG-056. `python3 -m unittest discover -s tests -p
'test_harness_native*.py'` passes 77 tests. New controls cover all retained source
maps, unknown missing sources, conflicting available sources and exception scope
across changed pins/schema/digests and conflicting present metadata. All 3,420
available entries match; ten exact historical omissions remain explicitly unverified.

All ten `python3 scripts/check-all.py` gates pass in run-me3ukw5u with tested
sources unchanged. Exact commands/hashes are in validation/results.json. Initial
mandoc lint flagged one overlong source line; final lint/ASCII 78/ASCII 60/HTML
commands pass after reflow. The initial result is retained. Independent reader/
HTML visual/narrow-layout review remains pending. All test attempts passed.

Audit stdout equals decision 0140; catalog, 24 native inputs and release locks
match the baseline. Omission exceptions require exact manifest hashes, normalized
schema and exact missing metadata names/digests. New/repinned evidence inherits
no exception; conflicting present entries always reject. No missing artifact is
invented and no historical receipt changes. Full source closure for those five
snapshots is not claimed. STANDARDS.md records E-01/E-05/E-08 scope and revisit.

Missing artifacts, independent review and filesystem deadline/race limits remain
BG-056 work. No native/sibling/release-pin changes; RC1 remains unpublished.
Source copies/diff identify this slice. Manual reflow, planning/decision validation
notes and evidence followed aggregate checks; tested Python/inventory bytes stayed
fixed. Next work consolidates limitations and prioritizes operational gaps.
