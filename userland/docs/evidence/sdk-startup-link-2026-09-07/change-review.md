# Change review — UL-005 imported SDK startup link

- Requirement/UL ID: UL-005 SDK-05 startup/adapter/helper closure. Plan:
  docs/evidence/sdk-startup-link-2026-09-07/PLAN.md. Host ELF link only; no
  execution, sibling write or pin change.
- Applicable clauses: E-01–08, TD-01–05, TE-01–03, CC-01, CP-01–03. Userland
  owns the consumer; pkg-mgr owns the imported payload already verified.
- Ownership/bounds: private build/sdk-startup-* copy of imported SDK after
  hash check. process.py 30s/16MiB/cleanup. No host header/libc fallback.
- Tools: pinned Clang/LLD 21.1.8 from native-stdio evidence. C17 with prior
  native-c diagnostics and assembly options. BSD-2-Clause adapters unchanged.
- Tests: positive crt1/crti/probe/io/memory/libc/crtn link; omitted crt1,
  omitted __aether_io, missing memory object path, missing __udivti3; reused
  missing-header/libc leaf controls. ELF64 x86-64, no INTERP/DYNAMIC/undef.
- Documentation: sdk-consumer README, coverage, BACKLOG/STATE.
- Missing: SDK-07 rebuild tracking, SDK-08 native run, independent review.
- Completion: does not close UL-005.
