# Native bootstrap owner evidence review — 2026-09-06

Read-only package review of Aether-userland UL-058 NB-01. [Exact identities](review.json)
verify all 1,117 files in the owner manifest, 22 retained ISO/serial pairs (13 new
producer cases and nine original-pin regressions), and four native negative marker
sets. Copied receipts retain their original bytes. No sibling commands were executed.

Malformed second reference, descriptor and rights each produce child 95; the
separate early-publication mutant produces child 97. All four have parent 53 and
broker 970/reclaimed 0 with no CONNECTIONS PASS marker. This is scoped rejection
and no-publication/no-adapter-traffic evidence, not successful remote reclamation.
The owner's source, ELF inspections and channel-count assertions are retained in
the verified manifest; this review does not claim independent re-execution.

NB-02 has only preparation files at inspection, with no completed receipt. NB-02–04,
UL-059 public carrier/parser/consumer, ASan and Cam's reviews remain open. Native
shell/make execution and package persistence are separate release gates. Package
runtime, harness selectors, old pins and frozen archive remain unchanged.

Validation commands and exact documentation hashes are in validation.json.
