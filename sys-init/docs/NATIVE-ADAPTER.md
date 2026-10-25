# Bounded native adapter checkpoint

Current result: [decision 0083](decisions/0083-native-interrupted-sampling.md).

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

## Previous malformed-sampling checkpoint

Current result: [decision 0082](decisions/0082-native-malformed-sampling.md).

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

## Previous retained-sampling checkpoint

Current result: [decision 0081](decisions/0081-native-retained-sampling-profile.md).

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

## Earlier checkpoints (historical)

Latest build study: [decision 0080](decisions/0080-native-composition-size-study.md)
finds a retained-sampling candidate that fits 4 KiB. Native qualification and profile
adoption remain pending; the current 125-case runtime witness is unchanged.

Latest target result: [decision 0079](decisions/0079-native-raw-sample-retention.md)
passes 125 cases with actual raw capture and stale-error prefix retention.
The raw methods coexist with unchanged decoded methods. Driver integration remains
unfinished after combined probes exceeded 4 KiB; historical next-work notes below
refer to their own checkpoints.

Latest local logic: [decision 0078](decisions/0078-terminal-receipt-validator.md)
adds a host-tested raw receipt validator, not yet linked into Adapter/Driver.
The 120-case native witness remains unchanged. Actual raw capture and bound
retention are next; host malformed inputs do not qualify producer behavior.

Latest sampling result: [decision 0077](decisions/0077-native-bound-sampling.md)
passes 120 cases. Sampling identity guards, held fact and first-read stale error
retention pass with fixture-seeded admitted state. Full launch composition remains
open. Next: NT-04 partial raw receipts/error origin; earlier checkpoints below
retain their historical scope and work order.

Current terminal result: [decision 0076](decisions/0076-native-terminal-collisions.md)
passes 114 cases including optional-worker regressions. Actual numeric terminal
collisions retain distinct kinds; live/three-read terminal samples pass. Next is
NT-03 bound sampling. Partial failure/pending history and full integration remain
open; earlier checkpoint notes are historical.

Current terminal design: [decision 0075](decisions/0075-native-terminal-evidence-contract.md)
specifies kind/result qualification with retained target observation consistency.
Next is NT-01–02 actual numeric-collision evidence. This documentation adds no
native cases; the 89-case implementation witness remains unchanged.

Current absence result: [decision 0074](decisions/0074-native-synthetic-missing-return.md)
passes 89 native cases, including explicitly synthetic Started-with-no-return
closure schedules. No actual kernel reply is lost. The
[binding acceptance review](research/NATIVE-BINDING-ACCEPTANCE-REVIEW.md) records
remaining gaps; ND-02 terminal-kind contract work is next. Earlier checkpoints are
historical and do not claim full driver or recovery conformance.

Current launch receipt result: [decision 0073](decisions/0073-native-launch-receipt.md)
passes 84 native cases. Worker/reader retention and writer transfer precede
application; generation and launched-event qualification wait. Closure retains the
receipt. Next is IR-07 synthetic absence. Earlier next-work statements below are
historical; real lost-reply recovery remains open.

Current receipt result: [decision 0072](decisions/0072-native-channel-receipt.md)
passes 80 native cases. Returned channels remain owned until qualified local
application; duplicate invocation and mismatched application deny. Closure retains
the pair and phase. Next is launch receipt/writer transfer IR-05–06. Earlier
next-work statements below describe their own checkpoints.

Current design: [decision 0071](decisions/0071-native-receipt-ownership.md)
specifies bounded invocation/receipt ownership. Next is actual channel-return
retention before local application (IR-01–04). This adds no native cases and
claims no lost kernel reply or recovery; the 75-case witness below is unchanged.
Earlier next-work statements describe their own checkpoints.

Current exhaustion result: [decision 0070](decisions/0070-native-generation-exhaustion.md)
passes 75 cases. Exhausted-slot denial leaves issuance and inventory unchanged;
the same token can acquire on another slot. NB-09 invocation/receipt ownership
design is next; earlier checkpoints below are historical.

