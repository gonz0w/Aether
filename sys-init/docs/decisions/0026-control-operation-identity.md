# 0026 — Specify control identity before transport

Accepted 2026-09-06 for BG-050 specification and bounded model correction.
[Control v0](../specs/CONTROL-V0.md) separates receipt, operation outcome,
client waiting, cancellation and resource cleanup. It records existing joins and
supersession, and proposes bounded replay without choosing a production transport.

Reject joining shutdown with ordinary stop, even for identical scope. Shutdown
closes future activation admission; ordinary stop does not. Silent join loses
intent, while implicit escalation changes an already-observed operation. Explicit
conflict preserves both callers' semantics; a later shutdown remains possible
after stop completes. Store the shutdown flag in the model operation and include
it in join comparison. No native ABI or old evidence changes.

Validation: demonstrate the original failure, then test both conflict directions,
same-kind stop joining without deadline extension, and rejected partial stop with
no mutation. Run full model/mutation/host/harness/standards checks. No native
behavior changes, so fresh QEMU execution is not required. Existing 215 audited
native outcomes remain historical supporting evidence, not a control-interface test.

Follow-on C07–C10 covers request replay/eviction/identity bounds, client waiting and
real caller authority. No exactly-once, authentication, persistent enablement or
native control delivery claim. BG-050 stays active for those cases and eventual
CLI/transport specification; local specification is not shared-standard promotion.

Result: [retained evidence](../evidence/control-operations-2026-09-06/README.md)
captures the original assertion failure and 37 passing corrected-model tests with
three mutation controls. Full development checks also pass. Only C01–C06's mapped
model semantics are exercised; C07–C10 remain explicit follow-ons.
