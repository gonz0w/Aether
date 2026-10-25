# Logical control contract and model correction — 2026-09-06

[Decision 0026](../../decisions/0026-control-operation-identity.md) and
[Control v0](../../specs/CONTROL-V0.md) define the next logical facade scope.
The native runtime and transport remain unchanged.

`before-tests.log` records 37 model tests with one expected failure: equal-scope
ordinary stop and shutdown joined instead of rejecting conflicting intent.
`model-before.py` retains the unfixed model. The corrected model stores shutdown
intent on operations and compares it during joining. `model-after.json` records
37 passing tests and all three existing mutation controls. New cases test both
conflict directions, same-kind deadline-preserving joins and partial-stop rejection
without effects. No replay/authorization/transport coverage is inferred.

Full validation passes on macOS arm64: 37 model tests/three controls, 48 host,
37 harness, all three pinned standards, quality records and the historical native
audit of 215 outcomes. The full report/logs are under `validation/`. Native status
is not-run; this change affects the deterministic model only.

The logical contract maps C01–C10 and explicitly leaves request replay, eviction,
finite client waits and real authority unimplemented. BG-050 stays active. Source,
specification and process snapshots are retained with this bundle's manifest;
historical native evidence and shared pins were not changed.
