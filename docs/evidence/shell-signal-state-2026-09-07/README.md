# Nested native entry and architectural state witness

Before code: qualify nested caller-local upcalls and exact CPU restoration using
the existing runner-local fixture. No kernel/API/grant/quota or sibling changes.
The fixture lacks mapping authority; permission transitions remain a separate
explicit-grant experiment rather than an ambient shortcut.

Nested C handlers must observe inner/outer masks, preserve the complete outer
payload, and return normally through musl. An assembly witness owns fixed scratch,
saves caller FP/callee registers, initializes all GPRs allowed by the operation,
all XMM registers, x87 ST0, MXCSR and status flags, fills all 128 red-zone bytes,
and traps without a C call. The handler destroys the saved register values in
live registers; return must restore them. Snapshots/flag capture must not overwrite
the tested red zone, and cleanup must restore caller FP/callee state and clear DF.

Simplicity: C cannot prove this register boundary because its ABI permits compiler
clobbers. One assembly fixture plus the current C/harness seam is the smallest
credible witness; no test-only kernel flag or new runner. Nested skip, saved-R12
corruption and red-zone corruption controls must fail at exact terminal79/80 with
owner1501. No faults or timeouts count as a correct rejection. Select the full
command-runner and host suites, emitted-assembly review and existing style/pin
checks. Preserve attempts and freeze final test sources during qualification.

## Results

All 235 command-runner cases pass. The new positive completes two generations
with four domains reclaimed. Nested skip fails at terminal 79; saved-R12 and
red-zone corruption each fail at terminal 80; all three controls produce owner
1501. Exact statuses are required, so a fault or timeout cannot satisfy them.
The full host suite passes, including 98 Python tests, Zig tests, workflow and
offline standards checks. C formatting, Python syntax and simplicity snapshot
hashes pass. Emitted assembly was inspected for save/restore ordering, register
snapshots and flags capture below the tested red zone. No attempts failed or
were interrupted.

Only startup-client.c, the new frame-registers.S and launch_smoke.py change
relative to the prior qualified runtime sources. All 34 kernel files and
build.zig are unchanged. The assembly uses 1176 bytes of static scratch in this
single-context fixture. x87 coverage samples ST0, with no claim for every FP
configuration or AVX. Synchronous nesting is not asynchronous delivery.

Sources and target artifacts are hash-verified in the accompanying archives;
command-results.json retains case-level receipts. Prior evidence is preserved.
No sibling files, released standards pins or SDK inputs were changed. This is
not consumer sign-off or a completed full-dash handoff. Next is permission/unmap
transition coverage using the existing explicit memory grant, then pending
signals and interruption-safe transport.
