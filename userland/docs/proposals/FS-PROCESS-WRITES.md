# Shared process descriptor writes — UL-007/081/082

## Selected scope — 2026-10-24

The maintainer requested continuation after [client mutation receipts](FS-CLIENT-MUTATIONS.md).
This record owns the next finite foundation through root STATE: explicit AF09
existing-home-file opens and serialized shared-position process writes. Owner:
userland filesystem implementing agent. Base
`50bfe167322de7b4655a6ed6c0e10826fe007606`, candidate `codex/fs-process-writes`,
target unchanged `codex/consolidate-system`. Apply PROJECT/METHOD/DEVELOPMENT,
userland quality PROCESS, pinned Foundations O/I/E and adopted CE/CD/CR/CA/TD/SE.

Non-goals: FILE/C/libc/startup wire changes, general path/CWD write resolution,
create/namespace/append/truncate, zero-write POSIX semantics, partial-write
translation, reconnect/replay, native/in-place placement/readiness/fit/guests,
new quotas/dependencies, pins/seals, durability or persistent Zsh/packages/ISO.

## Contract before code

`fs_process_writes` explicitly requires AF09/fs_home_wire, process views,
fs_paths, fs_file16 and fs_replace. Reject CWD and in-place selections for this
finite library phase. Old/default and AF07/08 remote guards remain. All current
FILE protocols explicitly reject AF09 by existing service MAGIC, including when
the new remote broker is valid; no new symbol is required from sealed dependencies.
Old connect still refuses AF09 before input; only `ProcessFiles::connect_home`
consumes both greetings before publishing the broker. Authentication, nonreused
service epoch, native admission and settlement stay trusted caller duties.

`open_home_file(process, name, HomeAccess, cloexec)` validates the exact current
process and reserves existing alias/description capacity before lookup. Access is
ReadOnly2, WriteOnly4 or ReadWrite6. Name is one existing component1–255 without
NUL/slash/dot/dotdot. Resolve only against the retained home handle; no caller base,
path-prefix authority, home creation or widening of root/open_read. Reject directory
results, closing their temporary handle before returning existing Remote(-21).
Failed close retires admission. Client bindings remain sole rights authority;
no mode/rights copy is added to a description. Dup/replace/inherit preserve the
same handle and thus cannot amplify access.

`write(process, fd, bytes)` returns the existing exact MutationCompletion on
validated full success. Under one exclusive mutable broker borrow, validate exact
process, live FD/description, nonempty count1–4096 and signed64 offset+count before
one Client::write at the shared offset. Advance that description only on success
by its validated count. All dup/inherited aliases observe the same position;
independent opens remain independent. No framing-level write-all or automatic
retry. Reads/seeks/flags/close/exec/settlement retain existing algorithms.

Failures return caller-owned `ProcessWriteFailure { error: ProcessError,
outcome: MutationOutcome, cleanup: Option<[i64;2]>, offset: Option<u64> }`.
Offset is the selected shared position once a live description is validated,
including later local/source failures; None means no live description was selected.
Retain this attempted location because retirement makes position() unavailable.
The caller correlates the receipt with its process/FD/input invocation. Local process/FD/count/range
failures are NotSent with current cleanup; they preserve active state and positions.
Client errors retain exact original Error inside Files(Source(error)), exact
outcome/progress and both raw cleanup values, including COMMITTED TXG0. Any retired
client retires all descriptor views; process records remain occupied/unsettled.
Never advance offsets on error, publish staged bytes as a successful transfer,
guess an uncertain cursor or reopen/reset after failure. Subsequent calls are
NotSent/Retired with the same cleanup. Copies survive broker drop. Endpoint cleanup
is not native settlement, engine export, durability or successful recovery.

## Authority, resources, simplicity and tests

Use one existing service/client and one authoritative description ledger: four
process views,16 aliases per view,13 shared descriptions,16 client bindings. No
new field, heap/workspace, unsafe/FFI/assembly/dependency/channel/worker or native
budget. Retained root/home and provisioning consume slots: the tested source pair
leaves12 free owner handles, so remote Full can occur before13 local descriptions
fill. Test this real exhaustion; no capacity claim beyond exact provisioning.
Existing exclusive Rust borrowing serializes calls and prevents reentrant alias
mutation; it is not native endpoint authentication or a concurrent POSIX lock.

The simpler alternative is errno-only writes through the old read adapter. It
would erase irreversible progress, guess offsets and silently widen root/FILE
consumers. Choose a small AF09 process extension using existing capacity,
lookup, client receipts and descriptor lifetime algorithms; only internal offset
visibility changes. Borrow the accepted shared-open-instance ownership and
fail-closed uncertain-I/O model from FILE-DESCRIPTORS/SERVICE-IO. No complexity can
be removed yet while frozen consumers require old profiles. Do not introduce a
generic mutable Store trait or a second rights/offset/error ledger for one adapter.

