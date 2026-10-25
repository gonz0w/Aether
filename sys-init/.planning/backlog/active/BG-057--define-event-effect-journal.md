---
id: BG-057
title: Define and prototype lifecycle event effect journal
status: active
created: 2026-09-06
source_type: research-follow-on
area: model
---

## V1 disposition — 2026-09-07

Further framework expansion is shelved. Existing findings/checks remain available
for the BG-063 simplification audit; only changes needed by the
[accepted v1 scenario](../../../docs/V1-SCOPE.md) proceed. Earlier next steps
below do not override this disposition.


## Problem

Decision 0038 demonstrates twelve effects in one observation cut, repeated force
occurrences and background effects without a related active operation. The
eight-slot submission ledger cannot account Model.batch unchanged. This is local
work, with no demonstrated kernel blocker.

## Inputs and dependencies

Read `docs/research/EVENT-ACCOUNTING-BOUNDARY.md`, decision 0038, the six
EventAccountingBoundaryTests and decision 0037. Coordinate BG-050 for delivery,
BG-033 for unknown/recovery and BG-032 for exact producer-result mapping. Preserve
the existing submission token format, lifecycle semantics and retained evidence.

## Acceptance

Specify a separately versioned, bounded event journal with occurrence identity,
service-generation ownership and retained cause independent of active operation
history. Decide force occurrence semantics explicitly. Define whole-cut capacity
reservation before model mutation, observation retention on denial, serial/history
exhaustion and unknown-result behavior. The review derives a conservative twenty
effects per cut for current source; justify every resource bound before coding.

Prototype reservation, capture and transfer under a single trusted owner. Test
twelve-effect cuts, same/later-cut force, completed/evicted operation provenance,
invalid or capacity-denied cuts leaving clock/events/state unchanged, post-mutation
failure preserving accounting, and unknown obligations with incoming terminal
evidence. Include meaningful omission controls and full checks with retained logs.
Do not claim liveness when a full/unknown ledger prevents observation progress.

## Remaining gates

No automatic acknowledgment-to-observation mapping. Exact native result/instance
identity and terminal/cleanup witnesses require one selected producer profile and
fresh consuming evidence. No native execution, real stream integration, driver
replacement, durable journal or production scheduling is accepted by this story.

## Isolated journal checkpoint — 2026-09-06

Decision 0039 implements twenty-credit reservations, per-occurrence tokens,
retained supplied cause, acknowledgment/retirement and capture-failure closure.
Twelve new tests and a reservation omission control cover the isolated primitive.
Remaining: lifecycle-owned cause retention and validation, admission before
Model.batch, caller observation ownership on denial and unknown-progress policy.
Do not mark BG-057 complete until those integration witnesses exist.

## Journal-owned lifecycle checkpoint — 2026-09-06

Decision 0040 integrates a separate JournalRuntime with existing Model hooks:
retained per-service cause, whole-cut reservation before mutation and token-only
transfer. Ten tests cover bounds, history-independent cause, restart/retry and
failure ownership. Capacity-denied observations remain caller-owned and unchanged.
Unknown currently blocks terminal observations too. BG-057 remains active with
BG-033 for bounded unknown-observation/reconciliation policy before liveness or
recovery claims; control composition and BG-032 producer mapping remain separate.

## Observation inbox checkpoint — 2026-09-06

Decision 0041 supplies four-cut trusted retention, FIFO whole-cut application and
fail-closed overflow without dropping accepted data. Unknown is not reconciled;
commands cannot pass queued observations. Nine tests and a capacity omission
control cover the bounds and failures. BG-033/BG-032 next review exact producer
reconciliation evidence; BG-057 remains active for that policy and control
composition. No native queue, progress guarantee or replacement owner is claimed.

## Reconciliation evidence review — 2026-09-06

Decision 0042 freezes fifteen selected sources and distinguishes confirmed ABI-6
returns from terminal/wait observations and command reply uncertainty. The reviewed
profiles do not implement general lost-result or replacement-owner reconciliation.
BG-058 is captured for qualified confirmed-result mapping and rejection tests;
BG-033/BG-032 retain actual recovery and fresh native consumer witnesses. No journal
unknown transition, shared pin, native source or sibling backlog was changed.

## Confirmed-result qualifier checkpoint — 2026-09-06

Decision 0043 adds pure owner/profile/target/issued-token qualification and exact
selected ABI-6 return classification. Eight cases plus an issued-state omission
control pass without journal or lifecycle mutation. BG-058 is active for serialized
application, separate terminal/cleanup observations and native target acceptance.
Unknown recovery and native force mapping remain unsupported.

## Result application checkpoint — 2026-09-06

Decision 0044 applies qualified returns under a trusted serialized guard, requiring
the exact retained call and fresh qualification. Eight tests plus a binding
omission control cover stale results, reentry and before/after-ack failures.
Acknowledgment never synthesizes observations; uncertain apply closes the owner.
BG-058 retains exact native terminal/cleanup mapping, target bookkeeping and
fresh witnesses. Existing bypass APIs/threads are outside this trusted experiment;
unknown recovery and native force remain unsupported.

## Native target registry checkpoint — 2026-09-06

Decision 0045 adds two-slot trusted target reservation, independent generations,
confirmed launch/reclaim adoption and native terminal-kind/detail projection.
Nine tests and a generation omission control pass. Unknown reservations remain
held; retirement requires separately observed model cleanup. BG-058 remains active
for actual fact-to-lifecycle mapping, stopped-kind and rejected-launch cleanup,
plus fresh native witnesses. The first selected fault is #UD; broader fault vectors,
native force and unknown recovery remain unsupported.

Decision 0046 adds qualified terminal-event projection and distinct stopped policy.
Seven cases and a stopped-kind mutation control pass. BG-058 next defines complete
driver resource accounting and no-target cleanup for confirmed launch rejection;
the generic launch_failed event currently requests reclaim and cannot alone serve
as that native adapter. Fresh native composition remains required.

Decision 0047 adds fixed two-endpoint rejected-launch cleanup. Nine tests and an
endpoint-omission control pass. Local reclaim qualifies only after both endpoints
close; an executed acknowledgment precedes cleaned. BG-058 next inventories
successful-launch resources/waits and composes the driver, then obtains fresh
native rejection/cleanup witnesses. Helpers/devices and unknown recovery remain
outside this profile. No native source or shared pin changed.

Decision 0048 adds admitted-target reader/target/wait accounting. Seven tests and
a wait-release omission control pass. Both targets share one wait slot, retained
through unknown registration, with 64 non-reused tokens. All cleanup orders require
all owned resources released. BG-058 next composes pre-launch resource acquisition,
launch outcome routing and observation delivery, then obtains fresh native witnesses.
Helpers/devices and unknown recovery remain outside the profile.

Decision 0049 composes retained launch attempts, outcome routing and both cleanup
paths with explicit observation delivery. Eight tests and an event-retention
omission control pass. The first driver requires an exact synchronous runtime
with at most two services. BG-058 next defines pre-acquisition capacity and
channel-create failure handling, then obtains fresh consuming native witnesses.
Larger-graph admission and automatic stop/force handling remain open.

Decision 0050 adds channel acquisition reservation and exact result qualification.
Seven tests and a reservation omission control pass. Successful endpoint pairs are
retained before binding; selected create errors complete empty inventory locally.
BG-058 next specifies and executes a fresh native acquisition/rejection/cleanup
witness with pinned producer/consumer inputs. No native or shared pin changed.

Decision 0051 passes a fresh 17-case native acquisition/cleanup witness on the
pinned SI-04 producer: three new cases and 14 byte-identical compatibility clients.
Known channel/launch rejection, endpoint cleanup and wait retention are demonstrated;
the two omission controls fail at exact assertions. BG-058 next routes per-attempt
outcomes through native adapter errors and owned cleanup/retry state. This fixture
is not a full Python driver port or unknown-effect recovery.

Decision 0052 passes 20 fresh native cases with 17 byte-identical compatibility
clients and 177 frozen inputs unchanged. Attempt retains adapter-returned busy
error/endpoints and gates one replacement on cleanup; writer/guard omissions hit
exact 961/963 assertions. BG-058 next integrates wait ownership/release and
cancellation into Attempt. Timed retry, broader error policy and recovery remain open.

Decision 0053 passes 23 native cases for Attempt wait ownership and cancellation.
Cancelled tokens remain owned until explicit release; omission controls hit 971/973.
All 177 inputs are unchanged. Eighteen old binaries match; two Attempt clients
changed with the new field and pass their old oracles. BG-058 next covers native
deadline/completion precedence and service-cancellation intent. Unknown recovery
and timed restart policy remain open.

Decision 0054 passes 27 native cases for deadline/completion precedence and
service-cancellation intent. All 177 inputs remain unchanged; 21 old clients match,
two changed Attempt clients pass prior oracles. Initial compile failure is retained.
BG-058 next defines/tests partial-cleanup failure retention and stop-error policy
before broader control composition. Timed retry and unknown recovery remain open.

