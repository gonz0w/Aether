# Bounded receipt encoding — 2026-09-06

Host Python encoding/decoding with deterministic model integration on macOS arm64.
This is client receipt serialization only: no authenticated transport, observation/
wait reply encoding, native delivery or actual effect-dispatch loop is implemented.

Commands from repository root:

- `python3 scripts/check-runtime-model.py --output /private/tmp/sys-init-reply-final-20260906.json`
  passes 69 tests and six mutation controls. model.json contains verbose cases,
  caught assertions, source hashes and host identity; model.log records stdout.
- `python3 scripts/check-all.py` passes 69 model/six controls, 48 host and 37
  harness cases, plus all offline standards, quality and native-evidence gates.
  validation/ retains its exact report and raw logs. The native audit verifies
  215 historical outcomes; it does not run a new native target.
- `git diff --check` passes for tracked changes.

A hand-authored golden receipt establishes exact bytes. Tests reject entire
internal submissions, added effects and oversized/cyclic values before
serialization; check normalized scope, Unicode/identity bounds, replay bytes,
malformed responses and ownership after an injected MemoryError. Failed-session
receipt coverage uses a synthetic failed flag, not a transport failure witness.
The new receipt-fields mutation must cause one assertion failure without errors.

initial-model.json/log retain the passing 68-test/five-control run before splitting
out the field-rejection test and adding its mutation. No failed implementation
run was observed. source/ retains final implementation and documentation. Result
Markdown notes were added after full checks; runtime and inventory hashes match
the successful run. SHA256SUMS.json binds every file except itself, and model
source hashes match the retained source. Existing bundles/pins are untouched.
BG-050 retains observation/wait replies, caller enforcement and stream delivery.
No independent sign-off, production guarantee or shared ABI acceptance is claimed.
