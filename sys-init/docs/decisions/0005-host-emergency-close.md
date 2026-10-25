# 0005: Close host admission before emergency cleanup

Accepted 2026-09-05 for the trusted direct-child experiment, portions of BG-028
and BG-054. This is a local lifetime rule under pinned Foundations O-04, I-04
and E-06; it changes no shared standard, native ABI or operator protocol.

`close()` ends admission permanently before attempting cleanup. Subsequent
`start`, `stop` and `pump` calls reject, without observing or dispatching work.
Construct a new runtime for a new experiment. Calling `close()` again is allowed:
it retries retained cleanup failures and is harmless after successful cleanup.

Only tracked Popen children are killed and waited for. Failure to kill or wait
retains that child and its readiness descriptor for another close attempt; it
must not prevent attempting cleanup of other tracked children. Cleanup errors
raise, rather than reporting success. Successful wait plus descriptor closure
permits removing the child from the host inventory. No global wait or PID scan
is used; an unrelated child remains its caller's responsibility.

On closure, discard queued adapter observations and reject new ones. The model
is a frozen diagnostic snapshot after emergency closure, not evidence of an
orderly stop transaction. Its operation must not be retrospectively marked
successful. The public `closed` flag identifies this terminal adapter state;
remaining `children` identify cleanup still requiring attention. Normal runtime
stop/reclaim semantics and operation history are unchanged.

This chooses explicit lifetime invalidation over synthesizing successful model
stop events during exception handling. Cleanup must work when policy processing
itself has failed or exhausted its event budget. The caller still owns a
`try/finally` that invokes `close()`; Python exceptions do not automatically
invoke it. Destructors and automatic recovery are not introduced.

Validation: caller-exception/finally cleanup, descriptor closure and reaping,
post-close admission rejection, repeated close, injected wait/kill failures with
retained ownership and retry, and an unrelated caller-owned child. Failure
injection tests exercise the adapter's error path with real children; they do
not claim an actual kernel wait failure was observed.

Abrupt supervisor death, SIGKILL, machine failure, escaped helpers and external
reaping are not covered by a finally block. Direct wait ownership must remain
exclusive to this adapter during normal use. BG-028 retains parent-death and
helper-chain experiments, measurements and stronger enforcement choices; BG-033
retains native supervisor recovery. No crash containment is claimed here.

## Recorded result

All six new cleanup tests pass on macOS. The [combined report](../evidence/host-cleanup-2026-09-05/positive/results.json) passes three standards checks, 34 model tests and three mutation controls, 30 host tests and 10 harness tests. Disabling the closed-state guard in an isolated copy causes seven assertion failures, including subtests: [control](../evidence/host-cleanup-2026-09-05/negative.json), [log](../evidence/host-cleanup-2026-09-05/negative.log). Standalone host reports now fingerprint every discovered host test file, including the new cleanup suite.
