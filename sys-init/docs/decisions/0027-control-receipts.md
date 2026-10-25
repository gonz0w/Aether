# 0027 — Trusted in-process control receipts

Accepted for a bounded BG-050 prototype, 2026-09-06. Implement Control v0 C07–C09
around the existing deterministic model. One facade owns mutation dispatch for
one trusted caller and a captured model epoch/revision. External code may inject
model observations, but must not concurrently dispatch mutations. This is neither
authentication nor a thread-safe/native transport.

Logical payload is an exact dict with version, epoch, revision, sequence, verb,
services and budget. Version is integer 0; sequence is 1..2^64-1; budget is
1..1,000,000 logical ticks; names are a unique list of 1..8 existing model services,
normalized by sorting. Verb is start/stop/shutdown, with shutdown covering all
managed services. Reject extra fields, wrong types, booleans as integers, wrong
identity, unknown names and sequence gaps without dispatch or sequence consumption.

Use a 64-entry insertion-ordered receipt cache plus a nondecreasing high-water
sequence. Reserve storage before dispatch. Identical retained replay returns the
original detached receipt but **no effects**; changed payload rejects. Evicted
identities return retired/unknown, never fresh dispatch. Lifecycle rejection is a
cached rejected receipt and consumes the sequence. Unexpected failure after
dispatch begins poisons the facade: subsequent mutation returns unknown and never
retries, while owned model state remains available for diagnosis.

Submit returns schema sys-init-control-submit-v1, receipt, effects and replayed.
Receipt schema sys-init-control-receipt-v1 contains sequence, disposition, reason
and optional operation snapshot (epoch, ID, kind, shutdown, scope, revision, deadline).
Effects occur only on first dispatch and are separate from replayable receipt.
Admission is accepted, joined or rejected; retired/session-failed returns unknown.
Snapshots never expose mutable model/cache objects.

Observation schema sys-init-control-observation-v1 returns operation identity and
current outcome, or unknown for wrong epoch/retired identity/session failure.
Read active operation independently of bounded completed history. A finite wait
is a nonblocking observation with explicit caller logical now/deadline: pending
before deadline, timeout at/after it, complete for a known terminal outcome, or
unknown. It never advances manager time, cancels work or changes operation budget.
Disconnect has no manager effect. Real blocking I/O and clock integration are open.

Unsigned sequence exhaustion rejects new sequences; retained replay still works.
Conservatively reject new dispatch when model next operation ID exceeds uint64,
including requests that might join, without consuming sequence. This limit is
specific to the facade; the synthetic model's Python counter remains unchanged.

Test replay before/after completion, changed payload, gaps, eviction, bounded
history, immutable snapshots, conflicts, late-launch cleanup, malformed inputs,
epoch/revision changes, identity exhaustion, timeout/disconnect and injected
post-dispatch failure. Run full development checks; no native code changes or
new native witness required. Shared I-01–06/E-05–08 apply; no shared pin changes.

Next: define a bounded external encoding and authority/session contract before
real delivery. Owner review must settle restart epoch identity, caller/session
lifetime, byte/depth bounds and ambiguous effects; no exactly-once or durable
replay guarantee follows from this trusted cache.

Result: [retained evidence](../evidence/control-receipts-2026-09-06/README.md)
passes twelve facade cases (49 combined model tests), three lifecycle controls
and full development checks. Source hashes include the facade. The evidence
remains synthetic model execution; no transport or enforcement claim is added.
