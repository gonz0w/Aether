# 0043 — Pure qualification of confirmed ABI-6 returns

Accepted for BG-058 on 2026-09-06 after decision 0042's frozen producer review.
Implement a pure trusted evidence qualifier before applying results to the
journal or producing lifecycle observations. No native call, recovery transition,
shared ABI or production authority boundary is introduced.

A BoundCall retains the exact issued event token, journal, opaque original-owner
binding, producer SHA-256, ABI-6 profile, syscall and expected native target.
Targets are the selected profile's generation-encoded handles: two slots, three
native generations. Native generation is independent of model generation. For
launch this target is an expected slot/generation supplied by trusted adapter
bookkeeping, not a handle discovered by guessing. Its actual native reservation
and identity binding still require a consuming witness.

Only launch/0x23001, stop/0x20007 and reclaim/0x20002 are supported. force explicitly
rejects; it has no selected native mapping. Both bind and qualify require the
journal open and the exact token still issued. Reserved, terminal, unknown,
evicted, stale or altered tokens cannot qualify. The owner identity is supplied
out of band and compared by object identity. A hash/profile/name is not authority.

Reply is an exact built-in dict containing schema=abi6-return-v1, profile,
producer, token, syscall, target and result. All fields must match the bound call;
result is an exact signed 64-bit integer. Success is the expected target for
launch and zero for stop/reclaim. Known pre-effect errors are launch EACCES,
EINVAL, EBUSY, ENOSPC, EFAULT; stop EACCES/EBADF; reclaim EACCES/EBADF/EBUSY.
Preserve the exact negative return and operation. Other values reject without
changing journal/lifecycle state. A received EBADF on the original still-issued
call can classify that call's rejection; EBADF obtained later for an already
unknown call cannot reconcile it.

Return a detached immutable tuple: confirmed-result-v1, outcome, syscall, result,
target, postcondition. Outcome is executed or rejected-before-effects. Positive
postconditions are instance-admitted, target-terminal and target-reclaimed;
negative returns have none. These describe the reviewed local handler guarantees,
not ready service state, occurrence-caused termination, full-domain cleanup or
cross-core/device quiescence. No terminal kind is inferred from numeric detail.
No Model.batch or journal.acknowledge occurs here. Repeated qualification while
still issued is a pure repeated calculation; once externally acknowledged it
rejects. There is no receipt cache, replay protocol or exactly-once claim.

Input sizes are fixed: ten-field token, seven-field reply, 64-character producer
hash, fixed profile, bounded target/result scalars and one owner reference per
context. No internal queue or growing history. Callers retain context objects;
no global resource budget or crash-atomic application is claimed. The later driver
must serialize/revalidate qualification and acknowledgment and fail closed on an
ambiguous apply. BG-058 remains active for that application contract, explicit
terminal/cleanup observations and fresh native adapter acceptance. BG-033 retains
actual unknown reconciliation; it remains unsupported by this experiment.

Test all three positive results and allowed errors, wrong owner/profile/producer/
target/syscall/token, non-issued and unknown state, force, malformed fields/types,
unsupported results, repeated pure qualification and unchanged ownership. Add an
issued-state omission control. Run model/full checks; retain exact source/logs.
Standard-library Python only; existing journal/token/wire/native contracts and
shared pins remain unchanged. Foundations O-01/04, I-03–06 and E-04–08 apply.

Validation: 173 model tests, sixteen distinct mutation controls, 48 host tests,
37 harness tests and all offline adoption/quality/evidence gates pass.
[Retained evidence](../evidence/confirmed-result-2026-09-06/README.md) binds the
qualifier, tests and runner. Native execution was not rerun; no native source or
existing journal/lifecycle implementation changed.
