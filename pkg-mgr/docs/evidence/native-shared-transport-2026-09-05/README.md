# UL-050 fixed shared-file aliases — 2026-09-05

Six package-staged/rebuilt QEMU boots pass: positive child-first, parent-first,
frozen-offset, early-close, wide-rights and leak-close. Host: arm64 macOS; target:
Aether x86-64. Existing AENMX001 transport is unchanged; only the witness harness
adds the explicit userland-shared consumer schema/cases and exact oracles.

`invocation.json` records the exact command, external original producer/tool pins,
selected source capture and private output root. Original report is
Aether-userland/docs/evidence/native-shared-userland-2026-09-05/summary.json.
Normalized report copies here preserve data; external pins apply to original bytes.
Archive/client/backend/build/SDK identities remain in the accepted producer report.

Retained root: `/Users/cam/DEV/pkg-mgr/.pkg-mgr-live-ul050-shared-2026-09-05`.
Captured source: `/Users/cam/DEV/Aether-userland/build/native-shared-userland-v9g1gn5u/Aether`.
Large payloads/images and frozen tools/dependencies remain in the private root.
Small receipts, serial logs, commands, results and source snapshots are copied here.
Their receipt/serial hashes and whole package implementation closure were verified.
Reproduce with the pinned original inputs and a fresh --root, not an existing bundle.

Child-first and parent-first require exact terminal order 2/0/1 and 0/2/1 in both
generations; clients exit 29, backend 17, supervisor 100/reclaimed 6. Frozen offset
and early close require parent50; wide rights requires child48; all require
supervisor970/reclaimed0. Missing final close requires supervisor975/reclaimed0.
Each negative requires the exact profile panic without a success marker.

Six input controls reject schema confusion, the older connections selector,
incomplete case sets, an unaccepted case, reduced pool or memory-enabled build
before output creation. Exact validation errors are in input-controls.json.

Clients independently validate shared reads, narrowed rights, reply/reference
scope and surviving aliases. The final-close backend probe is owner code. The
rights control distinguishes EACCES from ENOTSUP, not a successful forbidden write.
No dynamic inheritance list, parent-requested spawn, libc interposition, POSIX
parenting, shell, recovery or persistence is established. No sibling runtime or
shared pin changed. [Contract](../../NATIVE-LAUNCH-TRANSPORT.md).

`macos-fixtures.log` records all three pinned standards checks and sixteen
ordinary fixture scripts passing after this change.
