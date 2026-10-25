# Bounded shared-position file I/O

The opt-in `--file-io` producer extends the Rust shared-file broker over unchanged
AENMX001 / ABI 9. It supplies the ordinary read-size, EOF and parent-write owner
extension identified in userland's UL-052 inherited-libc plan. The existing
`--shared-files` and `--inherited-launch` modes keep their scheduled two-byte
reads and unsupported parent writes. Consumers must select this new mode
explicitly; existing evidence and consumer pins are unchanged.

This is a direct-protocol conformance client, not userland's libc adapter or the
[CR-01 command runner](NATIVE-COMMAND-RUNNER.md). It retains one shared open-file
record, parent descriptor 3, read-only child descriptor 10, three workers and six
channels. General descriptor tables, two-entry stdin/stdout inheritance and
public read/write/close integration remain userland integration work.

## Operations and ownership

The [shared-file framing and caller binding](NATIVE-SHARED-FILES.md) and
[parent-requested admission and collection](NATIVE-INHERITED-LAUNCH.md) apply.
Requests contain four little-endian u32 fields (operation, reference, descriptor,
count), then 16 payload bytes. Replies contain a signed result at byte 0 and read
data at byte 16. No backend handle or client-controlled offset is exposed.

- Read operation 1 accepts counts 0–16 and zero payload. The broker reads at its
  authoritative position, returns the actual byte count, and advances only for
  positive results. Short reads and EOF (zero) are ordinary results. Zero-length
  reads validate the live reference and leave the position unchanged. There are
  no peer-position scheduling gates in this mode.
- Write operation 2 requires the parent alias's write authority. The read-only
  child receives EACCES even for a zero-length request. Parent counts 0–16 are
  accepted; payload bytes after count must be zero. Writes use the same shared
  position and advance only by the actual positive backend result. Counts above
  16 or malformed padding return EINVAL. The volatile backend holds 64 bytes;
  requests beyond available capacity return ENOSPC without advancing the position.
- Close operation 3 retains consuming alias removal. Closed, foreign, stale or
  wrong-index references return EBADF before file effects, including zero-length
  operations. Terminal observation removes an unclosed alias. Only final alias
  removal closes the actual backend record.

The owner remains a bounded synchronous conformance broker. Unexpected transport,
backend or client failure aborts the experiment; uncertain delivery recovery and
operation replay are not implemented. There is no seek, persistence, general
write splitting, multiple open-file records or production filesystem claim.
Cross-project normative standards remain owned by Aether-standards; this is a
local experiment contract and does not record other-owner approval.

## Executable witness

Each of two fresh rounds seeds `abcdef`. The parent reads `ab`, requests the
read-only child and collects its actual exit. The child reads `cde`, then a short
one-byte `f`, observes EOF repeatedly and exits without closing. The parent
observes EOF, appends 58 `X` bytes in bounded chunks, reaches ENOSPC at capacity,
and closes. Before closing the backend, the broker independently reads all 64
bytes and checks `abcdef` followed by 58 `X` bytes. This catches acknowledged
writes that never reach storage. A stale backend read then proves actual closure.
Both rounds require terminal order 2/0/1, exit details 29/29/17 and six reclaims.

The five-case suite also requires these deliberate failures:

| Control | Required failure |
| --- | --- |
| frozen-offset | Child data check exits 204; broker 970, zero reclaims |
| zero-consumes | Parent data check exits 203; broker 970, zero reclaims |
| wide-rights | Child zero-length write incorrectly succeeds; child exits 201, broker 970, zero reclaims |
| skip-write | Suppress successful storage effects while preserving capacity checks; final independent backend read rejects at broker 985, zero reclaims |

Each control requires its ordered serial context and the designated profile
panic; a timeout or unrelated panic cannot pass. The rights control detects an
unauthorized successful zero-length operation, not a demonstrated data overwrite.

```sh
python3 scripts/launch_smoke.py --file-io \
  --libc-build /absolute/strict-musl-sdk \
  --tools-lock /absolute/compiler-tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

[Retained evidence](evidence/native-file-io-2026-09-05/README.md) records the native
suite, affected regressions, host checks, sources and tool hashes. This mode
changes no kernel source, ABI, quotas or success marker. It is a prerequisite
for ordinary command I/O, not completion of CR-01, fork/exec or the native shell.
