# 0004: Synchronize the host clock at request boundaries

Accepted 2026-09-05 for the trusted host experiment, within BG-054. This is a
local adapter ordering rule; it does not define native Aether clocks or the
future control transport. Pinned Foundations I-04/I-05 and E-04/E-06 apply through
[standards adoption](../STANDARDS.md). Shared releases and pins are unchanged.

## Problem and contract

The adapter previously advanced model time only when observations or due timers
required a batch. After an idle interval, start/stop used that stale timestamp
to allocate new operation and service deadlines. The next observation could
immediately expire a newly accepted request.

Before submitting each start or stop, perform one ordinary bounded observation
cut and synchronize its time even when it contains no events or due deadlines.
Continue using the monotonic elapsed-millisecond clock, clamped against backward
movement. Allocate new request budgets from this observation timestamp; command
validation and process launch time count against them. This is not a promise of
exact host scheduling latency or a fresh budget after process creation finishes.

The observation cut precedes request validation. It can record an existing exit,
accept readiness, dispatch an already eligible dependent/retry, or expire an old
timer before the new request is considered. A rejected request has no request
effects, but does not roll back this independent lifecycle progress. This API
does not atomically combine a caller request with every available OS event.
At most four events enter the cut; remaining observations retain existing bounded
queue behavior. Events arriving later cannot undo an earlier dispatch.

Joining an identical pending request keeps its original operation ID and deadline,
and cannot renew a service timeout. Expired work goes through ordinary model
deadline handling before request admission. Rejection within the model still
preserves the state at admission. Callers needing atomic control/event ordering
require the future BG-050 transport contract.

Directly assigning model time would bypass overdue timer handling. Inflating the
requested budget by idle time would mix clock correction with policy limits and
leave per-service deadlines wrong. Reusing the existing observation path avoids
both problems and leaves the deterministic model unchanged.

## Validation and limits

Four host tests control `HostRuntime.now()` while retaining real child creation,
signals, readiness pipes and cleanup. They check fresh startup/stop budgets after
idle time, duplicate start/stop deadline preservation, and overdue startup work
before an invalid request. The duplicate stop fixture signals readiness only after
installing its SIGTERM-ignore handler. No long sleep establishes timing order.

The [combined positive report](../evidence/host-deadlines-2026-09-05/positive/results.json)
passes all standards checks, 34 model cases and three mutation controls, 24 host
cases and 10 harness cases on macOS. Removing the two synchronization calls in a
disposable copy produces four assertion failures: [negative report](../evidence/host-deadlines-2026-09-05/negative.json)
and [log](../evidence/host-deadlines-2026-09-05/negative.log).

This proves the tested adapter/model boundary with controlled time. Existing
wall-clock host tests also pass; no scheduler precision, cross-host conformance,
parent-death containment or native deadline behavior is claimed. BG-054 retains
cross-host coverage; BG-028/BG-040/BG-050 retain broader ownership and transport.
