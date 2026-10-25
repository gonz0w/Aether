# Change review — UL-005 SDK-08 closure selection

- Requirement: UL-005 SDK-08 selection only. Plan: PLAN.md in this directory.
  No native boot, sibling write or pin change.
- Clauses: E-01–08, TD-01, TE-01/03–04. Userland owns consumer identity; Aether
  owns native execution once a snapshot is captured.
- Bounds: inspect hashes of existing files. Live Aether is not copied (96G).
- Tests: closure JSON vs live sources/receipt/ELF; three mutants; NOT RUN native.
- Documentation: SDK-08-CLOSURE.md, sdk-consumer README, coverage, BACKLOG/STATE.
- Missing: captured producer snapshot, native pass/denial/cleanup, independent
  review. No waiver of SDK-08.
- Completion: does not close UL-005 or SDK-08.
