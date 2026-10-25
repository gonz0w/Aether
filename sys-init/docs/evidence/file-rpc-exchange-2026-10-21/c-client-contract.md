# AEFD0001 C file-client transport — UL-007/081/082

`experiments/filesystem-service/fd-client.c` supplies a separately selected C17
transport client for the [file-only wire](FS-FD-WIRE.md). It reuses the exact v3
codec. It does not interpose libc, alter the linked ABI29 shell or implement the
missing startup/descriptor routing/console/pipe/process/exec dispatcher. No native
endpoint binding, trap execution, concrete memory fit or shell acceptance follows.

## Ownership and API

The trusted caller initializes fresh unowned `struct aefd_client` storage once
with `aefd_client_init(client, io, workspace, channel_generation)`. A valid nonzero
channel generation is assigned externally, never acquired from request names or
PID/FD labels. It must not be reused with a replacement stream. Initialization
requires all four callbacks and a caller-owned 4096-byte workspace. Invalid
initialization returns 0 without consuming callbacks or modifying storage.
Success returns 1, initializes sequence 1 and clears workspace. It acquires an
exclusive borrow of callbacks/context/workspace. Do not reinitialize the client,
copy its live state or reset its sequence to replay/reconnect.

The C caller must serialize access and ensure no callback reentrancy. Client,
workspace, arguments, name, reply and callback-owned storage are valid and disjoint
for the call. Unlike the Rust reply guard, C does not enforce these lifetimes.
The trusted adapter must authenticate real native endpoint holders/directions,
provide bounded callback durations and preserve actual ownership/cleanup evidence.
Callback addresses and numeric generation are not native authority. Sys-init owns
matching endpoint/lifecycle policy; no sibling implementation is supplied here.

`aefd_client_exchange(client, opcode, args, name, length, reply)` uses the existing
six wire operations. Open takes exactly one component and length; other operations
require NULL name and zero length. Numeric fields obey the wire's exact bounds;
unknown opcodes require all-zero arguments. Local malformed arguments return 0,
clear workspace and cause no I/O or sequence advancement. Invalid names return 0;
there is no pathname resolver or local successful substitute.

Return 1 means the complete reply is validated. Caller must inspect `reply.status`:
negative semantic errno is a valid response and consumes sequence, with zero result
and body; the next request may continue. Successful read bytes are available in
workspace, with the unused tail zero, until the next exchange or abort. Metadata
is published only after the whole header/body/padding passes validation. Local
invalid or retired calls leave reply metadata untouched. Retired calls return -1.
The client never interprets readonly file size, digest or labels as exec authority.

## Transport and failure boundaries

Each read/write callback receives a range of 1–64 bytes. A positive result must not
exceed that range; short success advances only by the observed count. The private
-11 would-block result invokes `wait(context, writing)`; zero wait result permits
continuation at the same byte offset. Any other read/write error, zero progress,
oversized count, EOF, failed wait, malformed response or incomplete transfer retires
the stream. Only -11 is retryable; no EINTR retry or whole-request replay exists.

One budget of 16384 I/O attempts covers the entire request header/body and response
header/body. Each would-block consumes one attempt and at most one wait; the budget
is not reset between phases. It is a finite-call bound, not a wall-clock deadline
or proof of native scheduler progress. The adapter must bound individual callbacks.
UINT64_MAX is never sent; after delivering MAX-1, the next call retires before I/O.

`aefd_client_abort` clears/releases workspace and consumes local live state before
calling `close(context)` once. Both raw input/output close outcomes are retained
in `client.closed`; after retirement repeated calls cause no more I/O or closure.
Releasing the workspace pointer allows the caller to reuse/free it after abort.
This local result is not native revocation, server detach, process settlement,
export/device quiescence or successful supervisor shutdown. The owner must settle
all actual endpoints/processes separately. Unknown file operation outcomes may
have advanced shared offsets; no client recovery/reconnect policy is invented.
A request accepted by the server is not the same as the caller observing success.

Runtime automatic storage is a 64-byte header plus small control values. The
4096-byte workspace is supplied externally. No measured native code/stack/heap/
backing/channel fit or permission to enlarge existing limits is implied.

## Qualification

```
python3 -B experiments/filesystem-service/check-fd-client.py
```

The host C test replays sealed prior actual C request/Rust response bytes through
scripted callbacks; it does not invoke a live Rust server in this experiment.
It compares emitted requests byte-for-byte and checks ab/cd/f shared-offset data,
semantic status, padding, sequence and raw closure. Short chunk sizes 1–64, every
832-byte response and 704-byte request interruption prefix, malformed replies,
wait direction/failure, budget, zero/oversized/error callbacks, local denials,
full 4096-byte data, 255-byte names, semantic-error continuation and exhaustion
are covered by 1631 schedules. Seven compiling omissions must fail their specific
assertions. These schedules are not independently launched native tasks.

The checker pins the source/tool closure before execution, including
v3 and prior evidence manifests, exact recorded bytes, Clang 21.1.8/resource headers,
UBSan runtime and owned command helper. It records the host SDK header closure
before compilation and rechecks it afterward. C17 strict warnings, nonmutating
format checks and UBSan apply. Each compile is bounded to 60 seconds and test to
30 seconds, with clean environment, owned build directory and 16 MiB stream bounds.
Python 3.10+ is the host-tool baseline. The minimum offline Python lacks lzma;
plain 704/832-byte fixtures retain exact prior extraction hashes without new tools.

[Evidence](../evidence/filesystem-fd-client-2026-10-21/README.md) retains all attempts,
including the initial mutation-target mismatch and minimum-interpreter xz setup
failure. No runtime change was needed for those tooling issues. Earlier wire and
process-source qualification is reused only for unchanged bytes and original scope.
Source-only candidate: `build/service-deliveries/filesystem-fd-client-2026-10-21-v1`.
Independent owner/reader and assembled native acceptance remain pending.

Next explicitly select this transport in a reviewed shell facade with truthful
file/pipe/console routing and startup binding, preserve native-copy/failed-exec
parent/FD state, establish immutable executable admission and measure full fit.
Sys-init then assembles its dispatcher/readiness/shutdown and Aether qualifies
native commands, errors, cleanup and fresh boot. Full UL-007/081/082, M3/R1,
packages/Zsh/TTY and POSIX conformance remain open.
