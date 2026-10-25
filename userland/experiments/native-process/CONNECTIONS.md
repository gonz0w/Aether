# Independent multi-client transport witness (UL-049)

Six native AENMX001 / ABI 9 cases pass with both owner clients replaced by
independently authored Clang/musl clients. The completed ABI 8 contract was also
reviewed for its three-image envelope and worker/supervisor slot split. This run
accepts ABI 9's bounded connection workload; ABI 8's program-stop workload was
not independently executed here.

Each client has its own request/reply pair; the Rust broker owns the backend pair.
Userland clients send at most three bytes per write and receive at most five per
read. One sends eight bytes, waits for the exact 32-byte continuation frame
(u32 777 and 28 zeros), then sends its remaining 24 bytes. The other completes
its request, validates the full file response and marks itself ready first.
The broker's retained terminal order proves that second client completed while
the first request was incomplete. Both rounds require slot order 2/0/1, client
exit 29, backend exit 17, supervisor 100 with six reclaims and the unchanged
`AETHER NATIVE CONNECTIONS PASS` marker.

The independent clients validate startup/TLS state, distinct delegated endpoints,
channel-factory and third-executable launch denial, foreign backend writer denial,
and EBADF for using their own endpoints in the wrong direction. Response assertions
require u32 result 16, zero handle/size/reserved words, and all 16 seed bytes.
The broker never exposes its file root or handle to these clients. Its existing
checks additionally cover failed-launch endpoint preservation, transferred
endpoint loss, pool exhaustion, consuming reclaim and stale endpoint/child use.
Those broker checks are owner code, distinguished from the independent clients.

| Case | Required outcome |
| --- | --- |
| Positive | Two rounds and exact lifecycle order described above |
| Four-channel pool | Supervisor 950, zero reclaims, designated profile rejection |
| Nonzero second reserved word | Invalid launch envelope; no worker terminal |
| Wrong third ELF machine | Invalid launch ELF; no worker terminal |
| Broker rejects partial frames | Supervisor 959, zero reclaims, designated profile rejection |
| Broker corrupts delivered data | Independent client slot 2 exits 44; supervisor 960, zero reclaims |

Negative cases require the precise panic/context and absence of the success marker.
Generic timeout, unrelated panic and build failure cannot pass. All six completed
on the first build/run; no loader, kernel, shared adapter or sibling source changed.

```sh
python3 experiments/native-process/connections.py --aether ../aether \
  --producer ../aether/docs/evidence/native-connections-2026-09-05 \
  --sdk build/native-c-xhkdw6jv
```

The runner pins the completed producer summary, archive and report, validates all
165 archived source files, rejects links/unlisted paths/traversal/duplicates and
builds under a private root. Only boot dependencies come from the sibling checkout;
pinned owner verification checks their manifest before boot. The SDK inventory,
receipt and compiler tools match UL-044's tested pin. Client inspection checks
static x86-64 ELF, bounded initialized TLS, NX stack, no W+X/dynamic segments,
no unresolved symbols and no Linux syscall instructions. Rust uses size
optimization, fat LTO and the profile's immutable linker bound; broker size is
3528 bytes. Commands/version logs cover Clang/LLD 21.1.8, Rust 1.98.0, Zig 0.16.0
and QEMU 11.1.1. QEMU uses TCG, one CPU, 256 MiB, no NIC and private firmware
variables, with the pinned 30-second owner watchdog. Final source/SDK checks pass.

[Retained evidence](../../docs/evidence/native-connections-userland-2026-09-05/README.md)
includes sources, exact producer archive, client/backend ELFs, brokers, build
receipts and serial logs. Large images remain in
`build/native-connections-userland-_9j0guun`; receipt hashes identify them.
All three local standards checks pass. Prior ABI 5/7 and file/libc/init suites
were not rerun: this change adds separate clients/runners and leaves their tested
source paths unchanged. The producer's broader regressions remain separate.

This is finite partial-request progress, not general fairness or recovery under
stalled backend/non-reading clients. It does not route the local FD/stdio facade,
implement inheritance, execute a shell, establish POSIX parenting, or compose
sys-init policy. Shared standards/pins and pending PD owner review are unchanged.

Aether now also retains a distinct `shared-files` producer using ABI 9, with fixed
bootstrap aliases, shared position, narrowed child rights and final-close tests.
UL-050 subsequently completed [six independent shared-file cases](SHARED.md).
UL-051 next consumes the distinct parent-requested inherited-launch contract. Sharing
an envelope and completion marker does not make it accepted by this connection
witness. General inheritance-list admission/rollback and shell process semantics
remain separate owner-coordinated work.
