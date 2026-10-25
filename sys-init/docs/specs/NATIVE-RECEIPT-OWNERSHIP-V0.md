# Native invocation and receipt ownership v0

Accepted local experimental design, 2026-09-06; decision 0071, BG-058/BG-057 NB-09.
This refines [Native driver binding v0](NATIVE-DRIVER-BINDING-V0.md). The phases
and tests below are specified, not implemented. No kernel reply transport,
persistent receipt format or replacement-owner recovery is introduced.

## Source findings

The current [binding driver](../../prototypes/native-supervisor/binding.rs) calls
[Adapter](../../prototypes/native-supervisor/adapter.rs) synchronously and retains
a successful channel pair before its injected completion check. Its `pending`
index records a reservation; it does not independently distinguish an invocation
that has started from one that may still start. Sequential, nonreentrant execution
currently supplies that separation. Splitting invocation and application must add
an explicit phase guard before exposing either operation; merely keeping `pending`
would allow a second call at the same reserved index.

The [model driver](../../prototypes/runtime_model/lifecycle_driver.py) reserves
before a caller supplies a synthetic reply. [BoundCall](../../prototypes/runtime_model/confirmed_result.py)
qualifies the original occurrence, and [ResultApplier](../../prototypes/runtime_model/result_applier.py)
separately acknowledges the journal. None executes the native invocation.
[EventJournal.driver_lost](../../prototypes/runtime_model/event_journal.py) retains
issued effects as unknown. Those model rules motivate the boundary but do not
prove native receipt retention. The [reconciliation review](../research/UNKNOWN-EFFECT-RECONCILIATION.md)
explains why observation or a stale-handle error cannot discharge an unknown effect.
The [review snapshot](../evidence/native-receipt-contract-2026-09-06/reviewed-files.json)
retains these exact sources.

## Bounds and ownership

Keep one trusted live context, the existing two attempt records and immutable
synthetic issuance table. Add at most one outstanding call/receipt position across
this initial creation/launch slice. Reserve that position before invocation and
retain it until local application succeeds or the owner remains closed. No queue,
heap allocation, concurrent callbacks, owner replacement or capacity replenishment
is admitted. A stalled receipt applies explicit admission backpressure; it never
waits on an optional diagnostic sink.

The position binds the live owner reference, fixed producer/profile, original full
ten-field token, attempt index, operation (creation 0x24000 or launch 0x23001),
selected slot and reserved expected target. Creation is a substep of the original
launch occurrence, not a newly minted journal operation. Launch additionally binds
the actual retained writer. Numeric identities remain metadata, not authority.

The driver owns the position and its retained resources throughout. It is not a
caller-owned return object that can be dropped after a successful effect. Typed
wrappers are Copy today, so logical exclusive use must be enforced by phase and
access paths; Rust's type system alone does not prove this ownership invariant.
Resource wrappers may reside in the receipt or the attempt, provided exactly one
location is designated usable and transfer cannot fail after clearing the source.
Retain the original result/error and binding even after resource transfer. For
this slice, a decoded Adapter result is the receipt; it is not a transcript of all
trap registers or a claim to qualify arbitrary malformed kernel returns.

## State transitions

| Phase | Required state and permitted transition |
| --- | --- |
| Reserved | Issuance already consumed by reservation; no call yet. Attempt and receipt capacity fixed. Only this phase can start this operation. |
| Started | Mark before entering Adapter and increment the invocation counter once. Invocation is permanently non-repeatable. An absent return leaves effects unknown. |
| Returned | Capture the actual result and any resources in the preallocated owner position immediately, before fallible matching or a test pause. No second invocation or launch from this receipt is permitted. |
| Applied | Qualify the retained binding, apply its recorded outcome once, and retain the per-operation completed phase in the attempt. Only then release the shared receipt position. This is local application, not journal acknowledgment. |
| Closed | An unresolved or invalid post-start transition permanently closes admission. Preserve previous phase, original binding, any received result/resources and failure cause. Do not reset consumption or infer cleanup. |

Closure is a separate owner state, not an overwrite of the phase/evidence. Denied
preflight calls leave the position and all counters unchanged. A mismatched local
application request (wrong context/index/token/operation/target) denies without
taking or replacing the existing receipt. A genuine retained-result mismatch or
unsupported post-call outcome closes the owner with its receipt intact. After
closure, ordinary application cannot reopen admission; any later available result
is diagnostic retained evidence only and needs a separately specified recovery
path before use.

A controlled pause after Returned may resume matching local application while the
owner remains open. The receipt position blocks other invocation during the pause.
Repeated application after Applied denies without repeating effects or advancing
generations. Closure/cancellation while paused preserves the receipt; cancellation
cannot undo a received success. There is no timer or automatic expiry in this slice.

## Operation-specific effects

For channel success, retain both actual endpoints before any pause or matching.
Neither endpoint is available for launch until application qualifies. For the
already qualified creation busy error (0x24000/16), retain the exact error and empty
inventory; release the provisional slot and creation position only on application.
Keep issuance consumed. Unknown absence is never translated to busy or rejection.

For launch, retain the reader throughout and mark writer use in-flight before the
call. Before a real return the writer is unavailable for reuse or closure: transfer
may have occurred. A successful return must retain the actual worker and mark the
writer transferred before any pause or expected-target comparison. Only matching
application advances the admitted native generation, once. Actual-worker retention
on mismatch remains decision 0069's rule. A received qualified busy rejection keeps
both endpoints; only its application releases the provisional slot. Other results
retain their origin and remain subject to ND-04; no new errno classification is
accepted here. A local Adapter guard failure is not evidence of a kernel call.

