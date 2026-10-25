# Shared-position musl read/write/EOF (UL-055)

Ten native cases pass against the completed `file-io` producer, extending the
local libc witness to ordinary bounded read sizes, short reads, repeated EOF and
parent writes. [UL-054 review](../../docs/GENERAL-FILE-IO-REVIEW.md) records that
the required owner extension was already delivered; no sibling edit was needed.
The earlier two-byte inherited mode and its adapter remain unchanged.

The new separate-TU probe calls actual musl read/write/close/dup/dup2. One local
binding carries reference/index/rights, never a position or backend handle.
Reads and writable-parent writes send one request of min(count,16) bytes per call;
larger user buffers therefore receive a short result. Callers explicitly loop;
the adapter does not prefetch or replay. Zero reads and authorized zero writes
reach the owner for validation. Closed/wrong FDs fail locally even at zero count.
Oversized counts and supported nonzero null buffers reject; child writes require
EACCES even at zero count. Duplication remains deliberately unsupported.
Valid local buffers, single-thread execution and no cancellation remain limits.

Client framing stays at three-byte writes/five-byte reads. Replies must fit the
requested count, have zero metadata and correct payload padding before caller bytes
are copied. Writes cannot return data. Successful calls preserve errno. Transport
uses the separately renamed channel hook to avoid libc recursion. Lost/corrupt
replies poison the entire connection; file, launch and collection helpers cannot
send further frames. Local close consumes the binding once despite an unknown
reply. No reconciliation or remote recovery is claimed.

## Workload and controls

The parent reads `ab`, requests its read-only child and collects normal exit 29
once. The child reads `cde`, receives a short one-byte `f` from a 32-byte libc
request, and observes EOF with multiple sizes. Caller bytes beyond each actual
read remain unchanged. The parent observes EOF, appends 58 X bytes using requests
larger than the transport cap, tests ENOSPC, then confirms EOF and zero-write
behavior at full capacity before closing. The broker independently checks all
64 backend bytes (`abcdef` plus 58 Xs), then proves actual final closure through
its stale-handle probe. Two fresh generations require client slot order 2/0/1,
exit details 29/29/17 and six reclaims.

Raw foreign/stale/wrong-index and malformed zero/count/padding probes retain owner
checks independently of the local facade. The child directly probes zero-write
denial so the local rights check cannot hide a missing broker check. The parent
retains narrowed admission, duplicate admission and one-time collection assertions.

| Case | Required result |
| --- | --- |
| Positive | Two rounds, exact lifecycle and CONNECTIONS PASS |
| Frozen broker position | Child data assertion 91; broker 970/reclaimed 0 |
| Zero-read consumes position | Parent data assertion 90; broker 970/reclaimed 0 |
| Missing child write denial | Child raw denial assertion 93; broker 970/reclaimed 0 |
| Acknowledged writes omit storage | Owner readback assertion 985/reclaimed 0 |
| Wrong invalid-FD errno | Libc probe 80; broker 970/reclaimed 0 |
| Forced errno contamination | Libc sentinel probe 82; broker 970/reclaimed 0 |
| Dropped read / corrupt read / dropped close | Verified refusal/no-replay probe 122; broker 970/reclaimed 0 |

Fault injection occurs after an actual completed request/reply. The probe verifies
one additional completed operation and outgoing frame, caller-buffer preservation,
consuming close, and no frames from subsequent file/launch/collection attempts.
Dropped close is injected after the storage workload, when the real close can
complete; the parent then exits 122 intentionally. Exact rejection contexts and no
success marker are mandatory. These failures do not establish remote recovery.
The rights control catches unauthorized zero-write success, not a data overwrite.

## Reproduction and limits

```sh
python3 experiments/native-process/fileio-libc.py --aether ../aether \
  --producer ../aether/docs/evidence/native-file-io-2026-09-05 \
  --sdk build/native-c-xhkdw6jv
```

The pinned 172-file producer archive, summary/report hashes and tested strict-musl
SDK/compiler inventory are verified before private builds. Archive extraction
rejects unsafe/unlisted/duplicate paths and links. Owner tools verify boot inputs.
Seven client variants retain link maps and separate probe objects, static x86-64/
TLS/NX/W+X/dynamic/undefined/Linux-syscall inspection and exclusion of threaded
cancellation. Commands retain Clang/LLD 21.1.8, Rust 1.98.0, Zig 0.16.0 and QEMU
11.1.1 versions. QEMU uses TCG, one CPU, 256 MiB, no NIC, private firmware variables
and the pinned 30-second watchdog. Final source/SDK stability checks pass.

[Retained evidence](../../docs/evidence/native-fileio-libc-2026-09-05/README.md)
contains sources, archive, artifacts, receipts and serial logs. Large images stay
in `build/native-fileio-libc-axvn5i2q` with receipt hashes. The initial dropped-close
control attempted closure before required writes, causing broker 985 rather than
the intended reply-loss outcome. It was not accepted. After moving the injection,
all ten cases were rerun. All three standards checks pass. No old adapter, shared
channel source or sibling runtime changed; older native suites were not rerun.

This is one inherited reference and one volatile 64-byte record, no seek, open,
stdio, general descriptor table, durable storage or shell. General libc sizes use
bounded short transfers; no arbitrary scheduling fairness is claimed. Compatibility
rows distinguish this new mode from earlier profiles. UL-056 subsequently prepared the [command and candidate review](../command-runner/README.md).
UL-057 awaits the completed producer for native execution: a real bytecount command needs two records at stdin/
stdout, copied argv/env and exit 0, beyond this one-reference conformance workload.
