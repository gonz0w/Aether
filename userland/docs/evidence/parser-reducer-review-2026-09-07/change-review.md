# Change review — UL-062 reduction outcome classification

- Requirement/UL ID: UL-062. Plan: PLAN.md in this directory. Classification
  only in check-parser-extended.py plus host unittests. C fixtures, parser,
  process helper, native contracts and pins unchanged.
- Applicable clauses: TE-01–03, TD-01–05, TC-02, CE-03–05, CP-01–03, E-01–08.
- Bounds: existing 225-byte/1024-call/30s/cleanup caps. Exit 91, incomplete
  cleanup, diagnostic noise, missing PASS, mismatched retain and invalid
  metadata abort reduction. Only exact PASS/no files is a negative.
- Tests: 11 in-process controls including old-logic false negatives; full
  --ubsan-only sweep on Python 3.14.7 and 3.10.21.
- Documentation: EXTENDED.md PXR-04a, coverage, BACKLOG/STATE.
- Missing: ASan, independent review. No waiver.
- Completion: does not close UL-062.