## Native error retention — 2026-09-06

Decision 0055 passes 31 native cases. Partial cleanup retains worker/wait after
reader close and adapter reclaim-precondition failure; explicit stop/observation
allows completion. Actual stale-target stop error preserves cancelled intent and
an unresolved Attempt, denying retry. Controls hit exact 990/0 and 991/3 assertions.
All 177 inputs are unchanged; 23 preceding binaries match and four changed Attempt
clients pass their previous oracles. An initial passing run is retained; review
added a readiness wait before deliberate reader close and the final rerun passes.
BG-058 next covers reader-close and wait-release failure retention; BG-033 recovery,
timed restart and wider graph/control integration remain open.

## Native release error acceptance — 2026-09-06

Decision 0056 passes 35 native cases. Reader-close error retains reader/worker/wait
and stops cleanup; wait-release error retains wait after other cleanup succeeds.
Retry remains denied. Exact controls hit 992/2 and 993/3. Reader error is kernel
EACCES; wait release is adapter ownership denial. Both Attempt records remain
unresolved despite deliberate fixture disposal/teardown. All 177 frozen inputs
remain unchanged; 25 of 31 preceding raw clients match and changed clients pass
prior oracles. Initial wrong reader errno expectation is retained separately.
BG-058 next defines native effect-to-event routing with retained pending events;
complete driver composition and BG-033 recovery remain open.

## Native pending events — 2026-09-06

Decision 0057 passes 38 native cases. Admitted launch, terminal observation and
complete cleanup produce generation-tagged pending events. Full inbox retains
ownership; terminal supersedes undelivered launch; cleanup requires terminal
delivery; retirement eligibility waits for Cleaned delivery. Controls hit exact
994/0 and 995/0. This is a bounded in-process inbox, not journal execution or
complete lifecycle policy. All 177 frozen inputs are unchanged; 27 of 35 prior
clients match and changed clients pass prior oracles. Initial passing run before
explicit terminal-delivery guard is retained; final strengthened run passes.
BG-058 next routes known launch rejections and cleanup notifications; BG-057
retains full journal/cut integration and BG-033 unknown recovery.

## Native rejected-launch events — 2026-09-06

Decision 0058 passes 41 native cases. Received native busy launch queues its exact
error and generation in LaunchFailed, retaining both endpoints. Failure delivery
precedes cleanup; Cleaned survives full inbox until acceptance. Duplicate launch
is local denial without another event. Controls hit 997/0 and 998/0. This is the
selected 0x23001/16 path and in-process inbox, not general error/recovery support.
All 177 frozen inputs unchanged; 28 of 38 preceding clients match and changed
clients pass previous oracles. BG-058 next gates routed replacement on accepted
Cleaned delivery with fresh generation events; BG-057 full journal/cut integration
and BG-033 unknown recovery remain open.

## Native routed replacement — 2026-09-06

Decision 0059 passes 45 native cases. Pending Cleaned blocks replacement before
channel acquisition. Accepted delivery permits one generation-two route with fresh
endpoints/worker and reset pending/delivery state. Old inbox contents preserve new
launch backpressure; all replacement events carry two. Duplicate original retry is denied; generation-two budget remains the existing
Attempt rule. Controls hit 1001/0 and 1002/1. All 177 frozen
inputs unchanged; 31 of 41 preceding clients match and changed clients pass
prior oracles. BG-058 next integrates cancellation intent with the routed gate;
BG-057 journal/cut identity and BG-033 unknown recovery remain open. This is
explicit bounded retry, not timed restart or full native driver conformance.

## Native routed cancellation — 2026-09-06

Decision 0060 passes 48 native cases. Cancellation before failure delivery, during
pending Cleaned and after cleanup transfer preserves intent and queued evidence.
Retirement eligibility never grants cancelled retry permission: pending cleanup
denies 0/16; completed delivery still denies retry/launch 0/13 with allowance unused.
Controls hit 1005/0 and 1004/0. All 177 frozen inputs unchanged; 32 of 45 prior
clients match and changed clients pass previous oracles. BG-058 next consumes
routed cancellation for a live admitted worker and observed terminal event;
routed stop errors, BG-057 journal/cut integration and BG-033 recovery remain open.
This is in-process rejected-route cancellation, not external control delivery.

## Native routed live stop — 2026-09-06

Decision 0061 passes 51 native cases. Routed live stop preserves worker/reader/wait
and pending state, without fabricating Terminal or delivery acknowledgment. Native
terminal 144 supplies the event; accepted delivery gates complete cleanup, and
Cleaned delivery still leaves cancelled retry denied. Both launch-delivery orders
pass. Controls hit 1006/0 and 1007/0. All 177 frozen inputs unchanged; 35 of 48
prior clients match and changed clients pass prior oracles. BG-058 next qualifies
routed stop-error preservation of pending evidence and intent. BG-057 full journal
integration and BG-033 recovery remain open. No external control or POSIX signal
semantics are claimed.

## Native routed stop error — 2026-09-06

Decision 0062 passes 54 native cases. Actual stale-target stop error preserves
exact errno, intent, unresolved worker and pending historical terminal evidence.
Its later transfer is not recovery: cleanup fails on native observation, queues
no Cleaned and keeps retry denied. Controls hit 1009/3 and 1010/3. All 177 frozen
inputs unchanged; 38 of 51 preceding clients match and changed clients pass
prior oracles. BG-058 next qualifies routed partial cleanup retaining remaining
resources without Cleaned. BG-057 journal identity and BG-033 recovery remain
open. Final fixture accounting does not establish successful Attempt cleanup.

## Native routed partial cleanup — 2026-09-06

Decision 0063 passes 57 native cases. Reader close and worker reclaim precede a
wait-release ownership denial; the route retains unresolved wait, emits no Cleaned
and denies retry. Repeated failure preserves the same state. Controls hit 1012/3
and 1013/3. All 177 frozen inputs unchanged; 41 of 54 preceding clients match
and changed clients pass prior oracles. Deliberate fixture wait disposal leaves
Adapter clean but never qualifies route cleanup/recovery. BG-058/BG-057 next
review accumulated native evidence against model driver integration gaps;
complete operation identity, journal/cut delivery and BG-033 recovery remain open.

## Native driver review — 2026-09-06

Decision 0064 completes the comparison, not this story. The cited review in
`docs/research/NATIVE-DRIVER-INTEGRATION-REVIEW.md` defines stable follow-ons:
ND-01 issued identity/admission and ND-02 terminal kind qualification (BG-058),
ND-03 whole-cut acceptance and actual retirement (BG-057 with BG-058), ND-04
selected errors/unknown retention (BG-058; recovery remains BG-033), and ND-05
policy composition (BG-040/BG-057). Acceptance and negative cases are in the
review. Next: ND-01 local bounded contract and test plan; no kernel blocker is
demonstrated. Preserve existing tokens and ABI; native implementation requires
fresh consuming evidence. The 57-case decision 0063 witness remains unchanged.

## Native binding contract — 2026-09-06

Decision 0065 specifies ND-01 in `docs/specs/NATIVE-DRIVER-BINDING-V0.md`.
NB-01–09 define required identity/admission and partial-failure cases. Contract
complete; implementation and fresh target witness remain open. Next: bounded
trusted native binding fixture, full original tokens, two attempts, one creation
and retained synthetic issuance (explicitly not journal execution). No consumed
identity reset or retirement API. ND-02 exact terminal kind, ND-03 cut acceptance,
ND-04 errors/recovery boundaries and ND-05 policy composition remain tracked by
decision 0064; this does not complete either active story.

## Native binding admission — 2026-09-06

Decision 0066 passes 61 native cases. Two generation-one services bind complete
issued tokens to actual retained workers/readers; preflight denial preserves
reservation and acquisition count, and consumed tokens remain denied after
fixture cleanup. Controls hit 1014/0 and 1015/0. All 178 frozen inputs unchanged;
44 of 57 prior raw clients match and changed clients pass prior oracles.
This is synthetic issuance and read-only launched qualification, not a pending
event queue or journal. Next: NB-04 post-acquisition failure retention with an
omission control. Remaining ND-01 cases, ND-02–05 and BG-033 recovery stay open.

## Native post-acquisition binding failure — 2026-09-06

Decision 0067 passes 63 native cases. Local binding failure after actual channel
success retains both endpoints, original token/slot and consumed/pending state;
separate binding_failed closes admission without inventing native errno. Repeated
calls deny without new acquisition. Writer-loss control hits 1017/0. All 178
frozen inputs unchanged; 44 of 61 prior raw clients match and changed clients
pass prior oracles. Fixture disposal clears Adapter accounting but leaves the
driver failed and reservation retained; no recovery or journal cleanup is claimed.
Next: NB-05 selected creation/launch rejection within an explicitly scoped fixture.
Remaining ND-01, ND-02–05 and BG-033 recovery stay open.

## Native binding busy rejection — 2026-09-06

