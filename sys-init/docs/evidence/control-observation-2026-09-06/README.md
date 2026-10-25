# Observation and wait reply evidence — 2026-09-06

Host Python codecs and deterministic model snapshots on macOS arm64. No real
caller authority, remote clock, stream delivery or native execution is added.

Commands from repository root:

- `python3 scripts/check-runtime-model.py --output /private/tmp/sys-init-observation-final-20260906.json`
  passes 77 cases and seven mutation controls. model.json retains verbose tests,
  assertions, source hashes and host identity; model.log retains stdout.
- `python3 scripts/check-all.py` passes 77 model/seven controls, 48 host and 37
  harness tests, plus all offline standards, quality and native-evidence gates.
  validation/ retains exact reports and raw logs. The native audit covers 215
  historical outcomes and is not a new target witness.
- `git diff --check` passed for tracked changes.

Cases include actual pending/timeout/success/unknown facade results, a synthetic
24-combination state/outcome matrix, nested identity mismatch, malformed/deep
frames, Unicode/identity bounds, mutable-snapshot isolation and injected output
MemoryError without cancellation. A hand-authored unknown observation fixes exact
wire bytes. Existing receipt golden bytes still pass. Removing the identity check
must cause one assertion failure, with no errors, in the named negative control.

initial-model.json/log preserve the passing 77-case/six-control run before adding
the identity mutation. No failed implementation run was observed. source/ records
final source and documentation. Full-run hashes identify execution inputs; only
result Markdown notes were added afterward. Model source hashes match source/.
SHA256SUMS.json binds every retained file except itself. Existing evidence and
shared pins are unchanged. No independent sign-off or production claim is made.
BG-050 retains error replies, delivery bounds, caller enforcement and recovery.
