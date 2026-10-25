# Chosen-target FILE replacement — UL-007/081/082

2026-10-23. Pre-code contract and review. Root STATE owns integration. This is an
opt-in fs_replace Rust primitive and separately approved fs_file16 ledger below
the FILE wire and public libc dup2. The foundation sections record their original
scope; the matching-consumer contract/results below now select the new protocol
and public binding. Native execution and general POSIX conformance remain open.

## Requirement and failure contract

Replace one process view's remote FILE descriptor at exact target3–15 with an
alias of a validated source FILE descriptor. It must work with all13 FILE slots
occupied, without allocating a spare FD, description, source handle or new field.
Keep one authoritative Descriptions ledger and use its existing reference scan.
A clone-shared description retains its offset; a distinct target's old description
remains live in any other process/view until its last alias closes.

Validate live view/process and both indices before effects. Invalid/missing source
or out-of-range target returns BadFd without source calls, map/offset/flag changes
or closing the victim. A valid source==target preserves CLOEXEC and performs no
source close. Distinct success returns target, clears only its CLOEXEC, keeps
source/unrelated descriptors unchanged and shares source position. A missing
target is allowed. The trusted local description indices must reference real
occupied descriptions; an internal inconsistency retires instead of publishing.
ProcessFiles::replace performs its existing exact opaque process-key/generation
validation; neither numeric FD nor process labels grant authority.

Under the exclusive serialized mutable borrow, install the new alias first, then
scan all views for remaining references to the old target description. Close the
old underlying source handle exactly once only when no references remain. The
new source alias participates in that scan, so same-description replacement never
closes it. On successful close release the old description slot. Any failed or
unknown source close retires the entire shared ledger/source and returns failure;
there is no usable replacement, continuation, rollback, re-open or automatic retry.
No recoverable close-error/POSIX victim-preservation claim follows after retirement.
A future public bridge must convert uncertainty to its real fail-stop outcome,
not report an ordinary recoverable failure with a usable partial table.

No new native/grant authority, AF07 operation, heap, unsafe boundary, mutable global,
backing, channel, worker, file/handle quota, watchdog or transaction allowance.
Existing defaults/APIs/sealed deliveries/release pins and all wire bytes stay exact.
The existing private non-atomic aefd_redirect is not renamed to public dup2.

## Security, simplicity and checks

Apply current O/I/E, approved CE/CD/CA/TD and SE-01–05 through the existing review
process. Protected state is the shared description/offset/alias ledger; untrusted
inputs are FD selectors and stale process keys. Exact process binding, capacity,
last-reference cleanup and close uncertainty must remain explicit.

Simpler alternative: duplicate to a spare FD then close/move the target. It fails
when the13-slot table is full and adds partial-close cleanup. Reuse the actual
bounded alias table and reference scan instead; no second counter/retirement queue
or new resource pool is needed. Compatibility remains opt-in; no obsolete native
path is removed until a complete consuming replacement is qualified.

Use the actual ProcessFiles/Remote/AF07 service over host synthetic storage:
full-table distinct replacement/shared offsets/CLOEXEC; self/same-description and
empty target; cross-view retention until last close; invalid/stale/settled process
with no effects; failed close retires once and cannot expose a replacement/replay.
Keep37 existing in-place producer cases; test default producer separately if changed
behavior escapes the selected branch. Compile semantic controls for wrong target,
CLOEXEC, skipped last close and premature cross-view close, requiring actual test
assertion failure rather than compiler error. Strict Rustfmt/Clippy/unsafe checks,
host and freestanding libraries. Compare concrete layouts; selected native whole
owner fit and runtime acceptance remain separate. Current Python runs; minimum
runner missing coverage stays explicit. Preserve compact attempts/hashes/commands
and remove owned generated outputs, without source/binary archives.

Before execution, the focused checker adds --replace to
`python3 -B experiments/filesystem-service/check-process-descriptors.py --in-place`.
Combined --paths remains separately selectable and requires its existing client.
Update README/quality coverage and root workflow/STATE. Technical review is by the
implementation agent; independent/native and complete public dup2 acceptance remain
pending. Next the authenticated FILE/C mixed-table protocol must consume this
primitive with exact source/target ownership and full-table semantics before any
public libc/redirection claim.

## Public bridge capacity decision, before implementation

