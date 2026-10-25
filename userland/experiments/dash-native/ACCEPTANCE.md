# Current dash workload acceptance

As of 2026-09-24 UTC, **12 of 12 unchanged scripts have bounded local native evidence**.
These results span separately pinned private fixtures. They do not establish a
single assembled twelve-script pass, public SDK support or M3 completion.

[Verified index](../../docs/evidence/dash-parent-consumer-2026-09-24/verified-index.json)
binds the script contracts and local evidence seals. The original
[workloads.json](workloads.json) remains unchanged because it is a pinned historical
input; its NOT RUN fields describe the original proposal, not current acceptance.

| Workload | Local native status | Evidence or next requirement |
| --- | --- | --- |
| DASH-argv | Qualified, matched phase one | [718-case replay](../../docs/evidence/dash-phase-one-consumer-2026-09-14/README.md) |
| DASH-signal-table | Qualified, matched phase one | Same replay; bounded self-USR1 and real substitution pipe |
| DASH-syntax-error | Qualified, matched phase one | Same replay; exit2 and exact rejection controls |
| DASH-wait | Qualified, matched recovery fixture | [747-case matched replay](../../docs/evidence/dash-recovery-consumer-2026-09-14/README.md);15 wait/recovery transcript checks |
| DASH-fd-closure | Qualified, focused and matched fixtures | [3 focused cases](../../docs/evidence/dash-closure-consumer-2026-09-14/README.md) plus the newer matched316 connections; separate from writable leak control |
| DASH-failed-exec | Qualified, matched failed-exec fixture | [759-case replay](../../docs/evidence/dash-failed-exec-consumer-2026-09-15/README.md); two fresh VM positives and five controls |
| DASH-fd-leak-control | Qualified, focused and full connections | [358-case matched replay](../../docs/evidence/dash-substitution-regression-2026-09-23/README.md); real FD9, helper95/parent22, empty stdout |
| DASH-redirection | Qualified, focused and full connections | Same matched replay; shared-offset writes and reopened helper readback exactly AB |
| DASH-denied-redirection | Qualified, focused and full connections | Same matched replay; authenticated EACCES, real subshell2, parent0 and exact output |
| DASH-pipeline | Qualified, parent-driven fixture and matched suites | [890-case replay](../../docs/evidence/dash-parent-consumer-2026-09-24/README.md); actual dash jobs, two helper copy stages, exact output and15 reclaims |
| DASH-substitution | Qualified, focused and full connections | Same358-case replay plus [3 focused cases](../../docs/evidence/dash-substitution-consumer-2026-09-23/README.md); exact arguments/pipe bytes/EOF, output and lifecycle |
| DASH-early-reader | Qualified, parent-driven fixture and matched suites | Same replay; one byte, real EPIPE/pump42/pipefail, two child collections, exact output and15 reclaims |

Startup/custom-handler/mask evidence is included in phase one but is not a
thirteenth script. Native descriptor redirection, fixed /next substitution and
producer milestones must not silently replace an unchanged workload's oracle.

The final parent-driven fixture now passes101 capacity,358 connections and431
command-runner cases locally (890 total), with287 matching runtime-source hashes
and21 independent lifecycle checks. Both remaining scripts are qualified; matching
command-runner replay is no longer pending for this fixture. One host-support
mismatch and one collector admission-count error were corrected and retained;
all native suites passed first execution.

All12 scripts have bounded evidence across private profiles, not one assembled
interactive shell. Next compose parent pipelines with serial exec/substitution
and the native runtime in one session. General signals/TTY, persistent filesystem,
package/sys-init assembly and independent SDK/reviews remain open. Full UL-007/M3
and R1 are not complete. [Scratch requirements](SCRATCH.md) preserve earlier limits.


## Serial integration checkpoint — 2026-09-24

[First serial pipeline consumer qualification](../../docs/evidence/dash-serial-pipeline-consumer-2026-09-24/README.md)
passes898 native cases plus29 lifecycle checks on287 matching runtime inputs.
Actual dash accepts a pipeline then a builtin/exit follow-up at six prompts across
three generations, with15 terminal results/reclaims. The twelve-script matrix
remains12/12; this is an additional bounded serial witness. SESSION-01–06 remains
NOT RUN and the newer shell-streams delivery is not covered by this evidence.


## Serial forwarding checkpoint — 2026-09-24

[Forwarding consumer qualification](../../docs/evidence/shell-streams-consumer-2026-09-24/README.md)
passes105 native cases,110 host tests and11 independent controls. Long combined
UART output and nine prompt-driven commands per three-generation run pass; native
corruption reclaims normally and the host rejects the exact output mismatch.
Earlier898 regression is prior qualification. Matrix remains12/12; SESSION-01–06
is NOT RUN. Fixed job topology, separate-stream acceptance and full M3 remain open.


## Composed SESSION checkpoint — 2026-09-25

[SESSION-01–06](SESSION-ACCEPTANCE.md) now passes independently for the unchanged
private007/ABI21 scripted workload: three parent lifetimes, exact separate streams,
27 copies,21 helper execs,24 admissions and30 terminal results/reclaims. All910
matching native cases and115 Python/required Zig/Rust host checks pass. The original
proposal remains pinned unchanged; its NOT RUN fields are historical. The12-script
component matrix stays12/12. Next compose recovery, scratch and real serial input;
shared SDK/reviews, TTY, persistence and full M3/R1 remain open.
