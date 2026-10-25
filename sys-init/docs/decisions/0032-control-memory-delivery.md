# 0032 — Error replies and bounded in-memory delivery

Accepted for BG-050, 2026-09-06. Exercise response loss and ownership without a
socket or kernel interface. Shared I-01–06/E-04–06 apply via STANDARDS.md. This
is a sequential trusted model driver, not an authentication or stream boundary.

Error replies have exactly schema=sys-init-control-error-v1, code and disposition.
Codes invalid-frame, invalid-request and busy require disposition not-dispatched;
internal-error requires unknown. There is no echoed payload, exception, caller,
sequence or operation identity. One outstanding reply supplies local correlation;
this envelope is not a multiplexed protocol. Existing strict JSON rules apply,
with depth one and the same 4096-byte body limit. Error encode validates before
serialization; unknown fields or mismatched combinations reject as error-reply.

Delivery(Model) constructs and retains the model's sole Control facade. It starts
connected and owns one reply slot (at most 4100 bytes) and one effect batch (at
most eight model effects). receive accepts one complete bounded request frame;
there is no incremental buffering. A pending reply rejects another receive with
local Backpressure before parsing or dispatch. If effects await transfer, receive
returns busy without dispatch. No queue grows on repeated input.

Decode failure queues invalid-frame and closes input until reconnect; no frame
resynchronization occurs. Logical validation failure queues invalid-request and
does not consume a sequence. Lifecycle rejection remains a normal receipt.
Unexpected dispatch failure returns internal-error/unknown; the Control failure
guard remains set. Unexpected receipt encoding failure also returns unknown,
with the cached receipt and captured effects retained. Do not translate either
failure into proof of no effects. Fallback error encoding failure propagates;
manager state and effect ownership are retained for diagnosis.

The owner captures first-dispatch effects before encoding the receipt. take_effects
transfers the entire batch once to the trusted driver, which then owns execution;
it does not acknowledge actual execution. The deterministic model emits at most
one effect per service per dispatch (eight services). A bound violation poisons
the Control and raises for diagnosis rather than silently dropping effects.
No real process is launched by this experiment. Driver crash/retry after transfer
needs a separate execution-acknowledgment/recovery contract.

read_reply removes the reply bytes. disconnect discards only the connection reply
and closes input; it cannot clear effects, receipts, the sequence high-water mark
or failed state. reconnect reuses this same owner/facade and refuses a pending
reply. A client retry uses the same logical identity; after pending effects are
transferred, receipt replay emits no effects. No caller binding is established
by these methods. Lifecycle observations still enter the model through its trusted
driver. Multiple connections, real clocks, stream deadlines, incremental reads,
effect execution and caller rights are not implemented.

Test strict error combinations, malformed/logically invalid input, lifecycle
rejection, reply backpressure, retained effects across disconnect, replay without
duplicate transfer, busy limits, post-dispatch failure and receipt serialization
failure. Add an error-disposition mutation control. Run model/full checks and
retain evidence. Shared pins/native sources/CLI contracts remain unchanged.

Next define a bounded incremental frame reader with logical read/write deadline
inputs and interruption tests before real I/O. Actual authority/revocation and
restart identity remain gates under BG-050/BG-032/BG-033. This result does not
implement B04–B06 or claim crash-safe exactly-once execution.

Result: [retained evidence](../evidence/control-delivery-2026-09-06/README.md)
passes 89 model tests/eight controls, 48 host tests, 37 harness tests and all
offline gates. Error-disposition mutation fails by assertion. Native audit checks
215 historical outcomes; no native code changed or target execution was repeated.