The existing C map has16 logical slots0–15, while the remote FILE view admits
only13 selectors3–15 and startup requires one unique remote selector per local
FILE entry. With all13 remote FILE entries live, redirecting a FILE onto stdin
would require a14th remote alias even though replacing a logical stream slot.
The private duplicate-then-close path cannot satisfy that full-table case. The
Rust primitive fixes FILE-to-FILE replacement, not this mixed-class mismatch.

Propose a separate versioned view allowing16 FILE aliases at0–15, retaining only
13 shared open-description objects,16 AF07 client bindings, four process views
and the existing16 logical C slots. Do not grow source handles/descriptions to16:
new aliases need no extra source handle. Keep default3–15 profiles and all current
wire/startup versions unchanged. Exact compile-time version propagation must
cover client, FILE handler, C codec/map, fork/exec/startup validation and owner;
wrong/mixed versions fail before effects, never auto-negotiate or reinterpret.
Public dup2 semantics and consumed/unknown close handling remain a further reviewed
integration contract. No new native syscall, authority, worker, channel or VM.

First measure only the actual Option<Descriptor> type's array geometry using the
pinned Rust compiler, without selecting or implementing the larger view. Compare
four arrays of13 and16 slots; keep the13-entry description array unchanged. This
is prospective data-layout evidence, not native code/data/stack acceptance or
permission to change the currently selected FILE slot bound. The current-limits
instruction required explicit disposition for that13→16 extension; the maintainer
approval and implemented library slice are recorded below.
Any implementation still has to fit49152 owner code/8192 stack/data,35MiB/seven
domains/twelve channels, current handle/workload/time/capture limits. Stop on fit
failure; no implicit resource increase. This extends a needed shell capacity
contract, not a generic VFS or extra compatibility matrix.

## Initial13-slot results and capacity measurement

Implemented only the fs_replace exact-target3–15 primitive.41/42 selected/combined
path cases and19 compiling controls each pass, retaining all existing producer
cases; strict format/Clippy/host/freestanding libraries pass. Two initial test-only
compile/lint failures remain retained; production replacement body unchanged.
No wire/C/libc/kernel/default or numeric-bound change is selected. Native witness
at commit7d6d0e44c remains scoped to that frozen path/read composition; later native
work needs fresh matching inputs and complete selected-owner measurement.
[Compact evidence](../evidence/filesystem-file-replace-2026-10-23/README.md).

Read-only actual type geometry: Option<Descriptor>=2 bytes; four13-slot arrays104,
four16-slot arrays128, delta24. Keeping13 descriptions means no extra source-handle
capacity; whole owner code/data/stack fit remains unmeasured for that proposal.
This measurement preceded the16-slot approval and implementation below. It did
not select a larger profile or authorize a native guest.

## Approved 16-slot library profile —2026-10-23

Maintainer approved a separate16-slot FILE view, selectors0–15, for host and target
build testing only. Keep13 shared descriptions,16 AF07 bindings, four process
views and every other resource/authority/time limit; no VM execution is authorized.
The earlier pending-decision paragraphs record the preceding scope, not a current
approval request. Implement as fs_file16 plus fs_replace; default3–15 is unchanged.

Separate the alias array length from the13-entry description array, including
unsafe in-place initialization. No new fields, pool, reference counts or handles.
Aliases0–2 are remote FILE selectors, never console rights or local FD identities.
Open chooses the lowest free alias; it still rejects a14th shared description
before source lookup. Duplicate/replacement may populate all16 aliases without
new source handles. Presence/CLOEXEC masks use every bit0–15. Fork, exact generation,
exec-close and settlement must scan the complete selected view and retain one
shared offset/source handle until its final alias closes across all four views.
Errors before effects and failed/unknown close retirement retain the prior contract.

First qualify the real ledger over AF07 synthetic storage: full16 aliases/13
source descriptions, capacity rejection before lookup, low selectors, masks,
shared offsets, self/distinct replacement, inherited victim lifetime, generation
reuse/unknown copy, failed close/read/invalid completion and poisoned in-place
initialization. Old default/paths replacement profiles remain regression selections.
Use --file16 with --in-place --replace, optionally --paths, in the existing checker;
strict format/Clippy and host/x86_64-unknown-none libraries, compiling semantic
controls and concrete layout comparison remain required. A compile-time fence
must reject use by the old FILE protocol before effects. A matching explicit wire,
C map and fork/exec/startup consumer is a following integration step, not an excuse
to reinterpret the old protocol. Complete selected-owner code/data/stack fit must
pass before selecting it for native acceptance; library size is not whole fit.
Keep49152 code/8192 data/guarded stack and all other limits unchanged. No VM,
released pin update, independent sign-off or public dup2 claim follows here.

