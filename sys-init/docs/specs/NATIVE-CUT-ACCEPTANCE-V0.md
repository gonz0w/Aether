# Native cut acceptance v0

Local experimental contract, decision 0156, BG-057 PH-07. Specified requirements,
not an implemented coordinator, kernel ABI or shared wire format. Extends
[pending history](NATIVE-PENDING-HISTORY-V0.md); [source findings](../research/NATIVE-CUT-ACCEPTANCE-REVIEW.md)
explain why existing route delivery cannot substitute for these requirements.

## NC-01 — Owner and provenance

Name the trusted serialized owner CutCoordinator. It exclusively coordinates the
original History, lifecycle application adapter and effect journal. It cannot
accept a caller-created Fact, claimed cleanup boolean or supplied owner identifier
as provenance. Bind each observation to the same live owner, fixed profile and
producer, immutable epoch/revision, full ten-field launch token, attempt index,
actual worker/full native generation and retained source record. No owner restart,
reentry, concurrent mutation or imported nonempty inventory is supported.

The existing native fixture uses a retained ABI-6 logical context label even under
the independently pinned ABI-15 image profile. Integration must explicitly bind
both the actual consumed envelope/producer and the logical contract context; do
not treat the fixture label as discovery of the running kernel ABI or silently
rewrite old evidence. New profile adoption requires its own pinned witness.

Terminal membership references the sealed original Sample and matching fact.
Launched requires the qualified applied launch return and ownership transfer;
Cleaned requires confirmed resource inventory and the separately issued/applied
reclaim obligation for the same attempt. Neither sample numbers nor launch token
confer stop/reclaim authority. Closed/conflicted/failed history cannot enter a new
cut; diagnostic inspection continues without application or retirement.

## NC-02 — Cut identity and bounded storage

A cut has one coordinator-issued serial, exact observation count, canonical order
by immutable attempt index, and complete ordered member identities/content. It
references retained source records without overwriting them. A receipt identifies
the live coordinator, that serial, the whole membership and lifecycle application
result. Raw samples remain in History; no digest substitutes for full equality.
Effect-journal cut serial and observation-cut serial are distinct and explicitly
associated when application creates effect obligations.

| Resource | Initial logical bound |
| --- | --- |
| Owner/attempts | One live owner, two lifetime attempt slots; no slot reuse |
| In-flight observation cut | One, containing one or two members, at most one per attempt |
| Per-attempt phases | Launched, Terminal, Cleaned; at most one applied occurrence of each |
| Retained coordinator records | Six fixed cut records, each at most two member references plus phase/result metadata |
| Existing raw history | Two primary samples plus one diagnostic, nine triple slots; never replenished here |
| Effect reservation | Preserve the model's separately justified twenty-credit whole-cut bound; no new native twenty-effect implementation claim |

Six records cover the worst case of six separately applied phase observations.
Cancelled/unknown reservations also retain a record and can exhaust this budget.
Check free record and journal capacity before application; no eviction or allocation
on exhaustion. Zero-member/time-only cuts and rejected-launch paths are outside this
first profile, not silently accepted. Serials start at one, are bounded by u64,
never wrap and are never reused once reserved. Exact duplicate requests consume
neither a record nor serial. Target byte layout and strict image fit require later
measurement; these logical bounds are not a stack/performance claim.

## NC-03 — Ordering and preflight

Validate every member and its expected before/after lifecycle state before any
model mutation. Launched must be applied in an earlier cut before Terminal for
that attempt; Terminal must be applied in an earlier cut before Cleaned. Reject
a mixed-phase duplicate for the same attempt before sorting or application. A
terminal sample may be retained while Launched waits; never replace the launch
notification or reread the worker to retry delivery.

Two services may advance in one cut only when both independently satisfy their
preconditions. Wrong owner, source/token field, worker, phase, generation, member
count or altered membership denies the entire cut with sources, lifecycle state,
clock, pending position, resources and counters unchanged. A stale event skipped
by Model.batch is not successful application. The adapter must check exact expected
transitions and capture every resulting effect obligation for this cut.

## NC-04 — Reservation and application

Reserve the coordinator record and all required journal capacity as one serialized
pre-application step. If capacity is unavailable, return Busy/Full without modifying
source ownership or the model. A partial internal reservation must unwind before
returning ordinary denial, or close and retain its exact uncertainty. Validate the
same inputs again before calling the lifecycle adapter.

Record Reserved then Applying before model mutation. Commit Applied only after the
entire cut's lifecycle transitions and generated effects have been captured and
associated with the same cut. In this trusted single-owner experiment, publishing
that record is the logical commit point. Queue insertion, callback invocation,
returned effect tokens and an empty inbox do not individually establish it.
No disk durability, crash-atomic publication or power-loss recovery is claimed.

