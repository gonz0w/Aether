# Accounted submission delivery evidence — 2026-09-06

Decision 0037 adds an opt-in model delivery owner that reserves eight logical
accounting credits before a fresh submission. Capacity denial leaves lifecycle
state and request sequence unchanged. Tokens transfer once; acknowledgment does
not imply lifecycle observation. Unknown results keep capacity occupied. The
conservative gate may defer new stop/shutdown requests while obligations remain.

Initial command: `python3 scripts/check-runtime-model.py --output /private/tmp/sys-init-accounted-initial-20260906.json`.
`initial-model.json` and `initial-model.log` retain 128 passing tests and eleven
mutation controls before the admission mutation was added. Final command:
`python3 scripts/check-runtime-model.py --output /private/tmp/sys-init-accounted-final-20260906.json`.
`model.json` and `model.log` retain 128 passing tests and twelve mutation controls.
No failing implementation test run was observed in this work. An evidence-copy
command initially used an incorrect planning path; the path was corrected before
manifest verification.

`python3 scripts/check-all.py` passed all eight stages in `out/checks/run-jqqieqrd`.
`validation/` retains the complete run: 128 model tests, twelve mutation controls,
48 host tests, 37 harness tests, and offline standards, experience, distribution,
quality and historical native evidence checks. The native audit verifies retained
evidence; native execution was not rerun and native sources were unchanged.

`source/` preserves implementation, tests, runner and associated planning and
adoption records. Model source hashes match the retained files. Final Markdown
validation notes were added after the full check; tested executable sources were
unchanged. `SHA256SUMS.json` covers every retained file except itself.

This remains a trusted Python model, not native authorization, durable accounting
or exactly-once execution. Stream and AuthorizedStream still use baseline Delivery.
Event-generated effects and exact producer-result mapping remain the next work;
this submission-only wrapper does not account external Model.batch effects.
