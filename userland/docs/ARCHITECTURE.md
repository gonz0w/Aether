# Architecture and integration requirements

The separately selected [in-place FILE broker constructor](proposals/FS-BROKER-INIT.md)
initializes private nested state directly in caller-owned MaybeUninit storage.
No valid enclosing reference exists before every field and the sole greeting
succeed; returned failure preserves actual close results and once-only drops.
This supplies construction, not native authority, complete owner fit or admission.

2026-10-22 UL-007/081/082: [real TLS shell relink](proposals/FS-FORK-TLS.md) corrects
stage81's missing PT_TLS defect. A checked initialized four-byte C17 TLS object
survives the full link; Aether's unchanged actual ELF parser accepts the279568-byte
shell under default limits (79/128 pages including16 stack pages).1010 stage cases/
nine controls, frame5847, default/opt-in libc78 each and seven parser tests pass on
minimum/current Python. Native execution/whole peak fit and matching sys-init
transaction/owner/reader/full UL/M3/R1 remain open; old sealed bytes stay fixed.

2026-10-22 UL-007/081/082: [authoritative file view v1](proposals/FS-FILE-VIEW.md) now
exports exact remote FILE presence/cloexec from the sole ProcessFiles ledger,
without source calls or mutation.31 process tests/13 controls plus borrow/compiler
and external host/target checks pass; default remote regressions pass. This supplies
sys-init0202/BG-071's requested input. BG-069/070 still require owner consumption,
exact pre-copy file/stream comparison, complete native transaction/settlement,
whole fit and fresh Aether witnesses. Full UL/M3/R1 and owner/reader remain open.

The [opt-in armed stage](proposals/FS-FORK-STAGE.md) now captures a live guarded
fork snapshot, parks once, correlates the parent disposition and quarantines/
rebinds/reconstructs only the actual child before context-ready. One5040-byte
aggregate contains one boot/context plus88 arm bytes; default binding remains4952.
Pinned copy_rebind with REBIND_LIBC_REPAIR leaves TID/list repair to __post_Fork.
Full shell links; matching owner gate/transaction, whole fit and native execution
remain open. No new kernel primitive, old wire fallback or fork stub.

The [fork-frame candidate](proposals/FS-FORK-FRAME.md) implements only Aether's
proposed304/32-byte data validation/correlation and fresh child-frame correspondence.
The codec selects no owner wire; the separate opt-in stage supplies armed
quarantine/rebind. Owner file/stream publication and settlement remain open.

The [serialized file inheritance v1](proposals/FS-SERIALIZED-COPY.md) library API
holds exclusive access to the sole ProcessFiles ledger across synchronous native
copy observation and local view publication. This is an additive alternative to
the unchanged native-frozen API, not a selected dispatcher protocol. Stream/source
exclusion, authenticated copy and child-only rebind remain owner integration gates.

The [libc binding module](proposals/FS-FD-LIBC.md) supplies actual optional public
FD symbols/private I/O hook, errno normalization/preservation, existing32-byte wait
client and terminal wrapped exit. One4952-byte BSS boot context feeds the sole
startup consumer; no old runtime/greeting competitor or syscall fallback. Public
dup2 rejects unsupported stronger semantics; private receipt redirect remains
explicitly non-atomic. Complete pinned shell link isolates missing authenticated
128-map fork staging (__aether_fork_stage), not an unresolved FD/wait/exit symbol.
Actual process owner transactions/whole native fit remain acceptance gates.

The [AEFDB001 startup proposal](proposals/FS-FD-STARTUP.md) binds existing ABI29
identity,128-byte tagged table, seven native sources and persistent pipe history
in one304-byte greeting. A sole consumer uses actual auxv/PID/PPID observations,
rejects wrong16-byte header early, validates before context/identity publication,
transfers endpoint ownership once and records raw closes on failure. Boot object
is4952 bytes including context4600 and scratch304. This requires off-init-stack
placement and matching sys-init review/dispatcher; it changes no selected profile
or old installed-table/copy/exec protocol.

