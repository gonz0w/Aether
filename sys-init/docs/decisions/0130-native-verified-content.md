# 0130 — Verify semantic buffers against retained digests

BG-056 host slice, 2026-09-07. Capture each semantic input once with the bounded
reader, verify that buffer against the pinned manifest map, then decode/parse it.
Require subsequent receipt-correspondence hashes to match the same manifest map
as well, preventing inconsistent cross-receipt comparisons. Keep buffers local to
each read; do not cache whole bundles or change semantic report/serial/envelope rules.

Test semantically harmless late changes, verification before JSON parsing and
retained positive/negative controls; run focused/full checks. E-01–08 host scope.
Preserve catalog, evidence, native source and release pins. Strict receipt schemas,
complete membership/final consistency, filesystem I/O deadlines and independent
review remain open. Verified consumed buffers do not establish an atomic tree.

Validation: 47 native-harness tests and all ten gates pass in run-718_ig3c.
Native audit stdout, catalog bytes and 24 native inputs remain unchanged.
Four manual lint/render commands pass. Evidence:
../evidence/native-verified-content-2026-09-07/README.md.
