# 0022 — Cleanup and retry after rejected native readiness

Accepted for a bounded BG-040 experiment, 2026-09-05. Extend decision 0021's
shared polling policy using the unchanged, independently built worker modes.
No kernel, shared interface, dependency, descriptor or production protocol change.

For each of silent deadline expiry and malformed readiness, observe the expected
rejection before any dependent launch. Stop the rejected worker, observe terminal
detail 144, close its reader, reclaim it and require empty adapter accounting.
Only then launch generation two in the same slot. Its worker and reader identities
must differ. Receive its own valid frame and check generation, liveness and deadline
at admission, then launch the dependent. Stop, close and reclaim both remaining
workers. Completion requires the kernel's exact three-reclaim success marker.

Two controls establish enforcement: retaining the failed provider's reader must
reject at 927 after one reclaim; omitting fresh readiness must reject at 929 after
one reclaim and before dependent launch. A generic timeout, unrelated assertion or
boot failure cannot satisfy either oracle. Rejection kind mismatches use 925;
fresh identity mismatch uses 928; final lifecycle/accounting failures use 930.

This selects explicit cleanup before one retry over an unbounded restart loop or
kernel-owned retry policy. All acquired resources have an explicit success-path
disposal; unexpected adapter failures remain fatal fixture assertions, not a
production recovery implementation. There are at most two concurrent workers,
three launches, one retry, a 10-interrupt initial deadline, a 100-interrupt fresh
deadline, and the existing iteration and external watchdog bounds. No allocation,
new unsafe operation or cross-core synchronization is introduced in policy code.

Validation: two positive schedules, two omission controls, all nineteen prior
native cases, retained producer/worker/consumer identity and full offline checks.
The prior worker ELF is reused through its newest bounded-build receipt; old
evidence stays immutable. Source/binary compatibility is measured separately from
semantic regression. No target timing, general retry/backoff, repeated exhaustion,
operator recovery or full BG-040 completion is claimed. Follow-on: specify a finite
retry budget and repeated-failure exhaustion before adding automatic retries.

## Result

[Target evidence](../evidence/native-readiness-retry-2026-09-05/README.md) passes
all 23 cases. Both positive schedules complete with three reclaims; omission
controls reject at 927/929 with one reclaim. All nineteen prior raw supervisors
remain unchanged. Positive clients are 2,272 bytes under the 4 KiB bound; all
178 frozen consumer inputs remain stable. BG-040 stays partial for finite retry
budget/exhaustion, production framing and broader lifecycle policy.
