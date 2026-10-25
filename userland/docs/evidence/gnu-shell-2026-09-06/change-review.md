# UL-066 GNU shell/PTY review

- Requirement/scope: exercise pinned tr-case-class and stty-row-col scripts with
  unmodified upstream init support against existing static Linux-musl binaries.
  Exact plan snapshots precede each run. Userland owns selection evidence; no
  native runtime, shared API, package recipe, service or standards pin changed.
- Applicable rules: Foundations E, approved coding CP/CD, testing TD/TE, local
  Distribution PX/TX applicability and documentation process. These experiments
  do not adopt a user-facing renderer or modify the native command runner.
- Ownership/authority/lifetime: UUID-owned offline container, read-only repository,
  private 64 MiB scratch tmpfs, UID 65534, no capabilities/no-new-privileges,
  512 MiB/32 PIDs. The single-thread Python guest creates a private PTY, child
  session and controlling terminal, leaving stdout/stderr captured separately.
  The parent owns both descriptors and closes them in finally. No host tty used.
- Dependencies/provenance: candidate digests verified against GNU build receipt;
  source archive verified against source.lock before reading selected tests and
  init scripts. GPL notices and COPYING unchanged. Image digest pins bash and
  supporting utilities; runtime Python/kernel/QEMU hash recorded. Explicit quoted
  tr/stty wrappers select QEMU candidates. No package installation or SDK rebuild.
- Bounds/errors: each test child session has 45 seconds, process-group kill and
  five-second reap on timeout; outer container 180 seconds, owned removal in
  finally with 15-second bound. Fixed trusted test inputs, not adversarial output
  flood/fuzz coverage. No concurrent Python thread uses the preexec session setup.
- Oracles: unmodified upstream byte/diagnostic checks, exact eleven ordered
  row/column success lines and exit 0. Independent before/after termios and
  TIOCGWINSZ measurements require exact initial 24x80 restoration. Negative
  no-terminal run must return 77 plus prerequisite diagnostic; it is a harness
  control, never target coverage. Scratch empty and cleanup status zero required.
- Results/failures: initial run successfully executed scripts but local uppercase
  marker expectation rejected it; retained INCOMPLETE. Corrected lowercase exact
  inventory passes. Available tr cases pass; absent ISO-8859-1 means conditional
  branch NOT RUN, shown by locale probe and trace. All eleven window-size checks
  pass, both attempts restore state and remove containers. Shell syntax checked
  in actual image; Python syntax and final source receipt matches validated.
- Documentation/evidence: README reproduction/results, STATE next action, BACKLOG
  and draft coverage updated. Both attempts, raw JSON traces, source/runner
  snapshots, build receipt, validation and quality log retained under this bundle.
  Prior immutable evidence unchanged. Source/tool/image/config changes invalidate
  reuse; exact candidate byte checks justify this slice's reuse of prior build.
- Actual review: Codex task inspected upstream initialization, path-prepend rules,
  controlling-terminal prerequisite, cleanup trap, row/column expectations and
  first-party process/descriptor ownership. Independent technical reviewer and
  reader/recovery walkthrough remain pending UL-061–063. No broad security audit,
  sanitizer, fuzz, native authority or release conformance is claimed.
- Remaining: getlimits for stty-invalid, tracing for main stty, budget for pairs,
  unavailable locale branch, and an alternative to static-incompatible LD_PRELOAD
  bad-speed injection. UL-066 stays active. UL-008/012/016 retain native TTY,
  packaging and source/security work; quality migration remains UL-061–063.
