# Mixed FD consumer integration — 2026-10-21

[Decision0198](../../decisions/0198-mixed-fd-consumption.md) consumes32-member
stream replacement plus ten sealed dependencies and the separately selected
15-member process baseline:12 deliveries/277 manifest entries. Complete inventories
and every byte hash verify before and after consumption. The C transport/facade/
codec are unchanged from decision0197. Old92-file exchange packet and current
source closure verify unchanged. Accepted runtime owners/defaults/releases stay fixed.

The new tests/fd_dispatch_mixed.c uses actual delivered canonical bindings/table,
routing/pipe/write/replace helpers plus C transport/facade. A128-byte synthetic
startup table labels three console entries (not actual consoles). The pipe creator
creates two real host OS pipe ends and installs logical3/4 with pipe selectors3/4.
Opening a file through live RPC installs logical5/file selector3, then duplicating
creates logical6/file selector4. Numeric collisions therefore occur in the same
process/table; kind and selector together select the source. No parallel FD ledger.

Five paired sessions pass with actual live C/Rust bytes. The Rust server includes
the unchanged existing host App/fixture plus tests/native_fd_mixed_server.rs; it
uses the unchanged Peer and freshly compiled actual handler/ProcessFiles/client/
AF07 service with synthetic storage. Positive performs nine file RPC exchanges:
open, read, duplicate, current seek, shared-offset read, nonzero-count EOF read,
cloexec and both closes. Source opcodes are exactly lookup/read/read/read/close;
lookup count1 and raw source-local close count1. Short-read tail and EOF caller
bytes preserve prior output, file write returns -30, file replacement and file-only
seek on a pipe return -38 before effects. Real pipe bytes P and Q travel through
tagged read/write; stream aliases preserve actual ends until final close, empty-
target replacement resets only distinct target flags and self preserves flags.
Closing the final write alias produces actual EOF at the read alias. Both actual
pipe ends close. Final closed logical read/close errors do no RPC.

Lost-body session loses file read body after header/effect. C output and logical
map remain unchanged, workspace clears, both peers retire and further calls do no
I/O; Rust sees lookup/read only. Stale-map and unknown-close sessions end after
one successful file open: source count lookup only, no file read or retry, server
observes transport EOF and retires source once, repeated serve returns Closed.
Unknown close is exercised with and without physically closing the host read end.
Both preserve map, retire file admission and publish no replacement. Client owner
explicitly closes unresolved stream ends, separately from metadata/admission;
physical close count2 is checked in all five cases. No cleanup is inferred from
file-client abort. Both raw file-channel closes are0 and occur once.

Three omissions compile and fail specific C exits: route file by logical rather
than source selector ->7; close nonlast stream alias physically ->18; accept unknown
stream-close completion ->21. Corresponding Rust exit may be101 on early client
closure; it cannot satisfy the C assertion oracle. All five normal sessions exit
client0/server0 and join service fixture threads. Every owned process stops in all
eight sessions, with no forced cleanup. Preparation JSON records commands, results,
server source counters/oracles, exact input and host library/tool/header/runtime
pins and artifact sizes/digests. Native endpoint/trap objects are not built or run.

Strict C17 diagnostics/UBSan/format, strict Rust2024/default Clippy/rustfmt pass.
Host C headers are discovered by preprocessing and pinned before compilation;
LLVM resource headers, UBSan, compiler/formatter, Rust tools and host compiler/
runtime libraries pin before use and recheck afterwards. Compiler commands have
60s/4MiB bounds; paired sessions have30s watchdog and owned-group kill/reap fallback.
The new host test buffers, source callbacks and synthetic startup grants establish
no native authority, actual console, native IPC/OpenZFS, shell/libc/POSIX dup2,
copy/immutable exec/failed-exec preservation or complete memory/channel fit.

Next userland must select linked shell/startup and actual native binding adapters,
copy/exec and bounded placement; sys-init then owes matching full dispatcher/
readiness/shutdown/fit and Aether fresh exact command/error/cleanup/readback.
See [current handoff](../../FILESYSTEM-BOOT-HANDOFF.md#mixed-fd-helper-checkpoint--2026-10-21).
No sibling edits/messages, guests, quota expansion or release promotion. No new
shared standard or approved exception. Independent review remains open.
local-checks.json records full offline checks; sha256.json seals all packet files
except itself. runner.py.txt is inert reproduction text; use fresh evidence/output
roots and preserved selected inputs rather than rerunning into this sealed packet.
