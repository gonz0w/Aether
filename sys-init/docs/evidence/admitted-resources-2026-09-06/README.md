# Admitted resource cleanup evidence — 2026-09-06

Decision 0048 / BG-058. Seven new model tests cover six cleanup orders, retained
pending registration, failed and mismatched resource returns, two-target contention,
64-token exhaustion, duplicate/stale identities and cleanup without a wait.
The wait-release omission control fails by assertion as required.

Commands from the sys-init repository:

```sh
python3 scripts/check-runtime-model.py --output /private/tmp/sys-init-admitted-resources-20260906.json > /private/tmp/sys-init-admitted-resources-20260906.log 2>&1
python3 scripts/check-all.py
git diff --check
```

The model run passed 213 tests and 21 distinct mutation controls, with 100 seeded
traces and a 1,000-trace benchmark. model.json/model.log retain that run.
validation/ retains run-419m7b9a: all eight offline gates pass, including 213 model,
48 host and 37 harness tests. sources_unchanged is true. No failed attempts occurred.

source/ retains exact model inputs and affected tracking/decision documents.
Every model source hash was verified against the retained copy. Decision/planning
validation notes were appended after the full check; executable model inputs
remain unchanged. reviewed/ retains the previously frozen producer sources used
for this contract, with identities in reviewed-files.json.

This is a trusted post-admission fixture with reader, native target and optional
wait only. Supplied return contexts are synthetic, not authenticated native
records. A completion/cancellation status cannot release the wait. Only explicit
release qualifies. Projection does not itself mutate lifecycle ownership; the
integration tests explicitly deliver cleaned after all resource conditions hold.

Pre-launch acquisition, routing both launch outcomes, complete driver composition,
helpers/devices and fresh native consuming witnesses remain outside this result.
No native source, shared release or pin changed; no native execution was rerun.
SHA256SUMS.json covers all retained files except itself.