Current target result: [decision 0069](decisions/0069-native-expected-target.md)
passes 72 cases. Match reserved native targets only after retaining actual launch
resources; mismatch closes admission. Fixture generations are explicitly accounted.
NB-08 exhaustion and NB-09 lost replies are next; earlier checkpoints are historical.

Current rejection result: [decision 0068](decisions/0068-native-binding-busy-rejection.md)
passes 67 cases. The two selected busy errors release provisional slot claims
while preserving consumed identity and any acquired endpoints. NB-06 expected
target/result qualification is next; earlier checkpoints below are historical.

Current failure result: [decision 0067](decisions/0067-native-binding-failure-retention.md)
passes 63 cases. Acquired endpoints survive local binding failure; driver closure
and consumed identity persist after fixture disposal. NB-05 selected rejection is
next; no full driver/journal/recovery claim. Earlier checkpoints below are historical.

Current binding result: [decision 0066](decisions/0066-native-binding-admission.md)
passes 61 cases. Full-token admission and two local identity/reservation controls
pass; next is NB-04 retained post-acquisition failure. The predicate does not
queue events or execute a journal. Earlier implementation plans below are historical.

Next implementation contract: [decision 0065](decisions/0065-native-driver-binding-contract.md)
and [binding v0](specs/NATIVE-DRIVER-BINDING-V0.md), with NB-01–09 future acceptance
cases. No native implementation or additional target pass is claimed.

Integration review: [decision 0064](decisions/0064-native-driver-integration-review.md)
prioritizes issued identity/admission, exact terminal kind, then journal acceptance
and retirement. [The crosswalk](research/NATIVE-DRIVER-INTEGRATION-REVIEW.md)
distinguishes current native witnesses from model-only behavior and absent
integration. Historical "next" statements below describe their own checkpoints;
current work order is decision 0064. This review adds no native cases.

Latest partial-cleanup result: [decision 0063](decisions/0063-native-routed-partial-cleanup.md)
passes 57 cases. A wait-release error after reader/worker cleanup retains the wait,
withholds Cleaned and denies retry. BG-058/BG-057 next compare accumulated native
route coverage against the model driver; no full journal/recovery claim.

Latest routed error result: [decision 0062](decisions/0062-native-routed-stop-error.md)
passes 54 cases. Stop failure preserves exact error, cancelled intent and terminal
history; subsequent failed cleanup keeps the worker unresolved and emits no Cleaned.
Routed partial cleanup remains BG-058. Fixture disposal is not recovery.

Latest admitted cancellation result: [decision 0061](decisions/0061-native-routed-live-stop.md)
passes 51 cases. Stop preserves pending/resource ownership; observation supplies
Terminal and its transfer authorizes cleanup. Cleaned does not clear intent.
Routed stop errors remain BG-058; no POSIX signal/control-transport claim.

Latest cancellation result: [decision 0060](decisions/0060-native-routed-cancellation.md)
passes 48 cases. Cancellation preserves pending evidence and persists after
Cleaned transfer, denying retry with unused allowance. Admitted live cancellation
and routed stop errors remain BG-058; this is not external control transport.

Latest replacement result: [decision 0059](decisions/0059-native-routed-replacement.md)
passes 45 cases. Pending Cleaned denies acquisition; accepted transfer permits one
fresh generation-two route. Duplicate original retry is rejected; the fixed Attempt budget remains in place.
Routed cancellation remains BG-058; journal execution and timed restart are excluded.

Latest rejected-route result: [decision 0058](decisions/0058-native-rejected-events.md)
passes 41 cases. Received busy launch preserves its exact failure event/endpoints;
accepted failure transfer gates cleanup, and Cleaned transfer gates eligibility.
Routed replacement remains BG-058. Other errors and journal execution are excluded.

