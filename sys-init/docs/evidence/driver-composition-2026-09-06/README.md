# Driver composition evidence — 2026-09-06

Decision 0049 / BG-058. Eight new cases compose launch result application,
terminal precedence, both cleanup paths, journal backpressure and failure retention.
The event-retention omission control fails by assertion as required.

Commands from the sys-init repository:

```sh
python3 scripts/check-runtime-model.py --output /private/tmp/sys-init-driver-composition-20260906.json > /private/tmp/sys-init-driver-composition-20260906.log 2>&1
python3 scripts/check-runtime-model.py --output docs/evidence/driver-composition-2026-09-06/model.json > docs/evidence/driver-composition-2026-09-06/model.log 2>&1
python3 scripts/check-all.py
git diff --check
```

Both model runs passed 221 tests and 22 distinct mutation controls, including
100 seeded traces and a 1,000-trace benchmark. After the initial run, review added
an explicit maximum-two-service constructor check and extended the existing
profile test to verify rejection before runtime ownership is claimed. Earlier
driver/test sources are under initial-source/. All other model inputs match
source/. Every initial/final report source hash was verified. No failed runs.

validation/ retains run-uwuqaxal: all eight offline gates pass, including 221 model,
48 host and 37 harness tests. sources_unchanged is true. Decision/planning final
validation notes were appended afterward; executable model inputs remain unchanged.
source/ retains model inputs and affected documentation/tracking records.

The trusted driver accepts already acquired endpoint pairs. It does not create
channels or invoke native calls. Tests supply synthetic confirmed-return contexts
and use explicit resource-close/release evidence. Malformed launch replies close
the owner and retain unknown obligations; delivery backpressure retains pending
events. A successful trace does not authenticate replies or establish recovery.

Pre-acquisition capacity, channel creation failures, larger-graph admission,
automatic stop/force handling and fresh native consuming witnesses remain open.
No shared pin, native implementation or historical evidence was changed. No fresh
native execution was performed. SHA256SUMS.json covers all files except itself.
