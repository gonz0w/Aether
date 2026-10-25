# 0112 — Static record reference

BG-056 documentation and contract-coverage slice, 2026-09-06. Document the
current static-tools and native-boundaries record fields, reader order, source
selection, tool execution, result records and ownership/lifetime limits. Separate
maintainer review requirements from checks the reader actually implements.
No executable/settings/pin/native byte changes are authorized in this slice.

Add focused source-scope/boundary contract tests for currently uncovered recursive
versus top-level selection, path/symlink rejection, combined-byte accounting,
duplicate records and textual site matching. Existing real compiler/tool cases
remain. Run the aggregate and retain source identity and real report evidence.

Follow-up under BG-056: strict bounded duplicate-key/schema/type validation before
tool lookup; consistent structured failures for missing/wrong-type fields;
ordinary-file and parent-symlink policy; settings/inventory before/after identity;
complete tool-host dependency closure. These are review findings, not accepted
public APIs or promises that trusted mutable configuration is safe to ingest.
No new native witness is needed for documentation/tests only. Independent reader
review and installed manual coverage remain separate publication work.
Evidence: docs/evidence/static-record-reference-2026-09-06/README.md.

Validation: five focused record tests and all ten gates pass in
out/checks/run-n1dguucj. The real static report matches the documented field set.
Static reader/settings/boundary hashes and all 24 checked native inputs remain
unchanged. Validation gaps are recorded in the reference and BG-056.
