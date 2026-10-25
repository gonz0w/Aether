# 0037 — Capacity-gated effect delivery

Accepted for the sequential BG-050 model, 2026-09-06. Add AccountedDelivery as an
opt-in experiment; existing Delivery/Stream remain unchanged trusted baselines.
Shared I-01–06/E-04–06 apply via STANDARDS.md. No native calls or result-to-lifecycle
mapping are implemented.

Before a fresh request reaches Control.submit, require an open ledger, no unresolved
obligations, no outstanding capacity reservation, and eight remaining uint64 effect
serials. Reserve eight logical credits: the model can emit at most eight effects
per dispatch. Retained/retired request replay bypasses this fresh-admission gate
because it cannot create effects. Normal request validation still happens first.
Capacity denial produces busy/not-dispatched without consuming a request sequence
or changing lifecycle state. Invalid sequence gaps retain invalid-request behavior.

This deliberately conservative gate can defer fresh joins, stop and shutdown while
earlier effects await acknowledgment. It is not a production scheduling/cancellation
policy. It also leaves fewer than eight final serials unusable. Logical credits
bound accounting slots, not Python allocation or crash-atomic memory reservation.
More selective admission needs a separately tested effect plan before widening.

Capture returned effects before encoding the receipt. Reserve their exact tokens
in the ledger against the returned operation, release unused credits and retain
the token batch alongside raw effects. Replay produces no new tokens. A failed
dispatch retains its credits and Control's failed state because effects may be
unknown. Failed token reservation poisons Control and retains raw effects/credits
for diagnosis; no unaccounted transfer is allowed. Output failure cannot discard
successfully reserved tokens. Failure recovery remains unsupported.

AccountedDelivery forbids legacy take_effects. issue_obligations validates the
entire pending batch, marks its tokens issued and transfers that immutable tuple
once. This is invocation responsibility, not execution. A partial issue failure
closes the driver with unknown obligations; no retry is inferred. acknowledge
records the ledger result only and never injects Model.batch. Unknown retains
backpressure. driver_lost closes mutation and connection, preserves unknown
accounting and poisons Control; no replacement driver is installed.

Test capacity/serial denial before mutation, retained replay while ledger occupied,
single token transfer, receipt encoding failure, unknown acknowledgment, failed
reservation/dispatch and driver loss. Add an admission-gate mutation control.
Run model/full checks and retain evidence. Next specify event-generated effect
accounting and exact producer result/terminal/cleanup mapping, including capacity
before observation cuts. This subset accounts submission effects only; external
Model.batch remains trusted and is not yet covered by the driver.

Validation on 2026-09-06 passed: 128 model tests, twelve mutation controls,
48 host tests, 37 harness tests and every offline adoption/quality/evidence gate.
Evidence: [accounted delivery](../evidence/accounted-delivery-2026-09-06/README.md).
This is model evidence; native behavior was unchanged and no fresh target run
was performed.
