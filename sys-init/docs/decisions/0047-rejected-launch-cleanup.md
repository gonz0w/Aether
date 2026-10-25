# 0047 — No-target cleanup after confirmed launch rejection

Accepted 2026-09-06, bounded trusted model under BG-058.

The frozen producer reviewed in decision 0042 returns selected launch errors before
slot mutation or endpoint transfer (native_c.zig: launchOperation). The current
native adapter retains both endpoint counts on failure; init.rs's local invalid
slot probe closes writer and reader. That probe does not demonstrate a kernel
rejection path. These sources justify the model below, not fresh native acceptance.

## Contract

RejectedLaunchCleanup represents one attempt with precisely one reader and one
writer, no worker yet, no waits, helpers, devices or other resources. Construct
before applying the launch result from an exact retained ResultApplier launch
call and two distinct positive uint64 endpoint IDs supplied by the trusted driver.
The same call cannot claim two inventories. Claim metadata is pruned against
the applier's at-most-twenty retained bindings on each construction; no unbounded
claim history is retained. Names/IDs are bookkeeping, not native
authority; callers that bypass this trusted API remain outside the experiment.
The driver must register all resources before invoking the launch. This fixed
profile refuses to cover successful launches or any additional resource class.

accept_rejection requires the original owner and most recent successfully applied
result for that exact call/token/target, still retained in journal history, with
outcome rejected-before-effects. Unknown, successful and mismatched results cannot
open cleanup. Preserve the exact errno verdict. Once captured, journal history
retirement does not erase the retained rejection. failure_event returns denied for
EACCES (-13), otherwise launch_failed: denial is permanent, other selected failures
use existing finite retry policy. The driver explicitly submits the event.

close_reply consumes a trusted ABI-6 close result with exact profile, producer,
endpoint identity and syscall 0x24003. Only result 0 clears that endpoint. Selected
negative returns -13/-22 retain ownership and return False; unsupported/malformed
replies reject. Unknown return is never success. Duplicate successful closure and
unregistered endpoints reject. This is result qualification, not native invocation
or authentication. Two booleans and one verdict suffice; no queue or history grows.

The existing reclaim effect names cleanup of a service generation, not necessarily
a native syscall. qualify_reclaim requires both endpoints closed, confirmed launch
rejection, current owned matching generation/epoch with reclaim_sent, and an exact
issued reclaim token for that generation. It returns a local-cleanup-v1 fact for
that occurrence; the driver acknowledges it executed locally. Never bind this
no-target obligation to native 0x20002. cleaned_event requires that exact occurrence
still recorded executed and the model still owns the matching generation. It
returns cleaned for explicit delivery; it does not itself release model ownership.
Backpressure and failure retain inventory/facts. No unknown effect is reconciled.

## Alternatives and review

Native reclaim of a predicted handle was rejected: it can refer to no admitted
instance and cannot close supervisor endpoints. Clearing ownership on rejection
was rejected for the same endpoint leak. Keep legacy launch_failed and journal
schemas unchanged; specialize the driver path rather than changing every failure
policy. This models native ABI-6 only; it introduces no POSIX process assumption,
external dependency or actual cleanup operation. Standard-library Python only.

Foundations O-01/O-04, I-03–06 and E-04–08 apply. Shared releases/pins stay unchanged.
Test retained call ownership, unknown and admitted rejection, both close orders,
partial/failed close, stale tokens/generations, local reclaim acknowledgment before
cleaned, and replacement after cleanup. Add an omitted-endpoint mutation control;
run full checks and retain exact sources/logs. Successful-launch resource inventory,
wait/helper coverage, end-to-end driver composition and fresh native rejection
witnesses remain BG-058; unknown recovery remains BG-033. No native change here.

Reviewed source references: [frozen producer](../evidence/reconciliation-review-2026-09-06/reviewed/Aether/kernel/arch/x86_64/native_c.zig),
[adapter](../../prototypes/native-supervisor/adapter.rs),
[local denial probe](../../prototypes/native-supervisor/init.rs). Exact copies
and source hashes are retained with this decision's validation evidence.

Decision 0047 validation: 206 model tests / 20 distinct mutation controls,
48 host tests, 37 harness tests and all eight offline gates pass. Evidence:
`docs/evidence/rejected-launch-cleanup-2026-09-06/`. No fresh native execution.
