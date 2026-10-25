# Confirmed-result application evidence — 2026-09-06

Decision 0044 adds ResultApplier: one coordinator per runtime, at most twenty
retained BoundCall contexts, fresh qualification under a trusted execution guard,
and journal acknowledgment. Eight new tests cover separate observations,
reconstructed/foreign/duplicate contexts, stale results after unknown, reentry,
acknowledgment failure before/after commit and single coordinator lifetime.
The new negative control removes the retained-context check and fails by assertion.

Commands from `/Users/cam/DEV/sys-init`:

```
python3 scripts/check-runtime-model.py --output /private/tmp/sys-init-result-applier-20260906.json > /private/tmp/sys-init-result-applier-20260906.log 2>&1
python3 scripts/check-all.py
git diff --check
```

`model.json` / `model.log` retain 181 passing tests, seventeen distinct mutation
controls and 1,000 bounded benchmark traces. `validation/` retains successful
`out/checks/run-uj5cccc8`: model checks, 48 host tests, 37 harness tests and every
offline adoption/quality/historical-native-evidence gate. No failed test run
occurred. Native execution was not rerun; no new target coverage is claimed.

`source/` preserves all model report inputs and affected adoption/planning records.
All report hashes match. Model, EventJournal, JournalRuntime and BoundCall sources
match decision 0043. Final Markdown validation notes were added after full checks;
executable inputs and quality inventory were unchanged. SHA256SUMS.json covers
all retained files except itself. Existing evidence, shared release bytes, runtime
pins and native sources were not changed.

Producer/target/owner values remain synthetic trusted fixtures. The execution
guard blocks reentry and normal lifecycle operations; it is not a thread lock or
an enforcing native authority boundary. Acknowledgment failures preserve known
terminal records and unresolved issued state while closing further application.
No launch, terminal or cleanup observation is synthesized. The explicit observation
steps in tests are independently supplied model events, not native observations.
BG-058 remains active for native target bookkeeping, exact observation mapping
and fresh consuming witnesses. Unknown reconciliation and native force remain
unsupported, and existing bypass APIs are outside this coordinator's contract.
