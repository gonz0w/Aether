# Exec descriptor preparation — 2026-09-10

Implemented a pure Rust candidate transform for the existing64-byte descriptor
snapshot:16 records and three bindings. It validates canonical records and local
use counts, removes FD_CLOEXEC entries, preserves surviving descriptor numbers and
binding identities, and computes local holder-release obligations without effects.
No input is mutated, backend contacted, capability granted or offset reset.

A release obligation drops this process's holder; it is not permission to close a
backend that another process still holds. The caller must authenticate session and
live binding rights, exclude concurrent mutation, bind the captured table to the
native commit identity, and resolve backend cleanup before publication. Image
rejection discards the plan unchanged. Unknown commit/close outcomes need containment.

The [pre-code selection](../../NATIVE-SHELL-STARTUP.md#exec-descriptor-preparation-selection--2026-09-10)
records scope, ownership, forbidden results, tests and simplicity. The routine is
not yet imported by a native owner. No installed SDK, sibling, released pin, kernel
ABI or existing native executable path changed. Native execve and dash acceptance
remain open. Earlier611 target passes are historical image-gate evidence, not fresh
target qualification for this routine.

## Checks

- Five Rust tests pass: shared aliases, all16 last-alias positions, empty/full tables
  and multiple closed aliases, malformed records at every position, and count errors.
- Two deliberate implementation mutations fail the named shared-alias test: retain
  CLOEXEC entries; release a binding that still has a surviving alias. Their compiler
  commands pass and test executables return101 with assertion failures. Generic
  compilation errors, crashes and timeouts cannot satisfy these controls.
- `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global` passes,
  including99 Python tests and the new Rust tests via `tests/test_exec_fds.py`.
- Scoped Rust formatting, workflow, standards and whitespace checks pass. The
  simplicity snapshot's fixed digest and four input hashes are verified.

Run the existing host command above to repeat the tests. The compiled positive
and negative test artifacts, mutated sources, raw logs and timed commands are in
this packet. All selected checks passed their intended oracle on the first attempt;
negative assertion failures are expected controls, not failed qualification attempts.

`sources.json`/`sources.tar.gz` preserve237 frozen inputs; `change.patch` compares
against the verified native-exec-gate snapshot. `checks.json` records commands,
start UTC, elapsed time and observed/expected exit codes. `tools.json` records
local compiler/interpreter/build-tool identity. All archived source bytes were
read back and checked, and the preceding evidence manifest was verified.
`manifest.json` seals the packet except itself.

Next wire this exact routine into the Rust owner and bootstrap the surviving table
into the replacement C client. Qualify rejected admission with unchanged descriptors,
shared offsets, final-holder cleanup and unknown-outcome containment in QEMU before
claiming native descriptor publication. Host tests establish only preparation logic.
