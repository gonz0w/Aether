# 0030 — Bounded client receipt encoding

Accepted for the local BG-050 model experiment, 2026-09-06. First implement
submission receipts; observation/wait replies remain the next distinct schema
slice. No transport, caller authority or automatic dispatch is added.

The client receipt uses the existing sys-init-control-receipt-v1 fields exactly:
schema, sequence, disposition, reason, operation. `encode_receipt(result['receipt'])`
is the explicit projection from an internal submission. Passing the entire
submission or adding effects/replayed/other fields rejects. Never serialize or
walk the internal effects tuple. Replay encodes the same receipt bytes even when
the internal submission's replayed flag changes.

`encode_receipt` returns four-byte big-endian body length plus ASCII JSON (valid
UTF-8), with sorted keys, compact separators and escaped non-ASCII characters.
Body limit remains 4096 bytes. Validate exact built-in containers and all leaves
before serialization, bounding work independently of the supplied object graph.
`decode_receipt` applies the existing strict frame/JSON rules with depth three
(receipt, operation, scope array), then the same receipt validator. Request depth
remains two. Unknown fields, duplicate keys and invalid combinations reject.

Sequence and operation ID are exact integers 1..2^64-1; deadline is 0..2^64-1.
An operation has exactly epoch, id, kind, scope, revision, deadline, shutdown.
Epoch/revision are 1..64 Unicode scalar characters; scope is 1..8 unique service
names matching the model grammar, normalized by sorting. Encoder accepts exact
list or tuple scope; decoder returns list. Kind is start/stop; shutdown is exact
bool and true requires stop. Reject larger model deadlines explicitly, without
clamping or changing manager state. The logical model's clock is unchanged.

Accepted/joined receipts require an operation and empty reason. Rejected receipts
allow an operation or null and one of the current fixed lifecycle reasons:
shutdown admission closed, operation conflict, unresolved ownership, required
consumer outside stop scope. Unknown requires null operation and receipt-retired
or session-failed. No arbitrary exception text is exposed. A future lifecycle
reason needs an explicit compatibility update. These are receipt dispositions,
not completion claims; operation observations are a separate future reply.

Validation failures raise InvalidFrame('receipt') except the existing fixed
framing/JSON categories during decoding. Encode has no manager access. Failure
does not cancel, poison, retry or undo an admitted operation. The owner retains
receipt/effects and diagnoses output failure; transport-level error delivery and
effect execution independent of the connection are not implemented.

Test real accepted/joined/rejected/retired/failed receipts, byte-identical replay,
strict schemas and semantic combinations, maximum identities/names, large/cyclic
objects rejected before serialization, decoding limits and unchanged ownership
after serialization failure. Add a negative control for receipt field filtering.
Run model and full checks. Shared I-01–06/E-04–06 apply through STANDARDS.md;
existing CLI, pins, native code and internal response schemas remain unchanged.

Result: [retained evidence](../evidence/control-reply-2026-09-06/README.md) passes
69 model tests and six mutation controls, 48 host tests, 37 harness tests and all
offline standards/quality/native-evidence gates. The native audit verifies 215
historical outcomes; this change required no fresh target run. The field-check
mutation is caught by an assertion, not a parser/import error.
