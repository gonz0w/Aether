# Client mutation completion — UL-007/081/082

## Selected scope — 2026-10-24

The maintainer requested client mutation completion/error handling after
[AF09 service/client binding](FS-HOME-WIRE.md). This record owns that finite
slice through root [STATE](../../../.planning/STATE.md#system-work-index).
Owner: userland filesystem implementing agent. Base
`37902260234c188825f80c1fc016ad24d8ed0739` on `codex/consolidate-system`;
candidate `codex/fs-client-mutations`, target that unchanged consolidation branch.
Apply root PROJECT/METHOD/DEVELOPMENT, userland quality PROCESS and pinned
Foundations O-01–05/I-01–08/E-01–08 plus adopted CE/CD/CR/CA/TD/SE requirements.

Finite outcome: AF09-only Rust client write and typed namespace mutation calls
with complete validated completion/error receipts and once-only retirement. Use
the existing server operations and wire; no server, Owner or native profile change.
Non-goals: POSIX/FILE/process writes, shared offsets/append/truncate, automatic
retry/reconnect, home layout/provisioning, native readiness/fit/guests, new quotas,
SDK/pin promotion, durability, persistent Zsh/packages/ISO or release acceptance.

## Contract recorded before code

Add `Client::write(handle, offset, bytes)` for a live File with WRITE4, nonempty
1–4096 bytes and offset+length<=signed64 max. The server retains actual EOF/no-hole
enforcement: cached Entry.size is not authority. Reject empty writes locally;
this private API supplies no synthetic successful zero write. Opcode5/header then
64-byte padded data frames reuse existing framing and exclusive mutable access.

Add `Client::namespace(directory, NamespaceMutation)` for a live Directory with
LOOKUP1|MUTATE_DIR8. Typed operations are Create, MakeDirectory, Rename(from,to),
Remove and RemoveDirectory, mapping existing opcodes7,10,8,9,11. Each name is one
1–255-byte component, rejecting NUL/slash/dot/dotdot before any send; equal rename
names reject. Concatenate both rename names continuously (<=510 bytes) before
framing; padding occurs only at the end of the combined body. No path authority,
lookup/handle publication or raw operation selector is added.

Return `MutationCompletion { txg, bytes }` only after validating the complete
64-byte reply. Success requires exact magic/epoch/status0, word3=0, TXG>0,
word5=requested write bytes (namespace0), state2 and word7=0. This is provider
completion within the existing contract, not durability or a flush promise.

Every failure returns an immutable caller-owned
`MutationFailure { error, outcome, cleanup }`. Outcome is NotSent, Reported(progress)
or Unknown. Progress is Unassigned, Committed { txg, bytes_staged },
Completed { txg, bytes_staged } or Unknown. State1 is the producer's irreversible
COMMITTED observation, including its TXG0 anomaly; never label it pending or
retryable. Receipts retain copied observations after client abort/drop without
adding a Client field, outcome ledger, retry token or generation reset.

| Valid error reply | Returned reported progress |
| --- | --- |
| Canonical negative positive-i32 errno, state0/TXG0/staged0 | Unassigned |
| State1, TXG any, staged0 or full write length (namespace0) | Committed, preserving exact values |
| State2, TXG>0, staged0 or full write length (namespace0) | Completed, preserving exact values |
| EIO(-5), state3/TXG0/staged0 | Unknown |

All require exact magic/epoch, word3=word7=0. Namespace progress states1/2 also
require errno1–4095, matching the existing namespace producer; ordinary unassigned
errors retain its broader positive-i32 Backend error contract. Never expose a
partially validated progress tuple. Positive/out-of-range status, reserved data,
wrong size/state/TXG or malformed unknown markers become protocol Unknown.

Local validation/closed/binding failures before this call's first send are NotSent,
with current cleanup retained if already retired. Any send failure, even at the
header, may follow delivery and is Unknown. Send/receive loss or malformed reply
retires once without replay; returned cleanup contains both raw close outcomes.
Every canonical remote mutation error also retires, including Unassigned: payload0
cannot distinguish a pre-effect denial from a provider error that retired the
server. Success remains usable; no failure automatically retries or reconnects.
Subsequent calls fail NotSent/Closed and preserve the same cleanup without another
request or close. Caller retention of the returned receipt is explicit ownership;
no cached last-error value can overwrite an earlier outcome.

## Security, resources, simplicity and verification

Untrusted handle/name/data bytes cannot mint authority, mutate root/read aliases,
replay side effects or promote incomplete replies into success. Trusted endpoint
provisioning, service/Owner/backend remain in the TCB. Keep16 bindings, existing
connections/requests/data limits and permanent root/home slots. Use at most one
64-byte body frame at a time; no heap/workspace/unsafe/FFI/assembly/dependency,
Client fields, server wire or native quota change. Existing Rust2021 fixture
compiler/format conventions and pinned Rust1.98 stay selected.

Simpler alternative: call the read-only exchange helper and return errno only.
Insufficient: it discards committed/TXG/staged information and rejects legitimate
error payloads. Choose one private mutation reply parser and immutable returned
receipt using existing shutdown/transport helpers. This borrows the service's
explicit completion states and ownership; no general transaction/recovery system.
No frozen compatibility path can be removed yet. No complexity is removed now;
the added API is needed before truthful process/FILE write integration.

Write tests before implementation and retain the actual red result. Actual AF09
service/client tests must demonstrate write/readback, all five namespace operations,
exact completion and source rights, zero local effects on invalid input, server
Unassigned/Committed/Completed/Unknown failures and cleanup after retirement.
Scripted tests sweep header/body send loss, response loss, full4096-byte writes,
255+255 rename framing, signed-offset/name bounds, every completion/error field,
TXG0 committed anomaly, namespace errno limit and receipt persistence. Named
compiling omissions must fail for exact progress/retirement/framing/authority
reasons. Existing eight AF09 binding tests and affected AF07/08/sealed client
regressions remain; strict Rust/host/no_std/layout checks apply.

Command from `userland/` (registered before execution):
`PYTHONOPTIMIZE=1 python3 -B experiments/filesystem-service/check-client-mutations.py`.
Reuse the pinned owned-process helper,300-second suite deadline, bounded children,
private build output, source/tool freezing, explicit Python validation and compact
all-attempt results. Remove owned generated outputs. CLI follows the home checker
stdout help/version/JSON, escaped stderr and0/1/2/64 exits. Run affected standards,
workflow/userland quality/link gates and separate peer-agent review before local
integration. No native execution follows from these host/library checks.

## Implementation and review

The implementation adds one AF09-only module and returned receipt types; Client,
Binding, service and Owner layouts/wire remain unchanged. One64-byte buffer frames
both data and concatenated rename names. Existing shutdown owns once-only cleanup.
No heap, unsafe, quota, dependency or native-profile addition.

The new checker reuses the home runner's orchestration instead of copying its
pin/freezing/process/cleanup machinery. Existing default CLI and schema stay fixed;
optional in-repository parameters select the wrapper and its source freeze. Both
checks share one300-second deadline. This small refactor avoids two maintenance
copies of the same evidence contract. Both CLIs receive separate compatibility
controls; it does not add a public plugin/configuration interface.

## Results and separate review

[Attempt07](../evidence/filesystem-client-mutations-2026-10-24/attempt-07.json)
passes under Python optimization1:197 bounded children,13 mutation plus eight
binding tests, six new and six existing semantic controls,65 old host cases,
strict Rustfmt/warnings/Clippy and host/no_std checks. AF07/08/sealed clients expose
no new mutation API; old consumers/defaults and mismatch guards remain. Client
layout stays680/8 with host/target equality. Both CLIs pass help/version, escaped
usage64, missing/mismatched input2 and optimized explicit-oracle rejection. Root
standards/method/simplicity checks pass. Every failed attempt and complete cleanup
is retained. Current Python3.14.7 is tested; minimum Python3.10 is not established.

The first11 mutation tests preceded implementation and failed for missing APIs;
two direct service coverage tests were added after first green. Final controls
qualify only named semantic failures. Intermediate test/checker mistakes remain
failed observations; they did not require production changes. No broad suite or
native guest was run: affected userland libraries/host contracts select the focused
gate, and existing native approvals are consumed.

Peer agent `home_review`, separate from the implementing agent, reviewed final
production/test/checker source, attempt07, both CLIs and documentation against the
recorded base. Its [compact receipt](../evidence/filesystem-client-mutations-2026-10-24/peer-review-checks.json)
binds reviewed identities and validates all197 process results, six mutation and
six binding controls, frozen inputs and removal of all seven suite roots. It did
not rerun runtime tests. No unresolved implementation findings. Required semantic
markers and assertion lock lifetime were corrected; a README direction word was
also corrected. Root workflow41 references/37 tools/184 groups, userland quality,
17 scoped links/anchors and whitespace gates pass. Owned review outputs are removed.
This is ordinary peer-agent source/evidence review; no human, specialist, native
runtime, release or full draft-conformance acceptance is claimed.

## Status and continuation

Status: complete for the bounded AF09 mutation client, focused qualification,
separate review and local integration. The pre-code contract, actual compiler red
and every subsequent attempt remain in the
[compact evidence](../evidence/filesystem-client-mutations-2026-10-24/README.md).
Separate peer review and final process gates precede local integration. Old
seals/native inputs remain fixed. [Process descriptor writes](FS-PROCESS-WRITES.md)
now own the completed shared-position consumption and continuation toward FILE/C
write receipt/partial-write policy, native fit and fresh qualification.

## Observed local integration — 2026-10-24

Normal configured `.githooks` accepted
`36cd26ca6f9a2d0a6b5397f1f712871876959a1a`
(`feat(fs): retain client mutation completion and errors`). The unchanged target
`codex/consolidate-system` fast-forwarded from the recorded base to that commit.
Resulting tree `0ada764cc3d2dc8bf0d5e472ae9d8ae56943c11a` exactly matches
the verified candidate; the checkout was clean. `main` remains
`78c13fc5f5329bb590c2ab4772f2e1e2372dc067`. No remote action or guest ran.

The integrator rechecked all final source hashes. An initial index-only check
incorrectly included private ignored dependency files and failed at the sealed
producer LICENSE path; no source defect was inferred. Corrected verification
checks81 tracked inputs against the proposed index and78 retained dependency
files against their frozen hashes, all matching. This documentation-only closure
records observed identity and reconciles root selection/parent continuation;
separate narrow review precedes its normal commit and target fast-forward.
The [integration review](../evidence/filesystem-client-mutations-2026-10-24/integration-review.json)
records that scoped peer readback separately from the implementation review.
