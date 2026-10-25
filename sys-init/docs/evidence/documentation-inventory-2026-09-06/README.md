# Developer documentation evidence

Decision 0099 records 18 developer entry points, source hashes and literal
argument declarations, plus narrative coverage and missing manual/API work.
The aggregate command has a canonical source-checkout mdoc manual.

Selected --help/--version/invalid-option probes pass with expected 0/0/64
statuses. All ten aggregate gates pass in out/checks/run-vj3xc1hy; retained under
validation. Inventory identities and references were checked against current
sources. These are documentation/host checks; no native target execution.

mandoc terminal output at 78 and 60 columns was read locally; HTML was generated
but has not had visual or independent reader review. Initial lint warnings are
retained. Final lint exits 1 with only the exact explicit experimental OS STYLE
notice recorded in checks.json and DOCUMENTATION-INVENTORY.md. It is not a
zero-exit strict-lint pass. The host mandoc has no -V option (exit 5 retained);
its executable hash and host identity are recorded, not an invented version.

Two intermediate validation assertions rejected the lint result: first an
incorrect expectation of exit 0, then an incorrect assumption diagnostics were
on stderr. This mandoc writes that notice to stdout. The final check accepts
only the exact one-notice result; it does not ignore unknown diagnostics.
The source extractor produces the initial inventory; the check-all manual
reference/disposition was subsequently added by source review.

Independent technical/reader review, HTML visual review, remaining manuals and
assembly-owner target installation/lookup remain open. The style disposition
must be revisited at publication/tool change. Existing shared release pins and
native source bytes remain unchanged. No sibling repositories were edited.
