# Event journal evidence — 2026-09-06

Decision 0039 implements an isolated logical event journal: twenty-credit cut
reservation, explicit begin/cancel boundary, distinct occurrences including force,
retained caller-supplied lifecycle cause, bounded token history and unknown state.
Twelve new cases cover bounds, stale identities, cause retention, acknowledgment,
allocation failure and driver loss. The journal does not infer or authenticate
cause, invoke Model.batch, or execute a native effect.

Commands from `/Users/cam/DEV/sys-init`:

```
python3 scripts/check-runtime-model.py --output /private/tmp/sys-init-event-journal-20260906.json > /private/tmp/sys-init-event-journal-20260906.log 2>&1
python3 scripts/check-runtime-model.py --output /private/tmp/sys-init-event-journal-final-20260906.json > /private/tmp/sys-init-event-journal-final-20260906.log 2>&1
python3 scripts/check-runtime-model.py --output /private/tmp/sys-init-event-journal-verified-20260906.json > /private/tmp/sys-init-event-journal-verified-20260906.log 2>&1
python3 scripts/check-all.py
git diff --check
```

`initial-model` reports 145 passing tests; `capture-test-model` adds the capture
allocation-failure test (146). Both accidentally execute the event-reservation
mutation twice: fourteen entries represent thirteen distinct controls. The final
`model.json` / `model.log` report 146 tests and thirteen distinct mutation controls.
No failed test runs occurred. Reports/logs are unchanged. Changed earlier runner
and test inputs were reconstructed and verified against each report's original
source hashes; unchanged inputs are in `source/`.

`validation/` retains the successful `out/checks/run-85gcs10u` full run: 146 model
tests, thirteen controls, 48 host tests, 37 harness tests, and all offline adoption,
quality and native evidence audit gates. Native execution was not rerun; the audit
checks historical witnesses only. Final validation Markdown notes were appended
after the full run; tested executable sources and quality inventory were unchanged.

`source/` retains all model report inputs and the changed adoption/planning records.
All model input hashes were verified. `SHA256SUMS.json` covers every retained file
except itself. Existing evidence and shared release bytes were not modified.

BG-057 remains active for lifecycle cause retention and pre-observation admission.
The journal conservatively blocks new cuts behind unresolved work; no production
observation liveness, recovery, memory preallocation or crash-atomic durability
is claimed. Existing submission ledger, wire contracts and native behavior remain
unchanged. BG-032/BG-033 retain producer mapping and native acceptance witnesses.