Before Applying, explicit cancellation may mark the record Cancelled while leaving
source and model unchanged; the record/serial stay consumed. After Applying begins,
any exception, incomplete capture or uncertain return closes the coordinator and
retains Applying/Unknown plus all source and journal evidence. Do not roll back by
assumption, rerun the cut or mark it Applied to regain capacity. If publication of
Applied succeeded but delivery of its receipt is lost, an exact query may return
that retained receipt; it never invokes application again. An inability to prove
publication remains Unknown and follows BG-033.

## NC-05 — Replay and disposition

| Request/state | Required outcome |
| --- | --- |
| Exact retained Applied cut queried again | AlreadyApplied with the same receipt; no application, read, effect or capacity change |
| Same serial with changed membership/content/context | Denied; original record unchanged |
| Exact Reserved cut | Pending; no duplicate application |
| Cancelled cut | Cancelled; no resurrection or serial reuse |
| Applying/Unknown or closed owner | Closed/Unknown; inspect retained state only, no new mutation |
| Unretained, future or foreign serial | Denied; never inferred successful from a numeric range |

AlreadyApplied is a local observation-application result, distinct from
pending_history::Replay::Duplicate and EventJournal effect acknowledgment.
A closed owner may expose an immutable historical Applied receipt for diagnostics;
it does not reopen admission or permit a new retirement action.

## NC-06 — Pending and resources

Applied Launched marks only launch observation delivery. Applied Terminal may
release the single sampling/effect reservation for the matching pending attempt
so separately issued cleanup obligations can proceed. Perform that transition
under the coordinator's retained Applied record; if post-commit bookkeeping fails,
close and keep the receipt and remaining reservation, without applying again.
Keep the terminal sample, token, worker/reader ownership and consumed issuance.
This is a proposed integration rule; current History has no such method.

Stop/reclaim and endpoint/wait cleanup still need their own bound obligations and
positively known outcomes. Record each applied resource disposition; partial
cleanup preserves remaining ownership and any uncertainty. Reclaim execution
alone does not prove all endpoints/waits released, and neither it nor an empty
inventory proves lifecycle Cleaned has been applied.

## NC-07 — Retirement without recycling

Permit the private retirement transition only for an open coordinator with a
matching retained Applied Cleaned cut, earlier Applied Launched/Terminal for that
attempt, positively empty resource inventory, and no unresolved call, event or
effect obligation for it. Retire all eligible members named by the accepted cut
under the same serialized owner. If bookkeeping is only partly completed, close
and retain each exact disposition; do not claim atomic rollback or retry.

Mark a retained attempt tombstone and revoke its eligibility for further sampling,
effects and new observation membership. Keep full binding, raw samples, consumed
issuance, native generation and receipt records; an exact inspection/replay remains
historical only. Do not clear used, reset Sample, recycle an index, reopen a closed
owner or authorize replacement. Matching repeated retirement of an already retired
member is a no-op only while its exact retained receipt remains provable. Other
requests deny. BG-060 must define retention/reuse before sustained restarts.

## NC-08 — Qualification sequence

BG-059 first tests the pure coordinator with explicitly synthetic trusted sources
and a counted deterministic application fixture. It does not mutate native History
or claim real journal/native origin. Require:

- Ordered Launched/Terminal/Cleaned and a two-service whole cut with exact receipts.
- Terminal-before-Launched, same-attempt mixed phases, wrong identity/member and
  skipped lifecycle transition denial before application or accepted publication.
- Busy journal, exhausted six-record storage and exhausted serial with unchanged
  sources/model; exact replay does not consume capacity or call the fixture.
- Revalidation failure between reserve/apply; cancellation retains its consumed
  identity; pre-commit and post-commit failure keep their different known states.
- Uncertain application closes without rerun; exact Applied receipt remains
  inspectable after lost delivery. No stale/foreign receipt retires an attempt.
- Cleaned application without confirmed empty inventory cannot retire; partial
  cleanup/post-commit bookkeeping failure retains resources/history and closes.
- Controls skipping identity, accepting intake as application, allowing reordered
  phases, reapplying duplicates, retiring before Cleaned and resetting history
  must fail distinct named assertions, not compile/timeout/tool failures.

Then BG-057 integrates the real lifecycle/journal adapter with matched positive
postconditions, followed by fresh consuming native witnesses. Preserve all 185
current native oracles, existing ABI bounds and pins; keep catalog acceptance
separate from the known producer source-closure limitation. Source-defined strict
oracles, target size review and full local checks precede implementation acceptance.
No production language, POSIX adapter, durability or general recovery is selected.

