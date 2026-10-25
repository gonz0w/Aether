# UL-063 CSR-01/02 correction review

- Scope/requirements: TOOLING-PLAN precedes implementation. Owned subprocess
  lifetime/evidence and explicit environments in check.py, prepare-native.py and
  native.py. No C source, public command behavior, protocol, pin or owner policy
  changed. CP/CE/CD, TD/TE and Foundations E apply; first-party BSD preserved.
- Ownership/errors: new session/process group, file-backed stdin/stdout/stderr,
  partial output retained, start failure and timeout records. Remaining descendants
  prevent success. Group kill, direct-child reap and disappearance checked with
  bounded waits. Caller checks both completed cleanup and expected return code.
  No daemon/session-escape support or native process semantics inferred.
- Inputs/tools: exact environment/cwd/absolute command, resolved executable hash
  per invocation; fixed native tool lock before consumption. Rust dylib path only
  for Rust, private hashed wrapper for nested calls. Source/SDK and producer boot
  checks retained. No ambient compiler/PATH/loader settings silently propagated.
- Bounds: existing command deadlines retained; cleanup up to five seconds reap
  plus five seconds group disappearance. Default 16 MiB per-file limit; native
  build explicitly 512 MiB. No aggregate disk/memory quota claim. Local temp paths
  remain under build. Trusted bounded labels and single-thread preexec usage.
- Tests/results: seven process/environment checks pass; timeout-grandchild and
  early-leader-exit leave no live group. Missing tool retains start failure;
  normal/nonzero results distinct. Actual hostile PATH/CC/CPATH/CFLAGS build from
  foreign cwd passes all 21 cases. Normal host 10+11 pass; five native ELFs identical.
  Nine native scenarios pass with exact old terminal markers and cleanup.
- Failed attempts: Rust linker library lookup, shared LLVM collision with Zig,
  nested producer Rust lookup and missing xorriso retained as incomplete native
  runs. Recovered failed native.py snapshots match stored hashes exactly. Final
  tool selection isolates dependencies rather than restoring ambient environment.
- Actual review: current Codex task inspected process lifetime/finally behavior,
  result enforcement, explicit test-env preservation, nested smoke ownership,
  source identities and cleanup receipts. Independent technical/reader review
  pending, not replaced by passing tests. Output-flood/sanitizer/full dependency
  audit and detached-session cleanup are not claimed.
- Docs/retention: audit, README, BACKLOG, STATE and coverage updated; failed and
  successful raw logs, source snapshots, tool pins and receipts retained. Large
  native boot images/dependency copies remain in build with receipt identities.
  Historical source/evidence unchanged. No native bootstrap/public CLI acceptance.
- Completion: CSR-01/02 corrected in scoped drivers; UL-063 active for remaining
  migration/review and UL-059 active for owner handoff. UL-058 boundaries still
  required before public native runner; UL-069 remains deferred.
