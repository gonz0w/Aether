# I/O envelope correspondence — 2026-09-07

Decision 0136 / BG-056. `python3 -m unittest discover -s tests -p
'test_harness_native*.py'` passes 65 tests. New inert controls cover bad magic,
truncation/trailing data, zero/oversized lengths, maximum accepted sizes and
independently changed native/supervisor bytes. The existing wrong-serial fixture
now uses a valid inert envelope, preserving its semantic rejection oracle.
Initial missing fixture imports were corrected; the failed log is retained.

All ten `python3 scripts/check-all.py` gates pass in run-lfrm_fw8 with tested
sources unchanged. Exact commands/hashes are in validation/results.json. Four
mandoc lint/ASCII 78/ASCII 60/HTML commands pass. Independent reader/HTML visual
and narrow-layout review remains pending.

Audit stdout equals decision 0135; catalog, 24 native inputs and release locks
match the baseline. All 22 historical I/O envelopes reconstruct the claimed
native hash and contain their retained supervisor bytes. Reconstruction happens
only in memory; it does not restore a missing original file or execute code.

SDK receipts require separate direct/derived schemas. Direct receipts include
multiline patch old/new source text, which must not use single-line command/path
rules. SDK semantics, missing ISO artifacts, filesystem deadlines/races and
independent review remain BG-056 work. No native, sibling, release-pin or retained
evidence changes. RC1 remains unpublished. Source copies/diff identify this slice;
only planning/decision validation notes and evidence followed aggregate checks.
