# Corrected ABI29 input and dispatcher core preparation — 2026-10-21

[Decision0194](../../decisions/0194-abi29-dispatch-core.md) and the
[candidate guide/handoff](../../../prototypes/native-filesystem-session/README.md)
record the scope. This is host policy and Rust/C interoperability, plus native
object generation. No native shell/dispatcher, loader enforcement, peak runtime
fit, complete filesystem-backed path/exec or release acceptance is claimed.

preparation.json verifies all580 outer and574 bundle bytes before use and after
checks. The exact v2 identity header accepts the genuine boot owner7; linked
parent/helper hashes and sizes match the receipt. Compared with v1, exactly
README and src/fs-identity.h change;572 bundle members remain unchanged. Existing
prebuilt CRT/libc/dash provenance and original notices remain producer-owned.
No producer-supplied build/test scripts or guest payloads are executed; our local
harness compiles and executes the explicitly pinned C decoder.

The actual new Rust encoder supplies138 serialized shell/child identities to
the exact sealed C decoder under strict C17/UBSan. All138 accept,1803 malformed/
observation/restarted-owner controls reject and failed output sentinels remain
unchanged. frames.bin contains synthetic bookkeeping inputs, not authority.
Six Rust tests cover all startup bounds, seven-domain child membership and
inherited terminal/reserved wait/delivery/reclaim barriers through15 lifetimes.
Three compiling omissions (parent7, seven-domain PID, delivery-before-reclaim)
each select one actual test and fail. Logs, source copies, exact commands/tools,
native object and host binary hashes are bound by preparation.json; binaries
remain in the private out directory. children-compatibility.diff records the
small ledger change and extra membership/Default coverage.

prior-attempt1 preserves initial strict Clippy findings: the public child
constructor needed Default and the new encoder needed fixed-array chunk iteration.
Default delegates to the unchanged constructor; encoder uses Rust1.98 array chunks.
prior-compatibility-review.txt preserves a wrong review path assertion (source/
versus actual src/). Neither attempt changes a sibling or historical seal; final
checks and source copies describe the corrected result.

local-checks.json records full offline checks. sha256.json seals this packet
except itself. The original serial/AF06/AF07 runtime sources and immutable evidence
are unchanged. Next AF07 FD/path/exec contract and full sys-init transport/fit/
native composition remain explicit; see the guide. No sign-off is invented.
