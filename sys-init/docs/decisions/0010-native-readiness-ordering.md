# 0010: Observe readiness history independently of terminal state

Accepted 2026-09-05, bounded BG-032/BG-040 experiment. The frozen BG-055 native
supervision contract defines readiness as retained per-instance history; terminal
instances are not currently ready (NATIVE-SUPERVISION.md, operations 0x20001/4).
Consume that contract without new kernel APIs or shared standards.

An opt-in worker profile writes generation-tagged output but withholds readiness
until instructed. The supervisor observes complete output with a live, unready
status, then requests exit, real UD2, explicit stop, ready-then-exit, or
ready-then-UD2. Poll terminal status directly, never require observing a live-ready
intermediate state. Retained readiness must be false for the first three paths
and true for the latter two. These are controlled orderings, not a claim of
exhaustive interrupt or SMP race coverage.

Reobserve each terminal tuple, retained output/EOF and rejected input; reclaim and
reject stale operations. A fresh generation must initially be unready, then
perform ready-then-exit, preserving only its own readiness and output. A control
that invents readiness for an unready normal exit must reject at an exact
assertion. Skipped zeroing must still reject. Preserve older worker/client bytes.

Retain source/link inputs, executable inspection and target logs separately.
The C/Rust code remains an experiment, not a production language decision.
General deadlines, late external notifications, delegated readiness authority,
supervisor recovery and cross-core ordering remain open under BG-032/BG-040.
