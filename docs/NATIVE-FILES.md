# Native user-space file-service experiments

The base read-only kernel conformance experiment runs a Rust file service and a C client
in separate native address spaces. The service owns names, immutable contents,
open handles and read permissions. Kernel changes only provide two bounded byte
channels and atomic endpoint-pair transfer. No path lookup or filesystem engine
is added to the kernel. This is neither POSIX VFS nor persistent package install.

## Transport extension

AENFS001 retains the two-image launch envelope layout. Supervisor ABI 5 grants
existing launch/image/channel factories. It can create up to two channels, each
with the existing 32-byte queue and three generations. Channel grants distinguish
pool slot, generation and end. Creation chooses the first free nonretired slot;
EBUSY means channels remain live, ENOSPC means all slots have retired. Other
profiles retain their previous capacity and operations.

0x23002 launches with two distinct supervisor-owned endpoints, supplied in R8/R9.
Other arguments match 0x23000. Both authorities and the complete startup record
are validated before either transfer or child admission; failure preserves both
endpoints. Child auxv keys 0xa001/0xa002 supply them in that order. Existing
single-endpoint launch remains available. Exit/fault/stop closes both owned ends;
completion requires both channels empty and unowned. Execution remains BSP-only.

## Service protocol and authority

One client connection is delegated by the launcher. Its request endpoint is the
root authority boundary; a path string alone conveys none. The server issues a
connection-local root handle and checks that binding on open. It does not accept
arbitrary clients, authenticate identities or define a cross-project filesystem
standard. Future shared normative requirements belong in Aether-standards.

Requests and replies are exactly 32 bytes, accumulated across partial channel
transfers. Little-endian requests contain operation u32, handle u32, offset u32,
length/rights u32, name[16]. Reply contains signed result i32, handle u32, size u32,
reserved u32 and data[16]. Initial reply gives root handle 0xf001. Operations:
1 open (root, rights=1, NUL-terminated single-component name); 2 read (file handle,
explicit offset, length 0–16); 3 close; 4 write (always denied for valid handles).
Open returns connection-local file handle and byte length. Read returns its count,
with 0 at EOF. Close consumes the handle. Non-applicable fields must be zero.

Two immutable files are embedded in the Rust service: `hello.sh` and `message.txt`.
Only two open records are available; each permits three generations before
retirement. Invalid root returns EACCES, invalid/stale file handle EBADF, missing
file ENOENT, disallowed rights/write EACCES, malformed names/requests EINVAL,
open-record exhaustion EMFILE. Names containing `/`, `.` or `..` components are
not resolved; no traversal, symlinks, cwd or implicit global namespace exists.
Results describe volatile service state, never durable completion.

EOF on the request channel shuts down the fixed service and clears open records.
A partial final frame is an error, not a request. This single-client test does not
establish reconnection, service restart, replay safety or concurrent clients.
The C client uses a test protocol adapter, not userland's libc file facade.

## Reproduction and results

```sh
python3 scripts/launch_smoke.py --files \
  --libc-build /absolute/Aether-userland/build/native-c-BUILD \
  --tools-lock /absolute/Aether-userland/experiments/musl-reference/tools.lock.json
zig build test
zig build smoke
```

The existing runner verifies strict-musl and compiler/linker pins, compiles the
Rust service as a static library into its C startup ELF, builds the independent
C client and Rust launcher, and retains maps, sources, commands and exact target
outcomes under `zig-out/files-suite-*`. `--files` and `--channel` are mutually
exclusive. Existing help/version, error exits and build/QEMU watchdogs apply.
No package fetch, sibling modification, disk installation or activation occurs.

Three cases: successful reads/authority/lifetime; a Rust service compiled to
corrupt reply data (client exit 211 then supervisor result 611 before reclaim);
and a client closing after four bytes of a request (service exit 121 then
supervisor result 611 before reclaim). Each negative requires the exact profile
panic and ordered terminal context; timeout/boot failure cannot pass. Positive
completion checks successful client/service termination, both channel cleanups,
three child reclaims and a replacement child launched without endpoint grants.
Marker: `AETHER NATIVE FILE SERVICE PASS`.

