# Independent fixed-alias shared-file witness (UL-050)

Six native cases pass against the completed `shared-files` producer on AENMX001 /
ABI 9. Both clients are independently authored Clang/musl programs. The owner
supplies the broker, backend service and startup bridge. This is fixed bootstrap
delegation to two loaded clients, not parent-requested spawn or POSIX inheritance.

Each client validates its complete bootstrap: zero status, connection/generation
reference, descriptor index (3 or 10), rights (3 or 1) and zero trailing bytes.
Native endpoint/factory/third-executable denials remain active. Three-byte writes
and five-byte reads exercise incremental framing. Every RPC reply validates zero
metadata and padding, signed status and the bounded two-byte payload.

Before consuming data, both clients reject foreign, stale, wrong-index and raw-root
references, unknown operations, invalid read counts and nonzero read payload.
Malformed close count/payload must reject without removing the alias. The child
requires EACCES for write; the parent requires explicit ENOTSUP. The subsequent
exact reads establish that these operations did not disturb the tested file data,
shared position or reference lifetime.

The parent reads `ab`; the child next reads `cd`; the surviving client reads `ef`.
Test-only EAGAIN gating provides explicit ordering. Only an explicit EAGAIN response
is retried with a finite bound; a lost or malformed reply aborts the client and is
never replayed. In child-first mode, the child exits without close and the parent
survives to read and close. In parent-first mode, the parent closes/exits before
the child's reads. Parent repeat-close and post-close read must return EBADF.
Each successful order repeats for two fresh generations, clients exit 29, backend
exits 17, and supervisor reports 100 with six reclaims and CONNECTIONS PASS.

| Case | Required outcome |
| --- | --- |
| Child-first | Exact terminal slot order 2/0/1 in both rounds |
| Parent-first | Exact terminal slot order 0/2/1 in both rounds |
| Frozen offset | Independent parent exits 50; supervisor 970, zero reclaims |
| Premature backend close | Independent surviving parent exits 50; supervisor 970, zero reclaims |
| Missing child rights guard | Independent child exits 48; supervisor 970, zero reclaims |
| Missing final backend close | Owner stale-handle probe rejects at supervisor 975, zero reclaims |

All negative cases require the designated panic/context and no success marker.
The final-close probe is owner code: it reads through the old backend handle and
requires EBADF after both references are removed. The surviving-client reads
independently establish continued availability before final removal. The rights
control detects ENOTSUP where EACCES is required; it does not demonstrate a
successful unauthorized storage write. Timeout and unrelated panic never pass.

```sh
python3 experiments/native-process/shared.py --aether ../aether \
  --producer ../aether/docs/evidence/native-shared-files-2026-09-05 \
  --sdk build/native-c-xhkdw6jv
```

The producer summary, archive and report are pinned before consumption. Only
hash-matched listed regular files are extracted to a private root; links,
traversal and duplicate/unlisted paths reject. Boot dependency manifest verification
uses pinned owner tools. SDK/tool inventories use UL-044's tested strict-musl pin.
Client ELF inspection checks static x86-64, bounded initialized TLS, NX, no dynamic
or W+X segments, no unresolved symbols and no Linux syscall instructions. Rust
uses size optimization and fat LTO; the normal broker is 3968 immutable bytes.
Version/build logs record Clang/LLD 21.1.8, Rust 1.98.0, Zig 0.16.0 and QEMU 11.1.1.
QEMU uses TCG, one CPU, 256 MiB, no NIC and private firmware variables with the
pinned 30-second watchdog. Final source/SDK stability checks pass.

[Retained evidence](../../docs/evidence/native-shared-userland-2026-09-05/README.md)
contains the producer archive, consumer sources, four client variants, backend ELF,
brokers, receipts and serial logs. Large generated images remain in
`build/native-shared-userland-v9g1gn5u`, identified by receipt hashes. All six cases
passed on the first build/run. All three standards checks pass. No shared adapter,
older test source, sibling implementation or standard changed, so previous native
suites were not rerun; producer regressions remain separate evidence.

This does not interpose libc read/close, adopt a general FD table, create POSIX
parenting, implement a dynamic inheritance list, reconcile lost close replies,
recover a failed broker or run a shell. The local FD/stdio facade and pending PD
review remain separate. Userland retains eventual POSIX implementation ownership.

Aether now also has a completed `inherited-launch` fixture: an explicit parent
request admits one child alias, with native admission/channel-reservation rollback
controls. UL-051 subsequently completed [nine admission/collection cases](INHERITED.md).
UL-052 next reviews bounded libc/FD integration. Its
use of ABI 9 and the same marker does not imply acceptance from this witness.