Do not acknowledge the journal, emit a lifecycle event, infer terminal state or
emit Cleaned from receipt capture/application. ND-02 owns terminal qualification;
ND-03 owns event/cut acceptance and retirement. Stop/reclaim receipt semantics,
owner death and truly absent kernel return reconciliation remain ND-04/BG-033.

## Acceptance plan and implementation order

All cases below are future work. First implement IR-01–04 for actual channel
returns with phase/retention controls; record exact assertion markers before the
native run. Then implement IR-05–06 with launch transfer rules. IR-07 requires a
separate synthetic schedule; do not label it native lost-reply execution.

| ID | Required oracle and evidence layer |
| --- | --- |
| IR-01 | Native channel call returns into the retained position; hold application, attempt repeated start and another reservation. Exactly one factory call, same token/pair, no worker and unchanged native generations. Resume matching application once; duplicate application leaves state unchanged. |
| IR-02 | During the held receipt, wrong owner/token/index/operation/target application cannot remove or overwrite it. The correct application still succeeds. Typed private context checks are not transport authentication tests. |
| IR-03 | Close admission while holding a real channel receipt. Both endpoints, original result, phase and consumed token remain retained; further invoke/apply/reserve deny. Explicit fixture disposal uses retained handles without resetting history or claiming Cleaned. |
| IR-04 | Two independent native controls: omit the started/returned invocation guard and detect erroneous acceptance or changed call count before any repeated syscall; omit endpoint retention and detect the missing owner record. Neither generic timeout nor leaked-resource inference alone is an accepted oracle. |
| IR-05 | Native launch succeeds, then application is withheld: reader and actual worker retained, writer marked transferred, generation unchanged until qualified application. Duplicates cannot invoke launch again; matched application advances generation once. |
| IR-06 | Close while holding successful launch receipt; retain actual worker/reader and transferred-writer state. A semantic control that keeps writer reusable must fail the ownership oracle. Fixture teardown acts only on positively retained resources. |
| IR-07 | Synthetic Started-with-no-return schedule closes with unresolved operation and reservation; no retry, invented error/result or acknowledgment. Label the missing return injected and do not claim a real call was lost. |

For IR-04, separate start authorization from execution so the omission control
can observe forbidden authorization before performing a second effect. It must
exercise the same guard as the real invocation path. An added test-only predicate
that bypasses that path would not qualify. Resource-loss controls may terminate at
their designated assertion; retain their expected failure, not a passing cleanup
claim. Ordinary success/closure probes must account for actual retained resources
through explicit fixture teardown under the existing bounded target profile.

A truly lost syscall return cannot be produced by discarding returned wrappers.
If the syscall never returns, this single synchronous owner has no code execution
with which to record closure; an external watchdog is an incomplete execution,
not an NB-09 pass. The native probes prove local receipt retention/backpressure;
full missing-reply recovery remains open. No new kernel mechanism is required for
the first slice. If a fixture exceeds 4 KiB, split independent probes and preserve
each failure without weakening the ownership oracle.

## Review and standards scope

The alternatives were immediate application only (current behavior, no observable
held receipt), caller-owned replies (permits lost ownership), and a durable shared
receipt service (needs recovery/interface research). A bounded driver-owned
position makes the local ownership boundary inspectable without selecting a
production transport, language or POSIX/BSD/illumos/Linux process mapping.

Foundations O-01/O-03/O-04, I-01/I-03–06 and E-01–08 apply through
[STANDARDS](../STANDARDS.md). Distribution ID-02/04 does not authorize a recovery
owner; no session or authentication behavior is added. Existing pins, unsafe trap,
output markers, error contracts and experiment bounds remain unchanged. No new
dependency or exception. Documentation impact is this contract, its decision,
current work order and the open native-driver quality gap. Full development checks
validate the documentation adoption; fresh pinned target execution is mandatory
for subsequent implementation. No independent reviewer sign-off is claimed.

## Channel implementation — decision 0072

[Decision 0072](../decisions/0072-native-channel-receipt.md) implements IR-01–04
for channel creation: explicit phases, retained native pair/error and shared
start/launch guards. Local delivery checks the original owner/token/operation/target.
Three positive and two semantic omission probes pass in a fresh 80-case witness.
The pause is local after a real return; closure is injected in trusted fixture
state. No missing kernel reply, public cancellation or full NB-09 is demonstrated.
Earlier future-work wording describes the design checkpoint. IR-05–06 launch
receipt transfer is next, followed by IR-07 synthetic absence; other NB/ND and
BG-033 recovery remain open. See the decision for exact tests and size limits.

## Launch receipt implementation — decision 0073

[Decision 0073](../decisions/0073-native-launch-receipt.md) implements IR-05–06:
launch success retains actual worker/reader and records writer transfer before
application; generation and launched-event qualification wait for matching
application. Closure keeps the pending receipt. Two positive and two semantic
omission probes pass in a fresh 84-case witness. This is local retention after a
real synchronous return, not a lost kernel reply, public cancel API or recovery.
IR-07 synthetic absence is next; remaining NB/ND and BG-033 work stays open.
Earlier future-work statements describe their own checkpoints.

## Synthetic absence — decision 0074

[Decision 0074](../decisions/0074-native-synthetic-missing-return.md) executes IR-07
as a synthetic schedule in the native fixture: real start guard, omitted syscall,
retained Started/pending state and closed admission without invented result/error.
Two positives and three controls pass within a fresh 89-case witness. This does
not lose an actual kernel reply or authorize unknown-transfer cleanup.
The [binding acceptance review](../research/NATIVE-BINDING-ACCEPTANCE-REVIEW.md)
keeps remaining NB gaps explicit. Next is ND-02 terminal-kind contract work;
ND-03–05 and BG-033 remain open. Earlier next-work wording is historical.
