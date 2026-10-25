# Two clients and a backend: native connections v1

[Exec transaction boundaries](evidence/pipeline-exec-boundaries-2026-09-15/README.md)
now separate bounded validation/admission/commit from blocking transport, preserving
cancellation and authority checks. All54 native cases and104 host checks pass.
This is an integration prerequisite; exec/I/O interleaving remains next.

[Direct wait dispatcher intake](evidence/pipeline-wait-probes-2026-09-15/README.md)
qualifies wait-any, live WNOHANG, scoped denial and once-only collection across
fragmented replies. All54 native cases and104 host checks pass; wrong errno and
recollection controls reject. Exec/I/O integration and interrupted wait recovery
remain open; this is not full-dash or independent consumer acceptance.

[Parent wait alongside I/O](evidence/pipeline-wait-io-2026-09-15/README.md)
now retains a live blocking wait while child I/O advances, with once-only collection
and partial replies. Final51 native cases and104 host checks pass; early zero
completion is rejected. Ten build/size attempts are preserved. Broader wait-state
qualification, exec multiplexing and independent consumer acceptance remain open.

[Autonomous pipeline children](evidence/pipeline-autonomous-2026-09-15/README.md)
now initiate I/O without a separate dispatch-release token. All49 native cases
and104 host checks pass; obsolete-token injection is rejected. Parent/peer release
and sequential owner phases remain; interleaving parent waits with child I/O is next.

[Copied-child dash builtin](evidence/pipeline-copied-builtin-2026-09-15/README.md)
now runs printf directly in the forked writer, preserving live FD ownership and
excluding writer replacement through per-slot admission counts. All47 native cases
and104 host checks pass; all66 prior images are identical. Coordinated execution/
data/wait handling is next; sequential owner phases and dispatch release remain.

[Actual dash builtin pipeline](evidence/pipeline-dash-builtin-2026-09-15/README.md)
now runs pinned printfcmd/flushall in the replacement writer, with exact output
and wrong-byte rejection. All45 native cases and104 host checks pass; all62 prior
images are identical. Direct copied-child builtin execution and coordinated
execution/data/wait remain next; this is not full shell or consumer acceptance.

[Child-requested pipeline exec](evidence/pipeline-exec-request-2026-09-15/README.md)
now initiates replacement through a private public-execve shim, verifies denied
request rollback and retries with live snapshots. Forty-three native cases and104
host checks pass. Owner handling remains sequential; actual dash builtin execution
and execution/data/wait scheduling remain open.

[Inherited stdin and stderr](evidence/pipeline-stdio-2026-09-15/README.md)
complete the bounded fixture's inherited standard-stream path: actual libc input/
EOF, independent output/diagnostic captures and checked closure. Forty-one native
cases and104 host checks pass; retained input authority and dropped diagnostics
are rejected. Actual dash scheduling and consumer intake remain open.

[Inherited pipeline stdout](evidence/pipeline-stdout-inherit-2026-09-15/README.md)
now carries parent-granted output through actual forks, validated exec/CLOEXEC
revocation and independent parent closure. Thirty-eight native cases and104 host
checks pass; deliberately retained writer authority is independently rejected.
Inherited stdin/stderr and actual dash execution remain open.

[Pipeline final stdout grant](evidence/pipeline-stdout-2026-09-15/README.md)
now carries actual libc output into an explicitly granted bounded capture; forged
caller, malformed grant and dropped-output controls are checked. Thirty-six native
cases and104 host checks pass. This is post-exec output authority, not full inherited
stdio or console integration; actual dash/child-driven execution remains open.

[Multi-child wait-any intake](evidence/pipeline-wait-any-2026-09-15/README.md)
now exercises musl wait3/wait4, live WNOHANG, scoped PID rejection and once-only
terminal collection. Thirty-three native cases and104 host checks pass. Early
false completion is rejected; the discovered channel backpressure defect is fixed.
Actual dash streams, child-driven execution and concurrent scheduling remain open.

[Interleaved pipeline construction](evidence/pipeline-interleave-2026-09-15/README.md)
now supports pipe creation and parent close between successive native forks, with
reduced live inheritance. Thirty-one native cases and 104 host checks pass; a false
close acknowledgment rejects before another copy. Actual dash wait-any, standard
streams, child-driven execution and unchanged scripts remain integration work.

[Client pipe creation and child collection](evidence/pipeline-parent-ops-2026-09-15/README.md)
now exercises two requested pipes, public parent close and musl waitpid backed by
observed terminal records. Twenty-nine native cases and 104 host checks pass;
repeat collection returns ECHILD and a false status is independently rejected.
Fixed owner phases remain; actual dash orchestration, unchanged consumer scripts
and independent intake are still open. No full-dash handoff is claimed.

[Live libc fork/exec snapshots](evidence/pipeline-live-fds-2026-09-15/README.md)
now capture actual fcntl-created aliases and exec flags through the shared facade.
Twenty-seven native cases and 104 host checks pass. Initial pipe grants and exec
scheduling remain fixture-controlled; actual dash pipe/fork/wait orchestration
and independent intake remain open.

[Public musl fork pipeline](evidence/pipeline-public-fork-2026-09-15/README.md)
now creates all three children through public fork with copied libc repair, then
runs the libc exec/I/O path. Twenty-five native cases and 104 host checks pass.
Actual dash-driven pipe/fork/wait orchestration and independent intake remain open;
this fixed-snapshot witness is not a full-dash handoff.

[Seven-binding libc replacement I/O](evidence/pipeline-libc-2026-09-15/README.md)
now uses the shared descriptor adapter and actual musl read/write/close after exec,
including dup2, CLOEXEC aliases and EOF. Twenty-three capacity cases, twenty-one
legacy pipe cases and 104 host checks pass. Actual dash multi-child orchestration,
copied libc rebind and independent intake remain open; no full-dash handoff yet.

[Interrupted pipeline exec cleanup](evidence/pipeline-exec-stop-2026-09-15/README.md)
now cancels parked-admission and partial-table schedules after exact participant
terminal observation, with three-generation reuse. Twenty-one native cases and
104 host checks pass. Actual libc/dash integration and independent intake remain
open; scheduled cancellation does not establish arbitrary lost-receipt recovery.

[Copied pipeline replacement exec](evidence/pipeline-exec-2026-09-15/README.md)
now passes distinct-image startup, atomic CLOEXEC holder removal and exact pipe
I/O through three generations. Eighteen native cases and 104 host checks pass.
Validated fixture tables do not install libc descriptors; interrupted-exec cleanup,
actual dash scripts and independent intake remain open. No new full-dash handoff.

[Native copied pipeline workers](evidence/pipeline-copy-2026-09-15/README.md)
now inherit both pipes through actual freeze/copy and complete three generations
with fifteen reclaims. Sixteen native cases and 104 host checks pass. This is a
private snapshot/copy fixture; replacement exec, libc descriptor installation,
unchanged dash scripts and independent consumer handoff remain open.

[Native early-reader EPIPE](evidence/pipeline-epipe-2026-09-15/README.md)
now passes explicit close and exit-with-holder schedules through both pipe stages,
including fragmented error replies and three-generation cleanup. Fourteen native
cases and 104 host checks pass. Actual dash fork/exec, SIGPIPE composition and
independent consumer intake remain open; this is private AENMX004 coverage.

The [interrupted-writer receipt](evidence/pipeline-stop-2026-09-15/README.md)
extends the private AENMX004 capacity experiment with confirmed-stop cleanup of
partial requests and replies. Eleven native cases and 104 host checks pass;
normal capacity/pipe workers remain byte-identical. This does not change the ABI9
contract below or qualify actual dash fork/exec pipelines. STATE owns next work.

AENMX001 / ABI 9 is a separate BSP conformance profile for the transport portion
of UP-01. It reuses ABI 8's 80-byte three-ELF envelope, 48 developer entropy bytes,
three worker slots and supervisor slot 3. The magic selects six bounded byte
channels rather than four. Each channel retains its three-generation limit,
32-byte queue, 16-byte transfer bound, owner binding and consuming close behavior.
All older profiles retain their capacities, ABIs and completion markers.

Supervisor bootstrap registers match ABI 8 except RDI=9. Only the supervisor can
allocate channels or launch the third executable grant. Each paired launch
transfers one reader and one writer only after startup validation; rejected
startup preserves both endpoints. The fixture checks caller loss after transfer,
foreign worker access, full pool rejection, stale cleanup and two complete rounds
of replacement. Completion requires six reclaims, no admitted workers and no live
or buffered channels, then `AETHER NATIVE CONNECTIONS PASS`.

## Serial session profile (AENMX008 / ABI23)

