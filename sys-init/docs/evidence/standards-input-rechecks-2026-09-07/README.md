# Standards input rechecks — 2026-09-07

Decision 0121 / BG-056, macOS arm64 host checks. Fifteen focused tests pass:
`python3 -m unittest discover -s tests -p 'test_harness_standard*.py'`
(11 tests) and the same command with `test_harness_offline_locks.py` (4 tests).
An earlier passing focused run preceded the additional real-child test.
All attempts are retained. `python3 scripts/check-all.py` passes all ten gates
in run-4ijd1_d1; commands/source digests are in validation/results.json.

Three new tests cover 39 subcases across all three wrappers: six persistent
mutations during initial verification (18), the same mutations during mocked
child execution (18), and real children that print success text then modify
their own synthetic source (3). Mutations cover lock, manifest, payload, extra
file, missing file and symlink replacement. Prechecks prevent invocation;
postchecks prevent success. Real-child stdout remains visible and exit is 1.
No original checker/release file is mutated by the synthetic controls.

Three scoped wrapper diffs are retained. Lock and manifest bytes and digest maps
remain live only for the invocation; bounded path/type/read/traversal checks are
reused. Persistent changes at comparison points reject, but restored mutations,
concurrent directory swaps, interpreter/import dependencies and mutation after
final comparison are not closed. This is not atomic verified execution.
Failed children retain the previous CalledProcessError behavior.

All three standard stdout streams match decision 0120 exactly. Lock bytes and
24 native input hashes are unchanged; no new native behavior or target run is
claimed. All released-standard gates pass; RC1 remains unpublished. Twelve
manual lint/terminal/HTML render commands pass; independent reader/HTML visual
review and narrow-layout publication review remain pending. Source copies reflect
this slice within the larger existing dirty checkout. No runtime dependency added.
