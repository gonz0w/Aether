# 0139 — Producer receipt consistency

BG-056 host evidence slice, 2026-09-07; Foundations E-01–08 applies. Compare the
init suite case count in each legacy/host summary with its producer report.
Normalized summaries omit that field; preserve this documented variant. Compare
producer libc_receipt_sha256/libc_sha256/tools_lock_sha256 with the consumed
service-worker sdk_receipt_sha256/libc_sha256/tools_lock_sha256 respectively.
Worker links already bind these to retained files. No extra files are opened.

Inventory: 40 summary counts match; five normalized summaries omit counts. All
three links in 18 worker-bearing bundles match. The other 27 producer bundles do
not retain corresponding SDK/libc/tool-lock files. Of 395 recorded producer cases,
only 45 positive envelopes are retained; 350 other envelopes and all case serials/
ISOs are unavailable at their expected paths. Existing positive envelope/helper
comparisons remain authoritative, without a claim of full producer-suite auditing.

Test contradictory count and each dependency field plus normalized omission and
retained compatibility. Run focused/full checks. Preserve native behavior,
historical bytes, release pins and sibling repositories. No new dependency/API.
Source inventories have 8,307 summary and 3,430 report path occurrences, none as
standalone producer files; archive-member correspondence needs a separately
bounded archive-reader review. Missing artifacts, independent review and
filesystem deadline/race limits remain BG-056 follow-ons.

Validation: all 73 focused tests and ten gates pass in run-ch5gzenc.
Four manual lint/render commands pass; all attempts passed. Audit output, catalog,
native inputs and pins remain fixed. Evidence:
../evidence/producer-receipt-consistency-2026-09-07/.