Decision 0068 passes 67 native cases. Received creation busy retains empty
inventory; launch busy retains both endpoints. Exact errors and consumed tokens
remain while provisional slot claims release. Another issued service launches
in the released slot after fixture disposal; rejected tokens stay denied.
Controls hit 1018/0 and 1019/0. All 178 frozen inputs unchanged; 44 of 63 prior
raw clients match and changed clients pass prior oracles. The two busy paths use
explicitly inventoried fixture interference, not unknown inventory adoption.
Next: NB-06 expected target/received result qualification. Other errors, remaining
NB cases, ND-02–05 and BG-033 recovery stay open; no complete driver claim.

## Native expected target — 2026-09-06

Decision 0069 passes 72 native cases. Expected targets are reserved before
acquisition; actual worker/reader retention and writer transfer precede matching.
The successful case distinguishes native generations two/one from service
generation one. Wrong slot or generation closes admission with retained actual
resources and unchanged local counter. Controls hit 1021/0 and 1022/0. All 178
frozen inputs unchanged; 44 of 67 preceding raw clients match and changed
clients pass prior oracles. Known fixture admission history is explicitly recorded;
no unknown inventory adoption or kernel-fabricated-handle claim. Next NB-08 bounded
exhaustion, then NB-09 lost replies. Other errors, ND-02–05 and BG-033 stay open.

## Native generation exhaustion — 2026-09-06

Decision 0070 passes 75 native cases. Actual fixture admissions exhaust native
slot zero at generation three; repeated denial preserves unused issuance, empty
records and zero acquisition count. The same token reserves slot one and acquires
a channel without advancing that native generation. Controls hit 1023/3 and 1024/3.
All 178 frozen inputs unchanged; 44 of 72 prior raw clients match and changed
clients pass prior oracles. Pair disposal is fixture accounting, not retirement.
This is native-generation NB-08 coverage, not all token/cut/history exhaustion.
Next: NB-09 bounded invocation/receipt ownership design before lost-reply testing.
Other NB requirements, ND-02–05 and BG-033 recovery remain open.

## Receipt ownership design — decision 0071

Decision 0071 (`docs/decisions/0071-native-receipt-ownership.md`) specifies
a single driver-owned invocation/receipt position and non-repeatable phases.
Next, BG-058/BG-057 implement IR-01–04 actual channel-return retention and
local application backpressure; launch transfer IR-05–06 and synthetic absence
IR-07 follow. NB-09 is not yet qualified. ND-02–05 and BG-033 remain open.
The 75-case decision 0070 witness remains unchanged; no native execution is added.
Foundations O-01/O-03/O-04, I-01/I-03–06 and E-01–08 retain their existing scope;
no shared pin, API, exception, output or unsafe primitive changes. Review evidence
is `docs/evidence/native-receipt-contract-2026-09-06/`.

## Native channel receipt — 2026-09-06

Decision 0072 passes 80 native cases. Real channel returns remain owned before
local application; repeated invocation/launch authorization and mismatched local
application deny. Matched application happens once; injected closure preserves
phase, endpoints and consumed issuance. Controls hit 1025/0 and 1026/0.
All 178 frozen inputs unchanged; 44 of 75 prior raw clients match, and changed
clients pass their previous oracles. This qualifies the IR-01–04 creation slice,
not lost kernel replies, journal retirement or complete NB-09.
Next: IR-05–06 bounded launch receipt retention and writer transfer. IR-07 synthetic
absence, other NB/ND requirements and BG-033 recovery remain open.

## Native launch receipt — 2026-09-06

Decision 0073 passes 84 native cases. Successful launch returns retain the actual
worker/reader and mark the writer transferred before local application. Pending
receipts deny additional invocation/admission and launched-event qualification.
Matching application advances generation once; injected closure preserves receipt
and consumed identity. Controls hit 1030/0 and 1031/0.
All 178 frozen inputs unchanged; 44 of 80 prior raw clients match, and changed
clients pass their prior oracles. This qualifies IR-05–06 in the trusted local
fixture, not missing kernel replies, journal acceptance or recovery.
Next: IR-07 synthetic Started-with-no-return closure. Other NB/ND requirements and
BG-033 unknown-effect recovery remain open.

## Synthetic missing-return and binding review — 2026-09-06

Decision 0074 passes 89 native cases, including IR-07 synthetic creation/launch
absence. The real start guards run but the selected syscall is deliberately
omitted. Closure retains Started, pending identity and unknown outcome; no invented
error or retry is accepted. Controls hit 1033/0, 1034/0 and 1035/0.
All 178 frozen inputs unchanged; 44 of 84 prior raw clients match, and changed
clients pass prior oracles. This is synthetic transition coverage executed in a
native fixture, not an actual lost kernel reply or recovery witness.
The binding acceptance review keeps remaining NB gaps explicit. Next: ND-02
terminal-kind contract against the frozen producer; ND-03–05 and BG-033 remain open.

See `docs/research/NATIVE-BINDING-ACCEPTANCE-REVIEW.md` for the NB-01–09
coverage/gap crosswalk and retained owners. Contract work is locally unblocked;
no new kernel operation is inferred or requested.

## Terminal evidence contract — decision 0075

Decision 0075 specifies exact terminal kind/result and bounded observe/status/observe coherence. Next: BG-058 NT-01–02 actual colliding terminal-kind probes, then NT-03–07 bound retention/identity. ND-01 gaps, ND-03–05 and BG-033 remain open. No native source or shared pin changes; the 89-case witness remains unchanged.

The local contract is `docs/specs/NATIVE-TERMINAL-EVIDENCE-V0.md`; source review
and validation are retained in `docs/evidence/native-terminal-contract-2026-09-06/`.
Foundations O-01/O-03/O-04, I-01/I-03–06 and E-01–08 apply in unchanged scope;
no new exception, dependency, output, unsafe primitive or shared ABI is adopted.

## Native terminal collisions — 2026-09-06

Decision 0076 passes 114 native cases: all 89 prior base cases, four new terminal
probes and 21 existing optional-worker regression cases. Actual normal exit 134
versus fault 134 and normal exit 143 versus stop 143 retain distinct kinds despite
equal encoded results. Live sampling reads once; terminal sampling checks three
coherent reads. The kind omission control hits 1036/0.
All 181 frozen inputs unchanged; 44 of 89 prior base clients match, and changed
clients retain their oracles. The rebuilt worker's old modes pass their consuming
regressions. This is standalone NT-01–02 coverage, not bound pending-fact or journal
integration. Next: NT-03 retained-target identity and sampling reservation; NT-04–07,
remaining NB/ND requirements and BG-033 recovery stay open.

NT-04 specifically retains raw partial status and distinguishes the Adapter
boolean guard’s local errno 71 from native rejection before error-path claims.

## Bound sampling — 2026-09-06

Decision 0077 passes 120 native cases: all 114 prior cases and six sampling probes.
Owner/index and actual Worker/full-token checks reject before sampler reads. A
retained terminal fact takes three coherent reads and holds the single pending
position; duplicate reads/admission deny. Actual stale lookup 0x25001/9 closes the
driver while retaining the original target and error. Omission controls hit 1040/0
and 1039/0; four positive probes finish 100/3. All 181 frozen inputs unchanged.
65 of 114 prior clients match byte-for-byte; all prior oracles pass.

Fixtures seed admitted state from actual handles and trusted token/counters to
fit the unchanged 4 KiB bound. This qualifies bounded NT-03 sampling guards and
retention, not full launch-to-sampling composition, journal or recovery. Next is
NT-04 raw partial receipts and native/local error origin; composition, NT-05–07,
remaining NB/ND requirements and BG-033 remain open.

## Synthetic receipt validator — 2026-09-06

Decision 0078 adds a pure Rust raw sample accumulator and a required offline
host validator gate. Synthetic malformed replies retain their exact received
prefix; native operation/errno and local causes remain distinct. No native
Adapter/Driver source changes: the 120-case decision 0077 witness remains current.
Next: integrate actual raw Adapter capture and bound Driver retention, then run
fresh native cases. Host synthetic inputs do not complete NT-04/05 resource or
producer coverage. NT-06/07, full launch composition, journal and recovery remain.

## Native raw capture — 2026-09-06

Decision 0079 passes 125 native cases, including all 120 previous oracles.
Raw capture retains actual signed RAX/RDX/R8 for a coherent terminal sample and
actual stale errors at O1, S and O2. Successful prefixes remain intact; the native
prefix-omission control reaches 1042/reclaimed=1. Four positives finish 100/3.
All 183 frozen inputs unchanged; 65 of 120 prior images match byte-for-byte.

This is standalone raw capture and validation. Combined driver/receipt probes
exceeded 4 KiB in retained size attempts; binding.rs remains byte-identical to
its prior witness and still uses the decoded sampler. Next: a size-bounded driver
composition strategy before integrating raw history. Native malformed injections,
NT-05–07, full launch composition, journal retirement and recovery remain open.

## Composition size study — 2026-09-06

