# 0137 — SDK receipt fields

BG-056 host evidence slice, 2026-09-07; Foundations E-01–08 and local quality
process apply. Validate the 23 direct SDK receipt occurrences and four derived
I/O worker receipts at fixed retained paths using verified bounded JSON reads.
Follow derived worker/inputs/sdk-evidence.json once, require a direct receipt,
and compare its digest with sdk_receipt_sha256. Service-worker SDK inputs also
require the direct format. No arbitrary recursion or execution is introduced.

Use exact known fields and existing bounded digest, argv, integer and path
primitives. Direct artifacts require name/hash/byte count/instruction count and
ELF header rows; derived artifacts require name/hash. Collections: at most 64
artifacts, patches, checks, tools or header rows; 1,000 commands/argv; 10,000 input
hashes. Require nonempty collections, unique artifact/patch/tool names and true
inputs_unchanged. Patch old/new text permits tab/LF/CR, up to 65,536 characters,
but no other ASCII controls or DEL. Other text retains the 4,096-character rule.
Artifact counts fit uint64; instruction counts fit uint32. Header rows preserve
the existing uint32/uint64 structural bounds. These are structural claims, not
repeated ELF inspection, patch application, tool execution or SDK conformance.

Test retained variants, malformed nested fields, multiline compatibility and
fixed-path routing; run all checks. Preserve historical evidence, release pins,
success output, native inputs and sibling repositories. Missing original artifacts,
SDK semantic acceptance, filesystem deadlines/races and independent review remain
explicit BG-056 follow-ons.

Validation: all 27 retained SDK receipts, 69 focused tests and ten gates pass in
run-9nf8l3cz. Four manual lint/render commands pass. All attempts passed.
Audit output, catalog, 24 native inputs and release pins stay fixed. Evidence:
../evidence/sdk-receipt-fields-2026-09-07/.
