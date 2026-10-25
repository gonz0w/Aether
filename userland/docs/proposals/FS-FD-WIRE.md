# AEFD0001 file RPC candidate — UL-007/081/082

`experiments/filesystem-service/fd-protocol.rs` implements a separately versioned
file-only RPC over the actual AF07-backed ProcessFiles layer. `fd-protocol.h` is
a C17 pure request/reply/body codec. This candidate supplies exact bounded file
messages; it does not switch the linked ABI29 shell to them or replace its startup,
FD table/binding, console, pipe, process or exec protocols. No old machine bytes,
accepted owner, SDK/standards pin, native grant/quota/lifetime or sibling change.

[Evidence](../evidence/filesystem-fd-wire-2026-10-21/README.md) tests the actual
Rust handler/ProcessFiles/sealed AF07 service with synthetic storage, actual C-
emitted requests and C validation of actual Rust responses. No native IPC/OpenZFS,
complete dispatcher, concrete code/stack/heap fit or shell execution is claimed.

## Binding and caller-owned storage

Every opcode, including unsupported operations, revalidates the complete stored
process binding before effects or reply publication. The added ProcessFiles::
validate_binding is a pure exact-key check; canonical labels still prove no native
authentication. The original v1 preparation missed that check for unsupported
opcodes and is preserved as superseded; select the v3 source input carrying that correction and expanded payload tests.

The trusted dispatcher constructs Connection::bind(current_process_key,
nonreused_channel_generation) for an actually authenticated native endpoint. The
key is the existing opaque ProcessFiles selector, not a request field. Numbers,
magic, sequence, FD, filename and generation confer no native authority. Native
endpoint holder/direction/admission and observation checks remain mandatory.

One mutable caller-owned4096-byte workspace carries complete inbound padded name
frames or outbound read bytes. The handler allocates no4096-byte automatic array.
The ProcessFiles object and workspace must both reside in caller-selected bounded
memory in the intended domain. This does NOT prove they or their nested frames fit
init's4088-byte usable stack. Sys-init/Aether must prove full code/stack/heap/backing/
channel fit within unchanged limits. There is one AF07 greeting consumer: do not
call ProcessFiles::connect after the old activation path already read that greeting.

Connection::input_length(files, header) validates a complete64-byte header and
returns inbound padded-body size0..256. Invalid input retires connection/shared
source without dispatch. Caller assembles that many bytes boundedly in workspace,
then prepare revalidates header and complete body/padding before effects. Partial
header/body EOF/error must call abort; no resynchronization or replay. The transport
owns its actual peer endpoints and input-buffer clearing; inspection alone does
not take or initialize that external buffer.

## Requests

All fields are initialized little-endian64-bit words. Word0 bytes are AEFD0001;
word1 opcode; word2 exact nonzero channel generation; word3 exact expected sequence;
words4–7 arguments a,b,c,d. Sequence starts1; u64::MAX is never admitted, so delivery
of u64::MAX-1 reaches permanent exhaustion without wrap. This counter does not
extend any native process generation, authority, request or lifecycle allowance.

| Opcode | a | b | c | d | Inbound body |
| --- | --- | --- | --- | --- | --- |
| 1 open_read | cloexec0/1 | component length1–255 | 0 | 0 | ceil(length/64) complete64-byte frames, unused tail zero |
| 2 read | file FD3–15 | request length0–4096 | 0 | 0 | none |
| 3 seek | file FD3–15 | signed64 displacement encoded in two's complement | whence0 set/1 current/2 end | 0 | none |
| 4 duplicate | file FD3–15 | minimum0–15 | new cloexec0/1 | 0 | none |
| 5 close | file FD3–15 | 0 | 0 | 0 | none |
| 6 set_cloexec | file FD3–15 | flag0/1 | 0 | 0 | none |

Other opcodes with all-zero arguments/no body return canonical ENOSYS(-38), not
successful no-ops. Unknown nonzero argument layouts, noncanonical field values,
wrong generation/sequence/version, incomplete/excess body or nonzero name padding
are protocol failures before AF07 effects. Numeric FD fields outside3–15 are
invalid file-message shapes, not routing to console/pipe support. A valid FD field
with no live binding returns semantic EBADF(-9). A component is relative to the
existing delegated root; NUL/slash/dot/dotdot reject with EINVAL(-22). No general
pathname/cwd/symlink resolver, write/create/append, metadata credentials or exec.

Read/seek/dup/close/cloexec retain existing [process-view semantics](FS-PROCESS-DESCRIPTORS.md).
Zero read validates process/FD/READ/offset and returns0 locally; no new AF07 request
or EOF observation. Signed request ranges stay stricter than full POSIX. Every
request comes through the trusted connection's stored process key; no operation
can admit/rebind/copy/settle a process or invoke destructive exec commit.

## Responses and outcome ownership