Latest routing result: [decision 0057](decisions/0057-native-pending-events.md)
passes 38 cases. A private admitted route owns pending lifecycle facts until a
one-slot inbox accepts them. Terminal supersedes launch and gates cleanup;
Cleaned delivery gates retirement eligibility. Rejected-launch routing remains
BG-058; this is not native JournalRuntime execution.

Latest release result: [decision 0056](decisions/0056-native-release-errors.md)
passes 35 cases. Reader-close failure stops cleanup with resources retained;
wait-release failure retains wait after other cleanup. Native EACCES and local
ownership denial are distinct. Effect/event routing remains BG-058.

Latest error-path result: [decision 0055](decisions/0055-native-attempt-errors.md)
passes 31 cases. Partial cleanup retains unfinished worker/wait ownership; a failed
native stop retains cancelled intent and an unresolved Attempt. Reader-close and
wait-release failures remain BG-058. This does not claim reconciliation.

Latest policy result: [decision 0054](decisions/0054-native-attempt-intent.md)
verifies native deadline/completion precedence and service-cancellation intent
separate from wait cancellation. All 27 cases pass; cancellation retains resources
through stop, terminal observation and cleanup. Stop/cleanup error policy remains open.

Latest result: [decision 0053](decisions/0053-native-attempt-wait.md) adds an
Attempt-owned wait, cancellation that retains its token and explicit cleanup
release. All 23 native cases pass, including two omission controls. Eighteen prior
binaries match; two wait-layout-affected Attempt clients were freshly validated.

Latest owned-policy result: [decision 0052](decisions/0052-native-attempt-retry.md)
routes a real busy launch through Adapter::launch into a retained Attempt record,
with cleanup before one retry. Twenty native cases pass, including two omission
controls; 17 compatibility binaries remain byte-identical.

Latest witness: [decision 0051](decisions/0051-native-acquisition-cleanup.md) passes
busy channel creation, actual kernel launch denial, retained endpoint cleanup and
wait release after reclaim, with two omission controls. All 14 older non-custom
worker binaries remain unchanged. [Evidence](evidence/native-acquisition-cleanup-2026-09-06/witness/README.md).

Current lifecycle extension: [one provider/dependent workload](NATIVE-SERVICE.md)
now passes with four policy controls and unchanged adapter binaries.

Current follow-through: [SI-04 consuming refresh](evidence/native-slot-reuse-consumer-2026-09-05/README.md)
passes the exact forward probe, reverse order and all nine adapter cases against
the corrected producer. The local sequential-reuse gate is lifted; the failure
and extraction evidence below remain historical.

2026-09-05. Implements the extraction stage of
[decision 0018](decisions/0018-native-adapter-boundary.md). The
[adapter](../prototypes/native-supervisor/adapter.rs) owns native traps, entry
validation, opaque handles, operation/errno errors, typed observations and waits,
and checked `InterruptTick` arithmetic. The
[policy fixture](../prototypes/native-supervisor/init.rs) owns readiness admission,
terminal expectations and bounded polling. This remains experimental Rust, not a
production language decision or a POSIX runtime.

The single supervisor owns all handles minted through one adapter. Counters track
outstanding workers and endpoints; the adapter retains the registered token and
target pair plus the lifetime registration count. Native operations enforce
per-handle authority, stale references and slot/channel capacity. Successful
launch consumes the writer from the supervisor's accounting; rejected launch
retains it. Successful explicit close/reclaim decrements its respective count.
Wait release validates the retained pair and clears it only after native success.
Errors retain accounting, and the fixture terminates rather than guessing cleanup.
The counters are not a kernel inventory or a security boundary against bypassing
callers. No concurrency, multiple adapter owners, automatic retry or Drop cleanup.

