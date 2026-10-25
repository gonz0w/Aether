# Producer receipt consistency — 2026-09-07

Decision 0139 / BG-056. `python3 -m unittest discover -s tests -p
'test_harness_native*.py'` passes 73 tests. New controls check every retained
summary/worker variant, contradictory counts and each dependency field, with
five legitimate normalized count omissions. All 40 counts and 54 dependency links
match. Tests mutate parsed copies, not retained evidence. All attempts passed.

All ten `python3 scripts/check-all.py` gates pass in run-ch5gzenc with tested
sources unchanged. Exact commands/hashes are in validation/results.json. Four
mandoc lint/ASCII 78/ASCII 60/HTML commands pass. Independent reader/HTML visual
and narrow-layout review remains pending.

Audit stdout equals decision 0138; catalog, 24 native inputs and release locks
match the baseline. No extra files are opened by the new comparisons. The 27
producer bundles without workers lack corresponding standalone SDK/libc/tool-lock
files. Of 395 cases, only 45 positive envelopes exist at expected paths; the other
350 envelopes and all producer case serials/ISOs are unavailable there. This does
not expand positive-case auditing into full producer-suite acceptance.

Summary inputs (8,307 path occurrences) and producer sources (3,430) are not
standalone producer files. Bounded source-archive member review is the next
BG-056 scope; no archive extraction or assumed identity is introduced here.
Missing artifacts, filesystem deadlines/races and independent review remain open.
No native/sibling/release-pin/historical-evidence changes; RC1 remains unpublished.
Source copies/diff identify this slice; only planning/decision validation notes
and evidence followed aggregate checks.
