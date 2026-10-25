# Native linked receipt fields — 2026-09-07

Decision 0134 / BG-056. `python3 -m unittest discover -s tests -p
'test_harness_native*.py'` passes 61 tests. Four new tests cover all 130 consumed
linked receipts (45 summaries, 45 producer reports, 18 service-worker receipts,
22 I/O supervisor builds), malformed nested fields, collection/integer bounds,
and validation at each linked parsing site before further receipt use.
Routing controls inject invalid parsed objects after real manifest checks without
modifying retained evidence. Recorded commands are never executed by the audit.

`python3 scripts/check-all.py` passes all ten gates in run-boauxp1k with tested
sources unchanged. Exact commands and source hashes are in validation/results.json.
All four mandoc lint/ASCII 78/ASCII 60/HTML commands pass. Independent reader,
HTML visual and narrow-layout review remains pending.

The initial run exposed an old minimal synthetic build missing newly required
fields; it now supplies inert command/variant/supervisor digest fields so its
existing wrong-serial oracle remains exercised. The next run exposed a catalog
name-key error in the new test setup; corrected. Both failed logs are retained.
No implementation validator was relaxed to accept malformed historical data.

Audit stdout matches decision 0133 exactly; catalog, 24 tracked native inputs and
release locks match the prior baseline. No native behavior, sibling repository,
release pin or retained evidence changes. RC1 remains unpublished. Structural
validation does not establish extra ELF/ISO/tool/SDK correspondence or producer
suite execution. SDK recursive validation, unconsumed I/O worker reports,
filesystem deadlines/races and independent review remain separate work.

Source copies and checker.diff isolate this slice within the existing dirty tree.
Only decision/planning validation notes and evidence were added after aggregate
checks; tested implementation and inventory bytes stayed fixed.
