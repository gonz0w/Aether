# Change review — UL-062 host static/resource/concurrency/transport

- Requirement/UL ID, exact source/plan identity, purpose and supported scope:
  UL-062 next host slice. Plan:
  docs/evidence/extended-host-2026-09-07/PLAN.md. Host fixtures and contributor
  driver only. Production parser/adapter unchanged.
- Applicable standards clauses and affected owner/consumer contracts:
  E-01–08, I-03, TD-01–05, TC-01–03, TE-01–05, CE-02–09, CC-01–04, CP-01–03,
  DW/DS/DP, Experience CLI rules. Aether-userland owns the fixtures.
- Ownership, lifetime, authority, bounds, concurrency and failure/cleanup review:
  Analyzer runs are offline and write private plists. RSS uses getrusage, not
  unsupported Darwin rlimits. Forked children _exit; parent waitpid. Transport
  peer is process-local channel_raw. process.py owns each driver child including
  the 5-second hang watchdog.
- Language/compiler/flags, dependencies/provenance/licenses and resource budget:
  C17, pinned Clang/clang-tidy 21.1.8, UBSan on executed C, Python 3.10+.
  BSD-2-Clause. 32 MiB observational RSS budget for parser work; 3-minute suite;
  30-second children except hang at 5 seconds. No new dependencies.
- Test IDs, family/layer/stage, commands, tools/platform, deadlines and isolation:
  PXS-01–02 static/build; PXB-01–02 performance/metrics; PXC-01–02 concurrency;
  PXT-01–02 stress/fault. Command:
  python3 -B experiments/command-runner/check-extended-host.py
  macOS arm64, then Python 3.10.21.
- Independent success/denial oracles, fault controls and expected cleanup:
  Analyzer silence vs required null-deref text. RSS under/over oracles and
  undirtied mmap control. Eight child exit 0; hang timeout+cleanup. 3072
  channel_raw then poison/no-replay.
- Documentation surfaces changed, canonical references and inventory updates:
  EXTENDED.md, coverage.json, PROCESS extended row, BACKLOG/STATE, EXPERIENCE
  scoped CLI note.
- Evidence for every attempt, expected/observed results, hashes and retention:
  Private build/extended-host-* plus this directory. Keep failures.
- Reused evidence identity/impact review; freshness and invalidation triggers:
  Reuse Clang identity from native-stdio libc evidence. Parser sweep evidence
  remains valid because those sources are not edited. New fixture/plan changes
  invalidate this slice only.
- Missing coverage, defects, suppressions, risk, compensation and expiry:
  ASan still NOT RUN. Darwin cannot set RLIMIT_AS/DATA. Native sanitizer
  compensation remains documentary. Independent review pending. No waiver.
- Actual technical reviewer and separate reader walkthrough evidence, or pending:
  Pending.
- Final scope, unresolved follow-on UL IDs and completion decision:
  Does not close UL-062.
