# 0025 — Dependency loss preserves an admitted consumer

Accepted for bounded BG-040/BG-042 work, 2026-09-06. Follow
[runtime R-07](../specs/RUNTIME-V0.md) and the
[native/model review](../NATIVE-POLICY-REVIEW.md). Earlier decisions 0019/0020
remain valid stop-on-loss fixtures, not the initial model's dependency policy.

A ready provider authorizes one actual dependent launch. Cause provider terminal
state through explicit native stop or decision 0020's reader-close/normal-return
stimulus. Record dependency loss against that exact provider identity and reject
new admission. The already admitted dependent remains owned and running; do not
stop or restart it as a side effect of provider loss. Observe its live state both
after loss and after provider reclamation/replacement.

Reclaim the old provider, start generation two in its slot, receive fresh evidence
and accept the new binding. The old binding stays lost and cannot authorize new
work, including after its handle is reclaimed. Finally issue an explicit stop to
the original dependent, observe terminal status, close/reclaim it, then stop and
reclaim the replacement. Exactly three reclaims complete the fixture.

Controls: automatic dependent stop on loss must reject at 940 with zero reclaims;
bypassing the new-admission gate must reject at 941 with zero reclaims. The latter
rejects before an unintended third launch. Terminal/reclaim/setup errors use 942;
fresh binding or stale revival errors use 943; explicit shutdown uses 944. Exact
semantic contexts are required; boot failure or watchdog timeout cannot pass.

Loss is a manager-owned in-memory record, not a diagnostic string, RPC or provider
capability. No operator status API or persistent event stream is claimed. Recovery
creates a new provider binding explicitly; automatic rebinding/queued consumers
are separate work. The dependent calls no provider API in this fixture.

Limits: two concurrent workers, three total launches, 100-delivered-interrupt
readiness/wait bounds and existing polling/QEMU watchdogs. Reuse the unchanged
worker/producer and adapter; add no unsafe code, allocation, shared rule, ABI or
dependency. Full checks and four new target cases plus all thirty-one earlier
cases are required. Record raw-byte compatibility separately from outcomes.

Next BG-040/BG-050 work: specify operation identity and explicit desired state,
request joins, cancellation cuts and ownership of late launch completion before
implementing real control delivery. Use the existing R-11–R-16 model; identify
mechanism gaps through consuming evidence rather than guessing kernel support.

## Result

[Target evidence](../evidence/native-dependency-loss-2026-09-06/README.md) passes
all 35 cases. Automatic stop and bypassed admission reject at 940/941 with zero
reclaims. The two positive clients are 2,416/2,528 bytes, all thirty-one earlier
raw supervisors remain unchanged, and 178 frozen inputs stay stable. The
dependent remains live across loss, reclamation and replacement until explicitly
stopped. This is the bounded R-07 policy witness, not a complete native model port.
