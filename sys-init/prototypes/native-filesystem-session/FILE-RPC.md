# FILE peer delivery and mutation observations

## Selected AEFW0001 observation API

[Decision0223](../../docs/decisions/0223-file-write-observations.md) owns the
explicit `fs_file_write_wire` consumer and its current qualification status.
Match userland AEFW0001 dependencies; default peers reject that selection and
selected peers reject old wires. Old `serve_one`/`serve_received` stay available
on old selections. They cannot silently discard receipts under AEFW.

Use `serve_one_observed` to receive a header, or `serve_received_observed` with a
complete header from this same authenticated Peer under exclusive owner admission.
Keep the returned must-use `Exchange`: `observation` is an owned bound Process plus
exact FileWriteReceipt when the typed write path ran, `delivery` records complete
reply delivery or its original error, and `cleanup` retains local FILE closes.
The receipt's source close tuple is separate. Retain the authenticated endpoint/
holder association; a copied Process is an opaque broker selector, never native
authority. The Connection projects its existing key without a second mirror.

A validated write returning local NotSent still has a receipt. An ordinary operation
or a failure before typed-write preparation has None. Copy occurs before the first
reply send. A completed source write can have unknown delivery, including an error
after all reply bytes physically leave the callback. Guard drop, workspace clearing,
source/peer retirement and later object drop do not erase that owned observation.
No staged/error bytes become successful count, automatic replay or durability.

A delivered terminal source error closes the local Peer too; keep exact raw FILE
close results even if they fail. Repeated closed calls return None/Closed and the
remembered cleanup without I/O. Settlement, engine export/native reclaim and any
recovery remain caller-owned. Channels must remain bounded/non-panicking; normal
returns do not prove unwind recovery. No persistent Peer field, extra workspace, channel,
worker or native quota is added. Decision0224 owns the explicit home owner/router adoption and complete offline
fit; native activation remains separate. Existing sealed profiles/artifacts stay unchanged.

## Home owner consumer

[Decision0224](../../docs/decisions/0224-home-owner-fit.md) selects the home owner.
Under AEFW, `poll`/`poll_exec` return `Event::File(FileEvent)` containing the whole
Exchange and independent exact admission Result. An Ok event means the event was
observed. It does not mean admission, mutation or delivery succeeded. After outer
retirement, FILE cleanup is refreshed from the Peer. The receipt-discarding
`dispatch` helper is absent on this selection.

FILE classification completes after all64 header bytes. Failure after the first
matching16-byte prefix stays an exact gate error with no fabricated File event
or receipt and no source write. Complete malformed headers/body failures can
produce a File event without a typed write receipt.

Runtime stores the event with the current trusted native index, identity and
context generation before checking admission and delivery. `last_file()` exposes
the retained normal-return copy. `source_cleanup()` projects current sole-source
raw closes, including retirement after the original receipt was copied; it is
independent of FILE closes and never rewrites mutation progress or settles native
instances. Once-only run/fail-stop prevents uncertain
outcomes being overwritten through retry. Source/FILE closes and native resource
settlement remain distinct. No retained result survives owner crash by contract.

## Earlier read-only selections

Current mixed-owner selection,decision0210: `serve_received` accepts the complete
64-byte header already received from this same authenticated Peer under exclusive
owner admission, then shares the existing input/body/prepare/reply path. Every
Connection validation, output delivery, source retirement and once-only peer close
remains. `serve_one` still receives its own header and delegates to that path;
five existing FILE regression cases pass. `with_channel` gives only a scoped
callback borrow to the trusted router, without Process/generation rebinding.
The compiler rejects escaping that borrow; actual endpoint authentication and
effects on partial messages remain owner obligations.

The [mixed-channel router](FORK.md)
closes the gate before classification. No header prefix is read outside admission,
no second channel/cache/ledger is added, and an idle peer may be skipped only
before consuming any bytes. See [review](../../docs/decisions/0210-unified-owner-routing.md).

[Decision0196](../../docs/decisions/0196-file-rpc-exchange.md) prepares
fd_dispatch.rs, a separate no_std crate using the selected userland v3 handler.
It is not imported into the accepted init owner/default or linked ABI29 shell.
No new file operation/wire or service framework is introduced.

## Trusted binding and exchange

Peer::bind takes an already authenticated application Channel, opaque current
ProcessFiles key and nonreused channel generation. It owns peer-close obligations
including bad generation rejection. These selectors authenticate nothing; actual
native admission/endpoint holders/directions remain enforcing-boundary duties.
Every operation revalidates current membership through the sealed v3 handler,
including unsupported opcodes. Earlier superseded v1 is not selected.

