# 0023 — Finite attempts and readiness exhaustion

Accepted for the bounded BG-040 experiment, 2026-09-06. Extend decision 0022
with a three-attempt budget: the initial attempt plus at most two retries.
The budget belongs to the activation attempt sequence, not the worker generation;
reclaiming/replacing a worker must not reset it. Reserve before launching. A
denied reservation changes no counter and creates no worker or channel.

Silent and malformed schedules each reject readiness on all three attempts.
Stop, observe terminal detail 144, close and reclaim each provider before reuse.
Every replacement must have different worker and reader identities. Never launch
a dependent. After three cleanups, a fourth reservation must be denied, accounting
must be empty, and the fixture completes with the existing three-reclaim marker.
This marker reports a successful test of exhausted policy, not a ready service.

Controls: permitting a fourth reservation rejects at 931 after three reclaims,
before a fourth launch; stopping after two attempts rejects at 934 after two
reclaims. Wrong readiness result uses 932, identity reuse 933, cleanup 935.
An unrelated panic, timeout or missing tool cannot satisfy an expected result.
All twenty-three earlier target cases must retain their outcomes.

Use a small allocation-free counter with checked admission rather than a general
restart scheduler. Three is the fixture's declared attempt bound, not a proposed
distribution default. Each attempt has a 10-delivered-interrupt readiness deadline
and existing polling/guest watchdogs. There is one live worker at a time, no new
unsafe code, dependency, ABI, shared standard or production descriptor. Existing
adapter errors remain fatal fixture boundaries, not graceful production recovery.

Keep production time/backoff, operator reset and multi-service fairness separate.
Follow-on before broader automatic-retry claims: cancel or disable an activation
between attempts, preserving the exhausted/cancelled state and preventing late
readiness from authorizing a new launch. Map that policy to the deterministic
model before requiring a native control interface. Existing
`test_T11_finite_retry_budget_and_no_ready_reset` and
`test_T16_stop_cancels_retry_timer` in the
[model suite](../../tests/test_runtime_model.py) supply the finite-budget and
stop-cancellation expectations; native observation/intent mapping is the missing
step, not a new model semantics claim. Full checks, target evidence,
input stability and byte comparisons are required; no historical files change.

## Result

[Target evidence](../evidence/native-retry-budget-2026-09-06/README.md) passes all
27 cases. Both exhaustion schedules complete with three reclaims; extra admission
and early termination reject at 931/934 with three/two reclaims. All twenty-three
older supervisor binaries remain byte-identical and 178 frozen inputs stay stable.
Positive clients are 1,200 and 1,216 bytes. BG-040 remains partial for cancellation,
production timing/backoff and broader framing/authority.
