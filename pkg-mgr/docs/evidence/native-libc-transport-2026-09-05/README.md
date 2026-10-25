# UL-042 / UL-043 package consumer evidence — 2026-09-05

All 23 QEMU boot outcomes pass from the latest accepted UL-043 bundle: seven
failure-handling, four libc, four descriptor, four writable and four read-only
cases. Host: arm64 macOS. Target: Aether x86-64. The package witness harness
changed; runtime transport, receipts, sibling source and shared pins did not.

`invocations.json` records all five exact harness invocations, original sibling
evidence paths and external pins, matching captured kernel directories and private
output roots. Producer and tool pins use the same report for each run. Normalized
copies here retain report data; external pins apply to original report bytes.
Results identify the entire package helper closure and each payload/image/serial
identity. Source snapshots preserve the changed harness and unchanged transport.

Retained roots are `/Users/cam/DEV/pkg-mgr/.pkg-mgr-live-ul043-RUN-2026-09-05`,
where RUN is failures, libc, descriptors, writable or read-only. Large images,
payloads and frozen tools/dependencies remain there. Small commands, results,
receipts and serial logs are copied here and hash-checked. Reproduction requires
the original pinned inputs and a fresh --root; never reuse a published destination.

Eight specific metadata/build/profile/case-set controls reject before output
creation, recorded in `input-controls.json`. These are validation failures,
separate from the native semantic controls below.

Four injected reply/close cases complete with normal final cleanup; ignored
poisoning, leaked retain and relaxed reply checking require client 195/193/189.
Libc wrong errno, ignored flags and frozen positions require client 200/201/205.
All negatives require supervisor 611 and the exact profile rejection panic.
All successes require the file-service marker and supervisor 100/reclaimed 3.
Descriptor and file regressions keep their existing exact status expectations.

These are 23 outcomes in one current integration bundle, not 23 independent
features, performance samples or an additive total with prior overlapping runs.
Fault injection changes completed replies at the consumer boundary, not physical
channel delivery. Raw test RPC cleanup is not production recovery. Libc results
cover bounded public calls, not internal stdio, threads/cancellation, inherited
FDs, native shell or persistent installation. [Contract](../../NATIVE-LAUNCH-TRANSPORT.md).

`macos-fixtures.log` records all three pinned standards checks and sixteen
ordinary fixture scripts passing after this harness change.
