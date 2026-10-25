# Single-consumer startup batch — 2026-10-22

UL-007/081/082; [proposed contract](../../proposals/FS-FD-STARTUP.md),
[pre-code plan/review](review.md), [observations](summary.json), [candidate](candidate.json).
Implements one explicit AEFDB001/version1/304-byte greeting consumer, native PID/
PPID versus pinned identity checks, context/table/source/history admission,
single publication/borrow transfer and terminal failed-start channel cleanup.
This is a proposal/client, not sys-init acceptance, a selected shell startup or
native execution. No sibling edits/messages, guest, installation, profile/default/
quota/release-pin change, copy/exec implementation or monitoring.

Final actual Python3.10.21 and3.14.7 each pass803 startup scenarios, unchanged175
context/193 native-call/482 live C/Rust cases,88 prior host scenarios per child,
five new/eighteen retained compiling semantic omissions. Startup covers138 valid
shell/child identity combinations,20 persistent history cases, all304 valid-payload
truncations,16 short chunk widths/EAGAIN,292 corrupt nonopaque bytes,12 accepted
opaque label variants, native/auxv/zero-file-generation/factory failures, unknown
wait/oversized transfer/budget/mask errors, early incompatible headers, actual
host pipe exact304 consumption with following TAIL and EOF, reentry/readmission,
publication/scratch clearing/raw close results and child exit125 on restore failure.

Omitting magic validation, trusting a PID label over actual native query, omitting
factory role restriction, resetting pipe history or skipping channel cleanup must
compile and fail an exact intended assertion. Native queries require all-zero
argument registers; blocked signal guard spans the complete admission. No source
commands run during greeting validation. Failure preserves unadmitted context/
identity, closes borrowed channels once and never consumes another greeting.
Invalid endpoint tuples cannot establish a borrow and have no close claim.

Host native calls/control replies are injected. The real host pipe tests greeting
bytes/read-ahead/EOF only; they do not qualify native mask, identity, IPC grants or
console enforcement. The retained482-case suite separately executes actual Rust
handler/process/AF07 service with synthetic storage. Native enforcement/dispatcher/
copy/TLS/immutable exec/failed-or-unknown-exec state preservation remain unrun.

Strict C17/format/UBSan and retained Rust2021/rustfmt/default Clippy/unsafe checks
pass.173 host dependency inputs,217 exact native header pins, all tools/resources/
runtimes/helper, fifteen prior source closures and verbatim identity decoder are
verified/rechecked. Fourteen production ELF64/x86-64 objects relocatably link;
imports are getauxval plus memcmp/memcpy/memmove/memset. Actual int81 backend remains
inspected. Native entry's getauxval import and PID/PPID opcodes are build evidence,
not execution. Eighty static frame reports/max664 bytes exclude call chains,
callbacks/libc/interrupts and full backing/heap/stack/channel/resource fit.

Separate unlinked layout probe: boot4952 bytes, scratch304 at4612; embedded
context4600 bytes/workspace4096 at496. Caller must place the complete boot/context
outside init's4088 usable stack; no global allocation/instance or physical mapping
is selected here. All native borrows and source/factory permissions still require
actual authenticated owner enforcement, not arithmetic/frame labels.

The56-member source-only handoff is
`build/service-deliveries/filesystem-fd-startup-2026-10-22-v1`, manifest SHA256
`709a2c0f33b3cbf8dbecc3143d2976d5dd9093120cb4460eb41f697805147094`.
Exact context51 predecessor sources plus startup/header/native entry/host tests,
verbatim identity header, checker snapshot, proposal/license/vendor/dependency
receipts. Checker snapshot expects maintained repository layout; reproduce with
contract commands, not from the delivery directory. No SDK/engine/linked shell copy.

[Retention](retention.json) and [driver](retention-driver.py) preserve all three
passing owned attempts in attempts.tar.xz. Initial801 scope retained; final consumer
rejects bad16-byte header before waiting for a nonexistent incompatible payload,
and two dedicated mismatched-profile tests bring final scope to803. Final actual
minimum/current source/checker match. No failed qualification, suppression, source
workaround or fallback. Every source/checker, command/environment/deadline,16MiB
stream bound, process cleanup and artifact remains retained. One streaming hash/
size readback of all regular members precedes exact root removal. Logical bytes
are not physical reclamation measurement. Current Python/lzma retention remains
separate from minimum qualification. Quality/input/source/final command receipts
accompany seal; independent owner/reader review remains pending.

Next: wire libc/shell FD entry points and sole startup into coherent linked shell;
explicitly replace old64-byte table and process snapshot/copy/exec framing,
authenticate child rebind/file generation/source history/TLS repair, preserve
immutable image/failed-or-unknown-exec parent/FD state and select actual whole fit.
Sys-init must review/implement this proposed greeting and full dispatcher/readiness/
shutdown, then Aether fresh commands/errors/cleanup/readback. Wait attempt bounds
are not timeouts; owner stop/watchdog/settlement remain mandatory. Full UL/M3/R1/
POSIX/TTY/Zsh/package acceptance and bootable native shell remain open.

Retention removed44,591,712 logical bytes from three verified attempt roots and
kept6,454,940 archive bytes; physical reclamation was not measured. Quality gate
(all three pinned standards checks/draft inventory), minimum/current syntax,
git diff --check, scoped source whitespace and input preservation pass.
[Verification](verification.json) and verification.tar.xz retain final owned
commands/cleanup; the verification root was removed after streaming readback.
Fifteen predecessor source deliveries, six prior evidence packets and217 native
headers verify unchanged. Independent owner/reader review remains pending.