Reads deliberately request one byte, within the 16-byte native chunk limit, and
distinguish pending, EOF, byte and error. Historical ready and terminal detail are
separate. Clock ticks count delivered interrupts; checked arithmetic is not elapsed
time calibration. The profile's two-worker/two-channel/one-wait and 64-registration
limits remain. No native ABI, linker bound or standards pin changed.

## Target results

[Primary report](evidence/native-adapter-2026-09-05/results.json) passes nine cases
with all 166 frozen inputs unchanged. Source, producer artifacts, command logs,
raw clients, envelopes and serial logs are retained under the same bundle.

| Cases | Required result |
| --- | --- |
| Original policy | Same observation/deadline/cancellation/readiness/helper/replacement assertions; three reclaims and INIT PASS |
| Wrong deadline, late admission, skipped kernel deadline | Exact assertions 821, 822 and 821; designated panic, never timeout or generic boot failure |
| Supervisor exit and fault | Same live=1, terminal=1, queued=2, wait=1 preconditions and verified INIT CLOSED |
| Skipped cleanup zeroing | Cleanup-specific panic, never CLOSED |
| Adapter edges | Tick overflow rejection; invalid-slot launch retains endpoints for explicit cleanup; 64 registrations retire, stale release rejects and both adapter/kernel report exhaustion; stale observation rejects; three reclaims and INIT PASS |
| False cleanup | Deliberately returning clean while an endpoint is owned rejects at 831, reclaimed=0 |

The main policy is **3,952 bytes**, below the unchanged 4,096-byte immutable code
limit; the edge workload is 1,984 bytes. These are binary sizes, not performance
or production memory measurements. The first array-ledger implementation exceeded
the bound (5,232 bytes in a private size-only link); it never booted. Simplifying
accounting to counters while retaining native denial probes met the bound.
The failed initial build, passing seven-case intermediate run, and failed first
edge ordering remain under `attempts/`. Temporary links with a relaxed size
assertion were diagnostic only; accepted builds used the original linker map.

Reproduce the accepted nine-case workload from this repository:

```sh
python3 tests/native-init.py --producer docs/evidence/native-adapter-2026-09-05/producer --summary-pin 86d52e49898fcb859fcb7ffd7af46310152381590753f72e6ba690f17a14c9e4 --deps PINNED_AETHER_DEPS --work NEW_PRIVATE_DIRECTORY
```

The ordinary offline catalog includes these nine primary outcomes alongside the
previous 29. Repeated controls are recorded outcomes, not distinct features.
Failed probe/attempt bytes are protected by the manifest, but their failures are
not converted to passing cases or separately semantically audited by that catalog.
ISO hashes are recorded; ISO bytes are not retained. No Linux rerun is claimed.

[Full development validation](evidence/native-adapter-validation-2026-09-05/README.md)
passes 48 host, 34 model/three mutation controls, 30 harness and all standards
checks on macOS arm64, including the 38-outcome offline audit.

## Kernel order gate and handoff

The first edge workload exposed a kernel page fault under a new order. A
[minimal separate probe](evidence/native-adapter-2026-09-05/order-probe/source/prototypes/native-supervisor/init.rs)
removes all registered waits and performs only:

1. Launch slot 0, observe exit 17, close its reader, reclaim it.
2. Launch slot 1, observe exit 17, close its reader, reclaim it.
3. Reuse slot 0, then attempt the same cleanup and three-reclaim completion.

Both runs fail with kernel vector 14, CS=8, error=3, RIP
`ffffffff80030af0`, following the slot-0 and slot-1 terminal records. The
[failed report](evidence/native-adapter-2026-09-05/order-probe/results.json) remains
failed. The [serial log](evidence/native-adapter-2026-09-05/order-probe/cases/adapter-edges/native-serial.log)
and kernel ELF are retained. Address lookup with LLVM 21 maps RIP to `memset`;
this localizes the faulting instruction, not the exact caller.

