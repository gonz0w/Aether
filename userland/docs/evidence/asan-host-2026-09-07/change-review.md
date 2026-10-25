# Change review — UL-062 pinned ASan host diagnosis

- Requirement/UL ID: UL-062 PXA-01–04. Plan: PLAN.md in this directory.
  Diagnosis driver only; no production parser/adapter change; no compiler pin
  change.
- Applicable clauses: E-01–08, TD-01–05, TC-02, TE-01–04, CC-03, DW/DS/DP,
  Experience CLI.
- Ownership/bounds: process.py for UBSan and Apple comparison. Sampled ASan
  hang uses an owned session, 5-second bound, SIGKILL process-group cleanup.
  Apple clang is comparison-only.
- Tools: pinned Clang 21.1.8, /usr/bin/sample, Apple clang identity recorded
  separately. Python 3.10+. 60-second suite.
- Tests: deadlock sample oracles, UBSan empty-main success, Apple ASan
  comparison success, pinned ASan canary timeout without diagnostics.
- Documentation: EXTENDED.md, PROCESS UL-062 row, coverage, BACKLOG/STATE,
  EXPERIENCE scoped CLI note.
- Missing: ASan still not qualified on the pin. Independent review pending.
  No waiver.
- Completion: does not close UL-062.
