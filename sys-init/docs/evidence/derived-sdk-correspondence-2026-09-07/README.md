# Derived SDK correspondence — 2026-09-07

Decision 0138 / BG-056. `python3 -m unittest discover -s tests -p
'test_harness_native*.py'` passes 72 tests. New inert controls cover contradictory
input/artifact/envelope claims, unsupported artifact sets, bad envelope layout
and matching hashes over a mismatched embedded ELF. No retained artifact is
mutated or executed. All attempts passed.

All ten `python3 scripts/check-all.py` gates pass in run-bp3a1s_e with tested
sources unchanged. Exact commands/hashes are in validation/results.json. Four
mandoc lint/ASCII 78/ASCII 60/HTML commands pass. Independent reader/HTML visual
and narrow-layout review remains pending.

Audit stdout equals decision 0137; catalog, 24 native inputs and release locks
match the baseline. All 904 derived input links and eight artifact links match;
all four native envelope payloads equal the worker ELF. The first direct SDK
receipt's sdk/startup/bad-dup artifacts are unavailable and remain structural
claims. No guessed mapping or missing historical artifact is introduced.

Direct SDK semantics, absent artifacts, remaining producer correspondence,
filesystem deadlines/races and independent review remain BG-056 work. No native,
sibling, release-pin or historical-evidence changes; RC1 remains unpublished.
Source copies/diff identify this slice; only planning/decision validation notes
and evidence followed aggregate checks.