Decision 0080 identifies a build-feasible retained-sampling candidate: all 120
compiler configurations fit, with a 4048-byte maximum (48-byte margin). The candidate
uses optimization s, recorded inlining choices and normalized diagnostic paths;
all twelve paired-path images match. Nine candidate host tests and two omission
controls pass. This is build/host evidence only; the current runtime is unchanged.
Next: explicit profile/default compatibility decision and a fresh 127-case native
witness before adoption. Seeded admission, full launch composition, malformed native
injections, NT-05–07, journal retirement and recovery remain open.

## Native retained sampling — 2026-09-06

Decision 0081 passes all 127 native cases under retained-sampling-v1, including
all 125 prior oracles and two bound stale-prefix cases. The exact size-study
candidate now composes Driver with fixed raw-receipt storage through an exclusive
Sampling borrow. S/O2 native -9 preserves successful prefixes, original diagnostic
target, closed admission and pending state; positive probes finish 100/3.
All 183 frozen inputs unchanged; largest image 4048 bytes (48 bytes headroom).
All 121 comparable native images match the study bytes; six cases omitted by the study
have fresh native coverage and no claimed study baseline.

This qualifies bounded retained sampling with fixture-seeded admission. It does
not qualify full launch composition, malformed native injection, NT-05–07,
journal/history retirement or recovery. Next: NT-04 labelled malformed-reply
injection through the bound session with retained resources and exact local causes;
then NT-05 interruption and NT-06/07 pending-history bounds. BG-057 owns consumer
retirement and BG-033 retains unknown-owner recovery.

## Bound malformed sampling — decision 0082

Decision 0082 passes 136 native cases: all 127 prior oracles plus six labelled
malformed-reply probes and three omission controls. Each probe omits exactly one
selected S/O2 syscall and injects a synthetic raw triple; other received samples
are real. Exact data and local causes survive while Driver closes admission and
retains worker, reader, token, pending index and generation, with no terminal fact
or invented native errno. Further sampling denies without another read.

Six positives finish 100/reclaimed=3 after asserted retention and known fixture
cleanup. Skip closure, forget reader and invent errno controls reach 1043/0,
1044/0 and 1045/0. All 183 frozen inputs unchanged; 90 of 127 previous images
are identical. Largest image remains 4048 bytes; new images fit 3760–3872 bytes.
The first run's one-reclaim completion was rejected by the kernel and is retained;
the corrected run preserves the required three-reclaim positive oracle.

This is synthetic NT-04 qualification executed in the native fixture, not malformed
kernel output or a lost reply. Admission is still fixture-seeded. Next: NT-05
explicit synthetic interruption after O1/S, retaining resources and partial history
without retry/application; NT-06/07 pending-history bounds, full launch composition,
BG-057 consumer retirement and BG-033 recovery remain open.

## Interrupted sampling — decision 0083

Decision 0083 passes 143 native cases: all 136 prior oracles, empty-sample
interruption denial, two partial interruptions and four omission controls.
The partial probes retain actual O1 or O1/S returns, then invoke a private synthetic
interruption between reads. Local(Interrupted), exact prefix/count, closed admission,
pending identity, worker/reader, full token and generation remain. Repeated interrupt
and read calls deny without additional reads, invented fact/error or application.

Three positives finish 100/reclaimed=3 after retention checks and known fixture
cleanup. Omission controls reach 1046/0 (closure), 1047/0 (prefix), 1048/0 (fact)
and 1049/0 (reader). All 183 frozen inputs unchanged; 90 of 136 previous
images match byte-for-byte. Largest image remains 4048 bytes; partial interruption
probes are 3904/3952 bytes. Four earlier size revisions are retained, including
failed strict links; the fifth keeps all assertions by separating empty denial
and sharing the full-prefix predicate before and after denied calls.

This is synthetic NT-05 disposition in a native fixture, not syscall cancellation,
asynchronous delivery or lost-return recovery. Admission remains fixture-seeded.
Next: define/qualify NT-06/07 pending-history identity, conflict and capacity rules
with BG-057 consumer retirement. Full launch composition, additional NT-04 O1
injections and BG-033 unknown-owner recovery remain open.


## Decision 0084 follow-on: PH-07

Before any native pending-history acknowledgment or reset API, specify the named
whole-cut coordinator, owner/cut binding, launched-to-terminal ordering, applied
acknowledgment, stale acknowledgments and failure after application. Define the
exact boundary that permits resource/history retirement. Held/Duplicate is not
reservation, capture, application, reclaim or applied Cleaned. The model's pending
event replacement and inbox clearing do not establish native journal acceptance.
See docs/specs/NATIVE-PENDING-HISTORY-V0.md; BG-058 owns PH-01–06 comparison and
capacity qualification. This follow-on remains open; no retirement API is accepted.

## PH-07 handoff — decision 0155

The bounded PH-06 closed terminal slice now has fresh consumer execution. Start
the coordinator contract review described above; no acknowledgment/reset API is
authorized by the history witness alone. Define exact whole-cut ownership, ordering,
applied acknowledgment, denial/unknown retention and resource retirement before
implementation. No new kernel operation is demonstrated necessary yet.

## PH-07 contract — decision 0156

NC-01–08 now specify a private serialized CutCoordinator, exact whole-cut identity,
ordered phases, reserved application records, retained uncertain outcomes and
applied-Cleaned retirement without recycling. Source review and frozen inputs
are retained. This is design acceptance, not implementation or a new target run.
BG-059 qualifies the pure core next; BG-057 remains active for actual lifecycle/
journal and native integration. BG-060 owns sustained retention/reuse; BG-033
retains recovery. Do not substitute route delivery or intake for application.

## Pure retirement model — decision 0158

BG-059 now qualifies all-Cleaned-cut retirement through an explicitly synthetic
resource adapter, with whole-cut denial, exact replay and retained partial progress.
No actual journal obligation, endpoint/wait release or native cleanup is inferred
from its booleans. BG-059 retains NC-06 pending disposition and mixed-cut retirement;
BG-057 remains open for real lifecycle/journal and fresh native integration.

## Actual adapter handoff — decision 0159

BG-059's pure coordinator/disposition qualification is complete (254 model tests,
nine embedded cut-related omission controls). Next implement the actual lifecycle/
journal adapter: source qualification before phase admission, exact transition
postconditions, whole-cut effect reservation/capture and separately issued cleanup
obligations. Cleaned acceptance itself must require verified cleanup; retirement's
synthetic inventory gate is insufficient. Bind observation-cut and effect-cut
identities explicitly and preserve uncertainty on post-mutation failure. The pure
fixture's reserve-no-effects-on-error promise needs real evidence. Then integrate
with current native History and fresh consuming tests; do not infer origin from
preconstructed Source records. BG-058 complete launch composition, BG-060 reuse,
BG-033 recovery and BG-056 producer source closure remain their separate owners.

## Launched actual journal adapter — decision 0160

Decision 0160 connects Launched cuts to the actual JournalRuntime, Model.batch
and EventJournal. A prepared journal ticket is reserved before application; other
commands deny until consumption/cancellation. LaunchedAdapter revalidates exact
executed launch-token binding and starting state, checks the applied transition,
and verifies all generated effect obligations before returning the cut receipt.
Provider launch produces the real dependent launch obligation with its original
cause. Empty-effect cuts still retain their actual journal serial. Exact replay
changes neither lifecycle state nor journal. Queued/derived runtimes explicitly
deny the new reservation API so intake cannot masquerade as application.

All 263 model tests pass, including nine new adapter tests with two source omission
controls for missing transition and capture. All ten local gates pass in
`run-i4iynltv` with unchanged checked inputs. All twelve native consumer sources,
three release locks and catalog bytes remain unchanged. This is actual integration
of policy-model/journal code; native source origin and launch execution are still
injected model facts. No new QEMU or production-conformance claim is made.

Next BG-057: exact Terminal mapping and subsequent cleanup/Cleaned admission through
the actual lifecycle/journal adapter. Native source/worker provenance and consuming
integration remain BG-058/BG-057; BG-060 reuse and BG-033 recovery stay open. The
185-case native checkpoint and BG-056 producer source-closure limitation remain
unchanged. No native effects, reset or shared ABI are added.

## Terminal actual journal adapter — decision 0161

Decision 0161 integrates Terminal cuts with the actual lifecycle model and effect
journal. It validates bounded synthetic facts and the executed launch binding,
then maps normal exit, fault and stop without collapsing equal numeric results.
Application must retain terminal ownership, pending cleanup and exactly one real
reserved reclaim obligation. Replay returns the retained receipt without another
transition. Missing reclaim or incorrect terminal kind closes the adapter while
retaining the resulting state and captured obligations.

All 271 model tests pass, including eight Terminal adapter tests and two source
omission controls. All ten local gates pass in `run-v1m4lwsw`, with unchanged
checked inputs. All twelve native consumer sources, three release locks and
catalog bytes match the preceding checkpoint. This tests actual policy-model and
journal code with synthetic native-origin facts; it does not demonstrate native
source capture or resource disposal. No independent reviewer sign-off is claimed.

