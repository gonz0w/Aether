# SDK receipt fields — 2026-09-07

Decision 0137 / BG-056. `python3 -m unittest discover -s tests -p
'test_harness_native*.py'` passes 69 tests. New tests cover all 27 retained SDK
occurrences, malformed nested fields, direct-only nesting, valid multiline patch
text at its limit and routing at four fixed read locations. Routing injects invalid
parsed objects after real manifest verification without altering retained bytes.
The inert serial fixture copies a valid historical SDK receipt so its existing
semantic rejection remains reachable. All attempts passed.

All ten `python3 scripts/check-all.py` gates pass in run-9nf8l3cz with tested
sources unchanged. Exact commands/hashes are in validation/results.json. Four
mandoc lint/ASCII 78/ASCII 60/HTML commands pass. Independent reader/HTML visual
and narrow-layout review remains pending.

Audit stdout equals decision 0136; catalog, 24 native inputs and release locks
match the baseline. Direct/derived records have separate fields and nested
artifact/header/patch checks. Derived input follows one fixed retained path,
requires a matching hash and direct format; no arbitrary recursion occurs.
Patch snippets allow tab/CR/LF and bounded source text. No code is executed.

Structural validation does not repeat patching, tool execution, instruction-site
inspection or ELF acceptance. Further SDK artifact/input correspondence, missing
historical artifacts, filesystem deadline/race limits and independent review
remain BG-056 work. No native/sibling/release-pin/historical-evidence changes;
RC1 remains unpublished. Source copies/diff identify this slice; only planning/
decision validation notes and evidence followed aggregate checks.
