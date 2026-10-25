# Signal-copy contract review — 2026-09-10

Selected the next [native copy contract](../../NATIVE-SHELL-STARTUP.md#signal-state-across-native-process-copy--2026-09-10):
private copied action records and execution mask, empty child pending state,
unchanged parent pending state, and publication only after successful backing
preparation. Handler frames remain ordinary copied private memory, with existing
validated return checks. Rollback and reuse must preserve signal isolation.

Source review found that both freeze and copy reject the action-enabled profile,
even for default dispositions. Merely removing that gate would leave child action
records zeroed. Current execution-mask copying alone is insufficient. The gate
remains unchanged. The contract specifies eight witness groups before enabling
this extension; none is claimed executed by this review.

This is documentation-only work. All seven retained runtime source inputs match
the preceding mask packet. Host tests, standards, workflow, diff whitespace and
the four-file simplicity snapshot checks pass; exact commands and timings are in
checks.json. No failed test attempt occurred. The host log includes 98 Python
tests plus the build's Zig and offline pin checks. No fresh QEMU run was selected
because runtime sources did not change. Previous target evidence remains historical.

The source archive retains the reviewed kernel/client/harness and local guidance,
with SHA-256 identities and archive readback verification. The matrix is local
native producer work; userland SDK adoption and independent shell acceptance
remain separate. No sibling repository, release pin or shared standard changed.
No new tooling entry point or launch profile was added.

Next is implementation and target qualification of raw single-context signal-copy
state before composition with inherited streams and the SDK. Active-handler return,
parent pending delivery, child isolation and failure/reuse must all have direct
witnesses. Full dash, fork/exec/wait integration and R1 remain unfinished.
