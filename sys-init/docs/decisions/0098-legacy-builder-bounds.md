# 0098 — Remaining standalone compiler bounds

Accepted bounded host build fix, 2026-09-06; BG-056 CP-02. Lifecycle and native-supervisor standalone
builders still invoke the compiler without a deadline. Add a small shared host
helper under scripts with the established 180-second/4 MiB bounds, owned tool
process-group teardown and per-attempt logs/status. Capture helper and caller
source identity in each attempt. It is a host build dependency, not target code.
Preserve existing successful stdout, flags, variant choices and envelope bytes.
Failed compilation must not look like a successful attempt; failure logs survive.

Build three lifecycle and twenty supervisor variants before and after, from the
same local input envelope/compiler. Require exact raw/envelope equality for every
variant. These are build-only comparisons, not new execution or proof that every
variant/input pairing is meaningful on target. Native source and profile pins stay
unchanged. Exercise positive, nonzero, missing tool, timeout and overflow at the
helper boundary, then run all development gates. No sibling or post-R1 changes.

## Results

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
