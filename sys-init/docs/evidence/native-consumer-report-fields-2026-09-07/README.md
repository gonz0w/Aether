# Native consumer report fields — 2026-09-07

Decision 0133 / BG-056. Focused command `python3 -m unittest discover -s tests -p
'test_harness_native*.py'` passes 57 tests. Four new tests cover all 50 retained
report variants, malformed fields/types/bounds, required worker pins and rejection
before linked receipts. Routing tests inject a parsed invalid consumer object
after real manifest verification; they do not alter retained evidence.

`python3 scripts/check-all.py` passes all ten gates in run-k02c23ut with sources
unchanged. Exact commands and hashes are retained in validation/results.json.
Native audit stdout matches decision 0132 exactly; catalog, 24 native inputs and
release locks match the prior baseline. No native execution or sibling changes.

Consumer reports, cases and commands now have exact fields and bounded types.
Existing semantic and artifact oracles remain authoritative. Recorded image/ISO
digests get structural validation only. Producer summary/report and worker/build
receipt field schemas remain separate work. Sequential filesystem checks are not
atomic; I/O deadlines and independent technical/reader review remain open.

All tests passed. Initial mandoc lint flagged three overlong source lines; final
lint, ASCII widths 78/60 and HTML commands pass after reflow. Initial lint output
is retained. Manual reflow and planning/decision validation notes followed the
aggregate run; tested Python source stayed fixed. Independent HTML visual/narrow
layout review is pending. Source copies and the checker diff identify this slice
within the existing dirty checkout. RC1 remains unpublished and pins unchanged.
