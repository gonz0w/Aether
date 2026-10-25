# Trusted control receipts — 2026-09-06

[Decision 0027](../../decisions/0027-control-receipts.md) implements the in-process
Control v0 facade and twelve independent cases. `model.json` records 49 passing
tests and three lifecycle mutation controls. The earlier 48-case exploratory run
is retained as `initial-48-tests.log`; the final run adds shutdown snapshot coverage.

Cases cover replay without effects before/after completion, changed replay versus
join, eviction/high-water bounds, malformed requests, cached lifecycle conflicts,
logical wait/disconnect, late-launch ownership, detached snapshots, sequence/ID
exhaustion, ambiguous post-dispatch failure, retired history and shutdown intent.
The runner now records control.py alongside model/test/runner source hashes.

Full validation passes on macOS arm64: 49 model tests/three controls, 48 host,
37 harness, three pinned standards, quality inventory and the historical native
audit of 215 outcomes. Native status remains not-run: no native code changed.

This is one trusted caller with an in-memory 64-receipt cache, not authentication,
durable replay, exactly-once execution, socket I/O or a production control CLI.
Logical waiting samples state without advancing manager time. External encoding
and caller/session authority remain next under BG-050.
