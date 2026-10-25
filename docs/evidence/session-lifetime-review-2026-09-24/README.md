# Composed-session lifetime review

2026-09-24. Prospective owner design only; SESSION-01–06 has NOT RUN.

The [owner review](../../NATIVE-SHELL-STARTUP.md#composed-session-lifetime-review--2026-09-24)
derives the unchanged workload's lifecycle: nine children and seven exec replacements
per shell; three shells require27 copies,21 replacements and30 process reclaims.
It identifies three-use retirement limits, PID-delta/wait identity assumptions and
fixed argv/environment admission that prevent composition. It specifies reuse
barriers, bounded profile changes and semantic negative outcomes before code.
AENMX007/ABI21 remains a reserved design, not an implemented launch format. Wire
framing and linked stack review are still required before native qualification.

No runtime, sibling, released pin or earlier evidence changed. The existing dirty
worktree is preserved. The four changed planning/reference documents are retained
in review-inputs.tar.gz and verified by SHA256 in verification.json. This packet
records a design review, not independent approval, native delivery or full-shell
acceptance. No new runtime/tool entry point requires a workflow inventory change.

## Validation

- All306 runtime/host inputs match the previous sealed host-inputs.json, including
  tests/test_build_policy.py. No new native run is justified for this documentation
  step; previous QEMU results are not represented as fresh execution.
- All six archived consumer inputs match their pins, including unchanged script,
  helper and the independent65-byte stdout/19-byte stderr expectations.
- `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`
  exits0:110 Python tests plus the configured Zig/Rust and offline standards checks.
  Full output is host.log; cached build steps may be reused.
- Simplicity manifest digest and all four files verify; explicit workflow and
  `git diff --check` pass. Commands, durations and exit codes are in verification.json.
- Local links introduced by this step and review archive readback are checked.

Next implement the explicit bounded profile and reusable authenticated dispatcher,
then execute the whole script and controls on frozen sources with fresh matching
producer suites. Userland replay follows delivery. This review does not complete
SESSION, shared SDK adoption, persistence, packages or the R1 bootable shell.
