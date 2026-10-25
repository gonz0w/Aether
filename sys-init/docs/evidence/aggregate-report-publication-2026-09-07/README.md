# Aggregate report publication — 2026-09-07

Decision 0144 / BG-056. `python3 -m unittest discover -s tests -p
'test_harness_report_publication.py'` passes six tests. Temporary-file controls
verify atomic replacement failure preserves old bytes and cleans temporary files.
Mocked gate/snapshot controls cover initial/final snapshot failure, interrupt,
transient gate-report failure preserving completed checks, final-publication failure
without a summary and normal success. No historical files or gates are executed
by these fixtures. All test attempts passed.

All ten `python3 scripts/check-all.py` gates pass in run-k7q8lxv3 with tested
sources unchanged. Exact commands/hashes are in validation/results.json. Initial
mandoc lint found two long source lines; final lint/ASCII 78/ASCII 60/HTML commands
pass after reflow. Initial output is retained. Independent reader/HTML visual and
narrow-layout review remains pending.

Native audit stdout equals decision 0143; catalog, 24 native inputs and release
locks match baseline. Success fields stay compatible; failure records add bounded
stage/type/message details. Final publication failure returns nonzero with escaped
stderr and no terminal summary; prior complete report may remain running. Atomic
replacement does not imply crash durability. Output-directory creation, broken
pipes, fatal/repeated signals and blocking filesystem deadlines remain limits.

No native/sibling/release-pin/historical-evidence changes; RC1 remains unpublished.
Source copies/diff identify this slice. Manual reflow, planning/decision validation
notes and evidence followed checks; tested Python/inventory bytes stayed fixed.
