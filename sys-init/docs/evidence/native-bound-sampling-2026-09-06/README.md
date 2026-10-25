# Native bound sampling — 2026-09-06

Decision 0077 passes 120 native cases: all 114 prior cases and six sampling probes.
Owner/index and actual Worker/full-token checks reject before sampler reads. A
retained terminal fact takes three coherent reads and holds the single pending
position; duplicate reads/admission deny. Actual stale lookup 0x25001/9 closes the
driver while retaining the original target and error. Omission controls hit 1040/0
and 1039/0; four positive probes finish 100/3. All 181 frozen inputs unchanged.
65 of 114 prior clients match byte-for-byte; all prior oracles pass.

Fixtures seed admitted state from actual handles and trusted token/counters to
fit the unchanged 4 KiB bound. This qualifies bounded NT-03 sampling guards and
retention, not full launch-to-sampling composition, journal or recovery. Next is
NT-04 raw partial receipts and native/local error origin; composition, NT-05–07,
remaining NB/ND requirements and BG-033 remain open.

`witness/` retains exact frozen producer/consumer inputs, target cases, comparison
and the reused unchanged worker build. `preflight-builds/` preserves all size
attempts, including failures; final checks and adoption records follow in
`validation/` and `adoption/`. The native run is distinct from size-only probes.
`native-attempts/` retains the initial linker failure and deliberately interrupted
repeat, including frozen source bytes, produced artifacts and partial outcomes.

All eight development gates pass in `out/checks/run-8a7x0aod`. Eight current
consumer files and unchanged worker/builder sources match the retained native
evidence in `docs/evidence/native-bound-sampling-2026-09-06/`.
