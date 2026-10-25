# FILE mutation observations across reply delivery — UL-007/081/082, BG-069/070

## Selected scope — 2026-10-24

The maintainer requested continued service/client integration until blocked.
Following [home in-place construction](../../../userland/docs/proposals/FS-HOME-IN-PLACE.md),
this record owns the matched sys-init FILE peer observation seam. Owner: system
integration agent for sys-init/userland. Base
`cc7d6a33bb7379bcf9be477f665f6321bdd8188b`, candidate
`codex/fs-write-observations`, target unchanged `codex/consolidate-system`.
Apply PROJECT/METHOD/DEVELOPMENT, both component guidance/processes, pinned
Foundations O/I/E, CE/CD/CR/CA/TD/SE and the existing
[FILE RPC contract](../../prototypes/native-filesystem-session/FILE-RPC.md).

Finite outcome: a trusted Peer returns its copied write observation together with
independent reply-delivery status and raw local FILE endpoint cleanup, including
terminal source errors and uncertain sends. Old/default protocols remain usable;
old receipt-discarding consumers must reject AEFW dependencies. No native owner/
router activation, CWD merge, home layout/provisioning, new authority, persistent
ledger, retry/reconnect, quota, dependency, kernel ABI, VM, durability or release.
After this slice continue to actual matched owner composition and offline whole fit.
Consumed VM approvals remain consumed; a fresh disposition requires concrete
reviewed/prepared artifacts. No directory-boundary handoff blocks local integration.

## Contract before code

Select sys-init `fs_file_write_wire` explicitly only with matching userland AEFW0001
libraries. Compare the existing protocol MAGIC in both directions, using no new
symbol from old sealed consumers. Old `serve_one`/`serve_received` remain available
only on old selections; the new selected API makes discarding the mutation receipt
an explicit caller act. Existing native router/owner integration remains unselected
and must fail compilation if it tries the old API against the write profile.

Add a selected read-only `Connection::bound_process()` getter for its current
opaque Process key. It creates no key/authority and supplies no proof of native
admission. Peer copies this authoritative binding while the same exclusive
Connection validates and dispatches the request; it never uses a request-supplied
PID or a second process mirror. Caller still retains its authenticated endpoint/
holder association and native settlement duties.

New `ObservedWrite { process, receipt: FileWriteReceipt }` is owned Copy context.
New `Exchange { observation: Option<ObservedWrite>, delivery: Result<(), Error>,
cleanup: Option<[i64;2]> }` carries three separate facts. New
`serve_one_observed` and `serve_received_observed` return it on every normal path.
Copy receipt/context immediately after prepare and before the first reply send.
Return that copy after complete or failed header/body delivery, guard drop,
workspace clear and local/source retirement. Never publish a receipt on a request/body/preparation failure before entering
the typed write path. A validated write returning local NotSent still has its
typed receipt. An ordinary operation has None.
No error maps committed/staged progress to successful bytes or implies replay.
Mark the result must-use, document retained ownership and keep original transport/
protocol error identity. Delivery failure is independent of mutation completion.

Reuse the existing body/prepare/send path through one private inner operation with
a selected observation out-slot. No generic callback/trait or duplicate dispatcher.
Old selected code continues returning its original Result. Complete reply delivery
calls delivered exactly once; any error drops the guard and uses the existing
retirement/clear/once-only close path. After a delivered terminal source write error,
close the local Peer too, retaining both raw FILE closes separately from the source
close tuple in the receipt. A failed FILE close does not erase receipt or successful
reply-delivery observation. Closed calls return None/Closed with remembered cleanup,
clear the workspace and attempt no I/O. No process settlement, native reclaim,
engine export or recovery is inferred from either cleanup tuple.

Source Channel operations still promise complete bounded64-byte calls; partial
physical effects before Err are unknown delivery. Rust borrowing keeps the source,
connection and one4096-byte caller workspace exclusive. No persistent Peer/Connection/
ProcessFiles fields, heap, worker/channel or native limit changes. No new unsafe/
FFI/assembly boundary: existing transport objects remain compiled-only preparation.

## Simplicity, tests and documentation

Simpler alternative: keep returning only delivery Result. It loses the retained
mutation receipt when a send fails and cannot correlate terminal progress with its
bound process. Use one transient return value and one reused inner exchange, with
a read-only existing-key projection. Remove duplicated framing rather than adding
a recovery/logging framework; old protocol adapters remain needed by sealed users.

Before production, write tests and retain missing-new-API compiler red. Actual AF09
Owner/service/process/FILE tests cover successful write/readback, all terminal
progress states including COMMITTED TXG0, exact process/channel-generation/sequence/
FD/count/offset/source closes, ordinary and local NotSent outcomes, complete and
unknown delivery, request/prepare denials and no replay. Sweep128 reply-byte loss
prefixes using a Channel that can model partial physical output before Err; require
one source effect, copied completion after cleanup/drop and distinct raw FILE closes.
Also return exact unknown delivery if a callback emits all64 header bytes or all128
reply bytes and then returns Err. Exercise both entry points, bind/generation/closed
behavior, receipt retention across valid rebind/drop and terminal peer closure.

