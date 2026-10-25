# Scratch exec preparation host evidence — 2026-09-14

Scope: explicit files preparation for sixteen descriptors, three stream bindings
and two scratch descriptions. Existing pure validation is reused; this entry point
has no native caller yet and grants no authority. No fork/exec publication, dash
redirection, persistence, consumer acceptance or release readiness is claimed.

`focus.json` records compilation and all29 Rust tests passing. These include13
shared descriptor tests and actual scratch owner/backend composition. Both file
bindings, mixed alias flags, every descriptor pair, full capacity and malformed
records/counts are covered. The composition retains parent access when the child
loses its CLOEXEC reader, preserves a child writer after parent close, verifies
shared-offset AB readback, and closes all backend descriptions. A discarded plan
has no owner effects; native admission/rollback is still unqualified.

Two separately compiled controls run only the named composition test. Offset loss
returns B instead of AB; premature backend close makes the parent reader fail
EBADF. Each fails one exact test with exit101, not a timeout. Sources are frozen
for these checks. `sources.tar.gz` and `sources.json` capture scoped sources and
reference/status snapshots; binaries are hash-bound in `binaries.tar.gz` and
`binaries.json`. Every archived byte was verified before removing loose duplicate
binaries. No previous evidence or sibling was changed.

`host.log` retains the first failed host run: the pipe wrapper expected27 tests
but the shared module now supplies29, all passing. Its original wrapper is saved
as `failed-attempt-test_pipe_owner.py.txt`. Only that expected count was corrected.
`host-retry.log` records the successful required Zig host run, including104 Python
tests and offline standards checks. `checks.json` records workflow, Rust formatting
and the simplicity extension manifest/four-member verification.

Reproduce through `zig build test --cache-dir .zig-cache --global-cache-dir
.zig-cache/global`; direct Rust commands and exact test names are in `focus.json`.
No new script entry point or native profile was added. Native wiring must qualify
full connections and matching command-runner before the next consumer handoff.
Confirmed-stop poison recovery, public SDK acceptance and R1 assembly remain open.
