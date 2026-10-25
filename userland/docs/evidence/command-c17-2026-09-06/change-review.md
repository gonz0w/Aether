# UL-063 CSR-03 edition and stale-scenario migration

Plan recorded before edits. Apply CC-01, CP-01, TD-01/03, TE-01/03 and
Foundations E. Scope: select C17 in the host/object and five-client build drivers;
remove unreachable small-pool, parent-first, reserved and bad-third-machine
branches from the native driver. Keep source-pinned producer C builds C11.
No C source, native protocol, startup, grants, diagnostics or exits change.

Risk: compile-edition changes may change code generation; branch removal may
alter scenario selection. Require all 21 host/control outcomes, five ELF
comparisons against retained UL-057 bytes, and all nine native cases with exact
markers, terminal ordering and cleanup. Existing pinned LLVM/SDK/host tools,
private roots, owned subprocess groups and deadlines remain authoritative:
30-second host commands, 180-second build/smoke wrapper commands, 30-second guest
watchdog, 15-minute native suite budget. No new dependencies or installation.

Retain before/after drivers, complete small build results, native receipts/logs
and artifact digests; large images stay under build. Preserve every attempt.
Quality gate required. Update source review, README, backlog, STATE and coverage.
Readability restructuring and independent technical/reader review stay pending;
current task performs technical diff and result review only. No owner API approval,
public aether-run implementation or UL-063 completion follows from this slice.

Actual review: current Codex task inspected the five-hunk diff, compared the
nine-case AST inventory, verified all five ELF identities and all native process
cleanup records. All selected runtime checks pass on the first attempt. No C
source logic changed; no additional sanitizer selection for this edition-only
migration. Broader instrumentation remains UL-062. Independent reviews pending.