Inference for Aether investigation: loading another slot calls `aliases(owner,
false)` across all states, including previously reclaimed state with retained page
metadata. That may make reclaimed backing read-only again before reuse. Inspect
alias restoration and mapping ownership around load/reclaim; confirm with the
reproducer before treating this as the root cause. This is a result against the
frozen ABI-6 producer, not a claim about an untested current kernel checkout.

Reproduce the failure using the retained minimal runner/source:

```sh
python3 docs/evidence/native-adapter-2026-09-05/order-probe/source/tests/native-init.py --producer docs/evidence/native-adapter-2026-09-05/producer --summary-pin 86d52e49898fcb859fcb7ffd7af46310152381590753f72e6ba690f17a14c9e4 --deps PINNED_AETHER_DEPS --work NEW_PRIVATE_DIRECTORY
```

Expected current outcome is a nonzero runner failure with the above kernel panic;
a corrected producer must instead complete three reclaims and INIT PASS. The
accepted edge workload preserves the original overlap: both initial slots are
launched before reclaiming either, then replacement follows both reclaims. That
passes but does not resolve sequential cross-slot reuse.

BG-032 owns this handoff and consuming refresh. The original pause on broader
service/dependent replacement sequences is now lifted by the consuming refresh
linked above. The extraction is accepted
within demonstrated orderings; the broader workload remains unimplemented.
Shared Foundations O/I/E adoption is unchanged; no new shared standard is needed.


## Pending-history contract — decision 0084

[Native pending history v0](specs/NATIVE-PENDING-HISTORY-V0.md) defines private
bound terminal views, duplicate no-op, identity denial, retained conflict and
fixed capacity. This is design only: native coverage remains the 143 cases of
decision 0083. Next BG-058 PH-01/02 needs host comparison checks and fresh native
consumption; BG-057 PH-07 retains journal acceptance/retirement ownership.


## Bound terminal-history views — 2026-09-06

Decision 0085 passes 151 native cases, preserving all 143 previous oracles.
Seven positives qualify private bound terminal views, duplicate replay, every token
field, owner/index, equal-generation cross-service token, actual other worker and
empty-session denial. Every terminal probe checks retained state before/after
queries and exact raw history afterward. Positives finish 100/reclaimed=3 after
known fixture cleanup; the token-omission control fails exactly at 1050/0.

All 184 frozen inputs remain unchanged; 87 of 143 prior
images match byte-for-byte. Every changed image has fresh target execution.
Maximum image is 4096 bytes under the unchanged 4 KiB limit. Eleven
size/layout preflights are retained. Shared pure predicates and split probes keep
all assertions; no compiler profile, linker bound or worker change was needed.

This implements PH-01/02 origin and replay within a borrowed sampling session.
The view cannot mutate Driver or Sample and exposes no arbitrary candidate API.
It does not implement independent-candidate equality/conflict, fixed diagnostic
storage, retention across session destruction or journal acknowledgment/retirement.
Next BG-058 PH-03/04 qualifies a separately labelled synthetic conflicting sample
while retaining both histories and closing admission; PH-05/06 capacity and sealing
and BG-057 PH-07 whole-cut retirement remain open. Full launch composition,
additional NT-04 O1 injections and BG-033 unknown-owner recovery remain open.


## Pending-history conflict core — decision 0086

The private conflict core is host-qualified for independent duplicate comparison,
first-conflict retention, local closure and denial before synthetic production.
Nine view/conflict tests and four new exact omission controls cover it. All 151
native client rebuilds are byte-identical to decision 0085; this new code has no
native call site, so no native conflict execution is claimed. Next BG-058 owns
the Driver/storage guard and fresh consuming witness. See
`docs/decisions/0086-pending-history-conflict-core.md`; PH-05–07 remain open.


## Native conflict guard build study — decision 0087

