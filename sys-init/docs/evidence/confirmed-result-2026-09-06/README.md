# Confirmed-result qualification evidence — 2026-09-06

Decision 0043 implements pure trusted qualification of selected ABI-6 launch,
stop and reclaim returns. BoundCall retains exact issued token, original opaque
owner, producer identity and expected native target. Eight new tests cover
success/error returns, exact identity matching, force exclusion, malformed input,
unknown rejection, retired context and unchanged journal/lifecycle ownership.
The new omission control demonstrates that later EBADF must not qualify an
already-unknown obligation.

Commands from `/Users/cam/DEV/sys-init`:

```
python3 scripts/check-runtime-model.py --output /private/tmp/sys-init-confirmed-result-20260906.json > /private/tmp/sys-init-confirmed-result-20260906.log 2>&1
python3 scripts/check-all.py
git diff --check
```

`model.json` / `model.log` retain 173 passing model tests, sixteen distinct
mutation controls and 1,000 bounded benchmark traces. `validation/` retains the
successful `out/checks/run-nbyn4v2s` full run: model checks, 48 host tests,
37 harness tests and every offline adoption, quality and historical native audit
gate. No failed test run occurred. Native execution was not rerun; the audit
verifies retained witnesses and adds no new target coverage.

`source/` retains all model report inputs and affected adoption/planning records.
Source hashes match the report. Final Markdown validation notes were added after
full checks; executable inputs and quality inventory were unchanged. SHA256SUMS.json
covers all retained files except itself. Existing journal/lifecycle/native source,
shared release bytes, consumer pins and historical bundles were unchanged.

The producer hash and native-target values in tests are synthetic fixtures, not
validated native artifacts or authority. Expected slot/generation bookkeeping is
trusted input to this pure classifier and still needs native binding evidence.
The returned immutable postcondition is not Model.batch, journal acknowledgment,
reconciliation or cross-core/device cleanup. Repeated pure qualification while
still issued has no side effects. BG-058 remains active for serialized application,
separate observations and fresh native adapter acceptance; unknown/force remain
unsupported. This is not an authenticated wire decoder or a recovery service.
