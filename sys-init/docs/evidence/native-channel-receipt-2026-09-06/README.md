# Native channel receipt — 2026-09-06

Decision 0072 passes 80 native cases. Real channel returns remain owned before
local application; repeated invocation/launch authorization and mismatched local
application deny. Matched application happens once; injected closure preserves
phase, endpoints and consumed issuance. Controls hit 1025/0 and 1026/0.
All 178 frozen inputs unchanged; 44 of 75 prior raw clients match, and changed
clients pass their previous oracles. This qualifies the IR-01–04 creation slice,
not lost kernel replies, journal retirement or complete NB-09.
Next: IR-05–06 bounded launch receipt retention and writer transfer. IR-07 synthetic
absence, other NB/ND requirements and BG-033 recovery remain open.

`witness/` retains the full pinned target run and artifact comparisons.
`preflight-builds/` preserves seven source versions and all 161 probes, including
14 link-size failures and one extraneous invalid-cfg invocation. The final 94 valid
preflight configs pass. `failed-native-attempt/` retains the first run with 39
completed cases before a link-size failure. The fresh final run passes all 80 cases.
`validation/` and `adoption/` retain final development checks and tracking.

## Validation — 2026-09-06

The fresh pinned native run passes 80 cases; all seven current consumer inputs
match its frozen source hashes. New raw sizes are 3824 (receipt-channel), 3912
(receipt-identity), 3984 (receipt-close), 3840 (receipt-skip-phase) and 3792 bytes
(receipt-forget-writer). All are within 4096 bytes.

`python3 scripts/check-all.py` passes all eight gates in
`out/checks/run-kod9o983`: 228 model tests, 23 negative controls, 1000 traces,
48 host tests and 37 harness tests. The catalog verifies 1120 historical outcomes
across 36 bundles and 14,708 listed files; these are not distinct current tests.
`git diff --check` and the new reference link checks pass. Full evidence is in
`docs/evidence/native-channel-receipt-2026-09-06/`, including the incomplete first
native run and local build failures. Only validation notes and final evidence
copies follow checks; runtime sources, tests, inventory, catalog and pins remain
as checked. Next is the separately scoped IR-05–06 launch receipt slice.

`SHA256SUMS.json` inventories this bundle except itself. Hashes establish bytes,
not authority or broad conformance. No shared release or historical evidence was
rewritten; the new witness was appended to the native catalog.
