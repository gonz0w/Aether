# Change review — UL-062 extended matrix and compensation

- Requirement/UL ID: UL-062 PXM-01–04. Plan: PLAN.md in this directory.
  Inventory/driver only. No runtime parser or native behavior change.
- Applicable clauses: TC-01–03, TD-02/05, TE-01/03–04, E-01–08, DW/DS/DP,
  Experience CLI.
- Ownership: Aether-userland. Evidence hashes are identities, not authenticity.
  Native summaries are inspected, not rerun. Compensation is not a sanitizer
  equivalent and cannot waive PXE-04.
- Tools: Python 3.10+, existing evidence files. Suite under 30 seconds.
- Tests: live matrix check plus four in-driver mutants (PXE-04 pass, missing
  does_not_cover, missing file, wrong hash).
- Documentation: EXTENDED.md, PROCESS, coverage, BACKLOG/STATE, EXPERIENCE.
- Missing: independent review, ASan on a compatible pin, weekly cadence.
- Completion: does not close UL-062.
