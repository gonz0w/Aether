# Control boundary v0

Local BG-050 proposal, 2026-09-06. Builds on [Control v0](CONTROL-V0.md), the
[operator research](../research/OPERATOR-INTERFACE.md), and pinned Foundations
[O-01–05](../vendor/aether-foundations/v0.1.0/OWNERSHIP.md) and
[I-01–06](../vendor/aether-foundations/v0.1.0/INTERFACES.md).
The lifetime guard in [decision 0028](../decisions/0028-control-session-ownership.md)
and pure request decoder in [decision 0029](../decisions/0029-control-request-decoding.md)
are implemented for the model, together with receipt encoding under
[decision 0030](../decisions/0030-control-receipt-encoding.md). Authenticated
sessions and transport do not exist.
These are proposed local experiment bounds, not measured production budgets.

## B-01 — Request framing and parsing proposal

The pure request decoder accepts one complete frame: four unsigned big-endian
length bytes followed by exactly that many UTF-8 JSON bytes. Body length is
1..4096 bytes; total frame length is at most 4100. Reject short headers, zero or
excess length, truncated bodies, trailing bytes and multiple frames. No BOM,
compression, shell interpretation, byte-order negotiation or format guessing.
This length envelope permits testing without selecting a socket or native IPC.

Reject invalid UTF-8, duplicate object keys (including equivalent escaped keys),
unpaired Unicode surrogates, non-finite numbers and non-integer number syntax.
Use JSON decimal integer syntax only; no fractions or exponents. Bound integer
tokens to 20 decimal digits excluding an optional minus sign before converting;
logical validation subsequently rejects negative values and values above their
field maximum. Root must be an object; maximum nesting is two containers counting
the root and its services array. Check depth without treating brackets inside
quoted strings as structure, before handing input to a recursive parser.

Decoder output is a syntax-checked candidate dict. Pass it to `Control.submit`
for logical validation; decoding alone is not admission. Validated fields are
exactly the existing Control payload: version, epoch, revision,
sequence, verb, services, budget. Existing logical types, bounds and names remain
authoritative; reject unknown fields and unsupported versions. JSON whitespace,
key order, valid string escapes and service selection order do not change request
identity. Normalize using the facade's logical payload, not raw frame hashes.
No normalization of identity string contents or case is implied.

All framing, decoding and logical validation failures occur before dispatch and
consume no request sequence. The codec returns a value or a bounded fixed error
category, never echoes the offending payload into diagnostics. It performs no
I/O, model mutation or authority decisions. A later encoder must enforce the same
bounds and must not pass unlimited Python objects to an unbounded serializer.

For a later stream adapter, header validation precedes body allocation; hold at
most one frame and one pending response, stop reading under backpressure, and set
finite read/write deadlines before enabling delivery. Bad framing closes the
connection without attempting resynchronization. A complete-buffer codec alone
cannot demonstrate those stream allocation, timeout or queue guarantees.

## B-02 — Caller authority and session ownership proposal

The transport producer must supply an authenticated caller binding from its
enforcing boundary. Sys-init consumes that binding and owns lifecycle policy.
Caller names, UID-like numbers, paths, hashes, request sequences and operation IDs
in data confer no authority. No caller field or bearer token is added to the
payload. A transport with no accepted identity/authority mechanism is unsupported.
Neither a POSIX socket credential facility nor an Aether grant ABI is selected.

The first transport experiment should support one explicitly provisioned caller
and one manager-owned session, with serialized dispatch. Reconnecting the same
authorized binding attaches to its existing receipt cache/high-water mark; it
must not construct another facade. A different or unprovable binding is denied.
Loss of session state cannot authorize re-creation against the existing manager.
The in-process facade permanently claims its Model even after disconnect or
failure. This trusted-code guard is not a protection boundary or a concurrency
primitive; callers with model access can bypass it.

Before effects or cached results are exposed, the future adapter must verify
current authority for the requested verb and effective scope. Start requires
permission for its complete dependency closure, stop for every affected service,
and shutdown for the entire manager scope. Reject insufficient authority without
partial effects. Operation observation also requires authority for its scope;
knowledge of an operation ID is insufficient. Recheck on replay and observation,
including after revocation. Authorization denial must not reveal another caller's
receipt or consume the mutation sequence. Revocation prevents new requests and
observations; it does not silently cancel already-owned lifecycle work.

Epoch and configuration revision checks remain distinct from authentication.
An actual restart requires a producer-defined non-reused manager identity and a
recovery contract; the model's default boot-1 string provides neither. Copying a
Model or editing its private marker is not supported recovery. Additional callers,
delegation, policy updates and session replacement require separately bounded
contracts and tests before widening this one-caller experiment.

## B-03 — Ambiguous delivery and response boundary proposal

Before dispatch, an invalid frame or denied authority has no lifecycle effects.
After dispatch, response timeout or disconnect leaves the manager's operation and
receipt intact. Reattach only to the same authorized session and replay the same
logical sequence/payload. Return its retained receipt without effects; an evicted
receipt remains unknown/retired. Never automatically change the sequence to retry
an uncertain mutation. Unexpected dispatch failure leaves the session failed;
reconnection cannot clear it. State loss or unprovable identity yields unknown,
not a fresh execution. These rules provide no durable exactly-once guarantee.

The facade's effects tuple is internal manager-driver work, not client response
data. Receipt encoding now exists as a pure model helper (B07 below). Before real
delivery, extend the in-memory experiment with stream deadlines/backpressure
and execution of
first-dispatch effects independently of client connection lifetime. A serializer
must not accidentally make replay execute those effects again.

## Acceptance and remaining work

