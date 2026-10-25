# 0031 — Bounded observation and wait replies

Accepted for the local BG-050 model experiment, 2026-09-06. Extend decision 0030's
pure reply codec without changing its receipt bytes or internal facade schemas.
Shared I-01–06/E-04–06 apply through STANDARDS.md. No authority or transport is added.

Observation fields are exactly schema=sys-init-control-observation-v1, epoch, id,
outcome, operation. Outcomes are pending, success, failed, cancelled, incomplete
and unknown. Unknown requires null operation; every other outcome requires a
bounded operation snapshot whose epoch and ID match the observation. Epoch is
1..64 Unicode scalar characters and ID is integer 1..2^64-1. Existing operation
limits apply. The facade can represent other unknown epoch strings in-process;
the external codec rejects values outside its bounds without changing that API.

Wait fields are exactly schema=sys-init-control-wait-v1, state, observation.
State pending or timeout requires pending observation; complete requires success,
failed, cancelled or incomplete; unknown requires unknown. Complete describes a
terminal operation outcome, not successful service activation. A timeout does not
cancel the operation. No timestamp is encoded, so the decoder validates state
consistency, not whether a remote clock actually reached a deadline.

encode_observation/decode_observation and encode_wait/decode_wait use four-byte
length-prefixed JSON with 4096-byte bodies. Observation depth is three and wait
depth four; request/receipt depth stays two/three. Exact fields and bounded leaf
validation precede serialization. Canonical encoder rules remain sorted keys,
compact ASCII JSON and normalized scope. No effects, free-form diagnostics or
caller data can appear as additional fields. Validation errors have fixed local
categories observation or wait; framing/JSON errors retain the decoder categories.
Unexpected host errors propagate. Encoders have no manager access and no effects.

Test actual pending/timeout/completed/unknown model snapshots, all outcome/state
combinations, mismatch of nested identity, unexpected fields, limits, deep/cyclic
objects, failed encoding without cancellation, strict decode and unchanged receipt
golden bytes. Add an identity-mismatch mutation control. These are host-codec and
model observations, not authority, clock or delivery witnesses. Run full checks.

Next specify bounded transport error replies and an in-memory delivery experiment
with explicit ownership/backpressure/interruption bounds before any socket. Real
caller binding, scope/revocation and restart recovery remain BG-050 gates; current
pure codecs do not authorize an external service. No new dependency or native code.

Result: [retained evidence](../evidence/control-observation-2026-09-06/README.md)
passes 77 model tests/seven controls, 48 host tests, 37 harness tests and all
offline gates. The identity mutation causes an assertion failure without errors.
Native evidence audit checks 215 historical outcomes; no new target run occurred.