The [placed context contract](proposals/FS-FD-CONTEXT.md) validates complete tagged
table/source presence both ways before publication, wires internal borrows into
one stable context and automatically guards all FD operations, including local
aliases and multi-RPC redirect. Retired finish never issues source requests;
terminal receipts are cached. The embedded4096 workspace requires off-init-stack
placement. No constructor consumes a greeting or grants native authority; old
ABI29 installed-table/process snapshot formats need explicit matched adaptation.

The [native adapter contract](proposals/FS-FD-NATIVE.md) borrows authenticated
owner endpoints/source records, keeps physical stream generation history separate
from the canonical logical map, and implements existing16-byte channel/32-byte
control boundaries. Whole-operation signal protection covers multi-RPC redirection;
unknown replies preserve unresolved source records and retire without replay.
Only confirmed successful close consumes a record; both raw channel close results
remain cached. No startup format, greeting consumer, linked shell or dispatcher is
selected by this library. Owner admission, bounded native wait/cleanup and full
resource fit require matching runtime evidence.

The [receipt-based redirect](proposals/FS-FD-REDIRECT.md) supports all descriptor
classes using existing RPCs: prepare a fresh FILE duplicate before target close,
then publish only confirmed success. Known failures clean only a confirmed fresh
unpublished descriptor while live; unknown/collision never retry or close a
purported existing selector. Receipt preserves target/cleanup errors, consumed
holes and unresolved allocations, including unnamed lost-dup effects. No spare
logical slot is needed; spare remote capacity is required. This is not atomic
POSIX dup2. `aefd_session_redirect` is new; old stream-only replace remains intact.

The [integrated descriptor session](proposals/FS-FD-SESSION.md) borrows exactly
one canonical tagged map and file client and composes the existing file, stream,
pipe and chosen-target helpers. Fresh startup validates before publication and
rejects readmission. Stream seek is -29; flag query reads canonical C metadata.
The original stream-only replacement remains -38 for FILE entries; use the new
receipt-based redirect for bounded source-backed FILE replacement.

Full/omit-cloexec exports validate the whole map and publish inert data without
source mutation, copy authority or destructive exec. Terminal finish attempts each
occupied logical slot once, continues known errors, stops unknown, then records
remaining entries and both raw transport close results. Its cached receipt prevents
replay and is not proof of native settlement. Actual native rights, binding,
generation, deadline and cleanup remain owner duties. All borrows are exclusive,
serialized/nonreentrant; no second descriptor ledger or new service policy.

Host integration and freestanding ELF64/x86-64 objects/relocatable link are separate
evidence. Four unresolved libc memory functions and maximum264-byte individual
static frame do not establish executable/native ABI enforcement or full call-stack/
code/heap/workspace/backing/channel fit. No selected linked shell/startup or default
SDK/release pin changes. Exact component contracts and restrictions are linked
from the integrated session proposal.

The [typed C file facade](proposals/FS-FD-FACADE.md) now adapts the selected
transport into explicit-context file operations returning private negative errno.
Caller read output is copied only after complete validated response and remains
unchanged on error/EOF or beyond a short result. Actual C/Rust host-pipe integration
qualifies synthetic service behavior; it creates no local FD ledger or libc/pipe/
console routing. Consuming shell selection, native authentication/copy/immutable
exec, full fit and supervisor composition remain distinct gates.

The [C file-client transport](proposals/FS-FD-CLIENT.md) now retains AEFD0001
sequence through complete response validation using a caller-owned workspace.
Trusted callbacks own actual endpoint authority/deadlines; one16384-attempt budget
covers all phases. Partial/malformed/unknown completion retires once, clears and
releases storage, retaining both raw close outcomes. C access must be serialized
and nonreentrant. This is host callback qualification, with no libc interposition,
new shell selection or native object/link/fit/runtime claim.