Next BG-057: Cleaned admission after the actual reclaim obligation is applied and
remaining resources are verified empty. Native provenance remains BG-058; sustained
reuse remains BG-060 and recovery BG-033. The 185-case native checkpoint and BG-056
producer source-closure limitation remain unchanged.

## Cleaned actual journal adapter — decision 0162

Decision 0162 integrates Cleaned admission with the actual lifecycle model and
journal. It retains the exact reclaim token emitted by Terminal and requires its
executed disposition independently of a fresh, exact-source resource inspection.
Reader, writer, worker and wait ownership must all be empty, with no unresolved
cleanup. All cut members are preflighted before model mutation. Completion leaves
the same generation unowned with cleanup complete and no deadline; exact receipt
replay neither inspects nor applies again. Retry policy can schedule a future
attempt but this fixed-time cut does not launch a replacement.

All 280 model tests pass, including nine Cleaned tests and two source omission
controls. All ten local gates pass in `run-wpld9nvb`, with unchanged checked
inputs. All twelve native consumer sources, three release locks and catalog bytes
match the preceding checkpoint. Resource inspection and executed acknowledgments
remain trusted synthetic inputs; this is actual policy-model/journal integration,
not native resource disposal. No independent reviewer sign-off is claimed.

Next BG-057: combine the actual three-phase journal adapter with pending release
and retirement, including mixed cuts. BG-058 retains native provenance/disposal;
BG-060 retains sustained reuse and BG-033 recovery. The 185-case native checkpoint
and BG-056 producer source-closure limitation remain unchanged.

## Actual journal/retirement composition — decision 0163

Decision 0163 qualifies the actual JournalRuntime, CleanedAdapter, CutCoordinator
and Retirement together. Mixed Cleaned/Launched and Cleaned/Terminal cuts retire
only the Cleaned member and preserve the other member's real journal obligation,
synthetic pending position and lifecycle state. Old release/retirement replay is
inert. Cleanup does not substitute for pending release, and retirement performs
a fresh resource inspection. Uncertain release or marking closes the coordinator
while retaining Applied receipts, partial tombstones and actual journal state.

All 287 model tests pass, including seven new integration tests and two source
omission controls. All ten local gates pass in `run-zegjjv6m`, with unchanged
checked inputs. All twelve native consumer sources, three release locks and catalog
bytes match the preceding checkpoint. Runtime algorithms are unchanged: this is a
composition witness using trusted synthetic resource, pending and mark callbacks.
It is not native disposal or independent reviewer sign-off.

Next BG-057/BG-058: review the native adapter mapping against the current 185-case
checkpoint and define a bounded consuming integration witness for the three-phase
cut, pending release and retirement path. Native provenance/resource ownership
remain explicit requirements. BG-060 retains sustained reuse, BG-033 recovery and
BG-056 the producer source-closure limitation; no historical waiver is broadened.

## Native mapping and witness handoff — decision 0164

Decision 0164 maps the tested model/journal path onto current native sources.
The next local witness must compose actual Driver reserve/acquire/launch with
retained History instead of installing Applied Binding state directly. Native
journal issuance and per-attempt cleanup remain later implementation gates; global
adapter cleanliness and fixture disposal cannot establish mixed-cut retirement.
The review found no new kernel prerequisite for the first consuming witness.

All ten local gates pass in `run-_diyh18x`, including 287 unchanged model tests.
All twelve native consumer sources, release locks and catalog bytes remain
unchanged. This is a source review and witness plan, not new QEMU execution or
independent sign-off. The reviewed inputs and checks are retained in
`docs/evidence/native-journal-mapping-2026-09-07/`.

Next BG-058: implement and consume the one-attempt actual launch-to-history probe
specified in docs/research/NATIVE-JOURNAL-MAPPING.md. BG-057 retains native cut/
effect ownership, exact reclaim and per-attempt cleanup; BG-060 reuse and BG-033
recovery remain open. Preserve the 185-case checkpoint and BG-056 producer
source-closure limitation without expanding historical exceptions.

## Actual native launch/history — decision 0165

Decision 0165 passes all 190 fresh Aether native cases. The new positive uses
actual Driver reservation, channel acquisition and received/applied launch before
moving the same records into History. Real terminal O1/S/O2 is retained; replay
performs no new reads or launch. Explicit fixture disposal preserves history and
consumed issuance. Four controls reject exactly at 1071/0, 1072/0, 1073/0 and
1074/0; the positive completes at 100/3.

All 185 previous ABI-15 images and 151 ABI-6 rebuilds remain byte-identical. All ten
local gates pass in `run-ge4pi5zf`, including 287 model tests; five focused runner
checks pass. Maximum native image is 7592/8192 bytes. Evidence is retained in
`docs/evidence/native-launch-history-2026-09-07/`, including interrupted runs,
preflight layouts, legacy byte differences and the corrected inventory check.

Fixed issuance remains synthetic; no native journal receipt, Cleaned admission or
retirement is implemented by this witness. Producer/worker and shared release pins
are unchanged. The catalog remains at 50 bundles/3019 historical outcomes pending
complete producer source closure under BG-056; no historical exception is extended.

Next BG-057: define and implement bounded native cut/effect ownership against the
qualified native launch/history path. BG-058 retains per-attempt cleanup/reclaim
provenance, BG-060 sustained reuse and BG-033 recovery. No new kernel prerequisite
was required for this one-attempt composition.

## Native storage and credit-retirement gate — decision 0166

Decision 0166 defines the first native reservation/storage slice: six retained
cut records and one twenty-entry full-token effect pool. Checked source indices
avoid self-referential pointers into movable History; they confer no native
resource authority. Reservation/cancellation must retain consumed serials and
membership. No Applied receipt or effect acknowledgment is exposed by this slice.

The proposed repr(C) layout measures 1976 bytes aligned to 8 on the host, with the
same compile-time assertions passing for x86_64-unknown-none under Rust 1.98.0.
This excludes History, Driver, source/lifecycle/call records, stack and code; it
is not a total memory budget or runtime witness. All ten local gates pass in
`run-coqgyxx9`, including 287 unchanged model tests. Native consumers, release
pins and catalog bytes remain unchanged. Evidence: `docs/evidence/native-cut-storage-2026-09-07/`.

Next BG-057: implement the private fixed-storage reservation/cancellation owner
and qualify its bounds, identity and exhaustion with source omission controls.
Native source integration and QEMU acceptance follow separately. Explicit effect
record retirement is required before credit reuse; the first slice denies an
occupied pool rather than importing Python eviction semantics. BG-058 retains
cleanup provenance, BG-060 sustained reuse and BG-033 recovery. The 190-case native
checkpoint and BG-056 producer source-closure limitation remain unchanged.

## Fixed Rust reservation — decision 0167

Decision 0167 implements a private fixed Rust reservation/cancellation owner.
One exclusive owner anchor binds lifetime-bearing keys; foreign keys deny even
when serials match. One/two ordered Launched indices reserve a retained record and
twenty credits atomically. Exact duplicates are inert, different active requests
are Busy, and cancellation retains membership and both consumed serials. Six
cancelled records exhaust storage; occupied effects, closure and u64 exhaustion
deny without mutation. There is no application, acknowledgment or reset API.

Five host Rust tests and three source omission controls pass through the required
sample-receipts gate. The same code compiles for x86_64-unknown-none, asserting
1976-byte storage and a 1984-byte owner including its identity reference. These
exclude native History/resources/stack and are not target execution. All ten local
gates pass in `run-k_1qkpg_`, including 287 unchanged model tests. All twelve
existing native consumer sources, release locks and catalog bytes remain unchanged.
Evidence: `docs/evidence/native-cut-reservation-2026-09-07/`.

Next BG-057: bind reservation source selection to the actual native Driver/History
path and consume a fresh Aether witness before claiming native reservation.
Lifecycle application/effect capture, explicit effect-record retirement and exact
receipt publication follow separately. BG-058 retains cleanup provenance, BG-060
sustained reuse and BG-033 recovery. The 190-case native checkpoint and BG-056
producer source-closure limitation are unchanged.

## Native reservation binding — decision 0168

Decision 0168 passes all 194 fresh Aether native cases. A private reservation
binding validates original Context, complete launch token, owned reader/worker,
Applied acquisition/launch and full target/generation before reserving any cut.
The source History is immutably borrowed throughout reservation/cancellation.
Received-but-unapplied launch, foreign owner, substituted token and absent second
attempt deny; the subsequent valid request still receives serial one. Duplicate,
cancellation and new serial two preserve the real terminal Sample and pending
position without another read or launch. Explicit fixture disposal is separate.

The positive finishes at 100/3. Three controls reject at 1075/0, 1076/0 and 1077/0.
All 190 prior ABI-15 images and 151 ABI-6 rebuilds remain byte-identical. All ten
local gates pass in `run-_kw_g65q`, including 287 model tests and the ten Rust
groups with five reservation tests/three source controls. The maximum image is
8056/8192 bytes. Failed preflight layouts, the stack-fault run and assembly are retained;
checked accesses remove slice-panic formatting without changing the size limit.
A constant zero initializer removes constructor temporaries; a separate probe helper
keeps reservation storage out of the launch/capture frame. The 4096-byte native
stack and all image limits remain unchanged. Native execution validates these
particular paths; emitted frame sizes do not prove a general worst-case budget.
Evidence: `docs/evidence/native-reservation-binding-2026-09-07/`.

