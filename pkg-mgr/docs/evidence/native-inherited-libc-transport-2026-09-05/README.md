# UL-053 inherited musl package witness — 2026-09-05

All fourteen package-staged/rebuilt QEMU outcomes pass: nine admission/collection
cases through real musl I/O plus five adapter controls. Host: arm64 macOS; target:
Aether x86-64. Final sources include connection-wide poisoning and frame counters;
the earlier preliminary passing run is not substituted for this final acceptance.

`invocation.json` records the exact command, original report and external pins,
selected captured source and output root. Original report is
Aether-userland/docs/evidence/native-inherited-libc-2026-09-05/summary.json.
Normalized copies here retain report data; external pins apply to original bytes.
Source/SDK/client/probe/link-map identities remain in the producer evidence.

Retained root: `/Users/cam/DEV/pkg-mgr/.pkg-mgr-live-ul053-inherited-libc-2026-09-05`.
Captured source: `/Users/cam/DEV/Aether-userland/build/native-inherited-libc-ddm1h380/Aether`.
Large images, payloads and frozen tools/dependencies remain under the private root.
Small receipts, serials, command logs, results and source snapshots are copied here.
Receipt/serial hashes and the complete package implementation closure were verified.
Reproduction requires original pinned inputs and a fresh --root.

Four successful cases require two exact terminal rounds and six reclaims. Parent-
first order is 0/2/1; other successes are 2/0/1, with clients29/backend17. Five
broker controls require parent70/70/66/75/76. Wrong errno and contamination require
parent80/82. Dropped-read/corrupt-read/dropped-close require parent122 after the
independent fault assertions. Every negative requires supervisor970/reclaimed0,
the designated profile panic and absence of the success marker. These ten expected
workload rejections do not establish remote recovery or successful final cleanup.

Six input controls reject wrong schema, old raw-client selector, incomplete or
failed cases, reduced pool and memory-enabled build before output creation.
Their exact expected errors are recorded in input-controls.json.

The adapter holds no local position; shared ab/cd/ef and exact no-transfer/error
behavior are independently checked through linked musl. Lost/corrupt completed
replies poison file/admission/collection traffic without replay. General-size reads,
application EOF, stdio, general FD tables, exec/fork/shell and persistence are open.
No receipt/runtime helper, sibling implementation, ABI or shared pin changed.
[Contract](../../NATIVE-LAUNCH-TRANSPORT.md).

`macos-fixtures.log` records all three pinned standards checks and sixteen
ordinary fixture scripts passing after this change.
