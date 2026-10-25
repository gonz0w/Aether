# Independent broker/file coexistence witness (UL-047)

Six AENCO001 / ABI 7 native cases pass, plus six fresh ABI 5 broker regressions.
The independently authored Clang/musl requester now routes bounded file requests
through Aether's broker while both channel pairs remain live. The owner supplies
the broker, writable Rust file service, service startup bridge and kernel.

The positive workload fragments frames into seven-byte writes and five-byte reads.
It rejects direct backend endpoint use; sends complete bodies after invalid-version,
invalid-inheritance and forged/stale-ticket headers; then verifies those denied
creates left scratch absent and framing intact. It reads all 18 message seed bytes,
checks read-root create denial, creates/writes/reads/closes scratch, collects the
backend, and repeats with a new ticket and fresh scratch state. Existing namespace,
empty inheritance, busy launch, malformed collect and repeated collect assertions
remain active. Both backend generations exit 17, requester exits 29, and supervisor
reports 100 with three reclaims and the profile's channel cleanup checks.

| Case | Required outcome |
| --- | --- |
| Positive | Exact marker `AETHER NATIVE COEXIST PASS` and terminal outcomes above |
| Repeat-collect broker mutation | Requester 66; supervisor 903, two reclaims |
| Partial requester header | Requester 41; supervisor 903, one reclaim |
| Requester exit with live backend | Requester 42; supervisor 903, two reclaims |
| Two-channel pool control | Requester launch assertion 59; supervisor 903, one reclaim |
| Corrupt file-read data | Requester seed-data assertion 78; supervisor 903, two reclaims |

Negative cases require the precise rejection context and no success marker.
Build failure, unrelated panic and watchdog timeout cannot pass a case.

```sh
python3 experiments/native-process/coexist.py --aether ../aether \
  --producer ../aether/docs/evidence/native-coexist-2026-09-05 \
  --sdk build/native-c-xhkdw6jv
python3 experiments/native-process/check.py \
  --aether build/native-broker-userland-2nyvo0qd/Aether \
  --sdk build/native-c-xhkdw6jv
```

The new runner pins the completed producer summary, archive and suite report;
materializes only its 155 hash-matched regular source files; and builds in a private
root. Archive links, unlisted paths, traversal and duplicates reject. The sibling
checkout supplies boot dependencies only, verified by the pinned owner tools.
The strict-musl SDK and Clang/LLD inputs use UL-044's tested inventory. Rust 1.98.0,
Zig 0.16.0 and QEMU 11.1.1 versions, commands and native environment are recorded.
The producer's size-optimized (`opt-level=s`), fat-LTO broker is 3944 bytes within
its unchanged immutable one-page bound. QEMU uses TCG, one CPU, 256 MiB, no NIC,
private firmware variables and the pinned 30-second owner watchdog.

An initial build used `opt-level=z` and failed the one-page linker assertion.
It never booted; its failed receipt/log are retained separately. Matching the
producer's `s` recipe resolved that build failure. It is not a native failure or
an accepted extra case.

[Evidence](../../docs/evidence/native-coexist-userland-2026-09-05/README.md)
retains the exact producer archive, consumer sources/build receipts, requester and
service ELFs, brokers, command logs, serial logs and ABI 5 regression results.
Successful work roots are `build/native-coexist-userland-facbg_76` and
`build/native-broker-userland-722hyd56`; ISO/envelope hashes are retained while
large generated images remain in build/. Source and SDK stability checks passed.

This tests raw file RPC coexistence, not the local FD/stdio facade through this
broker. No inherited open-file references, fork/exec, POSIX wait, pipes, TTY,
persistence, sys-init adoption or recovery after lost mutation replies is added.
ABI 6 supervisor shutdown is separate. Shared standards and pending PD review are
unchanged. No sibling runtime changed. File/libc/init/default-boot suites were not
rerun because their implementations were untouched; the shared requester path
received the six ABI 5 regressions. All three local standards checks pass.

UL-049 subsequently completed [six independent ABI 9 multi-client cases](CONNECTIONS.md).
UL-050 next consumes the newer fixed-alias shared-files producer. UP-01's native inherited-file ownership/bootstrap
and UP-02's shell semantics remain owner-coordinated prerequisites for M3.
