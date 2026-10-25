# Native raw sampling — 2026-09-06

Decision 0079 passes 125 native cases, including all 120 previous oracles.
Raw capture retains actual signed RAX/RDX/R8 for a coherent terminal sample and
actual stale errors at O1, S and O2. Successful prefixes remain intact; the native
prefix-omission control reaches 1042/reclaimed=1. Four positives finish 100/3.
All 183 frozen inputs unchanged; 65 of 120 prior images match byte-for-byte.

This is standalone raw capture and validation. Combined driver/receipt probes
exceeded 4 KiB in retained size attempts; binding.rs remains byte-identical to
its prior witness and still uses the decoded sampler. Next: a size-bounded driver
composition strategy before integrating raw history. Native malformed injections,
NT-05–07, full launch composition, journal retirement and recovery remain open.

`witness/` preserves the fresh target run and unchanged reused worker build.
`preflight-builds/` retains three unsuccessful composition builds and the passing
standalone build. `rejected-pin/` retains the pre-execution pin typo rejection.
Final validation and adoption records follow. No actual target execution failed.

All nine development gates pass in `out/checks/run-onzug_wc`. Ten current
consumer files and unchanged worker/builder sources match the retained native
evidence in `docs/evidence/native-raw-sampling-2026-09-06/`.