serve_one borrows ProcessFiles and caller-owned4096-byte workspace. It clears the
buffer, receives one complete64-byte header, asks the actual Connection for bounded
padded name bytes, receives only those frames into workspace and prepares once.
It holds PreparedReply while sending the complete response header and every padded
body frame. Only full success calls delivered; semantic errno replies may then
continue at the next sequence. It does not parse/reimplement file operations.
The automatic request header is64 bytes; there is no4096-byte automatic buffer.

Any receive/header/body/prepare/send error retires the shared file source and peer,
clears workspace and closes peer endpoints once. Source and peer raw cleanup
results remain separate. A partial response may follow an effect: no resend,
reconnect, resynchronization or speculative rollback. Repeated serve on a closed
peer clears the caller buffer and returns Closed before I/O. close/Drop only close
local peer endpoints, not source/process settlement. The trusted owner separately
settles file views and native processes; Drop cannot prove a successful shutdown.
Native builds abort on panic; host unwinding/panic=abort native failure cleanup is
not established by normal-return tests. The selected handler deliberately retires
all four file views after one uncertain peer; no generic failure isolation claim.

Channel implementations must return Ok only after the complete64-byte operation
and bound each call. The existing endpoint/Framed adapter supplies <=16-byte chunks
and100000 attempts per frame; the C transport uses16384 attempts per whole exchange.
Neither establishes a common wall-clock deadline or permission to expand lifecycle
limits. Whole-operation deadline/admission/cancellation remain owner integration.

## Input and evidence scope

Selected inputs: process15-member seal
`95e67913a455612039941eaeafa96ff6b90add7661efe0470c8a70f6d3fdda27`,
wire20-member v3 seal
`ad1c8082948e08c1e2cc507dd2b069540699e20d9fe97852eadb390a63a4eabf`,
unchanged service77-member seal
`98a9fd12db4ecd1c736fe3ce332c9b69c631e043d4d87313827145675ba230a8`.
The live C test selects its separate nine-member client seal
`eac972b501518c97f67d483aafe6186ea2b5863dfaad26930108d4d7d290c48c`.
These are experiment inputs, not a shared SDK/release pin transition.

[Evidence](../../docs/evidence/file-rpc-exchange-2026-10-21/README.md) records
five actual handler/process/client/service host tests with synthetic storage,
three compiling guard omissions, strict Rust/default Clippy and native generic
library generation. Two fresh host pipe sessions use the actual C client rather
than captured-response replay: ten complete exchanges; then lost-body retirement,
unchanged failed reply metadata, cleared output and no retries. Short7-byte C
callbacks/EAGAIN exercise both directions. All child processes stop and AF07
fixture threads join. Strict C17/UBSan, headers/resource/runtime/tool pins are
recorded. No native IPC, OpenZFS client, shell, native holder or peak-fit claim.

Exact source copies, compiler/test argv, runtime outputs, scopes and pins are in
preparation.json; reproduction wrappers/drivers are inert evidence. Build copied
verified libraries with fs_process_views plus existing AF07 feature flags, then
host-test the supplied wrappers with explicit extern paths. Native no_std build
is generic-library preparation, not a concrete linked executable or fit witness.

## Remaining owner handoff (local, unsent)

The typed file-only facade is now delivered and consumed on host (decision0197).
Userland still needs to select it in the linked shell and define startup/FD-table
routing for files, console and pipes. Existing linked ABI29 clients do not speak AEFD0001.
File FD3–15 is this broker's namespace, not permission to reinterpret old pipe
bindings by numeric range. Specify exact binding types, process/fork inheritance,
path/cwd behavior and failed-exec parent/FD preservation. Readonly handles, sizes
or digests do not authorize immutable executable admission; loader policy belongs
to the relevant userland/package/kernel owners, not to this transport wrapper.

The composition must choose ProcessFiles/peer/workspace placement, endpoint
ownership and one greeting/readiness consumer. A4096-byte read workspace plus
state cannot be assumed to fit init's4088-byte usable stack. Keep existing code/
stack/heap/backing/channel/lifetime limits until concrete linked evidence resolves
fit. Sys-init still owes full startup/copy/exec/wait/endpoint/readiness/shutdown
composition; Aether must qualify exact assembled native command/error/cleanup/
fresh-readback witnesses. No second Owner/SPA, RAM-only shell substitute, sibling
edit/message, new guest campaign or formal release acceptance is introduced.

## Typed facade compatibility — decision0197

