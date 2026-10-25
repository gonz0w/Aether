# 0049 — Retained launch and cleanup driver composition

Accepted 2026-09-06 for BG-058's trusted Python model.

## Contract and scope

Compose decisions 0044–0048 in LifecycleDriver. It creates the sole ResultApplier
and TargetRegistry for an exact JournalRuntime with at most two configured services
(reject larger graphs before claiming the runtime; not QueuedRuntime, whose batch
means enqueue). Supporting larger graphs needs admission/backpressure work before
producing launch obligations beyond native capacity. Up to two attempts retain their service token, predicted native
slot, reader/writer IDs, call context, cleanup inventory and one pending event.
No real channel acquisition or native invocation is implemented: prepare accepts
a pair already acquired by the trusted caller. Rejected validation leaves that
pair caller-owned; after insertion the driver retains it even if binding fails.
Complete pre-acquisition reservation and channel creation failures remain BG-058.

prepare validates issued launch identity, two distinct positive uint64 endpoints,
no endpoint overlap with retained attempts, duplicate service and two-attempt
capacity. Then retain before registry reservation/binding/cleanup construction;
any subsequent exception closes the owner and keeps the attempt. There is no
implicit cleanup or silent loss on partial preparation.

launch_reply applies the retained call, immediately adopts its confirmed result,
and stores one lifecycle event. Success binds AdmittedResources to the retained
reader and records launched; the writer transferred to the target. Rejection uses
RejectedLaunchCleanup, releases only the native reservation and records the
qualified failure event. Retain original rejection inventory diagnostically on
success; only the selected admitted inventory governs subsequent operations.
Malformed/ambiguous launch replies or failed post-application routing close the
owner; journal issued effects become unknown, recorded outcomes remain retained.

terminal_reply projects through TargetRegistry. Running produces no event. A
terminal event supersedes a pending launched event; equal repeats are harmless,
conflicting pending terminal facts reject without discarding the first. This does
not implement a general observation inbox or multi-cut temporal ordering.

reclaim routes only an exact issued matching-generation reclaim obligation. For
rejected launch, both endpoint closes qualify local reclaim and the driver records
its executed acknowledgment without native invocation. For admitted launch, apply
the supplied confirmed native reclaim result; only success calls accept_reclaim.
Negative native reclaim leaves cleanup incomplete; retry policy for it is open.
Malformed/ambiguous native reclaim or application failure closes the owner. Missing
reply or invalid routing arguments reject before application. Stops/force, worker
readiness and arbitrary effects remain outside this coordinator's automatic path.

queue_cleanup obtains the selected inventory's qualified cleaned event, retaining
it for delivery. deliver submits all pending events as one bounded cut (at most
two). Journal backpressure leaves events intact. On successful cleanup delivery,
retire native bookkeeping if admitted and remove the attempt. Positive model retry
delay ensures replacement is not launched during the cleanup cut. A failed runtime
capture retains attempts/events; it does not falsely report delivery. A failure
in retirement after successful delivery closes the owner and retains diagnostics.

## Review and validation

No new dependency, native ABI, shared rule or POSIX process assumption. Existing
model/resource/journal contracts remain authoritative. The coordinator and raw
resource replies are trusted fixtures; public/private bypass and thread safety
are excluded. Two attempts and two event slots bound retained live state; callers
can retain old references but they cannot release replacement generations.

Apply Foundations O-01/O-04, I-03–06 and E-04–08. Test successful and rejected launch
through actual composed cleanup, terminal-before-launched, two-attempt backpressure,
unknown/malformed results, endpoint overlap and partial preparation/capture failure.
Add an event-retention omission control. Run full checks and retain source/log
hashes. BG-058 next covers pre-acquisition capacity and channel-create failures,
then native driver witnesses; BG-033 retains recovery. No native execution claim.

Decision 0049 validation: 221 model tests / 22 distinct mutation controls,
48 host tests, 37 harness tests and all eight offline gates pass. Evidence:
`docs/evidence/driver-composition-2026-09-06/`. No fresh native execution.
