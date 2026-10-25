# UL-066 GNU tr/stty runtime slice review

- Purpose/plan: consume UL-068's isolated header view and execute the previously
  prepared seventeen fixtures. Final plan and source retained in harness; older
  failed source/build stages remain in tr-stty-source-2026-09-06.
- Scope/rules: E/PX/TX, CD/CP, TD/TE and DP; local userland experiment. No upstream
  C patches, native ABI, sibling policy or release-pin changes. Native TTY and
  package boundaries are not exercised by Linux reference execution.
- Inputs: coreutils 9.11 pin, verified baseline musl 1.2.6 SDK, Clang/LLD/LLVM
  archive tools, Linux 6.18.49 x86 UAPI export and immutable local runtime image.
  Configure/flags/config and closure are retained; GPL/per-file notices preserved.
- Findings/fixes: unqualified host ar/ranlib produced a Darwin archive index and
  link failures. Explicit LLVM archive tools fixed that. Both resulting executables
  linked but strict ELF inspection rejected four optional weak gnulib thread probes.
  The supported --disable-threads configuration for these single-thread utilities
  removes those probes. No weak-symbol waiver or successful unsupported stub.
  A premature runtime invocation rejected the missing build receipt before creating
  a container; no tests were counted. Final build/runtime both complete.
- Bounds/cleanup: 240-second owned build groups; container offline/read-only apart
  from private scratch, unprivileged UID, 512 MiB/32 PIDs and 180-second suite limit.
  Each subprocess has 15 seconds. Partial observations persist for interrupted
  suites; finally removes the owned container (observed cleanup status zero).
  Private PTY descriptors close in finally. No user terminal or /dev/tty access.
- Oracles: twelve tr byte/error cases, stdin-not-terminal rejection, PTY save,
  echo-disable readback, exact termios restoration and malformed mode with unchanged
  termios. Expected/observed stdout, diagnostics, statuses and termios values retained.
  Runtime kernel/QEMU bytes are recorded; all seventeen pass. No skip/empty pass.
- File inspection: static ELF64 x86-64, no interpreter/dynamic section, unresolved
  external symbols, W+X load segment or executable stack. These do not establish
  native loader enforcement. Sizes are unstripped files, not performance/security.
- Warnings/limits: raw upstream compiler warnings and cross-configuration guesses
  retained, including format-security diagnostics; complete source/security audit
  is pending. Source authentication, upstream suites and BusyBox comparison remain
  open. No syscall interruption, complete raw/canonical/session/job-control,
  window-size restoration, native authority or POSIX certification claim.
- Documentation/review: README, coverage, BACKLOG and STATE updated. This task
  performed technical inspection/execution; independent source/reader reviews
  remain pending UL-061–063. Final executable builder/runner/case source hashes
  match the actual successful receipts. Quality gate is scoped to pins/inventory.
- Decision: GNU reference slice passes; UL-066 remains active for the remaining
  comparison, upstream tests and review. Original musl SDK remains unchanged.
