# FILE mutation receipts and C adapter — UL-007/081/082

## Selected scope — 2026-10-24

The maintainer requested continuing until blocked after the completed
[process-write foundation](FS-PROCESS-WRITES.md). This record owns the next finite
slice: versioned FILE home opens/writes, retained mutation receipts and explicit C
client/facade interoperability. Owner: userland filesystem implementing agent.
Base `65ee4aaf40a85f3c7f137bac66892bbaa8058a18`, candidate `codex/fs-file-writes`,
target unchanged `codex/consolidate-system`. Apply root PROJECT/METHOD/DEVELOPMENT,
userland quality PROCESS, pinned Foundations O/I/E and adopted CE/CD/CR/CA/TD/SE.

Non-goals: CWD/general writable paths, create/namespace/append/truncate, libc/routed
file-write activation, native startup/owner/in-place/fit/guest adoption, quotas,
pins/seals, automatic retry/reconnect, POSIX zero/partial-write translation,
durability or persistent Zsh/packages/ISO acceptance. After completion continue
toward the next matched integration gate; do not stop merely because this slice ends.
Consumed guest approvals remain consumed; any required fresh disposition must be
for concrete reviewed/prepared artifacts, not an abstract permission request.

## Contract before code

Select `fs_file_write_wire` / C `AEFD_WRITE_WIRE` explicitly, with matching AF09
process writes, root-path reads and16-alias replacement prerequisites. Require
path/dup2 wire selection and reject CWD/in-place. New magic is AEFW0001; old
AEFD0001/AEFP0001–3 and all current native/startup selections remain unchanged.
Old FILE still rejects AF09; new FILE rejects old brokers/services. No peer-driven
negotiation. Existing authenticated Connection/process/generation/sequence,
body validation, one4096-byte caller workspace and delivery guard remain.

Requests retain eight little-endian64-bit words: magic, opcode, nonzero exact
channel generation, expected sequence, a,b,c,d. Sequence starts1, never admits
u64::MAX and never resets on transport failure. Existing opcodes1–7 retain their
contracts. Add10 home_open: a=cloexec0/1,b=name length1–255,c=access0 ReadOnly2 /
1 WriteOnly4 /2 ReadWrite6,d=0. Its padded body is one existing home component;
NUL/slash/dot/dotdot reject. It cannot widen root-path reads or create a file.
Add11 write: a=remote FD0–15,b=count1–4096,c=d=0, padded input bytes (arbitrary
including NUL), zero tail. Validate complete header/body/padding and exact bound
process before one source operation. No synthetic zero write or write-all loop.

Ordinary replies keep the64-byte layout and old canonical error/body rules.
Home-open returns ordinary FD or errno, with no body. Write always returns a
64-byte header plus exactly64 receipt bytes, even on a validated terminal source
error. Header words: magic,status,generation,sequence,count-on-success-else0,
body64,0,0. Status is the existing errno mapping. A partial/malformed reply never
publishes header-only count or progress. Source retirement must not discard the
one retained write receipt; it makes the FILE connection terminal after this reply.

Receipt words0–7 are flags, attempted_offset,txg,staged,source_close0,
source_close1,error_kind,error_value. Flags low3 bits:0 NotSent,1 ReportedUnassigned,
2 ReportedCommitted,3 ReportedCompleted,4 ReportedUnknown,5 Unknown,6 success;
7 invalid. Bit3 means offset present; bit4 means source cleanup present; other bits
zero. Inactive fields must be zero. Present offset<=signed64 max; a sent/successful
write must have offset and a valid offset+requested range. Success requires flags14,
TXG>0,staged=requested, no closes/error. Reported states require source cleanup,
offset and original Source(Remote(errno)); tag1 TXG/staged0, tag2 any TXG /
staged0 or requested, tag3 TXG>0 /staged0 or requested, tag4 only EIO(-5) and
TXG/staged0. Unknown requires offset/source cleanup, no TXG/staged and original
Source(Protocol) or Source(Transport(raw)). NotSent preserves local error and any
existing cleanup, with TXG/staged0; no offset means no live description selected.
Neither success nor completed/TXG promises durability.

