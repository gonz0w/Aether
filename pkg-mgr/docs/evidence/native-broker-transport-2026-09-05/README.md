# Independent launch-broker package witness — 2026-09-05

Six transported QEMU outcomes pass: positive, allow-inheritance, wide-scope,
repeat-collect, partial-request and requester-exit. Host: arm64 macOS; target:
Aether x86-64, memory-disabled single-core ABI-5 experiment. No sibling source,
shared ABI or standards pin changed. [Contract](../../NATIVE-LAUNCH-TRANSPORT.md).

Original producer/tool report:
`/Users/cam/DEV/Aether-userland/docs/evidence/native-broker-userland-2026-09-05/evidence.json`
with external SHA-256
`f5bbc077734d8508fb9ea3d4bda3f840fe7272015e048afe4fb0a552d007f636`.
The normalized copies here preserve report data; the external pin applies to its
original bytes. Source restoration/donor identities are in that report. Historical
kernel_source_root names an earlier capture; accepted build commands locate the
final outputs beneath native-broker-userland-2nyvo0qd. Exact selected tool hashes
are checked against the report before copying them.

Reproduce:

```sh
python3 tests/native-launch-integration.py --profile process --producer-kind userland-broker \
  --evidence /Users/cam/DEV/Aether-userland/docs/evidence/native-broker-userland-2026-09-05/evidence.json \
  --evidence-sha256 f5bbc077734d8508fb9ea3d4bda3f840fe7272015e048afe4fb0a552d007f636 \
  --tools-evidence /Users/cam/DEV/Aether-userland/docs/evidence/native-broker-userland-2026-09-05/evidence.json \
  --tools-evidence-sha256 f5bbc077734d8508fb9ea3d4bda3f840fe7272015e048afe4fb0a552d007f636 \
  --aether /Users/cam/DEV/Aether-userland/build/native-broker-userland-2nyvo0qd/Aether \
  --root /absolute/new/private-root
```

Retained root: `/Users/cam/DEV/pkg-mgr/.pkg-mgr-live-ul046-broker-2026-09-05`.
Large images, payloads and frozen dependency/tool copies remain there. Results,
commands, receipts and serial logs here were hash-checked; results identify the
whole package helper closure. Source copies preserve this implementation.

Positive boot requires worker 17/33 in two generations, requester 29 and three
reclaims. The five negatives require requester 51/52/66/41/42, broker 903 with
one reclaim for partial-request or two otherwise, and exact rejection panic.
Five input controls reject wrong schema/profile, incomplete cases, an artifact
outside selected output and incompatible memory options before creating output.

This is empty-inheritance launch/collect, not POSIX process support, file/process
coexistence, inherited descriptor ownership or a fix for sys-init's SI-04 reuse
fault. These six cases do not replace the separate existing 27 FILE outcomes.

`macos-fixtures.log` records all three pinned standards checks and sixteen
ordinary fixture scripts passing after this change.
