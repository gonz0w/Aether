# Native artifact correspondence — 2026-09-07

Decision 0135 / BG-056. `python3 -m unittest discover -s tests -p
'test_harness_native*.py'` passes 63 tests. New controls reject missing/mismatched
worker SDK/tool-lock/libc links and a contradictory I/O supervisor hash injected
at the parsed receipt boundary during real manifest verification. Existing inert
serial fixture now retains a matching inert supervisor, preserving its original
semantic rejection test. No retained artifacts are mutated or executed.

All ten `python3 scripts/check-all.py` gates pass in run-9whx2d2a, with tested
sources unchanged. Exact commands/hashes are in validation/results.json. Four
mandoc lint/ASCII 78/ASCII 60/HTML commands pass. All attempts passed. Independent
reader/HTML visual/narrow-layout review remains pending.

Audit stdout equals decision 0134; catalog, 24 native inputs and release locks
match the baseline. All 22 supervisor links and three links in each of 18 worker
receipts pass. None of 2,997 init consumer ISO hashes has a matching retained
artifact. The first I/O bundle lacks the original envelope; four later bundles
retain worker/native-c.bin. These gaps cannot be repaired with invented history.

A follow-on SDK inventory found two distinct shapes: 19 direct SDK receipt
occurrences and four derived I/O worker receipts. Their semantic scope must be
reviewed before imposing one schema. Further envelope correspondence, SDK
recursion, filesystem deadlines/races and independent review remain BG-056 work.
No native, sibling, release-pin or historical-evidence changes. RC1 remains
unpublished. Source copies/diff identify this slice in the existing dirty tree;
only planning/decision validation notes and evidence followed aggregate checks.