The guard prototype remains outside accepted runtime sources: all 36 new-probe
links across eight revisions exceed 4096 bytes. The smallest conflict/resource
mapped extents are 4464/4624 bytes in different revisions. No new native execution
or semantic omission result is claimed. All eleven current consumer sources were
restored to the accepted decision-0086 snapshot; the 151-case runtime checkpoint
is unchanged. BG-058 next owns bounded layout analysis and any separately scoped
profile proposal. See docs/decisions/0087-native-conflict-guard.md.


## Conflict-guard layout review — decision 0088

Decision 0088 completes the bounded 80-link guard layout study: 78 links exceed
4096 bytes and two isolated forget-reader controls link but were not executed.
No full variant fits. The best same-source variant maps conflict/resources at
4256/4528 bytes, saving 208/96 bytes over the prior separate minima. Existing
Aether ABI 8 is not init-compatible: its bootstrap authority, profile dispatch,
worker slots and completion oracles differ. Hashed research snapshots and a
concrete init-compatible capacity request are retained; no runtime or sibling
source, ABI, bound or pin changed. The accepted 151-case runtime is unchanged.

Next BG-058: obtain a producer decision and separately pinned init-compatible
fixture before adopting a larger image. Then qualify the guard with fresh native
consumption, preserve all 151 cases and add the five proposed cases. Construction
denial, closed reoffer and PH-05–07 remain open. A deeper layout redesign, if
needed instead, requires its own bounded plan. See docs/research/
NATIVE-CONFLICT-GUARD-LAYOUT.md and NATIVE-INIT-IMAGE-CAPACITY-REQUEST.md.


## Opt-in init capacity profile — decision 0090

AENIN002 / ABI 15 is an explicit opt-in via `tests/native-init.py --init-large`.
Its pinned producer retains the two worker slots and init grants/operations, with
8192 bytes of immutable supervisor code and separate LARGE PASS/CLOSED markers.
Default AENIN001 / ABI 6 retains its 4096-byte linker and original markers. The
adapter accepts exactly the compile-selected bootstrap tuple, never either ABI
interchangeably. No production memory budget, extra grant or recovery is inferred.

For the new profile, supply the normalized producer directory and summary pin
from `docs/evidence/native-init-capacity-consumer-2026-09-06/producer-pin.json`;
omit `--deps`, because the source archive pins its boot dependencies. Supply the
existing explicit service-worker receipt and a fresh private `--work` directory.
The retained invocation gives exact reproduction arguments. The offline audit
requires an explicit `native_profile` catalog entry for AENIN002, verifies its
bounded envelope and rejects mixed completion markers. Existing catalog entries
default strictly to AENIN001. See decision 0090 for final execution results.

This profile refresh selects all 151 prior semantic cases. The conflict guard
remains a separate follow-on until its positive and omission probes execute.


## Capacity consumer result — decision 0090

Decision 0090 accepts the explicit AENIN002 / ABI-15 profile for the existing
151-case sys-init workload. All 151 cases pass in a fresh independent target run
(457 commands, 421 frozen inputs unchanged). Exact old semantic assertions are
preserved; only the producer-defined LARGE PASS/CLOSED markers differ. All 151
ABI-6 images also rebuild byte-for-byte identically under the default profile.
The new profile has an 8192-byte bound; these refreshed images still use at most
4096 bytes. Second-page protection/cleanup evidence comes from the pinned producer;
this consumer run does not yet execute a larger guard image.

SI-05's profile dependency is now available and the compatibility refresh passes.
Next BG-058: integrate the retained conflict guard under the explicit large profile,
run all 151 regressions plus its five proposed cases, then qualify construction
denial and closed reoffer. Guard lifetime/physical capacity and PH-05–07 remain
open; profile acceptance does not accept that guard or close the whole SI-05
consumer handoff. No sibling source or shared standards pin changed.


## Native conflict guard result — decision 0091

