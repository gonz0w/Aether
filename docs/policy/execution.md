# Aether execution policy

Canonical sections extracted from [PROJECT](../../PROJECT.md). Local policy is
bound to the containing source revision; external pins retain their own identities.
Existing owner change authority and all applicable contracts remain in force.
Commands and literal repository paths below keep their original working directory;
only Markdown links were rebased for this file.

## Current milestone execution direction —2026-11-01

Cam approved the [fixed reader profile](https://github.com/gonz0w/Aether/issues/97#issuecomment-6563209702)
and [standing direction](https://github.com/gonz0w/Aether/issues/97#issuecomment-6563276253):
“yes these type of requests are auto approved, i only want work to stop for desing
decisions or hard blockers.” For the selected filesystem/TTY/Zsh milestone,
routine bounded implementation and fit corrections and separately reviewed QEMU
checks may proceed within existing resource, disposable-media and no-network
boundaries without another per-step confirmation. This explicitly supersedes the
older per-run confirmation clauses below for that routine scope only.

Keep finite scope, affected checks, separate review, exact source/artifact/media
binding, one attempt per reviewed proposal and known stop/cleanup. Stop a cohort
at its first unexpected result. Diagnose and correct the failure, then review a
fresh matching candidate before another bounded attempt; consumed attempts stay
consumed. The standing owner instruction supplies execution authority for that
reviewed routine candidate. A local record or agent review cannot create it.
Stop for consequential design, authority or product decisions or genuine hard
blockers. No hardware, release/deployment, ambient authority or unbounded resource
expansion follows from this direction.

The approved default-off `native-mktemp-reader` profile enlarges physical
`State.output` to320 bytes in the existing private BSP read-only ABI14 closure.
Only engine slot0 has logical320-byte capacity; other slots and default profiles
retain256. Four States add256 raw bytes; actual linked aligned kernel static growth
must be measured and must not exceed16KiB. Larger growth needs an owner decision.
Per-request256/per-transfer16 limits, pointer and authority checks, eight-byte
observation format, query bounds and generation reset remain unchanged. No new
syscall, capability kind or ABI is introduced. Reuse the frozen reader engine,
controller and envelope artifacts; only the reader kernels/ISOs need rebuilding.

## Selected terminal MODE and transmitter-empty query —2026-11-01

Cam directly approved the reviewed [issue121 design](https://github.com/gonz0w/Aether/issues/121#issuecomment-6566036292):
“Approve this scoped design (Recommended)”. This selects explicit MODE permission
for the one admitted test application's terminal relationship and one opt-in,
console-holder-only nonblocking int81 operation `0x26004`. Existing limits and
default profiles remain unchanged. The accepted proposal identity is
`fe5446691ac214ee4331d7770ae9cae7a97f5064c02d2068b0ac088dd45d7c12`;
separate peer review is
`e79003da2596f794d3d3f44b85a2ca433a79272eb1fe12dfb7c2c4c30f2b9f6d`.
The published lifetime and GET-revision clarifications in that issue bind this
selection. Do not request the same design approval again.

The query accepts only F001 from the existing exact live console holder under
current slot/generation/admission/closed checks, with all auxiliary arguments
zero. It observes COM1 LSR once, enabling receive-error retention before reading
status. Return zero only for valid TEMT, EAGAIN while busy, and EIO for all-ones
or impossible TEMT-without-THRE. Preserve receive bytes and pending receive errors. The selected profile enables
retention before every initial LSR poll, including earlier write-status polls.
No raw port selection, pointers, queue, allocation or kernel wait is added.
Existing read/write, `0x26002` close and `0x26003` handoff keep their contracts.

Rust retains waiting and mode policy under the original absolute deadline and
attempt/containment bounds. The selected experiment saves mode, applies real
ICRNL with TCSADRAIN, verifies its byte effect, restores and verifies raw CR on
the existing duplex descriptor. Public mode controls require the original live
MODE-bearing reference, exact caller/generation, control token and applicable
revision. The unpublished private duplicate in the existing fourth alias slot
is only for trusted local cleanup after confirmed app stop; it cannot authorize
public requests after the original reference retires. GET has a zero request
body and returns current revision; SET/RESTORE compare expected revision.

This authorizes the scoped implementation and its focused checks. The standing
milestone direction covers separately reviewed finite QEMU candidates and normal
GitHub delivery. No quota, alias capacity, raw PIO grant, service placement,
canonical/ISIG/group support, native EINTR, full Zsh or R1 acceptance follows.

## Selected terminal SIGINT and safe read interruption —2026-11-01

Cam directly approved the reviewed [issue124 design](https://github.com/gonz0w/Aether/issues/124#issuecomment-6567425677):
“Approve scoped SIGINT design (Recommended)”. Proposal02 identity is
`c3437226baf99ae4d5bfaaa60ce3eb1a964bc49ac95db6b2de6715b718428912`;
separate peer review is
`54ff128f561a6e4f99616360c9e5efad2004e99f863cade476103579a03514ff`.
This selects one default-off SIGINT-only entry at int81 `0x29003`, bound to the
existing Rust TTY Owner generation and its exact admitted single-thread app
handle/generation. Existing limits and default profiles remain unchanged.
Do not request this same scoped design decision again.

RDI is that admitted app handle, RSI is SIGINT2, RDX is PREFLIGHT0 or POST1,
and R10/R8/R9 are zero. Validate actual relationship, caller/target generations,
admission/liveness and current disposition independently on each call.
PREFLIGHT has no effects: ignored0, supported handler1, default EOPNOTSUPP.
POST returns ignored0/no effect, newly pending1, or coalesced2; outcomes do not
claim delivery. Negative returns change no pending/action/execution state.
A preflight observation is no lease. No PID/group lookup, arbitrary signal,
handler pointers, general kill or successor authority is added.

Rust owns VINTR0x03 and read policy. A selected typed read carries only its own
pre-critical saved-mask eligibility, granting no targeting power. Preserve
positive progress, masked/ignored behavior and current absolute deadlines;
unknown effects cannot be replayed. Before libc exposes a known zero-byte EINTR,
validate the full reply, make the sole context idle, restore a stable local
saved mask, and deliver the actual checked handler at that safe unmask boundary.
Selected delivery failure returns EIO with the pre-mask-operation mask restored
and the pending occurrence uncommitted; the runtime takes its known containment
exit125. Selected self-post/poll0x29002 rejects with EACCES; older profiles retain
their existing entry behavior. Retain post-stop local MODE restoration.

Standing milestone direction covers focused implementation, separately reviewed
finite QEMU candidates and routine GitHub delivery. No general process groups,
stop/continue, canonical queue, full ZLE/Zsh, service relocation or quota increase
is selected. The fixed recipient is not a POSIX foreground process group.

## Selected real-Zsh filesystem composition —2026-11-02

Cam directly approved [issue137](https://github.com/gonz0w/Aether/issues/137#issuecomment-6576184144):
“Approve scoped #137 design (Recommended)”. Select the retained Rust Owner
namespace custody, narrow readonly real-terminfo FILE/startup/access/cwd consumers,
typed held-directory ncurses port, and one closed positive composition of the
existing large-Zsh, MODE and exact-generation SIGINT profiles.

The Owner retains existing HOME15/root3 privately; Zsh receives process endpoints
only. Preserve untouched-namespace preflight/commit, provision/readback before FD
startup, one Client/epoch and the retained directory until healthy teardown.
Keep all existing numeric limits, old profiles, ordinary/incompatible guards,
source/media binding, finite attempts, known cleanup and protected delivery.
No new syscall, grant, privileged path, full-stat/METADATA16 authority or resource
increase is selected. The [consumer contract](../../userland/docs/ZSH-FILESYSTEM.md)
records the closed wire and actual implementation/qualification limits.

The standing milestone policy authorizes routine implementation, reviewed bounded
builds/tests and GitHub delivery. A guest still requires actual matching artifacts,
fit/consumer review and the existing concrete execution/cleanup gates. This design
answer establishes no real prompt, job control, login, external command, cold
persistence, package or R1 acceptance. Further consequential deviations still go
to Cam; ordinary bounded corrections do not need another permission question.

### Fixed diagnostic evidence decision —2026-11-02

Cam [approved bounded diagnostic evidence](https://github.com/gonz0w/Aether/issues/137#issuecomment-6578169276)
for the fixed issue137 builtin workload. Completed actual route/known-defect/
structural checks plus one guarded diagnostic workload may establish scoped fit,
replacing proposal03's complete pre-image startup/parser/handler stack and peak
heap proof prerequisite for this experiment. Keep all numerical memory/time/
request/mutation, authority, no-network/disposable-media, finite-attempt/source-
binding and known-cleanup limits unchanged. Fresh concrete image/media/consumer
review still precedes execution. No unchanged or uncertain-effect retry is
selected; failures are diagnosed before a fresh reviewed candidate. This grants
no exact/general peak demand, external-command/job-control/login, cold recovery,
package or R1 qualification. The earlier scoped design approval stays effective.

### Scoped Zsh checkpoint delivery —2026-11-02

Cam directly answered
[“Approve scoped Zsh checkpoint delivery (Recommended)”](https://github.com/gonz0w/Aether/issues/137#issuecomment-6587956406).
For issue137 only, its reviewed actual prompt/builtin/normal-exit/export/cleanup
result, affected focused checks and required hosted CI may qualify source
integration and closure despite the failed/incomplete full-root host gate.
This is an explicit departure from DEVELOPMENT's major-handoff prerequisite;
it is not a full-host pass or general policy relaxation.

[Issue141](https://github.com/gonz0w/Aether/issues/141) retains the unclassified
failures and unverified descendant/pipe cleanup before a later assembled-system
checkpoint. Later known-clean probes do not reconcile that history. Preserve
quarantine and all numerical, authority, source/media and execution limits.
No extra guest, unknown-effect retry or cleanup authority follows. External
commands, login, persistent write/reboot/readback, packages and R1 retain their
own gates. The earlier design and fixed diagnostic-fit decisions remain effective.

## Selected Zsh parent/helper composition —2026-11-02

Cam directly approved
[the scoped parent/helper design](https://github.com/gonz0w/Aether/issues/142#issuecomment-6589424662):
“Approve scoped parent/helper design (Recommended)”. Reviewed proposal03 in
issue142 selects one real Zsh parent and one immutable helper child with the
actual internal pipe, existing copy/exec/SIGCHLD, one context per process and
Rust Owner namespace custody. [Issue143](https://github.com/gonz0w/Aether/issues/143)
owns implementation; the [local consumer contract](../../userland/docs/ZSH-FILESYSTEM.md#selected-parenthelper-extension)
records the selected ownership and compatibility requirements.

Child bindings are local to its real native slot/generation. MODE/private restore
and SIGINT stay parent-only; child SIGINT ownership is explicitly null. Only
READ/WRITE proxy descriptions are delegated, with an exclusive read lease and
truthful unsupported canonical/ISIG child input. Use complete336-byte selected
snapshots, preserve old304-byte profiles, and retain actual wait status through
known delivery/collection, reclaim and parent read-lease restoration. Unknown
effects contain without replay. No namespace grant, new syscall/capability kind,
global process table or numeric limit increase is selected.

This approves scoped implementation under the standing milestone direction.
Correct and measure the known oversized external frame before any image; fresh
actual integrated fits and applicable verification/artifact/media/cleanup gates
remain. No image/run result, general utility or filesystem-exec installation,
child job control/input, login, persistence, package or R1 acceptance is claimed.
Issue137's diagnostic-fit/full-host exceptions remain issue-only; issue141 retains
its failed coverage and unverified cleanup.

## Selected issue143 capacity and verification decision —2026-11-02

Owner direction,2026-11-02: Cam directly approved the
[scoped issue143 plan](https://github.com/gonz0w/Aether/issues/143#issuecomment-6591806304), including the reviewed proposal in comment6591273627.
Only native-zsh-external/native_zsh_process may use73,728 bytes of Owner RX
code and a12,288-byte mapped stack (12,280 usable), within unchanged128-page
Owner backing. Preserve ABI31/RSP0x802000-8, Runtime/workspace4,096 each,
RW/NX stack, absent guards and old-profile code/stack/parser/boot limits.
Fresh matched selected fit, boundary/guard tests and separate artifact/media
review precede an image/trial. The one fixed helper/status7/parent-prompt/clean
exit trial may establish remaining scoped workload fit despite unknown complete
parser/handler/heap/copied-peak proof. No general peak qualification follows.
Focused contract checks, separate review, required protected CI and successful
exact trial may qualify this issue143 checkpoint while issue141's full-root
integration gate stays open. This is an explicit issue143 policy exception,
not a full-host pass or transfer of issue137's exceptions. Preserve unknown
history/quarantines. Other app/time/request/mutation/capture/no-network,
disposable-media, finite-attempt and known-cleanup limits remain binding.
Login, persistence/reboot, packages, assembled-system and R1 gates remain separate.
Routine implementation, builds, reviewed bounded tests and delivery proceed
under standing approval; this decision grants no new syscall/capability kind,
arbitrary executable authority or unknown-effect retry.

## Selected issue145 home write and verification decision —2026-11-02

Owner direction,2026-11-02: Cam directly approved the
[scoped issue145 design and gates](https://github.com/gonz0w/Aether/issues/145#issuecomment-6594800206):
“Approve scoped #145 design and gates”. Reviewed plan02 selects only the exact
admitted post-exec helper writing16 fixed bytes to existing empty `/home/probe`
through Rust Owner custody and opt-in AEFP0005. Preserve old FILE dialects,
opcode10 DIRECTORY, reserved7 denial and issue143 status7/v2 behavior. Only this
helper may use fixed-home-open12/write11; parent/pre-exec/stale/other paths/modes
reject before mutation. Retain checked completed write/close outcomes, success-only
position changes and no replay of unknown/short effects. No namespace grant,
second filesystem broker, new syscall or kernel capability kind is selected.

The scoped exact-seven engine stays within9 mutations/96 requests. Fresh matching
parent/helper/Owner/engine fits must use the same selected ceilings: Owner
73,728 RX,12,288 mapped stack/12,280 usable, Runtime/workspace4,096 each and128
backing pages, plus existing application/engine/task/channel/capture bounds.
No numeric increase follows. Guarded fixed writer and original-provider pristine/
recovery readers may establish remaining scoped workload fit despite unknown
general stack/heap/copied peaks. Writer60s/120s/6000ticks, readers30s/3000ticks
within120s cohort, no network, disposable media, exact source/artifact/media review,
once-only inputs, finite attempts and known cleanup stay binding. Reader slot0
must fit its existing320-byte selection; defaults/other slots remain256.

For issue145 only, focused affected checks, separate review, required protected
CI, actual helper0/status0/prompt/export/reclaim writer and exact independent
cold readback may qualify checkpoint delivery while issue141's full-root gap
stays open. This is an explicit decision, not a full-host pass or transfer of
issue143's exception. Preserve failed history and quarantines. General redirection,
arbitrary exec, child job control/input, login, packages, assembled-system and
R1 gates remain separate. Routine builds, reviewed bounded tests and GitHub
delivery proceed under standing approval; new limit/authority choices still stop.

## Selected filesystem ELF exec and checkpoint decision —2026-11-04

Cam directly approved the [reviewed issue12 design](https://github.com/gonz0w/Aether/issues/12#issuecomment-6635124495)
and its gates: “Approve scoped #12 design and gates (Recommended)”. The
[decision record](https://github.com/gonz0w/Aether/issues/12#issuecomment-6635185907)
authorizes implementation in [issue148](https://github.com/gonz0w/Aether/issues/148).
Only default-off native-zsh-file-exec is selected: the actual admitted Rust Owner
lifetime may snapshot/install one sealed1..4096-byte filesystem ELF into its exact
frozen helper through int81 0x2300B. Keep existing eager loader checks and atomic
replacement; copy complete bytes/arguments into private kernel scratch, preserve
that copy through RELRO, clear scratch on every return and retain no user pointer
or new global image metadata. C004 is only a source receipt tag for existing
query/publication. Known rejection preserves old child/FD/freeze/receipt; uncertain
postcommit outcomes contain. Deny all three boot-cache fallback routes under this
selector, including generic launch; old profiles remain exact.

The sole Rust Owner provisions existing /home/probe with one exact completed ELF
write/close, binds eligibility to the retained object/epoch and seals it against
all further mutation/WRITE aliases. Namespace authority stays with the Owner;
READ, names, metadata and hashes never create execute rights. Save the672-byte
exec frame separately; acquire with EOF-first/exact full read/post-stat/checked
close into existing4096 workspace, restore before FD rebind/publication. Failed
or unknown acquisition/close never executes or replays. Preserve actual0600
metadata; this is explicit native authority, not POSIX executable-mode policy.

Keep7/9 mutations,96 requests, Owner73728 RX,12288 mapped/12280 usable stack,
4096 Runtime/workspace each,128 backing pages and all existing application/engine/
task/channel/worker/capture bounds. No numeric increase follows. Fresh actual
complete Rust ELF<=4096,336-byte startup/native-identity/READY obligations and
whole affected code/data/stack/backing/disjointness fits precede any image.
Embedded provisioning bytes count toward Owner RX; fit failure stops for replan.

For issue148 only, the reviewed guarded44-byte real-Zsh helper23/status23/prompt
trial may establish remaining fixed-workload fit despite unknown general peaks.
Keep60s writer/120s total/6000ticks, no network, disposable media, exact source/
artifact/media binding, finite attempts, once-only inputs, no automatic retry and
known cleanup. Focused affected checks, separate review, required protected CI
and actual READY/C004/helper23/status23/prompt/normal parent+exact-seven engine
export/mode restore/three reclaims/known host cleanup qualify checkpoint delivery
while issue141's full-root gap stays open. This explicit exception does not claim
a full-root pass, general VM/PATH runner, login, cold boot-to-program, packages or
R1. Preserve failures, quarantines and compact retention. Routine accepted work
and GitHub delivery retain standing approval; new authority/resource/design
choices and hard blockers still stop.

## Ordinary-app namespace and clock contract —2026-10-28

The owner approved the separately reviewed [issue98 proposal02](https://github.com/gonz0w/Aether/issues/98#issuecomment-6477628920)
for implementation and bounded host/offline-fit work. Proposal identity is
`258723ec94c221185e379fe7e67becd55b1497fd6efcbcdb36d565945e8a080e`;
separate technical review is
`7b19aa147eb9603131a993a7886ca5fd582022cefa4a5dfa1533b89e4bd73095`.
The decision covers one positive ordinary-app temporary-directory experiment.

Implement the fixed launch record of 320 bytes and startup record of 64 bytes, atomic
pre-greeting handoff of the sole AF09 namespace connection, and a distinct
read-only monotonic-clock grant bound to the app's nonreused lifetime. The
reviewed kernel operations are 0x2300a and 0x28012, startup tag 0xa003 and clock
capability kind 0x36. Preserve existing operations and callers. The proposal's
holder, direction, generation, epoch, admission, revocation and copy/exec denials
remain part of the accepted contract.

Use the existing 304-byte descriptor startup and stream wire for stdout/stderr,
with the reviewed one-app sys-init stream owner and app-local musl vector-write
adaptation. The app's actual EOF/EPIPE observations and once-only raw closes do
not establish engine export: sys-init independently requires app/engine terminal
outcomes, ordered export, reclaim and existing clean-halt settlement.

Ordinary limits remain 1 MiB ELF, 128 image-plus-fixed-stack pages, 128 backing pages
and 4096 TLS bytes, with 64 KiB mapped stack and initial SP at 48 KiB. Existing engine,
owner, channel, capture, source-freeze, retention and focused-test limits remain.
No larger Zsh profile, resource exception, ambient authority, SDK/provider rebuild,
new filesystem wire operation or general broker is selected. Implementation
requires finite issues, affected checks and separate review before integration.
This decision grants no QEMU, hardware, native sufficiency or release acceptance;
a later campaign needs its own reviewed artifacts and explicit execution grant.

## Bounded Zsh application trial —2026-10-25

The owner approved implementing and host-testing the separately reviewed
[application profile](https://github.com/gonz0w/Aether/issues/69): a distinct
1.5 MiB application ELF cap, 384 image-plus-existing-stack pages and 640 total
backing pages in each of five fork-capable application slots. The engine retains 8192 pages and
the owner retains 128. This assigns 45 MiB within the existing 64 MiB backing
reservation; 19 MiB remains ungranted. The selected application image window is
`0x200000..0x400000`. Existing capability, TLS, stack/bootstrap and ownership
checks remain binding; older profiles retain their defaults, selectors and seals.

At the admitted image limit, at least 256 backing pages remain for all later
runtime allocations, including TLS and allocator overhead. This is a bounded
trial resource decision, not evidence of Zsh heap/stack sufficiency. Routine
implementation and host verification follow the finite issue scope, required
checks and separate review. No guest, native prompt or ISO qualification is
authorized by this decision. Exact SDK/artifact qualification evidence stays local.
## AF09 diagnostic control review —2026-10-26

The owner reviewed and approved the concrete [issue75 diagnostic](https://github.com/gonz0w/Aether/issues/75)
from draft PR76/head `88a83fab808221cec5770b3db447d849478688ee`.
Introduce the compile-time `native-af09-drain` selector with default `none` and
exactly `file_prefix`, `exec_prefix`, `fork_prefix`, `stream`, `no_ack`,
`partial_ack`, `exit_deadline` and `pending_fragment`. Omitted/explicit `none`
retain ordinary behavior. This satisfies DEVELOPMENT's human-review requirement
for this closed non-boolean control; do not ask for the same review again.

Implementation, host verification and matched offline artifact preparation may
proceed under the [diagnostic contract](../../docs/NATIVE-AF09-DRAIN.md). Existing
profile/authority/resource limits, source freezes, cleanup, separate review and
major-handoff checks remain. This adds no runtime selector, guest permission,
resource exception, native sufficiency or release acceptance. A later guest
requires its concrete reviewed artifact and execution disposition.
## AF09 offline family budget —2026-10-26

The owner adopted a standing5400-second aggregate for the complete
[issue75](https://github.com/gonz0w/Aether/issues/75) offline admission/drain
family: file_prefix, exec_prefix, fork_prefix, stream, no_ack, partial_ack,
exit_deadline and pending_fragment, with twenty prepared roles in total.
One clock covers the whole selected suite from preflight through final input
verification, publication and owned cleanup; case and builder calls do not renew it.
Other target suites retain their1800-second ceilings.

Children remain180 seconds, live stdout/stderr4MiB each and compiler files16MiB.
Focused host300/complete host900 limits, source freezes, all tests, existing media
allowances, runtime authority/memory/request bounds and known cleanup stay binding.
This time-only default grants no guest, native sufficiency or release acceptance.

Earlier failed campaigns remain failed. Triage failures, correct their cause,
recheck affected inputs and obtain separate preflight review before a justified
fresh complete-family attempt. Do not blindly retry unchanged failed work or
replay unknown mutations. This standing default does not require another approval
for each ordinary corrective attempt inside its scope; a larger bound or another
consequential resource change remains the owner's decision.

## Selected cold-reopen checkpoint decision —2026-11-04

Cam directly approved [issue150’s separately reviewed proposal](https://github.com/gonz0w/Aether/issues/150#issuecomment-6648622214):
“Approve scoped #150 design and gates”. Select one default-off cold composition
that reopens existing home/probe and terminfo, using truthful canonical-zero
bootstrap receipts on both success and actual failure phases. Preserve old
result validation and extents; no fabricated creates or suppressed errors.
The sole trusted Rust Owner selects the actual current-epoch helper object only
after full expected3548-byte ELF/type/size/EOF/post-stat/checked-close validation;
byte equality restricts existing execution authority and never creates it.
Reopen/check the pinned1268-byte terminfo and retain its actual directory view.
No mutation or WRITE alias, namespace forwarding, new syscall, capability kind,
service, buffer or numeric increase follows. Existing0x2300B/C004/frozen-child/
private-copy/ELF/W^X/fallback denials remain binding. All failed/short/unknown
reads/stats/closes contain, retain obligations and never repair/replay.

Select an exact-zero client/bootstrap mutation engine with matching C/Rust
canonical result predicates, including pre-activation lookup/type/close errors.
Retain original writable/accounted SPA, READ|WRITE|FLUSH region, import, ordering
and export/cleanup; zero client mutations is not zero disk writes or bitwise
unchanged media. No diagnostic interface is added solely for raw receipt counts.
Native completion binds the actual reviewed predicates/artifact to focused host
result tests; do not claim independent raw UART count observation.

One fresh accepted provisioning writer is followed only after clean export and
known stop/cleanup by one fresh cold VM on that exact stopped disposable disk.
Use the fixed44-byte helper23/status23/prompt/exit workload, no network, once-only
inputs/no retry, each existing60s workload/120s total/6000ticks, capture limits and
known complete cleanup. Preserve Owner73728 RX/12288 mapped/12280 usable stack,
Runtime/workspace4096 each,128 backing,96 requests/9 mutation ceiling (cold
expected0), all existing application/engine/task/channel/worker/preparation bounds.
Fresh changed code/data/stack/backing/closure fits precede image; verified unchanged
inputs may reuse applicable evidence. A failed fit stops for replan.

For issue150 only, guarded exact workload evidence may establish remaining scoped
fit despite unknown general peaks. Focused affected behavior/capability/failure
checks, separate source/artifact/native-result review, fresh actual fits, required
protected CI and successful exact writer/cold evidence may qualify checkpoint
delivery while issue141 stays open. This explicit decision is not a full-host
pass or sustained manual/authenticated login, arbitrary exec, general write/reboot
recovery, packages, assembled-system or R1 acceptance. Routine work/delivery retain
standing authority; new consequential design/resource/gate decisions still stop.

## Selected cold Zsh idle and clean exit — 2026-11-06

Cam approved the [reviewed issue152 proposal](https://github.com/gonz0w/Aether/issues/152#issuecomment-6667792475)
in the [recorded decision](https://github.com/gonz0w/Aether/issues/152#issuecomment-6685881337).
Select the default-off Rust Owner cold-reopen variant. A clean no-child exit
requires the pristine child ledger and a confirmed close of the unused helper.
The existing exact settled-helper result, authority and resource limits apply.

The [34-byte serial workload](https://github.com/gonz0w/Aether/issues/152#issuecomment-6685904616)
uses one fresh qualifying writer and one cold trial on the exact stopped writer
disk, with a five-second idle interval. Existing no-network, finite limits and
stop rules apply. After fresh static fits, guarded native evidence may establish
the remaining scoped workload fit. Focused affected checks, separate review,
successful trial and required CI may qualify this checkpoint while issue141
remains open. Sustained manual login and assembled R1 have separate gates.

## Selected serial operator session — 2026-11-06

Cam approved the [reviewed issue154 design](https://github.com/gonz0w/Aether/issues/154#issuecomment-6697115453)
in the milestone chat and directed implementation through foreground serial trial
and delivery. Select the default-off operator composition with exclusive guest
limits of 6000 startup ticks, 24000 dispatch ticks and 30000 total ticks. Check
the outgoing phase before each transition. The existing Owner event interface
may park authenticated pending terminal reads using the pre-rescan sequence and
checked parent/engine liveness. Retain the existing resource quotas.

Use one local foreground Screen display on the private serial endpoint with
host command escapes disabled. The provisioning writer keeps 60s workload and
120s total. Cold operator execution has 330s workload and 360s total, with the
reviewed one-use disk, stop and capture rules. Fresh fits, focused affected checks,
separate review, a successful paired foreground trial with 65s idle and required
CI may qualify this checkpoint while issue141 remains open. Include the reviewed
local preparation and attachment instructions.

## Selected interactive serial workload — 2026-11-07

Cam directly approved the [issue156 workload and gates](https://github.com/gonz0w/Aether/issues/156#issuecomment-6707933187).
Use the existing operator guest for the fixed153-byte editing, real Ctrl-C130,
persisted-helper23 and clean-exit workload. This adds no target profile,
interface, authority or numeric limit. A closed host workload selection binds
its own proposal and approval; old automated and manual sessions stay unchanged.

Reuse only exactly bound unchanged target fits; changed target inputs require
fresh affected fits. One fresh reviewed writer/cold pair may establish remaining
scoped workload fit within the existing ceilings. Focused checks, separate
review, successful actual trial and required protected CI may qualify issue156
delivery while141 stays open. Keep one-use media, finite attempts, no replay of
unknown effects and known cleanup. General peaks, job control, authentication,
packages and assembled R1 remain separate.
