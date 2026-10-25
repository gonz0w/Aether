# Native launch receipt — 2026-09-06

Decision 0073 passes 84 native cases. Successful launch returns retain the actual
worker/reader and mark the writer transferred before local application. Pending
receipts deny additional invocation/admission and launched-event qualification.
Matching application advances generation once; injected closure preserves receipt
and consumed identity. Controls hit 1030/0 and 1031/0.
All 178 frozen inputs unchanged; 44 of 80 prior raw clients match, and changed
clients pass their prior oracles. This qualifies IR-05–06 in the trusted local
fixture, not missing kernel replies, journal acceptance or recovery.
Next: IR-07 synthetic Started-with-no-return closure. Other NB/ND requirements and
BG-033 unknown-effect recovery remain open.

`witness/` retains the full pinned target run and artifact comparisons.
`preflight-builds/` preserves two source versions and 196 compiler invocations,
including two initial link-size failures. The full target run passes all 84 cases.
`validation/` and `adoption/` retain development checks and final tracking.

## Validation — 2026-09-06

The full pinned native run passes 84 cases; all seven current consumer inputs
match its frozen source hashes. New raw sizes are 3848 (launch-receipt), 3880
(launch-receipt-close), 2088 (launch-keep-writer) and 2168 bytes
(launch-early-generation). The existing binding-admission client is 4080 bytes;
all clients satisfy the unchanged 4096-byte limit.

`python3 scripts/check-all.py` passes all eight gates in
`out/checks/run-h71nacli`: 228 model tests, 23 negative controls, 1000 traces,
48 host tests and 37 harness tests. The catalog verifies 1204 historical outcomes
across 37 bundles and 15,498 listed files; these are not distinct current tests.
`git diff --check` and local reference link checks pass. Evidence is retained in
`docs/evidence/native-launch-receipt-2026-09-06/`, including both initial local
link-size failures. No native build/execution failed in the full consuming run.
Only validation notes and final evidence copies follow checks; runtime sources,
tests, inventory, catalog and pins remain as checked. Next is IR-07 synthetic
Started-with-no-return closure, with real unknown-effect recovery still open.

`SHA256SUMS.json` inventories this bundle except itself. Hashes establish bytes,
not authority or broad conformance. Shared release bytes and historical manifests
remain unchanged; the fresh witness is appended to the native catalog.