This is native reservation/cancellation with one actual attempt, not lifecycle
application, effect acknowledgment, two-live-member application or retirement.
Issuance remains the fixed fixture token set. Producer/worker and release pins are
unchanged; the catalog remains at 50 bundles/3019 historical outcomes pending
BG-056 complete producer source closure. No historical exception is extended.

Next BG-057: bounded native Launched application and complete effect capture before
publishing any Applied receipt. The immutable reservation borrow must evolve under
one explicit mutation owner; receipt publication cannot substitute for actual
state transition. BG-058 retains cleanup/reclaim provenance, BG-060 sustained
reuse and BG-033 recovery. Image headroom is 136 bytes in this probe, not a promise
that additional code will fit; future probes require their own size review.

## Fixed Rust application core — decision 0169

Decision 0169 implements a fixed Rust Launched application transaction with
exclusive policy/reservation ownership. Independent attempts and a single started-
dependency pair have explicit starting/started state. Whole-member preflight
precedes mutation; the provider's transition generates and retains its dependent
launch obligation with all ten occurrence-token fields and Reserved disposition.
Verified application publishes an owner-bound Applied receipt; replay does not
repeat policy mutation or effect capture. Foreign/cancelled/stale inputs deny.
Unknown is recorded and the owner closes before mutation; failed verification
retains actual state and captured effects, and blocks replay/cancel/new admission.
Read-only state/effect inspection grants no execution authority.

All seven new application tests and four omission controls pass, alongside the
five reservation tests and three reservation controls. All ten local gates pass
in `run-7zvhu56k`, including 287 unchanged model tests and ten Rust groups. The same
code compiles for x86_64-unknown-none. Storage stays 1976 bytes; Reservations stays
1984; Application is 1992, excluding native History/resources/stack. The profiles
generate at most one effect per cut but retain the twenty-entry pool. Even a zero-
effect Applied cut keeps twenty credits; further reservation remains Full until
explicit retirement exists. No acknowledgment, effect execution or reset API.

All 194 existing ABI-15 images and 151 ABI-6 rebuilds are byte-identical, with a
maximum ABI-15 image of 8056 bytes. The new methods are not called by the native
consumer: this is host Rust execution and target compilation, not a fresh Aether
application witness. The 194-case native checkpoint remains decision 0168. Full
native integration still requires an exclusive original-History owner, exact
source revalidation, actual worker binding and a fresh consuming witness. Tokens
use the fixed fixture's symbolic domain; native journal issuance is not claimed.
Release locks and the 50-bundle/3019-case catalog remain unchanged. BG-056 complete
producer source closure remains a separate catalog-acceptance gap.

The first image-comparison driver failed while mistaking `rustc --version` for a
build command; its frozen inputs, driver and traceback are retained. Filtering
actual output-producing compiler commands fixed the driver; the fresh full rebuild
then passed. No image failure or target-run result is inferred from that error.
Evidence: `docs/evidence/launched-application-core-2026-09-07/`.

Next BG-057/BG-058: bind this application owner to qualified native launch history,
verify complete generated effects and consume fresh target controls. The driver
return's Applied state and policy observation's Applied receipt remain distinct.
BG-058 keeps per-attempt cleanup/reclaim provenance; BG-060 sustained reuse and
BG-033 recovery stay open. No additional host-platform campaign or sibling change.

## Native Launched application — decision 0170

Decision 0170 consumes the fixed Rust Launched application against original
native Driver/History. One binding exclusively borrows History and Application;
the shared full-source qualifier runs before reservation and application. Actual
launch return and policy application remain separate. Attempt zero's Launched
observation changes policy [0,0] -> [1,0] and retains the complete dependent-launch
token [1,2,3,1,0,5,1,6,7,1] with Reserved disposition. Exact replay is inert;
foreign Context, altered token and unsupported member deny before application.
There is no generated-effect execution, acknowledgment, readiness or retirement.

The positive finishes at 100/3. Skipped transition, dropped capture and corrupted
capture reject at 1078/0, 1079/0 and 1080/0 after checking retained Unknown,
closure of both owners, no retry/cancel/new admission, and the actual captured
output (including the corrupt token). Assertion 1082 distinguishes a broken
failure-retention postcondition from the designated semantic result. No terminal
sampling is needed for Launched: both primary histories stay empty and Driver
reads/pending stay unchanged through separate fixture disposal. The two ordinary
fixture workers completing the 100/3 contract do not execute the generated token.

All 198 fresh Aether cases pass. The prior 194 outcomes retain their exact expected
semantics; 190 images remain byte-identical. Four reservation images change due to
the extracted shared qualifier and are freshly exercised. All 151 ABI-6 rebuilds
remain byte-identical. New application images are 7344/7296/7232/7552 bytes;
the entire suite's maximum is 8152/8192 (the reservation positive). All ten
local gates pass in `run-eu5oc9o3`, including 287 model tests and ten Rust groups
with twelve reservation/application tests and seven omission controls. The same
core still compiles for x86_64-unknown-none; its storage/policy bounds are unchanged.

Preflights 1–2 exceed the image limit; preflight 3 fits but assembly exposes an
oversized stack frame. Full-token folded comparisons, direct empty-history checks
and exclusive borrowing remove unnecessary comparison code, Sample temporaries
and application copies. Preflight 4 and the eight-case restricted diagnostic pass
before the full consuming run. These are retained separately. The native stack
remains 4096 bytes, with no heap, new unsafe site, syscall or limit relaxation.
Stack/code measurements describe this probe, not a production resource budget.
Evidence: `docs/evidence/native-launched-application-2026-09-07/`.

Producer/worker/release pins remain unchanged; symbolic issuance/context labels
remain the fixed fixture domain and do not claim native journal issuance. Catalog
acceptance remains pending BG-056 complete producer source closure; the catalog
stays at 50 bundles/3019 historical outcomes without a new exception. This binding
supports only attempt zero Launched. Native mixed cuts, Terminal/Cleaned application,
per-attempt cleanup/reclaim evidence, effect acknowledgment and retirement remain
open. Additional OS provisioning and sibling edits remain outside this work.

Next BG-057/BG-058: qualify generated launch obligations for actual native execution
and retain their started/returned/applied dispositions before acknowledgment. A
Reserved token must never authorize replay or stand in for the worker return.
The generated dependent token has occurrence index zero, unlike the old synthetic
ISSUED[1] token at index one. Driver currently holds static issued-token references;
next work needs stable retained generated-token ownership and exact return binding,
not conversion to the old fixture token or authorization by matching service name.
Keep exact worker/resource ownership and bounded capacity; BG-060 sustained reuse
and BG-033 recovery remain separate. No kernel blocker was established.

### Application-owner lifetime follow-on

The decision 0170 application owner is local to `check_native_application`: its
Reserved effect remains inspectable through application/replay checks, and the
owner's scope ends before the outer fixture disposal. This is the end of that
bounded probe, not effect retirement or permission to recreate an owner and replay.
Before executing generated obligations, keep the same application/journal owner
alive across execution, return capture, acknowledgment and any explicit retirement.
The next witness must inspect the retained obligation across those boundaries;
it must not copy a token out, drop its owner and substitute the synthetic ISSUED
entry. This lifetime extension is local BG-057/BG-058 work, not a kernel blocker.

## Generated launch execution — decision 0171

Decision 0171 executes the exact generated dependent-launch obligation on Aether.
The original Application and History stay alive in the outer probe across policy
application, generated invocation, native return, acknowledgment and fixture disposal.
An owner-bound 96-byte EffectKey carries the complete retained occurrence identity;
the invocation boundary independently verifies original owner, exact token and
Started disposition before native I/O. It does not substitute ISSUED[1]. Native
grants and slot/generation checks remain separate from journal identity.

The generated record (compile-time bounded to 192 bytes) retains channel/launch
phases, reader/writer/worker and exact native error. Successful return transfers the
writer, retains the real worker and validates target 0xb0000102 before Applied.
The journal progresses Reserved -> Started -> Returned -> Applied -> Executed;
only Applied acknowledges, and repeated start/ack/perform calls deny without I/O.
The token and Executed disposition remain inspectable after fixture disposal.
Credits remain occupied; acknowledgment is not effect retirement or history reuse.

The positive finishes 100/3 using the actual provider and generated dependent plus
one ordinary fixture worker. Token substitution and early acknowledgment reject at
1083/0 and 1084/0. Retaining the transferred writer rejects at 1085/0 after verifying
Unknown closure and retained handles. An occupied, unreclaimed worker slot produces
the real launch error operation 0x23001/errno 16 at 1086/0, retaining reader, writer
and error without a worker or retry. Assertion 1087 detects broken failure retention.
The initial busy fixture instead reached channel creation; its failed run and a
diagnostic reporting operation 0x24000 are retained. Waiting for the occupant's
terminal return before closing its reader frees the channel while preserving the
busy slot. The five-case restricted rerun and full run then pass distinctly.

