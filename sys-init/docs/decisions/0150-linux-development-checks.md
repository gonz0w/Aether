# 0150 — Current Linux development-check attempt

BG-054, 2026-09-07. Run all ten gates from a private read-only source snapshot
using the previously pinned cached Linux arm64 image. Keep Podman startup and
execution in one session. No pulls/network, dropped capabilities, no privilege
escalation, 1 GiB RAM, two CPUs, 128 PIDs and 512 MiB private tmpfs. Retain existing
60-second/4 MiB gate bounds and use a 700-second outer wait with named-container
cleanup. Preserve failed gates and exact source identities, never turn missing
tools into skips or successes. Static settings currently have macOS-only tool
pins; Linux qualification must remain partial until actual provisioned tools and
reviewed identities exist. No automatic tool download, repin or runtime changes.

Run all local macOS checks after documentation/inventory updates. Keep native
and release bytes fixed. This is a host qualification attempt, not new native
execution, independent sign-off or production acceptance.

The initial snapshot omitted .planning and failed quality checks; retain it and
rerun with required planning records. Corrected full run blocks at missing Linux
rustfmt identity. Separate diagnostics expose absent rustup, a mocked test using
the actual platform, and missing writable sample-output mount. Scope expands
only to fixing that test fixture's platform selection (all tools already mocked)
and providing a private /work/out for diagnostics. Do not skip real tool tests.
Verify all five static-input tests on Linux and rerun sample receipt lookup;
retain pre-fix bytes, failed attempts and exact corrected commands.

## Result

Decision 0150 attempts current full Linux checks. Four initial gates pass; static
blocks at the missing Linux-aarch64 rustfmt identity. The cached image has no
rustup. Separate native-audit/model/host diagnostics pass; full qualification does
not. Corrected a mocked test's platform assumption; all five focused tests pass on
Linux and all ten macOS gates pass in `out/checks/run-vw4zfepp`. Failed snapshot,
output-mount and diagnostic attempts are retained. Native output/inputs and release
pins stay fixed. Next: provision Rust 1.98.0 compiler/rustfmt/Clippy for Linux,
review platform tool identities, then rerun all ten gates with private writable out.
Independent review, BSD/illumos and hosted scheduling remain open.
Evidence: `docs/evidence/linux-development-checks-2026-09-07/`.
