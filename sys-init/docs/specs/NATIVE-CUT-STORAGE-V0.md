# Native cut storage and reservation v0

Decision 0166, BG-057. Implementation contract and layout study, not an executable
journal, accepted native cut, shared ABI or production memory budget. Refines
[Native cut acceptance](NATIVE-CUT-ACCEPTANCE-V0.md) and the qualified decision 0165
launch/history path. The following is the first native implementation slice.

## Storage and authority

One private coordinator owns the existing History and one effect pool. Keep the
original external Context borrow so moving internal records does not mint a new
owner. No caller may install nonempty records or replace Context. Do not store
self-referential Rust pointers into movable History: cut members use checked
attempt/phase indices into coordinator-owned retained source associations.
Indices select records; they confer no worker authority. Native Driver ownership,
full issued token, actual worker/target, profile and source sample are revalidated.
No public receipt constructor or externally supplied successful phase is allowed.

Retain six cut records for two attempts and three phases each. A record stores its
observation serial, associated effect-journal serial, one/two ordered member keys,
before/after phase vectors and state. Retain twenty effect entries in a single
pool, not twenty entries per historical cut. Every effect has the complete ten-
field occurrence token and a separate disposition. Symbolic token fields stay
bound to the immutable native fixture context; hashes cannot replace equality.

The proposed layout uses explicit integer tags with checked conversion; zeroed
unused storage is not a valid reservation or acknowledgment. Only occupied members
and effects are interpreted, after count/index/tag checks. Unused bytes do not
supply observed native facts. Raw Sample history, resource handles, producer/profile
binding, lifecycle state and invocation receipts remain separately owned; they are
excluded from this layout's size measurement.

Retained cut records summarize observation application; they do not preserve all
old effect dispositions. The first implementation must deny a new reservation
while any effect slot is occupied, even when its disposition is executed or
rejected. No implicit effect-history eviction is introduced. A later explicit
retirement contract must move any required disposition into per-attempt retained
records before making the pool available again. This intentionally narrower first
slice can apply one effect-producing cut and then reach Full. It is not the full
Python journal's history policy or a liveness claim.

## Reservation operations and forbidden outcomes

- Validate owner, open state, member count/order, source association and expected
  phases before reserving either record or pool. Unsupported phases/profiles deny.
- Check a free cut record, empty effect pool, no active cut, and both nonzero u64
  serials before mutation. Exhaustion returns Full without wrapping or consuming
  a source. Reserve all twenty credits and one record in the same exclusive borrow.
- Record Reserved before returning the private reservation key. A key is looked up
  only within its issuing coordinator, with full retained membership equality.
  Matching integer serials from another owner do not authorize access.
- Repeating an identical Reserved request returns the existing key; it consumes no
  record or serial. A different request while reserved returns Busy.
- Cancel only the exact Reserved key; retain Cancelled membership and consumed
  observation/journal serials. Release unused pool credits, never erase history.
  Re-reserving the same observations receives new serials and a new record.
- Mark Applying before lifecycle mutation. Record each resulting full effect token
  before Applied. If capacity or postconditions fail after mutation, retain Unknown
  and all captured effects, close, and prohibit blind replay. Do not return a dummy
  Applied receipt from this reservation-only slice.

Initial public-to-parent methods should expose reservation/cancellation/inspection
only. Application and acknowledgment remain unavailable until their matching
native lifecycle and issued-return integration are implemented. An enum named
Applied in the layout is not an operation granting that state.

## Acceptance and follow-ons

BG-057 first implements this fixed reservation owner as private Rust logic with
explicitly synthetic source fixtures. Test empty state, canonical two-member
reservation, duplicate identity, Busy, wrong owner/key/member, phase/tag bounds,
six cancelled records, u64 exhaustion and cancellation replay. Source omission
controls must detect serial reuse, partial reservation and forgotten history.
Require native-target compilation and measured layout; host tests alone do not
establish native provenance, invocation, stack use or QEMU behavior.

Then integrate native Driver/History source selection and consume a fresh Aether
witness before accepting runtime behavior. Subsequent BG-057 changes add lifecycle
application and complete effect capture, retained disposition/credit retirement,
and exact receipt publication. BG-058 retains received reclaim and per-attempt
cleanup. BG-060 owns sustained history reuse; BG-033 owns unknown/replacement-owner
recovery. This slice adds no reset and does not resolve those follow-ons.

The layout study uses explicit repr(C) storage solely to make its size/alignment
inspectable. It is not a serialized format or FFI contract. The 8192-byte native
image limit remains independent of storage size; combined stack, code and total
fixture layout must be measured when linked. No POSIX dependency or kernel API is
added. Shared standards and release pins remain unchanged.

## Layout measurement — decision 0166

Installed Rust 1.98.0 reports Member 2 bytes, CutRecord 32 bytes, Effect 88 bytes,
and Storage 1976 bytes aligned to 8. Identical size/alignment assertions compile
for x86_64-unknown-none. These values include six cut records and twenty full-token
effects, plus the proposed counters; they exclude History, Driver, source metadata,
lifecycle state, call records, stacks and code. They establish representation size
only, not a total supervisor memory bound or performance result. Inputs and exact
commands are retained under docs/evidence/native-cut-storage-2026-09-07/.

## Reservation implementation — decision 0167

The private cut_reservation module implements only empty-lifecycle Launched index
reservation, exact-key inspection and cancellation. It is not imported by the
native supervisor entry point. Owner anchors are nonzero-sized, non-Clone values;
an exclusive constructor borrow and lifetime-bound keys preserve identity without
self-referential pointers. The same serial under a different anchor denies.

Six retained records and twenty reserved credits use the measured 1976-byte Storage;
the owner reference makes Reservations 1984 bytes on the tested host/target layouts.
No heap allocation or effect insertion/application/acknowledgment method exists.
The u64::MAX next value conservatively returns Full; serials never wrap. Tests
inject exhausted, closed and occupied state inside the module; callers cannot
import that state. Only phase 1 is accepted until lifecycle/provenance integration.
Five host Rust tests and three omission controls cover this bounded logic; the same
module compiles for x86_64-unknown-none. This is not a native reservation witness.
Next BG-057 binds selection to Driver/History and consumes a fresh Aether probe,
then implements application/effect capture and explicit effect-record retirement.

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

## Terminal core — decision 0173

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