Named compiling controls must omit receipt capture, corrupt context, erase a
terminal receipt, omit source retirement on inbound loss, confuse cleanup tuples,
or omit terminal FILE close;
require exact semantic markers rather than compiler/watchdog/generic failure.
Old five-case Peer/actual-service regressions and affected composed owner tests,
old/new/stray profile guards and old-API borrow denials apply on host/target. Strict
Rust1.98/2024 sys-init and existing2021 userland fixture convention, warnings,
unsafe denial, Clippy/Rustfmt and no_std libraries apply. Complete owner fit and
fresh native witnesses stay separate. Reuse the597-check producer contract suite
with one shared300-second cumulative deadline, owned process cleanup and all-attempt
compact source/tool/header/runtime identities. Freeze sources during qualification.

From the system root run
`PYTHONOPTIMIZE=1 python3 -B sys-init/scripts/check-file-write-observations.py`.
Register the workflow before execution. Update FILE-RPC, component README and
Experience/quality inventories, parent/root continuation and compact evidence.
Separate peer contract/source/control/evidence/reader review precedes normal-hooks
local integration. Do not claim affected human/specialist/native or release sign-off.

## Status

Separate pre-code peer-agent review (`home_review`) finds no authority/lifetime/
design blocker. Incorporated local NotSent, physically-complete error and rebind/
drop cases; use an observable inbound-retirement control instead of a private
sequence change hidden by subsequent abort. Test compiler red precedes production.

Attempt01 is the pre-production compiler red after all597 producer checks pass:
the old Peer has no Exchange/observed methods. Six new integration cases already
exist, including130 incomplete/physically-complete error positions, typed local
NotSent, all terminal progress, exact context, malformed/inbound loss and rebind.
The result is an API compiler red, not a semantic runtime-red claim. Owned output
is removed and frozen inputs verify.

Attempt02 compiles the new APIs and passes five cases, then exposes a test-only
source-stop expectation: successful writes followed by client abort yield exact
Receive(-32), not service-generated Retired. Attempt03 retains a nonqualifying
control abort from holding a test Mutex during assertion unwind; copy the count
first to avoid destructor panic. Attempt04 passes720 children. Separate source
review finds no production blocker but requires exact full terminal rows/context;
these assertions and actual successful-loss backing-byte checks are added before
final attempt05, which passes the same720 checks with all957 frozen inputs and
complete output disposal. The six peer cases include130 physical loss/error
positions; seven compiling controls fail their named markers. Both old56-case
composed-owner suites, matched host/target/Clippy/format/unsafe-denial builds,
profile/old-router/borrow guards and producer597 cascade pass. No persistent fields
or native limits change. Native router/owner activation, whole fit and execution
remain unqualified; old sealed images/pins are unchanged. Current Python3.14.7 is
tested; minimum3.10 remains unestablished. Exact-source CLI/process checks pass15 children: both entry points' help/version,
escaped usage64, missing/mismatched pin2 and optimized false-oracle rejection,
plus all three sys-init offline pins. Separate peer agent `home_review` reviewed
the pre-code contract, source/ownership, observable controls, final receipts and
reader instructions, finding no unresolved production blocker. Its
[review receipt](../evidence/file-write-observations-2026-10-24/peer-review-checks.json)
records frozen/control reconstruction, root workflow, both component quality,
links/whitespace and owned-output cleanup. This ordinary peer review supplies no
human, specialist, native or release acceptance. Normal-hooks integration is observed below.

## Observed local integration — 2026-10-24

Status: complete for the finite matched Peer observation seam, qualification,
separate peer review and local integration. Normal `.githooks` accepted
`bb17a4534e7bbfff5499206cfd7006db73c37f9a`
(`feat(init): retain FILE mutation observations on delivery loss`). The unchanged
`codex/consolidate-system` fast-forwarded from the recorded base. Tree
`97cf8161defeabae588009c9873042c1cd74eb2e` equals the reviewed staged candidate;
checkout was clean. Main remains `78c13fc5f5329bb590c2ab4772f2e1e2372dc067`.
The integrator verified225 qualified source blobs against the proposed index before
commit. No source, dependency pin, tool or native input changed after qualification.

This documentation-only closure reconciles parent/root continuation and observed
identity. Its [separate narrow review](../evidence/file-write-observations-2026-10-24/integration-review.json)
precedes normal closure commit/fast-forward. Next candidate: matched home-aware
owner/router construction and retained observation handling, followed by concrete
native whole code/data/stack fit and exact preparation. No guest, push, old-image
refresh, recovery policy or release acceptance follows this integration.
