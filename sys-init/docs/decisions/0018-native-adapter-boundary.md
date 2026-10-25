# 0018 — Bounded ABI-6 adapter boundary

Accepted for the experiment, 2026-09-05. Extraction is now implemented within
[the recorded adapter scope](../NATIVE-ADAPTER.md); the first bounded service/dependent workload now has
[decision 0019 and a target witness](../NATIVE-SERVICE.md); the sequential cross-slot reuse gate is now resolved by the
[independent consuming refresh](../evidence/native-slot-reuse-consumer-2026-09-05/README.md).
Owners: sys-init lifecycle policy; Aether native operations. Related work:
BG-032/BG-040 (active), BG-033 (partial/captured).

## Evidence and choice

[Decision 0017](0017-native-init-consumer.md) and the
[frozen producer contract](../evidence/native-init-consumer-2026-09-05/producer/NATIVE-INIT.md)
provide a consuming witness for AENIN001/ABI 6. The extended
[offline audit](../NATIVE-COVERAGE.md) checks all seven outcomes without executing
retained code. These are sufficient inputs for extracting a small experimental
adapter, not selecting a production implementation language or POSIX API.

Keep raw traps, grant validation and operation decoding behind a local boundary;
keep service generation, readiness admission and retry policy outside it. Reject
a direct port of the host millisecond model: the accepted clock counts delivered
interrupts. Reject a generic backend framework until a second real consumer needs
one. Rust may continue as the existing native fixture language without becoming
the distribution's implementation decision.

## Required local contract

| Operation | Required authority, state and result |
| --- | --- |
| Initialize | Validate ABI 6 and entry grants before effects; unsupported profile fails explicitly. One supervisor owns all adapter resources. |
| Launch | Use supplied factory/image authority and an available one-of-two slot. Transfer one fresh channel writer to the launched instance. Return an opaque worker identity only on success. Track partially allocated channels on failure. |
| Observe | Use observation authority and the exact worker identity; return revision, terminal detail and historical readiness separately. A ready bit alone never admits a dependent. |
| Clock/deadline | Represent `InterruptTick` and checked tick addition explicitly, with no implicit milliseconds conversion. Overflow is failure. Absolute deadline at/before now wins over a revision change. |
| Register/status | One outstanding registered lifecycle wait in the whole adapter, including retained completion. Pair token with target identity and observed revision. Status is pending, changed, timeout, cancelled or target-reclaimed; retain completion until release. |
| Cancel/release | Cancellation refreshes first and may preserve an already completed result. Release consumes the token; stale tokens fail. Track the producer's 64-token lifetime limit; exhaustion is explicit, never a retry loop or token wrap. |
| Read readiness | Poll the owned reader in the producer's bounded chunks (at most 16 bytes). Distinguish pending, EOF, bytes and error. Lifecycle waits do not wake on channel bytes. |
| Stop | Request explicit native stop for an owned live worker; observe terminal completion before claiming it. This is not graceful POSIX signal handling. |
| Close/reclaim | Close owned endpoints separately from worker reclaim. Preserve terminal evidence until policy consumes it; account for retained waits and release them. Reclaim success alone does not mean every adapter resource is released. |

Translate negative native results into explicit failure outcomes; preserve the
operation and failure class in trusted internal results. Never turn denied,
stale, busy or exhausted into successful no-ops. Do not retry a failed launch or
reclaim automatically. Ambiguous/unobserved ownership halts admission and ends
the experiment unsuccessfully; the profile's verified whole-domain shutdown is
available on supervisor death, not recovery or an ownership inventory API.

The single-threaded experiment owns at most two workers, two channels and one
registered wait. Use bounded polling/yield with an independent harness watchdog;
watchdog expiry is failure, never a service timeout or cleanup success. Helper
ownership remains explicit. A service generation is local policy identity and
does not itself confer authority or replace the kernel's opaque worker handle.

## Next consuming workload and acceptance

First extract the boundary while preserving the seven existing semantic outcomes
and rejection assertions; retain new build/source evidence and compare results,
not necessarily binary identity. Then add one bounded service/dependent workload:
launch a provider, receive its generation-bound readiness before a tick deadline,
re-observe liveness before dependent admission, observe provider failure, stop and
reclaim the owned dependent, clean up channels/waits, and launch a fresh provider.
Two slots suffice if replacement follows dependent cleanup.

A liveness observation is a cut, not atomic read-plus-admission and not a promise
that the provider cannot die immediately afterward. Subsequent observed failure
invalidates admission. Delayed evidence from an old generation cannot admit its
replacement. Define the workload's exact readiness bytes and failure schedules
before implementing it; the existing producer helper's byte 42 does not select
production framing or the host's `READY\\n` protocol.

Required controls: at/after-deadline readiness cannot admit; terminal-owner queued
readiness cannot admit; old generation evidence cannot admit replacement; busy
wait and exhausted tokens fail explicitly; cleanup cannot pass with an owned live
worker, endpoint or retained token. Keep producer-skip-deadline and cleanup-zeroing
controls. Exact assertions must distinguish these failures from build/boot errors
and watchdogs. Existing seven-case receipts remain historical and immutable.

## Standards and remaining gates

Apply offline Foundations [O-01–05](../vendor/aether-foundations/v0.1.0/OWNERSHIP.md),
[I-01,03–06](../vendor/aether-foundations/v0.1.0/INTERFACES.md), and
[E-01–08](../vendor/aether-foundations/v0.1.0/EVIDENCE.md). No shared rule, ABI,
release pin or machine marker changes. Exact adapter behavior belongs here;
future shared requirements belong in Aether-standards. No new exception.

Production elapsed clocks, scalable/blocking waits, general delegation, graceful
signals, supervisor recovery, SMP and POSIX portability remain outside this
experiment under BG-032/BG-033/BG-040. BSD/illumos host execution remains a
separate BG-054 gap. This decision does not close those stories.

## Extraction implementation note

The initial array ledger exceeded the unchanged 4 KiB native bound. The accepted
adapter uses worker/endpoint counters and a retained wait identity pair, while the
kernel enforces per-handle authority/capacity. This preserves one-owner accounting
without duplicating the kernel registry. Native denial probes remain separate from
ordinary adapter calls. Nine target outcomes pass; the separately retained
sequential-reuse failure gates broader ordering claims. See the checkpoint above.

## SI-04 consuming refresh

The corrected producer summary `3a399587b34010302d25838d9f8e1cc73e2b93bec1ac673321326494bde1f155`
passes the unchanged forward probe, a reverse-order copy and all nine adapter
cases in sys-init's own runs. The earlier failure remains historical evidence.
Resume the next workload specification; this refresh adds no policy implementation
or new shared interface and does not close the broader stories.