Write tests before code and retain actual pre-integration compiler red. Actual AF09
service/Owner tests cover shared dup/inherit/replace offsets, independent opens,
readback, access attenuation/root denial, CLOEXEC/settled final close and12-handle
exhaustion. Scripted tests cover every receipt state, malformed/lost replies,
header/body send loss, raw failed closes, local invalid/stale/bounds and no replay.
A real successful backend write with lost reply must have exactly one effect.
Named compiling controls omit home binding, success offset advance, failure
retirement, receipt progress or exact process validation; only exact semantic
markers qualify. Old13-/16-slot process libraries/tests, current FILE guard,
AF07/08 mismatch, strict Rustfmt/warnings/Clippy, no_std and layout checks apply.
Rust1.98/2021 fixture conventions remain; no unrelated migration.

From `userland/` run
`PYTHONOPTIMIZE=1 python3 -B experiments/filesystem-service/check-process-writes.py`.
Register before execution. Reuse pinned home/mutation runner orchestration and
owned helper, one300-second cumulative deadline, source/tool/seal freezing,
explicit Python oracles and compact all-attempt receipts with disposal. Both
existing and new CLI defaults/streams/exits stay under Experience; update README,
Experience/coverage/workflow. Focused affected gates and separate peer-agent review
precede normal-hooks local integration. No native execution is selected.

## Implementation and qualification

Separate peer-agent contract review preceded implementation and found no blocker;
its attempted-offset recommendation is incorporated above. All twelve tests were
written before production; the first eleven preceded the initial guard/compiler
red, with the signed-limit case added afterward before implementation. The small
extension uses existing capacity and lifetime algorithms; Description.offset alone
gains internal visibility. No fields or generic mutable Store API are added.
The mutation runner accepts an optional deadline, preserving its default while
allowing this wrapper to enforce one cumulative300-second budget. Only scoped
stale authority/profile comments required correction after source review.

[Compact evidence](../evidence/filesystem-process-writes-2026-10-24/README.md)
retains every failed/incomplete attempt and actual result. Final attempt05 passes320
bounded children:12 process/eight binding tests, six new plus twelve existing
semantic controls,13 client mutation cases, baseline65 old host cases and34/11
old process cases. Host/no_std, strict warnings/unsafe denial/Rustfmt/Clippy,
old/mismatched/FILE guard checks and unchanged1464/8 broker layout pass. All frozen inputs verify and owned
outputs are removed. Native
execution and complete owner fit remain untested. Current Python3.14.7 is tested;
minimum3.10 execution is not established. Root standards/method/simplicity and changed/new CLI compatibility gates pass.
The unchanged base CLI reuses prior byte-identical checked behavior.

## Separate review

Peer agent `home_review`, separate from the implementing agent, reviewed the
pre-code contract and final production/test/checker source, receipts and documents.
Its [compact review](../evidence/filesystem-process-writes-2026-10-24/peer-review-checks.json)
binds reviewed identities,320 complete/clean child results, all eighteen named
controls,163 frozen inputs, three compiler tools/native libraries and removal of
all five suite roots. It did not repeat runtime tests. The attempted-offset issue
was resolved before implementation; three stale comments were corrected before
final qualification. No unresolved findings. Fresh root workflow41 references/
37 tools/185 groups, userland quality,13 scoped links/anchors and whitespace gates
pass. Owned review/quality output is removed. This is ordinary peer-agent source
and evidence review, not human/specialist/native execution or release acceptance.

## Status and continuation

Status: complete for the bounded process-write foundation, final-byte
qualification, separate review and local integration.
[FILE receipts and the explicit C adapter](FS-FILE-WRITES.md) now own completed
consumption and the next owner/in-place integration, whole-fit and fresh native
qualification sequence. This process-only phase supplies no POSIX write acceptance.

## Observed local integration — 2026-10-24

Normal configured `.githooks` accepted
`882926e2c4fec96f863dd4857e11a867c4b85e43`
(`feat(fs): preserve shared process write outcomes`). The unchanged
`codex/consolidate-system` fast-forwarded from the recorded base to that commit.
Tree `7a00e6120b4e085e4b5f0b9de8755d170c75912b` matches the verified candidate
exactly; checkout was clean. `main` remains
`78c13fc5f5329bb590c2ab4772f2e1e2372dc067`. The integrator rechecked85 tracked
inputs against the proposed index and78 retained dependency files against frozen
hashes before commit. No source/pin/consumer change followed qualification.

This documentation-only closure records observed identity and reconciles root
selection/parent continuation. Its [narrow peer review](../evidence/filesystem-process-writes-2026-10-24/integration-review.json)
is separate from implementation review and precedes normal commit/target
fast-forward. No remote action, guest, FILE or native adoption follows.