This opt-in experiment composes the007 lifetime/observation mechanism with006
owner-only UART access. It preserves the24KiB owner,4088-byte stack, three children,
two pipes and fifteen task lifetimes. Parent/copied/replacement domains retain
stdio bindings and cannot access the UART grant directly. Existing envelope/ABI
pairs retain their behavior;008 is rejected when capacity is disabled and007 does
not gain UART access. See [the scoped startup contract](NATIVE-SHELL-STARTUP.md#real-serial-session-experiment--2026-09-29)
and [the producer evidence](evidence/serial-session-2026-09-29/README.md).
Independent consumption and SDK adoption remain separate from this private profile.

## Serial SESSION lifecycle profile (AENMX009 / ABI24)

This separately selected experimental producer combines008 SESSION/serial behavior
with the owner lifecycle operations in [NATIVE-INIT](NATIVE-INIT.md). Build with
`-Dnative-session-lifecycle=true` plus the complete SESSION closure: capacity,
scoped memory, process freeze/copy/exec, local runner, parent identity, public signal
actions and signal copy, single core/single context. `native-init-sustained` is
incompatible.009 without the selector, or a different envelope with it, rejects
before owner admission. The owner receives24; image/factory/channel grants and
worker bootstrap remain unchanged.

009 retains112-byte framing,80-byte entropy,24KiB owner/4088-byte stack, SESSION
IDs and fifteen task/channel lifetimes. It does not enable ABI22 typed IDs or
expand pipe/task/descriptor quotas. Healthy execution has no3000-tick deadline;
external test watchdogs still apply.0x2a000/1 use contextual owner clock grant e002
for snapshot/atomic compare-park;0x2a002 uses owner final-action grant f002. Return
values, reserved-field checks, wake hints and absolute deadlines match ABI22.
UART remains owner-only and cannot be transferred.0x20006 returns -38; quiescent
halt requires console closed, all workers reclaimed and channels/queues retired,
without fixed workload observation totals. Old profiles retain their finish rules.

Kernel-only qualification uses the private probe, not actual sys-init or dash.
Copy the frozen driver to a fresh packet so sealed evidence is never overwritten:

```sh
session_review=$(mktemp -d zig-out/session-lifecycle-review-XXXXXX)
cp docs/evidence/session-lifecycle-2026-10-03/run.py "$session_review/run.py"
python3 "$session_review/run.py" positive
```

[Evidence and before-code assessment](evidence/session-lifecycle-2026-10-03/README.md)
record the exact controls and remaining gaps. Actual consuming owner/SESSION loops,
matching SDK closure, independent review and complete R1 remain separate gates.

### Selected owner path and current idle limit

Compile the existing SESSION dispatcher with `--cfg pipeline_dash_parent --cfg
session_serial --cfg session_lifecycle` and its24KiB capacity linker to select009.
It launches one parent, drains real transport/dispatch/terminal progress before
compare-park and confirms child/pipe/channel/backing cleanup before closing UART
and requesting halt. It no longer publishes fixed workload observations or uses
three parents, iteration cutoffs or128/32-byte output observation admission limits
on this path. Old21/23 fixture paths retain their behavior and limits. Failure
retains unknown-effect resources and traps; it cannot masquerade as clean halt.
The kernel publishes009 cooperative-freeze transitions so parked queries can wake.

[Bounded native qualification](evidence/session-owner-lifecycle-2026-10-03/README.md)
uses a private Aether dispatcher and exact previously sealed worker ELFs. It is not
actual sys-init or a newly accepted userland runtime. A prompt with promptly supplied
commands passes; **healthy long prompt idle does not yet pass**. The frozen client
transport still polls for at most100000 attempts, then poisons the connection.
It can terminate the shell while the owner correctly retains a pending stdin read.
A reproducible private short-input check copies the historical driver to a new packet:

```sh
session_owner_review=$(mktemp -d zig-out/session-owner-review-XXXXXX)
cp docs/evidence/session-owner-lifecycle-2026-10-03/run.py "$session_owner_review/run.py"
python3 "$session_owner_review/run.py" short-session
```

### ABI24 endpoint wait (experimental `0x24004`)

[Producer review and evidence](evidence/session-channel-wait-2026-10-03/README.md)
adds a single-context wait on the caller's existing channel endpoint. RDI is the
exact held reader or writer capability; RSI/RDX/R10/R8/R9 must be zero. Only009
implements this operation; older profiles return ENOSYS (-38). No new grants,
worker UART/clock/factory rights, channel quotas or lifetimes are introduced.

A reader is ready when bytes are queued or the writer is closed. A writer is ready
when space exists or the reader is closed. Return0 is only a hint: retry the actual
read/write, retaining partial frame/byte offsets. Wait copies nothing and retains
no user pointers. Closure wakes the caller to observe EOF/EPIPE through read/write;
it does not itself report a byte count or fabricate a successful transfer.

Malformed reserved fields return EINVAL (-22) after endpoint validation. Stale,
closed, foreign or transferred-away authority returns EACCES (-13). An unmasked
nonignored pending signal returns EINTR (-4), without consuming or delivering it;
existing explicit signal processing remains required. Authority loss precedes
interruption, then readiness. Ignored/masked signals do not wake the caller, even
when exec retained a queued occurrence with a newly ignored disposition.

IF=0 spans the ready check, registration and scheduler exclusion. At most one
8-byte registration per domain; readiness scans are bounded by six domains/ten
channels. All blocked contexts use kernel HLT. Registration is revalidated against
holder/generation/stream/mask before selection and rotation, consumed once on wake,
and discarded on stop/terminal before backing reuse. There is no deadline, wait
set, automatic handler injection, SA_RESTART promise or multi-context/cross-core
wait support. A dead peer that retains its endpoint can leave a waiter blocked;
existing owner stop/cleanup authority resolves that lifecycle, not a new timeout.

A fresh private mechanism run (run only from a new evidence directory):

```sh
channel_wait_review=$(mktemp -d zig-out/channel-wait-review-XXXXXX)
cp docs/evidence/session-channel-wait-2026-10-03/run.py "$channel_wait_review/run.py"
python3 "$channel_wait_review/run.py" qualified
```

### Asynchronous child notification during wait

The [asynchronous child-notification witness](evidence/session-wait-notification-2026-10-03/README.md)
also qualifies SIGCHLD posted by an actual copied child's terminal event after its
parent parks. With `native-signal-suspend`, the existing generation-checked copy
relationship selects the parent; no signal-send grant is introduced. Unmasked
wait returns EINTR twice without dequeue/delivery. A masked parent remains parked
after child exit, accepts a real byte, then observes the retained signal when
unmasked. Installing ignore permits progress. Two parent/child generations reclaim
four tasks before authorized halt; this is a private mechanism result, not runtime
signal-policy or sys-init acceptance. Automatic delivery, wider schedules and the
explicit disabled-operation matrix remain open.

Run the private witness from a fresh evidence directory:

```sh
channel_notify_review=$(mktemp -d zig-out/channel-notify-review-XXXXXX)
cp docs/evidence/session-wait-notification-2026-10-03/run.py "$channel_notify_review/run.py"
python3 "$channel_notify_review/run.py" qualified
python3 "$channel_notify_review/run.py" negative-qualified
```

### Private wait-enabled dash composition

The [terminal/transfer race correction](evidence/session-poll-terminal-2026-10-03/README.md)
handles a peer exiting after `Session::poll` observes it alive but before the
subsequent transfer. Read EOF0 and write EPIPE-32 trigger a second observation of
the same held task. Only confirmed terminal state enters existing settlement;
EOF/EPIPE from a still-live peer remains an invariant failure. EAGAIN, other errors,
positive-count bounds, wait collection and reclaim prerequisites are unchanged.
No kernel/ABI/grant or runtime signal policy changes. Forced native read/write
windows distinguish the old failure, corrected settlement and live-peer denial.
The producer source patch is ready for sys-init's explicitly borrowed dispatcher;
its owned entry still needs matching consuming qualification. The original
uninstrumented failed call site is not claimed known from this test.

The [matched companion intake](evidence/abi24-companion-intake-2026-10-03/README.md)
now verifies userland's canonical009 runtime and sys-init's owned entry, with a
fresh delayed real-shell/cleanup/halt witness and wrong-ABI/busy-halt controls.
The normal immediate image reproduces a real dispatcher failure after the final
helper; a diagnostic-image pass does not establish its cause. Delivery is resolved,
composition acceptance remains open. Next test the terminal-observation/transfer
window identified in the packet's source review before changing the dispatcher.

[Matched private client qualification](evidence/session-client-wait-2026-10-03/README.md)
selects `-DSESSION_CHANNEL_WAIT` when compiling Aether's existing
`user/native-capacity/session-client.c`, alongside `SESSION_SERIAL`. The client
requires PIPELINE_STREAMS, probes009-only wait behavior before bootstrap, and
waits on the same endpoint after transport EAGAIN. It retains each partially
transferred frame's offset; wake is followed by an actual read/write rescan.
Other builds keep the old counter/yield path. This compile-time option is a private
fixture selection, not a published runtime/SDK profile or userland adoption.

Existing one-context RPC signal guards remain. Unexpected wait errors, including
EINTR, poison the synchronous channel and produce existing transport failure/EIO;
the client cannot safely restart an ambiguous partially transmitted request. No
POSIX EINTR/SA_RESTART or automatic handler-delivery claim follows from this change.

Real dash survives35 seconds of first-prompt idle and later delayed input, then
passes external execution, pipelines/substitution, persistent shell state/PID,
stderr and exit/ten-reclaim/authorized halt. Wide output passes separately. This
is an intermediate private shell demonstration: actual sys-init entry/policy,
userland's extracted runtime adoption/independent review, persistence/packages and
assembled R1 remain open.

Run in a new directory to preserve historical receipts:

```sh
client_wait_review=$(mktemp -d zig-out/client-wait-review-XXXXXX)
cp docs/evidence/session-client-wait-2026-10-03/{run.py,workers.py} "$client_wait_review/"
python3 "$client_wait_review/run.py" delayed
python3 -m unittest discover -s tests -p test_session_channel_wait.py
```

The driver verifies the sealed local SDK/libc/upstream objects before rebuilding
the private client. Host transport checks require pinned Clang21.1.8 and, on the
current macOS host, the installed SDK selected explicitly by `xcrun --show-sdk-path`.
That host SDK is a test-runner prerequisite, not native runtime input. Next hand off
matching sources/worker receipts to userland for canonical runtime adoption and
compose actual sys-init ownership before treating this as the product boot path.

## Session lifetime profile (AENMX007 / ABI21)

The [session admission contract](NATIVE-SHELL-STARTUP.md#aenmx007-admission-and-channel-integration--2026-09-24)
adds an explicit private profile with fifteen process/channel lifetimes. It retains
AENMX005's112-byte framing,80-byte entropy and24-KiB owner limit, five worker slots,
ten channels and existing scoped grants. Old004–006 still retire at three uses.
007 grants no UART capability or console operations. The capacity resource test
exercises two workers for fifteen generations and30 reclaims; it is not the
consumer's persistent-parent dash session. STATE records current qualification.
Higher-generation copied-child/pipe/dispatcher integration and consumer acceptance
remain required. No shared SDK, released standard or existing ABI is replaced.

## Workload and exact scope

The Rust broker owns a private request/reply pair for each of two strict-musl C
clients plus a private pair for the existing Rust file backend. Slot 1 runs the
backend; slots 0 and 2 are clients. Each client requests a fixed seed-file read.
Only the broker knows the backend root and open handle. This workload does not
expose the old raw file passthrough to clients. It also does not create inherited
open-file state or establish a production POSIX service.

Client requests are fixed 32-byte frames: little-endian u32 operation 1 followed
by 28 zero bytes. The connection selects the caller; there is no sender/owner
field. The broker keeps a separate partial-frame buffer and byte count for each
client, reads at most one native chunk per client per polling pass, and yields
between passes. Once a request is complete, it opens `hello.sh`, reads its first
16 bytes and closes the backend handle before replying with the file response.

The first client writes only eight request bytes, then waits. The second sends a
complete request, receives and validates actual file bytes, and marks itself
ready. Only then does the broker send the first client a 32-byte continuation
frame (u32 777, remaining bytes zero). That client supplies its remaining 24
zero bytes and receives its own file result. This test-only handshake proves that
an incomplete request does not prevent the other client completing file I/O.
Both clients exit 29; closing the backend input permits its exit 17. The broker
checks terminal results, closes its endpoints, reclaims all three and repeats
with fresh generations. Its immutable supervisor code is 3528 bytes in this run.

This demonstrates incremental request handling, not arbitrary slow-peer fairness.
Backend RPC and client reply transmission still use bounded synchronous loops.
A stalled backend or non-reading client can therefore fail this finite fixture.
General request cancellation, output buffering/backpressure, fairness under load,
partial-frame EOF recovery and sys-init service composition remain separate work.
No native protocol is claimed for inherited descriptor bootstrap yet.

## Acceptance and reproduction

```sh
python3 scripts/launch_smoke.py --connections \
  --libc-build /absolute/strict-musl-sdk \
  --tools-lock /absolute/compiler-tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

Six cases:

| Case | Required observation |
| --- | --- |
| positive | Two generations, terminal order 2/0/1 per round, client exits 29, backend exits 17, supervisor 100/reclaimed 6 and CONNECTIONS PASS |
| small-pool | Restrict only the new profile to four channels; exact supervisor 950/reclaimed 0 and profile rejection |
| reserved | Nonzero second reserved word rejects envelope before worker admission |
| bad-third-machine | Wrong third ELF architecture rejects before worker admission |
| reject-partial | Deliberately reject a partial frame; exact supervisor 959/reclaimed 0 and profile rejection |
| wrong-data | Corrupt a delivered seed byte; client 2 exits 245 and broker rejects at 960/reclaimed 0 |

Kernel host tests validate the new envelope branch. Existing native profiles,
memory, frozen legacy consumer and default two-core framebuffer checks remain
regressions. Original startup clients without a TLS segment were rejected by the
existing strict ELF validator; the corrected clients explicitly exercise TLS.
No loader rule was relaxed. Neither failed drafts nor timeouts count as passing
controls. [Pinned evidence](evidence/native-connections-2026-09-05/README.md).

## Handoff

Userland can independently replace either client against this completed transport
contract. This is Aether producer evidence, not an independent userland result.
Pkg-mgr must add explicit AENMX001 transport only when it consumes a matching
artifact set; existing receipts do not silently acquire six-channel support.
Sys-init's SI-04 corrected pin and ABI-6 consuming work remain separate.

The next UP-01 layer is the single user-space open-file owner from the
[ownership review](NATIVE-INHERITANCE-REVIEW.md): agreed bootstrap, restricted
alias admission, shared positions, rollback and real final-close handling.
Do not infer descriptor inheritance, fork/exec, shell pipelines, persistent
storage or broad supervisor recovery from this connection test.

## Cooperating process freeze slice — 2026-09-09

The connections suite also selects six opt-in freeze cases. Exact scalar ABI,
authority, sequence/cancellation errors and implementation selection are in
[NATIVE-SHELL-STARTUP](NATIVE-SHELL-STARTUP.md#freeze-boundary-implementation-selection--2026-09-09).
The new `native-process-freeze` build flag leaves other profiles unchanged. These
cases use existing image grants, lifecycle handles and connection creation; no
copy/exec operation or POSIX fork success is implemented.

`freeze-positive` cancels two successive freezes per parent across two generations,
checks source TLS/stack continuity, rejects stale tokens and foreign/malformed
handles and requires parent/dummy statuses29 in slot order0,1,2. `freeze-stop`
stops the pending parent, requires queried143/kind3 and invalidated cancellation,
then reclaims and repeats with a fresh handle; only dummy slots1,2 produce normal
terminal records. `freeze-disabled` requires ENOSYS from all three new operations;
`freeze-unsupported` enables the signal-action/runner-local profile and requires ENOTSUP from
self-freeze, using slots0,1 and the existing four-reclaim oracle. The other three
positives require six reclaims. All require no live channels. Threads remain
rejected at the existing connections bootstrap boundary, not a live freeze case.
`freeze-skip` deliberately omits parking and must reject owner1710 with no reclaims;
`freeze-token` deliberately accepts an obsolete request and must reject owner1712
with no reclaims. A boot error, unrelated panic or timeout is not either rejection.

The existing `--connections` command runs this complete selection with its older
six cases. Scope remains BSP-only and cooperating single-context workers. Pending
signal/thread copying, indefinite orphan recovery, process memory copying and
libc rebinding remain subsequent work. New C uses pinned clang-format21.1.8 and
the reviewed configuration; Rust uses edition2024. No new FFI convention is added.

## Private copied continuation — 2026-09-09

Five additional connections cases use native-process-copy, native-process-freeze
and native-memory. Exact operation0x23006 and the private return binding are in
[NATIVE-SHELL-STARTUP](NATIVE-SHELL-STARTUP.md#private-copycommit-implementation-selection--2026-09-09).
`copy-positive` resumes source0 and a copied child2 with distinct results, actual
PID/parent identity and fresh child grants. It preserves TLS/stack/FX state, tests
private anonymous writes in both domains, restores an inaccessible page and checks
an unmapped hole can be reused as zeroed backing. Independent endpoint traffic
coordinates the checks; this is not an inherited POSIX descriptor table.

An admitted terminal dummy1 exercises occupied-slot rejection before copy. Normal
terminal order is dummy1=29, child2=72, parent0=71 across two generations, then six
reclaims. Preflight checks include factory, source lifetime, sequence, slot,
endpoint direction/ownership, distinct channels and queued input rejection.
`copy-rollback` injects failure after staging and requires source still frozen,
endpoints still supervisor-owned and no consumed child generation. It cancels the
parent and launches a fresh dummy in slot2: terminal order1=29,0=71,2=29, six reclaims.
`copy-share` deliberately aliases writable anonymous backing and must expose
parent215/owner1821; `copy-anonymous` drops anonymous metadata and must expose
child218/owner1820; both require zero reclaims. `copy-zero` skips failed-copy zeroing
and must fail the emergency invariant `native copy rollback not zeroed`.

These cases extend the existing suite to17; no new CLI entry point is added. All
other profiles remain selected explicitly. Public fork, SDK cached-grant rebinding,
exec/CLOEXEC, signals, descriptor inheritance and wait remain unimplemented here.
The copied auxv intentionally retains old grant integers, whose use is denied;
only the native fixture consumes the explicitly returned child grant binding.


## Copy-profile thread identity — 2026-09-10

The copy profile's set_tid_address returns its generation-bound process identity
for single-context workers, preserving legacy/threaded behavior. The existing
copy-positive/rollback witnesses also check libc startup gettid/getpid agreement,
independent clear-TID registration, rejected replacement preserving the parent pin,
and successful parent/child registration returning their respective identities.
The copied libc TID remains the parent's until a future SDK hook rebinds it.
The new copy-slot-tid control deliberately returns slot identity: parent230,
owner1800 and zero reclaims are mandatory. This brings connections to18 cases.
No public fork, libc cache update or descriptor inheritance is claimed.


## Local libc child rebinding — 2026-09-10

Four additional cases bring connections to22. copy-rebind links a local helper
against receipt-pinned musl private headers, updates the three known auxv grants,
fixture endpoint variables and pthread TID after validation, and exercises public
getauxval/gettid and mmap/mprotect/munmap. Parent state remains unchanged across
two generations and six reclaims. Invalid old memory and reversed endpoint roles
reject without cache changes. copy-rebind-aux/tid/channel deliberately omit one
store update and require child240/241/242 respectively, owner1820 and zero reclaims.
Existing18 cases retain their oracles. This is a conformance helper for raw
connections, not a public SDK fork hook or inherited command descriptor support.
The archive pin and extracted private headers are verified; no kernel change.


## First inherited-stream witness — 2026-09-10

Three additional cases bring connections to 25. `copy-inherit` uses the real
startup descriptor adapter, a separate Rust stream backend and a copied child.
Both wrappers wait for owner completion after validated child rebinding. The
owner shares one input position across the two connection-local aliases; each
process retains a private 16-FD table and local duplicate counts. FD 10 inherits
CLOEXEC, and clearing the child's flag leaves the parent's flag set. Parent reads
a, child b, parent c; after all parent aliases close, child reads d and then e
through FD 10 after locally closing FD 0. Each backend binding closes once, when
its last process holder releases it.

Exact terminal order is source slot0=71, child slot2=72, backend slot1=17 in each
of two generations, then owner100 and six reclaims. The existing C bridge maps
Rust backend success0 to exit17. `copy-inherit-offset` deliberately gives the
child a private position and must reject owner1903 on its b read.
`copy-inherit-close` prematurely closes the backend on parent release and must
reject owner1952 on the child's next read. Both require zero reclaims.

These cases compose existing native-process-copy/freezing/memory and runner-local
mask guards. The kernel completion check preserves six reclaims for copy even
with runner-local enabled; no new operation, authority or resource pool is added.
The exact local records and bounded scope are in
[NATIVE-SHELL-STARTUP](NATIVE-SHELL-STARTUP.md#first-inherited-stream-witness-implementation--2026-09-10).
This first witness does not complete malformed-record, publication/rollback,
shared-poison or abnormal-stop coverage, an installed SDK fork hook, exec/wait,
pipelines or full dash. Those remain required before consumer handoff.

## Inherited-stream publication recovery — 2026-09-10

Seven additional cases bring connections to32. `copy-inherit-receipt` corrupts
reserved byte31 of the child receipt; `copy-inherit-completion` sends invalid
completion opcode68 after the valid readiness acknowledgment. Both require child251
with no application request on its channel, followed by parent73 and backend17.
`copy-inherit-stop` withholds the receipt, stops the copied worker and queries exact
status143/kind3 before removing its holders. Forced stop emits no normal child
terminal line; only parent73/backend17 appear in that case. Each positive repeats
two generations and requires six reclaims, unchanged parent FD10/CLOEXEC, reads a/b
from the original position and exactly three final backend closes.

Before holder removal, the waiting parent answers probe69 with reply70, then waits
for failure68. A skipped gate sends application I/O instead and rejects1962.
`copy-inherit-receipt-skip`, `copy-inherit-completion-skip`,
`copy-inherit-parent-skip` and `copy-inherit-stop-skip` deliberately omit receipt
validation, the child gate, the parent gate and native stop, respectively; exact
owner failures1961/1963/1962/1964 and zero reclaims are required. These are local
conformance records defined in
[NATIVE-SHELL-STARTUP](NATIVE-SHELL-STARTUP.md#inherited-stream-publication-recovery-selection--2026-09-10).
No public fork or errno contract is adopted. Pre-copy rollback, arbitrary table
validation, partial/missing messages, shared backend uncertainty and signal-aware
preparation remain open. Kernel, SDK, resource pools and released pins are unchanged.

## Inherited-stream pre-copy rollback — 2026-09-10

Four additional cases extend connections to36. `copy-inherit-rollback` uses the
existing native-copy-fail-stage flag and requires ENOMEM with the source still
frozen, the destination vacant and all staged endpoints still supervisor-owned.
Closing the four ends must remove access. Stale cancellation cannot wake the source;
matching cancellation returns EAGAIN to the rollback client, which waits for failure
notification and preserves FD10/CLOEXEC and reads a/b before final closure.
A fresh backend then occupies slot2 at the unconsumed generation. Normal terminal
order is parent0=73, backend1=17, replacement2=17 across two generations, six reclaims.

The rollback-leak/close/cancel variants omit one staged endpoint close, close a
still-held backend input or omit matching cancellation. Exact owner1972/1952/1973
and zero reclaims distinguish them from watchdog or generic panic failures.
The existing eight-KiB owner and six-channel/three-generation limits remain.
See the [pre-code selection](NATIVE-SHELL-STARTUP.md#inherited-stream-pre-copy-rollback-selection--2026-09-10)
for scope and ordering. This adds no public fork/errno ABI, generalized rollback,
signal-aware preparation or shared uncertainty recovery.

## Incomplete child publication — 2026-09-10

Six cases extend connections to42. `copy-inherit-incomplete-receipt-missing` and
`receipt-partial` withhold all or half of the32-byte binding receipt; the normal
child remains in its reader. `ack-missing` and `ack-partial` deliberately stall
the child after zero or16 acknowledgment bytes. The readiness reader preserves
actual byte count and requires all32 bytes within256 read attempts. Timeout is
not stop: the owner then invokes native stop and queries exact143/kind3 before
releasing child holders and using the existing parent recovery path.

Each positive requires parent0=73/backend1=17 (no normal forced-child terminal
line), two generations and six reclaims, with original FD10/CLOEXEC and reads a/b.
`copy-inherit-incomplete-ack-pad` deliberately treats the missing zero tail as
received and must reject owner1982. `copy-inherit-incomplete-stop-skip` must reject
owner1981 while the child remains active. Both require zero reclaims. Unexpected
byte counts/classification reject1980. External watchdog failure is never a pass.
The [selection](NATIVE-SHELL-STARTUP.md#incomplete-child-publication-selection--2026-09-10)
defines the fixture budget and deliberately stalled clients. Incomplete final
completion, parent snapshots, unrelated terminal states and backend uncertainty
remain outside this slice; no wall-clock deadline or public SDK ABI is claimed.

## Shared inherited backend uncertainty — 2026-09-10

The connections suite now selects45 cases. `copy-inherit-uncertain` receives a
complete malformed first read reply from the real backend. One owner-held latch
blocks every subsequent backend exchange across both client connections. FD0/10
reads return complete EIO with untouched buffers; clients retain private flags and
consume each descriptor close (last binding close reports EIO). No unknown offset
is advanced and no backend close is sent. Source74/child75 and confirmed backend
stop143/kind3 precede six reclaims across two generations.

`copy-inherit-uncertain-alias` deliberately bypasses the shared latch for the child:
a successful backend read violates the required EIO, producing child254/owner1992
before reclaim. `copy-inherit-uncertain-stop` omits stop and rejects owner1993 with
zero reclaims. Complete EIO keeps local transport usable for alias release; it does
not assert the backend operation had no effect. The conservative whole-service
block is scoped to the existing three-stream fixture. Missing/partial backend
replies, uncertain writes/closes and general service recovery remain future work.

## Missing inherited backend replies — 2026-09-10

The connections suite selects 49 cases. `copy-inherit-uncertain-missing` and
`copy-inherit-uncertain-partial` use a live backend that sends zero or 17 bytes,
then yields without completing the reply. The shared bounded record reader requires
all 32 bytes within 256 read attempts. It preserves the received count and marks
both clients' aliases uncertain on incomplete input. This is an attempt budget,
not a real-time deadline. Existing EIO/buffer/descriptor/stop/reuse oracles apply:
source74/child75, confirmed backend stop143/kind3, six reclaims over two generations.

The 17-byte prefix contains count1 and input byte a, so falsely padding its tail
could expose a successful read. `copy-inherit-uncertain-partial-pad` deliberately
does so and requires source254/owner1992 before reclaim. The missing-stop variant
requires owner1993 with zero reclaims. No unknown operation is retried or backend
close fabricated. Uncertain writes/final closes remain separate coverage.

## Uncertain inherited writes and final closes — 2026-09-10

The suite selects 56 cases. Write uncertainty follows a real stdout append and
blocks both clients' later writes with EIO. Final-close uncertainty occurs only
when the child's input holder is last: parent closes succeed without backend
traffic; child closes consume local aliases with EIO. Source74/child75 (writes) or
source76/child77 (closes), confirmed backend stop143/kind3 and six reclaims over two
generations are required. Repeated closes require EBADF and private flags survive.

Write/close replay controls require backend124 then owner1994/1995 before reclaim.
False close success requires child255/owner1996; both omitted-stop controls require
owner1993 and zero reclaims. The backend rejects later traffic after its injected
malformed reply. These cover selected completed effects with invalid replies, not
exactly-once operation or the missing/partial write/close matrix. No kernel or
public SDK contract changes are implied.

## Incomplete inherited effect replies — 2026-09-10

The suite selects 64 cases. Missing/17-byte replies after writes or final closes
use the existing shared block and confirmed-stop cleanup. The owner retains exact
received counts and requires all 32 bytes; a zero-filled partial close reply is
not success. Source74/child75 (writes), source76/child77 (closes), private flags,
consuming local closes and six reclaims over two generations remain required.

Write partial-padding requires source254/owner1992, close partial-padding requires
child255/owner1996, and both missing-reply omitted-stop controls require owner1993.
All require zero reclaims. No retry, guessed offset or fabricated close confirmation
is permitted. The attempt bound remains 256 reads with EAGAIN yields, not a real-time
deadline. Installed SDK and general process adoption remain separate.

## Incomplete final publication — 2026-09-10

The suite selects 72 cases. After child readiness, `copy-inherit-final-*` publishes
complete success to one client and zero/16 bytes to the other. No application request
may come from the incomplete client within 256 read attempts. Both clients must be
confirmed stopped143/kind3 before the complete peer's queued request is drained or
holders are removed. Both channels must then report EOF. The backend saw no
application operation; its three idle handles close normally, producing backend17
and six reclaims over two generations. This contains a partially published pair; it
does not pretend already observed success can be rolled back.

Parent/child padding controls reject owner2001 on application traffic. Omitted parent
or child stop rejects2002/2003 before discard/reclaim. All controls require zero
reclaims. The attempt bound is not a real-time deadline. This producer-fixture policy
is separate from installed SDK fork semantics and sys-init supervision policy.

## Client descriptor preparation — 2026-09-10

The suite selects 83 cases. A client validator checks its 16-slot table and three
admitted bindings before sending the plan or freezing. Canonical fields, duplicate
counts, live bits, exact roles/rights/lifetime refs and unpoisoned initialized
transport are required. Owner-side exact snapshot validation remains unchanged.
Nine rejected preparations require source78/backend17, empty source traffic, vacant
child identity, both spare channel slots available, and six reclaims over three
generations. No child is admitted. Skipping the local gate exposes plan bytes and
rejects2010; leaking a reservation rejects source78/owner2011 before reclaim.
This is fixture preparation validation, not arbitrary FD-set or signal-atomic
copy support. SDK adoption and companion policy remain separate.

## Masked preparation and restoration — 2026-09-10

The suite selects 91 cases. The client holds the existing all-maskable-signals guard
from descriptor validation through plan/freeze/rebinding/final completion. Private
saved mask state is copied with the client and restored before application I/O and
on returning errors. Mask bits are checked at held/restored boundaries; existing
nested FD guards preserve them. Forced-stopped clients do not resume.

Nonzero SIGUSR1/SIGUSR2 initial-mask cases cover success, preparation rejection,
pre-copy rollback and bad-receipt recovery. Omitted entry/rejection restoration
requires source79/owner2010; omitted parent/child restoration requires that client's
79/owner1950 before application traffic or reclaim. All prior lifecycle counts remain.
The kernel still rejects copying with custom signal actions or threads: these are
mask-state witnesses, not handler-capable fork, pending-signal or full SDK acceptance.

## Explicit native signal-copy experiment — 2026-09-10

The suite selects 98 cases. `native-copy-signals` requires private signal actions,
process-copy and single-context execution; ordinary action profiles still reject
freeze/copy. The opt-in copies validated dispositions and execution mask, starts
child pending state empty and preserves parent pending state before publication.
The raw client queries DFL/IGN/custom records (including signal64), coalesces a
masked post, checks child absence/parent delivery and private child mutation, then
posts to its inherited handler. Two generations retain the raw copy lifecycle.
One case runs the complete copied continuation inside a handler and returns through
both inherited stack restorers with the original mask. Injected staging failure
retains parent signal state through cancellation and destination-generation reuse.

Disabled opt-in rejects source246/owner1800. Deliberately dropped records reject
child247/owner1820; duplicated pending bits child248/owner1820; cleared parent pending
source248/owner1821. Each requires exact terminal ordering and zero reclaims.
The new experiment is not installed SDK fork support. Corrupted inherited return,
nonlocal escape, guarded descriptor publication and consumer acceptance remain
separate qualification. Existing kernel authority, ordinary action profile gates,
thread exclusion and released pins remain unchanged.

## Copied-handler return and escape — 2026-09-10

The suite selects 104 cases. Handler-copy checks R12 and XMM14's low 64 bits after
return through each copied restorer; the handler deliberately clears live XMM14.
The child alone corrupts its inherited frame's reserved byte, requires rejected
sigreturn (-22) with unchanged current mask, repairs it and returns normally.
Parent return remains valid. A separate sigsetjmp/siglongjmp case escapes both
copied handlers, restores the original mask and permits another self-delivery.

Omitted corruption accepts the frame without the required rejection witness and
fails child250/owner1820. Corrupted saved R12/XMM14 produce the same pair. Omitting
nonlocal mask restoration fails child249/owner1820. All new controls require zero
reclaims; positives retain two generations and six reclaims. This is selected
register/frame/escape evidence, not a full FP matrix or SDK fork adoption. Kernel,
backend and shared adapters remain unchanged. Guarded descriptor-publication
composition remains subsequent work.

## Signal/descriptor composition — 2026-09-10

The suite selects 110 cases. Explicit signal-copy support now composes with the
inherited-stream fixture: parent pending delivery and a fresh child post remain
masked until final completion. The handler checks publication, auxv endpoints,
cached/kernel identity, current references/rights and private FD10 flags/counts,
then duplicates into FD11 and closes the local duplicate without backend I/O.
Initial mask16 and errno survive delivery and nested descriptor guards.

Success and pre-copy rollback retain existing lifecycles and six reclaims. Early
parent restoration or stale child reference/missing child post requires client79/
owner1950 before reclaim. Kernel, owner, backend and shared adapters are unchanged.
Live-handler composition with rejected preparation or malformed completion, and
installed SDK fork/exec/wait adoption, remain subsequent work.

A corrupted decoded parent completion keeps the handler gate closed and rejects
source79/owner1950 before reclaim. Only outcomes67/68 authorize the parent callback;
the child gate follows its existing exact67 check. This is completion-validity
coverage, not full malformed-wire recovery with handlers.

## Live-handler returning rejection — 2026-09-10

The suite selects 118 cases. Known unpublished preparation78 and child receipt/
completion251 returns select a private observer before mask restoration. It records
one delivery without accessing descriptors; mask, errno and zero FD-operation count
are checked before terminal publication. Recovered parents retain the normal handler
and local dup/close path. This is fixture behavior, not enforcement against arbitrary
user callbacks. Preparation preserves three source78/backend17 cycles and six reclaims;
malformed child records preserve child251/parent73/backend17 and six reclaims.

Omitting abort selection or actually querying FD10 from the aborted callback rejects
source79/owner2010 or child79/owner1960, with zero reclaims. Partial-record forced-stop
containment with live handlers remains subsequent work. Kernel, owner, backend,
shared adapters, native wire contracts and installed SDK support are unchanged.

### Live-handler incomplete publication — 2026-09-10

The connections suite composes live copied handlers with four missing/partial
receipt/readiness cases and four final-completion containment cases. Readiness
failure confirms child stop, then recovers the parent through its checked callback,
saved mask/errno and descriptor duplication checks. Final completion confirms both
stops before draining the complete peer's queued request and releasing backend
handles. Each positive retains two generations and six reclaims. The complete peer
may execute its callback; silence is not an independent witness of handler absence.

Six controls reject zero-padding or omitted stops with exact owner results1982,
1981,2001,2002 or2003 and zero reclaims. The full invocation above runs these as
part of132 connections cases. No ABI, owner, backend, quota or SDK contract changes.
[Evidence](evidence/signal-incomplete-2026-09-10/README.md) records final artifacts
and limits. Installed SDK fork/exec/wait and independent dash acceptance remain open.

### Source-built public fork — 2026-09-10

The connections suite now builds fork/_Fork from the verified musl archive in
private output. Only the _Fork syscall site calls the native staging hook; upstream
fork orchestration, child repair and mask/error unwinding remain. The rebind helper's
new compile-time variant updates auxv/endpoints while leaving TID repair to libc.
No installed SDK or sibling source is patched.

Five cases add actual parent/child public fork returns, inherited CLOEXEC and shared
reads, cancellation/EAGAIN recovery and preparation/ENOTSUP refusal. Positives retain
six reclaims. Missing child repair and premature CLOEXEC clearing require child80/
owner1950 with zero reclaims. Full invocation above selects137 connections cases.
The first three attempts failed at compilation and are retained with sources and
artifacts in the [evidence](evidence/public-fork-2026-09-10/README.md).

This first call-path witness verifies mask16, errno, cached/kernel identity, private
TLS/data and backend shared offsets. Live-handler/atfork-callback composition,
exhaustive admission/error cases, wait/exec and independent SDK/dash acceptance
remain open. It does not enable native vfork or establish full POSIX fork support.

### Public fork live callbacks — 2026-09-10

Six more cases compose the actual SDK pthread_atfork implementation with native
signal delivery through public fork. Two registrations require reverse preparation
and forward parent/child callbacks. The private trace witnesses signal delivery
after staging completion and libc TID repair, before post callbacks on this pinned
musl implementation. Handlers check rebound endpoints/references, inherited CLOEXEC
and private FD counts; callbacks check mask16 and identity. Both preserve errno.
Parent posts coalesce while masked; the child receives its own fresh post.

Success, rollback and preparation refusal retain six reclaims. Reversed registration,
omitted child post and omitted child repair require client81/owner1950 and zero
reclaims. The full suite now selects143 connections cases. Linked symbol provenance
and [evidence](evidence/public-fork-callbacks-2026-09-10/README.md) bind actual musl
dispatch and allocation. Registration allocates before fork using the existing
native allocator; callbacks and staging introduce no allocations. Previous pending-
copy controls remain separate evidence for empty child pending state.

No installed SDK, kernel, owner, backend, shared adapter, resource limit or pin
changed. Callback delivery timing is an observation of this candidate, not a portable
libc ordering guarantee. Arbitrary callbacks, contention, recursive/threaded fork,
remaining admission/error cases, wait/exec and consumer acceptance remain open.

### Public waitpid retained result — 2026-09-10

Four cases extend the public fork candidate with privately source-built waitpid.
The [wire/adapter selection](NATIVE-SHELL-STARTUP.md#public-wait-first-execution-selection--2026-09-10)
defines connection-owned peek80/acknowledge81, PID/-1, options0/WNOHANG and exact
reply/body bounds. Retention is independent of stream descriptors: the parent
closes them before pending observation and later collection. Actual child exit72
is encoded only after native terminal observation; acknowledgment consumes the
result separately from resource reclaim.

Status delivery uses an existing native checked four-byte channel read directly to
the caller's output. Unmapped output returns EFAULT; the adapter drains the body
locally without acknowledging, permitting a later successful wait. NULL status
is tested as explicit discard. Wrong PID/options and pending replies leave the
sentinel unchanged. A post-collection peek returns ECHILD. Both normal and NULL
cases repeat over two generations with child72/parent71/backend17 and six reclaims.
Wrong-status and premature-consumption controls require parent82/owner1950 and zero
reclaims. Full invocation selects147 connections cases.

[Evidence](evidence/public-wait-2026-09-10/README.md) retains the initial compile
failure, corrected source build, target results and libc entry-point provenance.
The adapter masks signals across the exchange and explicitly remains outside
cancellation, EINTR/SIGCHLD, wait4/rusage, non-normal termination and general lost/
partial-reply recovery qualification. Lost acknowledgment remains an unresolved
outcome; no transparent retry or exactly-once delivery claim. Kernel, siblings,
installed SDK and release pins are unchanged; independent userland intake remains open.

### Retained wait causes — 2026-09-10

Five cases qualify normal exit134, actual #UD and actual default SIGTERM death after
child stream closure. Native records retain kind1/detail134, kind2/detail134 and
kind4/detail15 respectively. The bounded wait translator emits134<<8, SIGILL4 and
SIGTERM15; fault/signal words have no core bit. It does not turn all native details
into exit codes or infer an arbitrary signal from an exception vector. Other causes
remain unsupported in this candidate.

All three positives repeat pending/PID/options/EFAULT/retained/repeat checks over
two generations, parent71/backend17 and six reclaims. Encoding fault or signal as
normal exit requires parent82/owner1950 and zero reclaims. Full invocation selects152
connections cases. [Evidence](evidence/public-wait-causes-2026-09-10/README.md)
retains actual cause records and precise status macros. No early-death cleanup,
core dumping, SIGCHLD/EINTR, other signals/faults or reply recovery is implied.
Kernel, backend, SDK and pins are unchanged; wait4/wait3 intake remains open.

### Retained wait transport failures — 2026-09-10

Seven cases extend the full suite to159: missing/16-byte positive headers, a two-byte
status body, lost/malformed ACK replies, and replay/false-success controls. Closing
the reply endpoint makes truncation deterministic. Every positive checks EIO, mask
restoration, exact permitted output effects and a second local EIO with no traffic.
Unacknowledged results remain retained; a lost or malformed ACK reply leaves the
owner's result consumed. No transparent replay or exactly-once API promise follows.
Partial status bytes may have been written even when the call fails.

The owner observes parent71/child72 and no extra request, then backend17 and six
reclaims across two generations. Bypassing poison requires owner2024; accepting a
bad ACK requires parent82/owner2023, both before reclaim. [Evidence](evidence/public-wait-failures-2026-09-10/README.md)
retains full native receipts, source/artifact identity and older-profile comparison.
This qualifies EOF/truncation, not indefinite live-peer loss or reconnection. Actual
wait4/wait3, cancellation/interruption, exec and independent SDK/dash intake remain
open. The kernel, installed SDK and released pins are unchanged.

### Public wait4/wait3 candidate — 2026-09-10

The isolated build now links upstream musl1.2.6 wait3.c unchanged into a narrowly
adapted wait4.c: non-NULL rusage rejects ENOTSUP at entry, and NULL-rusage waiting
uses the existing retained-result adapter with musl errno conversion. Valid sentinel
and invalid-address usage pointers through both APIs leave status/usage unchanged
and send no request. Accounting is unavailable; zeros are not reported as measurements.

Five cases extend full connections to164. Public wait4 covers specific PID pending,
error, EFAULT/retry and repeated collection checks; wait3 directly covers -1 retained
collection, actual #UD/SIGILL and malformed-ACK EIO. The latter retains mask/poison
and no-replay behavior. Four positives repeat two generations/six reclaims; omitting
the usage gate requires parent82/owner1950 with zero reclaims. The existing waitpid
profiles remain unchanged. [Evidence](evidence/public-wait34-2026-09-10/README.md)
identifies linked upstream objects and the selected dash call site. This is a libc
entry-point witness, not execution of dash's waitproc/sigsuspend loop. Installed SDK,
kernel and owner are unchanged; full dash, accounting, interruption/cancellation,
SIGCHLD and independent acceptance remain open. Transactional exec is next.

### Native exec image gate — 2026-09-10

Four cases extend the suite to168. A frozen original client survives rejected image,
argument, pointer and freeze-token requests and cancellation with its old TLS/stack
cookies intact. A second freeze commits a distinct replacement ELF under the same
PID/parent and retained endpoint grants. Query identifies the committed image while
it stays parked across yields; cancellation and stale publication reject. Matching
publication runs the new argc/env/TLS checks and exits61 instead of the old client's29.
Two generations plus unrelated peer29 launches reclaim six resources. Early release,
token-bypass and unpublished-copy controls require owner2031/2032/2035 with zero
reclaims. The copy probe supplies valid fresh endpoints and a free destination slot;
endpoint allocation and cleanup failures use a distinct owner2036 result.

The [native contract](NATIVE-C.md#native-exec-image-gate--2026-09-10) and
[evidence](evidence/native-exec-gate-2026-09-10/README.md) distinguish image replacement
from Unix descriptor/CLOEXEC and service reply-loss handling. Broader command and
M4 regression results are retained because native mapping/dispatch code changed.
This is an opt-in producer experiment, not full execve or companion acceptance.

### Native exec descriptor composition — 2026-09-10

Three cases extend connections to171. The actual Rust owner uses `exec_fds::prepare`
on the checked64-byte C table and local counts. FD0/10 share binding0; FD10 and FD1
are CLOEXEC. Rejected image admission leaves both flags and the next input byte
unchanged. After known commit, binding1's exact backend-close success precedes
kernel publication. The replacement receives the existing bootstrap plus64-byte
survivor table, validates it before application I/O, installs FD0/2, rejects FD1/10
and reads c after the original image consumed a/b. Two generations reclaim six
domains, including a separate backend peer. The peer does not share open descriptions.

The32-byte channel cannot hold the complete bootstrap while parked; publication
releases only the trusted startup receiver, and table validation gates application
I/O. This does not yet qualify incomplete-bootstrap recovery. Mutations retaining
the old table require client216/owner2040; resetting the offset requires owner1903,
both before reclaim. [Evidence](evidence/exec-streams-2026-09-10/README.md) retains all
attempts and the complete connections/launch suites. No new native ABI is allocated.
Unknown close/commit outcomes, cross-process shared holders, public execve and
independent consumer acceptance remain open.

### Exec close-reply containment — 2026-09-10

Four cases extend connections to175. After committing a replacement but before
publication, the final CLOEXEC close backend returns no bytes or17 bytes and remains
alive. The Rust owner observes the incomplete32-byte record, confirms the pending
commit/freeze identity and stops all three fixture domains. Each exact lifecycle
handle must retain kind3/detail144 before any endpoint closure/reclaim. Two generations
reclaim six domains; partial response/peer bootstrap bytes are discarded only after
confirmed stop. No close replay or old-image cancellation occurs.

Forced stops emit no `NATIVE terminal` lines. The owner checks retained terminal
records directly; the harness demands no spontaneous exit/fault lines and exactly
six reclaims. A padding control requires owner2050 and an omitted source-stop
control requires2051, both before reclaim. [Evidence](evidence/exec-close-containment-2026-09-10/README.md)
preserves the initial incorrect log oracle and the final complete suites. These
fixed RAM backends have no external persistent authority; this is not generalized
backend recovery, shared-holder preservation or bootstrap-delivery containment.

### Exec bootstrap-stall containment — 2026-09-10

Six cases extend connections to181. After known commit and final-close success,
kernel publication releases the startup receiver. The owner stalls before/after16
bytes of the128-byte bootstrap or before/after16 bytes of the64-byte table, with the
writer still open. Across256 bounded polls it must observe no application request,
then verify the live source and matching published commit. All source/backend/peer
terminal records must confirm stop before endpoint closure/reclaim. Each positive
repeats two generations/six reclaims; no spontaneous terminal lines are accepted.

The C padding mutation consumes16 table bytes into its zeroed64-byte record; these
bytes contain all nonzero survivor entries. It reaches application read, which the
owner rejects at2060 before forwarding I/O or reclaiming. Omitted source stop rejects
2051. [Evidence](evidence/exec-bootstrap-stalls-2026-09-10/README.md) retains complete
suites, exact controls and the disk/cache infrastructure failures. This covers four
stalled-delivery boundaries, not EOF, malformed records or arbitrary hostile clients.
Kernel execution is distinct from complete startup/application readiness.


## Exec bootstrap rejection cleanup — 2026-09-10

The connections profile now qualifies EOF at0/16 bytes of the128-byte bootstrap
or64-byte survivor table, a malformed32-byte bootstrap header and a full survivor
table with reserved byte3 set. Bootstrap/EOF cases terminate the source at215;
the malformed table terminates at216. The owner requires no application request
and the exact retained source result before stopping backend/peer. Both forced
stops must be observed as raw terminal144/kind3 before endpoint closure/reclaim.
EOF cases have already closed the writer; cleanup closes it only once. The source
terminates itself and is not counted as a forced stop. Two generations reclaim six.

A table-validation bypass reaches read(0) and rejects at owner2070 with zero
reclaims. Omitting backend stop rejects2072 with zero reclaims. Forced backend
stops do not emit spontaneous terminal log lines; the oracle checks their retained
state in the owner and the exact source exit lines in the harness.

Qualification also found an older inheritance rejection race: application traffic
could arrive between an empty queue read and terminal observation. After confirmed
termination, the owner now requires actual EOF before accepting rejection. This
keeps the existing completion-skip control strict at1963 with zero reclaims.

[Evidence](evidence/exec-bootstrap-rejection-2026-09-10/README.md) records the full189
connections and five launch cases, host checks and retained failed attempts. This
remains a fixed RAM backend experiment; persistent recovery, cross-process shared
holders, unknown commit replies and public execve/consumer acceptance are separate.


## Exec shared-holder preservation — 2026-09-10

The exec-streams-shared case admits the replacement ELF independently as a peer in
slot2, alongside the source and one backend. Both private connections use the existing
0x76-prefixed local reference format. Connection selection identifies the caller. Backend
handles remain owner-private. Both connection records point to the same three
open-file records and the same input position. This admission is not public fork.

The existing descriptor plan removes only the source's local CLOEXEC holder.
The source reads a/b before exec and c after it, then closes its surviving input
and stderr descriptors and exits62. Its removal cannot close a record still held
by the peer. That peer reads d and writes z to stdout; the owner verifies both
an exact one-byte write receipt and a backend readback. Only the peer's subsequent
three closes cause backend close operations. Final acceptance requires both holder
rows empty, position4, exactly three confirmed backend closes per generation,
source62/peer63/backend17 in order, and six domain reclaims across two generations.

The exec-streams-shared-close control deliberately closes stdout during the
source's CLOEXEC removal; the peer write receives a failed backend result and the
owner rejects2080 before reclaim. exec-streams-shared-offset substitutes a private
peer position; the wrong input byte rejects1903 before reclaim. The source has
terminated but remains unreclaimed until these observations complete.

[Evidence](evidence/exec-shared-holders-2026-09-10/README.md) records the complete192
connections and five launch cases plus host checks. Kernel ABI, SDK and released
pins are unchanged. Peer-first exit/fault ordering, incomplete shared final-close
receipts, public fork/execve and independent consumer acceptance remain separate.


## Exec peer-first termination — 2026-09-11

The exec-streams-peer-first and exec-streams-peer-fault cases retain the replacement
in its committed, frozen state while the peer consumes a 32-byte barrier (word91,
remaining bytes zero). This fixture handshake selects the tested ordering only.
The normal peer closes descriptors0/1/2 and exits64. The faulting peer executes #UD;
the owner requires retained134/kind2 and output EOF before dropping its holders.
Only stdout lacks another holder and closes during this phase. Source input and
stderr remain live. The owner rechecks the exact commit/freeze identity before
publishing the replacement, which reads c and closes its remaining descriptors.

Acceptance requires position3, two empty holder rows and exactly three successful
backend close receipts per generation. Ordered terminals are peer64/kind1 (or
134/kind2), source62/kind1, backend17/kind1, repeated across two generations/six
reclaims. Neither client is reclaimed before the complete ownership observations.

exec-streams-peer-close-live deliberately closes handles retained by the source
while dropping faulted-peer holders; subsequent input receives a failed backend
read and rejects1952. exec-streams-peer-leak leaves the faulted peer's holder row
intact; final ownership accounting rejects2091. Both require zero reclaims.
These controls cover incorrect early release and missing release separately.

[Evidence](evidence/exec-peer-terminal-2026-09-11/README.md) retains all196 connections
cases, five launch cases, host checks and the failed initial compiler attempt.
The kernel ABI, installed SDK and released pins remain unchanged. Shared final-close
uncertainty, peer faults during partial I/O, owner death, public execve and independent
consumer acceptance remain separate. Fixed RAM cleanup is not persistent recovery.


## Shared exec close-reply containment — 2026-09-11

The peer-close-missing/partial and fault-close-missing/partial exec-streams cases
reuse the backend that performs its first close and stalls with zero or17 response
bytes. The source is already committed and frozen, and its local CLOEXEC holder
has been removed. A normal peer receives its local input-close acknowledgment and
waits for stdout-close success. A faulted peer has exact134/kind2 and output EOF.
The owner initiates the final stdout close once, treats the incomplete result as
unknown and verifies the retained source commit/freeze identity.

The owner sends no peer success acknowledgment and never publishes the replacement
or retries the close. Source/backend must be stopped with raw144/kind3 retained
results. A normal peer must also be stopped; a faulted peer retains134/kind2.
Only after every terminal is confirmed may endpoints close and all three domains
be reclaimed. Conservative fixture holder records are abandoned at that point;
no partial backend receipt is recorded as a successful release. Four positive
cases repeat two generations/six reclaims. Only faulted-peer spontaneous terminal
lines appear in the serial oracle; forced stops are checked by the owner.

exec-streams-peer-close-pad deliberately pads a short receipt and must reject2100.
exec-streams-fault-close-stop omits backend stop and must reject2101. Both require
zero reclaims. [Evidence](evidence/exec-shared-close-2026-09-11/README.md) records the
full202-case connections suite, five launch cases and host/format/pin checks.
No kernel, installed SDK or released pin changed. Production reconciliation,
persistent backend cleanup, owner death and public execve remain separate.


## First libc exec staging witness — 2026-09-11

exec-streams-public links a private source-built musl execve.c from the verified
1.2.6 archive. Only its syscall expression is replaced by a call to the local
staging hook followed by musl __syscall_ret. Original source, compiled wrapper,
upstream copyright and object inspection are retained. The installed SDK is not
patched. First-party code retains strict diagnostics; the private upstream wrapper
uses the existing upstream warning policy and a quote-only internal-header path.

The hook supports /next and the /denied admission control only. Unknown paths
return raw ENOENT before traffic. Supported paths require a single context with
all blockable signals already masked; other masks reject ENOTSUP. Valid stable
caller pointers are a precondition of this producer witness. Null argv/env lists
reject EINVAL; at most four strings per list and31 bytes per string are encoded.
General pointer-fault safety and threaded/signal-unmasked operation are not provided.

Wire order is32-byte zero-padded path,272-byte native argv/env record,64-byte local
descriptor snapshot, then the existing freeze. The connection identifies the caller.
The owner recognizes the selected path, captures the supplied argument record and
uses its own image authority. Known denied admission cancels freeze and supplies a
canonical32-byte EACCES record. Musl converts that raw negative result to -1/errno;
local flags and the next input byte remain unchanged. /next invokes the same-process
image-commit mechanism, existing CLOEXEC plan and survivor bootstrap. The new
image checks argv {exec-stream, hello} and env AETHER_EXEC=1 before application I/O.
A successful exec does not return to the old caller. The fixture does not retry
unknown completion or infer authority from a path string or numeric descriptor.

Acceptance repeats source62/backend17/peer17 twice with six reclaims. The false-return
control requires client220/owner1950; retaining CLOEXEC requires client216/owner2040,
both with zero reclaims. [Evidence](evidence/libc-exec-stage-2026-09-11/README.md)
records all205 connections cases, five launch cases and linked disassembly of the
actual execve call path. This is not a general public execve or independent SDK/dash
handoff. Caller-mask guard/restoration and broader pointer/authority contracts remain.


## Libc exec caller-mask guard — 2026-09-11

exec-streams-mask and exec-streams-mask-zero extend the private libc staging hook to
caller masks16 and0. Bounded argument validation runs before the guard; after that,
startup_mask_enter saves the previous mask and blocks all blockable signals before
descriptor snapshot and transport. The request adds a32-byte AEEMSK01 record after
the272-byte argument record: saved little-endian u64 at8 and zero bytes16–31. The
owner requires the magic, zero tail and no unblockable-signal bits, binds the record
to the source connection, and checks that the later /next request matches the
saved mask from the rejected /denied call.

After a canonical denied-admission reply, the hook restores the mask before returning
its negative errno through musl. On success the owner relays the saved-mask record
after the complete survivor table. The new image validates the record and confirms
that it is still fully blocked, installs the saved mask only after descriptor state
is ready, and verifies the resulting mask before application I/O. A failed mask
restore uses the existing fatal path; unknown transport completion cannot resume
the uncertain old image. The prior masked-only profiles remain unchanged in scope.

Both positive cases repeat source62/backend17/peer17 with six reclaims. The failure
restore omission requires source221/owner1950, and the replacement restore omission
requires source222/owner1950; each rejects before reclaim. [Evidence](evidence/libc-exec-mask-2026-09-11/README.md)
records all209 connections cases, five launch cases and host/format/pin checks.

This is mask-state qualification with valid stable pointers and one context. Live
pending-handler delivery, arbitrary pointer-fault safety, threaded callers, general
executable lookup and independent SDK/dash acceptance remain separate. No kernel
interface, installed SDK or released pin changed.


## Composed public fork/exec/wait — 2026-09-11

copy-inherit-public-fork-wait-exec composes the source-built musl fork, execve and
waitpid wrappers in one workload. It reuses the existing six-channel parent/copied
child/backend topology and fixed third-image grant, with native process copy,
freeze, exec and local-runner flags. No new ABI or quota is introduced. The C fork
and exec witnesses share exec-stage.h; the installed SDK is unchanged.

The owner publishes the copied child's descriptor receipt, serves parent input a,
and then admits the child's /next request under that child's existing connection.
The child's first freeze sequence is1. Its snapshot contains stdio and FD10, with
FD1 and FD10 marked CLOEXEC only in the child. The existing exec descriptor plan
removes those aliases; the parent stdout holder prevents a premature backend close.
After image commit/query, the owner drops only the child stdout holder and publishes
replacement bootstrap, survivor table and saved mask. PID, parent identity and
connection authority survive replacement. The replacement validates argv/env,
private TLS, identity, mask16 and descriptor state before application I/O.

The new image uses the existing AECAT001 local-reference namespace on its retained
connection. Equal numeric references in the two clients do not select the caller:
the trusted connection does. Parent and replacement read a/b/c in that order from
one owner-held position. Parent closes its own descriptors, probes WNOHANG while the
child is still live, and waits through the existing error/copy/acknowledgment checks.
The replacement closes its surviving stdin/stderr and exits72. Parent observes that
actual status, rejects a second collection with ECHILD, and exits71. Backend exits17.
Two generations require exact terminals (child, parent, backend), position3, three
backend closes and six total reclaims.

copy-inherit-public-fork-wait-exec-keep deliberately publishes the old CLOEXEC table
and requires child216/owner1950 before reclaim. The -status control corrupts the
encoded wait status and requires parent82/owner1950 before reclaim. [Evidence](evidence/libc-fork-exec-wait-2026-09-11/README.md)
records212 connections cases, five launch cases and host/format/pin checks, including
the preserved initial build failure and linked-libc inspection.

This composes real libc entry points but retains scripted owner ordering and fixed
image authority. It does not run dash, supply general SDK execve, validate arbitrary
caller pointers, qualify pending-handler delivery across the composed lifecycle,
or load executables from persistent storage. The next step is bounded request
dispatch for actual dash, with independent matching-revision consumer acceptance.


## Bounded post-fork dispatch — 2026-09-11

copy-inherit-public-fork-wait-exec-dispatch retains the initial single-fork admission
and descriptor publication, then routes parent/child traffic through dispatch.rs.
Each connection has an incremental 400-byte buffer: a 32-byte file/wait frame, or the
existing /next name followed by 272 argument bytes, 32 mask bytes and 64 descriptor
bytes. Polls read at most one bounded native chunk per client per pass. A partial
child exec frame cannot stop parent wait admission. Fixed backend exchanges and
exec bootstrap sends remain bounded and synchronous, so arbitrary slow-peer
fairness or general service recovery is not claimed.

File authority comes from the connection, the current generation-bound reference,
and its live holder row. The owner keeps one position per backend binding. A close
removes only that client's holder until the last holder permits a backend close.
The selected replacement drops child stdout through existing CLOEXEC preparation;
parent stdout survives. Read/write replies must have canonical reserved bytes and
bounded counts before any local position change or client publication. The current
workloads exercise reads and closes; dispatched writes are not target-qualified.

Parent first submits a foreign-reference read and requires EACCES with its output
byte untouched. In the default case it then probes WNOHANG and blocks in waitpid
while the child executes /next, reads a, closes its surviving descriptors and exits 72.
Parent collects the observed terminal, receives ECHILD on duplicate collection,
then reads b/c. The -late case reads a before waiting; the replacement reads b and
the parent reads c after collection. Both require an actually deferred wait, shared
position 3, three backend closes per generation, exact child 72 / parent 71 / backend 17
terminals and six reclaims. Saved mask 16, identity, argv/env, TLS and child CLOEXEC
checks compose with the existing replacement witness.

The -foreign control bypasses reference validation; the parent's untouched-byte/
EACCES check rejects with 85. The -early control issues successful wait status while
the child is still live; the parent rejects with 85. Both require owner 2130 / reclaimed 0,
not a generic panic or timeout. Owner 2131 rejects final accounting; 2132 bounds partial
request progress; 2133 validates the exec mask; 2134 rejects malformed backend replies.
These latter paths have no new independent fault-injection coverage in this packet.

[Evidence](evidence/post-fork-dispatch-2026-09-11/README.md) records 216 connections
cases, five launch cases and host/format/pin checks. The initial owner exceeded the
existing 8192-byte link assertion. Sharing send/control-call and dispatcher helpers
keeps normal code at 7992 bytes without relaxing checks or changing compiler options.
Older cases remain regressions; source snapshots, all attempts and payload/kernel
comparisons are retained. The same reproduction commands apply.

This removes scripted application request order only after one fixed fork. It does
not run dash, support multiple forks, accept arbitrary exec paths/pointers, compose
live signal delivery, load a persistent filesystem or publish an installed SDK API.
Next integrate the actual dash startup/external-command candidate and obtain the
matching-revision userland result. Sys-init/pkg-mgr policy and release pins are unchanged.


## Pre-fork requests and larger owner format — 2026-09-11

The optional AENMX002 envelope selects bootstrap ABI 17 and a supervisor code bound
of 1..16,384 bytes. All other AENMX001 header fields and limits remain: 80-byte
header/entropy prefix, three 1 MiB-bounded ELF images, 48 entropy bytes, six channels,
three worker slots, existing grants and one 4 KiB RW/NX supervisor stack. AENMX001
continues to select ABI 9 and accepts at most 8,192 code bytes. Unknown formats,
reserved bytes, mismatched lengths and zero/oversized code reject. No syscall,
capability or worker memory allowance is added. The new large-linker.ld is selected
only for the measured pre-fork owner; old profiles retain their linker and ABI.

The existing loader maps only the required code pages. Its shared validation checks
RX user mappings, RO/NX kernel aliases, the separate RW/NX stack and zeroed unused
bytes in the final code page. The new native witness exceeds two pages; additional
16,383/16,384-byte images exercise four-page mapping and the maximum. Downgrading
the same oversized owner to AENMX001 and declaring 16,385 bytes both fail with
invalid launch envelope before worker admission. Existing init-large/init-composed
capacity, code-write, stack-execute and dirty-tail controls are retained regressions.

After bootstrap, before_fork receives at most sixteen complete 32-byte frames,
including the fork header. Canonical wait-any/WNOHANG gets ECHILD, with no status
or collection token, because no child exists. Other wait fields get EINVAL. Reads
and writes share the existing file handler's generation/reference/holder checks
and update the same owner-held positions later passed to post-fork dispatch.
Other pre-fork operations get ENOTSUP. The existing fork header and descriptor
snapshot validation still governs admission. This phase has only one client;
bounded synchronous reads cannot starve a not-yet-existing child. Multi-client
incremental polling begins after publication as before. Phase exhaustion stops
the fixture at 2140; it does not fabricate fork completion.

copy-inherit-public-fork-wait-exec-dispatch-prefork calls actual private musl waitpid
before fork, requires ECHILD with status untouched, rejects a foreign-reference read
with its output untouched, and reads a. It then forks through the existing musl
hook. The child execs /next and reads b; parent collects the observed exit 72 and
reads c. Both preserve descriptor/CLOEXEC, mask, identity, TLS and holder checks.
Two generations require position 3, three backend closes each, exact child 72 / parent 71 /
backend 17 terminals and six reclaims. The -wait and -foreign controls deliberately
bypass their named condition and require parent 86 / owner 1950 / reclaimed 0 before child
admission. General pre-fork writes, other wait selectors/options, close-before-fork
and quota-exhaustion injection are not newly qualified by this workload.

[Evidence](evidence/pre-fork-dispatch-2026-09-11/README.md) records the full 223-case
connections suite, five launch cases, both prior init-capacity suites and host/
format/pin checks. The initial 8 KiB link failure and unsuccessful sharing probes
are retained. A temporary measurement-only linker was never booted. A later build
caught code_pages moving outside the init diagnostic's scope; the corrected final
run preserves all attempts. Actual code size and complete counts are recorded in
the packet. No older format silently receives larger capacity.

This advances the owner toward actual dash but still runs the C composition client.
Dash's ordinary external-command evaluator uses vfork; its subshell path uses fork
and wait3. Next compose actual startup services and a reviewed fork-based command
candidate, then obtain matching SDK/consumer evidence. General vfork, live signal
composition, arbitrary path/pointer handling, persistent storage and R1 readiness
remain separate. Userland owns its SDK/configuration acceptance; sibling trees and
released standards pins are unchanged.

## Actual dash fork/exec/wait command — 2026-09-11

Pinned actual dash now evaluates `(exec /next); exit $?` through its main, parser,
foreground subshell, forkshell, exec builtin and wait3. AECAT003 supplies bounded
identity and cwd startup; the existing copied-process owner handles child exec,
shared stdin and collection. The replacement verifies argv/environment, TLS,
PID/parent, zero restored mask and stdio with FD10/CLOEXEC removed before reading a
and exiting 72. Dash collects that actual status and exits 72. Two generations
require backend17, three final backend closes each and six reclaims.

[Evidence](evidence/dash-fork-command-2026-09-11/README.md) records the complete 227
connections cases, five launch cases and host/format/pin checks. Bypassing actual
main rejects parent72/owner1950; leaked child CLOEXEC rejects child224/owner2130;
wrong wait status rejects parent73/owner2130, all before reclaim. Linked call-path
inspection binds real upstream objects and private musl adapters. The first
attempt omitted the existing signal-copy build flag; the second exposed early
bootstrap rejection during mask publication. Both are retained; complete-frame
consumption preserves the exact rejection boundary.

This is a bounded producer shell command, not an interactive shell or installed
SDK/consumer acceptance. Ordinary external-command evaluation still uses upstream
vfork, which is not aliased to fork. Fixed /next uses the existing image grant;
there is no persistent executable lookup. Live SIGCHLD, arbitrary pointers/paths,
redirection/pipelines, recovery and independent SDK/dash adoption remain open.
No kernel source, ABI, dependency, sibling or released pin changes. Next settle
native dash's ordinary command launch/configuration and matching SDK handoff,
then progress toward interactive serial input and persistent storage.

## Ordinary dash external command — 2026-09-11

The explicit native fork configuration now runs `/next; exit $?` in actual dash,
without an explicit subshell. Source-built jobs.c selects upstream forkshell and
shellexec instead of vfork. The unchanged evaluator creates and collects the job;
two generations preserve stdio, remove FD10/CLOEXEC, read a, return child72 and
parent72, close each backend once and reclaim six domains. The previous explicit
subshell command remains a regression.

[Evidence](evidence/dash-command-config-2026-09-11/README.md) records original,
patched-disabled and enabled source/object comparisons, all 231 connections cases,
five launch cases and host/format/pin checks. The disabled branch matches upstream
relocation disassembly. The unconfigured ordinary command rejects rather than
passing through an unsupported vfork path; CLOEXEC leakage and corrupted wait
status retain their exact rejection contexts with zero reclaims.

This is a reviewed producer build selection, not a libc vfork alias or independent
SDK/consumer acceptance. The pinned native main and other 30 dash objects remain
unchanged. Kernel source, ABI, released standards pins and sibling repositories
are unchanged. The bounded single-fork owner and fixed /next image grant remain
limits. The packet includes an SDK/userland consumption handoff. Next obtain independent
consumption and qualify interactive serial input, then persistent executable loading
and release assembly.
Live SIGCHLD, arbitrary pointers/paths, pipelines, redirection and general recovery
remain separate acceptance work.

## Actual dash pipe substitution

The opt-in `copy-inherit-public-fork-wait-prefork-dash-command-pipe` case runs
pinned dash with `value=$(echo pipe); result=$?; echo "$value"; exit "$result"`.
Its private public `pipe()` adapter uses the existing five-binding fork v2 seam.
The child redirects its pipe writer to stdout; the parent reads `pipe\n` through
EOF before collecting actual exit0, then writes `pipe\n` to the independent
bounded stream backend. Readback verifies bytes before the last stdout close.
Two parent/backend/copied-child lifetimes yield six real reclaims. The `-header`
control rejects v1 at2174 before copy; `-status` supplies false child status256
and requires actual dash exit1 followed by owner2176 with zero reclaims.

Run the existing `--connections` command above. The [plan and evidence](evidence/dash-pipe-2026-09-11/README.md)
record qualification. No installed SDK, serial pipe profile, live-pipe exec,
same-parent repeated pipe generations or general recovery is claimed. Existing
pipe and serial-shell regressions remain required. Release pins are unchanged.

The `-pipe-repeat` extension executes two substitutions in one shell. Parent
identity stays at generation1 while pipe endpoints, copied-child identity and
freeze tokens advance1→2. The owner retires each pipe and reclaims each child only
after EOF, close, terminal and wait acknowledgment. Stdout readback is exactly
`pipe\npipe\n`. A fresh generation2 shell then runs builtin `echo clean` without
creating a child, verifying startup/backend reuse. Six actual tasks are reclaimed.
The `-pipe-repeat-token` and `-pipe-repeat-receipt` controls reject at2179 and2180
after exactly one reclaim; the latter observes child generation2 exit80 without
publishing readiness. [Plan and evidence](evidence/dash-pipe-repeat-2026-09-11/README.md)
retain source/target qualification and limitations. Serial adoption remains next.

## Serial pipe substitution

`copy-inherit-public-fork-wait-prefork-dash-command-pipe-serial` selects the existing
AENMX003/ABI18 console grant and pinned native dash input object. The host types
`a=$(echo pipe); echo "$a"`, then the same command using `b`, at separate prompts,
and exits. A second shell receives `echo clean; exit 0`. The owner validates every
stdio byte and cumulative offset, requiring real EAGAIN before input and preserving
each unapplied read until data arrives. Two private pipes still drain to EOF before
wait acknowledgment and retirement. The UART backend remains alive across both
shells; its replacement lacks the old console grant. Six real tasks are reclaimed.

The `-wrong` input control rejects at2182 with zero reclaims; `-token` rejects the
second copy at2179 after one child reclaim. The dedicated serial driver requires
complete panic lines and exact terminal history, not a partial token or timeout.
[Plan and evidence](evidence/dash-pipe-serial-2026-09-13/README.md) document the
fixed workload. This profile supports serial builtin substitutions; combined
serial exec/live-pipe exec, SDK integration and release assembly remain separate.


The [bounded native pipe exec](NATIVE-SHELL-STARTUP.md#bounded-native-pipe-exec--2026-09-13)
profiles (`copy-inherit-public-fork-wait-prefork-dash-command-pipe-exec`, `-stale`,
`-drop`) use the existing connections invocation and pinned SDK/tool lock.
They select a dedicated external writer in the third boot-image grant; no new
CLI switch or kernel ABI is added. Qualification is recorded in the linked packet.

## Serial external substitution

`copy-inherit-public-fork-wait-prefork-dash-command-pipe-exec-serial` and its
`-stale`/`-grant` controls compose actual external substitution with serial input.
Use the existing complete `launch_smoke.py --connections --libc-build SDK
--tools-lock LOCK` invocation. The [contract](NATIVE-SHELL-STARTUP.md#serial-external-substitution--2026-09-13)
defines the exact commands, independent generations, terminal sequence and
rejection stages; the [packet](evidence/pipe-exec-serial-2026-09-13/README.md)
records qualification. This dedicated private profile leaves older SDK interfaces,
console grants and kernel ABI unchanged.

## Consumer argument workload

`copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-argv` and its
`-arg`, `-env`, `-skip` controls execute the unchanged userland argument workload
through the existing connections command. The [contract](NATIVE-SHELL-STARTUP.md#unchanged-consumer-dash-argv--2026-09-13)
records pinned inputs, explicit executable authority, output readback and exact
terminal/reclaim requirements. No additional CLI or kernel mode is introduced.

## Consumer signal-table workload

`copy-inherit-public-fork-wait-prefork-dash-command-pipe-signal-table`, `-post`
and `-scope` exercise unchanged command substitution and actual USR1 trap delivery.
The [contract](NATIVE-SHELL-STARTUP.md#unchanged-consumer-dash-signal-table--2026-09-13)
defines the self-only facade, script/environment pins, byte readback and exact
rejection outcomes. The same complete connections command also requalifies the
four DASH-argv profiles under the captured consumer environment. Existing kernel
modes, quotas and released standards pins remain unchanged.

### Unchanged consumer descriptor closure — 2026-09-13

The three `copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-closure`
profiles reuse the fixed helper route and scoped exec table. The unchanged helper
checks descriptors3–63 closed; real dash must collect child0 and write closed ok
plus newline. Backend readback requires exactly10 output bytes, no stdin/stderr,
and six reclaims across two lifetimes. The `-leak` control injects FD3 after startup
so the actual helper returns95; `-status` corrupts wait delivery so dash takes its exit22 path.
Leak requires owner2130; corrupted status is rejected at missing output readback2310 before parent terminal publication. Both reclaim zero. This does not implement the
consumer's writable fd-leak-control script or /dev/null for background wait.
Run the existing complete `--connections` command with the pinned SDK/tool lock.
See the [review and results](evidence/dash-consumer-closure-2026-09-13/README.md).


### Private read-only null route — 2026-09-13

Four opt-in `copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-null`
profiles add `-handle`, `-eof` and `-table` controls. They use a separate fourth
binding3, incompatible with pipe bindings. The private script is
`(exec /inputs/helper status) </dev/null; s=$?; [ "$s" -eq 7 ] || exit 20; printf "null ok\n"`.
Dash redirects the subshell after fork; actual helper status7 and parent0/backend17
must recur across two generations with six confirmed reclaims. The owner reads
back exact output and unchanged original stdin; the helper verifies EOF without
modifying its read buffer. This script is not the consumer background wait script.

After the existing child fork receipt, its authenticated connection receives a
32-byte `AENUL001` record: little-endian factory at8, object at12, generation at16,
read right1 at20, binding3 at24, zero at28. The factory is `0x76060000 | generation`;
object is zero initially, then `0x79000000 | (generation << 8) | sequence` after
open. Exec publishes the active record after the existing bootstrap, survivor table
and saved mask. Generation is 1–255 and comes from the live child identity. These
numbers are references interpreted only by the owning connection, not capabilities
usable through an arbitrary channel. Existing public/SDK layouts are unchanged.

Canonical 32-byte requests carry operation, reference, binding and count at0/4/8/12.
Open6 requires the advertised factory, binding3, count0, `/dev/null` at16 and zero
remaining bytes. Only the authenticated child may create or use the object.
Read1 returns a fully zero EOF reply; write2 denies; close3 invalidates the object.
Counts are at most16, close count is zero, and non-open payload is zero. Replies
carry signed status at0 and are otherwise zero except successful open's object at4
and binding3 at8. The owner permits one active object and at most16 nonwrapping
open instances per lifetime. Host checks cover reopen, stale handles, wrong caller,
malformed frames and exhaustion. The native adapter supports one open per child;
its first-instance bootstrap is not a general reopen API.

The private C facade permits only read-only open and optional O_CLOEXEC. It checks
local descriptor availability before requesting creation, validates the response
before publishing an FD, and poisons transport on uncertain exchanges. The four-
binding exec plan drops the child's old input FD10 while preserving null at FD0;
parent input remains held. Further fork with live null rejects before staging.
Normal helper close removes the last null alias, and the owner requires inactivity
before successful teardown. The subsequent native lifetime probes below qualify raw owner reopening,
stale/foreign-generation rejection and exhaustion. The denial-and-retry section below now qualifies native prepare denial and
client recovery. Forced-stop cleanup remains unqualified.

The bad-factory bypass must produce child2/owner2130; false EOF produces
child224/owner2130. Retaining the unfiltered exec table produces child224, then
owner1950 when bootstrap publication encounters that terminated child. All require
zero successful reclaims. The full connections command above includes these four
profiles; [evidence and failed attempts](evidence/null-native-wait-2026-09-13/README.md)
record qualification separately from independent userland acceptance.

### Native null lifetime probes — 2026-09-13

The null helper now closes its actual FD0 before issuing private raw owner requests
for instances2–16. Each instance rejects the previously closed handle, stale reads
and closes while the current object is live, another generation's reference, and
an open while already active. A rejected stale close is followed by a successful
current-object read and close, so stale rejection cannot conceal premature release.
Wrong-generation factory requests cannot consume the next instance. Reads remain
EOF, writes deny, and the seventeenth lifetime open returns ENFILE with no object.
A final stale read/close and the owner's inactive check precede successful teardown.

These fixed32-byte exchanges run under the existing saved-mask guard. They do not
install FDs or widen the one-open C adapter. The positive still requires original
stdin preservation, helper7/parent0/backend17 twice, and six confirmed reclaims.
`-null-stale` falsely accepts a stale read and requires child225/owner2130;
`-null-limit` falsely accepts the exhausted open and requires child226/owner2130.
Both require zero successful reclaims. Existing handle/EOF/table controls remain.
The standard connections command includes all six null profiles. Focused native
and host checks pass; full-suite qualification is recorded in the
[lifetime evidence](evidence/null-lifetime-2026-09-13/README.md).

This covers raw owner reopening, stale rejection and exhaustion. The subsequent
denial-and-retry section qualifies native prepare denial and client recovery.
The subsequent pre-exec fault section covers idle-boundary owner cleanup. Other
interruption schedules, general libc reopening and background wait remain gaps. No kernel/SDK/pin or null wire-layout change is introduced.

### Null exec denial and retry — 2026-09-14

The private null staging adapter now calls public execve once for `/denied` before
forwarding `/inputs/helper`. The pathname guard prevents recursive reinjection.
This is a producer probe; no consumer failed-exec script or installed SDK is changed.
The dispatcher accepts the complete400-byte record only from the child connection,
requires the live null object and both original stream holders, and validates the
exact FD0/null and FD10/input-CLOEXEC table and zero prior-mask record.

At freeze sequence1, native prepare with unauthorized image0xffff must return
EACCES. Commit inspection remains `(0,0,0)` and the freeze observation remains1.
The owner resumes sequence1 and returns a canonical EACCES response. Client-side
checks require the real execve error, unchanged FD/users/reference/live snapshots,
restored prior mask, FD10/CLOEXEC, and a null read that returns EOF without changing
its buffer. The next argument/mask/table record must match byte for byte; successful
replacement uses fresh sequence2. The child's last original-input alias is released
at successful exec; null survives until helper close. The original parent input
is still independently verified at cleanup.

The added `-null-rollback` control closes null prematurely and must produce raw
child231/owner2130. `-null-mask` omits failure-mask restoration and must produce raw
child229/owner2130. Both require zero successful reclaims. Immediate invariant
failure uses the existing native exit trap so shell cleanup cannot replace the
original diagnostic. Existing handle/EOF/stale/limit/table controls remain; the
false-EOF control applies after replacement so it retains its original helper224
rejection. The full connections command includes eight null profiles. Qualification
and all attempts are recorded in [rollback evidence](evidence/null-rollback-2026-09-14/README.md).

This is the bounded zero-prior-mask, one-null-object route. No kernel interface,
SDK, quota or null wire layout changed. The subsequent fault section covers
pre-exec idle-boundary cleanup; other interruption schedules, general libc reopening,
consumer failed-exec acceptance and background SIGCHLD/suspend remain separate.

### Null owner cleanup after a child fault — 2026-09-14

The `-null-fault` profile deliberately executes UD2 after the real denied exec
has returned and the child's null EOF and descriptor/mask checks have passed.
It faults before successful replacement, with null and all three copied original
stream holders still live. No client finalizer or replacement helper runs.
The parent uses the same private foreground script, requiring shell status132
instead of helper7, then writes `null ok\n` and exits normally.

The dispatcher uses its existing child lifecycle capability to require retained
kind2/detail134, empty local framing, no pending operation and actual request
channel EOF. Only then does it mark that connection dead and release its local
null object. Later requests, including factory opens, are never served for the
dead connection. `Null::release_stopped` is an owner-local primitive, not a wire
operation or independent proof of termination. It is idempotent, preserves the
reference identity and makes old reads/writes/closes fail EBADF. The existing
normal close/reopen quota behavior is unchanged.

Both original stream holders must still exist before cleanup. Drop only the
child's holder row, without closing any backend object retained by the parent.
The owner checks the parent row and zero final backend closes before publishing
wait status through the existing fault-to-SIGILL conversion. The owner verifies the parent's
original input is intact; the parent ultimately closes all three backend objects. Require
exact stdout `null ok\n`, exact stderr `Illegal instruction\n`, parent0/backend17,
second-generation repetition and six reclaims after endpoint teardown.

`-null-fault-keep` skips null release and must reject owner2322 after the real
child fault; `-null-fault-holders` skips holder release and must reject owner2323.
Both require zero reclaims. These are separate from existing handle/EOF/rollback/
mask/stale/quota/table controls. All11 null profiles run through the documented
connections command. [Fault cleanup evidence](evidence/null-stop-2026-09-14/README.md)
records qualification and failed attempts.

Scope is one pre-exec #UD at an idle request boundary. Partial or queued request
interruption, post-exec fault cleanup and arbitrary supervision stops are not
qualified here. No kernel ABI, installed SDK, wire layout, service policy or
released pin changes. This does not accept consumer background wait; owner-scoped
SIGCHLD and atomic mask/suspend remain the next integration requirement.


### Background wait with native suspension — 2026-09-14

The `-null-wait` case uses unchanged pinned wait.sh, generated as a C literal from
its retained bytes. It enables native-signal-suspend; the `-null-wait-disabled`
control uses identical clients without routing. A startup libc probe tests an
already pending SIGCHLD, original/temporary masks and EINTR before restoring the
initial action/mask. Disabled routing gives parent233/owner1950, zero reclaims.
The real script then requires helper7/parent0/backend17 twice, exact `wait ok\n`
and six reclaims. The connections suite includes these two additional cases
(303 total, 13 null-family cases). Existing owner and helper limits are unchanged.

[Native suspend results](evidence/native-suspend-2026-09-14/README.md) establish
first execution; the [kernel contract](NATIVE-SHELL-STARTUP.md#first-native-background-wait-integration--2026-09-14)
records handler-only limits and outstanding forced-race/cleanup/consumer checks.

### Suspend ordering fixtures — 2026-09-14

The existing `--connections` invocation also selects
`copy-inherit-public-fork-wait-suspend-before`, `-after` and `-skip`.
Their [scoped contract](NATIVE-SHELL-STARTUP.md#deterministic-suspend-ordering-review--2026-09-14)
uses the existing copied-process wait/stream fixture and a read-only parked bit
on the private supervisor lifecycle query. The before case withholds the first
WNOHANG reply until child termination; the after case withholds remaining child
I/O until the parent is observed parked. The skip control omits suspension and
must reject owner2330 with zero reclaims. This is an opt-in native signal test,
not a new published SDK or independent consumer acceptance.

The `-suspend-stop`, `-suspend-ignore`, `-suspend-block` and `-suspend-repeat`
profiles add [lifecycle cleanup checks](NATIVE-SHELL-STARTUP.md#suspend-lifecycle-cleanup-review--2026-09-14)
to the same invocation. `-suspend-stop-skip` rejects owner2331;
`-suspend-repeat-post` rejects parent236/owner1950. Successful supervisor-stop
profiles check the retained143/kind3 through the query API; no new serial terminal
line is expected. These fixtures preserve the six-reclaim bound and public pins.

`copy-inherit-public-fork-wait-suspend-stale` starts a replacement in the old
parent's slot before old-child exit, verifies no stale notification, and completes
the replacement's normal child wait. `-suspend-stale-post` injects a pending
notification and requires replacement237/owner1950 with exactly three prior
reclaims. The [review](NATIVE-SHELL-STARTUP.md#stale-parent-replacement-review--2026-09-14)
specifies the private pre-bootstrap records and unchanged authority boundaries.
Both are selected by the existing connections invocation; no new CLI is added.

`copy-inherit-public-fork-wait-suspend-frame` forces three rejected stack placements
after real child exit and requires mask/canary preservation before successful
normal-stack retry. `-suspend-frame-valid` deliberately omits the stack switch and
requires parent238/owner1950 with zero reclaims. The [review](NATIVE-SHELL-STARTUP.md#suspend-frame-failure-recovery-review--2026-09-14)
specifies the bounded assembly and owned stack buffers. Both use the existing
connections invocation, with no new kernel operation or CLI.

`copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-failed-exec`
is the opt-in unchanged failed-exec prototype selected by the existing connections
command. Its [owner contract](NATIVE-SHELL-STARTUP.md#unchanged-failed-exec-owner-review--2026-09-14)
requires two sequential denied children, exact stdout, rollback and four reclaims.
Current evidence/qualification limits are in STATE. It is not a public SDK API.

The [failed-exec packet](evidence/failed-exec-native-2026-09-14/README.md) records
full qualification. Suffixes `-missing`, `-denied`, `-skip`, `-output`, and `-keep`
select the five semantic controls; native-traces.json binds exact terminal and
reclaim outcomes. `native-exec-denial` changes only the explicit completion verdict,
not the copy/exec API or quotas.

The opt-in `copy-inherit-scratch` profile preflights a bounded scratch file in the
existing stream backend across two lifetimes, then completes the original copy
fixture. `-drop` and `-epoch` reject omitted writes and a stale backend epoch.
See the [scratch contract](NATIVE-SHELL-STARTUP.md#native-scratch-transport-selection)
and [native evidence](evidence/scratch-native-2026-09-14/README.md). These are
backend transport tests, not shell-open or persistent-filesystem acceptance.

`copy-inherit-scratch-owner` composes owner-held offsets and parent/child holders
with the native scratch backend before the original copy fixture. Its `-offset`
and `-close` controls reject2503/reclaimed0. The larger existing owner envelope
is selected explicitly; [contract and evidence](NATIVE-SHELL-STARTUP.md#native-open-description-owner-composition)
record the scope and resource cost. Application scratch FD tables are not yet wired.

`copy-inherit-scratch-client` connects the private C scratch adapter to the owner
gateway, exercises open/dup/read/write/close and requires independent AB readback
before the original copy fixture. `-offset` and `-cloexec` reject client252 then
owner1950/reclaimed0. [Live C contract/evidence](NATIVE-SHELL-STARTUP.md#live-c-scratch-descriptor-selection)
records exact scope; scratch descriptors are closed before fork/exec in this step.

### Dash scratch descriptor leak selection — 2026-09-15

The connections suite includes the unchanged fd-leak-control script pinned in
`user/native-command/dash-scratch-inputs`. One owner retains the writer across
native fork and exec; the actual consumer helper must observe FD9 and return95,
then dash returns22. Expected stdout is empty. Both lifetimes require backend17
and six total reclaims. Parent-reference grant, omitted description and skipped
helper controls require their exact child/owner failures and zero reclaims.
The [shell reference](NATIVE-SHELL-STARTUP.md#dash-scratch-dispatch-integration--2026-09-15)
defines the bounded contract; STATE records qualification and remaining work.
This volatile scratch backend is not persistence or a supported filesystem SDK.

The companion redirection selection now writes A/B through duplicated descriptors,
closes the writer, and inherits a reopened reader on stdin. Native snapshots retain
old stdin at CLOEXEC FD10/FD11; exec removes those aliases while preserving the
reader and the parent's stream. Helper0/dash0, exact stdout AB, backend17 and six
reclaims are required. Lost-write, retained-stdin and skipped-helper controls must
reject with their exact oracles. See the [shell contract](NATIVE-SHELL-STARTUP.md#unchanged-scratch-redirection-workload--2026-09-15)
and STATE for current evidence and remaining integration limits.

[Full redirection qualification](evidence/dash-redirection-2026-09-15/README.md):
352 connections cases in 1091.44 seconds on 264 unchanged inputs, 104 host tests,
and 671 byte-identical prior images. All three semantic controls reject with
zero reclaims. Matching runner and independent consumer acceptance remain open;
the next workload is denied redirection into the read-only input namespace.

[Denied-redirection qualification](evidence/dash-denied-redirection-2026-09-15/README.md)
passes all 355 connections cases in 1105.85 seconds on 266 frozen inputs and all
104 host tests. Child fork-issued stream references remain valid without exec;
backend EACCES precedes child I/O. Exact denied ok newline, child2/parent0/backend17
twice and six reclaims pass. Wrong errno rejects owner2554; dropped output rejects
child2/owner2310, both with zero reclaims. Of 679 prior images, 671 are unchanged;
eight scratch owners grow 32–48 bytes and pass within existing bounds. Exact
consumer substitution/pipeline/early-reader qualification, matching runner and
independent intake remain before full handoff.

[Unchanged consumer substitution qualification](evidence/dash-consumer-substitution-2026-09-15/README.md)
passes all 358 connections cases in 1107.50 seconds on 268 frozen inputs and all
104 host tests. The actual helper receives the four quoted arguments and
WITNESS=value, writes eight pipe bytes and exits0; dash checks its captured value
and emits exact substitution ok newline. Two lifetimes reclaim six tasks.
Wrong arguments and skipping the helper both reject premature EOF with owner2175
and zero reclaims before terminal observation. Of 685 prior images, 674 are
unchanged; nine pipe owners and two small writers change and pass the full suite.
The new owner is 14,152 bytes within the existing bound. Multi-stage pipeline and
early-reader workloads, matching runner and independent intake remain open.

The pipe core now uses one bounded SharedPipe implementation: Pipe retains two
participants and its existing API, while PipelinePipe selects parent plus three
children. Participant slots are authenticated owner-local identities, independent
of kernel slots, bindings and object references. Staged peers reserve holders but
cannot issue I/O; readiness/terminal transitions validate each slot's generation.
Retirement checks all participant holders and pending frames. See the
[capacity and authority review](NATIVE-SHELL-STARTUP.md#pipeline-participant-ownership-and-capacity-review--2026-09-15)
and [qualification receipt](evidence/pipeline-participants-2026-09-15/README.md).
All 34 core tests and 358 existing native cases pass; no native profile selects
PipelinePipe yet. Two simultaneously live objects still require distinct identity
and authenticated routing. Native multi-stage pipeline and early-reader acceptance
remain open; STATE records the next action.

The private two-pipe adapter now validates an object-specific 0x7900 reference
family and bindings 3/4 or 5/6 before translating to the unchanged core interface.
It stores no authority state; creation takes a typed owner-selected object, while
data routing preserves authenticated caller and selected-core holder checks.
The [routing contract](NATIVE-SHELL-STARTUP.md#two-pipe-routing-review--2026-09-15)
defines bit bounds, errors and pending-frame obligations. Its
[host and compilation receipt](evidence/pipeline-routing-2026-09-15/README.md)
does not establish native pipeline execution: native profiles still import only
the previous pipe core. The next fork/exec adapter must validate both objects
before multi-object effects; STATE records remaining integration work.

The private pipeline adapter now stages seven-binding fork inheritance and applies
exec alias filtering, copy completion and exact terminal transitions atomically
to its two local cores. A failed second transition leaves the original pair
unchanged, including FIFO bytes that successful last-reader cleanup would discard.
The [transition contract](NATIVE-SHELL-STARTUP.md#two-pipe-descriptor-transitions--2026-09-15)
requires authenticated snapshots, current object generations, quiesced I/O and
independent admission/readiness/terminal evidence. None object generation means
no caller-held endpoints; it does not assert absence of another caller's object.
[Qualification](evidence/pipeline-descriptors-2026-09-15/README.md) covers host
transitions, target compilation and existing native pipe regressions. The new
functions are not yet wired into a native multi-stage pipeline; STATE records
remaining dispatch, capacity and full matching evidence.

The [five-worker capacity review](NATIVE-SHELL-STARTUP.md#five-worker-bundle-and-capacity-review--2026-09-15)
defines the candidate AENMX004 header and identifies bootstrap entropy, PID stride,
mapping, channel and lifecycle obligations. Its separate parser has
[host evidence](evidence/pipeline-bundle-2026-09-15/README.md); the normal loader
continues rejecting the candidate. STATE records native activation prerequisites.

### Five-worker capacity profile

`AENMX004` is accepted only with `-Dnative-pipeline-capacity=true`, bounded native
memory and single-context workers. Its owner receives entry profile19, five worker
slots and ten channel objects; old builds retain four state entries and old PID
stride. The standalone capacity fixture requires three cycles/fifteen reclaims,
including one exact stop, before the unchanged connections PASS marker.

The private `AENMX005` variant keeps the same112-byte layout,80 entropy bytes,
ABI19 and grants, and raises only the supervisor-code ceiling to24576 bytes.
`AENMX004` remains limited to16384 bytes; normal bundle builds reject both.
Exec variants in the capacity suite now use005 and the private six-page linker;
non-exec variants retain004 and the existing linker. An additional basic exec case
uses004 with the same retained-state owner and must still fit its four-page limit.
At most six user RX code pages and one RW/NX stack page use the already allocated
supervisor backing. The existing loader verifies code mappings, read-only/NX kernel
aliases and zero tail for every mapped code page. See the
[owner budget review](NATIVE-SHELL-STARTUP.md#private-owner-code-budget-review--2026-09-23)
for the measured need and compatibility/security boundaries.

```sh
python3 scripts/pipeline_capacity.py --libc-build <pinned-sdk> --tools-lock <pinned-tools.json>
```

The fixture checks all five workers live together, entropy/PID/parent identity,
wrong-owner grants, worker-slot5 denial, channel exhaustion, stale handles and
third-generation retirement. Wrong entropy and envelope/build pairing controls
must reject with the exact oracles in the harness. This is capacity evidence;
actual pipeline dispatch, shell scripts and full matching suites remain required.
The [capacity review](NATIVE-SHELL-STARTUP.md#native-five-worker-capacity-witness--2026-09-15)
records limits and test selection; STATE records execution results.

The capacity harness now also executes native writer/relay/reader roles over two
pipe objects with fragmented requests and retained partial replies. Its
[dispatch contract](NATIVE-SHELL-STARTUP.md#native-two-pipe-dispatch-witness--2026-09-15)
and [evidence](evidence/pipeline-dispatch-2026-09-15/README.md) require exact ten-byte
transfer, EOF and fifteen normal reclaims across three generations. Wrong routing
and write reapplication reject with zero reclaims. These independently admitted
roles do not establish actual fork/exec or general pipe error/recovery handling;
STATE records the next integration step.
