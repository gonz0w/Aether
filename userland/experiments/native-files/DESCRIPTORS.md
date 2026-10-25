# Bounded native file descriptors (UL-041)

The private [descriptor layer](fd-layer.h) runs over the existing AENFS001 file
protocol with the independent [consumer assertions](fd-probe.h). Four native
outcomes pass. It is a single-thread, single-client experiment with four local
descriptors and two open-file records, using the previously scoped userland
facade ownership in [NATIVE-DESCRIPTORS](../../docs/NATIVE-DESCRIPTORS.md).
The older native stream/libc facade remains a separate profile.

The service retains authority over names, file handles, rights and contents;
local descriptors add reference counts and shared positions. Duplicates share
one open-file record. Independent opens start at position zero. Closing an alias
leaves the service handle live; closing its last reference sends one consuming
close. `dup2` validates both numbers and retains the source before releasing the
destination. A same-number duplication does nothing. Lowest-free allocation and
capacity failures are explicit. Failed open does not publish local state, and
failed read/write does not advance the position.

This API returns negative errno values directly. It does not interpose libc
`open`, `read`, `write`, `close`, `dup` or `lseek`. Calls require valid local
buffers, transfer at most 16 bytes, and expose only absolute positions 0–64.
There are no initial standard descriptors, append/status/CLOEXEC flags,
concurrent callers, fork/exec inheritance, POSIX seek modes, signals, TTYs,
persistence or service recovery. The service's two handles and three generations
per slot remain additional bounds; local capacity is not a promise of unlimited
open/close cycles. These adapted limits are not POSIX conformance.

Transport/framing failures poison the connection and return EIO. Subsequent
remote operations are refused. Close removes the local descriptor even if its
remote outcome is uncertain; a failed destination close aborts duplication and
releases the temporary source reference. The implementation does not replay
mutations. UL-042 now has [direct reply/close fault injection](FAILURES.md); this run exercises a real closed output endpoint and
subsequent poisoned-open rejection, not a lost post-mutation reply.

## Target witnesses

| Case | Independent oracle |
| --- | --- |
| positive | Shared `abc`/`def` reads, separate-open `abc`, write denial preserving position, invalid/self duplication, local FD/OFD exhaustion, destination replacement releasing service capacity, surviving aliases, ENOSPC preserving position, EOF, final-close stale handle, fresh-open position reset, closed transport/EIO; client 29, service 17, replacement 33, supervisor 100/reclaimed 3 |
| frozen-offset | Deliberately omit offset advancement; alias read rejects at client 207 |
| early-close | Deliberately close service handle on every alias close; surviving alias rejects at client 213 |
| leak-close | Deliberately omit last-reference service close; subsequent open rejects at client 216 |

All negative cases require supervisor 611/reclaimed 0 and the exact native
profile-rejection panic, with no success marker. An initial incomplete run used
assertion 256 for the leak case; the native eight-bit exit status exposed zero.
All descriptor assertions were moved into 200–231, and the complete final suite
passed against the same captured kernel sources.

Reproduce with the pinned native SDK from UL-032:

```sh
python3 experiments/native-files/check.py --aether ../aether \
  --sdk build/native-c-xhkdw6jv --descriptors
```

The runner records source/SDK/tool identities, commands, ELF inspection,
envelopes, VM images and serial logs. It reuses the owner Rust service and
conformance supervisor in a private kernel copy. No sibling implementation,
shared standard, release pin or sys-init policy is changed.

[Retained evidence](../../docs/evidence/native-fd-userland-2026-09-05/summary.json)
also includes fresh default read-only and writable regressions after the shared
runner/client changes. Native shell acceptance remains open.

[UL-042 failure results](FAILURES.md) extend reply validation and test no replay
and failed-close reference cleanup. UL-041 evidence retains its original bytes.
