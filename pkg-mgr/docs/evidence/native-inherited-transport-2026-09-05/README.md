# UL-051 inherited-launch package witness — 2026-09-05

Nine staged/rebuilt QEMU cases pass: positive, parent-first, rejected-launch,
partial-reservation, leaked-reservation, leaked-admission, allow-child-write,
wrong-status and repeat-status. Host: arm64 macOS; target: Aether x86-64.

The AENMX001 package parser now matches the existing ABI-9 supervisor bound of
8192 bytes; its previous 4096-byte restriction could not accept the 5288-byte
broker. Tests accept 4097 and 8192 bytes, reject 8193 and preserve older profile
bounds. No kernel ABI, sibling source, shared pin or receipt field changed.

`invocation.json` records the exact command, original evidence/tool path and
external pins, captured source and private output root. Original report lives at
Aether-userland/docs/evidence/native-inherited-userland-2026-09-05/summary.json.
Normalized copies retain data; external pins refer to original bytes. Producer
archive/source/client/backend/build/SDK identities remain in that report.

Retained root: `/Users/cam/DEV/pkg-mgr/.pkg-mgr-live-ul051-inherited-2026-09-05`.
Captured tools: `/Users/cam/DEV/Aether-userland/build/native-inherited-userland-wrwi402h/Aether`.
Large payloads/images and copied dependencies/tools remain under the private root.
Small results, commands, receipts, serial logs and source snapshots are copied here.
Receipt/serial hashes and the whole package helper closure were verified. Reproduce
with original pinned inputs and a fresh --root; existing publication is not replaced.

Four successful scenarios each require two terminal rounds, client29/backend17,
supervisor100 and six reclaims. Parent-first orders 0/2/1; other successes order
2/0/1. Five controls require parent70/70/66/75/76 respectively, supervisor970,
zero reclaims and exact profile panic. Timeouts or unrelated failures cannot pass.

Six metadata/input controls reject wrong schema, the fixed-alias shared selector,
incomplete cases, failed acceptance, reduced pool and memory-enabled build before
output creation. Exact validation errors are in input-controls.json.

Independent clients check admission/result/reply scope and shared reads; the owner
supplies native rollback mechanisms and the final backend-close probe. This is
one-entry admission and consuming observed result, not general FD lists, libc,
fork/exec/waitpid, POSIX parenting, broker recovery, native shell or persistence.
Lost successful admission/collection replies remain unknown outcomes. Explicit
failure retries do not establish transparent replay. [Contract](../../NATIVE-LAUNCH-TRANSPORT.md).

`macos-fixtures.log` records all three pinned standards checks and sixteen
ordinary fixture scripts passing after this change.
