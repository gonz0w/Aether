# Change review — UL-005 SDK-08 first native cases

- Requirement: SDK-08 pass/denial/cleanup on an isolated producer snapshot
  plus the selected imported-SDK io_probe ELF. Plan: PLAN.md.
- Clauses: E-01–08, TD-01–05, TE-01–03. Aether owns native enforcement;
  userland owns consumer bytes. No sibling mutation.
- Snapshot: kernel/scripts/user/boot/tests, top-level docs md, .deps firmware/
  limine, sys-init scripts+native-supervisor prototypes. Exclude evidence
  archives and live zig-out.
- Tests: envelope pack; io supervisor wrap; zig -Dsmp=false -Dnative-memory;
  io_smoke pass; -Dnative-no-output denial; reclaim/cleanup from serial.
- Missing: historical contract pin, full test_io matrix, independent review.
- Completion: does not close UL-005 if cases fail or snapshot is incomplete.
