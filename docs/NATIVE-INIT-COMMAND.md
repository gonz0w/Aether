# BG-067: bounded real-command integration handoff

Producer delivery, 2026-09-08. [Frozen inputs, recipe and evidence](evidence/init-command-handoff-2026-09-08/README.md).
This supplies the selected composition boundary and reference cases needed to
start sys-init's BG-067 adapter. It does not claim that sys-init's owner has been
ported, independently accepted or booted. Userland supplies the real four-role
runner and bytecount; their original frozen sources are rebuilt here.

## Selected ownership and profile

Use the existing AENMX001/ABI9 three-image profile. **Sys-init replaces the reference
supervisor**, rather than supervising an extra broker domain. Its service policy
owns admission, stop, terminal observation and reclaim. The existing command/file
protocol logic remains a separate responsibility in that supervisor address space;
this is not process isolation between those components. The worker roles and wire
contracts remain unchanged. Do not substitute the ABI16 init binary or readiness
writer: the entry registers and transferred connections differ.

| Role | Slot / executable | Owned responsibility |
| --- | --- | --- |
| Runner | 0 / 0xc001 / source-built four-role runner | Decode startup, select bytecount, request launch/collection, close its file references |
| File backend | 1 / 0xc002 / C bridge plus Rust stream service | Seed input, output buffers and open backend handles |
| Command | 2 / 0xc003 / source-built bytecount | Public libc input/output and exit; no image/channel factory authority |
| Supervisor | 3 / raw code tail | Lifecycle authority, connection allocation, file-reference routing, child admission and terminal records |

Supervisor entry: RDI=9, RSI=0xa001 launch factory, RDX=0xc001,
RCX=0xc002, R8=0xd001 channel factory, R9=0xc003. No wait-factory grant is
supplied by this profile. Code must fit 8192 bytes, with a separate 4096-byte stack.
Reference raw images and sizes are in the case receipt; the consumer must measure
its own linked code and stack. This does not extend ABI16's 16 KiB allowance to
ABI9. Three generations per worker/channel remain the existing bounds.

Envelope: 80-byte header/entropy prefix: AENMX001, three ELF byte lengths,
supervisor length, two zero u32 fields, then 48 developer entropy bytes; append
runner, backend, command and raw supervisor in that order. All ELFs are preflighted
before admission. Existing [program](NATIVE-PROGRAM.md), [connections](NATIVE-CONNECTIONS.md),
[launch](NATIVE-LAUNCH.md) and [supervision](NATIVE-SUPERVISION.md) contracts define
exact formats and errors. No new syscall or published standard is introduced.

## Startup, transfers and cleanup

Start backend slot 1 before runner slot 0. Kernel argv is `worker` for the backend
and `client` for the runner, with no environment in this fixture. For each worker,
allocate a request and reply channel: transfer the request reader and reply writer
with 0x23002 only after validating startup. The supervisor retains request writer
and reply reader. Successful transfer denies further caller use of transferred
ends; rejected startup leaves them with the caller for cleanup. Six channels
support the two services plus the command, with 32-byte queues and 16-byte chunks.

Read the backend's fixed handle greeting before publishing runner startup. Send
224-byte AERUN001 with `aether-run`, `bytecount`, `--decimal`, followed by the
160-byte AERIO001 carrier: stdout/write/512, stderr/write/256, child-input/read/6,
child-output/read-write/64. Six is the input capability's bound; the empty case
has zero data without changing that carrier. These are connection-local file
references, not kernel handles. Actual command argv comes from validated runner
forwarding: `bytecount`, `--decimal`; its legacy two-binding carrier supplies input
and output. Do not conflate either carrier with kernel argv or a readiness byte.