Decision 0091 accepts the bounded native synthetic conflict guard under the
explicit ABI-15 profile. All 156 cases pass: the 151 prior cases plus two guard
positives and three omission controls. Guard-conflict retains exact primary and
diagnostic histories; guard-resources preserves reader, worker, pending state,
token, generation and acquisition/launch counters while admission is closed.
Both positives complete at 100/3. Primary overwrite, skipped Driver closure and
forgotten reader reject exactly at 1052/0, 1053/0 and 1054/0, respectively.

The guard exclusively borrows Driver and both sample stores, reserving diagnostic
storage before the explicitly synthetic producer. Conflict closes Driver admission
without dropping owned resources. Explicit fixture cleanup and two subsequent
ordinary generations complete successfully. This is not a second kernel-produced
observation or a general diagnostic-producer API. Largest image is 4528 bytes;
the native workload now consumes an image beyond the old 4096-byte bound. The
extension contains read-only data/GOT entries; do not infer second-page instruction
execution from size. Producer page-permission and second-page execution evidence
remain separately pinned in decision 0090.

All 151 default ABI-6 images rebuild byte-for-byte identically. No producer,
linker bound, native operation, standards pin or sibling source changed. The
SI-05 compatibility refresh and its five requested guard cases now have consumer
witnesses. Next BG-058: qualify denied guard construction returning both original
borrows unchanged, and a dedicated control proving closed reoffer cannot invoke
the synthetic producer. The current repeated call returns Closed but is not that
omission qualification. PH-05 two-primary/one-diagnostic physical capacity,
PH-06 sealing, BG-057 PH-07 retirement and BG-033 recovery remain open.


## Guard denial and reoffer result — decision 0092

Decision 0092 passes all 162 native cases: 156 prior cases and six new denial/
reoffer probes. Unsealed-primary and occupied-diagnostic construction denials
return the original Driver, primary and spare addresses with both full sample
values and the checked ownership/counter fields unchanged. The unsealed case
then reads and constructs a guard using those returned borrows. The occupied
store remains unchanged through explicit cleanup. Both complete at 100/3;
forgetting the reader rejects at 1055/0, and clearing the spare rejects at 1056/0.

A caller-owned bounded counter observes entry into the actual private synthetic
producer closure before spare acquisition. The first conflict invokes it once;
the closed reoffer returns Closed without increasing the count or changing either
history. Bypassing both Driver and Held admission checks reaches that same closure
again, even with no spare available, and rejects exactly at 1057/0. The positive
finishes at 100/3. This is fixture observability, not a metrics or public producer
API. The two snapshots used by the denial oracle are test data, not proof of the
future physical nine-triple storage limit.

All 151 ABI-6 images rebuild byte-identically. No syscall, unsafe block, heap
allocation, producer/standards pin, ABI bound or sibling source changes. Next
BG-058: PH-05 two primary histories with one reserved diagnostic store under the
shared Driver owner, then PH-06 sealing. BG-057 PH-07 retirement and BG-033 recovery
remain open. This slice does not cover every invalid constructor combination or
retention after guard destruction, and does not establish the full storage budget.


## Fixed history capacity result — decision 0093

Decision 0093 passes all 166 native cases: 162 prior cases and four capacity
probes. History owns Driver, two primary Sample stores and one diagnostic Sample.
Temporary Sampling/Pending borrows cannot outlive this owner, and dropping those
handles does not replenish storage. The diagnostic retains its attempt index;
Driver retains the original token, worker/generation and reader association.

The native positive retains a Live observation in attempt 0, then a Terminal
history in attempt 1. Live releases the global position without freeing its
history; Terminal keeps pending at 1. Resampling and index 2 deny without extra
sampling returns. A synthetic conflict occupies the one reserved diagnostic and
closes admission; another offer cannot invoke its producer. Both primaries and
resources remain intact, including the old Live history after explicit worker
stop. Cleanup and ordinary reuse finish at 100/3. Losing Live history, recycling
a primary and recycling the diagnostic reject exactly at 1058/0, 1059/0 and 1060/0.

