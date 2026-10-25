# Exclusive console handoff evidence — 2026-09-06

The [native v2 contract](../../NATIVE-CONSOLE.md) passes in QEMU: bootstrap moves
its duplex UART authority to a live child generation and loses access. Separate
conformance clients perform real serial I/O. This is not production sys-init,
a userland console service, TTY acceptance or a boot-to-shell release.

The final wrapper receipt in console-handoff-final-2026-09-06/results.json records
exact commands, UTC intervals and exit codes. All nine commands passed:

- Original v1 console mode, v2 handoff-close and v2 handoff-fault, each with positive
  binary exchange and wrong-input rejection (six target cases).
- Four existing native channel cases and seven M4 target regressions.
- Host checks (85 Python tests plus kernel, all offline standards and workflow),
  scoped Zig, Rust 2024 and pinned Clang-format 21.1.8 checks.

The v2 clients check invalid/stale/terminal targets, reserved-argument and wrong-
grant denial without losing ownership, removal of bootstrap access, denial of
onward transfer and denial in the subsequent slot generation. The fault run
requires actual generation-2 kind-2/detail-134 evidence before acceptance; it does
not close the grant before faulting. Wrong input yields worker 73 and supervisor
941/reclaimed 1 rather than a success marker.

## Retained attempts

console-mfp47w5b is the initial passing close-mode run. Its source archive was
captured immediately afterward and verified against every original receipt hash.
console-apo_iivj is the passing fault-mode run after adding automatic source
archival and the explicit fault-kind oracle. Final runs repeat all three modes
against frozen final runtime sources; their paths are recorded in wrapper logs.

console-pmz6m2cw is an intentional broken-kernel control: only the recipient
comparison against the task generation was removed. After the owner faulted,
the replacement received authority incorrectly; the client caught this and the
kernel rejected at supervisor 944/reclaimed 2. Its suite report says incomplete
because the positive expectation failed. The separate control receipt classifies
that exact failure as the expected mutation rejection. The original kernel bytes
were restored in a finally block before final qualification. No unplanned failed
attempt occurred in this slice.

All console attempts retain hash-verified source archives and their artifacts,
logs and receipts. The generation-control and final-run wrapper scripts are
included for inspection; the mutation script temporarily edits the working tree
and should only be run with no concurrent source work. Regression archives retain
their existing native evidence format. The strict SDK receipt/tool-lock hashes
are in console receipts. Installed Rust/QEMU/Zig selection remains the project's
pinned local toolchain; this does not claim complete transitive tool provenance,
an independent committed build or full standards compliance.

Production adapter assignment and owner adoption remain open. There is no
reopening/recovery after handoff, arbitrary forwarding, FIFO flush, dedicated
transferred-recipient stop test, interrupt-buffering or physical UART acceptance.
No sibling repository or consumer pin changed. Retain all attempts according to
DEVELOPMENT; a passing retry does not authorize evidence deletion.