The launcher also checks distinct-channel grants, full pool rejection, invalid
record rollback preserving both endpoints, duplicate-end rejection and loss of
access after each pair transfer. Host checks reject substitution between equal
generations in different channel slots. The file consumer checks root authority,
traversal/missing-file/write denial, two-open limit, bounded reads and EOF, close,
slot reuse and stale handles. This is neither a filesystem backend plugin API nor
userland libc adoption; files are embedded in the service, not loaded from disk.

Next: agree the shared process/file-service requirements with userland, then
provide bounded writable file operations and executable lookup for the selected
script workload. Current read-only records do not provide POSIX shared offsets,
rename, directory traversal, shell execution, persistence or rollback.

[Retained results](evidence/native-files-2026-09-05/README.md) record all three
file-service cases and the existing launch/channel/memory/consumer/host/default
regressions passing.

## Writable scratch extension (opt-in service build)

The `--writable-files` service build keeps the AENFS001 kernel ABI unchanged.
It explicitly delegates an additional connection-local write-root handle 0xf002
in initial reply word 8. Read root 0xf001 remains read-only; requests cannot obtain
write rights through it. Normal `--files` retains the original read-only behavior.
This is bounded user-space scratch consistent with the direction of the unreleased
PD proposal, not approval or implementation of its POSIX/process requirements.

One mutable file has at most 64 bytes and a single-component name of at most 15
bytes. It disappears when the service exits. Operation 5 creates it exclusively
(write-root, offset 0, rights 3, name), returning a new RW open handle. Operation 1
can subsequently open it with rights 1 through either root or rights 3 through the
write root. Seed files remain immutable. Existing names return EEXIST; a different
second mutable file returns ENOSPC. Creation first reserves an open record; failure
must not publish a file or consume a generation. The two-open/three-generation
limits remain unchanged.

Operation 4 writes 0–16 payload bytes at an explicit offset; bytes after the payload
must be zero. Operation 6 truncates/extends to the offset field, with other fields
zero. Both require a writable scratch handle. Capacity failure returns ENOSPC;
malformed lengths/fields return EINVAL. No partial mutation occurs on rejection.
Writing beyond EOF zeros the gap. Truncation clears removed bytes, and extension
zeros newly visible bytes. A zero-length write is a no-op. Reads through another
open handle see current contents; offsets remain caller-supplied, not POSIX shared
open-file positions. Neither append concurrency, rename, unlink, persistence,
fsync nor crash recovery is provided.

Run the writable service/client suite with:

```sh
python3 scripts/launch_smoke.py --writable-files \
  --libc-build /absolute/Aether-userland/build/native-c-BUILD \
  --tools-lock /absolute/Aether-userland/experiments/musl-reference/tools.lock.json
```

The writable build explicitly grants its one client both roots; it does not
implement multi-client selective delegation. Five target cases cover successful
scratch mutation plus the existing corruption/framing controls and two new
semantic controls: skipping truncate/extension zeroing must yield client exit 236;
ignoring a read-only open handle's write restriction must yield client exit 240.
Each requires supervisor result 611 before reclaim and the exact rejection panic.
Timeout or a different client error cannot satisfy these controls.

The positive client also verifies protected seed files, create failure when open
records are full followed by successful retry, exclusive create, single-file
capacity, gap zeroing, zero-length write behavior, failed capacity/overflow writes,
read-only mutation denial, truncate/extension, rejected oversized truncation,
malformed write length, stale handles and contents retained across close/reopen.
All writes are acknowledged only after service-local mutation; if the reply is
lost the caller's outcome is unknown. There is no replay/deduplication contract,
and retry is not automatically safe. Reboot or service exit loses scratch data.

Kernel source and native ABIs are unchanged by this service extension. The
read-only file suite and the launch/channel modes of the shared runner are
regressions; unrelated memory, descriptor and default display targets need not
be repeated for this user-space-only change.

[Writable scratch evidence](evidence/native-writable-files-2026-09-05/README.md)
records five passing writable cases plus read-only/launch/channel and host checks.