The [AEFD0001 candidate](proposals/FS-FD-WIRE.md) now defines file-only64-byte
requests/replies over checked process views. Every opcode revalidates its trusted
bound key; borrowed4096-byte caller workspace and pending response state prevent
reuse/replay until confirmed complete delivery. Response loss retires shared file
admission. Host C/Rust tests cover real AF07 policy with synthetic storage; native
endpoint authentication/workspace placement/whole-stack fit remain owner gates.
This distinct wire does not replace the current shell/bootstrap/console/pipe/exec
protocol. Select v3 source; v1 lacks stale-unsupported validation and is superseded.

The [process-view candidate](proposals/FS-PROCESS-DESCRIPTORS.md) now adds four
trusted broker views over the one AF07 client and13 shared descriptions. Native
identity labels reuse pinned sys-init startup code; actual admission/endpoint
authentication and settlement remain external dispatcher obligations. Inheritance
shares offsets, flags diverge per view, final close scans all views and stale
service/instance keys reject. This is host policy, not native fork/exec or a new
shell message protocol. Exact path/binding/immutable exec and native fit stay open.

The [AF07-backed descriptor layer](proposals/FS-REMOTE-DESCRIPTORS.md) now owns
a fresh authenticated client connection and shares one fixed-array description
algorithm with the owner-local adapter. It creates no local Owner/SPA. Host tests
exercise actual-service read/seek/dup/final-close/cloexec and unknown-I/O retirement.
No process-caller authentication/binding messages, fork sharing, immutable exec
or native composition is implemented. Earlier seals and wires remain fixed.

The [AF07 read-only client](proposals/FS-AF07-CLIENT.md) now retains checked
connection handles over the existing sealed service, with explicit-offset reads,
lookup/stat/close/disconnect and fail-stop partial I/O. Host interoperability uses
the actual service/Owner with synthetic storage. No live Owner/SPA is duplicated.
Sys-init decision0194 supplies startup/child/wait core, not a full dispatcher.
Transport-backed shared FDs, exact process/path/binding/exec translation, immutable
image authority and native composition/fit remain open; old seals stay unchanged.

The [read-only descriptor core](proposals/FS-DESCRIPTORS.md) now implements local
shared offsets, independent opens, final-alias close and per-FD close-on-exec over
one dedicated existing Owner policy context. File FDs3–15 reserve console0–2.
It has host/typed-library evidence, not an AF07 wire/libc/native integration or
cross-process/fork/exec authority contract. Original service/client pins remain fixed.

The private [ABI29 shell client candidate](proposals/SESSION-FS-ABI29.md) selects
shell1/children2–4 in AENFS003's seven-domain geometry. Its AEFSH001 greeting
validates actual native PID/PPID/memory before client identity publication and
uses a distinct startup symbol. Complete pinned client CRT/libc/components now
link and pass host parser/initial backing checks. Matching sys-init dispatch,
runtime resource fit and native filesystem/FD/exec qualification remain open.
Existing ABI23/24 and AF06/07 contracts and sealed artifacts remain distinct.
The current boot profile keeps owner6 at generation0/PID7 through shell
generations1–3. Select the corrected v2 input; shell and supplied/native PPID
must agree with7, while copied children keep the actual shell PID as parent.


> Current scope, 2026-09-05: the [bounded native experiment](../experiments/native-c/README.md) now demonstrates startup, private TLS/FP context, partial output and cleanup. The [kernel-owned contract](../../docs/NATIVE-C.md) defines its exact ABI and narrower limits. Requirements and earlier gap snapshots below remain proposals for broader support; they do not negate that witness. Shared requirements are owned by [Aether-standards](../../../Aether-standards/docs/CATALOG.md), consumed through the [Distribution adoption](DISTRIBUTION.md). Native allocation, service-owned I/O and general POSIX integration remain open.

> Shared-standards migration, 2026-09-05: [Foundations adoption](STANDARDS.md) now routes the canonical shared ownership, interface and evidence rules. Domain mechanisms and exact implementation contracts below remain owned by this project. Shared-rule changes belong in a new standards release; adoption does not change implementation status.

Proposed consumer requirements, reviewed 2026-09-05. Not accepted sibling APIs.

