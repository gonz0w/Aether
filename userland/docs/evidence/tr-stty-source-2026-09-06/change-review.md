# UL-066 tr/stty review

- Purpose/scope: pin providers, inspect exact features/dependencies, attempt GNU
  static Linux-musl build; prepare independently expected byte/error/PTY tests.
  Plan/source copies retained in harness; no native or release acceptance.
- Applicable rules: E-01–08, PX/TX, CD/CP, TD/TE and DP. Local userland ownership;
  pkg-mgr consumer whitespace use read only. No sibling/shared-standard mutation.
- Ownership/lifetimes: private build directories and process groups; 240-second
  phase deadline with group termination. Runtime runner is prepared for one owned
  offline read-only container, 512 MiB/32 PIDs, 180 seconds, and 15-second cleanup.
  PTYs are owned within that container, never the user's terminal. Runtime cleanup
  is not exercised yet; missing candidate binaries prevent runtime acceptance.
- Inputs/licenses: archive pins before extraction, safe data extraction filter,
  existing compiler/wrapper/SDK verified before build. Coreutils tr/stty GPLv3+,
  BusyBox distribution GPLv2 only; complete archives/notices retained. HTTPS bytes
  and BusyBox published SHA match do not authenticate a signer. UL-016 pending.
- Commands/compiler: builder copies and commands.json per attempt record exact
  argv; Clang/LLD 21.1.8, musl 1.2.6 Linux reference. SDK/tool receipt retained.
  CFLAGS -O2 -fstack-protector-strong; optional libraries disabled explicitly.
  Whole host tool/OS transitive closure is not hermetically pinned.
- Outcomes: configure succeeded; first direct-target build omitted generated
  gnulib headers. Explicit BUILT_SOURCES completes in second attempt, which fails
  at copy-file-range.c's linux/version.h include. No fake UAPI declarations or
  changed libc-function answers were introduced. Full config guesses/warnings
  remain retained, including format-security warnings requiring source review.
- Tests: fixed independent expected stdout/exit/error observations, private PTY
  echo transition and exact termios restore prepared (17); NOT RUN. Upstream
  suites discovered but NOT RUN. Host syntax and empty-inventory/changed-digest
  rejection controls pass. No speed, security or conformance inference.
- Documentation: README, source comparison, plan, BACKLOG, STATE and draft
  coverage updated. No new shipped CLI or rendering behavior; upstream unchanged.
- Review/evidence: this task performed source inspection and attempted builds;
  separate independent technical and reader reviews pending UL-061–063. Source
  review hashes verified; failed network DNS attempts preceded successful approved
  HTTPS acquisition and consumed no partial archives. No install/VM changes.
- Completion: source/build investigation recorded; UL-066 active. UL-068 must
  provide pinned Linux UAPI headers in a separate reference view and rerun build
  before runtime claims. BusyBox build, broader source-security review and native
  TTY/package boundaries remain open. No companion completion is required here.
