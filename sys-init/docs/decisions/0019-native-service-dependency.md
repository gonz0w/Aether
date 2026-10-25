# 0019 — One native provider/dependent lifecycle

Accepted 2026-09-05 for a bounded experiment under BG-032/BG-040. Follows
[decision 0018](0018-native-adapter-boundary.md) and the corrected
[SI-04 consuming pin](../evidence/native-slot-reuse-consumer-2026-09-05/README.md).
Aether owns enforcement; sys-init owns admission and dependency invalidation.

Use unchanged ABI-6 workers and adapter. One provider and one dependent each get
a fresh channel and an independently owned worker handle. The existing worker
writes exactly byte 42 then stays live. This byte is the entire fixture readiness
frame, not a production framing decision or the host `READY\n` protocol. No new
shared standard, loader operation, POSIX facility or implementation language is
selected. Foundations O-01–05, I-01/03–06 and E-01–08 continue to apply.

A local service record binds a worker, reader and generation (1 then 2). Captured
readiness binds the same identities to the received byte; no payload can choose
its generation or confer authority. Admission requires matching identities, byte
42, current provider liveness and a final clock observation strictly before the
absolute deadline. A deadline at/before now rejects even buffered valid evidence.
Use checked interrupt-tick addition; reads poll/yield with both a 100-tick deadline
and the existing bounded iteration/QEMU watchdog. Watchdog expiry is failure.
Lifecycle waits do not wake on bytes. Observation cuts are not atomic admission
or a promise that a worker remains alive after the observation.

Positive workload:

1. Launch provider generation 1, receive readiness, verify expired-deadline
   admission rejects, then admit and actually launch the dependent before the
   original readiness deadline. Failure to admit cannot silently skip this launch.
2. Register a wait on the provider revision; explicitly stop the provider as a
   controlled failure injection. Observe changed completion and terminal detail
   144, release the wait, and reject its retained readiness as current evidence.
3. Invalidate the dependency by stopping the still-owned dependent. Require its
   observed terminal detail 144; close both readers, reclaim both workers and
   require empty adapter accounting. Stop is native forced termination, not a
   graceful signal or spontaneous process fault.
4. Launch a fresh provider generation 2. Reject generation-1 evidence against this
   instance, accept its own new frame, then stop/close/reclaim it. No second
   dependent is launched: this profile completes after three worker reclaims.

Designated policy mutations bypass deadline rejection (901), terminal rejection
(902), dependent stop (903), or old-generation/instance/channel binding (904).
Each must fail at its exact assertion with its known reclaim count, never pass on
a timeout or unrelated panic. The guard controls exercise the same admission
function used to authorize the real dependent launch. Existing nine adapter cases
retain their prior semantic outcomes and raw binary identities; their deadline
and zeroing kernel mutations remain part of acceptance.

This selects one hard dependency, one readiness frame and one bounded restart.
A configurable graph, retries/backoff, arbitrary inherited helpers, spontaneous
provider fault schedules, scalable event waits, elapsed-time deadlines, supervisor
recovery and POSIX portability remain follow-ons under existing BG-032/BG-040 and
decision 0018. No story is closed by this workload.

## Implementation witness

[Native service checkpoint](../NATIVE-SERVICE.md) passes the positive lifecycle,
four designated policy mutations and all nine unchanged adapter cases. The
2,960-byte client fits the original bound. Broader failure schedules remain open;
this witness uses controlled stop and does not implement a service descriptor.
