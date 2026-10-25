# 0136 — I/O envelope correspondence

BG-056 host evidence slice, 2026-09-07. Foundations E-01–08 applies. The retained
builder and consumer specify AENFD001: 8-byte magic, two little-endian uint32
lengths, 32 entropy bytes, native image, supervisor. Require exact total length,
1–1,048,576 image bytes and 1–4,096 supervisor bytes. Reconstruct AENATC01 + entropy
+ native image in memory and compare its digest with consumer native_sha256.
Compare embedded supervisor bytes with the verified retained supervisor.raw.

Inventory confirms all 22 retained I/O cases match both checks. The first bundle
lacks an independent original native file, but its embedded bytes support this
reconstruction check. Do not write reconstructed artifacts or rewrite historical
evidence. Existing bounded verified content reads enforce ownership/read limits;
no native code executes and no new dependency, API or release pin is introduced.

Use inert synthetic layouts to test bad magic, truncated/trailing data, zero and
oversized lengths, changed native bytes and changed supervisor bytes. Keep the
existing semantic-serial negative test reachable with a valid inert envelope.
Run focused and full checks; preserve successful audit output and native inputs.

SDK direct/derived receipts remain distinct. Recursive SDK semantics, unavailable
ISO artifacts, filesystem deadline/race limits and independent review remain
BG-056 follow-ons. Host correspondence is not loader or native execution proof.

Validation: 65 focused tests and all ten gates pass in run-lfrm_fw8.
Four manual lint/render commands pass. Initial fixture import failure was fixed
and retained. Audit output, catalog, native inputs and pins remain unchanged.
Evidence: ../evidence/io-envelope-correspondence-2026-09-07/.
