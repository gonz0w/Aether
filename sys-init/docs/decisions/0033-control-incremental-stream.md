# 0033 — Incremental framing and logical deadlines

Accepted for the trusted BG-050 model, 2026-09-06. Wrap decision 0032's Delivery
with a sequential Stream(Model, now, read_budget, write_budget). This is an
in-memory byte-stream simulation, not a socket, authenticated endpoint or timer.
Shared I-01–06/E-04–06 apply through STANDARDS.md; native sources/pins stay unchanged.

Maintain reading, writing or closed phase. Reading stores at most one frame
(four-byte header plus 1..4096-byte body). feed accepts exact bytes of at most
4100 bytes, fills/validates the header before copying body bytes, and rejects
overflow/trailing data before dispatch. It accepts one frame only; pipelining is
unsupported and rejected, never silently truncated or queued. An empty chunk is
no progress, not EOF; disconnect is explicit. On complete input, clear the read
buffer and submit once through the retained Delivery owner.

Writing retains only Delivery's one response plus an integer offset. read accepts
a 1..4100-byte maximum and returns that prefix of remaining response; no receive
is allowed while writing. Successful drain starts the next read deadline. If
Delivery closed input on malformed JSON, draining its error closes the stream.
Invalid header/chunk framing closes without a reply. Unexpected dispatch/output
exceptions also close and propagate, preserving the Delivery's manager/effects.

Time is exact integer 0..2^64-1, nondecreasing across all calls and reconnects.
Budgets are 1..1,000,000 logical ticks; initial/reconnect time must be below MAX.
Each phase deadline is min(MAX, entry time + budget), never extended by partial
read/write progress. At now >= deadline, close before accepting bytes or emitting
output. Saturation shortens the available budget at clock exhaustion; it never
wraps. Invalid clock/count arguments reject before mutation. tick must be called
by the trusted driver: no autonomous timeout or real elapsed-time guarantee exists.

disconnect discards buffered input and pending output, not manager work or effects.
reconnect is allowed only when closed and reuses the same Delivery/Control; it
cannot reset an active phase's deadline. take_effects remains the trusted ownership
transfer. Timeout after admission, including after partial output, is uncertain
to the client; retry the same logical identity after pending effects transfer.
Before a complete frame is dispatched, read timeout has no lifecycle effects.

Validate partitioned headers/bodies, all split positions, exact maximum input,
oversized/trailing frames, reply backpressure and small output chunks, deadline
edges/no extension, monotonic clock/exhaustion, reconnect replay and exceptional
encoding cleanup. Add an exact-deadline mutation witness. Preserve receipt/error
bytes and all earlier model cases; run full development checks and retain evidence.

Next review and specify a producer/consumer caller-binding and scope/revocation
contract before real I/O. Also define effect execution acknowledgment/recovery:
transfer alone is not execution. BG-050/BG-032/BG-033 retain these gates. No native
grant numbers, UID authority, public CLI or production exactly-once claim is added.

Result: [retained evidence](../evidence/control-stream-2026-09-06/README.md) passes
99 model tests/nine controls, 48 host tests, 37 harness tests and all offline
gates. The off-by-one deadline mutation fails by assertion. Native evidence audit
checks 215 historical outcomes; no new native execution was needed or performed.
