# Native terminal kind collisions — 2026-09-06

Decision 0076 passes 114 native cases: all 89 prior base cases, four new terminal
probes and 21 existing optional-worker regression cases. Actual normal exit 134
versus fault 134 and normal exit 143 versus stop 143 retain distinct kinds despite
equal encoded results. Live sampling reads once; terminal sampling checks three
coherent reads. The kind omission control hits 1036/0.
All 181 frozen inputs unchanged; 44 of 89 prior base clients match, and changed
clients retain their oracles. The rebuilt worker's old modes pass their consuming
regressions. This is standalone NT-01–02 coverage, not bound pending-fact or journal
integration. Next: NT-03 retained-target identity and sampling reservation; NT-04–07,
remaining NB/ND requirements and BG-033 recovery stay open.

`witness/worker/` retains the full rebuilt worker; `witness/` contains exact frozen
producer/consumer inputs, target cases and comparisons. `preflight-builds/` records
107 passing configurations. `validation/` and `adoption/` retain final checks and
current documentation. No failed build or target execution occurred.

## Validation — 2026-09-06

The full pinned native run passes 114 cases: 89 previous base cases, four new
terminal probes and 21 existing optional-worker cases. All 181 frozen inputs are
unchanged. Eight current native consumer files match the executed snapshot; current
worker C and builder source match the retained successful worker build. New raw
sizes are 1784 (terminal-fault-collision), 2160 (terminal-stop-collision), 2000
(terminal-live) and 1752 bytes (terminal-ignore-kind), within 4096 bytes.

`python3 scripts/check-all.py` passes all eight gates in
`out/checks/run-jwemyt39`: 228 model tests, 23 negative controls, 1000 traces,
48 host tests and 37 harness tests. The catalog verifies 1407 historical outcomes
across 39 bundles and 17,565 listed files; these are not distinct current tests.
The catalog checks worker input/ELF correspondence for each optional-worker case.
`git diff --check` and local reference links pass. No failed build or execution
occurred. Full evidence is retained in
`docs/evidence/native-terminal-collisions-2026-09-06/`.

Only validation notes and evidence copies follow checks; runtime sources, tests,
inventory, catalog and pins remain as checked. Next is NT-03 retained-target identity
and sampling reservation, with NT-04–07 and remaining NB/ND/recovery still open.

`SHA256SUMS.json` inventories this bundle except itself. Hashes establish bytes,
not authority or broad conformance. Shared releases and historical manifests
remain unchanged; the fresh witness is appended to the native catalog.
