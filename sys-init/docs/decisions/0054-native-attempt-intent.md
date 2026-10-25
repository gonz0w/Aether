# 0054 — Native deadline precedence and service cancellation intent

Accepted 2026-09-06 for BG-058/BG-040's bounded Attempt policy.

Extend wait registration with explicit observed revision and InterruptTick deadline;
the existing convenience method retains its distant-deadline behavior. Preserve
adapter completion kind/revision/tick. A controlled fixture registers three terminal
workers: (1) past/current deadline plus revision zero yields Timeout, (2) distant
deadline plus revision zero yields Changed, (3) current revision plus distant
deadline yields Pending then Cancelled. Cancellation must preserve an already
selected Timeout or Changed result. All tokens require explicit cleanup release.
No wall-time calibration or general interrupt-race coverage is claimed.

Add retained service-cancelled intent, set before requesting native stop. If a worker
exists, invoke Adapter::stop; keep worker, reader and wait fields intact until
terminal observation and explicit cleanup. A failed stop leaves cancelled intent
and ownership intact. If no worker exists, cancellation still suppresses future
launch/retry. Local intent denial is operation=0/errno=13, distinct from kernel
operation identity. Wait cancellation does not set service intent. This is forced
native stop, not graceful POSIX signal delivery or an operator authentication API.

A second fixture cancels a busy failed attempt, cleans its endpoints and blocker,
and verifies retry is denied locally before new channel acquisition. It then starts
a live worker, registers a wait, cancels service intent, confirms ownership remains,
observes stopped terminal detail 144, and cleans reader/worker/wait. One final
normal worker completes the existing result=100/reclaimed=3 oracle.

Controls: deliberately map Timeout completion to Changed in the fixture status
projection and require assertion 980/reclaimed=0; omit storing cancelled intent
and require 981/reclaimed=1 when retry wrongly reaches acquisition. Both must hit
exact designated profile rejection, not timeout/generic boot failure. Four new
cases join all 23 prior cases on pinned SI-04/Rust 1.98.0/4 KiB/BSP-only inputs.
Compare binaries, preserve differences, retain sources/logs and run full checks.

The authoritative precedence comes from frozen native_wait.zig refresh: deadline
before missing target before revision, with retained completion once selected.
Service intent policy belongs to sys-init. Foundations O-01/O-04, I-03–06/E-01–08,
scoped ownership/error/unsafe review and existing Experience marker conventions
apply. No new unsafe primitive, dependency, shared ABI/pin or POSIX conformance.
Stop-error policy, partial cleanup failures, automatic timed retry and full control
integration remain BG-058/BG-040; unknown recovery remains BG-033.

Decision 0054 validation: 27 native cases pass with 177 inputs unchanged; 21 prior
binaries match and two changed Attempt clients pass their old oracles. Full checks:
228 model tests / 23 mutation controls, 48 host tests, 37 harness tests and all
eight gates pass. Catalog: 302 outcomes / 21 bundles / 5,970 listed files. Initial
compile failure retained separately. Evidence: `docs/evidence/native-attempt-intent-2026-09-06/`.