## Layering and ownership

TTY applications use libc and a POSIX runtime that must ultimately operate through
Aether capability-controlled primitives. The selected experiment is a native transport adapter retaining musl internal
conventions; see [decision 002](decisions/002-native-musl-experiment.md). The final
ABI and runtime implementation remain open. Prefer keeping policy
outside the kernel; do not freeze a single global POSIX server or distributed
service topology before the required semantics and authority costs are understood.

| Owner | Responsibility |
| --- | --- |
| Aether | Native objects, grants, execution context, memory, IPC, loader mechanisms |
| sys-init | Bootstrap, lifecycle policy, readiness, supervision and recovery policy |
| pkg-mgr | Source recipes, artifact identity, staged payloads, install/trust policy |
| Userland | Package requirements/evaluation, SDK experiments, TTY acceptance, operational Rust filesystem service |
| Unassigned pending agreement | POSIX process/FD/VFS/TTY adapters, libc OS adaptation |

Do not import ambient native root privilege through a POSIX compatibility layer.
Path lookup is constrained by delegated namespace authority. Descriptor inheritance,
process creation and exec must define which capabilities survive. Package hashes
identify bytes, not grants; installation is not service enablement.

## Current compatibility gap

Aether's [lifecycle v1](../../.planning/M4-LIFECYCLE-V1.md) now specifies a
third boot module with a 32-byte envelope and at most 4096 code/constant bytes,
one stack page, fixed worker selection and scoped factory operations. Its initial
registers carry fixture information, not a C process environment. It explicitly
excludes argv/env, console handles, filesystems, shared user memory and FP/SIMD.
This is useful sys-init conformance progress, not a musl execution target.

The older package boot-pair receipt does not prove compatibility with the current
kernel/module set. Refresh exact producer/consumer artifacts before any handoff.
pkg-mgr's documented host zlib linkage is static zlib with the host system runtime,
not a fully static musl executable. No sibling tests were rerun in this review.

## Companion refresh

Sys-init now demonstrates an independently authored lifecycle v1 client, and
pkg-mgr records ordinary file modes plus private-root binary transport/replacement.
Aether reports bounded remote replacement as well as live display. These supersede
earlier broad wait/status descriptions but do not provide a general C runtime.
See the [native handoff](NATIVE-C-HANDOFF.md) for current consumer requirements.

## Required contracts and acceptance witnesses

| Area | Required behavior / witness | Work |
| --- | --- | --- |
| Image/startup | ELF segments, zeroed BSS, stack alignment, argv/env/auxv, bounded rejection, entry/exit | UL-003/006 |
| CPU context | TLS/thread pointer, FP/SIMD preservation before ordinary x86-64 C, interruption correctness | UL-003/006 |
| Memory | Allocation/mapping limits, invalid pointers, zeroing and exhaustion failures | UL-003/006 |
| libc boundary | Error mapping, partial/interrupted I/O, required startup calls, honest unsupported results | UL-002/006 |
| Processes | fork semantics or justified shell adaptation, exec, retained status, wait, reaping | UL-007 |
| Descriptors/VFS | pipes, dup, close-on-exec, shared offsets, paths, cwd, modes, links, EOF | UL-007 |
| TTY/session | canonical/raw mode, echo, controlling terminal, groups, Ctrl-C/Z, stop/continue | UL-008 |
| Identity | UID/GID views, credential transitions, namespace/grant inheritance and denial | UL-010 |
| Lifecycle | sys-init-owned launch/session cleanup/restart with explicit failure authority | UL-010 |
| Packaging | target ABI and complete file metadata; inert descriptors; incompatible payload rejection | UL-005/012 |

An early single-threaded program still requires auditing libc TLS initialization.
Deferring pthread applications does not justify skipping that audit. General C
code may use vector registers even without explicit floating-point expressions.
The integer-only compile probe deliberately avoids claiming those facilities.

## First boot profile

