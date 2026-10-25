# Source-backed redirection batch — 2026-10-21

UL-007/081/082: receipt-based FILE/PIPE/CONSOLE redirection, preparation, target
close, rollback cleanup and session entry in one batch. [Contract](../../proposals/FS-FD-REDIRECT.md),
[plan/review](review.md), [final results](summary.json), [candidate](candidate.json).

A FILE source prepares a real remote duplicate before target effects. Only complete
success publishes. Known failures clean only confirmed fresh unpublished duplicates
while live; unknown/collision never retry or close a purported existing selector.
Receipt retains target and cleanup errors, consumed holes and unresolved allocation,
including unnamed lost-dup effects. No spare logical FD required; spare remote
capacity is required. This bounded API is not atomic POSIX dup2. Original stream-
only replace remains unchanged; new `aefd_session_redirect` handles all classes.

Actual Python3.10.21/3.14.7 each pass:

- 269 preceding live file cases plus213 new live C/Rust cases (482 total);
- all88 preceding host integration scenarios per C child;
- eight compiling omissions requiring exact C assertions and observed failed child;
- strict C17 diagnostics/format/UBSan and Rust2021/default Clippy/rustfmt/unsafe;
- nine freestanding x86-64 C objects and a separately inspected relocatable link.

New cases:21 scenarios and192 partial-header losses at preparation, target close
and rollback cleanup. Actual unchanged Rust handler/process/AF07 policy uses
synthetic storage over real host pipes. Tests prove shared offsets/flags, rollback
FD rejection, all-class target handling, empty/self/alias/full logical and remote
capacity, known error continuation, consumed error, unknown with/no physical close,
stale source/target/cleanup, duplicate collision and AF07 body/count/close faults.
Host stream bytes/EOF/close, RPC ordering/no unknown replay, AF07 lookup/final-close
counts, C exit/source join and backend/transport drop are independent oracles.
Stale state is deliberate rejection input, not admitted native authority.

126 host SDK headers and exact source/tool/resource/runtime/helper pins verify and
recheck. The native217-header set must exactly equal prior session36 pins before
compile and afterward. Nine ELF64/x86-64 objects/relocatable link leave only memcmp/
memcpy/memmove/memset unresolved. Forty-three static frame reports/max264 bytes
exclude call chains/callbacks/libc/interrupts and full code/stack/heap/workspace/
backing/channel fit. No executable/native loader/ABI/runtime or console witness.

Forty-one-member source-only handoff:
`build/service-deliveries/filesystem-fd-redirect-2026-10-21-v1`, manifest SHA256
`1f808da2135af11be7a8225975a645a15a9b02d4ce84c3991ebea6d728901140`.
New helper/harness plus explicit session C/header extension and exact prior sources,
contract/license/dependency receipt. Rust policy/wire/service and prior packets
remain unchanged. No SDK/engine copy, linked shell/default/profile activation.

[Retention](retention.json) inventories three passing owned attempts in
[attempts.tar.xz](attempts.tar.xz), preserving commands/environment/deadlines,
streams/process cleanup, source/checker snapshots and artifacts. Initial run records
the same native headers; final checker adds explicit equality with prior217-header
pin before use. Final minimum/current reruns use that stronger selection. Production/
API/harness bytes unchanged; no failures, skips, suppressions or source workaround.
Every retained file hash/size verified in one streaming readback before exact root
removal:29,974,952 logical bytes removed,5,659,440 archive bytes retained. Physical
reclamation not measured. Current Python lzma retention is separate from minimum
qualification. Quality/input-preservation/final-source receipts accompany the seal.

Implementing-agent technical review only; independent owner/reader pending. Native
adapters/coherent linked-shell/startup selection, stronger atomic/full-capacity
semantics before claiming that POSIX behavior, immutable executable/copy/failed-
exec parent/FD preservation, full fit and matched dispatcher/readiness/shutdown/
Aether commands/errors/cleanup/fresh boot remain open. Full UL/M3/R1/TTY/Zsh/packages
incomplete. No sibling edit/message, guest, target install, release pin/default/
quota change or monitoring. Local receipt/map preservation is not native settlement.
