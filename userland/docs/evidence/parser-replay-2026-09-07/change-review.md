# Change review — UL-062 parser replay and reduction

- Requirement/UL ID, exact source/plan identity, purpose and supported scope:
  UL-062 current slice PXR-01–05. Plan:
  docs/evidence/parser-replay-2026-09-07/PLAN.md. Host command-runner parser
  fixture only; runner-parse.c, native interfaces, siblings and release pins
  unchanged.
- Applicable standards clauses and affected owner/consumer contracts:
  Foundations E-01–08, I-03; Testing TD-01–05, TC-01–03, TE-01–05; Coding
  CE-02–09, CC-01–04, CP-01–03; Documentation DW/DS/DP; Experience output/exit
  rules for the existing contributor CLI. Aether-userland owns the fixture.
- Ownership, lifetime, authority, bounds, concurrency and failure/cleanup review:
  Exclusive create of failure.bin/json in a private child cwd. Replay reads at
  most 226 bytes and accepts at most 225. Pointers to active inputs stay live
  only during need()/retain. Each replay/reduction step uses a unique owned
  directory, process.py cleanup and 16 MiB output caps. No shared directory,
  network, VM or production bypass.
- Language/compiler/flags, dependencies/provenance/licenses and resource budget:
  C17, pinned Clang 21.1.8, existing UBSan selection, Python 3.10+ standard
  library. BSD-2-Clause original work. 30-second child timeout, 1024 oracle
  calls, 180-second gap, 225-byte cap. No RSS budget. Default ASan remains
  required and still known-timeout on this host.
- Test IDs, family/layer/stage, commands, tools/platform, deadlines and isolation:
  PXR-01–05 plus PXE-01/02/03/05 regressions. Command:
  python3 -B experiments/command-runner/check-parser-extended.py --ubsan-only
  on macOS arm64, then Python 3.10.21. Format and local quality gate.
- Independent success/denial oracles, fault controls and expected cleanup:
  Named ORACLE + exit 90 + retained bytes/metadata. Original parser must pass
  the reserved-byte input. 91 for missing/invalid/oversized/colliding files.
  Synthetic deletion/zero/non-reproducing/budget controls. Complete process
  cleanup required.
- Documentation surfaces changed, canonical references and inventory updates:
  EXTENDED.md, coverage.json UD-parser-extended, PROCESS extended-stage wording,
  BACKLOG/STATE. No public CLI flags added.
- Evidence for every attempt, expected/observed results, hashes and retention:
  Private build/parser-extended-* plus curated copies in this directory. Keep
  failed attempts. Prior sweep evidence binds old sources only.
- Reused evidence identity/impact review; freshness and invalidation triggers:
  Reuse the pinned Clang identity from native-stdio libc evidence. New fixture
  sources invalidate that sweep's qualification of these files.
- Missing coverage, defects, suppressions, risk, compensation and expiry:
  ASan timeout, sanitizer-only crash isolation, transport/concurrency stress,
  static analysis, RSS budgets, native compensation and independent review
  remain open. No waiver.
- Actual technical reviewer and separate reader walkthrough evidence, or pending:
  Pending. This record is not approval.
- Final scope, unresolved follow-on UL IDs and completion decision:
  This slice does not close UL-062.
