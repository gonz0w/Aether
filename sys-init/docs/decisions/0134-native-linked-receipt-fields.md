# 0134 — Native linked receipt fields

BG-056 host evidence slice, 2026-09-07. Apply Foundations E-01–08 and the local
quality process to producer summaries/reports, consumed service-worker receipts
and I/O supervisor build receipts. Validate before using linked fields. Preserve
all retained bytes, release pins, semantic oracles and native behavior.

Inventory: 45 summaries (2 legacy, 38 with host/tools, 5 normalized AENIN002),
45 producer reports, 18 consumed service-worker receipts and 22 I/O builds.
Require exact known fields, bounded collections/text, digest maps, command argv,
tool identities and ELF program-header integer rows. Summaries allow only their
three observed variants. Recorded commands and paths are data, never executed.
Reuse existing text/digest/path primitives; introduce no dependency or shared ABI.

Limits: 10,000 digest-map entries; 1,000 commands/cases/argv items; 64 tools,
suites or program headers; text 4,096 characters. Empty argv elements allowed;
booleans excluded from integer fields. Worker input maps must be nonempty and
inputs_unchanged must be true. Check producer case uniqueness and success.
Tests cover all retained variants, malformed nested records and early rejection
at each linked parsing site. Run focused and aggregate checks, retaining evidence.

SDK receipt recursion, unconsumed I/O worker reports, additional artifact
correspondence, filesystem deadlines/races and independent review remain separate
BG-056 work. This does not claim full producer-suite or SDK acceptance.

Validation: all 130 consumed linked receipts pass; 61 native-harness tests and
ten gates pass in run-boauxp1k. Four mandoc commands pass. Initial synthetic
fixture and new test setup failures were corrected and retained. Audit stdout,
catalog, 24 native inputs and release pins remain fixed. No native execution.
Evidence: ../evidence/native-linked-receipt-fields-2026-09-07/.
