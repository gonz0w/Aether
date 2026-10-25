# UL-066 BusyBox reference comparison review

- Requirement and scope: build the pinned BusyBox tr/stty candidate with Clang/musl,
  compare the existing seventeen GNU fixtures unchanged, and exercise focused
  upstream tests. PLAN.md snapshots precede the build and runtime work. Current
  harness sources, archive and SHA256SUMS identify this slice.
- Applicable requirements: local Foundations build/evidence rules and approved
  coding CP/CD, testing TD/TE and documentation clauses in docs/quality/PROCESS.md.
  Userland owns selection evidence. No shared interface, release pin, package
  recipe, service policy, native command-runner or sibling implementation changed.
- Ownership/authority/lifetime: build roots and run containers are uniquely owned;
  repo mounts are read-only at runtime, scratch disposable and no host TTY is used.
  Reference Linux ioctl semantics do not confer native authority. Explicit applet
  argv selects the measured implementation. Configuration and generated table
  require two applets, with no shell/SUID/runtime installer. No real-prefix install.
- Tools/dependencies: successful evidence.json pins Clang/LLD/LLVM tools, original
  musl SDK, source, UAPI files, compiler flags and generated wrapper. Separate UAPI
  receipt pins GNU make and host SDK selection. BusyBox license and full archive
  retained unchanged; first-party scripts carry BSD-2-Clause. Independent archive
  authentication and security/maintenance review remain UL-016. Upstream labels
  this version unstable. Compiler warnings remain raw evidence, not waived audits.
- Bounds/concurrency/failures: build commands have 240-second process-group timeout
  cleanup, two make jobs; runtime has 512 MiB/32 PIDs, offline/no-new-privileges,
  non-root UID, read-only filesystem and owned cleanup with 15-second bound.
  Focused upstream run has a 180-second deadline. Common runner retains its
  existing per-case/PTY/container limits. Cleanup returned zero on all three runs.
- Tests and oracles: static ELF inspection passes. BusyBox common fixtures return
  INCOMPLETE (13/17); four tr mismatches are preserved with expected/actual bytes,
  stderr/status. GNU regression passes 17/17 using the same revised cases.py.
  Five upstream tr tests pass; their harness checks stdout, not independent status
  equality. /bin/echo is an image helper. Invalid classes/ranges and no-terminal,
  invalid mode, /dev/full and exact PTY restoration are independent consumer cases.
- Attempts/retention: first build retained accidental sh selection and failed
  duplicate CRT link. Corrected wrapper omits CRT/libc only for partial links;
  final link still uses the pinned musl wrapper. No upstream source workaround,
  assertion weakening or successful unsupported stub. Both build roots, three
  runtime roots, source snapshots and failed logs are retained here.
- Documentation: README adds reproduction/results, BACKLOG and STATE name the
  next action, coverage links this evidence while remaining draft. Architecture
  and roadmap acceptance are unchanged because this does not complete UL-066.
- Reuse/freshness: original SDK receipt, unchanged SDK and UAPI inventory validated;
  builder/common/upstream source hashes match actual run receipts. GNU binary
  reuses coreutils-musl-bdcrzzq6 with a fresh runtime run. Affecting source,
  configuration, SDK, tool, fixture or image changes invalidate this evidence.
- Actual review: Codex task technical inspection of builder, partial-link wrapper,
  applet check, fixture dispatch, upstream runner and observed receipts. This is
  not independent review or maintainer sign-off. Reader/recovery walkthrough and
  independent technical review are pending UL-061–063; sanitizer/fuzz coverage is
  not supplied here. Remaining gaps include GNU upstream suites, BusyBox legacy
  scripts, wider termios coverage, native TTY authority and full POSIX behavior.
- Decision: retain GNU tr as provisional first choice; five matching stty cases
  do not decide its provider. UL-066 stays active, next GNU upstream suites.
  UL-008/012/016 retain native TTY, packaging and trust/security follow-ons. No
  release readiness, native execution, security or speed claim follows.
