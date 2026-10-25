# 0197: Consume the typed C file facade against our exchange driver

2026-10-21 / BG-067. Userland delivered a12-member source-only facade candidate,
seal695b758f7d37547ad7ee14f01f0fbfe68cb73549aa69029cc612411b2c5260ce.
Verify full membership and all hashes; its C client/codec bytes must equal the
previously selected client9. This consumes explicit file-only calls, not a shared
shell startup/descriptor ABI or native authority.

Requirement: demonstrate the actual typed facade communicating live with our
unchanged Peer/Connection/ProcessFiles/client/AF07 service using synthetic storage.
Use the already built, source-matched decision0196 server and strict C17/UBSan
client. Check open/read/seek/shared dup/cloexec/final close and semantic EBADF,
local invalid inputs without I/O, preserved short-read output tails and lost-body
retirement with unchanged caller output, cleared private workspace and no replay.
Retain exact inputs/tools/header/runtime/artifact hashes and owned child cleanup.
Specific compiling controls must fail their intended assertion, not compilation
or a generic server/watchdog error. Run full offline development checks.

The simpler alternative is to trust the producer's live host evidence. It does
not exercise our server wrapper. Choose a small C test consumer reusing that
server, without a new runtime wrapper, mock wire or descriptor ledger. This adds
no runtime complexity and confirms the new typed seam without duplicating parser
or service machinery. No obsolete accepted path is removed in this slice.

Host pipes, synthetic storage and host test workspace only. No native shell,
endpoint authority, memory fit, immutable execution, failed-exec preservation or
POSIX libc conformance is claimed. Neither the native startup nor file/pipe/
console binding contract is delivered by this file-only facade. Do not route
FD3–15 by numeric range or connect after consuming the one AF07 greeting. Complete
shell composition still needs that owner contract, copy/exec admission and full
resource placement before a separately authorized fresh Aether witness. No sibling
edits/messages, native guests, release-pin changes or quota expansion.

## Result

The12 members verify and C transport/codec match the selected nine-member input.
Two live typed-C/unchanged-Rust-driver sessions pass: ten complete exchanges and
lost read-body retirement. Three strictly compiling omissions fail exact C exits:
lost copy7, excess tail11 and masked retired transport4. A generic Rust/watchdog
failure cannot satisfy these oracles. All five sessions stop both owned processes;
normal sessions exit0/0 and join the synthetic source service. Header/resource/
runtime/compiler/formatter and source/artifact hashes match after use. Strict
C17 diagnostics/UBSan and formatting pass. The source workspace is test-only.

[Evidence](../evidence/file-facade-consumption-2026-10-21/README.md) preserves the
initial pre-execution manifest-reader mistake: entries contain size/digest objects,
not bare digests. The local reader was corrected; old packet bytes never changed.
The new C fixture is tests/fd_dispatch_facade.c. This extends existing exchange
coverage and guide; no runtime source, owner, standards pin or ABI changes.
