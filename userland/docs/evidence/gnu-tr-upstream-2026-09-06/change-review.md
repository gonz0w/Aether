# UL-066 GNU upstream tr review

- Scope/requirements: exercise the pinned GNU tr.pl against the previously built
  static Clang/musl binary, with exact inventory and a deliberately failing
  candidate. PLAN snapshots identify the staged setup corrections. No change to
  package selection acceptance, native runtime, shared APIs or standards pins.
- Applicable clauses: Foundations E-01–08; approved CP/CD, TD/TE and documentation
  requirements through docs/quality/PROCESS.md. Userland owns selection/harness
  evidence; package, init and native TTY implementation contracts remain untouched.
- Ownership/lifetime/authority: one UUID-named container per run, read-only source
  mount, owned 64 MiB scratch tmpfs, non-root UID, no capabilities, no network,
  no-new-privileges. Perl runs in the image; explicit QEMU wrapper invokes the
  measured tr. Host Perl does not run the target binary. No user's TTY, install,
  header image, shared prefix or sibling repository is modified.
- Dependencies/tools: source archive checked against local lock before consumption;
  tr/Coreutils/CuSkip copied unchanged. BusyBox is not involved. Binary digests
  checked before execution against retained GNU build receipt. Image digest,
  Perl/QEMU hashes, Perl version, Linux kernel and wrapper hashes are recorded.
  File::Compare and Text::ParseWords are pure-Perl local 5.34 helpers pinned before
  consumption; upstream notices and Perl Artistic/GPL documentation retained.
  These do not become target dependencies. Trust/security review stays UL-016.
- Bounds/failure cleanup: 180-second runtime deadline, 512 MiB/32 PIDs, 64 MiB
  scratch, owned forced removal with 15-second bound in finally. All six cleanup
  statuses are zero. Fixed small fixtures bound ordinary log size; no fuzz or
  adversarial output flood is claimed. Python argv is structured and generated
  shell paths use shlex.quote. Wrapper shell syntax is checked in the image.
- Tests/oracles: exact 134 named test markers and upstream status 0 for positive;
  exit-99 wrapper must execute the same inventory, produce status mismatch and
  upstream status 1. Final controls match the final runner hash. Missing module
  and preload errors produce zero observed cases and are retained as incomplete.
  Upstream compares actual output/diagnostics/status. No assertions were relaxed.
  CuTmpdir is omitted because the owned container supplies private scratch; its
  Perl dependency closure is not needed. This is a scoped invocation, not a full
  make check claim. Final Python syntax validated on recorded host interpreter.
- Documentation/retention: README, STATE, BACKLOG and draft coverage updated.
  All six runs, helper licenses, source snapshots and raw logs retained here.
  Existing GNU and BusyBox evidence remains unchanged. Binary/build evidence
  reuse is limited to unchanged bytes checked against the GNU build receipt.
- Technical review: Codex task inspected subprocess ownership, path quoting,
  source pins, upstream input generation/status comparisons, marker inventory,
  setup failures, control rejection and cleanup. Independent technical reviewer
  and reader walkthrough remain pending, not implied by this task inspection.
- Remaining gaps: tr shell script and all stty scripts unrun. Main stty requires
  tracing; invalid needs getlimits; PTY and expensive-pair budgets need setup.
  Static LD_PRELOAD cannot exercise bad-speed injection. UL-061–063 retain review,
  inventory, extended/sanitizer/source-audit gaps; UL-008/012/016 retain native
  TTY, packaging and source trust. No source audit, security, performance, full
  POSIX, native Aether or release acceptance claim. UL-066 stays active.