The supervisor owns each native connection and instance handle. Runner and command
own their admitted file-reference closures. The backend owns underlying buffers;
it is stopped only after clients are terminal, references retired and readback
complete. Observe with 0x20001; normal exit, fault and controlled stop are distinct
kinds. Reclaim with 0x20002 only after terminal state. 0x20007 is the existing
controlled stop operation; this packet qualifies the fault branch, not a new
stop-recovery policy. Close both retained channel ends and reclaim each client;
then close the backend request writer, observe EOF termination, close its reply
reader and reclaim. Preserve partial cleanup on errors; never replay an unknown
consumption or treat a terminal record as reclamation.

Sys-init's current Service/Pair adapter needs paired request/reply ownership in
place of a single readiness channel, role/image selection and backend EOF ordering.
Its cleanup method currently requires terminal observation before endpoint close;
the backend requires request EOF to terminate. The adapter must explicitly settle
that ordering, retaining per-end close progress, rather than smuggling side effects
into observation. No generic journal or extra service is required by this handoff.

## Producer acceptance and consumer work

The five source-built cases use the unchanged kernel:

- Positive: input `abcdef`, output `6\n`, child/runner/backend exit 0/0/17.
- Empty: empty input, output `0\n`, the same terminal results.
- Fault: injected #UD after command bootstrap, before bytecount; input unchanged,
  no output, command detail134/kind2, runner exit1, backend exit17. Reference owner
  retires the faulted command's file references and completes cleanup.
- Wrong role: invalid AERIO001 startup causes runner110, no command admission,
  owner1401/reclaimed0. Retained failure, not recovered cleanup.
- Omitted stdout close: child0/runner0, owner1403/reclaimed0. Retained failure
  demonstrates the close obligation; it does not qualify recovery.

Positive, empty and fault each require two generations and six reclaims. Backend
readback proves exact output, untouched input, empty runner output, EOF and stale
handle denial. Sys-init must preserve these semantics while supplying its owner,
then independently freeze and run its consuming cases. This packet opens that
adapter work; it does not close BG-067 or confer consumer sign-off.

The native watchdog (<3000 ticks), registration bounds in other profiles, sustained
idle strategy, authorized shutdown source and final action remain later acceptance.
Conformance `finish(100)` is not operator shutdown, filesystem flush or poweroff.
Dash, persistence and package release gates are unchanged.

Reproduce from this checkout with the pinned SDK/tool inputs recorded in the packet:

```sh
python3 docs/evidence/init-command-handoff-2026-09-08/run.py --libc-build /absolute/strict-sdk --tools-lock /absolute/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

Use the archived sources for matching-revision reproduction. Builds never follow
mutable sibling code; imported source hashes and the SDK/tool receipts are checked.
The retained SDK archive is `docs/evidence/init-composed-capacity-2026-09-07/sdk-inputs.tar.gz`
(SHA256 `179e9100b6a0a5ee537450cd87d5642e31c00617d545b09bc5c1679e9a997c77`).
Preserve third-party notices and the existing released standards pins.

## SI-07 sustained-profile review — 2026-09-25

Status: producer design review; no new profile, ABI, operation or runtime behavior
is enabled. The current command profile and sealed evidence above remain intact.
The [consumer requirement](../sys-init/docs/SUSTAINED-INIT-HANDOFF.md) requests
useful repeated bytecount commands, actual idle/wakeup past the old deadline and
an authorized orderly shutdown. Sys-init retains all admission/restart/shutdown
ordering policy. The first final action proposed here is halt, not poweroff or
reboot, and does not claim persistent storage flush.

### Current code findings

- `native_c.zig:nativeTick` panics at 3000 ticks in all current profiles. Tick
  accounting must be separated from a selected sustained guest's healthy lifetime;
  a host test timeout remains mandatory and must never pass as guest completion.
- `native_c.zig:threadOperation` requires the current domain's nonzero thread cap.
  The command supervisor has none. Address wake only visits contexts within that
  same domain; it cannot wake init on another domain's channel or terminal event.
- ABI6 `waitOperation` uses retained revision records but returns through `select`
  without parking. It has a 64-registration lifetime and observes one instance.
  Merely exposing its factory to ABI17 would not implement sustained blocking.
- The scheduler already has an interruptible kernel idle frame. A sustained wait
  should reuse that path, preserving saved user registers, FP state and mappings.
- Process/memory/thread handles OR generation bits into tags at bit 28. Channel
  handles put generation at bit 8 and object identity at bit 16. Raising generation
  limits without revising the selected encoding can alias identity fields. Legacy
  three-use and SESSION fifteen-use bounds avoid those collisions and must stay.
- `finish(100)` enforces fixture reclaim counts, emits a test PASS and halts. It is
  neither a shutdown request source nor an authorized final-action contract.

### Proposed enforcing contract

Use a separately selected sustained three-image profile, keeping the current three
worker slots, six channels, code/stack budgets and backing quotas. Version and grant
assignments must be frozen with the chosen input route before implementation. Do
not silently extend ABI9/17/21 or repurpose a legacy grant.

**Identity and reuse.** Use explicit disjoint type, object and generation fields
for this profile. A proposed 28-bit nonzero generation keeps four-slot numeric
PIDs within signed 32-bit range; reserve generation zero, reject creation at the
selected maximum, and retire rather than wrap. Audit consumer token encodings
separately: wider native lifetimes cannot silently widen private file-reference
fields or permit their counters to alias. Live quotas stay independent of total successful cycles. All
instance-derived memory/thread grants, copied identities and channel ends must
use the same selected profile rules. A positive integer remains only a selector:
lookup still requires the actual holder and live object. Test the last generation
by constructing host boundary state, not by billions of native iterations.

**Observe and park.** Add one owner-local retained event sequence, scoped to the
supervisor's existing instances/channels and its selected input authority. Snapshot
returns the current sequence. The supervisor drains available work, then asks to
park only if that sequence is unchanged. The enforcing boundary validates authority
and deadline, compares and parks atomically while interrupts are masked. An event
before registration returns immediately; an event after registration makes init
runnable. Relevant terminal/readiness, channel readable/writable/EOF and authorized
input changes advance the sequence. Wake is a hint to rescan, never evidence that
work completed. Ignore unrelated or foreign events. Reject sequence exhaustion
without wrapping or parking on an ambiguous identity. Keep at most one wait;
explicit cancellation must retain its outcome and may not fabricate an event.

Return monotonic tick units, with documented absolute deadlines and ordering for
an event at its deadline; no wall-clock or nanosecond multiplication promise is
needed for this workload. Healthy time does not expire at 3000 ticks. Checked clock
exhaustion must fail explicitly. Kernel idle must resume on timer/input readiness;
do not simulate waiting with a user-space yield loop. Native controls must exercise
both registration orderings, deadline completion, spurious wake/recheck and cancel.

**Shutdown.** Input authority and final-action authority are distinct. Only the
selected input holder receives request bytes; kernel code does not parse a textual
`shutdown` command or assign policy from a path/PID. Sys-init validates the request,
stops new admissions, settles the outstanding bounded backend exchange, then stops,
observes and reclaims clients before the backend. Final halt requires its separate
boot-derived grant, no admitted dependent workers, no owned/queued transport and
no pending wait. Denied authority and unsupported actions leave state unchanged;
busy cleanup returns an explicit error. Successful halt is nonreturning and has an
unambiguous diagnostic distinct from `finish(100)`. No forced cleanup, timeout-based
reuse, backend replay or new durability claim is allowed.

### Selected input: serial console

The maintainer selected the serial console on 2026-09-25. The sustained bootstrap
supervisor owns the UART grant; ordinary workers do not. Sys-init/userland own
command framing and shutdown intent. Kernel code treats bytes as opaque input,
checks receive/error readiness without consuming bytes, and uses timer-driven
readiness checks to wake the existing idle path. A separate controller domain and
extra worker/channel quota are unnecessary. Final-halt authority remains distinct
from UART authority. This selection does not enable a runtime profile by itself.

### First implementation slice: sustained state core

Implement the host-testable identity and retained park state in
`kernel/native_sustained.zig` before connecting the selected profile to native
admission. This is an implementation prerequisite, not native SI-07 acceptance.
Keep current runtime dispatch and every legacy handle byte unchanged in this slice.
The core owns no user pointer, grant table, heap allocation or policy service.

Use positive 64-bit identities: type in bits 56–62, object index in bits 32–39,
nonzero generation in bits 0–27, remaining bits zero. Distinct instance, memory,
thread, channel-read and channel-write tags prevent cross-kind aliases. Limit
creation to generation 0x0fffffff and retire at exhaustion. Enforcing integration
must still check the caller's holder authority; an encoded value is never authority
by itself. Four-slot derived PIDs remain within signed 32-bit range.

A single retained park has an expected event sequence, optional absolute tick
deadline and optional completion. Only a changed sequence or serial readiness
completes as an event; polling with neither must remain parked. Deadline wins when
observed at the same instant as an event. Cancellation completes once. Completion
must be consumed before another park, preventing a delayed result from satisfying
a later wait. Future sequence values reject; changed sequence, ready input and an
already reached deadline return immediate completion. Sequence exhaustion rejects
without mutation or wrapping. The caller serializes compare/park and event updates;
actual IF=0 enforcement and scheduler integration remain required target evidence.

Test registration before/after events, serial readiness before/during park,
spurious polls, deadline ties, cancellation/retention, sequence and identity
exhaustion, and disjoint type/object/generation encodings. Run Debug and ReleaseSafe
core tests plus the existing host suite; record exact results. No native regression
is claimed from host-only state tests. Native integration is the next action.

### Acceptance, security and simplicity

Preserve the existing real runner/bytecount/backend and original negative cases.
The sustained positive must remain idle beyond 3000 guest ticks, wake for useful
work, complete at least five fully cleaned command/channel reuse cycles, reject
old grants after reuse, and settle a real authorized shutdown. Record separately
launches, terminal observations, endpoint closure, wait outcomes and reclaims.
Add denial controls for foreign input/final-action grants, live-resource halt,
unsupported action, stale sequence/instance/channel, and omitted atomic comparison.
A timeout, panic or early PASS must reject the positive. Run host boundary tests,
selected native race/cleanup controls and matching affected legacy regressions,
then deliver a frozen packet for sys-init's independent owner replay.

The simpler alternative is exposing existing waits and increasing fixture limits.
It is insufficient: those waits have the wrong authority/wakeup scope, and the
handle fields eventually overlap. A dedicated event daemon, generic poll framework
or supervision policy in the kernel is unnecessary. Reuse the existing idle path,
channel ownership and terminal-before-reclaim checks; no legacy path can be retired
while consumed. New state is one bounded wait/sequence per selected supervisor,
not a global task table. New unsafe obligations are atomic park/publication under
IF=0 and resuming the correct saved context; no unvalidated user pointer or shared
writable event page is needed. Complexity is limited to the selected input source
and this one sustained profile. Foundations O-01–05, I-01/03–05 and E-01–08 apply;
no new exception, shared standard or independent approval is claimed.

Review checks: `python3 scripts/check_workflow.py`, `python3 docs/check-standards.py`
and `git diff --check` pass. This is a documentation-only review; no new native
execution or model test is represented as sustained-init evidence. The prior
SESSION host and native results remain scoped to their sealed inputs.

### Experimental serial wiring (not yet a handoff)

The in-progress native selector is `-Dnative-init-sustained=true`, AENSI001 with
ABI22 entry. It uses the existing 80-byte three-image envelope, 16 KiB supervisor
code, one 4 KiB stack, three workers and six channels. Bootstrap image/factory
registers match ABI17; additional fixed grants are contextual bootstrap grants:
UART 0xf001, event/clock 0xe002, final halt 0xf002. Workers cannot use them merely by
knowing their values. UART transfer is denied. Memory/thread/copy/exec experiment
flags are excluded from this first profile, so their legacy encodings cannot leak
into sustained generations. Worker launch and channel generations use the new
identity core. No older envelope selects this behavior.

Experimental operations: 0x2a000 snapshots sequence in RDX and ticks in R8;
0x2a001 compares RSI sequence and parks with RDX absolute deadline (zero means
indefinite); both require RDI=0xe002. Completion returns RAX=0 event or -110 deadline,
RDX completion sequence and R8 tick. R10/R8/R9 input fields must be zero. Snapshot
RSI/RDX must also be zero. Foreign callers/grants return -13, malformed/future
observations -22, occupied -16, exhausted sequence -28. This single-context blocking
form has no public cancel operation; core cancellation coverage is not native
cancellation acceptance. Final action 0x2a002 requires RDI=0xf002 and RSI=0 for halt;
other actions return -38. RDX/R10/R8/R9 must be zero. Close UART and fully reclaim
workers/channels first or receive -16. `finish(100)` returns -38 in this profile.
Numeric assignments remain experimental until a matched, qualified packet exists.

Native wiring must first prove actual timer idle, serial wake, grant denial and
final halt, then integrate real repeated command/service workloads and the full
legacy regressions. A zero-worker idle witness alone cannot close SI-07.

### Current SI-07 integration dependency — 2026-09-25

[Exploratory results](evidence/sustained-core-2026-09-25/README.md) demonstrate the
serial-selected kernel mechanism: 3004 idle ticks, wake on real UART input,
contextual grant denials, channel reuse beyond three lifetimes and checked halt.
The legacy five-case real-command suite still passes. These are selected checks,
not complete new-profile qualification or independent sys-init acceptance.

The real runner/bytecount/backend composition completes generations 1 and 2.
Generation 3 is admitted by the kernel, then runner startup exits 110: the frozen
userland `experiments/command-runner/four-role.c` rejects all generations except
1 and 2. `runner-result.c:ar_admission` and `native-io.c` contain the same restriction.
The current sibling copies are byte-identical to those pinned inputs. The first
exploratory run timed out after this rejection because the old fixture error path
called unsupported finish; the new profile's error path now emits a failure and
faults, and the second attempt reproduces the same generation-3 exit immediately.
Neither run is accepted as sustained success. The consumer checks remain unchanged.

Userland must provide a versioned sustained role-carrier, admission-reply and
native-I/O contract plus matched rebuilt runner/bytecount inputs and rejection
oracles. It must specify finite private reference/receipt generations and retirement:
current file references combine generation with fields at bit 16, so expanding a
comparison to the kernel's 28-bit lifetime would alias fields. Preserve existing
bounded decoders/fixtures and do not conflate private protocol epochs with native
instance identities. Sys-init then supplies its owner and accepts the composition.

After matching input delivery, finish five useful cycles and real shutdown,
worker/foreign authority and race controls, fresh source-built inputs, and matching
legacy regression/evidence before presenting SI-07 as a producer handoff. The current
experimental profile is not merge/release qualification. No sibling edits or
relaxed consumer assertions were used to bypass this dependency.

Exploratory commands (prepared images and original prerequisites are recorded in
that packet): `python3 docs/evidence/sustained-core-2026-09-25/run-probe.py`,
`python3 docs/evidence/sustained-core-2026-09-25/run-final-probe.py`, and
`python3 docs/evidence/sustained-core-2026-09-25/run-command.py`. Use a new
`PROBE_ATTEMPT` value for each execution; do not overwrite existing run receipts.
The command probe is expected to expose the recorded consumer rejection until
new inputs arrive. It is not a passing smoke command.


Serial readiness correction: polling the line-status register must retain its
read-cleared error bits until the actual reader reports EIO. The selected profile
now latches those bits across receive and transmit readiness polls; it never
consumes receive data merely to test readiness. Non-monitoring legacy mode remains
unchanged. Six state-core tests include this case; native UART error injection is
still an open test, not implied by the ordinary byte-wakeup probe. Hardware basis:
[TI TL16C550C, section 7.7.8](https://www.ti.com/lit/ds/symlink/tl16c550c.pdf).


### SI-07 authority and wake checks — 2026-09-29

The [new mechanism packet](evidence/sustained-controls-2026-09-29/README.md)
extends the existing Rust probe with an unprivileged, scalar-only worker.
It deliberately supplies known event/halt/UART/factory numbers and requires
EACCES from the enforcing kernel context checks. Six real task lifetimes check
terminal-event wake, exact disjoint identities, confirmed reclaim and stale denial.
Owner probes cover malformed reserved inputs without sequence mutation, a real
channel publication between snapshot and park, readiness of an unread serial byte
across two registrations, and a deadline after consuming that byte. No kernel
implementation, ABI, grant or quota is changed.

```sh
python3 docs/evidence/sustained-controls-2026-09-29/run.py <fresh-positive-id>
python3 docs/evidence/sustained-controls-2026-09-29/run.py <fresh-negative-id> --wrong-expectation
```

The negative worker falsely expects authority; its exact exit77 must be observed,
reclaimed and rejected by the owner. Timeout, early loader panic and any other
worker result cannot pass. Native inputs, code and sources are preserved per
attempt. STATE records measured results; this is not a substitute for the blocked
versioned runner/bytecount contract or independent sys-init consumption.


### SI-07 v2 enforcing-owner reconciliation — 2026-09-29

[Aether's protocol review](evidence/si07-v2-review-2026-09-29/REVIEW.md) finds the
AERIO002/NIO2/0x7b proposal compatible with experimental AENSI001/ABI22, conditional
on full-width native cohort equality and16-bit pre-effect exhaustion. No new kernel
operation, grant or capacity increase is needed. Host arithmetic checks all65535
private epochs/seven namespaces and144 full-width divergence cases; Debug and
ReleaseSafe state-core checks pass. This supplies Aether's design disposition only.
Runtime adoption, sys-init approval and full native qualification remain open.

The review identifies each carrier, child-bootstrap, receipt and cohort hook in the
current Rust owner. Keep existing AERIO001 inputs/owner behavior unchanged until
userland supplies the complete opt-in bootstrap/transport and rebuilt runner plus
bytecount. The current consumer generation casts must become full-width validation
before narrowing. Pure host decoder patches omit this transport closure and cannot
unblock actual five-cycle commands. On delivery, freeze exact manifests, implement
those owner hooks, qualify actual useful cycles/exhaustion/authority/cleanup and
matching legacy regressions, then hand off to sys-init for independent consumption.


### Matched SI-07 v2 command checkpoint — 2026-10-03

The [native integration packet](evidence/si07-native-2026-10-03/README.md) consumes
userland's sealed NATIVE_SUSTAINED_V2 runner/bytecount and supplies matching Rust
owner hooks. Select `--cfg init_sustained_v2` together with the existing
`init_sustained`, `command_runner`, `runner_success` and `runner_startup` recipe.
Kernel selection stays `-Dnative-init-sustained=true`, AENSI001/ABI22. This private
compile closure is not a new public bootstrap API or sys-init policy implementation.

The carrier is AERIO002; child offset28 is NIO2; admission/collection use0x7b epochs.
The owner checks successful full64-bit instance identities for backend slot1,
runner slot0 and child slot2 against the epoch before publishing each peer binding
or receipt. Mismatch stops every currently owned peer, observes stopped143/kind3,
closes endpoints, reclaims and confirms the stale instance rejects. Epochs outside
1..65535 reject before worker admission. Legacy cfg defaults retain their carrier,
zero child discriminator and0x73 receipts. No kernel grants, limits or ABI change.

The final fresh-backend positive observes3044 total/3004 idle ticks, five actual
commands through generation5, exact6-newline output checked by the owner,0/0/17
terminal statuses,15 reclaims and authorized serial halt. Cohort divergence and
65536 pre-effect rejection pass exact native markers. Five legacy command cases
pass with frozen legacy application sources. Final raw/ELF owner pairs bind scoped
stack inspection at3816/4088 maximum and9344/16384 maximum code. Formatting-only
rebuilds match all three native-tested raw owner images exactly.

Isolated frozen test cohorts seed worker generations before first admission and
complete real commands at255,256,65534,65535. The final cohort rejects65536 before
another admission and halts with three reclaims. Production initial generations
remain unchanged; this is not65535 sequential executions or a reset operation.
Both parent-carrier mismatch directions use a private observer to prove exit110,
no child admission or backend stdout/stderr effect, two reclaims and halt. That
observer does not implement general service recovery. Across all nine final owner
images, code/estimated stack maxima are10000/16384 and3832/4088. Nine trace comparisons
and66 intentional corruptions pass; inspection remains a contributor model with
manually reviewed immutable memory-builtin targets, not formal all-path assurance.

This closes the missing generation3 composition input and supplies a sealed replay
checkpoint. The next gate is independent userland technical replay and sys-init's
actual consuming owner, including its explicit outstanding-request interruption/
partial-reply policy. Full SI-07/SUSTAIN-01–06 acceptance remains open. Native
child-bootstrap mismatch, remaining malformed/stale/foreign schedules and partial/
poisoned-close cleanup are not filled by host decoder sweeps or parent mismatch
observers. Sources, all failed attempts, payload identities, recipes, archive readback
and local checks are retained in the packet. No SDK publication, reader approval
or R1 readiness follows. The candidate packet is prepared locally; no sibling
repository or chat has been modified or messaged.

### SI-07 companion intake — 2026-10-03

The [local review](evidence/si07-handoff-review-2026-10-03/README.md) verifies six
companion snapshots, all343 sys-init loop source members,35 unchanged kernel files
and both complete userland retained archives. A fresh offline Rust rebuild matches
sys-init’s normal raw/ELF loop owners exactly. Twenty retained traces and fourteen
local oracle mutations pass; these are companion native executions, not additional
Aether QEMU runs. All original producer evidence remains unchanged.

Nine original producer and seven request-loop cases now have independent userland
replay. Sys-init owns the loop: request precedes resource acquisition; halt is valid
before work and after fully settled cycles, including six commands/18 reclaims and
buffered rh. Partial replies accumulate only to completion; reply loss and close/
reclaim errors retain Unknown and deny replay, ending in explicit fixture failure.
Those controls establish fail-closed behavior, not recovered cleanup or general
mid-effect cancellation. Developer-console authority is not authenticated operator
access. No kernel ABI, grant, quota, pin or runtime source changes.

Missing-input/fixed-five blockers are resolved. Next kernel qualification is native
child-bootstrap profile mismatch and remaining malformed/stale/foreign schedules,
then wait-transition/useful-session integration with the actual sys-init owner.
Full SUSTAIN-01–06/SI-07, reader/SDK disposition and assembled R1 remain open. The
request-loop consumer final seal arrived after initial discovery and verifies at
intake; its archived work and exact local snapshot retain their declared scope.

### Native child-bootstrap profile controls — 2026-10-03

The [child-profile packet](evidence/si07-child-profile-2026-10-03/README.md) qualifies
both native child mismatch directions, keeping the parent/owner matched. Bytecount
exits120 before child I/O; the private observer verifies empty child stream, zero
I/O progress and unchanged backend output, then stops/observes runner143/kind3,
closes/reclaims owned clients, observes backend17/reclaim and stale denial, and
halts with exactly three reclaims. Runner stop and backend bytes remain owner
assertions, not separately emitted UART observations. Matched v1/v2 controls both
complete one exact6-newline command with0/0/17 and three reclaims. All four use the
unchanged ABI22 kernel and retain actual idle beyond3000 ticks.

The copied test observer is not sys-init recovery policy; no normal owner, kernel,
ABI, grant, quota, payload or released pin changes. Native child-profile mismatch
coverage is now supplied for independent consumption. Remaining malformed/stale/
foreign schedules, broader waits and useful-session integration remain next. Full
SUSTAIN-01–06/SI-07, SDK/reader disposition and R1 remain open. See the packet for
exact recipes, frozen sources, linked resource inspection, controls and retention.

### SI-07 private request-denial checkpoint — 2026-10-03

The [request-denial packet](evidence/si07-request-denial-2026-10-03/README.md) qualifies
four native controls using one complete frame injected after real child receipt.
Count17/nonzero padding return -13; a live runner-context fd4 selector on the child
connection and epoch1 selector during actual generation2 return -9. Exact padded
reply delivery, no child I/O/backend output effects, confirmed stopped143 clients,
endpoint/task retirement, backend17 and stale denials precede authorized halt.
Stale has a healthy completed/reclaimed first cycle and six reclaims; others three.
All idle beyond3000 ticks. Four comparisons/53 corruptions and host/pin checks pass.
Maximum code10472/16384 and estimated stack3832/4088; raw/ELF identity and scoped
GOT/register inspection bind all images. Failed build/inspection attempts remain.

Original owner/child/kernel/sys-init, ABI/grants/limits and release pins remain
unchanged. Private selectors are connection-local data, not native capabilities.
This does not demonstrate arbitrary endpoint spoofing, truncated-frame handling,
production interruption recovery, independent consumption or complete SI-07/R1.
Next are retained-frame/wait transitions and useful shell-session integration.

### SI-07 wait/command composition — 2026-10-03

The [composed-wait packet](evidence/si07-wait-composition-2026-10-03/README.md) adds
two native schedules to the matched v2 command. One serial byte remains ready
across two waits and is consumed once. Delayed input requires at least10 guest
ticks before wake; future sequence rejects -22 without mutation; empty input then
reaches its absolute deadline with -110. Each exact6-newline/0/0/17 command retires
all tasks/channels and denies stale references before an old lifecycle observation
returns retained event/current sequence, then authorized halt with three reclaims.
That event can include channel/terminal/cleanup publication; it is not a uniquely
attributed terminal-source witness. Both idle beyond3000 ticks. Two comparisons/
28 corruptions pass; code9912/16384, estimated stack3784/4088 and raw/ELF/assembly
inspection qualify. Host/pin checks and failure retention are recorded in the packet.

No normal runtime, ABI/grant/limit, sibling policy or released-pin change. Exact
wait ordering beyond these schedules, cancellation and truncated-frame coverage
remain open. Next reconcile sustained ABI22 ownership with the existing ABI23
interactive SESSION contract before composing sys-init and a useful serial shell;
these payloads cannot be substituted across profiles. Full SI-07/R1 remains open.

### SI-07 bounded kernel dependency complete — 2026-10-03

The [completion review](evidence/si07-completion-review-2026-10-03/README.md) closes
the original kernel-backlog requirement: sustained lifetime/idle/wakeup, more than
three useful cleaned cycles, scoped authority/stale/exhaustion handling, authorized
quiescent halt and an actual matching sys-init-owned consumer. Six sealed packets
and276 current source members verify;30 retained traces/141 corruptions and local
host/pin checks pass. No new QEMU execution or sibling owner approval is inferred.

Full SUSTAIN-01–06 native matrices and production composition remain partial;
consumed/foreign native endpoints, truncated frames, wider interruption/cancel
schedules and final-epoch consuming composition are not all established. ABI22
has no public cancellation operation; pure-core cancellation remains host coverage.
No general recovery or exhaustive race claim is made. The kernel dependency does
not include full dash, OpenZFS, package installation or release approval. Next
reconcile the distinct ABI22 sustained and ABI23 interactive SESSION ownership/
profile contracts for the assembled sys-init/serial-shell path.
