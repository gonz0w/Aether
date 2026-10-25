# 0141 — Producer source correspondence

BG-056 host evidence slice, 2026-09-07; Foundations E-01–08 applies. Compare every
producer report source digest with the summary map already verified against the
source archive. Missing or conflicting source entries reject. Preserve exactly
ten historical omissions: kernel/.DS_Store and kernel/arch/.DS_Store in the five
normalized bundles recorded by decision 0140, with their exact recorded digests.
Scope the exception to the five existing manifest hashes plus normalized summary
schema; changed pins, names or digests get no exception. Never exempt present but
conflicting data. No archive files, receipts or pins are rewritten.

This checks all 3,420 available source references and explicitly retains ten
unverified metadata references among 3,430. It does not claim full source closure
for those five snapshots. The exception is historical compatibility, not a new
producer rule; new/repinned evidence must be complete or receive its own review.
Record the shared E-01/E-05/E-08 scope limit in STANDARDS.md. Tests cover retained
variants, conflicting/unknown/missing sources and pin/schema/name/hash scope.
Run focused/full checks; native behavior and sibling repositories stay fixed.

Missing producer/SDK/ISO artifacts, independent review and filesystem deadline/
race limits remain BG-056 work. Further evidence work should consolidate these
limits and prioritize unresolved operational checks rather than fabricate history.

Validation: 77 focused tests and ten gates pass in run-me3ukw5u. Four
final manual lint/render commands pass after one overlong source line was reflowed;
initial lint output is retained. Audit output, catalog, native inputs and pins
remain fixed. Evidence: ../evidence/producer-source-correspondence-2026-09-07/.
