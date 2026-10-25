# Standalone compiler-bound evidence

Decision 0098 bounds lifecycle and supervisor compiler calls to 180 seconds and
4 MiB, with owned process-group teardown, retained log prefixes and classified
attempt receipts containing helper/caller source identities. Three helper test
methods exercise success, nonzero, timeout, overflow and missing executable.
All ten aggregate gates pass in `out/checks/run-adyfr1pj`.

All three lifecycle and twenty supervisor build variants retain identical raw
and enveloped bytes; baseline.json/comparison.json retain commands and hashes,
and before/after directories retain artifacts and logs. These are build-only
comparisons with one fixed offline worker input, not new target execution or
qualification of arbitrary variant/input combinations. The compiler flags and
existing successful builder output are preserved. New per-attempt logs/receipts
are additive. Existing build directories can still contain prior artifacts after
a failed attempt; the nonzero builder exit and attempt outcome must be checked.

Native source/build inputs match the earlier boundary-review hashes. Release
pins and sibling repositories are unchanged. Complete per-profile source review,
interface manuals, operational support readiness and independent review remain
open under BG-056. No publication or candidate-adoption approval is implied.