## Pure core checkpoint — decision 0157

The Python cut_coordinator model implements exact retained synthetic source/cut
identity, one active reservation, six retained records, ordered phases and
cut-bound application receipts. Adapter preconditions and returned/observed phase
states are rechecked; uncaptured application closes with Unknown and retains the
returned diagnostic result. Exact receipt replay invokes no application. Cancelled
records remain consumed; a new reservation for the same still-eligible observation
may use a new serial/record, never resurrecting the cancelled cut.

The source registry contains at most six immutable, explicitly synthetic records.
Ten-field tokens use fixture scalars rather than parsing the published token schema;
identity relies on the exact retained object and immutable content, not constructor
privacy against hostile Python. Adapter reserve has a declared no-effects-on-error
contract. Actual journal reservation, source authority and enforcement remain
unqualified. Python allocation is not a native fixed-memory guarantee.

NC-06 native pending/resource disposition, NC-07 retirement, post-commit bookkeeping
failure, resource-bound cleanup and associated retirement/reset omission controls
remain BG-059/BG-057 work. No native function or public acknowledgment/reset API
is added. See decision 0157 and its retained model evidence for validation scope.

## Synthetic retirement checkpoint — decision 0158

A separate single Retirement owner now consumes exact retained Applied receipts
for cuts containing only Cleaned members. Earlier Launched/Terminal applications
must remain recorded. A declared read-only synthetic adapter supplies immutable
source-bound inventory: reader/writer/worker/wait ownership, applied reclaim and
unresolved obligation. Every member must pass before either is marked. This does
not qualify actual issued cleanup effects, native resource disposal or journal
obligations; those claims still need real adapters and consuming witnesses.

Per-attempt observed inventory, started/retired disposition, exact receipt and
returned result remain retained. A returned None is distinct from an exception
without a return. Any failure after marking starts closes the core; neither
rollback nor repeated marking is attempted. Exact repeated retirement is a no-op
while open and provable; closed owners retain inspectable application records.
Source/history, consumed serials and cut records are never reset. Callback reentry
and attachment of a second Retirement owner are denied.

NC-06 terminal-application pending release and actual cleanup-obligation accounting
remain open. Mixed-phase cuts still require selective retirement semantics and
tests: this first entry denies them, preserving history. BG-059 remains active for
those cases; BG-057 owns real lifecycle/journal/native integration, BG-060 sustained
reuse and BG-033 recovery. Logical bounds add two disposition/observation/returned
slots; Python allocation is not a native layout or performance witness.

## Pending and mixed-cut checkpoint — decision 0159

The same single Retirement owner now releases one exact Terminal member's pending
position under its retained Applied cut receipt. The synthetic adapter exposes
pending_source() as a read-only inspection and release(source, receipt) as its
logical bookkeeping operation. Actual native effects remain outside this adapter.
Require exact pending/source identity before starting, exact returned receipt and
an empty position afterward. Retain started/confirmed status, original source and
any returned result. Failure closes without replay; a previous exact confirmed
release does not touch a later member's pending position.

Selective retirement now uses only Cleaned members of an exact Applied mixed cut,
retaining the entire original receipt. Each selected member additionally requires
confirmed release under its earlier exact Applied Terminal receipt. Other members,
including their pending position, remain untouched. All selected members still
pass resource preflight before marking. The earlier all-Cleaned-only limit is
superseded for this pure model, without changing historical evidence.

Pure tests use trusted synthetic source registration, application, reservation and
resource disposition. Those fixtures do not certify actual journal effect capture,
phase admission, applied reclaim, native raw receipt provenance or cleanup. In
particular, the core model can be given Cleaned before resource disposal; retirement
denies missing release/resources, but the real lifecycle adapter must also gate
acceptance of Cleaned itself. BG-057/BG-058 own that integration before native
acceptance. BG-060 retains sustained reuse and BG-033 unknown recovery.

## Launched journal integration — decision 0160

JournalRuntime now exposes reserve_batch, cancel_batch and batch_reserved with
its actual EventJournal ticket. A prepared ticket blocks other runtime commands;
normal unprepared behavior is unchanged. Applying consumes that reservation through
the existing Model.batch admission hook and actual effect capture. Cancellation
consumes its journal serial; failure closes the runtime without retrying the cut.
Prepared identity remains diagnostic when application fails.

