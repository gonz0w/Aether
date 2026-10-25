# Source metadata regression corpus — 2026-09-06

The host corpus has 71 cases with seed 20260906: a canonical positive, 24 required
field omission/duplication/empty-value cases, 16 order permutations, 16 unknown-key
cases, five malformed byte counts, five invalid hash lengths and four inert URI
controls. Each child has a five-second deadline. Input records and raw output are
retained. Exact diagnostic/status expectations are independent of parser output.
The original target bytes must remain identical and command-looking URI values
must never create the sentinel file. A 64-KiB URI is an accepted stress control;
this does not introduce or prove a parser resource bound.

The first attempt had an incorrect expected label (`source-record-invalid`).
The existing parser contract says `source-metadata-invalid`; the test expectation
was corrected, with the initial input/output/results retained. No parser source
was changed to satisfy the new tests. The focused corrected run passes all cases.
The source shell fixture now invokes the corpus in the ordinary suite, so it cannot
silently disappear from routine checks. Changed shell lint and development checks
are required separately; this work does not resolve remaining metadata lint findings.

This is bounded deterministic mutation coverage, not a deployed fuzzing schedule,
resource-exhaustion proof, remote authenticity check or snapshot freshness policy.

The full watchdog-controlled suite passed all sixteen fixture scripts and three
standards checks, including the 71 corpus cases. suite-corpus retains that separate
run; input identities were verified unchanged after completion.
