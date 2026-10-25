# Scoped technical review

Reviewer: Codex implementation agent,2026-10-03. SSDK-06 independent review remains
pending/deferred. No supervisor/client/kernel source is modified or rebuilt here.

Read current sys-init STATE and decision0183, sealed owned entry/dispatcher,
normal/wrong-ABI/busy sources, raw/ELF identities, borrowed origin, original failing
and passing traces, and diagnostic check-caller source. Entry validates actual
ABI24/grant tuple before dispatch. It delegates one session to the bounded module,
then requests native halt only after settlement; success never returns. The module
stays in the same owner TCB. Its generic failure emits owner failure and UD2 without
claiming reclamation or successful halt. Wrong ABI reaches that path before launch.
The small busy control prints that path only after checking actualEBUSY16; its
alternate failure address differs, so exact diagnostic/address checks distinguish it.

Producer normal code15056 bytes, estimated3816/4088 stack; diagnostic3880 and
busy200bytes/64stack are separately identified. Native wrapper stack/source results
are reused as scoped producer inspection, not recomputed or promoted to formal
bounds. Independent LLVM21 objcopy binds actual ELF load bytes to every raw owner.
All clients/entropy/kernel and other module identities are unchanged in actual ISO
readback, not merely manifest descriptions. Every input is verified before use.

Replay driver has no detached session. The pinned existing helper owns each driver
and emulator group, checks exit/complete cleanup, limits files16MiB and deadlines.
QEMU has fixed no-NIC/BSP/TCG configuration, read-only firmware code and a fresh
variables template in its owned run root. It never writes into the delivered kit.
Serial is bounded1MiB/90seconds; child terminate/kill waits are each3seconds.
Partial diagnostics wait for a newline; full panic bytes are retained before failure
or negative classification. Negative oracles compare exact post-boundary bytes,
not generic nonzero exit. Healthy results use the frozen independent userland
oracle. Source/config/tool hashes, receipts and every attempt are retained.

Original delayed failure audit confirms complete host-accepted input and real owner fail-stop
before parent settlement. The same generic UD2 address does not name the causing
check/unwrap. Existing diagnostic successes and new passing witnesses do not prove
a fix. Concrete bounded diagnosis proposal is in SYSINIT-SESSION-CONSUMPTION.md;
implementation and acceptance remain with that owner. No automatic retry or
unsupported cleanup success is introduced by this consumer.
