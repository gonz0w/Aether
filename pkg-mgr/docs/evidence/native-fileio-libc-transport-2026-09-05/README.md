# UL-055 general-size shared I/O package witness — 2026-09-05

All ten final native outcomes pass after package staging/image reconstruction.
Host: arm64 macOS; target: Aether x86-64. Existing ABI-9 transport, receipts,
sibling source and shared pins are unchanged. The old two-byte adapter remains
a separate accepted profile, not evidence for the new read/write/EOF semantics.

`invocation.json` records the exact command, external original producer/tool pins,
captured source and output root. Original report is
Aether-userland/docs/evidence/native-fileio-libc-2026-09-05/summary.json.
Normalized copies preserve report data; external pins apply to original bytes.
Producer records retain source/archive/client/probe/link-map/SDK identities.

Retained root: `/Users/cam/DEV/pkg-mgr/.pkg-mgr-live-ul055-fileio-libc-2026-09-05`.
Captured source: `/Users/cam/DEV/Aether-userland/build/native-fileio-libc-axvn5i2q/Aether`.
Large staged payloads, images and frozen tools/dependencies remain in the private
root. Results, commands, receipts, serial logs and source snapshots are copied here.
Receipt/serial hashes and the whole package implementation closure were verified.
Reproduce with original pins and a fresh --root; do not overwrite publication.

Positive execution checks both terminal rounds 2/0/1, clients29/backend17 and six
reclaims. Frozen-offset/zero-consumes/wide-rights require slot2/91, slot0/90 and
slot2/93. Skip-write requires owner supervisor985/reclaimed0. Wrong errno, leaked
errno and dropped-read/corrupt-read/dropped-close require parent80/82/122/122/122;
all except skip-write require supervisor970/reclaimed0. Every negative requires
the exact profile panic and absence of success. Timeout is not acceptance.

Only the producer's final ten-case run is consumed. An earlier dropped-close
injection occurred before required writes and failed its expected context; it is
not counted. The final injection follows the storage workload and actual close.
Fault probes prove connection-wide poison/refusal and no replay, not reconciliation
or successful remote cleanup. The independent clients exercise libc behavior;
full-storage readback and final backend-handle closure are owner probes.

Six input controls reject schema confusion, old two-byte selector, incomplete or
failed cases, reduced pool and memory-enabled builds before creating output.
Their exact errors are recorded in input-controls.json.

One call transfers at most 16 bytes; short/zero/EOF, capacity and shared position
remain bounded to one 64-byte volatile record and valid local buffers. This is not
stdio, open/seek, two-record command stdin/stdout, native shell or durable install.
[Contract](../../NATIVE-LAUNCH-TRANSPORT.md).

`macos-fixtures.log` records all three pinned standards checks and sixteen
ordinary fixture scripts passing after this change.
