# Console/channel composition evidence — 2026-09-06

AENSC003 / ABI 12 combines the existing init/channel launch mechanisms with UART
handoff. A console conformance task reads real QEMU serial bytes, sends them to a
separate client address space, receives its reply through a second channel, then
writes it to serial. The client cannot access the UART. Neither executable is a
production terminal adapter, shell or sys-init implementation.

The final wrapper receipt in console-relay-final-2026-09-06/results.json records
commands, UTC intervals and exit codes. All commands pass:

- Eight console cases: original v1, exclusive handoff-close, handoff-fault, and
  composed relay, each with a wrong-input rejection case.
- Nine existing native init cases, four channel cases and seven M4 target cases.
- Host checks (85 Python cases plus kernel and offline standards/workflow checks),
  scoped Zig, Rust 2024 and pinned Clang-format 21.1.8 checks.

The relay client checks all UART operations are denied, validates the eight-byte
binary payload, and replies via its granted writer endpoint. Bootstrap checks it
lost both channel endpoints and console ownership. Both workers terminate and
close their channels; a replacement in the former console slot is denied UART
access, and three total reclaims precede the unchanged console pass marker.
The new profile also checks the bootstrap clock grant; comprehensive wait behavior
is covered by the unchanged init suite, not claimed as a new production consumer.

## Attempts and oracle control

console-je36qc1q is the initial passing relay attempt. The final wrapper repeats
it on the final frozen runtime sources along with all selected regressions.

console-pel_ccgw deliberately changes the client's first reply byte from 'a' to
'`'. The guest finishes, but the external serial-byte oracle rejects the altered
reply with `serial output mismatch`. This proves a guest success marker alone
cannot pass the round-trip test. The original source was restored in a finally
block before final qualification. Its incomplete suite status is classified as
an expected reply-corruption rejection in the separate control receipt.
No unplanned failure occurred in this slice.

Every console attempt retains a source archive verified against every digest in
its receipt, plus artifacts, raw serial logs and commands. Final-source regression
archives and both wrapper scripts are included. The corruption wrapper temporarily
edits a source file and requires exclusive working-tree access. SDK receipt/archive
and tool-lock identities remain in the native receipts; local installed toolchain
selection does not establish complete transitive provenance or an independent
committed build. All retained raw serial logs intentionally contain control bytes.

[Native contract](../../NATIVE-CONSOLE.md) defines layout, authority and limits.
No new syscall, pool or dependency was added. Existing envelope versions and
consumer pins remain unchanged. Production console routing, shell/process/TTY
behavior, sys-init consumption, durable storage and package integration remain
open. Retain all attempts under DEVELOPMENT policy; no release claim follows.