Original error_kind mapping (error_value0 unless shown):1 BadFd,2 Full,3 Invalid,
4 Overflow,5 Retired,6 InvalidCompletion,7 SourceInvalid,8 SourceClosed,9 SourceFull,
10 SourceProtocol,11 SourceTransport(raw signed64),12 SourceRemote(negative
positive-i32 errno),13 Identity(raw signed32),14 Stale,15 Busy,16 Generation.
Status must equal the existing errno mapping for that exact cause/value. NotSent
accepts local causes, excluding Protocol/Transport/Remote. Unknown accepts only10/11;
reported accepts only12. Zero/status0 is success only. No new generic errno API.

`PreparedReply::write_receipt()` returns an owned Copy observation including
exact generation, sequence, FD, requested count and success {offset,completion} or
original ProcessWriteFailure. The selected `Connection::bound_process()` getter copies its current opaque key
for the [matched peer](../../../sys-init/docs/decisions/0223-file-write-observations.md);
it grants no native authority or proof of admission.
The trusted dispatcher must copy this before
attempting delivery and retain it through uncertain sends/cleanup. Dropped,
forgotten/pending or partially delivered guards retire without replay; copied
observations survive cleared workspace and dropped broker. The dispatcher retains
the authenticated Process/endpoint correlation alongside that copied context. `delivered` clears
workspace and advances sequence once but never revives a terminal connection.
No persistent outcome ledger or Client/ProcessFiles/Connection field is added;
only the selected transient reply guard holds its receipt.

C `aefd_client_write` requires a caller-owned output receipt and retains context
(generation/sequence/FD/count), complete remote receipt when validated, and its
own local FILE close tuple separately. An explicit observation discriminator
distinguishes validated remote receipts from synthesized NotSent/Unknown, and
local FILE cleanup has a separate presence indicator and raw tuple. Return1 means complete validated remote
receipt, including errors;0 is local invalid arguments/no I/O;-1 is local FILE
retirement. Once any transport callback is attempted, incomplete send/receive or
malformed header/body yields Unknown, never NotSent or trusted partial progress.
An already retired client returns current-call NotSent with retained FILE closes.
Copy the whole validated receipt before terminal abort clears/releases workspace.
No last-error field or automatic replay. Keep the single16384-attempt transfer
budget across request header/body/reply; partial transfers continue one frame,
only -11 waits, without resubmitting a request. Input/output/client/workspace are
valid disjoint exclusive ranges; callbacks are nonreentrant and duration-bounded.

Explicit C facade `aefd_file_open_home` uses component-only validation despite
root-path selection; `aefd_file_write` requires the output receipt, returns full
validated count or negative private errno, and never turns staged/error bytes
into success. No libc/POSIX/routed writer is switched. Generic exchange rejects
opcode11 locally so old metadata paths cannot silently discard its receipt.

## Authority, resources, simplicity and tests

One existing authenticated service/client and description owner remain authoritative.
FD/name/magic/sequence are selectors, never grants. Native endpoint authentication,
actual copy/admission/settlement, supervisor recovery and package policy stay with
their owners. Preserve root3/home15 attenuation, four process views,16 aliases,
13 descriptions, actual12-free-owner-handle configuration,16 service bindings,
4096-byte workspace and all native ceilings. No heap/new unsafe/FFI/assembly,
channel/worker, native ABI/profile or dependency. New C uses existing pinned
Clang21.1.8/C17 strict diagnostics/format/UBSan and declared freestanding checks;
Rust1.98/2021 fixture conventions persist. No unrelated formatting migration.

Simpler alternative: use ordinary errno-only FILE replies. Insufficient: the
current retired-source rule erases committed outcome, and the C facade cannot
reconcile a lost shared-position write. Use one fixed receipt frame, copied
outcome and existing guard/transport algorithms. Borrow accepted explicit
completion/shared-open ownership, not a generic transaction/recovery framework.
No compatibility code can yet be removed while old native consumers remain sealed.
The added cost is required for one truthful next write consumer.

Write tests before production and retain actual pre-integration compiler red.
Actual Rust FILE/process/AF09 service tests cover home access/readback, shared
positions/flags/close, terminal receipt delivery despite retired source, all exact
progress/attempted-offset/cleanup values, owner copies surviving dropped success
and error guards, sequence/forgotten guard rejection and no replay. Sweep malformed
headers/body/tails/versions and semantic/local denials before source effects.
C codec/client/facade tests must consume actual Rust replies and produce actual
Rust-consumed requests, sweep every receipt field/state/cause and sent/received
prefix loss, protect unpublished output/workspace, distinguish both cleanup tuples,
retain TXG0 committed and reject partial progress, verify16384 budget/waits and old
profile regressions. Named compiling controls must fail their exact semantic
markers, not compilation/timeout/generic panic. Strict Rust/Clippy/C/format/UBSan,
no_std/freestanding builds, mismatch guards and affected older consuming suites
apply; whole native fit remains separate.

