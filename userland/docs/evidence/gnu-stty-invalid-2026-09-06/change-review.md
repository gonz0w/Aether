# UL-066 GNU invalid-input review

- Scope: build GNU's noinst getlimits helper from pinned source in a fresh private
  tree, then run unmodified stty-invalid.sh with the existing tr/stty candidates.
  Plan snapshots precede build/runtime. This is test support, not target package
  selection, installation or a native ABI change.
- Applicable requirements: Foundations E-01–08, approved CP/CD and TD/TE, local
  Distribution PX/TX applicability and documentation workflow. Userland owns
  evidence; no shared standard, service policy, recipe or sibling code changes.
- Provenance: same pinned Clang/LLD/LLVM tools, musl SDK and case-sensitive Linux
  UAPI export as GNU candidate builds. Builder verifies inputs before use, records
  compiler flags/configuration and applies the same static ELF restrictions.
  Upstream GNU source/licenses remain unchanged; first-party Python is BSD-2-Clause.
- Authority/lifetimes: existing offline image, owned UUID container, non-root UID,
  no capabilities/network, read-only repo, 64 MiB private scratch, 512 MiB/32 PIDs.
  Each PTY test owns a separate child session and controlling PTY. Parent closes
  both descriptors; timeout kills the test process group. No user tty is used.
- Bounds: each build command 240 seconds with process-group cleanup; tests 45
  seconds each within 180-second container deadline; container cleanup 15 seconds.
  Fixed fixtures only; no flood/stress/sanitizer claim. Python argv stays structured
  and generated wrapper paths quoted. Upstream shell syntax checked in the image.
- Oracles: helper executes under QEMU and must print ULONG_OFLOW=2^64. Upstream
  invalid test must return 0 and independently restore termios/window state.
  Require observed twelve speed checks and all four /dev/tty regressions, avoiding
  conditional-branch omission. The two saved-setting overflow checks remain in
  unchanged upstream script. Existing tr shell/window-size tests rerun, no-TTY
  prerequisite control stays status 77, and scratch/container cleanup must pass.
- Reuse: original GNU tr/stty binaries checked against prior receipt. Input/source,
  tool, config, helper or runner changes invalidate affected evidence. Build outputs
  stay under build/; immutable prior evidence is preserved. Retain raw build and
  test attempts, current source snapshots, receipts and helper binary here.
- Technical review: Codex task inspected upstream numeric-boundary generation,
  malformed arguments, conditional /dev/tty branch, helper pin validation and
  first-party subprocess/PTY ownership. Independent technical/reader review and
  sanitizer/fuzz/source-audit migration remain UL-061–063, not implied sign-off.
- Remaining scope: main stty tracing, expensive option pairs, unavailable locale
  branch and static-incompatible LD_PRELOAD bad-speed injection. Native TTY,
  packaging and source/security remain UL-008/012/016. UL-066 remains active;
  no whole-POSIX, native Aether, security, performance or release claim.
