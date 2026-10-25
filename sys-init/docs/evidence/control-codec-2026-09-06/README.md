# Control request decoding — 2026-09-06

Pure Python complete-frame decoding with deterministic manager integration on
macOS arm64. No authenticated caller, socket, stream allocation/backpressure,
response codec or native delivery is demonstrated.

Commands from the repository root:

- `python3 scripts/check-runtime-model.py --output /private/tmp/sys-init-codec-model-accepted-20260906.json`
  passes 61 tests and five negative controls. model.json contains verbose test
  output, exact assertions, source hashes and host identity; model.log is stdout.
- `python3 scripts/check-all.py` passes all offline checks. validation/ retains
  the report and raw stage logs: 61 model/five controls, 48 host and 37 harness
  cases. Native evidence audit checks 215 historical outcomes, not new target runs.
- `git diff --check` passed for tracked changes.

The depth and duplicate-key mutation controls each require three assertion
failures without test errors. Hand-authored frames and exact-state assertions
exercise parsing without effects, limits and equivalent logical request replay.
The existing three lifecycle controls remain present.

initial-model.json/log retain the first passing 61-test run before adding codec
mutations. pre-summary-fix-model.json records all five controls passing, while
its log still says three due to the runner's old hard-coded count. The final
runner derives the printed count from the report. No failed implementation run
was observed; the intermediate inaccurate summary is preserved for provenance.

source/ retains final implementation, tests and documentation. Full-run hashes
bind execution inputs; result-only Markdown notes were added afterward. Runtime
and inventory inputs match the passing full run. SHA256SUMS.json binds all files
except itself. Earlier retained bundles and shared release bytes are unchanged.
The boundary remains an experimental local contract, not an accepted shared ABI
or independent owner review. BG-050 retains responses, authority and delivery.