From `userland/` run
`PYTHONOPTIMIZE=1 python3 -B experiments/filesystem-service/check-file-writes.py`.
Register before execution; reuse pinned owned-process and checker orchestration,
one300-second cumulative budget, final source/tool/header/runtime/seal freezing,
compact all-attempt evidence and complete owned-output disposal. Update experiment
README, Experience/coverage/workflow and parent/root continuation. Separate
peer-agent contract/source/evidence/doc review precedes normal-hooks integration.

## Status and continuation

Pre-code contract and separate peer-agent contract review preceded implementation;
no blocker found. Eight Rust cases plus new C codec/client/facade tests were written
before production. Attempt01 fails from a Rust LLVM path leaking into Clang;
checker now isolates C tools. Attempt02 is the planned missing-C-API compiler red.
Attempt03 passes new C unit/prefix matrix but Rust test compilation fails because
its body helper expects a fixed array instead of a validated slice. During review,
a newly introduced C preprocessor branch also inverted old name validation;
attempt04 reproduces that with the existing old client test. A clear shared
name-staging branch and a test-only slice reader correct both. The initial scope in attempt05 passes354 children before its deliberate remaining-gates
placeholder failure. Expanded signed-value/actual terminal-C tests were added afterward,
not part of the pre-code red. Attempts06–09 retain test-oracle, native dependency-scan,
linker environment and named-control qualification corrections. All attempts remain
retained in `docs/evidence/filesystem-file-writes-2026-10-24/` with complete cleanup.

Final attempt10 passes452 bounded children with29 Rust cases and11 new compiling
semantic controls, old C1631 schedules,320 predecessor checks, strict host/target
Rust/Clippy/C/format/UBSan, profile guards and freestanding C relocatable linking.
All919 frozen inputs verify before complete owned-output disposal. The C maximum
individual frame328 is not whole executable/call-stack acceptance. Actual live C
success and terminal error retain the exact receipt. No persistent owner fields, native limits or
libc/routed write activation are added. Current Python3.14.7 is tested; minimum3.10
execution is not established. Exact-source CLI/process gates pass17 children. Separate peer agent `home_review`
reviewed the pre-code contract, production/test/checker source, retained receipts
and final documentation, with no unresolved production finding. Its
[review receipt](../evidence/filesystem-file-writes-2026-10-24/peer-review-checks.json)
records input reconstruction, workflow/quality, links/whitespace and complete
owned-output cleanup. Review corrections include complete header/format-input
freezing and exact signed-value/live-C assertions. This is ordinary peer-agent
source/evidence/reader review, not human/specialist/native or release acceptance.
Normal-hooks local integration is observed below; see the
[compact evidence](../evidence/filesystem-file-writes-2026-10-24/README.md).

After integration continue with matched home in-place construction, then C/native
owner placement and offline fit. No native placement or guest is prepared or
authorized by this slice. Scope authority, resource exceptions and fresh native
execution remain owner gates; passing libraries and continuing work cannot renew
consumed approvals.

## Observed local integration — 2026-10-24

Status: complete for the bounded FILE/C receipt slice, qualification, separate
peer review and local integration. Normal `.githooks` accepted
`35b2b16853db6b2e8cc5ea65c99f0a59336ad6c9`
(`feat(fs): retain FILE write completion receipts`). The unchanged
`codex/consolidate-system` fast-forwarded from the recorded base. Tree
`15b561dc90886974d3b97aa0e0155feee66f642c` equals the reviewed staged candidate;
checkout was clean. Main remains `78c13fc5f5329bb590c2ab4772f2e1e2372dc067`.
The implementer also checked187 qualified source entries against the proposed
index. No source, pin, tool or native input changed after qualification.

This documentation-only closure reconciles the parent/root continuation and
observed identities. Its [separate narrow review](../evidence/filesystem-file-writes-2026-10-24/integration-review.json)
precedes the normal closure commit/target fast-forward. [Home in-place construction](FS-HOME-IN-PLACE.md) now owns completed consumption
and continuation through the matched dispatcher/native owner and actual whole fit.
No push, guest, libc activation or native acceptance follows this integration.