All 203 fresh Aether cases pass. All 198 prior images/outcomes and 151 ABI-6 rebuilds
remain byte-identical. The five new images are 7944/4968/7944/6744/8072 bytes; the
suite maximum is 8152/8192. All ten local gates pass in `run-hgsvbhzx`, including
287 model tests and ten Rust groups with fifteen core tests and nine omission
controls. The same core compiles for x86_64-unknown-none, preserving 1976-byte
storage and 1992-byte Application. No heap, new unsafe site, syscall or image/stack
limit relaxation is introduced. These remain bounded experiments, not a production
resource or readiness claim. Evidence: `docs/evidence/generated-launch-execution-2026-09-07/`.

Producer/worker/release pins remain unchanged. The catalog stays at 50 bundles and
3019 historical outcomes pending BG-056 complete producer source closure; no new
exception is introduced. Symbolic epoch/revision remain fixed fixture context.
Native Terminal/Cleaned application, general effect rejection policy, explicit
retirement, sustained reuse and recovery are not implemented by this step. No
additional OS provisioning or sibling edits were made.

Next BG-057/BG-058: retain the acknowledged generated-launch return as an original
per-attempt source before explicit effect-pool retirement, then qualify the
dependent Launched policy observation. The current twenty-credit hold deliberately
blocks another cut even after acknowledgment. Freeing it requires a retained exact
Executed occurrence and native resource/return association, not merely an empty
adapter or copied token. Keep the same owner across those transitions; do not
clear the effect pool or recreate Application as a workaround. BG-060 sustained
reuse and BG-033 recovery remain separate. No kernel blocker was established.

## Acknowledged launch retirement — decision 0172

Decision 0172 retains the acknowledged generated launch before explicit effect
retirement, then applies the dependent's Launched observation on Aether. The same
Application, History and GeneratedLaunch remain alive through the two cuts and
fixture disposal. Private retained metadata binds the original owner, complete
occurrence token and originating cut serial; it grants no native authority.
Native qualification separately checks original context, Applied channel/launch,
reader/worker retention, transferred writer, error absence and full target.

Retirement requires the current Applied cut, exact original receipt/effect key,
Executed disposition, unused remaining effect slots and empty output storage.
It writes retained metadata before clearing the occupied slot and freeing twenty
credits. Missing retained output closes while keeping the original Executed
occurrence and occupied capacity. Foreign, stale, repeated, unacknowledged and
occupied-tail denials preserve storage. Historical effect count and retirement
status use existing record padding: storage remains 1976 bytes, Application 1992.

The second cut has fresh serial/journal two, applies [1,0] -> [1,1] and generates
zero effects. The prior single-cut policy assumption is fixed so Launched does
not issue the dependent launch again. The first cut retains its original count
one, before/after state and membership. Empty-cut retirement explicitly verifies
zero occupied effects before releasing the second cut's credits; neither cut is
evicted and serials are not reset. Host tests also verify historical replay,
foreign owners, every token field, nonempty retention output and stale-key denial.

All 208 fresh Aether cases pass: the new positive finishes 100/3; controls omit
retention (1088/0), bypass acknowledgment (1089/0), forget historical effect count
(1090/0), or bypass native source qualification (1091/0). Assertion 1092 checks
failure retention and dependent postconditions. All 203 earlier semantic outcomes
pass again; 194/203 prior images and all 151 ABI-6 rebuilds are byte-identical.
The five new images are 8064/7968/8064/8096/7984 bytes; suite maximum 8152/8192.
All ten local gates pass in `run-ilflnaqs`, including 287 model tests and ten Rust
groups with eighteen core tests and twelve omission controls. The no_std core
also compiles for x86_64-unknown-none. No heap, unsafe site, syscall, dependency
or image/stack-limit increase is introduced.

The first two preflight sets failed the two-page linker bound. The retained map
identified formatted bounds-panic machinery from new dynamic indexed access;
checked record lookups remove that dependency without weakening denial. The third
preflight and focused five-case target run passed. Final ownership/closure review
adds same-Application retained-source validation, preserves History closure on
ambiguous dependent application, and retains occurrence checks through disposal.
The fourth preflight and full target run cover those final bytes. Native stack
assembly is retained; the root frame remains 3176 bytes, with the unchanged
528-byte Adapter launch frame and bounded intervening calls on the 4 KiB stack.
The target witness qualifies this concrete composition, not arbitrary call depth.

Evidence: `docs/evidence/acknowledged-launch-retirement-2026-09-07/`.
Producer/worker/release pins and catalog bytes remain unchanged. The catalog still
records 50 bundles/3019 historical outcomes pending BG-056 complete producer source
closure; no exception is extended. This is process-local retention, not storage
durability, Terminal/Cleaned application, general multi-effect retirement,
sustained reuse or recovery. Independent reviewer sign-off is not claimed.

Next BG-057/BG-058: qualify retained provider/dependent terminal observations for
native policy application under the same owner, retaining partial/error evidence
before cleanup. BG-060 owns sustained history capacity/reuse and BG-033 recovery.
No kernel blocker is established; other-platform provisioning remains deferred.

## Terminal application core — decision 0173

Decision 0173 adds the fixed Rust Terminal application primitive. After both
Launched observations, one member can advance from phase 1 to phase 2 while the
peer and historical launch cuts stay unchanged. The transaction reserves the
whole pool, records Unknown before mutation, and captures exactly one complete
reclaim occurrence before publishing Applied. Its local token uses kind 8 for
reclaim, existing activation cause 7 and operation 1. Source facts, terminal kind,
readiness, native grants and actual reclaim remain outside this pure primitive.

Exact replay returns the retained cut and cannot issue another reclaim. Early,
foreign, cancelled, wrong-phase and mixed-member requests deny without mutation;
application revalidates policy. Unexpected pool entries or failed transition/
capture verification preserve actual phase/effects, retain Unknown and close.
Both terminal orders are exercised, including explicit acknowledged retirement
between cuts and preservation of the original launch records. Four omission
controls detect skipped transition, dropped/corrupted capture and reopened Unknown.
No Cleaned, retry, general multi-member Terminal cut or sustained reuse is added.
Storage remains 1976 bytes and Application 1992 bytes, without allocation or new
unsafe code. Phase-specific reservation shares the same bounded implementation.

All ten local gates pass in `run-w7c_s_i7`: 287 model tests, ten Rust groups with
22 core tests and 16 omission controls. The core also compiles for the native
no_std target. All 208 existing ABI-15 clients rebuild within their unchanged
8192-byte limit (maximum 8152). 190 images match decision 0172 byte-for-byte;
18 changed images were freshly consumed on Aether and preserve their exact prior
outcomes. All 151 ABI-6 images rebuild identically within 4096 bytes. The retained
comparison names every client and the restricted native runner executes exactly
the 18 changed images. This is not a new 208-case execution campaign. No failed
builds, tests or native attempts occurred in this step.

The new Terminal methods are not invoked by native clients. Representative
bound-reservation and dependent-launch assembly is retained and contains neither
Terminal entry point. Therefore this evidence demonstrates host core behavior and
compatibility of existing native paths, not native Terminal application. Full
sealed-Sample/fact/worker/occurrence qualification and consuming execution are the
next BG-058 gate; no caller-created terminal phase is accepted as native evidence.

Evidence: `docs/evidence/terminal-application-core-2026-09-07/`.
Producer/worker/release pins and the 50-bundle/3019-outcome catalog are unchanged.
BG-056 producer source closure is still pending; no existing exception is extended.
The core is process-local, with no durability, recovery or independent review claim.
Other-platform provisioning remains deferred and no sibling repository was edited.

Next BG-057/BG-058: bind this Terminal primitive to sealed original provider and
generated-dependent samples under the original owners, preserving partial returns
and errors before cleanup. A fresh target witness must cover that binding and its
reclaim capture. Actual reclaim/Cleaned application, BG-060 sustained retention and
BG-033 recovery remain later work. No kernel blocker is established.

## Native Terminal capacity boundary — decision 0174

Decision 0174 attempted the native generated-dependent Terminal binding and
found a concrete image-capacity blocker. The refined candidate retains the source
association in an exclusive session before capturing actual register returns.
Its linker-computed text/constant/GOT section is 11,680 bytes against the unchanged
8,192-byte bound; size-z and fat-LTO alternatives still exceed the bound. Across
two candidate snapshots, all 48 bounded links reject as expected. Assembly output
is build-only; no candidate was executed and no native Terminal claim is made.

A read-only check of current Aether confirms AENIN002/ABI 15 still has the same
8 KiB code and 4 KiB stack contract. The candidate root frame is 3,288 bytes before
caller/saved-register/nested frames, so stack compatibility also needs an actual
consumer witness. A larger native-C mapping is not an accepted init replacement.
This is a profile limit for this composition, not proof that every design needs
more memory or that the kernel is defective.

