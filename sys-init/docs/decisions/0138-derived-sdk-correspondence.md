# 0138 — Derived SDK artifact correspondence

BG-056 host evidence slice, 2026-09-07. Foundations E-01–08 and local quality
process apply. Four derived SDK receipts have 226 retained input files each,
worker/worker.elf matching the startup artifact, and worker/native-c.bin matching
the envelope digest. Verify all input-map links through existing bounded digest
reads, require exactly the supported startup artifact and compare its digest.
Bind the native envelope to both SDK envelope_sha256 and consumer native_sha256;
require AENATC01, 32 entropy bytes and 1–1,048,576 image bytes, and compare its
image payload with the verified worker ELF. No commands or artifacts execute.

All 904 input links and eight artifact links match in the initial inventory.
The first direct SDK receipt's sdk/startup/bad-dup artifacts are not retained.
Do not invent mappings, fetch missing artifacts or rewrite historical evidence.
No release-pin, native behavior, sibling or shared ABI changes. Test contradictory
inputs/artifact/envelope claims and payload mismatch; run focused/full checks.

Direct SDK semantic claims and absent artifacts, further producer correspondence,
filesystem deadline/race limits and independent review remain BG-056 work. This
host identity check does not certify ELF loading, patch effects or SDK provenance.

Validation: 72 focused tests and all ten gates pass in run-bp3a1s_e.
Four manual lint/render commands pass; all attempts passed. Historical inputs,
audit output and pins remain unchanged. Evidence:
../evidence/derived-sdk-correspondence-2026-09-07/.
