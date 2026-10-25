# 0135 — Retained artifact correspondence

BG-056 host evidence slice, 2026-09-07. Foundations E-01–08 applies. Compare I/O
build supervisor_sha256 with the verified retained clients/<case>/supervisor.raw.
Require consumed service-worker inputs to contain inputs/sdk-evidence.json,
inputs/tools.lock.json and inputs/libc.a with digests matching the corresponding
sdk_receipt_sha256, tools_lock_sha256 and libc_sha256 top-level fields. Existing
input-map verification then binds these claims to retained bytes.

Inventory: all 22 I/O supervisors and all three links in 18 service-worker
receipts match. No new file paths come from arbitrary receipt fields. Use existing
bounded verified digest reads. Preserve all native/runtime bytes, release pins,
retained evidence and successful audit output. No dependency or shared ABI change.
Test wrong and missing links, changed supervisor hashes and existing semantic
controls, then run full checks. Native execution is unnecessary for host auditing.

None of 2,997 init consumer ISO hashes has a retained matching artifact. The first
I/O bundle also lacks the original native envelope; four later bundles retain it
as worker/native-c.bin. Do not invent historical files or rewrite receipts. These
remain explicit evidence limits; SDK recursive semantics and additional envelope
correspondence need a separate scope review under BG-056. Independent review and
filesystem deadline/race limitations remain open.

Validation: 63 focused native-harness tests and all ten gates pass in
run-9whx2d2a; four mandoc lint/render commands pass. No failed attempts.
All identity comparisons stay fixed; no native execution. Evidence:
../evidence/native-artifact-correspondence-2026-09-07/.