The candidate code was removed from maintained native files after retaining both
source snapshots, commands, diagnostics, maps and assembly. All thirteen maintained
native inputs match the previously qualified decision 0173 snapshot byte-for-byte.
No new native behavior, compiler option, image/stack limit, producer pin, shared
release pin, catalog entry or sibling repository change is adopted.

Native Terminal integration is blocked pending an Aether capacity/profile decision
or a reviewed architecture alternative. BG-061 captures local qualification and
`docs/INIT-CAPACITY-HANDOFF.md` gives the producer/consumer requirements. The handoff
has not been added to the sibling backlog. BG-057/BG-058 remain active; their native
integration step is paused at this boundary. Actual reclaim/Cleaned, sustained
retention and recovery remain separate. Independent review is not claimed.

## Composed Terminal consumption — decision 0175

Decision 0175 independently accepts AENIN003/ABI 16 for the bounded native
Terminal experiment. The producer packet matches its manifest; all 499 source
files match the archived map. A consumer-owned intake receipt preserves the
original producer source/report/envelope bytes and provenance. No sibling file,
shared release pin, old envelope or old evidence was changed.

All 214 sys-init cases pass in fresh Aether QEMU execution from captured sources,
including the generated-dependent Terminal positive (100/reclaimed 3) and five
controls (1094–1098/reclaimed 0). An independent source-extracted replay also
passes all 32 producer composed-profile boundary cases using pinned SDK libc.
Those cases cover page/length boundaries, malformed inputs, code-write and
stack-execute denial, stack guards, dirty-tail rejection and owner cleanup.
This replay rebuilds helpers and kernel, not libc. The 453 upstream cases remain
producer evidence; they are not counted as our executions.

The Terminal session binds the original owner, generated worker and retained
launch acknowledgment before observe/status/observe. Its exclusive borrows keep
the association stable through sampling/application. Actual raw returns are
retained before interpretation. Wrong-owner and premature application deny;
missing/corrupt reclaim capture retains Unknown and closes admission. Local
interruption preserves the two completed reads and prevents further capture or
application. Exact repeat application cannot issue another effect.

The positive image is 11,680 bytes within the explicit 16,384-byte limit. All six
new paths execute with the unchanged 4 KiB stack and no guest fault. This is
bounded path evidence, not a stack high-water measurement or future headroom
claim. The primitive adds no allocation or unsafe site. All 208 ABI-15 and 151
ABI-6 clients rebuild byte-identically to their qualified baseline; no new legacy
target campaign is claimed. All ten development gates pass in run-aoks0khj.

The emitted full reclaim occurrence remains Reserved. Fixture disposal is not
execution/acknowledgment of that occurrence and does not apply Cleaned. Next is
exact issued-reclaim execution and acknowledgment, then Cleaned handling under
BG-057/BG-058. Provider Terminal, general mixed cuts, generated-source errno
variants, sustained retention (BG-060), recovery (BG-033), new-profile catalog
support and independent review remain open. No production POSIX, physical-target,
performance or release-readiness claim follows. There is no current kernel blocker.

## Issued reclaim and Cleaned — decision 0176

Decision 0176 executes the exact generated-dependent reclaim occurrence,
acknowledges it, and applies Cleaned. The driver checks the original source and
full Started token, records actual reader-close and worker-reclaim tuples before
interpretation, and clears each reference only after its own zero success.
Returned/Applied/Executed cannot precede the actual work. Repeated execution and
acknowledgment deny. Partial errors preserve Unknown, actual returns and remaining
references; History admission closes. Closed-reader EACCES (-13) and stale-worker
EBADF (-9) are observed kernel outcomes, not manufactured errno.

Cleaned requires the exact acknowledged reclaim, its original-owner retirement
metadata, a retained Terminal cut and no generated resource references. It moves
the dependent from phase 2 to 3, preserves the original Terminal history, emits
no effect and replays without mutation. Invalid resources/sources deny before
application. Unexpected transition or pool contents retain Unknown and close.
Raw reclaim tuples remain local through acknowledgment; this is not persistent
recovery or extended raw-return retention.

Ten new cases pass in fresh Aether execution: reclaim and Cleaned positives both
return 100/reclaimed 3; token/early-ack/reader/worker/error controls return exact
1100–1105 contexts, and Cleaned controls return 1108/1109 after one reclaim.
All 214 prior ABI-16, 208 ABI-15 and 151 ABI-6 images rebuild byte-identically.
Those 573 comparisons reuse earlier target evidence; this is not a new 224-case
execution campaign. The maintained composed suite now selects 224 cases with
the pinned service worker. All ten local gates pass in run-gsx2lahk; the Rust
core passes 25 tests and 17 omission controls across ten top-level Rust groups.

Default Cleaned linking rejects at 18,616 bytes. Only its three probes add fat LTO
and one codegen unit; positive is 14,728 bytes. Reclaim stays size-s (positive
13,912 bytes). Code stays bounded at 16,384 bytes and stack at 4096. All ten final
paths execute without guest faults; this is not a stack high-water/headroom or
performance claim. Storage/Application remain 1976/1992 bytes, with no allocation
or added unsafe site. Shared release, producer, worker and old profile pins stay
fixed; sibling repositories and historical evidence are unchanged.

Retained failures include the first nested fixture-launch stack fault, the stale
reader's incorrect EBADF oracle, a nested stale-worker fixture stack fault, the
three default-profile Cleaned link rejections, and the stale 22-test local oracle
after adding three passing core tests. Fixture preparation/reuse now runs in the
caller, the errno expectation matches the enforcing kernel, and the required
core count is 25. No failed attempt is counted as acceptance.

The provider is still disposed by fixture cleanup; it has not traversed policy
Terminal/Cleaned after dependent Cleaned. Next BG-057/BG-058: complete that
two-service teardown and preserve both histories. Then address fixed storage
retirement/reuse under BG-060. Recovery (BG-033), independent review and new-profile
catalog audit support (BG-056) remain separate. No current kernel blocker.

## Complete pair teardown — decision 0177

Decision 0177 completes provider Terminal, exact reclaim/acknowledgment and
Cleaned after the already-qualified dependent teardown. Both services reach
Cleaned under the original application owner. Provider observations are tied to
the original issued launch record and Launched receipt, captured into its unused
primary sample before interpretation. Foreign owner, unsealed source and local
interruption deny; interruption retains two actual returns and closes History.
The generic close/reclaim executor checks the exact Started key before calls and
retains actual returns through acknowledgment for either service.

A Terminal member may now have a Cleaned peer; the selected member must still
be Launched. Empty dependent-Cleaned retirement releases its effect-pool credits
without erasing the cut. Provider Terminal/Cleaned occupy cuts 5 and 6. Native
checks verify stage receipts and both complete primary samples; the 26-test
core suite explicitly compares all six preserved records. A rollback to the old
peer guard fails the new test as expected. There is no record reset or eviction.

Four new Aether cases pass: full teardown gives 100/reclaimed 3; owner, seal and
interruption controls give 1111/1112/1113 after one reclaim. Both policy-owned
workers are reclaimed before the adapter-empty check. A separate ordinary reuse
probe supplies the kernel fixture's required third reclaim, preserving its PASS
contract; it does not replace either policy teardown or create a seventh cut.

All 224 prior ABI-16 images rebuild: 208 are identical and 16 changed probes are
freshly reexecuted with their exact prior outcomes. All 208 ABI-15 and 151 ABI-6
images remain identical. This is 20 fresh native executions plus 567 unchanged
images, not a fresh 228-case campaign. The maintained composed case catalog now
contains 228 cases with the pinned worker. All ten local gates pass in run-ej7zipxo;
26 core tests, 17 existing core controls and the extra rollback control pass.

All four new probes use the existing explicit fat-LTO/one-codegen-unit profile.
The positive is 16,360 bytes, only 24 bytes below the unchanged 16 KiB bound.
All new/changed paths execute without guest faults on the unchanged 4 KiB stack.
No future code/stack headroom or performance claim follows. 8 earlier bounded
links reject and remain retained; no failed native attempt occurred in this step.
The complete-pair fixture omits repeated dependent-only negative/replay exercises
that remain in separately reexecuted cases. Actual enforcement remains intact.
No allocation, unsafe site, shared release pin, producer/worker pin or sibling
repository change is introduced. The old evidence catalog remains unchanged.

Next BG-060: research bounded history retention and fresh-attempt admission after
a complete cycle. The six-record store cannot sustain restarts, even after its
empty credits are retired. Native final-Cleaned credits remain retained; the core
test additionally retires them and still verifies record exhaustion. Preserve
unknown outcomes and stale-receipt denial; do not introduce a reset as a shortcut.
BG-057/BG-058 remain active for sustained integration; BG-033 recovery, BG-056
new-profile catalog support and independent review remain separate. No current
kernel blocker is established.
