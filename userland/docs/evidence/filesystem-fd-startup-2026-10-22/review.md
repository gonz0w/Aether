# UL-007/081/082 startup batch — before code

Scope: explicit proposed AEFDB001/version1/304-byte startup envelope, sole greeting
consumer, actual native PID/PPID observations versus pinned AEFSH001 identity,
tagged128 map/seven native sources/two pipe histories/parent-only factory, existing
context admission, bounded short-read/wait handling and once-only failure cleanup.
Provide target entry reading actual auxv; no shell/libc interposition, old-profile
fallback, dispatcher or copy/exec implementation. This proposes required sibling
startup changes; it does not authorize sibling edits or assert owner acceptance.

O/I/E, CE/CD/CC/CP, TD/TC/TE and SE-01–05 apply. Mark startup attempted before
native operations, block signals for the complete consume/validate/publish boundary,
restore exact prior mask; restore failure retains native fail-stop125. No replay
or readmission after failure. Native endpoint labels alone grant nothing; actual
auxv/channel grant and owner dispatcher enforce authority. Observe0x10027/0x1006e
with zero arguments, reject native errors and cross-check memory/PID/PPID with the
verbatim identity decoder. Slot1 factory0x76050001, child2..4 factory0. History never
resets; reuse context validation for physical/logical correspondence and class
separation. Publish identity/context only after complete payload validation.

Place greeting scratch304 in stable caller-owned boot object beside the4600-byte
context, not a4096 automatic buffer. Startup temporary guard borrows endpoints
until ownership transfers to the admitted context; no second greeting client or
logical table. Failed admission closes both endpoints once and preserves raw close
results/attempted flag even if close fails. Clear scratch after success/failure.
No source close, owner settlement or native readiness claim. Attempt budget16384
is not a timeout; native wait still requires owner watchdog/stop.

Host exact ABI/identity and single-consumer oracles, all304 truncated payloads,
short chunks1..16/EAGAIN/wait/oversize/budget/malformed/identity/native-error/source/
factory/history cases, actual host pipe greeting and observed EOF, mask/restore
failure, reentry/readmission, publication/no-replay/cleanup. Keep175 context+193
native-call+482 live C/Rust cases/18 controls unchanged; new compiling semantic
omissions must fail exact assertions. Strict C17/format/UBSan; target14 production
objects/link/int81/actual auxv imports/layout/static frames,217 prior header pins.
Actual minimum/current Python. Existing pinned owned process helper,60s compile/
30s test/16MiB logs, all attempts retained and streaming-readback before removal.

Simplicity: composing independently read greetings would create multiple consumers
and permit mismatched identities/tables. A fixed explicit envelope is the smallest
reviewable proposal binding existing inputs; do not generalize to a bootstrap TLV
framework. Reuse context/native/identity codecs; remove no existing qualified
profile. Full shell/copy/immutable/failed-exec/resource fit/owner/native/reader gates
remain open. Independent owner acceptance is required before native selection.

## Implementing-agent review and actual results

Reviewed native argument widths/pointer lifetime, fixed bytewise codecs/no unaligned
casts, zero-argument PID/PPID queries, boot PPID7 and child memory/PID/parent tuple,
role factory restriction, nonzero opaque file generation, source/map correspondence
and persistent history. Admission uses one greeting reader and temporary native
signal guard, then transfers endpoint borrows to the existing stable context.
Native observations/query failure/header/body/identity/source rejection never
publishes identity/context. Raw channel closes/attempt flag retain failures; no
source cleanup or actual settlement inferred. Scratch clears on all returns after
attempt. Reentry/readmission never restarts an attempted greeting. No copy reset.

Early header validation rejects unknown magic/version/length at16 bytes before
waiting for the remainder. This is a stricter failure boundary added after the
initial801-case pass; final803 minimum/current passes use the same refined source.
All three passes retained. No failed qualification, suppression, production workaround
or old-format fallback. Other declared lengths do not expand bounds or allocate.
Actual native wait duration remains unbounded absent owner watchdog/stop.

Minimum3.10.21/current3.14.7 each pass803 startup+175 context+193 native-call+482
live C/Rust cases/88 prior host scenarios per child, five new/eighteen retained
compiling controls. All304 prefixes, opaque/nonopaque distinctions, all supported
identity combinations, persistent histories, real host pipe exact304/tail/EOF,
query/mask/cleanup/no-replay/publication and actual child125 have explicit oracles.
Host calls and control replies are injected; old Rust service source is unchanged.
Strict C17/format/UBSan and Rust/Clippy/unsafe checks pass.173 host dependency inputs,
217 prior native header pins and all tool/runtime/helper/source inputs verify.

Fourteen target production objects/link/import/int81 inspection,80 static frames/
max664 and separate boot4952/scratch304@4612/context4600/workspace4096@496 layout
qualify build only. Native getauxval plus four memory imports unresolved intentionally;
no executable, loader, allocation/peak-fit, native identity/mask or dispatcher witness.
Proposed startup changes require sys-init owner review before selection. Implementing-
agent technical review only; independent owner/reader, full linked shell/copy/
immutable/failed-exec/full-fit/dispatcher/native/UL/M3/R1 acceptance remains open.

Final quality, minimum/current syntax, tracked diff/scoped whitespace and input
preservation checks pass. Fifteen prior source deliveries/six evidence packets/
217 native headers verify unchanged. Three owned attempts were archived and every
regular member streaming hash/size verified before removal:44,591,712 logical bytes,
6,454,940 archive bytes retained. Final command receipts are retained separately.
Source-only56-member candidate seal is in candidate.json; final qualified minimum/
current source/checker remain exact. No independent sign-off inferred.
