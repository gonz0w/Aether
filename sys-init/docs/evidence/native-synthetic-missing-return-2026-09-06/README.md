# Synthetic missing-return schedules — 2026-09-06

Decision 0074 passes 89 native cases, including IR-07 synthetic creation/launch
absence. The real start guards run but the selected syscall is deliberately
omitted. Closure retains Started, pending identity and unknown outcome; no invented
error or retry is accepted. Controls hit 1033/0, 1034/0 and 1035/0.
All 178 frozen inputs unchanged; 44 of 84 prior raw clients match, and changed
clients pass prior oracles. This is synthetic transition coverage executed in a
native fixture, not an actual lost kernel reply or recovery witness.
The binding acceptance review keeps remaining NB gaps explicit. Next: ND-02
terminal-kind contract against the frozen producer; ND-03–05 and BG-033 remain open.

`witness/` retains the full pinned run and artifact comparisons. `review/` and
`reviewed-files.json` preserve the binding audit basis before checkpoint notes.
`preflight-builds/` retains one source snapshot and 103 successful builds.
`validation/` and `adoption/` retain final checks and current documentation.

## Validation — 2026-09-06

The full pinned native run passes 89 cases; all seven current consumer inputs
match its frozen source hashes. New raw sizes are 2752 (missing-channel), 3368
(missing-launch), 1456 (missing-skip-close), 1544 (missing-invent-error) and 1904
bytes (missing-forget-writer). All clients satisfy the unchanged 4096-byte bound.
All 103 local configuration builds and the full target run pass without failures.

`python3 scripts/check-all.py` passes all eight gates in
`out/checks/run-wo779a2_`: 228 model tests, 23 negative controls, 1000 traces,
48 host tests and 37 harness tests. The catalog verifies 1293 historical outcomes
across 38 bundles and 16,323 listed files; these are not distinct current tests.
`git diff --check` and local reference link checks pass. Evidence is retained in
`docs/evidence/native-synthetic-missing-return-2026-09-06/`. Only validation notes
and final evidence copies follow checks; runtime sources, tests, inventory, catalog,
review findings and pins remain as checked. Next is ND-02 terminal-kind contract
work; the binding review retains remaining NB/ND and real recovery gaps.

`SHA256SUMS.json` inventories this bundle except itself. Hashes establish bytes,
not authority or broad conformance. Shared releases and historical manifests
remain unchanged; the fresh witness is appended to the native catalog.
