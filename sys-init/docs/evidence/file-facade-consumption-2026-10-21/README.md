# Typed file facade consumption — 2026-10-21

[Decision0197](../../decisions/0197-file-facade-consumption.md) consumes the exact
userland12-member facade candidate using our unchanged decision0196 exchange
server artifact and source closure. All12 manifest members and complete prior
92-file packet verify; underlying C transport/codec are unchanged. Full inputs,
commands, host header/resource/runtime/tool closure, artifacts and actual owned
process outcomes are in preparation.json. runner.py.txt is inert reproduction
text; run in a new evidence/output root to preserve this packet.

Two live host pipe sessions pass. Positive ten typed exchanges exercise open,
read, shared dup/current seek/offset, cloexec, nonfinal/final close, semantic EBADF
including a zero read on a closed FD, preserved short-read output tail and local
invalid inputs with no I/O. Lost read body after effect/header retires without
replay, clears private workspace and preserves all caller output. Actual C I/O
uses <=7-byte callbacks and synthetic direction-specific EAGAIN waits. Both raw
local closes succeed once; repeat abort and later retired read do no new I/O.

Three mutations compile with the same strict C17/UBSan settings and fail the
specific C assertions: missing copy exits7, copying excess short-read tail exits11,
masking retired transport exits4. Generic Rust failure/timeout cannot satisfy the
control. Both processes stop in all five sessions; positive/lost-body exits0/0,
copy/tail controls exit client7/11 with server101 on early closed transport, and
retired-error control exits client4/server0. Normal server cases join the service
fixture thread. No forced group cleanup needed. Tool output is4MiB/60s bounded;
paired sessions have30s watchdog and own-group kill/reap fallback. Host pipes and
synthetic AF07 storage are not native IPC, OpenZFS, shell, endpoint authority,
immutable exec, native process-copy/failed-exec preservation or peak-fit evidence.

Strict C17 diagnostics, format and UBSan pass. Host headers are discovered with
preprocessing, pinned before compile and rechecked after runs, along with LLVM
resource headers, UBSan and exact tools. Native/runtime sources are unchanged.
Initial preparation failure retained: local reader expected digest strings where
prior packet entries have size/digest objects. Failure happened before compilation
or execution; corrected reader compares actual sizes/digests. Old packet untouched.

The [narrowed handoff](../../FILESYSTEM-BOOT-HANDOFF.md#typed-file-facade-checkpoint--2026-10-21)
requires selected linked shell/startup/mixed FD routing and native copy/immutable
exec/failed-exec preservation plus exact placement/full fit before full dispatcher
and native composition. File-only facade is delivered; shell selection is not.
No sibling edits/messages, native guest, quota expansion or pin change. Independent
owner/reader/release and native acceptance remain open. local-checks.json records
full offline checks; sha256.json seals the packet except itself.
