# Journal-owned lifecycle evidence — 2026-09-06

Decision 0040 adds a separate JournalRuntime owner over the existing lifecycle
algorithm. Hooks retain per-service cause and reserve an entire cut before model
mutation. Tokens represent each occurrence; the public wrapper returns no raw
effects for invocation. Ten new cases cover twelve-effect cuts, duplicate force,
background cause after history eviction, unrelated operations, restart/retry,
invalid/capacity denial, unknown plus terminal evidence, and capture/transfer failure.

Commands from `/Users/cam/DEV/sys-init`:

```
python3 scripts/check-runtime-model.py --output /private/tmp/sys-init-journal-runtime-20260906.json > /private/tmp/sys-init-journal-runtime-20260906.log 2>&1
python3 scripts/check-all.py
git diff --check
```

`model.json` / `model.log` retain 156 passing model tests, fourteen distinct
mutation controls and 1,000 bounded benchmark traces. The new control moves
reservation after Model._begin and fails the unchanged-state assertion.
`validation/` retains the successful `out/checks/run-0eypll_z` full run: model
checks, 48 host tests, 37 harness tests and all offline adoption/quality/native
evidence audit gates. No failed implementation test run occurred in this work.

`source/` preserves all model report inputs and affected planning/adoption records.
All model source hashes match the retained files. Original Model, Control and
EventJournal bytes match decision 0039. Final Markdown result/next-step notes were
added after full checks; executable sources and quality inventory were unchanged.
`SHA256SUMS.json` covers every retained file except itself. Historical evidence,
vendored releases and native code were not changed; native execution was not rerun.

This is trusted synthetic model integration, not a Control backend, authenticated
boundary, native effect driver or recovery implementation. Unknown obligations
conservatively block incoming terminal observations. The caller retains unaccepted
input; no native queue or real-time retention is demonstrated. BG-057/BG-033
remain open for bounded unknown-observation/reconciliation policy before production
progress claims. BG-032 retains exact producer mapping and consuming witnesses.
