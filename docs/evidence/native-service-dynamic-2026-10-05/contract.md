# Dynamic musl creation and confirmed reuse

Before-code scope,2026-10-05. Extend R1-03's private producer witness with actual
creation calls in progress while detached cleanup owns older records. Keep kernel,
maintained user source, public ABI/SDK, quota, sibling and released pins unchanged.
Production libc/runtime remains userland-owned; accepted VM/musl designs apply.

Use one joinable cleanup worker and one joinable creator within82 service slots,
leaving80 detached peers per round. Four rounds produce322 lifetime admissions;
small companions use primary creation, one cleanup worker and four reused peers.
Only service creation is worker-origin and overlaps older pending cleanup. The
primary must complete a real native join park before cleanup returns. This is
bounded one-CPU concurrency, not parallel multicore execution or engine acceptance.

Each fixture record has an atomic FREE/RESERVED/LIVE/PENDING lifecycle. Clone
reserves only FREE under upstream list-lock ownership, publishes immutable saved
metadata after native admission, and rolls reservation back on failed admission.
A thread-local record pointer avoids racing scans of reusable scalar metadata.
Destructors complete before PENDING release; one cleanup owner alone consumes
pending records. It permits native exit, observes the exact ID stopped, unmaps,
retires and verifies the old ID rejects before publishing FREE. No TCB read after
unmap. Creation cannot recycle a pending record. Atomic admission and occupancy
counts stay bounded; generation uses exact monotonic native IDs, not slot index.

For each service transition, cleanup pauses after its first retirement until the
next actual pthread_create reaches preflight before upstream locks. It then
continues servicing whichever pending peer owns the upstream lock, including while
the creator is blocked. Never wait for a particular pending slot or acquire the
list lock before allowing its owner to exit. New peers await a later round gate.
TSD/TLS/errno, inherited masks, stack patterns, stale-ID rejection, full capacity
output preservation and exact final budget remain required across record reuse.

Untrusted IDs confer no authority. Existing held native thread/memory grants
validate clone/observe/unmap/retire. Running stack/TLS mappings must reject unmap.
Wrong-grant clone must preserve caller output, admission and budget, then report
exact360. Premature unmap reports352, missing overlap proof365 and omitted primary
native join park356. Failure drains published peers through confirmed cleanup and
retains the original error; no rejection is converted into success. Whole-domain
stop/replacement remains a separate positive. Cancellation/detach/orphan recovery,
production resource sizing and unbounded schedules remain unsupported.

Tests: historical origin source rebuilt as a fresh regression; four-round dynamic
creation/reuse; live stop/replacement; four exact controls. Fixed180-second builds,
30-second guests/3-second teardown; retain every attempt with source/SDK/tools,
recipes, artifacts and logs. Full host/pin/workflow/format/simplicity/link checks,
then archive every member and verify before removing only owned duplicates.
Document the reference, workflow, STATE and roadmap. No companion SESSION claim.

Simplicity: repeating fully settled batches cannot test this lifetime requirement.
Keep upstream locking and existing native authority primitives; add only a local
atomic record lifecycle and direct TLS association needed to make reuse race-free.
No kernel RPC, public registry or generic reaper service is introduced. None of the
immutable old witnesses is removed; this replaces their phase assumption only in
this experiment. Production integration must account for the helper cost and
avoid accumulating test-only paths into an SDK implementation.

Before attempt2: attempt1 reaches all three expected historical-origin worker
terminals but times out before supervisor completion; no dynamic case ran. Retain
raw logs/source and classify it as incomplete final supervision, not a pass or an
explained infrastructure fault. Review also removes creator_done from the final
peer join barrier: last retirement must wait for primary join entry even if the
creator has not yet published completion. Same build/guest deadlines remain.

Before attempt3: attempt2 completes the fresh historical regression, then the
new probe compilation fails because this intentionally restricted SDK has no
stdatomic.h. Use pinned Clang's C11 atomic builtins directly, preserving sequential
consistency and avoiding a new header/dependency. Also keep the final join-entry
barrier as ordinary child yielding: the primary's musl wait must park on its real
join word, not wake a second test word before that park. Retain both attempts;
no dynamic behavior has yet qualified and no runtime/SDK bytes change.