Selected12-member source seal
`695b758f7d37547ad7ee14f01f0fbfe68cb73549aa69029cc612411b2c5260ce`
keeps the selected C transport/codec unchanged. tests/fd_dispatch_facade.c links
actual aefd_file_* calls to the unchanged server over live host pipes. Positive
ten exchanges cover shared offsets, semantic closed-FD errors including an actual
zero read, untouched short-read tail and local invalid inputs with no I/O. Lost
body leaves caller output untouched, clears private workspace and retires without
retry; both raw local closes are observed once. Three compiling copy/tail/retired-
error omissions fail exact C assertions. Strict C17/UBSan/format and full input/
header/runtime checks pass. [Evidence](../../docs/evidence/file-facade-consumption-2026-10-21/README.md)
reuses the exact prior server artifact/source closure; all owned processes stop.
This file-only seam introduces no local FD ledger or libc symbol. Full linked
shell startup/FD routing, copy/immutable exec and native placement/fit remain open.

## Mixed descriptor helpers — decision0198

The selected32-member replacement candidate seal
`5b43ec90ed2481b618d0b23e4801b9dde18d5997bbcd319e611f984824cd7183`
brings current canonical routing/table/stream/write/pipe helpers; all ten dependency
deliveries and process15 verify separately. tests/fd_dispatch_mixed.c composes
these helpers with unchanged Peer/actual handler/service through live host pipes.
The included tests/native_fd_mixed_server.rs reuses the existing App and fixture.
Five cases check distinct logical/source FD numbers, actual pipe bytes/aliases/
redirection/final-close EOF, file shared offsets and complete EOF, loss/staleness
and uncertain stream closure both with/no physical effect. Actual resource-owner
cleanup is separate from admission retirement. Three selector/alias/unknown-close
omissions compile and fail exact C exits. Strict C17/UBSan/format and Rust/Clippy/
format pass. [Evidence](../../docs/evidence/mixed-fd-consumption-2026-10-21/README.md)
records exact artifacts and all owned processes stopped. No runtime source changes.
The helpers are delivered; selected linked shell/startup/native adapters, native
copy/immutable exec/failed-exec preservation and full placement/fit remain open.

## Session and FILE redirection — decision0199

Selected redirect41 seal
`1f808da2135af11be7a8225975a645a15a9b02d4ce84c3991ebea6d728901140`
and session36 seal
`7aa7a9c15d12f83a9c76655397557cf1f0aed48191becd9ce884bc9bd701131d`
compose the exact predecessor helpers without another map/client or new file wire.
tests/fd_dispatch_session.c and included tests/native_fd_session_server.rs use
unchanged Peer/actual handler/process/service. Six live host cases verify shared
FILE offsets after replacing a pipe target, actual old-target EOF, known-refusal
prepared rollback, lost dup/cleanup headers, unknown target with/no physical close,
projection and cached finish/raw local closes. Three cleanup/publication/unresolved
omissions compile and fail exact C assertions. All owned processes stop; strict
C17/UBSan/format and Rust/Clippy/format pass. [Evidence](../../docs/evidence/session-redirection-consumption-2026-10-22/README.md)
retains exact inputs/tools/artifacts. Host receipts are not native settlement or
atomic POSIX dup2. Selected linked shell/startup/authenticated native adapters,
copy/immutable exec/failed-exec and full placement/fit remain owner prerequisites.


## Separate physical-CWD integration

The monorepo's `fs_cwd_wire` selection uses FILE `AEFP0003` with AF08 source
libraries. Operation8 carries a1..255-byte path with a zero-padded body; operation9
returns a physical absolute NUL-terminated path,2..256 bytes, only after complete
header/body delivery. Both use the existing authenticated process key, generation,
sequence, owner gate and4096-byte workspace. Malformed/partial state retires the
source and all local views without replay. No native kernel ABI or grant changes.
The existing startup/map002 and fork/exec02 geometry is retained; do not invent a
new geometry version for a FILE operation. Old FILE versions reject CWD libraries.

Build the producer with userland's `check-directory-contexts.py`, the matching C
provider with `check-fork-stage.py --exec --paths --dup2 --cwd`, then run
`scripts/check-broker-init.py --libraries OWNED_PRODUCER --compact-compare
--unified-route --compose-owner --guarded-stack --exec-provider OWNED_PROVIDER
--paths --dup2 --cwd` from sys-init. These are offline/fit gates; native execution,
actual non-root directories/home provisioning and persistent Zsh remain separate.
The owner forwards these operations through the shared Connection implementation;
there is no duplicate syscall/path policy or second CWD ledger in sys-init.
See `userland/docs/proposals/FS-CWD.md` from the system root for authority/lifetime/
error contracts and exact focused coverage.