## Library checkpoint before matching consumer implementation

The separate fs_file16/fs_replace ledger now passes15 host cases/21 compiling
controls in both component and canonical-path selections, plus strict Rust checks
and freestanding libraries. Old13-slot selections pass41/42 cases/19 controls each;
old FILE protocols pass10/11 cases/eight controls each. Legacy protocol builds
reject a16-slot producer before effects on host and target. No wire interpretation,
public libc/C map, kernel or native input is changed. Four harness failures remain
retained; no production correction or relaxed oracle hid an unexpected result.

Concrete test-Channel ProcessFiles grows1440→1464 bytes, exactly24; single-view Descriptors
grows1128→1136 (+8) and target const checks agree. The whole selected owner fit is pending,
not extrapolated from that ledger measurement. No guest ran. [Compact results and
limitations](../evidence/filesystem-file16-2026-10-23/README.md). Next define and
implement the matching explicit FILE/startup/C map/fork/exec consumer version,
then public mixed-class dup2 with real fail-stop handling; qualify complete owner
code/data/stack before preparing any new native composition. This is engineering
work in the monorepo, not another external alias-bound approval request.

## Matching consumer and public dup2 implementation contract —2026-10-23

Maintainer directs matched protocol/startup integration and public dup2 under the
current limits. Select fs_dup2_wire only with fs_path_wire/fs_paths/fs_file16/
fs_replace/process views. Use AEFP0002 for FILE, AEFDT002 for the128-byte map,
AEFDB002 for the304-byte startup, AEFORK02 for fork requests and AEEXEC02 for exec
requests. Headers retain their existing shape/version lane1; their distinct magic
selects this exact profile. Pure unchanged ready/refusal receipts keep their old
32-byte encoding, authenticated per live channel/sequence. Old defaults and sealed
inputs retain every byte. No autodetection/fallback. C AEFD_DUP2_WIRE requires
AEFD_PATH_WIRE. Propagate one trusted build selection through the codec, table,
startup/fork/exec, actual shell/provider and owner; mismatched Rust components fail
at compile time, foreign C/Rust frames before effects. No kernel API change.

New FILE opcode7 has source/target0–15 in lanes4/5 and zero lanes6/7, no body.
The owner invokes existing ProcessFiles::replace under its serialized route guard.
Success returns exactly target, no body. The C client validates both the selected
range and exact returned target; malformed/partial/lost outcomes retire without
replay. Earlier wire profiles keep opcode7 unsupported with canonical zero args.
Existing opcodes1–6 accept low selectors only in the new version; descriptor
allocation uses the lowest free remote alias, independent of local C FD numbers.

Public dup2 remains selected only in this version. Validate the live generation,
whole local map shape/unique FILE selectors and both local FD indices before
source effects; invalid/missing source or invalid target returns EBADF preserving
source/target/flags/offsets. Self returns target preserving CLOEXEC with no RPC or
close. Distinct success clears target CLOEXEC and shares source description/offset.
The existing context native mask/guard serializes the whole operation against
signal/fork/exec snapshots. No new state or unguarded helper is published.

FILE→FILE invokes opcode7 on source/previous target selectors, reuses the target
selector and publishes only after confirmed success; full16 aliases need no spare.
FILE→empty/stream prepares one free remote alias first. A stream target implies
at most15 FILE aliases in the16-entry map, so the new range supplies a spare.
Reject alias collisions/malformed results terminally; never close a purported
collision. Then close the old stream only if its last local alias disappears.
A known unconsumed close error preserves the target, cleans up the prepared alias
with checked close, then returns the original error. Unknown close/cleanup retires,
never replays/rolls back uncertain outcomes. A known consumed stream close error
is ignored for dup2 as its target was closed; install the prepared alias/source.
Stream→FILE closes the exact old FILE alias before publishing the source stream;
known no-effect errors preserve the target; failed/unknown last-source close is
terminal through the FILE owner. Stream→stream uses the same checked last-alias
close rule. Source stream aliases need no new native grant/holder within one view;
existing fork capture/holder publication remains authoritative across processes.

Private helpers may return failure with retired admission, but public dup2 must
actually call the existing nonreturning exit path141 when its live started context
retires. It may not expose recoverable EIO and resume with unknown/partial state.
Keep pre-start errors ordinary; busy/reentrant guard returns EBUSY without teardown.
No blanket POSIX conformance: only this selected bounded FD subset is qualified.
Old stream_replace/private structured redirect remain distinct compatibility APIs.