Propose a serial console, immutable staged base, explicitly bounded writable
scratch area and small authorized recovery payload. No general filesystem layout
is accepted yet. Read-only media does not replace source authenticity or runtime
confinement. Define how console possession becomes authorization before shipping
an administrative prompt. A developer-only QEMU session must be labeled as such.

## Public command-runner proposal (UL-059)

[The local aether-run contract](AETHER-RUN.md) separates CLI parsing/result policy
from the existing finite exit-29 native conformance runner. It proposes explicit
startup and result handoffs, delegated I/O, preserved child status and distinct
unknown/cleanup evidence. It is not an approved producer API or native CLI.
Shared changes require canonical standards and affected-owner review; current
frames, pins and test markers remain unchanged.

## Toybox native candidate boundary (UL-067)

The [bounded cat proposal](TOYBOX-NATIVE-CAT.md) records the local experimental
scope, startup/diagnostic/finalization ownership and current domain gaps. It adds
no accepted native ABI or package policy. Its CAT-01–08 acceptance cases live with
the proposal and are linked from ROADMAP; all native cases remain NOT RUN.

## Current session SDK boundary — 2026-09-29

[UL-081 assessment](SESSION-SDK-BOUNDARY.md) binds the accepted private008/ABI23
application link closure. Explicit startup/process/descriptor/memory adaptation
complements native musl; omitting memory adaptation can still link and must not
satisfy component admission. The future opt-in runtime/application split requires
owner agreement and sealed artifacts before consumer SSDK-01–06. Existing exact
private acceptance remains valid; no public libc/POSIX runtime owner or SDK support
is assigned by inference. Shared SDK implementation and independent review are open.

## Bounded runtime ownership agreement — 2026-09-29

Aether-userland implements the bounded libc/POSIX runtime extension by explicit
maintainer assignment. The initial extraction uses the accepted AENMX008/ABI23
session protocol, with process/FD/bootstrap/mask state in a runtime object and
dash startup/environment/helper-path policy in an application object. Component
checks reject omitted memory adaptation before linking; these are build admission,
not native enforcement. Aether retains ABI/grants and fixture authority. Native
requalification and independent review are required before SDK promotion.

### SI-07 maintained client profile, 2026-10-03

`NATIVE_SUSTAINED_V2` explicitly selects AERIO002 parent roles, NIO2 child
bootstrap and0x7b receipts. Both adapters reject native generation outside1..65535
at full return width before narrowing/record transfer; wire epoch must equal that
cohort. Public client symbols are versioned, so legacy/v2 mixed links reject.
Bindings publish only after complete validation; single-attempt bootstrap, poisoning,
consumed close, bounded framing and existing runner selection remain authoritative.
[Client delivery](evidence/sustained-runtime-2026-10-03/README.md) contains rebuilt
runner/bytecount and host evidence. Native enforcement, retirement, coherent cohort
provisioning, reclaim and halt require matching Aether hooks; sys-init policy remains
separate. Default legacy client artifacts remain byte-identical.

## Bounded lab-image build boundary — 2026-10-03

experiments/lab-image consumes an externally selected boot-input manifest and
sealed explicitly selected AENMX008/ABI23 or AENMX009/ABI24 SDK candidate. It rebuilds the clients, requires whole ELF
equality with the qualified payload, extracts/verifies all actual ISO boot modules,
then copies the qualified ISO/firmware/workload/notices into a new build/ kit.
The receipt records incomplete/failed/pass build state and exact inputs/tools.
Build success and native boot success remain separate. This developer tool does
not implement package state, install to a prefix, write physical media, define
sys-init policy, or add native authority. It is not a source-execution sandbox;
selected recipe/support bytes are trusted code. Concurrency against hostile host
mutation, physical hardware, persistence and unrestricted sessions are unqualified.

## ABI24 endpoint-wait client boundary — 2026-10-03

