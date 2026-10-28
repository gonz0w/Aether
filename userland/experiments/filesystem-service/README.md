## Boot-session lifetime contract

[FS-SERVICE-LIFETIME](../../docs/proposals/FS-SERVICE-LIFETIME.md) specifies one
Owner/source connection across two work phases and a controlled idle boundary.
`service-lifetime-tests.rs` exercises actual library paths with host storage and
channels. Its build selection, bounds and proof limits are in that contract.
[Issue9](https://github.com/gonz0w/Aether/issues/9) owns the contract;
[issue60](https://github.com/gonz0w/Aether/issues/60) records the admission cutpoint;
[issue61](https://github.com/gonz0w/Aether/issues/61) records the source-only fixed
drain deadline. [Issue64](https://github.com/gonz0w/Aether/issues/64) retains matched
native qualification; host tests do not prove native drain timing.

## AF09 offline composition

[Issue3](https://github.com/gonz0w/Aether/issues/3) owns live integration;
[FS-HOME-PREP](../../docs/proposals/FS-HOME-PREP.md) holds the durable engine,
fixed FILE helper, guarded-input and independent-reader contract, exact commands
and dated private qualification summary. These checks require the exact private
qualification receipts, SDK/OpenZFS/runtime dependencies and applicable standards
inputs. They are not replayable from the public source alone.

From `userland/`, run
`PYTHONOPTIMIZE=1 python3 -B experiments/filesystem-service/check-home-probe.py`
for the actual guard/map helper, selected final attempt count and bounded UTC
checks. From the system root, run
`PYTHONOPTIMIZE=1 python3 -B scripts/check_fs_home_prep.py` for preparation guards
and the typed independent read-only oracle. Compact reports retain source/tool
identities, child outcomes and owned cleanup. These host/target checks start no guest.

The root `scripts/fs_home_launch.py` and `scripts/fs_home_inputs.py` commands consume
explicit current receipts and unused dependency directories. The component
`sys-init/scripts/qualify-home-owner.py --inputs DIR --seal SHA --prepare` prepares
exact prospective images; it has no execution option. These three CLIs retain
ASCII help/version, stdout JSON, escaped stderr diagnostics and0/1/2/64
success/failure/prerequisite/usage exits. Keep failed receipts, correct prerequisites
and select new unused outputs. Issue4 owns fresh native disposition and issue56
separately tracks guarded legacy coverage; old profiles/seals remain distinct.

## Native home producer candidate

From `userland/`, run
`PYTHONOPTIMIZE=1 python3 -B experiments/filesystem-service/check-home-native.py`.
This offline gate builds the explicit `fs_home_native` candidate with matched
AFSRPC09 home policy, wire and activation dependencies. It tests the actual Rust
entry over typed C storage substitutes and selected original C import/lifecycle
bodies over host instrumentation. Target objects and original provider headers
are separate build evidence. Results and remaining checks belong to
[the native producer record](../../docs/proposals/FS-HOME-NATIVE.md).

The trusted entry creates fixed diagnostic `home` and empty `probe` components
once before greetings. It retains both original typed provider results and Owner
outcomes separately, validates non-root home identity, closes the verification
handle and delegates root3/home15 through existing activation. Existing names
fail; no replay or rollback is supplied. Bootstrap and later mutations share nine
provider attempts; the selected service stops after96 requests. Private carriers
are96/320/384 bytes with distinct home symbols; old entry/layout/seals stay exact.

The importer checks ordered completion independently of the last service TXG,
including bootstrap-only failures. Close attempts, native settlement, export and
durability remain different outcomes. This candidate establishes no installed
home layout, native authority/peak, complete engine/helper/image fit, guest or
recovery qualification. Full composition and a fresh scoped guest disposition
remain later gates. Old native entries deliberately reject home activation.

The checker uses ASCII help/version and JSON on stdout, escaped errors on stderr,
and exits0 success,1 operational failure,2 missing pinned prerequisite,64 usage.
Inspect the reported compact attempt before correcting a failure; restore the
named exact prerequisite for exit2. No source may change during a frozen run.
Generated owned output is removed after retaining commands/hashes/short failures.

## Home service activation

From `userland/`, run
`PYTHONOPTIMIZE=1 python3 -B experiments/filesystem-service/check-home-activation.py`.
Select `fs_home_activation` with matching AFSRPC09 dependencies and call
`filesystem_activation::run_home` with the existing Owner/channel, authenticated
source peer/Session/home Handle, recipient/epoch and bounded readiness callback.
It delegates both grants through the existing service, keeping root3/home15.
The old root-only activation API remains scoped to old selections.

Both grants attach before one callback. Publication precedes the first send so
the client can drain the32-byte native queue; `Report.ready` requires both complete
greetings. The wrapper validates root1/home2 and latches malformed/callback/send
failures with actual raw cleanup. A retained ready bit after loss proves neither a
usable client nor a live replacement. No replay or native settlement follows.
The callback retains the caller's UTC/native-readiness obligations.

[The owning contract and evidence](../../docs/proposals/FS-HOME-ACTIVATION.md)
record real service/client host cases, controls, old-profile checks and target
libraries. No matched native-home entry, actual home creation, complete engine
fit or guest is selected. The existing native entry deliberately rejects this
wrapper until its separate integration. The checker uses the existing plain
CLI/report/prerequisite recovery rules, schema `aether-home-activation-check-v1`.

## Home broker in-place construction

From `userland/`, run
`PYTHONOPTIMIZE=1 python3 -B experiments/filesystem-service/check-home-in-place.py`.
The explicit `fs_home_in_place` selection requires matching AF09 home/in-place
client, process writes and FILE wire prerequisites. Use
`Client::connect_home_in_place` or `ProcessFiles::connect_home_in_place` with the
exclusive final `MaybeUninit` slot. A returned borrow means every nested field and
both grants validate. Old constructors retain their single-greeting behavior and
refuse AF09 before input.

On returned error, keep the original `ConnectFailure` and both raw close results;
the channel has been dropped once. Do not assume the slot initialized. On success,
retain its address while borrowed, settle/disconnect and drop the initialized value
once. Bounded non-panicking callbacks remain required; unwind recovery is not added.
The [contract and evidence](../../docs/proposals/FS-HOME-IN-PLACE.md) distinguish
host/poisoned-storage checks and concrete constructor reservations from native
placement, complete owner fit and guest acceptance. The checker follows the plain
CLI/exit/report rules below with schema `aether-home-in-place-check-v1`; correct the
named prerequisite or inspect the failed report before another run.

## FILE writes and retained receipts

From `userland/`, run
`PYTHONOPTIMIZE=1 python3 -B experiments/filesystem-service/check-file-writes.py`.
Select matching `fs_file_write_wire` / `AEFD_WRITE_WIRE` with the AF09 process,
path and dup2 prerequisites. AEFW0001 adds existing-home-component opens and
one1–4096-byte write at the shared description offset. Old profiles stay available.
CWD, native in-place and libc/routed writers are not selected.

Copy Rust `PreparedReply::write_receipt()` before attempting delivery; keep the
authenticated process/endpoint context with it. The owned receipt survives dropped
or uncertain delivery and source retirement. A validated terminal write error still
gets its one receipt reply. No delivery or progress permits replay or proves durability.

C `aefd_client_write` requires caller-owned `aefd_write_result`: return1 means a
complete validated remote receipt, including errors;0 means invalid local input
without I/O;-1 means local FILE retirement. Inspect `observation`, original remote
cause/progress/offset and the separate source and FILE cleanup tuples. Any attempted
transfer followed by loss or malformed reply is Unknown. The explicit facade
`aefd_file_write` returns full validated bytes or negative errno and retains the
same receipt; staged bytes on error never become a successful count. Generic
exchange rejects write so it cannot discard the receipt. Inspect the observation
and reconcile effects through a separately defined recovery policy before a new
connection; no automatic retry/reconnect exists.

The [owning contract](../../docs/proposals/FS-FILE-WRITES.md) records exact fields,
bounds and continuation. The checker uses pinned tools, an actual per-translation-unit
C header closure,300-second cumulative deadline and complete owned-output disposal.
It follows the plain CLI/exit rules below with JSON schema
`aether-file-writes-check-v1`. Inspect the compact report and correct the named
failure or prerequisite before another run. Host interoperability and freestanding
objects do not establish native owner placement, full fit, execution or persistence.

## Shared process descriptor writes

From `userland/`, run
`PYTHONOPTIMIZE=1 python3 -B experiments/filesystem-service/check-process-writes.py`.
The explicit `fs_process_writes` library selection consumes AF09 through
`ProcessFiles::connect_home`. `open_home_file` opens one existing home component
with ReadOnly, WriteOnly or ReadWrite access. Root `open_read` stays attenuated.
Dup, replacement and trusted inheritance share the same source handle and offset;
independent opens keep independent offsets. Write takes1–4096 bytes and advances
the shared offset only after validated complete success.

Keep returned `ProcessWriteFailure` values: they retain the original process/source
error, mutation outcome, raw endpoint cleanup and the attempted offset when a live
description was selected. Remote errors/loss retire all views without replay;
process records remain unsettled. Local NotSent denials preserve live aliases.
No error progress becomes a successful byte count or a guessed cursor. Endpoint
cleanup does not settle native instances or prove durability.

The [contract and results](../../docs/proposals/FS-PROCESS-WRITES.md) own scope,
limits and continuation. This phase explicitly rejects CWD/in-place selections;
older FILE protocols reject the write broker. The explicit FILE/C receipt
selection above consumes it; libc and native integration remain separate. The plain checker follows the CLI/exit rules below
with JSON schema `aether-process-writes-check-v1`; inspect its compact report and
correct the named failure or prerequisite before another run.

## Client mutation completion and failures

From `userland/`, run
`PYTHONOPTIMIZE=1 python3 -B experiments/filesystem-service/check-client-mutations.py`.
The AF09-only `Client::write` accepts a writable file, explicit offset and1–4096
bytes. `Client::namespace` accepts a mutable directory and typed Create,
MakeDirectory, Rename, Remove or RemoveDirectory operation. Local invalid input
and rights failures send nothing. The service enforces actual EOF and no holes.

Success returns a validated `MutationCompletion { txg, bytes }`. Failure returns
`MutationFailure { error, outcome, cleanup }`: NotSent means this call sent nothing;
Reported retains exact Unassigned, Committed, Completed or Unknown producer
progress; Unknown means transport loss or an invalid reply prevented a trusted
observation. Committed can retain TXG0 and must never be replayed. Neither TXG nor
Completed promises durability. Keep the returned receipt for later reconciliation.

Every remote mutation error, malformed reply or transport failure retires the
client once and returns both raw close results. Later calls return Closed/NotSent
with the same cleanup. There is no automatic retry or reconnect. Correct local
input before another call; inspect reported progress and reconcile unknown effects
through a separately defined recovery policy before creating another client.

[Contract and results](../../docs/proposals/FS-CLIENT-MUTATIONS.md) own the finite
host/library scope. The checker shares the home runner's pinned tools,300-second
deadline and cleanup. Its plain CLI uses stdout help/version and JSON schema
`aether-client-mutations-check-v1`, escaped stderr and0/1/2/64 exits described
below. Inspect its compact report before another run. Process descriptor writes are recorded above; FILE writes and
native qualification remain separate.

## Two-grant service/client binding

From `userland/`, run
`python3 -B experiments/filesystem-service/check-home-wire.py` for explicit
AFSRPC09. Trusted `run_home` derives root3/home15 through the checked owner;
`Client::connect_home` validates both greetings before returning a usable client.
The same16-slot tables retain both roots. Source provisioning remains in the
owner ledger, leaving12 further owner handles for this fixture. Root reads and
home-relative lookups/reads/physical paths use the actual service; parent aliases
remain read-only. Old FILE/root-activation selections reject this selection; the matched FILE and
home activation APIs require their explicit selections described above.

[Contract and results](../../docs/proposals/FS-HOME-WIRE.md) own scope and
continuation. Client mutation completion is recorded above; process CWD/write integration and
native engine readiness/full-fit/execution require their own next contracts. The checker uses
the same offline prerequisites, plain CLI and0/1/2/64 exits as check-home below;
its versioned stdout JSON schema is `aether-home-wire-check-v1`, with status,
compact report path and cleanup. Inspect the report and correct the named failure
before another run; generated outputs are removed after compact readback.

## Bounded home delegation

From `userland/`, run
`python3 -B experiments/filesystem-service/check-home.py` for the separate
`fs_home` owner-library candidate. Trusted provisioning derives home rights15
from a live directory grant and supplies system-root rights3 in one new session.
It uses the existing tables; no path, UID or client request grants mutation.
The [owning contract](../../docs/proposals/FS-HOME.md) records scope, results and
continuation. Service greetings, writable process descriptors and native execution
are separate work.

The checker is offline after pinned tools are installed. `--help` and `--version`
write stdout and exit0; invalid usage writes stderr and exits64. Missing or changed
pinned prerequisites exit2; an executed check failure exits1. The plain ASCII
stdout JSON uses schema `aether-home-check-v1`: status, report path and cleanup
identify the compact result and disposal outcome. Errors are escaped on stderr.
Correct prerequisites or inspect the reported failure before running again; a
host pass is not native authority, persistence or complete-owner fit evidence.

## Public directory/owner candidate

`python3 -B experiments/filesystem-service/check-directory-contexts.py` selects
AFSRPC08/AEFP0003 and real public `chdir`/`getcwd` bindings. Physical paths come
from the original OpenZFS SA/ZAP walk; no string cache or synthetic root. Dot,
dotdot, repeated/trailing separators, root confinement, fork-local changes,
exec preservation and final-reference teardown compose through existing handles.
Symlinks remain explicitly unsupported. The separate canonical candidate below
and all old wire defaults stay unchanged. Map/startup002/fork/exec02 keep their
existing geometry. Same authority and resource limits; no writable home yet.

The actual entry, C/Rust/C traffic, malformed/partial/cleanup cases and matching
shell/provider pass focused host/target checks. Complete owner44968/49152 code,
7624/8192 resident and7992/8184 conservative stack fits. This is offline evidence;
the completed root-only AF08 native result is in the owning contract, while
persistent Zsh ISO qualification remains open.
[Contract](../../docs/proposals/FS-CWD.md),
[compact results](../../docs/evidence/filesystem-public-cwd-2026-10-23/README.md).

## Retained process-directory candidate

The separate producer `check-process-descriptors.py --in-place --replace --file16
--paths --cwd` retains real service CWD handles across fork/exec and releases the
last reference on settlement. Relative reads use the admitted process's CWD.
Root/dot selection is supported; parent/symlink/getcwd/public POSIX semantics and
matched owner integration remain separate. Existing FILE wires reject this
candidate, preventing silent changes to root-relative paths. No write grant,
handle/worker/channel limit or native pin changes.27 tests/29 controls pass; the
unsafe-denied13-alias candidate passes50/25, old16-alias regression15/21. Actual
ProcessFiles type growth96 bytes; whole-owner fit/native still pending.
[Contract](../../docs/proposals/FS-CWD.md) and [compact results](../../docs/evidence/filesystem-process-cwd-2026-10-23/README.md).

## Directory-anchored CWD foundation

`python3 -B experiments/filesystem-service/check-paths.py` now checks retained
service-directory-relative file/directory walks (30/13 client,9/8 descriptor tests,
eight compiling controls). Borrowed bases stay live, unknown cleanup retires and
absolute/root escape syntax rejects. No fields/limits/wire/native selection or
public CWD/write policy is added. [Review/results](../../docs/evidence/filesystem-directory-paths-2026-10-23/README.md).

## Matched protocol/startup and public dup2 candidate

The separately selected `--paths --dup2` FILE/startup/fork/exec versions consume
16 aliases/13 descriptions and actual public dup2. Producer uses
`check-process-descriptors.py --in-place --replace --file16 --paths`; protocol uses
`check-fd-protocol.py --paths --dup2`; provider uses
`check-fork-stage.py --exec --paths --dup2 --path-probe`, all under this directory
from userland/. Matching Rust owner command and full contract are in
[FS-FILE-REPLACE](../../docs/proposals/FS-FILE-REPLACE.md). Focused tests/default
regressions and whole-owner fit pass (41360 code/7528 data/7992 conservative stack).
[Results/prepared native gate](../../docs/evidence/filesystem-dup2-owner-2026-10-23/README.md).
The approved three-guest dup2/read/recovery sequence passes with current limits;
no write authority or persistent Zsh ISO acceptance follows.

## Earlier16-slot ledger checkpoint

The approved fs_file16/fs_replace foundation keeps13 shared descriptions and16
AF07 bindings across four views. Its original15 cases/21 controls with/without
paths and old13-slot regressions are in
[the ledger evidence](../../docs/evidence/filesystem-file16-2026-10-23/README.md).
The view arrays add24 bytes. That checkpoint alone did not select a wire or
qualify native execution; the matched integration and full owner fit are above.

2026-10-23: explicit owner `--paths` and provider `--exec --paths --path-probe`
compose the canonical path wire/libc binding and fixed immutable read probe. Ten
probe outcomes, actual C/fork/exec/libc and full owner checks pass at unchanged
limits (40640 code/7504 resident/8000 conservative stack). No CWD/public dup2/home
writes/general loader/Zsh acceptance; native sequence awaits fresh disposition.
[Commands/review](../../../sys-init/docs/decisions/0221-root-path-owner.md) and
[results](../../docs/evidence/filesystem-path-owner-2026-10-23/README.md).

2026-10-23: `python3 -B experiments/filesystem-service/check-fd-protocol.py --paths`
checks separate AEFP0001 canonical root paths; without arguments checks unchanged
AEFD0001 component semantics.11/10 tests and eight compiling controls each pass,
with actual C/Rust/C interoperability and freestanding builds. No libc/CWD/native
selection; [evidence](../../docs/evidence/filesystem-path-wire-2026-10-23/README.md).

2026-10-23: opt-in fs_paths adds canonical delegated-root file reads to Client
and Remote descriptors. Run `python3 -B experiments/filesystem-service/check-paths.py`
from userland.22/13 client and9/8 descriptor selected/default tests plus five
compiling controls pass; no new fields/authority/wire or selected native behavior.
[Contract](../../docs/proposals/FS-ROOT-PATHS.md) and
[compact evidence](../../docs/evidence/filesystem-root-paths-2026-10-23/README.md).
CWD, writable home provisioning, libc/path wire, native fit and Zsh/ISO remain open.

2026-10-23: `python3 -B experiments/filesystem-service/check-fork-stage.py --exec`
selects the new immutable-helper exec and application-ready provider. It links the
actual TLS shell and command entry/helper; the unchanged ELF parser accepts both.
80 C exec/readiness cases and two compiling reply-sequence/return controls pass,
plus existing fork/frame/libc regressions. The actual608-byte C request is consumed
by sys-init's Rust decoder in its matching checker. See
[decision0213](../../../sys-init/docs/decisions/0213-owner-stack-exec-readiness.md)
and [results](../../../docs/evidence/owner-exec-2026-10-23/README.md).
This is build/host qualification of the process/system-shell foundation, not native
execution, general persistent loading or Zsh/TTY/ISO acceptance. Default selection,
sealed deliveries, released pins and resource bounds remain unchanged.

The [armed fork stage/constructor](../../docs/proposals/FS-FORK-STAGE.md) now

2026-10-22 UL-007/081/082: [real TLS shell relink](../../docs/proposals/FS-FORK-TLS.md) corrects
stage81's missing PT_TLS defect. A checked initialized four-byte C17 TLS object
survives the full link; Aether's unchanged actual ELF parser accepts the279568-byte
shell under default limits (79/128 pages including16 stack pages).1010 stage cases/
nine controls, frame5847, default/opt-in libc78 each and seven parser tests pass on
minimum/current Python. Native execution/whole peak fit and matching sys-init
transaction/owner/reader/full UL/M3/R1 remain open; old sealed bytes stay fixed.

2026-10-22 UL-007/081/082: [authoritative file view v1](../../docs/proposals/FS-FILE-VIEW.md) now
exports exact remote FILE presence/cloexec from the sole ProcessFiles ledger,
without source calls or mutation.31 process tests/13 controls plus borrow/compiler
and external host/target checks pass; default remote regressions pass. This supplies
sys-init0202/BG-071's requested input. BG-069/070 still require owner consumption,
exact pre-copy file/stream comparison, complete native transaction/settlement,
whole fit and fresh Aether witnesses. Full UL/M3/R1 and owner/reader remain open.
passes1008 stage cases/seven controls,5847 frame and78 default libc regressions,
and the full pinned shell link. Use check-fork-stage.py for the opt-in path.
Matching sys-init gated transaction, whole fit and native execution remain open.

The [fork-frame candidate](../../docs/proposals/FS-FORK-FRAME.md) adds pure request,
reply/ready/sequence and child-startup correspondence checks under pinned inputs.
It performs no native copy or live copied-context reinitialization.

The [serialized copy v1 library contract](../../docs/proposals/FS-SERIALIZED-COPY.md)
adds exclusive local file-ledger access across copy observation and inheritance.
It addresses the local clone ordering obstacle without changing the old frozen
API. Owner stream exclusion, versioned staging and child rebind remain pending.

# Private Rust filesystem policy (UL-082)

The default non-fork [libc FD bridge and shell-link boundary](../../docs/proposals/FS-FD-LIBC.md)
adds actual optional open/open64/fcntl/dup/pipe/lseek/hook exports, startup, wait and
wrapped exit with stable BSS context/errno behavior. Run
`python3 -B experiments/filesystem-service/check-fd-libc.py`:78 new host scenarios/
five new controls, retained803 startup/175 context/193 native-call/482 C/Rust cases/
23 controls. Seventeen target units and complete pinned dash32/CRT/libc/public-fork
link isolate exactly missing __aether_fork_stage; no executable is produced. Native
copy/FD-clone/rebind needs a matching owner transaction, and public dup2 remains
unsupported. [Evidence](../../docs/evidence/filesystem-fd-libc-2026-10-22/README.md).

The [single-consumer startup batch](../../docs/proposals/FS-FD-STARTUP.md) proposes
AEFDB001/304-byte startup and consumes it into context after native identity and
binding validation. Run `python3 -B experiments/filesystem-service/check-fd-startup.py`:
803 startup+175 context+193 native-call+482 live C/Rust cases; five new/eighteen
retained controls. Fourteen production target objects and separate layout/import
inspection. This is an opt-in proposal/client, not a selected linked shell or
accepted native dispatcher. [Evidence](../../docs/evidence/filesystem-fd-startup-2026-10-22/README.md).

The [placed context batch](../../docs/proposals/FS-FD-CONTEXT.md) groups startup
cross-validation, internal borrow/workspace wiring, automatic full-operation masks
and terminal shutdown reporting. Run `python3 -B experiments/filesystem-service/check-fd-context.py`:
175 context scenarios,193 prior native-call scenarios, unchanged482 C/Rust cases/
88 prior host scenarios per child and six new/twelve retained controls. Twelve
production target objects/relocatable link plus separate context-layout inspection.
No linked shell/startup, owner authentication or native full-fit acceptance.
[Evidence](../../docs/evidence/filesystem-fd-context-2026-10-22/README.md).

The [native adapter batch](../../docs/proposals/FS-FD-NATIVE.md) groups concrete
channel transport, stream I/O/close, generation-checked pipe creation and outer
signal guarding. Run `python3 -B experiments/filesystem-service/check-fd-native.py`:
193 host native-call scenarios, unchanged482 C/Rust cases/88 host scenarios per
child, four new plus eight retained semantic controls. Eleven x86-64 objects and
relocatable link include an inspected int81 backend. These are separate host/build
evidence; coherent linked shell/startup, owner authentication and native runtime/
whole fit remain open. [Evidence](../../docs/evidence/filesystem-fd-native-2026-10-22/README.md).

The [file/stream redirection batch](../../docs/proposals/FS-FD-REDIRECT.md) adds
structured session redirection and actual prepared-duplicate rollback cleanup.
Run `python3 -B experiments/filesystem-service/check-fd-redirect.py`:482 live
C/Rust cases+88 prior host scenarios per child/eight controls on minimum/current
Python. Strict C17/UBSan/format and Rust/Clippy/unsafe checks; nine x86-64 objects/
relocatable link separately inspected. No native/atomic-POSIX/whole-fit claim.

The [integrated descriptor batch](../../docs/proposals/FS-FD-SESSION.md) combines
startup, operations, flags/seek, inert snapshot export and terminal finish reporting.
Run `python3 -B experiments/filesystem-service/check-fd-session.py`:15 integrated
plus19 replacement/22 creation/18 output/14 lifetime host scenarios per child,
269 live C/Rust file cases and eight compiling omissions on minimum/current Python.
Strict C17/format/UBSan and Rust/Clippy/format/unsafe checks; separately builds eight
freestanding x86-64 objects and a relocatable link with static frame reports.

Predecessor recipes/contracts remain linked from the integrated proposal and their
immutable evidence. The current native adapter and FILE-redirection proposals above extend this
older scope; selected shell/startup and native acceptance remain open.

The [typed C file facade](../../docs/proposals/FS-FD-FACADE.md) now qualifies actual
C client/Rust handler/AF07-service interaction over host pipes with synthetic
storage. `check-fd-facade.py`:74 live cases/six compiling controls on minimum/current
Python, strict C17/UBSan and Rust/default Clippy/format/unsafe denial. No libc
interposition, selected shell FD routing or native execution/fit.

The [C file-client transport](../../docs/proposals/FS-FD-CLIENT.md) now provides
AEFD0001 short-I/O/wait/bounded-call/no-replay handling over the exact v3 codec.
Run `python3 -B experiments/filesystem-service/check-fd-client.py`:1631 callback
schedules/seven compiling controls on both interpreters, strict C17/UBSan/format.
Uses recorded actual C/Rust bytes; no live Rust/native or selected shell facade.

The [AEFD0001 handler/C codec](../../docs/proposals/FS-FD-WIRE.md) adds versioned
file messages and confirmed-delivery ownership over checked process views.
`check-fd-protocol.py` passes9 host tests/eight semantic controls, actual C/Rust
wire exchanges, C17/UBSan boundaries and borrow controls on minimum/current Python.
Workspace is caller-owned; native init stack fit is not assumed. Select v3 source
candidate; old shell wire/facade is unchanged and native integration remains open.

The [process-view candidate](../../docs/proposals/FS-PROCESS-DESCRIPTORS.md) adds
central shell/child views, inherited shared descriptions, independent flags and
exact-key/generation/settlement barriers. `check-process-descriptors.py` selects
fs_process_views:18 host tests/eight controls, plus default local/remote regressions.
Canonical identity comes from pinned sys-init source; actual native authentication/
copy/settlement remains external. No native shell/fit or new wire/grant.

The [AF07-backed descriptor layer](../../docs/proposals/FS-REMOTE-DESCRIPTORS.md)
now uses the read-only client and the same offset/lifetime core as the local
adapter. `check-client.py`, `check-descriptors.py` and `check-remote-descriptors.py`
pass12/12/8 host tests and8/8/11 semantic controls on minimum/current Python.
Remote uses one fresh connection and no local Owner/SPA. No native shell/FD/exec
or resource-fit claim; [evidence](../../docs/evidence/filesystem-remote-fds-2026-10-21/README.md).

The separate [read-only AF07 client](../../docs/proposals/FS-AF07-CLIENT.md) now
speaks the existing sealed metadata service using its Channel/Framed adapter.
Run `python3 -B experiments/filesystem-service/check-client.py`: eleven actual-
service/scripted host tests, eight compiling omissions, format/Clippy and native
generic-library generation. No native execution, linked fit or shell FD/exec.
Exact dependency, bounds, failure/cleanup and source-only delivery are in the
proposal and [evidence](../../docs/evidence/filesystem-af07-client-2026-10-21/README.md).

The separate [read-only descriptor core](../../docs/proposals/FS-DESCRIPTORS.md)
now supplies owner-local shared offsets/dup/final-close/cloexec and failure tests.
It does not change the AF07 wire or provide a native/libc/dispatcher integration.

This is the first maintained userland policy layer for the operational filesystem
service assigned by the maintainer on2026-10-18. It is a no_std Rust library,
not a running daemon, public IPC protocol, SDK release or POSIX implementation.
Aether retains the original CDDL OpenZFS engine and enforcing block contracts.
Its readonly namespace/channel fixtures remain unchanged regression consumers.

The [producer handoff](../../docs/evidence/filesystem-policy-2026-10-18/producer-pair.json)
pins five matching source inputs before adaptation. owner.rs derives the bounded
session/handle logic from its BSD-2-Clause readonly namespace fixture. Its new
WRITE right belongs only to this private library; the old readonly wire and its
rights3 are unchanged. There is no raw inode/pointer/time field in a client write
operation and no new public opcode. Full independent owner/native acceptance remains.

## Authority and lifetime contract

Trusted service administration constructs one Owner with an exclusive provider,
a trusted UTC policy and a nonreused endpoint epoch. attach receives a retained
kernel-authenticated endpoint binding, not a deserialized UID/PID/peer label.
Every operation checks its peer, session, handle lifetime and attenuated rights.
Client transport must retain this binding independently of messages; synthetic
labels in host tests do not establish native authentication. Four sessions and
sixteen handles are bounded arrays; serials do not wrap or become reusable.

Backend calls, metadata, teardown and external dataset/property access must be
serialized by the provider composition. The private C bridge must own exactly one
context, retain its SPA borrow through consuming Drop, and prevent aliasing,
reentry, pointer escape and unsafe Send/Sync. The policy core has no unsafe
blocks, allocations, locks or external crate dependencies. Production library
compilation uses panic=abort; host tests alone use the standard test harness.
Backend truthfulness and cleanup remain part of the storage TCB.

## Existing-file write contract

Only existing regular files, explicit offset, no hole, length0–4096 and end at
most INT64_MAX. WRITE must be provisioned and attenuated through the directory;
READ does not imply WRITE. UTC comes from the Owner's provisioned Clock, bounded
to valid seconds/nanoseconds, and never from request fields. Empty writes call
neither Clock nor provider. Other mutations are absent, never successful no-ops.

One nonempty provider call is admitted per context until the producer qualifies
sustained transaction observation. The call budget is consumed even on an
unassigned error and cannot be reset by closing/reopening a handle. Later writes
return WriteLimit; reads remain available after a known unassigned error. This is
an explicit current bound, not a sustained service or an engine quota revision.

A valid success requires error0, state2, nonzero assigned TXG and the entire
requested staging count. The policy updates the size of every open alias with
the same object/generation, including aliases with only READ. stat and read use
that coherent current size. A later lookup reporting conflicting alias size/kind
retires the context. Previously returned Entry values are snapshots; no public
metadata caching protocol is asserted. Full persisted metadata belongs to the
original engine and is not fabricated by this size-only policy layer.

A positive-error/unassigned/zero-progress result preserves read access. A committed
error returns its exact progress and retires all sessions/handles; completion loss
or malformed/contradictory result also retires the context permanently. Backend
Drop is consumed once, and no operation automatically retries. This does not
certify pool/device quiescence or permit automatic service restart. The future
wire adapter must retire on a lost write reply before accepting more requests.
Neither bytes_staged, assigned TXG nor state2 is a public durability acknowledgment.

## Validation and next integration

Pinned Rust1.98.0/edition2021, rustfmt and default Clippy with warnings denied.
Run the owned host checker offline from the repo root:

```
python3 -B experiments/filesystem-service/check.py
python3 -B experiments/filesystem-service/check-mutations.py
```

Thirteen host tests cover shared real byte storage and alias EOF, principal/rights/
stale-handle denials, bounds, invalid time, pre/post-assignment errors, uncertain
completion, eleven malformed results, table/serial exhaustion and cleared replies.
Eight compiling semantic omissions must fail tests, including removed WRITE/peer
checks, alias updates, retirement, call budget, UTC/assigned-TXG validation and
reply zeroing. [Review/evidence](../../docs/evidence/filesystem-policy-2026-10-18/README.md).
No kernel/ISO/pool run is performed by these checks; outputs stay under build/.

## C bridge and native composition

bridge.rs now implements the private synchronous C factory/root/lookup/read/write/
close and runtime UTC reader. Spa::from_raw is the explicit unsafe admission point:
accounting/import/SPA/property/UTC lifetime remains the trusted owner's obligation.
Its derived context cannot clone, overlap, escape, Send or Sync. Every call borrows
separate live initialized buffers/results; no pointer escapes. An owned factory
error is closed, erroneous reads are cleared, and consuming close is checked.
Close violating its nulling contract deliberately fails stop (native panic=abort).

Run `python3 -B experiments/filesystem-service/check-bridge.py`. Nine compiled
Rust/C fixture tests, six compiler negatives, two ABI drift controls and one native
write-omission control pass. Actual private C definitions and Rust x86_64 objects
partially link against pinned original native headers. No whole engine executable,
VM, native resource/stack/authority or persistence claim follows. Default Clippy
covers bridge tests and callback, without suppressions.

native-probe.rs/native-probe.h define a proposed private engine-owner callback,
with three-word progress output:0 unassigned,1 committed,2 synced,3 uncertain.
Errno or failed readback never erase already-observed progress or certify no
writes. Fixed internal test principals are not transport authentication. This
callback checks one16-byte overwrite/alias read, not a complete file/recovery oracle.
[Bridge review/delivery](../../docs/evidence/filesystem-bridge-2026-10-18/README.md)
and [producer selection proposal](../../docs/proposals/FS-SERVICE-NATIVE-ENTRY.md).

Native execution is blocked by Aether's current separate repeated-write timeout
and its renewed-disposition gate, plus missing matching callback selection. Keep
one nonempty provider call per context. Do not boot/execute/retry this partial
composition or substitute a weaker oracle for the producer's full-file hash,
metadata, ordered drain/export and fresh READ1 VM evidence. No sibling edits or
messages are authorized by this proposal. Authenticated transport/reply-loss
retirement, sustained transactions, mutations, filesystem-backed runner/packages
and sys-init assembly remain required for R1. Snapshot/rollback remains post-R1;
reader review is deferred, not the cause of this native blocker.


## Current bounded service transport — 2026-10-19

Aether's current Rust-write/fresh-recovery and eight-write producer handoffs
supersede the old timeout/selector blocker above. These are not independent
consumer acceptance of this new composition. `service.rs` and `channel.rs` now
provide a one-connection,64-request AFSRPC01 loop with bounded short transfers,
readiness greeting, lookup/read/write/stat/close/disconnect and all-exit context
retirement before endpoint cleanup. `native-service.rs`/`.h` expose the exact
trusted engine entry with attenuated bootstrap rights, shared UTC and retained
native reader/writer bindings. Keep the one-nonempty-provider-call policy bound.

Run `python3 -B experiments/filesystem-service/check-service.py` offline. Its
private-recipe stdout/root and failure1 contract matches the existing checkers.
Actual Python3.10.21/3.14.7 qualification,11 host tests, four native-entry/typed-C
fixture tests, seven compiling semantic omission controls, default Clippy/rustfmt,
native panic-abort object/ABI checks and actual isolated owner-guard rejection
are recorded in [transport evidence](../../docs/evidence/filesystem-transport-2026-10-19/README.md).
The native object is not an executable or native execution witness. The C fixture
and injected traps establish host behavior, not native holder enforcement.

[Exact wire, ownership, entry, limits and producer integration proposal](../../docs/proposals/FS-SERVICE-TRANSPORT.md)
records the remaining native gate: Aether's current builder rejects writable+IPC
and admits only the old write-probe seal. New reviewed profile/client provisioning
and full original-engine/recovery/cleanup qualification precede sys-init assembly.
No sibling edits, guard bypass, retries, released pins, old readonly wire or immutable
bridge delivery changes. No continuous service, POSIX, durability or R1 acceptance.


## Retained native producer review — 2026-10-20

The exact Aether normal/lost-reply/partial-request/injected-close-failure matrix
now passes [consumer retained-evidence checks](../../docs/evidence/filesystem-native-consumption-2026-10-20/README.md).
Run `python3 -B experiments/filesystem-service/check-native-handoff.py
../Aether/docs/evidence/fs-service-native-2026-10-19.json` from the userland root.
This checker creates no outputs or guests and reads only an explicitly selected
receipt after its fixed digest verifies. All12 roles and19 semantic corruptions
are covered; no independent target run, complete report replay or sign-off follows.
Runtime policy remains one nonempty call/context. The next matched producer
retirement profile must support service16-byte writes; existing engine lifetime
qualification only retires4096-byte writes after context consumption. Keep current
bounds/retained progress/no-replay and delivery bytes until separately qualified.


## Separate approved eight-write candidate — 2026-10-20

Run `python3 -B experiments/filesystem-service/check-service.py --lifetimes`.
This adds strict cfg-specific host/actual-entry, semantic omission, native object/
import and ABI checks; it never launches a VM. Owned build outputs must be removed
after recording compact results. The default one-write profile stays unchanged.
The separate27-member `filesystem-service-lifetimes-2026-10-20-v1` delivery has
manifest `0eddb895d8a8d6276834a0d4ec58aa77e13e44be882d5eab46695cf716ff825c`.

The approved variant accepts exactly sixteen-byte writes and at most eight
aggregate attempts, consuming the C context, checking original successful result
retirement and reopening before the next accepted write. Failures never reset
history or replay. Post-write readback/retirement/reopen errors preserve state2,
original TXG/staged bytes and retire aliases. Dataset/SPA lifetimes cover every
context; owned error outputs are consumed exactly once. Lost/partial replies and
endpoint cleanup retain outcomes. Seven actual-entry cases and four compiling
omissions pass, plus default regressions and x86-64 imports/ABI checks. Aether’s
native matrix remains pending; a host candidate is not a launchable service or
whole-system uptime/R1 acceptance. Namespace operations and operational lifecycle
remain required. See Aether `docs/evidence/fs-service-lifetimes-integration-2026-10-20.json`.


## Eight-write native producer gate passed — 2026-10-20

Aether's new exact27-member candidate/profile passes12 fresh guests with seven
images admitted before launch. Normal, partial-request and final-close-failure
complete eight16-byte calls with last795/fresh805; lost reply stops after one
788/fresh798 without replay. Full independent780248-byte final file/hash/metadata/
EOF, original ordered export/drains, all21 cleanup boundaries/three terminal0/
live0/reclaims3, recovered whole media/outside guards pass. Controller4096,
observer8192, writers60s6000/readers30s3000 and other bounds stay fixed. Sources/
tools frozen, all VMs joined/owned output removed.699-method Aether integration
checkpoint passes. Exact service reports are checked in-engine; retained numeric
observations are not a complete72-byte report or general failed-close proof.

Producer receipt: `../Aether/docs/evidence/fs-service-lifetimes-native-2026-10-20.json`,
SHA256 `cac88f4ff8faa4c86a4e2361d20ece087519008fa997687df3099e0ad6b54e4e`.
The retained old checker remains explicitly pinned to the old25-member receipt;
it does not verify this new result. This is producer evidence, not independent
userland native execution/human sign-off. Compact retention hashes repeated
unmodified dependency scans/source-context catalogues; no full archive/replay claim.
Old sealed candidate/default policy, SDKs and released standards pins stay unchanged.

The next UL-082 delivery must specify authenticated namespace mutation authority
and alias/POSIX rules, zero-staged mutation progress/retirement, idle/reply-loss
behavior and an exact executable/ABI/provisioning/readiness/shutdown contract.
Existing Aether `zpl-mutate.h` (bounded create/same-directory no-replace rename/
remove) and `zpl-resize.h` (bounded shrink) are private serialized engine-owner
interfaces, not client authority. Do not infer mutation permissions or silently
reuse16-byte retirement for zero-staged operations. Aether matches that new
candidate/profile; sys-init owns lifecycle and pkg-mgr installation. These gates
still block operational service/runner/packages/Zsh/ISO/M3/R1 assembly; finite
eight-call evidence is not general uptime or permission to reset history.


## Separate namespace candidate — 2026-10-19

`python3 -B experiments/filesystem-service/check-namespace.py` checks the separate
`fs_namespace` Rust variant and AFSRPC02 entry against pinned original C contracts.
The default and `--lifetimes` checker/profile remain unchanged. The exact36-member
`build/service-deliveries/filesystem-service-namespace-2026-10-19-v1` candidate is
sealed with manifest SHA256
`9d504603cac15be48e6a45dd266baae27c23b1851477a5fa1d27e44a4e0dc7d3`, object
`d54182a8758b0e153c6f056460987497e6397c74c6b51c284b148e86fcdf8bdc`.
It is host/object-qualified; Aether native engine execution remains a separate gate.

This variant adds explicit directory LOOKUP1+MUTATE_DIR8 and trusted bounded UID/GID
bootstrap labels. A single create, same-directory no-replace rename or remove
attempt consumes all aliases and the original C context before one reply. Remove
rejects every live file alias across connections. Names fit the16-byte frame;
no raw victim IDs, caller credentials or clock values. Successful namespace
completion is stop6, not a public durability or operational-ready promise. Failed,
committed and unknown outcomes never replay; no zero-staged observer retirement.
The single namespace/nonempty-write attempt shares one budget. This does not make
the eight-write profile accept namespace commands or mix their lifetimes.

Eight actual-entry tests plus five compiling semantic omissions cover authority,
malformed/stale frames, all live aliases, missing identity, shared budget, original
progress including committed TXG0, consume-before-reply, every partial input prefix,
lost/partial reply, endpoint cleanup, UTC/lookup/factory errors. Strict Clippy/
rustfmt and target imports/export/ABI controls pass. The checker uses the pinned
existing owned-process helper; retains compact results/short failures and disposes
owned build outputs after sealing. Original C definitions remain in Aether; the
candidate carries declarations and original BSD-2-Clause Rust/C test source with
existing toolchain notices. Native partial-request, operational mixed lifetimes,
blocking idle, executable/provisioning/readiness/shutdown, consumer acceptance and
persistent Zsh/packages/ISO remain open. See the transport proposal's namespace
contract and Aether's matched AT-FS-SERVICE-NAMESPACE profile.


Namespace native result2026-10-19: Aether's exact36-member selection passes13
fresh guests with all9 images admitted before launch. Create788/798,
rename804/814, remove820/830; fresh lost-reply and injected-close create788/798.
Independent original780248-byte file/namespace/allocation/metadata/ACL/EOF, original
export/drains/all21 cleanup/terminal0/live0/reclaims3, fresh media/guards pass.
Frozen source/tool/intake audit passes; baseline engine/controller exact, all
joined owned outputs disposed. The compact producer receipt is Aether's
`docs/evidence/fs-service-namespace-native-2026-10-19.json`. It is distinct from
independent userland/reader acceptance and does not generalize the old25-member
checker. Native partial-request, operational mixed lifetime/idle/executable/init,
persistent Zsh/packages/ISO remain open. A separate fixed eight-transaction mixed
profile has now been approved; its own qualification is still required.


The separately approved fixed mixed profile uses all three cfgs fs_namespace,
fs_lifetimes and fs_mixed, AFSRPC03 and only aether_fs_mixed_run. Run
`python3 -B experiments/filesystem-service/check-namespace.py --mixed`. It checks
10 actual-entry tests,7 compiling semantic omissions, strict Clippy/rustfmt/native
object/import/export/72-byte ABI. Exactly8 shared attempts combine4 namespace and
4 writes16; trusted rights15/UID/GID1000, root-only alias refresh and typed0/16
success-only consumed-context retirement preserve failed/unknown outcomes without
replay. Old checker selections and sealed25/27/36 candidates remain unchanged.
New41-member candidate: build/service-deliveries/filesystem-service-mixed-2026-10-19-v1,
seal e07aeeff522094d4994c90ec63ea68c6fb2ca2f6163d994c6e8a54a3f43181a9.
Host/object qualification is not native execution, operational service or ISO
acceptance. See the transport proposal and current STATE for remaining work.


## Fixed mixed producer consumption result — 2026-10-19

The sealed41-member candidate now passes matching Aether original-engine native
qualification on7 images admitted before12 fresh guests. Normal/partial/close
complete8 total attempts,795/805; lost-first-create788/798, empty p. Independent
original/new file/namespace/allocation/metadata/ACL/EOF/recovery/media/export/
drains/all cleanup pass. Writer31.15–48.21s<=60s6000/readers30s3000; controller<=4096,
observer7596/8192 and other limits fixed. Frozen inputs/old seals/baseline bytes
pass, all VMs join/owned outputs removed, no native failure/retry. Aether final
broad720-method checkpoint and pins/workflow pass. Receipt
`../Aether/docs/evidence/fs-service-mixed-native-2026-10-19.json`, SHA256
`8e925cb74fc6c1a7289006374a3afbb89e095019b874c17d430ccea90b5d5991`.
Producer evidence is separate from independent userland acceptance; no old sealed
OWNER/member bytes or checker pins were rewritten. Current finite8/16-byte/
64-request candidate has no operational executable/ABI/provisioning/idle/larger-
transfer/readiness/shutdown delivery. See Aether OPENZFS-FEASIBILITY's remaining
operational handoff. Those contracts, matching engine/profile composition and
init/runner/packages/Zsh/ISO remain UL-082/M3/R1 gates, not another write-count
matrix. Existing authorization allows scoped implementation here; new explicit
resource-ceiling changes still need their own maintainer decision. No change to
sys-init/pkg-mgr/standards, SDK/released pins or independent owner/reader sign-off.


## Separate ABI26 mixed-wait candidate — 2026-10-20

`python3 -B experiments/filesystem-service/check-namespace.py --mixed-wait`
selects fs_namespace/fs_lifetimes/fs_mixed/fs_wait. Existing selections stay
unchanged. It passes13 actual-entry tests/11 compiling omissions, strict native
object/Clippy/rustfmt edition2021 and72-byte C ABI/import/export checks. Negative
wait errors are exact; positive unexpected status becomes EIO. Partial offsets
survive spurious hints, failed frames are cleared, and original mutation outcomes
and both endpoint closes remain visible without replay. All bounds stay fixed.

Delivery `build/service-deliveries/filesystem-service-mixed-wait-2026-10-20-v1`
contains43 sealed members, exporting only `aether_fs_mixed_wait_run` among service
entries, requiring AENBD004/ABI26. Seal
`d37083501c788adad04e8dc4da936656180dd4d2108a97f411bbd35cf876395b`, object
`df7948c2966e6bac7a88a9eda12fd9e3cd1617a0a1589ea46d3c0356f08d45f1`.
Old25/27/36/41 candidates remain immutable; current default/namespace/mixed/eight-
write regressions pass. Native engine/recovery qualification remains separate.
Aether integration command is in its NATIVE-C reference and workflow inventory.
This is still a finite relocatable service, not an operational executable,
independent acceptance or persistent Zsh ISO. See transport proposal for the
pre-code authority/resource/unsafe/failure/simplicity review and remaining work.


## ABI26 writable-wait producer result — 2026-10-20

Separate43-member candidate now passes Aether7-image/12-guest native matrix,
567 balanced primary wait/wake pairs (182/30/174/181), full original/final file,
namespace/allocation/metadata/ACL/time/EOF/media/guards/export/drains/all21 cleanup
and three terminal0/live0/reclaims3 per guest. Complete795/fresh805; lost-first-
create788/798/empty p. Controllers4059/3020/4091/4059<=4096, observer7596/8192;
all other limits fixed. Writers31.01–42.49s including post-run checks<=60s6000;
readers30s3000. Old candidates and baseline engine/controller exact, new writer
unchanged across isolated legacy metadata-position repair. SDK/Rust/service
inputs audited, joined generated outputs disposed. Host728 checkpoint plus final
six wait/three namespace bridge repair checks pass; unchanged results reused.

Producer receipt: ../Aether/docs/evidence/fs-service-mixed-wait-native-2026-10-20.json
SHA256 1f4625bbd014775f06dab230ea08f34ba15592a6f920bcf10a9bd3161ad181cf.
It is producer evidence, not independent userland/reader acceptance. Temporary
helper retained the wrong VM command filename; source-derived argv templates are
explicitly not captured commands, boot/tool observation has noted post-run limits.
The next data gate must capture native-qemu-command.json and emulator/boot hashes
before disposal. Independent/full E-01/release acceptance stays open. Old sealed
OWNER/member bytes remain capture-stage statements and are not rewritten.

Maintainer approved the separate4KiB data profile in Aether OPENZFS-FEASIBILITY.
Next implement AF04 header/body framing and length-checked success-only retirement
under unchanged other bounds; keep all qualified old profiles. Operational
executable/provisioning/readiness/shutdown/lifetime, directory/layout and POSIX/
runner/packages/Zsh ISO/R1 remain open. No new sibling edit/message authorization.

## Separate 4 KiB service candidate — 2026-10-20

Run `python3 -B experiments/filesystem-service/check-namespace.py --bulk` for the
explicit AFSRPC04 selection. It checks16 actual-entry tests and15 compiling
semantic omissions, Rustfmt/Clippy/unsafe boundaries, native object/import/export
and the typed72-byte ABI. Legacy single/eight-write/namespace/mixed/mixed-wait
selections pass separately. The approved data profile uses one4096-byte service
buffer and existing64-byte frames, validates all write-body frames/padding before
provider effects, and binds trusted successful retirement to request length1..4096.
Partial/unknown outcomes never replay. Preserve original failure/uncertainty fields.

The separate49-member dependency is
`build/service-deliveries/filesystem-service-bulk-2026-10-20-v1`, manifest
`b09125af433e5431a5bd7e40f0266cb1e242a043722cfad43abbd03dce2e4e91`, object
`712c1291b6db18671c8b88501eda83aa4ed1e361180fb2a0e4cbca6afe928945`.
Entry `aether_fs_bulk_run`; five cfgs fs_namespace/fs_lifetimes/fs_mixed/fs_wait/
fs_bulk; kernel AENBD004/ABI26. OWNER/build bytes describe qualification at sealing;
matching native qualification is recorded separately in Aether STATE/evidence.
No prior delivery, SDK or released standards pin changes. The Aether integration
command is in `../Aether/docs/NATIVE-C.md`, with all three mixed/wait/bulk flags.

Eight mutations/64 complete requests/100000 attempts per frame and all other
approved time/memory/authority/cleanup bounds stay fixed. This is still a finite
relocatable service. Operational executable/provisioning/lifetime/readiness/
shutdown, directory/layout and POSIX/runner/packages/Zsh ISO remain UL-082/R1 work.
Retain compact results and remove owned joined checker outputs after consumption;
do not archive binaries, copied SDKs or build trees as test evidence.

## Separate checked service lifetime candidate — 2026-10-20

Run `python3 -B experiments/filesystem-service/check-namespace.py --runtime`.
The separately approved55-member dependency is
`build/service-deliveries/filesystem-service-runtime-2026-10-20-v1`, manifest
`34cde46be6e486d220f3b4e5da018232ab0ccba608e08e481abb3d83dc22aeba`, object
`c83c527993738d87be0293ef71175a6cb5b40e4093e86b5c1e6a7aab7ff1205a`.
Entry aether_fs_runtime_run; same AF04/ABI26 and six cfgs, adding fs_runtime to
namespace/lifetimes/mixed/wait/bulk. Only this selection replaces artificial
cumulative8/64 stops with monotonic, representation-checked counters. Original
observer epoch/permanent-failure/borrow/graph guards and typed retirement stay.

Host18 actual-entry tests/16 compiling omissions, actual policy/bridge at MAX,
request-overflow positive/compiling omission, native object/Clippy/rustfmt/C format
and typed72-byte ABI/import/export checks pass. Tests cross both old caps, include
258 host-only mutations and namespace-after-eight, and keep original outcomes,
aliases, framing, wait and consuming cleanup. Native qualification remains a
separate fixed9-mutation/96-request workload; final p8192 in two checked4096-byte
blocks, q absent. The Aether integration command adds --filesystem-service-runtime
to all three explicit mixed/wait/bulk options. STATE records matching native
results; the sealed OWNER captures host-only qualification at delivery time.

All six older selections pass and old sealed dependencies/SDK/standards remain.
Writer60s6000/readers30s3000 and other resource/authority/cleanup limits stay fixed.
Fit/time failure stops; no retry, reset/replay or relaxed check. Still no standalone
service, supervisor readiness/shutdown contract, general uptime or persistent
Zsh ISO/R1 acceptance. See existing transport proposal and current STATE.


## UL-082 checked lifetime producer qualification — 2026-10-20

The separate55-member AF04/ABI26 aether_fs_runtime_run candidate now passes
Aether's7-image/12-guest native9-mutation/96-request matrix. Complete796/806 recovers
p8192 in two independent blocks; lost/partial788/798 recovers empty p. Full original/
new file/metadata/namespace/media/export/drain/cleanup and5294 balanced primary
waits pass. All engine/controller pairs and six older seals stay exact. The only
subsequent code change is Aether's narrow page-fragment channel-copy fix, qualified
by actual-body/four compiling omission checks, full757 host checkpoint and four
legacy native channel guests. Writer60s6000/readers30s3000, authority/memory and
all other limits unchanged. Initial timeouts, monitor launch/retention errors and
host implementation failures remain; generated outputs are disposed.

Producer receipt: [Aether native result](../../../docs/evidence/fs-service-runtime-channel-fixed-native-2026-10-20.json)
SHA256 695b1ee0a7bf537a6d42a976507dccce4b74ddd7fa83f7f799af4f5828c671a7.
This is finite producer evidence, not independent owner/reader acceptance or an
operational service. Keep UL-082/M3/R1 open. Next deliver the exact operational
executable/entry/resources/dependency/notice closure, authenticated block/dataset/
endpoint provisioning, generation-bound usable-namespace readiness and explicit
admission-close/drain/export/quiescence/reclaim contract. Sys-init's existing
persistent-boot intake requires those inputs before direct lifecycle wiring.
Preserve failed/uncertain outcomes; no reset/replay, new production service ABI
or shared PS adoption is inferred. Directories/layout/metadata/persistent loading,
runner/packages/Zsh/TTY and wider serial-session composition remain. No sys-init,
pkg-mgr or standards edit/message or SDK/released-pin change.


## Private activation preparation — 2026-10-20

The separately selected `fs_activation` library/entry wraps the qualified runtime
policy without a new protocol, authority or readiness channel. After imported
root validation it validates the local AF04 greeting, reads the existing UTC
provider and publishes native worker readiness once, before greeting output.
Publication failure consumes/closes without request effects; errors never retry.
The 72-byte result's `ready` still means completed greeting transfer. A terminal
instance may retain native readiness after a lost greeting: consumers must check
that their exact admitted retained instance is live and ready. Publication before
transfer avoids a startup cycle between the 64-byte greeting and 32-byte queue.
This is local startup state, not sys-init acceptance, durability or safe restart.

```sh
python3 -B experiments/filesystem-service/check-namespace.py --activation
```

Host checks pass: 21 actual-entry tests, three direct wrapper tests, 21 compiling
semantic omissions, checked counters, strict Rust/Clippy/format, typed C ABI and
packed-layout rejection. The existing runtime selection still passes its 18
entry tests. Its object differs in embedded LLVM bitcode only; all other file
bytes match the prior sealed object under the same Clippy-last emission sequence.
That comparison is not LTO reproducibility or a new native qualification.

No activation candidate is sealed or admitted. The actual Aether 9/96 controller
with its scalar readiness gate needs 4,181 bytes, exceeding the fixed 4,096-byte
code ceiling. Native work awaits a separate resource decision; the proposed
8 KiB controller is not approved or implemented. See
[Aether's proposal](../../../docs/OPENZFS-FEASIBILITY.md#proposed-activation-controller-budget--2026-10-20)
and [compact results](../../../docs/evidence/fs-activation-host-2026-10-20.json).
The previous 55-member lifetime delivery and all older seals remain fixed.
Operational executable/provisioning/shutdown, native readiness and independent
consumer checks, directories/metadata, persistent loading/packages/Zsh remain.


### Approved 8 KiB candidate — 2026-10-20

The maintainer approved the separate controller limit. The 58-member activation
candidate is now sealed at
`build/service-deliveries/filesystem-service-activation-2026-10-20-v1`. Manifest SHA256
8b87bad17f02fafc41982c94d0f4f8120b89a15df9c632ba763d76236d755fb3;
entry/object and exact cfg/resource/readiness contract are in its inputs.json.
Aether requires explicit activation/runtime/bulk/wait/mixed selection; the old
runtime seal cannot substitute. Native qualification is pending, not inherited
from the host checks or the earlier lifetime matrix. The previous pending-resource
paragraph is historical; all other fixed limits remain unchanged.


### Activation producer qualified and next capacity stop — 2026-10-20

Aether's exact58-member candidate passes7 admitted images/12 fresh guests across
normal/lost/partial/close-error and independent recovery, at unchanged limits.
The partial-prefix failure was the controller treating legal EAGAIN as fatal;
its selected correction transfers exactly16 bytes with bounded suffix progress.
No owner source/seal change. [Native receipt](../../../docs/evidence/fs-service-activation-prefix-fixed-native-2026-10-20.json),
[final-byte review](../../../docs/evidence/fs-activation-qualified-2026-10-20.json).
Previous pending-native statements describe the delivery-time state.

Package integration is blocked under the current16-byte name bound: pkg-mgr
requires64-hex blob names. The actual parser/policy probe rejects these before
backend effects. A separate255/component510/rename profile is proposed in the
owner transport proposal and Aether feasibility review; it needs an explicit
maintainer decision. Nothing here widens AF04 or changes a published pin.
Operational entry/resources/provisioning/shutdown, directory/layout/metadata,
filesystem-backed execution and runner/packages/Zsh/sys-init remain open.


### Approved AF05 name implementation — 2026-10-20

Maintainer approved separate255/component510/rename. Private fs_names requires
activation/runtime/bulk/wait/mixed; header MAGIC AFSRPC05, entry aether_fs_names_run,
same72-byte/nine-argument result. Named headers reserve bytes48..63 as zero;
word5 holds low32 source/high32 destination only for rename. Full64-byte padded
body is received in existing4096 scratch before effects. Invalid structure, epoch,
partial body or padding stops/consumes; lexical/policy denials may reply/continue.
NUL/slash/dot/dotdot names never reach a mutator. Nothing resets or replays.

Run `python3 -B experiments/filesystem-service/check-namespace.py --names`.
Actual entry29/wrapper3/26 omissions, strict Rust/Clippy/format/typed C/object,
legacy activation21/runtime18 and exact legacy non-bitcode object checks pass.
The separate61-member delivery is
`build/service-deliveries/filesystem-service-names-2026-10-20-v1`, manifest
99cb2e36ad13e108761ca513aed53cc4681ce9b8033aa4663c1faf0aec091e78.
Old seals/pins stay fixed; LLVM bitcode differs without a LTO reproduction claim.
A separate AF05 run shares original AF04 body/data helpers; a selected dead-code
expectation retains the old run verbatim for compatibility. No new buffer/heap/
static/channel/stack or kernel operation. All other resource/authority/9/96/time/
verification/cleanup bounds stay fixed. Native preparation is not executable/
provisioning/shutdown, directory/layout/metadata, persistent loading/runner/package/
Zsh/sys-init or independent acceptance. STATE links host and native progress.


## UL-082 AF05 package-length producer qualified — 2026-10-20

Exact61-member AF05 now passes Aether's7-image/12-fresh-guest matrix on64-byte
names differing at the last byte. Full796/806 recover8192 bytes; lost/partial
788/798 empty, no replay. Original/new file/metadata/namespace/EOF/media/export/
drain/all cleanup and5473 balanced waits pass. Old seals/pins and baseline/
independent controllers stay exact; frozen inputs pass and owned trees disposed.
[Native receipt](../../../docs/evidence/fs-service-names-native-2026-10-20.json),
SHA25644125fdce33a0b06638e2a94e9ef281cfae768c0a3ab0c0ca48a83570353880d.
Entry29/wrapper3/26 omissions/legacy21/18/strict ABI and772 integration checks pass.
Every other resource/authority/workload/time/cleanup limit stays fixed. This is
producer evidence, not independent acceptance, operational executable or ISO.
Maximum255 is host/engine-contract coverage. The FFI still creates regular files
only and mutation policy is scoped to the provisioned root. Next operational
entry/resources/provisioning/shutdown and directory/hierarchy/layout/metadata/
loader/runner/package/Zsh/sys-init/TTY work remains; UL-082/M3/R1 stays open.
Do not reinterpret prior pending-native paragraphs as current STATE or lift any
bound from this result. No package-format workaround or RAM-only ISO.


## Delegated directories AF06 — 2026-10-20

Run `python3 -B experiments/filesystem-service/check-namespace.py --directories`.
The separate67-member current dependency is
build/service-deliveries/filesystem-service-directories-2026-10-20-v1, manifest
e01e269a91a96bac3a428fb1197dc862032838dcb94602c0c6042ef9e8e5c4fa. Entry
`aether_fs_directories_run` keeps nine trusted arguments/72-byte result, existing
activation/UTC and AF05 framing/data bounds; MAGIC is AFSRPC06. New named operations
10 mkdir0700 and11 empty-rmdir require LOOKUP|MUTATE_DIR on the actual delegated
parent, trusted uid/gid and shared UTC. No raw client object/parent identities,
slash/dot/dotdot/NUL traversal or widened rights. Live aliases prohibit rmdir;
failed/unknown/partial/lost outcomes never replay. Only exact synced zero-staged
namespace success can consume/retire/reopen, then refresh that parent and every
alias. The root cache changes only if it is that parent. No unrelated root lookup
substitutes for a child refresh. A provider lacking directory refresh fails closed.

Typed directory-bridge.rs binds Aether's exact zpl-directories.h functions and
validates mkdir output/type and refreshed identity. SPA/context/name/result borrows
remain exclusive/disjoint through synchronous FFI, with no pointer escape, Send/
Sync/reentry or concurrent teardown. Reuse the original tables, scratch and typed
retirement, with no new allocator/channel/kernel operation. All existing9/96,
60s6000/30s3000, code/stack/observer/engine/worker/I/O/authority bounds remain fixed.
Immutable AF05 and older dependencies stay unchanged. General modes, directory
rename/cross-directory promotion, recursive deletion, symlinks and open unlink are
unsupported. Ordinary backend mutation errors also retire the context; production
policy/error usability remains part of the operational handoff, not a retry API.

Host actual entry15/wrapper3/27 semantic omissions, strict object/typed ABI/Clippy/
format and legacy18 behavior checks pass. Active legacy source/panic locations
changed, so current objects are not claimed byte-identical to sealed old ones;
embedded bitcode/LTO reproduction and fresh legacy native acceptance are not claimed.
Aether785 host and actual controller5281/3845/4581/5281 fits pass. The initial
reader preparation guard failure is preserved with no guest execution; its fix
and49 affected checks precede a fresh native matrix. STATE records target results.
Directory support is not an operational executable, sys-init handoff, persistent
runner/packages/Zsh or ISO acceptance. The candidate OWNER.md states explicit
startup authority, readiness and shutdown obligations, preserving separate ordered
engine drain/export/block quiescence and native reclaim. Never use the fixture's
expected-negative conversion as a real clean service result.


AF06 producer qualification now passes all7 admitted images/12 fresh guests.
Full796/806 recover the renamed4096-byte blob and exact directory hierarchy;
lost/partial788/798 leave only empty files. Original/new data/metadata/inventory/
media/export/drain/all cleanup and2476 balanced waits pass;36 reclaims/live0.
Nine old seals/pins remain fixed and owned generated outputs are disposed.
[Final native receipt](../../../docs/evidence/fs-service-directories-reader-fixed-native-2026-10-20.json),
SHA256 dd54d56ccf97a774d3ed47099e1352312afe940419e3d6e0e9eaa74c6ecafae8.
This is a finite producer result, not an operational executable or independent
acceptance. STATE records the approved next separate120s/65s-idle lifetime profile;
all old bounds and all other resources/authority/workload limits remain unchanged.

## Kernel storage idle lifetime handoff — 2026-10-20

The unchanged AF06 producer now passes Aether's separately selected private
AENBD005 owner27/engine26 lifecycle qualification:6500 idle ticks2885→9385 followed
by remaining mutations and read4096, exactly9/96. Fresh recovery verifies809/819
and complete content/metadata/media/export/drain/reclaim;9 lifetimes/live0 and1426
balanced waits/wakes. Writer120s once, readers30s3000; other limits and old seals
unchanged. See STATE and the root native receipt; generated outputs are disposed.
This resolves the bounded kernel idle experiment, not the operational owner.
UL-082 next needs a launchable entry/resource/provision/readiness/shutdown delivery
with real failure outcomes. Do not ship the fixture's expected-error normalization
as success or combine storage/SESSION flags. Persistent runner/packages/Zsh/TTY
and independent acceptance remain; no new source/seal or public API here.


## Executable owner contract

`launch-owner.rs` is the separate no_std executable main, not a new version of the
sealed AF06 library. It uses Aether's fixed native engine adapter and the original
nine-argument `aether_fs_directories_run` entry. Trusted immutable dataset/rights/
uid/gid policy belongs here; native holder/rights checks still authorize access.
The136-byte LaunchState is an exclusive synchronous local borrow, not an RPC or
released startup ABI. The engine/SPA/code remain resident until service contexts
and endpoints are consumed and ordered engine shutdown finishes.

A real failure never becomes a successful exit. Before service acquisition, main
closes each inherited endpoint once on startup failure; after acquisition the
original service owns closure. Zero exit requires real readiness, clean disconnect,
all separate cleanup stages, no error and successful endpoint closes. Neither a
fixed request/transaction count nor the old expected-error fixture determines
success. A clean read-only session is valid; unknown outcomes cannot reset/replay.

The exact bootstrap, resource closure, readiness, shutdown obligations, builder
and sys-init consuming gate are specified in
[Aether's native reference](../../../docs/NATIVE-C.md#launchable-filesystem-owner-and-sys-init-intake--2026-10-20).
Build from Aether with `python3 -B scripts/fs_launch.py --output .deps/fs-launch-YYYY-MM-DD-vN`.
It retains one current sealed native dependency and disposes preparation outputs;
no guest is executed. `launch-owner-tests.rs` executes this actual main/helper
logic with typed FFI fault doubles. Focused host/native-object, strict Clippy/format
and compiling-omission checks run from Aether with
`python3 -B -m unittest discover -s tests -p test_fs_launch_rust.py -v`.
Native service/sys-init acceptance remains a separate requirement; existing
storage and SESSION flags cannot be combined and this owner is not a Zsh ISO.


## Borrowed engine metadata input — 2026-10-21

UL-082 now has a separate metadata.rs binding for Aether's original C getter.
It is unsafe trusted-owner input: retain the exclusive live view/SPA borrow,
resolve object/generation through authorized service handles, exclude mutation/
properties/export/teardown and keep raw64-bit owner labels/flags and signed times
as observations. No public stat, credential/ACL/permission or client raw-inode API.
There is no retained pointer, allocation, mutable state, ownership transfer or
implicit retry. Errors never publish metadata. The136-byte record is layout-
checked against actual C and rejects contradictory identity/type/parent/link/time.

Aether's separate READ-only namespace consumer passed original-decoder root/file
metadata and stale-generation rejection, full780248-byte SHA256/EOF and existing
owner denial checks,3 generations/21 cleanup boundaries and unchanged guarded
medium within30s/3000ticks/32MiB engine/4KiB controller. This is a private engine
binding witness, not metadata adoption by the operational service. Existing AF06,
its67-member dependency and the active30-member executable seal remain unchanged.
Original zdb references independently cover seconds/labels/flags; nanos are exact
in host ABI tests and range-checked on disk, not independently zdb-decoded.

Run from Aether: python3 -B -m unittest discover -s tests -p test_fs_metadata.py -v.
The focused selection covers8 methods,9 named compiling omissions,2 compiler
negatives, C/Rust all-field/error cases, Clippy/rustfmt, native object/selection
and failed-preparation cleanup. Separate native command:
python3 -B scripts/fs_metadata.py --run. Retain compact commands/hashes/results,
not generated build/images or copied SDKs. Aether STATE/native reference records
exact receipts and the broader checkpoint; independent owner/reader review remains
pending. No sys-init/pkg-mgr sources, package policy or released standards pins
are changed by this binding.

Next UL-082 integration must select a metadata-capable service/backend/authorized
handle and reply contract; do not silently reinterpret AF06 or serialize raw
object/generation as authority. Include failure clearing, stale/rights denials,
unknown reply handling, resource fit and native consuming delivery before adoption.
Ordinary mode changes/cross-directory promotion, filesystem loader/runner,
ABI29 shell/PID/FD integration and Zsh/TTY remain R1 work. This module does not
complete UL-082 or provide the persistent Zsh ISO.


## Authorized metadata service candidate — 2026-10-21

AF07 (`fs_metadata` plus AF06 cfgs) connects the unchanged qualified metadata.rs
binding through the owned C bridge and policy handle checks. It introduces an
explicit METADATA16 right and opcode12, preserves raw64-bit labels/signed times
without credential/permission inference, and sends112 endian-defined data bytes
in the existing bounded framing. No backend object/generation/parent IDs appear
in that body. Context retirement precedes malformed-result error publication;
partial/lost replies stop without replay. The borrowed binding bytes are unchanged.

Run `python3 -B experiments/filesystem-service/check-metadata-service.py` in the
provisioned checkout (actual Python3.10.21 and3.14.7 qualified). This internal
recipe has optional --format; it is not a shipped/public CLI.23 actual-entry host
cases include the15 existing directory cases plus metadata success/authority/
provider/failure/unsupported/192 reply-prefix checks. Eight compiling omissions,
C layout/packed rejection and native object/Clippy/format checks pass. AF06's
separate checker also passes; old sealed candidates/executable stay exact.

[Exact new protocol/owner integration input](../../docs/proposals/FS-SERVICE-METADATA.md)
and [evidence/limitations](../../docs/evidence/filesystem-metadata-service-2026-10-21/README.md)
record the next gate. Current Aether writable IPC, real launch and bounded sys-init
activation/recovery are qualified producer prerequisites. AF07 still needs its
matched metadata provider/intake/client/native resource/negative/recovery witness,
then a replacement launchable owner. No new guest, default, SDK/pin, limits or
observer recycling is inferred; no sys-init/pkg-mgr/standards edits or messages.


## Separate AF07 operational owner input — 2026-10-21

Aether's selected AF07 native service gates now pass. `launch-metadata-owner.rs`
is a separately selected fixed Rust main/callback, importing aether_fs_metadata_run
with root rights31 and the exact existing77-member metadata service dependency.
It preserves the136-byte engine launch state/72-byte result, original native
bootstrap/SPA/readiness/drain/export/shutdown contract. Failure is never converted
to fixture success. Added guards reject incoherent clean progress/empty disconnect
and contradictory evidence cannot cause a second startup close after a service.
The original launch-owner.rs and AF06 executable/defaults stay unchanged.

Run `python3 -B experiments/filesystem-service/check-af07-owner.py` offline in this
provisioned checkout. Eight actual-owner host cases/nine compiling omissions,
five old-owner cases, default Clippy/format/unsafe-op diagnostics, panic-abort
native object, C layout/packed, exact import, duplicate-owner and old-entry controls
pass on actual Python3.10.21/3.14.7. Rustc emits the shipped object; Clippy's different
code bytes are a separate source-check result, not a byte-equivalence claim.
[Evidence](../../docs/evidence/filesystem-af07-owner-2026-10-21/README.md),
[exact engine/consumer handoff](../../docs/proposals/FS-AF07-OPERATIONAL-OWNER.md).
The object is not a linked executable/native operational acceptance. Current Aether
fs_launch.py still hardcodes AF06; a separate AF07 engine link/intake/fit/native
consumer and matching sys-init selection remain required. No sibling edit/message,
new guest, limit/history/idle allowance or old sealed-source change is authorized.

## In-place broker candidate

The separate `fs_in_place` constructor resolves BG-073's aggregate-construction
stack issue. See [contract and exact commands](../../docs/proposals/FS-BROKER-INIT.md).
`check-process-descriptors.py --in-place` checks the additive API; default retains
unsafe denial and the old by-value API. The mapped sys-init owner uses this API
in `sys-init/scripts/check-broker-init.py` from the system root. Host tests pass;
required-root code16544/16384 still blocks native admission. No native, complete
stack/resource fit or persistent Zsh/ISO acceptance follows.


## AF09 admission/drain host prerequisites

[Issue75](https://github.com/gonz0w/Aether/issues/75) owns the diagnostic work;
[the proposed contract](../../../docs/NATIVE-AF09-DRAIN.md) defines the fixed cases,
real counters and remaining native gates. The separate `fd-home-drain` C fixture
and cfg-only Rust counter path are host-tested foundations. They do not replace
`fs_home_probe_three` or qualify native admission, drain timing or persistent ISO.

From this component's `userland/` root, run the host-only C checker with an unused
output directory under an existing nonsymlink parent:

```sh
python3 -B experiments/filesystem-service/fd_home_drain_checks.py --evidence /private/tmp/af09-drain-check-UNIQUE
```

It needs pinned Clang/clang-format21.1.8, the installed macOS SDK and the retained
private `docs/quality/clang-format.yaml` input; a public-only checkout reports a
prerequisite block. Do not reconstruct private standards content. It records
compact receipts, checks actual code/codec paths and UBSan, and removes temporary
objects/executables. `--help`/`--version` do not build. Exits0/1/2/64 distinguish
pass, failure, prerequisite block and usage. The exact Rust host-only recipe and
qualification receipts remain private; no public counter-only runner is claimed.
The owner approved this exact control for implementation, host verification and
offline preparation; see the [recorded decision](../../../PROJECT.md#af09-diagnostic-control-review-2026-10-26).
These host checks select no guest.

The child wait-loop checks use the existing Aether native-yield callback
`0x1fffe`. A forbidden libc `sched_yield` sentinel prevents a host stub from
masking the unsupported Linux-style operation. Repeated zero results keep the
child waiting; nonzero results retain failure119. Target-object inspection and
these host checks remain separate from a matched guest result.

Controller failure-path checks run independently without spawning children:
`python3 -B experiments/filesystem-service/fd_home_drain_checks_tests.py`.
Unknown/unresolved cleanup retains its owned work; an expired complete aggregate
cannot report a passing run after final verification or cleanup.

## Private created-identity Owner core (#88)

The mixed namespace policy adds `CreatingBackend` and `Owner::create` alongside
unchanged `Backend::mutate` and `Owner::namespace`. The trusted bridge retains the
provider-created object, generation and type through its existing context
retirement/reopen. Owner checks the parent/session, LOOKUP and MUTATE_DIR rights,
attenuated child rights, name, UTC, mutation budget, free handle slot and serial
before dispatch. A reopened same-name child must match the retained identity and
metadata before publication. No client supplies an object identity.

The result separates original mutation progress from handle acquisition.
`CreatedAcquisition.progress` retains the provider Completion or Lost value even
when `entry` fails after a completed mutation. The path never retries, reconnects,
unlinks or rolls back by name. Fixed file mode 0600 and directory mode 0700 remain
provider limits. Requested modes, umask, wire/opcodes, public client and mktemp/libc
consumers are outside this private API. Closing a handle does not remove its
namespace object.

From `userland`, the focused selections are
`python3 -B experiments/filesystem-service/check-namespace.py --mixed`,
`python3 -B experiments/filesystem-service/check-namespace.py --directories`, and
`python3 -B experiments/filesystem-service/check-namespace.py`. Their current host
runs passed 17, 23 and 8 entry tests, respectively, with 11, 31 and 5 compiling
semantic omissions. All 78, 242 and 48 selected commands met their expected
outcomes, including the directory selection's 18 legacy runtime host tests.
The tests use typed C fixtures, narrow Backend states and the existing descriptor
admission callback. Formatting and strict Rust checks retain pinned Rust 1.98.0
and the explicit edition 2021 migration.

The selected compile-only Owner/Zpl caller and minimal external non-LTO typed
boundary fit the existing limits:

| Selection | Code bytes (limit 49,152) | Conservative stack bytes (limit 8,184) | State plus workspace bytes (limit 8,192) |
| --- | ---: | ---: | ---: |
| Mixed | 10,576 | 3,096 | 1,112 Owner + 144 context + 4,096 workspace = 5,352 |
| Directories | 11,008 | 3,128 | 1,128 Owner + 144 context + 4,096 workspace = 5,368 |

The entry-reachable positive graphs contain creation and reopen paths; the
no-create controls have no reachable create/mkdir edge. The fresh Owner and
single-create caller may fold constructor-known preconditions. These are selected
caller measurements, not all-state worst-case, full-provider/system/native fit
or actual mapped-state proof. The workspace is a budgeted envelope, not measured
provider working storage. No native OpenZFS, public mktemp/libc or release gate is
qualified by these host and compile-only results.

The separate legacy bridge checker remains unavailable because its exact
historical prerequisites are missing; that default bridge algorithm is excluded
by cfg from this change. The available directory regression passed legacy host
behavior, but both exact-object and non-bitcode-object comparisons were false.
No byte equivalence, embedded-bitcode/LTO reproduction or fresh legacy native
acceptance is claimed; sealed historical artifacts retain their existing bytes.

The failed directory attempt 07 and three failed mixed fit attempts remain failed
in the compact evidence. They exposed an extreme-counter Clippy comparison, a
Rust/Clang library-path collision and the private ELF section oracle's confusion
between SHF_WRITE and actual RX load permissions. The diagnostic attempt retained
the actual section facts before the oracle correction; resource and mapping
limits stayed fixed. Successful runs verified frozen inputs, known child stops
and owned-output disposal. [Issue #88](https://github.com/gonz0w/Aether/issues/88)
links exact receipts and failures and owns live quality, separate review and
protected integration status.
