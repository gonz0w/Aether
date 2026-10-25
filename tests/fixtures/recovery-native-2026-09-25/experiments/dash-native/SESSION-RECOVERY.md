# UL-007 recovery after an early reader exits

2026-09-25. Consumer-owned next handoff after accepted SESSION-01–06. Execute the
entire [script](recovery/early-reader.sh) through actual dash main in one parent;
repeat it across three owner generations. Native execution is **NOT RUN**. This
is a new, smaller recovery composition, not a replacement for the accepted script.

Use the unchanged helper pinned in [manifest.json](recovery/manifest.json), with
WITNESS=value, LC_ALL=C and PATH=/nonexistent. Only /inputs/helper needs executable
lookup authority. No scratch filesystem, real-prefix installation or serial input.
The target dash must support pipefail as in the already qualified early-reader
component; this is an explicit dash feature requirement, not portable sh evidence.

## Positive contract

| ID | Required observation | Status |
| --- | --- | --- |
| RECOVERY-01 | Actual pump and one helpers run concurrently; one consumes exactly one byte and exits0; pump encounters native EPIPE, not a simulated status, and exits42; pipefail gives42 | NOT RUN |
| RECOVERY-02 | Both failed-pipeline children are waited/collected and their pipe references disposed before the next external command; no stale child result or retained writer | NOT RUN |
| RECOVERY-03 | The same live parent executes the argv/environment helper successfully after recovery, then a fresh three-stage pipeline transfers exactly ten bytes with all three statuses zero and real EOF | NOT RUN |
| RECOVERY-04 | Final helper finds fd3–63 closed; parent PID remains unchanged; exit0, exact49-byte stdout and20-byte stderr match the pinned files | NOT RUN |
| RECOVERY-05 | Every negative below rejects at its specified semantic boundary, with exact cleanup; timeout, generic crash or synthetic transcript cannot pass | NOT RUN |
| RECOVERY-06 | Repeat the entire workload in three parent generations with authenticated phase identities and complete worker/channel reclamation | NOT RUN |

The pump writes bounded 4096-byte chunks (at most4096 attempts) and ignores SIGPIPE
so the write error is observable. The one helper consumes without echoing its byte.
No pump data belongs in stdout. After checking42, the parent disables pipefail and
runs the healthy pipeline under ordinary dash behavior. The owner must additionally
require successful upstream statuses, not just the last pipeline command's status.

Expected logical work per parent: seven copied children (two recovery helpers,
one argv helper, one builtin writer plus two copy helpers, one final closure helper),
six helper exec replacements and one parent. Across three parents:21 copies,
18 helper execs and24 terminal/reclaim results, including three pump exits42.
If memory admission is recorded only for parents and helper exec replacement as in
SESSION, expect21 admissions. These are consumer expectations requiring producer
reconciliation before running, not an assigned slot map or an implemented ABI.
Specify exact slots/generations, per-phase waits and admission semantics separately.
Review fit against all current code, stack, memory, channel and lifetime bounds;
do not silently extend the fifteen-use profile or infer fit from total counts.

## Required negative controls

- Suppress EPIPE or falsify the pump result: the normal42 recovery predicate must
  fail (parent42 if the pipeline completes with a different status). A pump99 is
  not success; a hang must be bounded and rejected with confirmed cleanup.
- Retain a real reader reference after one exits: demonstrate the actual pending
  write/parent wait, then stop, observe, close and reclaim; never accept timeout.
- Skip collection or replay a stale recovered-child identity into the next phase:
  reject before that identity can satisfy a new child's wait or gain authority.
- Wrong WITNESS in the post-recovery argv helper: helper91 and parent43; no healthy
  pipeline or final success output. Recovery must already have completed.
- Corrupt the healthy pipeline's bytes while preserving normal lifecycle: the
  consumer's exact output checker rejects even if all statuses are zero.
- Leak unflagged fd3 into the final helper: helper95 and parent45; final success
  output absent, earlier recovery and healthy pipeline already completed.

Freeze each producer mutation, native error identity, permitted output prefix,
phase/count/terminal oracle and cleanup rule before consumer replay. Mutants are
separate isolated cases; never edit positive inputs to accommodate missing behavior.
POSIX PID selectors and output strings do not confer native authority.

## Delivery and review boundary

Supply a sealed complete source/support export, current host tests, tool/SDK pins,
exact compiler flags and target ABI, resource limits, linked owner stack audit,
raw separate streams, authenticated phase observations and all failed attempts.
Require matching affected producer regressions. Consumer replay uses the existing
owned runner: sequential suites,3600-second outer deadline,1800-second review ceiling,
512 MiB streams and unchanged guest watchdogs. Preserve completed evidence before
verified archive cleanup. Broad shared SDK/reader reviews remain separately open.

This handoff requests owner implementation/review; it does not authorize edits to
Aether from this project. Failed-exec recovery, scratch redirection and real serial
composition follow as explicit new workloads. Full UL-007/M3/R1 remains open.
