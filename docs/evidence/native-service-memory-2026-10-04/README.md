# One larger service memory owner

Status: private producer qualification passes, 2026-10-04.
[Before-code scope](contract.md) selects one 32 MiB service and three small
companions, with off-stack owner metadata and unchanged thread/authority limits.
[Interface and limits](../../NATIVE-SERVICE-MEMORY.md) record the remaining work.

196 target cases qualify: 162 maintained memory/thread, 14 origin/reuse/entropy,
seven M4, ten larger-owner, one unsupported envelope and two thread-storage.
190 are fresh guests; six main cases are recovered after exact rebuilt ELF,
supervisor and kernel identity with the original envelope/ISO/QEMU receipts.
Full 137 Python/Zig/Rust/pin/workflow, 13 memory, four partition/geometry and 17
launch tests pass, as do two actual removed-bound mutants and nine selected
prerequisite/release guards. Bare thread FS-cookie storage is not a musl TCB.

All failed attempts remain: launch test initialization, stop-marker wrapper,
three-full-generation timeout, unsuccessful fixture edit, metadata error-kind
expectation, missing explicit compiler atomic-header path, last-child observation
error-kind, thread handshake yield accounting, and removed-view error-name wrapper.
The separate big-image case repeats BSS/admission/stale checks three times and
full allocation once; ordinary positive retains two full-budget generations.
The watchdog remains 30 seconds. Quadratic kernel scans are a concrete next
latency task; this packet makes no performance or full-engine claim.

Recipes: sdk-setup, model, regressions, origin-regression, reuse-regression,
entropy-regression, guards, native, view-control and threads Python files here.
They use pinned offline SDK/tools and private copies; M4 uses the maintained
`python3 scripts/regression.py` runner. `checks.py` binds frozen inputs, exact
negative contexts, old isolated-alias source coverage (historical, not fresh),
format/pin/workflow and release guards. `archive.py` reads every archive member
before removing only owned duplicates. `manifest.json` binds all packet files.
Full-engine admission, independent reader/SDK adoption, persistent filesystem
and assembled R1 remain open. No sibling or released pin was changed.