SESSION_CHANNEL_WAIT requires SESSION_SERIAL and a matched009 kernel/owner.
On EAGAIN, transfer waits on the same endpoint with zero reserved arguments,
then rescans the actual transfer at its partial offset. Readiness conveys neither
bytes nor EOF. Nonzero wait including EINTR, zero/negative or oversized transfer
poisons the synchronous protocol; no fallback/replay or implicit signal handling.
Existing public FD transactions retain their outer mask. The default vendor008
path remains exact. The component/build profile and lab envelope must match;
Aether retains all native authority, sys-init supervision policy remains separate.
[Qualified closure/handoff](ABI24-SESSION-HANDOFF.md) identifies evidence and limits.

## Owned-entry consumption boundary — 2026-10-03

The sealed sys-init decision0183 entry uses the exact009 client/kernel closure
under its owned final-action policy. Userland's independent artifact readback and
fresh bounded VM witnesses establish consumption, not sys-init's full acceptance.
An original final-phase owner fail-stop remains unclassified; its generic fault
address and complete host writes do not establish the causing operation or exact
guest delivery. [Current disposition](SYSINIT-SESSION-CONSUMPTION.md) proposes
bounded owner diagnostics without authorizing a sibling policy change or replay.

## Sys-init read-race checkpoint — 2026-10-04

UL-007/012/081: [independent repaired-owner consumption](evidence/sysinit-read-race-consumer-2026-10-04/README.md) verifies unchanged
kernel/client closure, actual old-owner EOF failure, repaired forced race and
live/error fail-closed controls. Matched sys-init developer kit is locally delivered;
full composition acceptance, maintained sys-init recipe, writeEPIPE qualification,
SSDK-06 reader and full M3/R1 remain open. Historical exact caller is unavailable.
No sibling implementation authority or release promotion is inferred.


## Private maintained service-runtime boundary — 2026-10-06

[The opt-in service supplement](../experiments/native-service-runtime/README.md)
uses explicit memory/thread grants and actual musl internals. One ordinary reaper
is charged against82/two workers; applications get81/one.512 lifetime admissions
include the reaper and never reset on retirement. Join saves native metadata before
upstream unmap; detached cleanup confirms stop before unmap/retire. Creators and
joiners use the upstream thread-list lock; the sole reaper never takes that lock
during detached retirement, because another detached exit can hold it awaiting
reaper permission. Atomic record publication/free orders metadata and cleanup;
free is published only after unmap, native retirement and live accounting. Unknown retirement
poisons admission or terminates the owner rather than claiming cleanup.
Initialization belongs to the initial caller; finish permanently closes admission,
reports EBUSY until application workers settle, then joins/retires the reaper.

The guarded base archive is unchanged. Consumers must explicitly force the
supplemental archive before libc and omit conflicting private adapters. Monotonic
condition/sleep waits retain one original deadline across bounded native parks;
UTC, cancellation/dynamic detach, manual stacks and broader scheduling semantics
reject. Engine resource/entropy/storage and sys-init lifecycle policy stay with
their owners. Exact matching intake is required; five local VM cases do not prove
actual engine entry, general POSIX or a wider shell SESSION contract.


## Private shared UTC composition — 2026-10-06

The [opt-in UTC runtime](../experiments/native-utc/README.md) owns explicit raw
RTC interpretation, Gregorian conversion and one shared immutable monotonic-
anchored estimate per address-space lifetime. Native source/grant enforcement
stays with Aether. Serialized initial establishment occurs after runtime init
and before application helpers; closure follows helper joins and precedes finish.
Unestablished/unavailable/malformed sources remain errors with unchanged outputs.
Checked time/gettimeofday wrappers replace upstream failure-ignoring bodies in
this variant; realtime waits remain unsupported. One-second quantization and
read uncertainty are distinct from accuracy/trust. Engine timestamp consumers
must check errors/ranges before persistence; this delivery does not accept them.


## Private filesystem service policy — 2026-10-18 (UL-082)

