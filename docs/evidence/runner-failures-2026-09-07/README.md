# Runner operational failures — 2026-09-07

This extends the bounded AEOUT001 producer fixture, not the kernel ABI or native
resource limits. Userland owns real parsing/presentation and independent adoption.
See the [preimplementation contract](contract.md) and
[NATIVE-COMMAND-IO](../../NATIVE-COMMAND-IO.md) for the exact profile semantics.

The client stops on zero/negative write progress, attempts remaining alias closes
once, and returns operational status 1 after delivery/close failure. The owner
requires the selected failure to have actually occurred and verifies exact sink
prefixes, unchanged input, both aliases consumed and backend close/stale denial
before two-generation native reclamation. No child is launched or collected.

## Cases

- Zero and EIO writes after 16 stdout help bytes; zero progress after 16 stderr
  usage bytes. The other sink remains empty.
- Actual backend ENOSPC after 512 accepted bytes of a 528-byte X capacity probe.
  This is a resource witness, not CLI text or successful truncation.
- Complete help delivery followed by a consuming stdout close returning EIO;
  stderr still must close. Backend handles remain independently owned until
  readback and verified cleanup, regardless of parent close results.
- Retrying failed output rejects at 1310. Hiding a write failure or ignoring the
  close failure rejects at 1301. Fabricating exit1 without output rejects at 1311.
  These are exact oracle failures, not accepted recovery paths.

## Retained first failure

Attempt 1 passed the delivery/exhaustion witnesses, then failed the close-error
case at owner 1303 with zero native reclaims. The transport treated every nonzero
close response as ambiguous, poisoned the connection and prevented the second
alias's close from reaching the owner. This is an implementation failure, not an
expected negative test or runner/infrastructure failure. Remaining cases were not
run in that attempt. `attempt-1.tar.gz` retains source inputs, cases, artifacts and
logs, including the exact failing terminal status1 and owner1303 evidence.

The fix is scoped to AEOUT001: a complete valid EIO close reply confirms consumption
of that alias and permits cleanup of other roles. Malformed/other unknown close
responses still poison; legacy profiles retain their original behavior. The
contract records this distinction before the transport edit. No ambiguous backend
cleanup, unobserved result or lost reply is treated as recovered.

## Remaining scope

Ambiguous reply/transfer/close outcomes, remaining startup cases, exact denied
launches and composition with child launch remain open UL-059 coverage. The full
RL matrix, affected-owner review, immutable handoff and independent userland
build/adoption remain separate gates. UL-067 and the filesystem/package release
are not completed by these bounded failure witnesses.

Reproduce with the NATIVE-COMMAND-IO command using SDK
`/Users/cam/DEV/Aether-userland/build/native-c-5olokhku` and tools lock
`/Users/cam/DEV/Aether-userland/experiments/musl-reference/tools.lock.json`.
Use the same arguments with `--inherited-launch` and `--connections` for regressions.

## Final qualification

Attempt 2 passes all 85 command cases: previous 76 plus five operational-failure
witnesses and four exact rejection controls. Nine inherited-launch and six
connections regressions pass, as do all 98 Python tests, Zig tests and offline
pin/workflow checks. Rust/C formatting and diff checks pass. Sources remained
frozen through all three final suites and match each receipt. All 34 kernel/build
inputs match the preceding stream qualification. Stream supervisors remain at
most 5,200 bytes within the 8,192-byte bound. Pins and sibling files are unchanged.

`final-artifacts.tar.gz` retains frozen source snapshots, generated headers,
compiled/native envelopes, command results and serial logs. ISOs, duplicate
installed boot copies and kernel.elf are omitted; ISO hashes and commands remain
in receipts. `attempt-2.json` records final command-suite start/end UTC; other
receipt modification times are explicitly filesystem observations. Missing per-case
timestamps and independent owner review remain evidence limitations, not waived
standards or release gates. No ambiguous outcome is qualified by this result.