Tests: actual Rust handler/AF07 service and C/Rust/C vectors, malformed low/high
selectors/reserved/generation/sequence/foreign version/drop/close uncertainty;
full table, FILE/FILE/stream/empty matrix, source validation/self/flags/shared
offsets, collision/known no-effect/consumed error/unknown/cleanup failure; actual
public errno and nonreturning fail-stop body with a host exit observation. Include
compiling semantic omissions for exact-target validation, alias/flag rules,
uncertainty retirement and public fail-stop. Run selected/default focused protocol,
C fork/exec/readiness/libc and Rust owner checks, strict format/Clippy/UBSan and
freestanding whole shell/helper/owner links. Compare actual C/Rust fork/exec/startup
bytes and reject foreign versions. Complete owner must fit49152 code/8192 data/
guarded8192 stack (8184 usable); maintain35MiB/seven domains/twelve channels,
16 AF07 bindings/13 descriptions/four views, current transactions/watchdogs/capture.
Stop on actual fit failure, do not raise limits. Record compact attempts/hashes;
remove owned generated trees after readback. No VM is authorized by preparation;
changed persistent composition still needs its scoped disposition. Current Python
only; minimum runner, independent review/native acceptance stay explicit.

Simplicity: spare-then-close alone fails at full FILE capacity and cannot preserve
unknown outcomes. Reuse the one Rust replacement and existing C map/native guard
with one selected opcode, rather than a second FD ledger, transaction protocol,
generic VFS or kernel syscall. No obsolete qualified path is removed before its
replacement has native consumer acceptance. No dependency, write authority,
writable-home policy or released standard pin change. Implementation-agent review
only; independent owner/reader/release sign-off remains separate.

## Fixed native probe selection and preparation

The --exec --paths --dup2 --path-probe immutable helper keeps the existing
13-byte AF07-READ:ok marker/fixed exec-wait script. After opening /zstd read-only
with CLOEXEC it verifies self-dup2 preserves flags, duplicates to local10, replaces
the original FILE from10 with CLOEXEC clearing, duplicates the FILE onto stdin,
reads16 bytes through stdin, seeks the shared original to780248-byte EOF and
checks EOF through10 and the original. Close every known created alias and the
original; any failed step returns non7 and qualification stops. No filesystem
mutation or disk executable loading. Independent full-file/media readers remain
mandatory.19 host actual-body outcomes exercise each known failure and cleanup;
public binding tests separately prove uncertain outcomes cannot resume. Same code,
stack/data/backing/handle/worker/channel/watchdog/transaction/capture limits.
Preparation may refresh private source-matched dependencies, preserving all old
seals/released pins; changing the preparation recipe invalidates old live-source
input receipts even when the engine executable is identical. Explicit checked
provider reuse verifies reports/profile/source/tool/artifact correspondence and
borrows their owned output trees until the caller compacts/removes them; no generic
cache or automatic reuse. No guest execution without the required disposition.

## Matching consumer host/build result

AEFP0002/map002/startup002/fork02/exec02 and public dup2 are implemented and pass
the focused families in [compact results](../evidence/filesystem-dup2-owner-2026-10-23/README.md).
Complete selected owner41360/49152 code,7528/8192 data and7992/8184 conservative
stack fit; old path owner40640/7504/8000 remains exact. Source-matched diagnostic
images/receipt are prepared, no VM ran. The next gate is fresh scoped persistence
disposition for the exact changed composition; prior native read approval is
consumed. All bounds, authority, media/full-file/recovery/wait/cleanup oracles and
stop/no-retry remain. Writable home/CWD/loader/packages/Zsh/TTY/ISO are still open.

## Bounded native consumer witness —2026-10-23

The explicitly approved pristine reader → selected owner/helper → fresh recovery
sequence passes on the prepared frozen bytes. Public self/CLOEXEC, local10/exact
FILE replacement, FILE→stdin/read16/shared EOF/checked close yield one marker and
helper7/parent0/engine0,21 cleanup rows,327 paired waits and halt1936/6000. Both
readers verify the complete780248-byte original file; recovery preserves stopped
writer media/canaries, all VMs stop. [Compact results/disposition](../evidence/filesystem-dup2-owner-2026-10-23/README.md).
Current limits unchanged, zero FS mutation requests; metadata import/export may
write. No source changes/retry/extra guest. Generated outputs removed and approval
consumed. Host rejection/mixed/full-table coverage remains distinct from this one
native success workload; independent durability and full Zsh/ISO remain open.