The [current producer handoff](evidence/filesystem-policy-2026-10-18/producer-pair.json)
resolves operational filesystem ownership here; it does not transfer enforcing
block grants or init/package policy. Retain original OpenZFS C behind one Rust
policy owner. [The private policy contract](../experiments/filesystem-service/README.md)
requires retained authenticated endpoint/session bindings, attenuated WRITE,
trusted UTC, serialized sole context ownership, coherent alias size and permanent
retirement/no retry after committed or uncertain errors. Client paths, IDs,
metadata, raw C pointers and timestamps do not confer native authority.

One nonempty provider call per context is the current explicit bound. Host policy
qualification is not a running service; the matching C bridge must prove layout,
buffer/SPA lifetime and consuming Drop before native composition. Existing readonly
wire/rights and producer fixtures stay unchanged. No public opcode or SDK API is
allocated. Native sustained transactions, complete metadata/directory mutations,
lost-reply retirement, resource fit and persistent runner/package/sys-init assembly
remain open. Close/Drop alone does not certify device quiescence or durability.


UL-082 bridge implementation (2026-10-18): [private C bridge contract](../experiments/filesystem-service/README.md)
now enforces one borrow-checked context through synchronous C calls/consuming Drop,
using already-established runtime UTC. Unsafe admission requires live exclusive SPA,
accounting-before-import and exclusion of teardown/property changes. No Send/Sync,
cloning, reentry or client raw pointer authority. Proposed native callback separately
reports committed/synced/uncertain progress even on readback failure. That header is
unadopted private composition, not a public opcode/SDK. Actual C/Rust object binding
is verified; producer selector and current uncertainty disposition still gate native
execution. Full-file/metadata/ordered drain/export/fresh-VM oracles remain mandatory.


UL-082 transport checkpoint (2026-10-19): [AFSRPC01 and native entry](proposals/FS-SERVICE-TRANSPORT.md)
add a separate private version with one trusted provisioned connection, retained
kernel-authenticated endpoint holders, service-local nonreused tokens, attenuated
rights and64 complete requests. No request can attach or select peer/object/UTC.
Every exit consumes the filesystem context before both endpoint close attempts;
lost replies are never replayed. Committed/unknown completion ends admission.
One nonempty provider call remains; state2 is not durability. Current artifact is
an ELF64 relocatable object, not a launchable service. The current Aether builder's
writable+IPC guard/intake requires a matched owner profile and fresh native evidence
before sys-init composition. Historical callback/recovery blockers are superseded
by current producer results; existing readonly wire/default SDKs stay unchanged.


## Separately selected metadata service — 2026-10-21 (UL-082)

[AF07 contract](proposals/FS-SERVICE-METADATA.md) adds an explicit METADATA16 right
and opcode12 on retained authenticated handles. Peer/session/handle scope and
attenuation precede the sole exclusively borrowed C getter. Raw labels/mode/flags
and signed times are observations; no credentials/capabilities or client-selected
C identity. The112-byte endian-defined body omits backend identity and parent.
Provider failure publishes no body; malformed metadata consumes all aliases/context
before error publication; reply loss ends without replay. Existing4096 scratch,
retirement, endpoint close and independent native drain/reclaim obligations remain.
This is a new cfg/entry/wire, preserving sealed AF06/executable/binding bytes.
Current writable IPC/executable/init producer gates are cleared; matching AF07
provider/intake/client/native fit/recovery and replacement owner delivery are next.
Host/object checks do not authorize a default profile or native metadata adoption.


## Separate AF07 executable owner input — 2026-10-21

[New fixed Rust owner](proposals/FS-AF07-OPERATIONAL-OWNER.md) calls the qualified
AF07 service with explicit root rights31, trusted dataset/labels and existing
inherited native holders. The136-byte launch state,72-byte result and main/engine
callback ABI stay fixed. Startup endpoint ownership never resumes after observed
service evidence; missing/unknown phases still fail. Clean exit requires actual
ready/disconnect/requests/close/error and coherent no-transaction or successful
bounded progress. No native reclaim/durability/restart follows from those checks.
Old AF06 owner and all sealed service/executable bytes remain selected. Current
artifact is a source/native-object input pending Aether's explicit full engine
link/intake/image/stack/native qualification and matched sys-init consumption.
