# File exchange driver and live host C interoperability — 2026-10-21

[Decision0196](../../decisions/0196-file-rpc-exchange.md) and
[API/remaining handoff](../../../prototypes/native-filesystem-session/FILE-RPC.md)
describe the separate fd_dispatch.rs candidate. Accepted runtime/pins are unchanged.
preparation.json binds process15/wire20-v3/service77/C-client9 complete manifests,
exact source copies/tools/native libraries, compiler/test commands and outcomes.
No producer-supplied build/test scripts are executed; pinned sources and fixture
compile in owned local roots. Source/compiler assertions are not native authority.

Five actual-service/Owner host tests use synthetic storage and deterministic peer
channels. They check complete header/body delivery and sequence continuation,
semantic-error continuation, lost response header/body with no replay, partial
input/nonzero padding with no lookup effect, stale process even for unsupported
requests, bad bind closure and backend bad-body/count/final-close retirement.
Peer and AF07 source raw closes are checked independently; all failed workspace
bytes clear. Three compiling omissions (body send, source abort, delivery
confirmation) fail one selected semantic test each. Native libraries are generic
no_std builds, not a concrete native process or code/stack/heap fit witness.

Two fresh live host pipe sessions connect the actual sealed C transport client to
the new Rust driver, actual handler/process broker/client and actual AF07 service/
Owner with synthetic storage. Positive: ten exchanges cover open/read/dup/current
seek/shared offset/flag/final close, EBADF and ENOSYS continuation. C observed344
I/O calls,60 read waits/54 write waits and one actual callback closure. Negative:
server loses read body after effect/header; both sides retire, dirty workspace
clears, failed C reply metadata remains unchanged and further C calls do no I/O.
C observed76 calls/11 read waits/14 write waits/one closure. Source service runs
in a joined fixture thread; both owned OS processes exit0 in each case. This is
live interoperability, not the earlier producer's captured-response replay.

Exact logs and process teardown are in live-attempts.json and positive/lost-body
logs. C uses <=7-byte pipe callbacks and synthetic EAGAIN waits. Header discovery
is preprocessing only; all discovered header bytes, LLVM resource headers and
UBSan runtime are pinned before actual compile and rechecked after execution.
Strict C17 warnings/UBSan and Rust format/default Clippy pass. Host callbacks and
buffers are test-only; no native IPC/OpenZFS/ELF admission/shell/workspace/peak fit
or physical storage claim. Actual native endpoints and lifecycle still need fresh
Aether witnesses under a complete selected composition.

prior-attempt1 retains strict compilation rejection of an unused Message import;
removed without suppression. initial-unit-tests logs/source retain the earlier
passing tests before stronger omission assertions. All guard controls and live
sessions use final source identities. The accepted old owners/core/endpoint
packets and released/default pins remain fixed; no sibling writes/messages or
additional guest. Host scripts/wrappers are retained as inert reproduction text.

Next shell facade/startup/file-console-pipe binding, process/fork/immutable exec/
failed-exec contract, bounded placement and full sys-init shutdown/fit remain open.
local-checks.json records final repository checks; sha256.json seals this packet
except itself. No independent release/reader or native sign-off is claimed.

prior-clear-order retains the earlier passing source/logs before final review
moved workspace clearing ahead of shared-source abort/external cleanup. Final
host/native dispatcher builds, all five tests/three omissions and both live C
sessions use the corrected order. No native run or accepted runtime changed.
