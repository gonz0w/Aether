# Error replies and memory delivery evidence — 2026-09-06

Sequential trusted Python model on macOS arm64. No socket, native control,
authenticated caller, wall clock or effect execution is implemented. The driver
accepts complete frames and transfers effects once; execution acknowledgment and
crash recovery remain outside the experiment.

Commands from repository root:

- `python3 scripts/check-runtime-model.py --output /private/tmp/sys-init-delivery-final-20260906.json`
  passes 89 tests and eight mutation controls. model.json contains verbose cases,
  assertion controls, host identity and source hashes; model.log is stdout.
- `python3 scripts/check-all.py` passes all offline gates: 89 model/eight controls,
  48 host and 37 harness cases. validation/ retains exact reports and raw logs.
  Native audit verifies 215 historical outcomes, not new target execution.
- `git diff --check` passed for tracked changes.

Tests cover fixed error combinations/golden bytes, extra/unbounded error fields,
reply/effect backpressure, eight-effect transfer, disconnect and replay, malformed
input, logical and lifecycle rejection, post-dispatch failure, receipt encoding
failure and failed fallback encoding. The error-disposition mutation must cause
one assertion failure without test errors. No native enforcement claim follows.

initial-model.json/log preserve the passing 88-test/eight-control run before the
maximum batch case. No failed implementation run was observed. source/ retains
final implementation and documentation. Full-run hashes bind execution inputs;
result-only Markdown notes were added afterward. Model source hashes match the
retained copies. SHA256SUMS.json covers every file except itself. Existing pins
and historical bundles are unchanged; no independent sign-off is claimed.
BG-050 retains incremental framing/deadlines, authority and real delivery; the
trusted driver retains execution responsibility after take_effects.
