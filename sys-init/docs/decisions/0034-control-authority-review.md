# 0034 — Existing caller binding, explicit service policy

Accepted as a research handoff, 2026-09-06. The [source review](../research/CONTROL-AUTHORITY-HANDOFF.md)
finds existing native owner-bound channels/private broker connections relevant to
a single-client service-control experiment. It does not find an accepted sys-init
reconnect/revocation/effect-acknowledgment composition in those reviewed contracts.
This is a bounded review conclusion, not a claim that no mechanism exists anywhere.

Proceed with [local authority requirements](../specs/CONTROL-AUTHORITY-V0.md) and
a trusted single-binding policy model before selecting a native profile. Avoid a
new kernel API request until the consumer proves a concrete missing facility.
Do not import command-broker EOF teardown into service lifecycle policy or mix
ABI-9 channel capacity with ABI-6 timers and supervisor-failure semantics.

BG-050 retains model authority/revocation tests; BG-032 retains producer selection,
native binding and consuming evidence; BG-033 retains effect execution acknowledgment
and recovery. OQ-021/022 preserve uncertainty. No runtime code, standards pin,
companion file or historical evidence changed. Validate references, snapshot
identity and full offline checks; no new model or native coverage is claimed.

Result: [retained review and validation](../evidence/control-authority-review-2026-09-06/README.md)
passes full offline checks: 99 model tests/nine controls, 48 host, 37 harness and
all standards/quality/native-evidence gates. Selected producer bytes were rechecked
after capture; new review links resolve. No new behavioral/native coverage is added.