LaunchedAdapter binds up to two retained fixture Source objects to actual executed
launch-effect tokens through an explicit per-position injective symbol encoding.
It rechecks full launch token/context, starting/owned/pending state and generation,
then verifies started transition and complete real journal obligation capture.
Receipts carry the actual journal serial, distinct from coordinator cut identity.
Prepared capacity is exercised on both a dependency-generating and empty-effect
cut. All this runs the real policy model and journal, not the earlier counted
application fixture; source/worker origin and executed launch outcome are still
injected model facts. No native execution or cryptographic provenance follows.

This adapter only supports Launched at unchanged model time. The earlier pure
Terminal/Cleaned/resource tests are not automatically integrated: their exact
mapping, cleanup-before-Cleaned admission, failure behavior and real ownership
must be wired and witnessed under BG-057/BG-058. No automatic event replacement,
source reset or production-language decision is introduced.

The reserved-batch API is restricted to the direct JournalRuntime profile.
QueuedRuntime and other derived runtimes deny before reservation: their batch
method may only enqueue, which is not application. Decision 0160 tests that denial
with unchanged model, journal and inbox state.

## Terminal model/journal integration — decision 0161

TerminalAdapter extends the Launched event/verification hooks while preserving
its earlier profile and tests. It registers up to two Launched and two Terminal
sources under matching owner, actual model launch token and opaque fixture worker.
Terminal content is (revision, result, kind, historical_ready), strictly typed and
bounded; accepted pairs follow the existing native-terminal contract. This is a
synthetic qualified-fact representation, not an O1/S/O2 provenance constructor.

After an earlier applied Launched cut, revalidate running/owned state, generation,
context and the retained executed launch token. Map normal results to exit detail
result-1, and fault/stop to their distinct kinds. Actual model postconditions include
Terminal, cleanup pending, ownership retained, exact terminal kind/detail and one
real reserved reclaim obligation for each member. Verify complete journal capture
through the existing adapter before publishing the receipt. Historical readiness
never invents a Ready observation. A missing or wrong transition/capture closes
without retry or resource release; exact replay changes neither model nor journal.

Only fixed-time running-to-terminal transitions are integrated here. Other phase
families, real native origin and confirmed resource disposal are not inferred.
BG-057 next gates Cleaned admission on actual issued/applied reclaim and verified
remaining resources, followed by fresh native integration with BG-058.

## Cleaned model/journal integration — decision 0162

CleanedAdapter adds up to two exact Cleaned bindings, with (0,) fixture content,
to the matching Launched/Terminal bindings. It retains each Terminal transition's
actual reclaim token before the reserved-batch capture verification completes.
That token must subsequently have an executed journal disposition. A fresh trusted
read-only inspection returns Resources bound to the exact Cleaned source: all four
reader/writer/worker/wait ownership flags false, reclaim_applied true, unresolved
false. This synthetic inspection is not a native ownership inventory or authority.

The whole cut is inspected before any model event; observed values remain retained
on denial. Context, terminal ownership, generation and cleanup-pending state are
revalidated after inspection. Applying the actual cleaned event must leave the
same generation unowned, cleanup complete and no outstanding deadline or launch.
The existing full-capture verification precedes receipt publication. Fixed model
time permits a future retry to be scheduled, but does not admit replacement/reuse.
Receipt replay neither inspects nor mutates. Failed callbacks, reentry or postchecks
close the owners and retain available evidence; nothing performs cleanup for them.

This completes the three phase mappings in the bounded actual model/journal path.
BG-057 next combines this path with pending release and retirement; BG-058 retains
native observation/resource provenance. BG-060 governs eventual history reuse.

## Actual journal/retirement composition — decision 0163

The existing Retirement now has integration witnesses with CleanedAdapter and the
actual JournalRuntime. The fixture supplies one synthetic pending position and
two tombstones; it shares resource inspection with cleanup admission. No native
pending view or resource operation is substituted by this test. Mixed cuts apply
through the actual reserved batch and retain all generated journal obligations.
Only Cleaned members retire. A later member's pending position, reserved reclaim
and lifecycle state survive another member's retirement and replay unchanged.

Cleanup admission does not imply pending release; retirement requires its exact
Applied Terminal receipt and confirmed release. It performs a new resource check.
Uncertain release/mark closes the coordinator while retaining the Applied journal
receipt and actual journal state; it does not rewrite application as Unknown or
invent an effect acknowledgment. Callers must continue to obey the single-owner
boundary: the closed coordinator blocks further work through it, while raw runtime
access remains outside this composition's authority contract.

Seven integration tests and two source omission controls cover these distinctions.
The remaining BG-057/BG-058 handoff is native source/resource and consuming adapter
integration, starting with a bounded mapping review against the current native
checkpoint. No sustained history reset, worker reuse or recovery is inferred.