| Case | Required witness | Current status |
| --- | --- | --- |
| B01 | Exact byte/depth edges; malformed UTF-8/JSON; duplicate/escaped keys; integer limits; trailing/partial data; no sequence consumption | Implemented: CodecTests framing/parsing and facade rejection cases |
| B02 | Equivalent encodings preserve logical replay identity | Implemented: CodecTests equivalent-encoding replay |
| B03 | Reconstruct after completed work, eviction/disconnect or ambiguous failure cannot reset history | Three model regressions in decision 0028 |
| B04 | Wrong caller, insufficient closure rights, revoked rights and unauthorized replay/observation deny before effects or disclosure | No enforcing adapter; unimplemented |
| B05 | Interrupted response, reconnect, slow reader and partial request preserve bounded state and operation ownership | Real transport unimplemented |
| B06 | Restart identity cannot alias earlier requests; recovery retains or reports unknown ownership | Producer/recovery contract unimplemented |
| B07 | Strict bounded receipts omit internal effects; replay has identical bytes; output failure preserves ownership | Implemented: ReplyTests and receipt-fields mutation |
| B08 | Observation identity and wait/outcome consistency; bounded encoding without cancellation | Implemented: ObservationReplyTests and identity mutation |
| B09 | Error disposition, reply/effect backpressure, disconnect and uncertain output preserve work | Implemented: DeliveryTests, trusted complete-frame model only |
| B10 | Bounded incremental input/output, deadline edges and reply-loss replay | Implemented: StreamTests and deadline mutation; injected logical clock |

BG-050 retains all unimplemented rows, response schema and public CLI grammar;
BG-032 is the route for demonstrated native mechanism gaps, BG-033 for recovery,
and BG-045 for status scope. A matching producer/consumer authority contract and
fresh target witness are required before claiming native delivery. No shared
standard version, release bytes or numeric native rights are changed here.

## Receipt wire reference

[Decision 0030](../decisions/0030-control-receipt-encoding.md) defines the exact
bounded receipt fields, allowed reason/disposition combinations and limits.
`encode_receipt(submission['receipt'])` projects the existing logical receipt;
`decode_receipt(frame)` returns its normalized detached dict. The full internal
submission is rejected. Framing is the same four-byte length and 4096-byte body
cap as requests, with depth three for receipt/operation/scope. Encoder output is
compact sorted-key ASCII JSON; request decoding still permits only depth two.
Validation is complete before serialization. No client-visible effects or
replayed flag are encoded, so original and replay receipts have identical bytes.
No operation completion, response delivery or caller authority follows from
successful receipt encoding. Observation/wait encoding is now implemented below;
transport error encoding is now implemented below.

## Observation and wait wire reference

[Decision 0031](../decisions/0031-control-observation-encoding.md) defines exact
fields and combinations. `encode_observation`/`decode_observation` use depth three;
`encode_wait`/`decode_wait` use depth four. Both retain the 4096-byte body cap,
canonical encoder and strict decoder rules. Observation ID/epoch must equal its
operation snapshot; unknown requires null operation. Wait pending/timeout requires
pending outcome, unknown requires unknown, and complete requires a terminal outcome
(success, failed, cancelled or incomplete). These replies do not prove clock
expiry, authentication or delivery. Unknown epoch strings outside the external
1..64-scalar bound reject without changing the broader in-process facade API.
Transport error encoding and bounded in-memory delivery are now implemented
below; real stream delivery and authority remain unimplemented.

## Error and in-memory delivery reference

[Decision 0032](../decisions/0032-control-memory-delivery.md) defines exact error
fields/codes and the Delivery API. `encode_error`/`decode_error` use depth one.
Invalid-frame, invalid-request and busy mean not-dispatched; internal-error means
unknown. No unvalidated request identity, exception text or payload is echoed.

Delivery retains one Control facade, one reply and one effect batch. Pending reply
blocks admission locally; pending effects return busy. `take_effects` transfers
the batch once to a trusted driver without proving execution. Disconnect discards
only reply bytes; reconnect retains manager state and request history. Malformed
frames close input; serialization failure cannot erase captured effects. This
experiment accepts complete frames only and has no real I/O/deadlines. Decision 0033 now adds
bounded incremental framing and logical deadline/interruption tests. Authority,
revocation and driver crash recovery remain gates before real service exposure.

## Incremental stream reference

[Decision 0033](../decisions/0033-control-incremental-stream.md) defines Stream's
reading/writing/closed phases, exact API bounds and logical deadline rules.
feed validates the four-byte header before copying body data, rejects trailing
bytes/pipelining and dispatches only complete input. read returns bounded response
prefixes; input is blocked until drain. Neither partial read nor partial write
extends the phase deadline. At or beyond deadline, close before progress.
Disconnect clears only connection buffers; reconnect reuses the manager and its
receipt history. No autonomous timer exists; the trusted driver supplies tick.

Next review actual producer caller binding and scope/revocation requirements,
plus driver effect execution acknowledgment/recovery, before real I/O. The logical
stream model does not satisfy real-time, caller-authentication or native delivery
witnesses in B04–B06. No real endpoint is exposed.

## Authority handoff

[Decision 0034](../decisions/0034-control-authority-review.md) reviews existing
producer mechanisms and routes local scope/disclosure/revocation to
[Control authority v0](CONTROL-AUTHORITY-V0.md). A01–A03 trusted policy tests are
next; native binding and effect acknowledgment require separate witnesses. No
new rights arise from endpoint/operation numbers or a successful codec.

## Trusted authority model

[Decision 0035](../decisions/0035-control-authority-model.md) implements the local
A01–A03 scope/disclosure/revocation fixture. It wraps stream admission/output,
closes on denied scope and preserves cached sequences/owned effects after output
denial. Opaque binding identity is test input, not real caller authentication.
C10/B04 remain open for native producer enforcement and consuming witnesses.