The owner provides nine fixed triple slots; this legal scenario fills seven
(1 Live + 3 Terminal + 3 synthetic diagnostic). It does not claim two simultaneous
terminal facts. Separate x86-64 LLVM constant-return inspection measures History
at 760 bytes: Driver 336, three Samples at 136 each, plus diagnostic association.
Raw payload layout is 24 bytes. These are target type-layout measurements, not
peak stack usage or a production memory budget; transient values remain separate.

All 151 ABI-6 images rebuild byte-identically. No producer, ABI bound, shared
standard pin, syscall, heap allocation or sibling source changes. PH-05's bounded
Live/Terminal/conflict capacity slice now has native evidence. Next BG-058 PH-06:
qualify denial of Live/Failed/Interrupted promotion while retaining histories,
issuance, pending state and resource ownership in this container. BG-057 PH-07
whole-cut retirement and BG-033 recovery remain open. Full launch composition,
all failure combinations and retirement are not established by fixture seeding.


## Owned history sealing — decision 0094

Decision 0094 qualifies owned-history replay denial for Live, one/two-return
Awaiting, malformed-status Failed, and Interrupted after one/two returns. The six
positives complete at 100/3. False acceptance, erased primary and forgotten reader
controls reject exactly at 1061/0, 1062/0 and 1063/0. Repeated replay/conflict/capture
denials preserve complete samples, original binding/resources, issuance, generation,
pending/closed state and counters. No synthetic conflict producer runs. Explicit
fixture disposal preserves history and consumed issuance; it does not qualify
retirement. The malformed status slot and local interruptions are explicitly
synthetic; other retained returns come from the pinned native producer.

All 175 native cases pass (166 prior plus nine). All 151 ABI-6 images rebuild
identically. No new allocation, unsafe code, syscall, producer/worker source,
standard pin or sibling change. Next BG-058 PH-06: native errno history under this
owner, plus closed terminal inspection/replay without reset; BG-057 PH-07 whole-cut
retirement and BG-033 recovery remain separate. This slice establishes the six
listed source dispositions, not all failure combinations or production init.

The canonical [native-runner manual](man/sys-init-test-native-init.1) covers
current inputs, profile selection, workspace and error behavior. Target
acceptance still requires the matching retained producer/consumer evidence.

## Composed profile — decision 0175

`tests/native-init.py --init-composed` explicitly selects AENIN003/ABI 16,
1–16384 code bytes and the unchanged 4096-byte stack. It is mutually exclusive
with `--init-large`; default ABI 6 and ABI 15 remain separate. Expanded profiles
require archived boot dependencies and reject `--deps`. The composed input is
a sys-init-owned `sys-init-init-composed-intake-v1` normalization receipt binding
the unchanged upstream report, source archive, positive envelope and provenance.
It is not an upstream summary or a published shared standard. The source manual
records options and execution limits. New Terminal acceptance is recorded in
[decision 0175](decisions/0175-init-composed-terminal-consumer.md).

## Issued reclaim and Cleaned — decision 0176

Two adapter methods retain the complete raw close/reclaim register returns;
local counters change only on actual zero success. The trusted effect driver
qualifies the original owner/source and exact Started token before calls.
Its raw tuples remain local through effect acknowledgment; they are not durable
recovery records. The retained application acknowledgment supports Cleaned only
when the generated resource references are empty. See decision 0176 for scope
and error/stack evidence. The three Cleaned probes explicitly use fat LTO and
one codegen unit; the native runner records those options per command.

## Complete pair fixture — decision 0177

The four pair cases use the explicit LTO profile. Provider sampling is bound to
the original issued launch record, owner and Launched receipt; the generated
dependent remains associated with its own retained source. Both share the guarded
close/reclaim executor, which rechecks the Started key before native calls.
After both services reach Cleaned and the adapter is empty, the unchanged kernel
fixture's third-reclaim requirement is met by a separate ordinary reuse probe.
