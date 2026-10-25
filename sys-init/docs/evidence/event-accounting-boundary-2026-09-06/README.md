# Event-accounting boundary evidence — 2026-09-06

Decision 0038 records six new executable characterization cases and a source
review before changing delivery. Exact expected traces demonstrate twelve effects
in one cut, repeated force for one generation, background effects after operation
completion or outside the active operation scope, and reclaim acknowledgment
without cleanup. The twenty-effect bound is a conservative source derivation,
not an exhaustive test result or a production budget.

Commands from `/Users/cam/DEV/sys-init`:

```
python3 scripts/check-runtime-model.py --output /private/tmp/sys-init-event-boundary-20260906.json > /private/tmp/sys-init-event-boundary-20260906.log 2>&1
python3 scripts/check-all.py
git diff --check
```

`model.json` / `model.log` retain 134 passing tests, twelve mutation controls and
1,000 bounded benchmark traces. `validation/` retains the full successful run
from `out/checks/run-36iivj3_`: 134 model tests / twelve controls, 48 host tests,
37 harness tests, and all offline standards, quality and historical native audit
gates. No failed test runs occurred in this work. The new cases characterize
current behavior; they do not establish a native policy for duplicate force.

`source/` retains every model report input and the changed research, decision,
adoption, coverage and planning documents. Model report hashes match these
retained files. Final validation notes were appended after the full run; tested
executable inputs and quality inventory remained unchanged. `SHA256SUMS.json`
covers all retained files except itself. Earlier evidence was not changed.

Native runtime behavior, shared pins and existing token/wire contracts are
unchanged. This is synthetic model/source evidence, not native result decoding,
real observation retention, event journal implementation or recovery. BG-057
captures the next bounded journal experiment. BG-032/BG-033 retain exact producer
mapping and recovery witnesses. No kernel mechanism blocker is established.
