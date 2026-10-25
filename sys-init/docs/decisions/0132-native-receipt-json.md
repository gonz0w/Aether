# 0132 — Strict native receipt JSON parsing

BG-056 host slice, 2026-09-07. Parse every verified JSON receipt/report buffer as
UTF-8 with the existing 4 MiB/depth-32 limits, duplicate-key and non-finite rejection.
Require an object at each receipt root. Reject numeric overflow to infinity as
well as NaN/Infinity literals; preserve finite JSON numbers. Keep serial text
host-decoding behavior and existing semantic/identity checks unchanged.

Test all five receipt-reading sites, malformed/deep/overflow values and retained
compatibility. Run focused/full checks; preserve catalog/evidence/native bytes
and pins. E-01–08 scope is host parsing, not complete per-schema field validation.
Exact receipt fields/types and reviewed extension policy remain BG-056 follow-ons;
sequential filesystem race limits and independent review remain open.

Validation: 53 native-harness tests and all ten gates pass in run-zw1mn0x6.
Native audit output, catalog and 24 native inputs stay unchanged. Four manual
lint/render commands pass. Evidence:
../evidence/native-receipt-json-2026-09-07/README.md.
