# UL-007/081/082 FD message preparation review

Pre-code plan,2026-10-21. Current companions request exact process/FD/path/binding
messages and warn that4096 bytes plus state cannot fit assumed4088-byte init stack.
Add a distinct opt-in AEFD0001 read-only file RPC codec over the existing trusted
ProcessFiles API. Do not silently replace the old ABI29 client FD/bootstrap/pipe/
console/exec wire. No syscall/owner/service/source pin or native resource expansion.

Bind trusted dispatcher-selected opaque Process and nonreused channel generation;
request bytes contain no native admission identity. Versioned64-byte little-endian
header carries op/generation/sequence/four args. Ops open-component/read/seek/dup/
close/set-cloexec only. Unknown canonical empty op returns ENOSYS, malformed bytes
fail stop before effects. No process admission, exec/commit or settle messages.
Validate all header/argument/reserved/body lengths and padding before AF07 effects.
Reads<=4096, component1–255, file FD3–15, minimum0–15 and checked signed64 offsets.
Canonical semantic failures return negative private errno with zero result/body.

One caller-owned4096-byte workspace holds inbound padded name or outbound read,
not an automatic stack array. Borrow ProcessFiles/Connection/workspace through a
PreparedReply guard until complete application header/body delivery is confirmed.
No second effect/next sequence while pending. Guard Drop/failed or unknown send
retires shared source and connection; no response/request replay. Delivery marks
sequence consumed, known errors may continue. Tail/error workspace bytes zero.
Native authentication, peer endpoints/settlement and workspace/state placement/
full code-stack-heap-channel fit remain explicit dispatcher/native obligations.

Pin prior15-member process candidate and unchanged77-member service, tools/native
libraries/helper and borrowed identity before use. Safe no_std Rust2021, default
Clippy/rustfmt/warnings/unsafe denial and native generic-library preparation only.
Host tests use actual ProcessFiles/sealed AF07 service with synthetic storage and
caller-owned workspace: positive wire operations, shared views, errors, malformed/
stale/replayed/partial input, reserved/padding, no effect before validation, reply
loss/drop retirement/zeroing, exact sequence delivery and raw cleanup. Add compiling
semantic omissions and require assertion failures. C17 fixture with strict pinned
Clang/UBSan validates exact Rust replies and emits actual client request bytes;
new codec does not interpose libc or select native transport. Minimum/current
Python; compile60s/tests30s,16MiB streams, clean env/build roots. Quality/syntax/
whitespace/format checks and all failed attempts retained; no new guests.

Foundations O/I/E, Distribution PX, CR/CC/TD/SE and stricter local limits apply.
Simpler alternative: raw frame builder plus caller success flag. It does not retain
workspace/offset outcome ownership while response delivery is uncertain. Borrowed
reply guard uses Rust lifetimes/Drop for this current failure boundary instead of
an async/RPC framework, transaction log or another owner. Reuse current process/
description algorithms. Remove no old accepted wire; new message integration needs
explicit consuming owner/client review. Independent owner/reader/native acceptance,
bootstrap/console/pipe/full paths/immutable exec/failed native exec and M3/R1 remain
open. No general POSIX conformance, native stack safety or authority from labels.

## Implementation-agent technical review and outcome

The selected v3 candidate implements the planned file-only surface. Review found
and corrected an early v1 defect: canonical unsupported operations could publish
ENOSYS for an expired process key. The maintained pure validate_binding method
now checks full opaque membership for every header, including unsupported ops.
v1 remains superseded and unchanged; v2 contains corrected runtime bytes; v3
retains those bytes and adds full-payload/provenance qualification. No native
consumer selected any of these candidates during this work.

Persistent pending state is set before effects, independently of the borrowed
reply guard. Forgetting the guard therefore cannot replay the stream. Complete
transport delivery is a trusted caller obligation; only delivered advances the
sequence. Dropped or uncertain delivery clears workspace and retires the shared
source. Rust lifetimes prevent concurrent reuse while a guard is live; the valid
external consumer compiles and the overlapping consumer fails E0499. panic=abort
is not a cleanup guarantee. Native endpoints and process settlement are outside
this library's authority.

Header, process key, operation shape, exact body length and padding are validated
before effects. Semantic errors are initialized canonical negative responses;
invalid protocol and retired sources fail stop. Tests cover every incomplete
255-byte component body, stale unsupported requests, sequence replay/exhaustion,
raw close failures, forgotten and dropped replies, actual 4096-byte reads and a
907-byte EOF response padded to 960. One caller-owned workspace avoids an automatic
4096-byte runtime array; concrete native placement and full memory fit remain
unqualified. It must not be assumed to fit the init stack.

The C codec performs no I/O or libc interposition. It validates actual Rust
responses to actual C requests and publishes decoded metadata only after complete
validation. Name/body overlap, zero/oversized/full bodies, padding and error
zeroing are exercised. Successful decoding includes negative operation status;
callers must inspect it. No full pathname, pipe, console, startup or exec support
is implied, and the linked ABI29 shell remains on its existing wire.

Final Python 3.10.21 and 3.14.7 runs each pass nine host tests and eight compiling
semantic omission controls. C/Rust interoperability covers ten exchanges, eighty
corrupt headers and three padding denials plus body boundaries. Current process
regressions each pass eighteen tests/eight controls. Strict Rust/default Clippy,
format/unsafe/warning checks, C17 strict warnings and UBSan pass. Native generic
library and wire bytes match between interpreters. Compiler/resource headers,
103-header host SDK closure and UBSan runtime are recorded before C qualification
and rechecked afterward. These are synthetic host-service tests and native object
preparation, not Aether execution, OpenZFS access or POSIX conformance.

The local quality gate passes; its explicit runtime/full-audit/reader/publication
NOT RUN boundaries remain. Failed setup, compile/mutation-target attempts and
preceding guard versions are preserved with exact source/checkers and logs.
Fourteen owned roots were archived and every regular file hash/size read back in
one streaming pass before removal: 223119933 logical bytes removed, 58022808
archive bytes retained. Physical disk reclamation was not measured. No unrelated
build roots, source deliveries or prior evidence were removed. Five candidate
manifests and all members verified unchanged; selected sources/contract match
maintained files. No new guests, sibling edits/messages or real-prefix install.

Independent owner/reader review, explicitly selected C facade, matching dispatcher,
channel authentication/lifecycle, native fit, copy/immutable exec and failed-exec
semantics remain open in STATE/BACKLOG. Full UL-007/081/082, M3 and R1 remain
incomplete. This review records the implementing agent's assessment only.
