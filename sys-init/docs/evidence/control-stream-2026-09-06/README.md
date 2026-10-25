# Incremental stream evidence — 2026-09-06

Trusted in-memory Python stream with injected logical time on macOS arm64. No
socket, real timer, caller authentication, native delivery or effect execution
is added. Deadlines depend on the trusted driver calling tick/feed/read.

Commands from repository root:

- `python3 scripts/check-runtime-model.py --output /private/tmp/sys-init-stream-final-20260906.json`
  passes 99 tests and nine mutation controls. model.json retains verbose cases,
  caught assertions, source hashes and host identity; model.log is stdout.
- `python3 scripts/check-all.py` passes 99 model/nine controls, 48 host and 37
  harness tests, plus all offline gates. validation/ retains reports/raw logs.
  The native audit checks 215 historical outcomes, not new native execution.
- `git diff --check` passed for tracked changes.

Tests exercise every two-chunk split of a hand-authored request, one-byte chunks
for a maximum-sized frame, invalid headers/trailing bytes, small output prefixes,
backpressure, read/write deadline edges with no progress extension, invalid clocks
and saturation, partial output loss/reconnect replay and encoding-failure cleanup.
Changing >= to > at deadline must cause one assertion failure without test errors.

initial-model.json/log retain the passing 99-test/eight-control run before adding
the deadline mutation. No failed implementation run was observed. source/ retains
final code and documentation. Execution hashes bind exact inputs; result-only
Markdown notes were added afterward. Model source hashes match retained copies.
SHA256SUMS.json covers every file except itself. Existing evidence/pins remain
unchanged. No independent sign-off, native conformance or production claim is made.
BG-050 retains caller binding/scope/revocation and real I/O; BG-032/BG-033 retain
mechanism and execution/recovery contracts where demonstrated gaps require them.
