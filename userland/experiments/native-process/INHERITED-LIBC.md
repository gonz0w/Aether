# Bounded musl I/O on inherited references (UL-053)

Fourteen native outcomes pass: the nine UL-051 admission/collection cases now use
real musl read/close for shared data and parent alias closure, plus five adapter
controls. A new userland binding tracks only reference, index, rights and local
lifetime. The broker remains the sole owner of shared position and remote reference
counts. No kernel, sibling implementation, old facade or shared transport source
changed. This implements the bounded [UL-052 plan](../../docs/INHERITED-LIBC-PLAN.md).

## Implemented path

A separate probe translation unit calls external musl read/write/close/dup/dup2.
Its client channel object renames the original `__aether_io`; the new adapter
provides the single active hook. Channel transport still calls native operations
directly. Link maps and ELF inspection retain the resulting linkage and exclude
the threaded cancellation object. The adapter returns raw negative errno and
restores the caller's errno after transport polling; musl performs normal public
error translation. Threads, cancellation and EINTR are not supplied.

The full validated bootstrap publishes one binding: parent index 3 or child 10.
Read accepts exactly two bytes, or zero with no request. Other positive sizes
return ENOTSUP; oversized counts return EINVAL; a null supported-size buffer
returns EFAULT. Invalid/negative/closed FDs return EBADF. Writes return EACCES for
the child and ENOTSUP for the parent. Dup/dup2, including same-FD dup2, deliberately
return ENOTSUP on a valid binding. This is an adapted subset, not general POSIX I/O.
Non-null invalid pointer handling remains outside the valid-local-buffer fixture.
No seek, open, flags, stdio, hidden prefetch or local offset is adopted.

One successful read request advances only the broker's position. The probe uses
actual libc reads for `ab`, `cd`, `ef` across clients. A completed EAGAIN is returned
to libc and retried explicitly by the bounded workload. Each successful call must
preserve sentinel errno; no-transfer/rejected preflight calls must leave the adapter
request counter unchanged. Later exact reads confirm no position/data consumption.

Close removes the local binding before its single consuming request. The parent's
normal close still allows the separate child-result operation: ECHILD after prior
collection, EAGAIN while pending in parent-first mode. Raw protocol denial probes
remain independent of local checks. The child exits without libc close; the owner
removes that remote reference after observed exit and checks real final backend
closure through its existing stale-handle probe.

## Uncertain replies

Lost or malformed replies poison the entire client connection. No caller bytes
are copied until the result, metadata and payload padding validate. A poisoned
connection blocks further frames from file, launch and collection helpers.
A close remains locally consumed even if its reply is lost; a repeated close
returns EBADF. Unknown remote completion is not converted into retryable EAGAIN,
replayed, or repaired with a client position.

The drop-read/drop-close controls suppress a reply only after the real owner
operation and full reply complete. Corrupt-read changes a reserved reply byte at
that same point. Each requires EIO, unchanged caller bytes for read, one completed
operation, one injected fault and exactly one outgoing frame. Follow-up file calls
must refuse; launch/collect attempts must also send no frames. For a poisoned read,
local close consumes the binding and reports EIO without a remote request. The
client exits 122 only after these assertions; the broker rejects the unfinished
workload. This proves refusal and no replay, not remote reconciliation or recovery.

| Cases | Required result |
| --- | --- |
| Positive / parent-first | Exact respective client exit order in two rounds; clients 29, backend 17, six reclaims |
| Rejected launch / partial reservation | Explicit rejection then successful retry and two-round completion |
| Leaked reservation / leaked admission | Parent 70; broker 970/reclaimed 0 |
| Accepted excessive child rights | Parent 66; broker 970/reclaimed 0 |
| Wrong status / repeated status | Parent 75 / 76; broker 970/reclaimed 0 |
| Wrong invalid-FD errno | Libc probe 80; broker 970/reclaimed 0 |
| Forced errno contamination | Libc zero-read/sentinel probe 82; broker 970/reclaimed 0 |
| Dropped read / corrupt read / dropped close | Verified fault-probe 122; broker 970/reclaimed 0 |

Every negative requires its designated context and profile rejection, without the
success marker. Positive cases require `AETHER NATIVE CONNECTIONS PASS`. Unrelated
panic, timeout or build failure cannot pass. The errno control deliberately forces
EAGAIN contamination even on a zero-read path; it is not a throughput/polling test.

## Reproduction and evidence

```sh
python3 experiments/native-process/inherited-libc.py --aether ../aether \
  --producer ../aether/docs/evidence/native-inherited-collect-2026-09-05 \
  --sdk build/native-c-xhkdw6jv
```

The pinned 170-file producer archive and tested strict-musl/Clang/LLD inventory are
unchanged from UL-051. Private extraction rejects unlisted/duplicate/unsafe paths
and links. Owner verification checks boot inputs. Eleven client variants retain
maps, separate probe objects and static x86-64/TLS/NX/W+X/undefined/Linux-syscall
inspection. Version and command logs record Clang/LLD 21.1.8, Rust 1.98.0, Zig
0.16.0 and QEMU 11.1.1. The normal broker is 5288 immutable bytes. QEMU uses TCG,
one CPU, 256 MiB, no NIC, private firmware variables and the pinned 30-second
watchdog. Final source and SDK stability checks pass.

[Evidence](../../docs/evidence/native-inherited-libc-2026-09-05/README.md) retains
sources, producer archive, clients, backend/brokers and serial logs. Large images
remain in `build/native-inherited-libc-ddm1h380` with receipt hashes. An initial
14-case run passed before review tightened poisoning to cover launch/collection
and added an outgoing-frame counter. All 14 were rerun on the final source; only
that final set is acceptance. Older native-file/stdio/ABI-5/7/init suites were not
rerun because their implementation paths were unchanged. All three standards checks
pass. Compatibility rows now distinguish this inherited profile from the old
local-offset file facade; no shell tier is promoted.

UL-054 found the separate owner file-I/O extension already delivered, and UL-055
completed [ten independent libc read/write/EOF cases](FILEIO-LIBC.md). The current two-byte scheduling fixture cannot
serve general programs or FILE buffering. Duplication/flags, general open/seek,
process replacement, pipes, TTY, PD review and lost-result recovery remain separate.
