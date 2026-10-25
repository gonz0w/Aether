# UL-066 GNU main and option-pair test review

- Scope/plan: add an opt-in extended run of the pinned upstream main and expensive
  pairs scripts, preserving the four-case regression suite. Source/plan identities
  are copied before runtime. No target rebuild, package install, shared interface,
  sibling change, pin update or native command-runner behavior change.
- Applicable rules: Foundations E; approved CP/CD, TD/TE; local Distribution PX/TX
  applicability and quality workflow. Implementation/evidence remain userland-owned.
- Inputs: unchanged GNU static tr/stty and getlimits receipt checks; source archive
  hash verified before copying tests/init/config and src/stty.c unchanged. Upstream
  Perl option scanning uses the pinned image interpreter. Preserve GNU licenses.
- Authority/lifetimes: UUID-owned offline non-root container, no capabilities,
  no-new-privileges, read-only repo, 64 MiB scratch tmpfs, 512 MiB/32 PIDs. Separate
  private controlling PTYs and child sessions per terminal script; both parent
  descriptors close in finally. No user terminal or UAPI image is involved.
- Bounds/errors: pairs 240 seconds, other scripts 45, container 420; process-group
  kill and five-second reap on script timeout, owned container removal in finally
  within 15 seconds. Fixed upstream option set, no unbounded fuzz. Raw trace and
  measured terminal state retained even on nonzero script outcomes. Cleanup and
  source matching required independently of a semantic pass.
- Oracles: existing four regression expectations remain. Extended pass requires
  both new scripts status 0, independent exact termios/window restoration and
  nonempty pair execution. Unsupported options are not filtered locally. Missing
  strace or other prerequisite is a skip, not target coverage. A host strace run
  around QEMU would not independently establish guest syscall behavior or native
  authority. No successful stub replaces a prerequisite or an unsupported option.
- Actual review: Codex task inspected upstream option discovery/reversible flags,
  main tracing prerequisites, expensive-test opt-in, script cleanup and first-party
  PTY/process ownership. No independent technical or reader sign-off; UL-061–063
  retain source audit, inventory, extended/sanitizer and review gaps.
- Retention/docs: preserve every run, exact output/status/state, script snapshots,
  input receipts and quality log. README/STATE/BACKLOG and draft coverage carry
  results and next action; immutable earlier evidence is unchanged. Any affecting
  source/tool/config/image change invalidates reuse. No broad POSIX, security,
  performance, native Aether or release acceptance claim.
- Observed result: extended INCOMPLETE. Main script returns 0 but final input-speed
  tests alter c_cflag; independent restoration is false. Pairs finishes status 1,
  reports 188 operation failures, all with cmspar, and restores state. 9,029 traced
  stty calls include setup/restore, not that many independent assertions. Prior
  four script/control expectations still hold. Scratch empty and container removed.
- Follow-up isolation: six fixed requests compare QEMU candidate and image stty
  on separate PTYs, ten seconds/request within an 80-second owned container, same
  resource/isolation limits and 15-second cleanup. Candidate cmspar fails while
  image stty sets it; -cmspar succeeds in both. Combined candidate parodd/cmspar
  fails but applies PARODD. Image digest pins the comparator; this does not hold
  implementation versions constant or prove a QEMU defect. Root cause remains open.
  Probe source and exact orchestration retained; both containers removed. PTYs
  are destroyed after observation, so main's nonrestoration cannot affect a user.
- Completion decision: UL-066 stays active. Next inspect exact candidate and
  QEMU termios translation; do not filter cmspar or relax restoration to claim
  conformance. Explicit recovery can be tested separately from upstream status.