A response is64 bytes: AEFD0001, signed status word1, exact generation word2,
consumed request sequence word3, result word4, actual body length word5, words6/7
zero. Success status0: open/dup resultFD3–15; seek checked nonnegative signed64
position; close/set flag result0; read result equals count and body length. Only
read success has a body: ceil(count/64) initialized frames with zero unused tail.
Count0 has no frames. Error result/body are0; error workspace is cleared.

Private errors preserve positive-native errno as negative AF07 errors. Local FD
missing=-9, table full=-24, invalid=-22, signed overflow=-75, AF07 capacity=-28,
unsupported=-38. These mappings are not POSIX conformance. A stale process key,
fatal/unknown source or closed source produces no usable reply: retire all shared
FD admission and expose transport/retirement failure to the trusted caller.

prepare marks the connection pending before effects, then returns PreparedReply
borrowing connection, ProcessFiles and workspace exclusively. header()/body()
expose exact immutable header and padded data; no next effect/reuse is allowed
while the guard is live. The trusted transport calls delivered() ONLY after the
complete header AND all body bytes are confirmed delivered. That consumes sequence,
clears pending state/workspace and allows the next request. Known semantic errors
also require complete delivery to continue.

Drop, partial/failed delivery, lost confirmation or explicit abort retires the
connection and entire shared AF07 file source, clears workspace and never replays
an effect/response. One failed application peer can therefore stop all four file
views in this bounded fail-stop candidate; no general fault-isolation/recovery
policy is claimed. Persistent pending state also rejects redispatch if a safe Rust
caller forgets the reply guard; it cannot silently repeat the same read/open.
Drop/lifetime controls do not prove native sends occurred, handle panic=abort or
replace actual native peer settlement. The trusted caller must retain and settle
all application endpoints/processes and the separate sys-init child ledger.

Local source closes preserve both raw results. Even local0/0 is not native
revocation/reclaim, server detach/export/device quiescence or successful shutdown.
No automatic replacement/reconnect or cross-process sequence reset is supplied.

## C codec and qualification

C functions borrow valid initialized pointer ranges supplied by caller. aefd_request
initializes a header and checks basic generation/sequence only; it does not approve
operation arguments, authority or effects. aefd_name validates/copies one component
and initializes its256-byte output. aefd_decode validates a complete response
against the caller's retained exact generation/sequence/op/read length, publishing
its output struct only after checks. Return1 means valid encoding, including a
negative semantic status; caller must inspect status. aefd_body validates a complete
padded read body, allows overlap, clears all rejected output and zeroes unused
4096-byte tail. No function sends/receives, authenticates or retries. Do not consume
a read from its header before all body frames are received and validated.

```
python3 -B experiments/filesystem-service/check-fd-protocol.py
```

Actual Python3.10.21/3.14.7 pass9 host tests/eight compiling semantic omissions,
10 actual C request/Rust response exchanges,80 malformed C-decoder header cases,
three padded-body denials, full/zero/oversized-body and overlapping-copy checks under pinned Clang
C17/UBSan. A valid consumer compiles; overlapping prepared responses reject with
Rust E0499. Actual4096-byte responses and907-byte multi-frame EOF responses verify data/count/
padding and delivery clearing through the real AF07 policy. Host Clang SDK header
closure, LLVM resource headers and UBSan runtime are hashed before C compilation/
execution and rechecked afterward. Rust1.98/2021 default Clippy/rustfmt/warnings/unsafe denial and identical
native no_std generic-library bytes pass separately. ProcessFiles adds only the pure binding-validation entry to the prior15-member
source; its18 tests/eight omissions rerun on both interpreters. Other dependency
sources remain exact, and unchanged qualification is reused only in its original
scope. C fixture automatic buffers are host-only, not native stack fit.

Source-only candidate:
`build/service-deliveries/filesystem-fd-wire-2026-10-21-v3`. Includes the new Rust
handler/tests, C codec/fixture and pinned process/client sources/tests, license,
contract and dependency record. No copied native engine/SDK or new selected image.
Independent affected-owner/reader and assembled native acceptance remain pending.

Next integrate a separately selected C shell facade and dispatcher startup/FD/
console/pipe binding, exact native copy/failed-exec/immutable image admission and
workspace placement/fit, then Aether native command/error/cleanup/fresh-boot
witnesses. Readonly handles, size, labels or hashes do not authorize immutable exec.
Packages/Zsh/TTY, broader POSIX and full UL-007/081/082/M3/R1 stay open.

## Separate canonical root-path variant —2026-10-23

AEFD0001 remains component-only. Explicit fs_path_wire+fs_paths selects AEFP0001
with canonical1–255-byte delegated-root paths through the actual ProcessFiles
adapter; C selects AEFD_PATH_WIRE. Compile-time broker selection must match;
wrong peer versions retire without fallback/effects. Other operations, frames,
workspace, process identity, sequence and delivery/cleanup remain unchanged.
This is read-only and supplies no CWD/POSIX relative path or libc slash support.
[Contract and results](FS-ROOT-PATHS.md#explicit-path-file-wire-pre-code-scope).
No native owner or released pin selection follows from this library candidate.
