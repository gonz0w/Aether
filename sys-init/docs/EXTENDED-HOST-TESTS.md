# Extended trusted-host test plan

Plan EHT-01 / decision 0146, BG-054 with BG-056. **Implemented locally by decision 0147; not scheduled.** The [corpus manifest](extended-host-plan.json) pins 54 existing host
test IDs, their source/runtime inputs and eight seeds. The ordinary host gate
already exercises this corpus once; this plan adds repeat/order qualification.
It does not add a production supervisor, new native feature or platform claim.

## Workload and reproducibility

Run eight sequential fresh workers, one per fixed seed. Every worker executes all
54 cases exactly once: 432 planned executions. Reject missing/extra/duplicate IDs,
import/discovery errors, skips, zero cases and incomplete execution. A failing case
fails that seed and the campaign; stop before launching another worker. Record
unattempted seeds. Do not rerun automatically or accept a majority of passes.

Use standard-library unittest and the existing trusted-child fixtures. Keep each
class contiguous; its setUpClass/tearDownClass lifecycle must not be scattered.
Order class identifiers by `(rank, class_id)`, then methods within each class by
`(rank, test_id)`. Rank is SHA-256 of UTF-8 text
`sys-init-eht-order-v1\n<seed>\n<class-or-test>\n<identifier>`; seed is the exact
64-character lowercase hex string in the manifest. No time-derived seed, runtime
random module or host path enters ordering. Save the complete ordered ID list.
Seed order is manifest order. A replay uses the same manifest, source hashes,
worker command, Python/tool identity and recorded ID order on the named platform.

Pin the implementation runner/helper separately when implemented. Before every
worker and after the campaign, verify the corpus/runtime sources against the plan.
A new test or source change requires a reviewed plan revision and new evidence;
never edit an accepted evidence bundle. This plan's source hashes do not claim
closure over the Python standard library, host kernel or compiler runtime.

## Budgets and ownership

| Resource | Planned limit |
| --- | --- |
| Workers | Eight, sequential, one fresh process each |
| Worker duration | 60 seconds including output drain and direct-child wait |
| Whole campaign | 600 seconds; check remaining budget before launch and during capture |
| Output | 4 MiB combined stdout/stderr per worker, separate retained raw prefixes; at most 32 MiB worker logs |
| Cleanup | One second for cooperative interruption, then force termination of the owned worker process group and reap the direct child |
| Output location | Newly created private directory under an explicit local output root |
| Concurrency | One campaign; no parallel workers or concurrent source edits |

The supervisor must own capture, cleanup and report publication. A timeout,
overflow, interruption, failed cleanup or invalid worker evidence is distinct from
a semantic test failure. An abrupt kill of the supervisor and escaped/deep child
groups are not magically contained; name actual cleanup evidence and limitations.
No host service installation, detached jobs, network downloads or native execution.
Byte/deadline budgets do not establish all filesystem syscalls are interruptible.

## Results, retention and triage

The planned campaign report should contain schema/profile/plan hash, platform and
Python identity, worker/runner source hashes, start/end timing, resource limits,
ordered seeds and per-seed commands/IDs/discovered/executed/skipped counts, outcome,
exit status, cleanup outcome and log paths/hashes. Record running and final states
with atomic replacement. Publish failure/interruption and unattempted seeds; do
not emit a success summary until final evidence is saved. Use the established
0 success, 1 failure, 64 invalid usage and 130 interruption contracts.

A worker must independently report the IDs it actually ran and outcome counts;
the parent compares these with its expected order and source identities. Exit zero
alone is insufficient. Fault controls must prove detection of missing/extra/skipped
cases, wrong order/seed/source, timeout, output overflow, failed publication and
interruption/cleanup. A successful empty or truncated worker report is forbidden.
Use controlled stubs for runner failure paths; distinguish them from the real
54-case corpus run. Do not add timing thresholds as performance regressions.

Retain every attempted seed's raw logs and campaign report, including failures.
Retain the first failure before triage. The sys-init maintainer owns investigation:
replay the exact failing seed/order first, compare source/environment/cleanup,
record any retry as a new attempt, then link a reduced regression and disposition.
Do not silently discard flaky failures or rewrite the failing record. Working
runs may stay under out/; accepted qualification copies get a new sealed docs/
evidence bundle. Cleanup of accepted evidence requires a separate retention policy.

## Invocation, freshness and qualification

Run `python3 scripts/check-extended-host.py` locally. Use `--plan` and
`--output-root` for explicit paths, and `--seed <recorded-seed>` for a one-seed
replay. See [the command manual](man/sys-init-check-extended-host.1).
The manifest retains its planning-origin status; campaign reports establish
execution status. Decision 0147 implements identity checks and failure controls. Keep the extended campaign outside the normal ten-gate
command until its measured cost and acceptance policy are reviewed.

After implementation, run on relevant host/runtime/fixture changes and before
claiming extended qualification. For active local development acceptance require
matching source/plan hashes, the same platform/tool profile and a run no older than
seven days; any relevant change invalidates that reuse immediately. This is a
local development freshness rule, not an assembled-release age policy. Release
owners must set their own supported targets, cadence and evidence-age limits.
No cron, hosted CI, notification or background monitor is configured by this plan.

Initial execution target is the available macOS arm64 development host. Linux,
BSD and illumos need matching environments and their own retained attempts. The
older Linux witness remains valid only for its frozen snapshot. SMP, physical
hardware, PID 1 behavior and Aether VM qualification remain separate. Actual
independent technical/reader review and release ownership are still required.


## First implementation witness

Decision 0147 executes eight real workers locally: all 432 case executions pass
without skips. This witnesses host repetition/order variation on the recorded
macOS/Python profile. The campaign stays outside the ten-gate command and no
scheduler is configured. Exact logs, hashes, timings and controls are retained in
[evidence](evidence/extended-host-runner-2026-09-07/README.md).

## Replay and platform handoff

Decision 0148 verifies the first seed through the real replay CLI against the
retained campaign order and identities. This is 54 replay executions, separate
from full campaign qualification. Linux refresh is blocked: the existing Podman
VM stopped after reporting startup success, before image inspection or tests.
A working environment and independent review remain required. See
[evidence](evidence/extended-host-replay-2026-09-07/README.md).

## Linux EHT-01 witness

Decision 0149 completes all eight seeds (432 executions, no skips) in the pinned
Linux arm64 container. Plan, corpus, implementation and complete ordered worker
records match the macOS campaign. Keeping startup and execution in one session
restored connectivity; the prior failed attempts remain retained. This is EHT-01
coverage, not a refresh of all ten Linux development gates. No BSD/illumos, PID 1,
native or production claim follows. [Evidence](evidence/extended-host-linux-2026-09-07/README.md)
retains image identity, container constraints, raw logs and checks.
