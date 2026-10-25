# Placed descriptor context batch — 2026-10-22

UL-007/081/082; [contract](../../proposals/FS-FD-CONTEXT.md), [pre-code plan/review](review.md),
[observations](summary.json), [source candidate](candidate.json). This batch wires
native48/session/redirection into one stable context, validates startup table/source
agreement, automatically guards every FD operation and caches terminal reporting.
No startup wire, greeting consumer, linked shell, source policy or native profile
is selected. Existing sources/deliveries and ABI29 shell remain unchanged.

Actual Python3.14.7 and3.10.21 final runs each pass175 new context host scenarios,
193 prior native-call scenarios,482 existing live C/Rust cases and88 prior host
scenarios per child. Six new compiling omissions plus four native/eight older
controls fail exact intended assertions: missing source, orphan source, omitted
local-operation guard, omitted redirect guard, lost finish cache and omitted
transport cleanup after mask failure. No native authority follows from labels.

New tests cover all seven physical stream selectors with valid/alias/missing/orphan
maps, FILE/PIPE selector overlap, invalid table/native inputs, corrected pre-admission
retry/readmission refusal, every FD wrapper's reentry/guard, file open/read/seek/
flags/dup/close, local stream aliases/replace/projection, pipe publication/finish,
committed FILE/stream redirect and known FILE-target rollback with all RPCs under
one mask,128 file header/body prefixes, stale-map retirement, cached unknown finish,
mask failure and child exit125 after restoration failure. Real host pipe writer
close/EOF and a lost write's actual bytes are independently observed. Retired-active
reentry does not abort the outer operation. Known failures preserve their existing
private errno/target-FD contracts; no new POSIX success or source replay.

The context fixture injects exact native-call arguments and scripted file/control
replies. It is not a duplicate file policy, native dispatcher or enforcement
witness. The unchanged482-case suite executes the actual Rust handler/process/AF07
service with synthetic storage. Native193 tests retain short transfer/EAGAIN/wait/
generation/malformed/unknown boundaries. Host real effects and injected responses
remain separate from Aether execution, native signal behavior and service authority.

Strict C17/format/UBSan and Rust2021/rustfmt/default Clippy/unsafe checks pass.
169 host dependency inputs,217 exact prior native headers, tool/resource/runtime/
helper pins and native48/fourteen source closures verify/recheck. Twelve production
ELF64/x86-64 objects relocatably link with only memcmp/memcpy/memmove/memset unresolved;
backend disassembly still contains int81. Seventy-five static frame reports have
maximum664 bytes in context initialization, excluding call chains/callbacks/libc/
interrupts. A separate unlinked layout object measures context4600 bytes,
workspace4096 bytes at offset496. No production writable static or allocator is
introduced. The context CANNOT reside on init's4088 usable stack; actual off-stack
mapping/placement/peak backing/heap/stack/channel fit still requires owner selection.
Objects/layout do not demonstrate native executable loading or runtime enforcement.

The51-member source-only handoff is
`build/service-deliveries/filesystem-fd-context-2026-10-22-v1`, manifest SHA256
`a7638088c36fca3b061a76affd193c1eacd55b023b4a537be0db045b7b518317`.
Exact prior sources plus context/header/host tests, checker snapshot, contract,
license, vendor/dependency/qualification receipts. The checker snapshot expects
the maintained repository layout; use the contract's reproduction commands rather
than running it from its delivery directory. No SDK, engine, executable or shell
copy is added. Inputs are pinned before build consumption; moving siblings are
inspected for current owner status, never silently compiled into this packet.

[Retention](retention.json) and [driver](retention-driver.py) preserve all six owned
attempts in attempts.tar.xz: four failed fixture/control preparations, then matching
final175 current/minimum passes. Raw errors, checker/source snapshots, commands,
environment/deadlines/16MiB stream bounds, artifacts and complete process cleanup
remain retained. summary.json records exact dispositions. The failed control exposed
a redundant check; the final single comparison is exercised independently in both
directions. No equivalent omission is counted as a successful negative control.
Every regular member's hash/size is read back in one streaming pass before exact
root removal. Logical byte accounting is not physical reclamation measurement.
Current Python/lzma retention is separate from minimum qualification. Local quality,
minimum/current syntax, whitespace and final source/input receipts accompany seal.

Implementing-agent technical review only; independent owner/reader pending.
Remaining: selected shell/startup with one authenticated greeting consumer, explicit
old64-byte installed table/process snapshot adaptation, child channel/source/file-
generation/TLS rebind, immutable image/failed-or-unknown-exec parent/FD preservation,
concrete full placement/fit, matching sys-init dispatcher/readiness/shutdown and fresh
Aether commands/errors/cleanup/readback. Native wait still needs owner watchdog/stop;
attempt bounds are not timeouts. No native guest, sibling edits/messages, installation,
release pin/default/quota change, monitoring, POSIX/job-control/SIGPIPE/full M3/R1/
TTY/Zsh/package acceptance or copied-context authority is claimed.

Retention verifies59,146,455 logical bytes from six attempt roots and keeps
10,883,036 archive bytes; physical disk reclamation was not measured. Final quality
gate (all three pinned standards checks and draft inventory), minimum/current
syntax, git diff --check and scoped source whitespace pass. [Verification](verification.json)
and verification.tar.xz retain exact final owned commands/cleanup; its temporary
root was removed after streaming readback. Fourteen predecessor source deliveries,
five prior evidence packets and217 native headers verify unchanged. Independent
owner/reader acceptance is still pending.