Before attempt4: attempt3 passes the rebuilt origin regression and small dynamic
peer, but the service does not terminate within30 seconds. This is unqualified
progress, with cause unresolved. The dynamic lifetime witness now checks4 KiB of
real per-thread stack pattern; requested256/128 KiB stacks, guards and eager mapping
cost are unchanged. Deep240 KiB touches remain in the fresh origin regression.
This separates repeated lifetime coverage from old deep-stack stress, without
relaxing native allocation, authority, join or reuse checks or any deadline. No
latency/high-water claim is made; a further timeout will need progress diagnosis.

Before diagnostic attempt5: attempt4 still times out in the service after small
peer completion. The deep stack loop was not the cause established by this run.
Add an explicitly diagnostic-only producer trace and supervisor reader in the
private packet. Numeric phase progress uses existing bounded stdout; the separate
recipe records diagnostics, never semantic acceptance. It retains30-second guest
budget and frozen sources. Final qualification omits the trace cfg entirely.

Diagnostic attempt5 itself times out before its100000 polling iterations finish;
retain it as failed diagnosis, not workload acceptance. Diagnostic attempt6 caps
its own reader at5000 iterations under the unchanged guest deadline. Production
and normal qualification code paths are unaffected by this diagnostic cfg.

Before attempt7: diagnostic6 ends deliberately with725, showing the creator
published the first thread of round3. This establishes progress beyond round2,
not completed four-round cleanup or a root cause for the deadline overrun. Final
bounded requirement is two full rounds:162 service/three peer lifetime admissions,
80/one reused records and one overlapping transition per service generation.
Four-round stress remains failed/unqualified; it is not silently accepted under
a larger deadline or represented as281-lifetime engine coverage. The final run
still requires82/two live capacity, all-record reuse, exact authority/mask/TSD/TLS/
stack and final budget, primary park and stopped service replacement. Also release
phase/preflight/reaped/arrival barriers when the first error is recorded, so a
creator rejection cannot strand cleanup waiting for a future preflight. Production
sizing and measured latency/engine lifetime still need separate acceptance.

Attempt7 still times out before the first service terminal despite completing the
small companion; two rounds are not accepted yet. Diagnostic8 adds helper/join
completion and the first error to the same bounded trace, to distinguish a final
settlement fault from incomplete creation. No deadline or kernel change.

Before attempt9: diagnostic8 reports724: first second-round retirement, with no
recorded error. Replace pending detached busy-yield polling with actual native
compare-and-park on that immutable record's allow_exit word; the sole cleanup
owner stores permission and counted-wakes it before confirming native exit. This
removes polling while musl's list lock is held without permitting any other code
to acquire that lock before exit. Record and wait-word mappings remain pinned
until terminal observation. No kernel/ABI or deadline changes; final trace cfg
still absent. Two full rounds and all exact controls rerun.

Before attempt10: parked exit allows the first full162-admission service to
terminate successfully in attempt9, but repeating that service in the same30-second
guest times out. No full attempt passes yet. Separate the schedules: the ordinary
case executes one two-round service plus a small peer and its replacement; the
stop case executes one-round full82-live stop and one-round full replacement.
The fresh origin regression retains its old full-service generation replacement.
This preserves each named invariant under its stated workload without counting
repeated two-round/four-round service stress as qualified. Dynamic reuse after a
full-service stop,281 engine lifetime and latency remain missing. No workload is
accepted by timeout and the original budget is unchanged.

Before attempt11: attempt10's ordinary dynamic guest completes all terminals and
exact supervisor100/reclaimed3, but the recipe's old hard-coded replacement-slot
assertion still expects service0 instead of the scoped peer1 replacement. Retain
as a failed receipt check, not final coverage. Correct only the per-case assertion
and rerun every planned native case. Runtime/source behavior stays unchanged.
