# Local test plan and extended coverage

For pkg-mgr contributors. Plan revision 1, 2026-09-07 UTC. This is local process
for the experimental host prototype. Aether remains the release target; host
checks are development evidence. Candidate standards and release pins are unchanged.

## Required selection

Run from the checkout. The pkg-mgr maintainer owns test selection and triage.
The [inventory](development-inventory.json) maps sixty-eight critical case groups to
stable IDs, requirements, owner, family, stage, layer, test location, oracle,
forbidden effects and limitations. The gate rejects missing/duplicate IDs, absent
requirements/oracles, invalid scope and missing/ambiguous test anchors. Finding an
anchor never marks a case executed. Existing subsystem rows retain broader scope.

| Change | Required selection | Deadline and boundary |
| --- | --- | --- |
| Documentation/process | `python3 tests/check-development.py`; `sh tests/check-standards.sh` | 60 seconds each; syntax, references, case locations and pins |
| Shell/parser/transaction/development gate | `sh tests/check.sh`; changed-shell lint from DEVELOPMENT | 600-second process-group watchdog; all selected cases and cleanup must pass |
| Manual content | `python3 tests/check-manuals.py --render-required` | 60-second child deadlines; all three manuals, examples, host rendering/lookup |
| Compiler/manual release example | `python3 tests/check-manuals.py --render-required --binary-example` and affected recipe integration | 600-second operational budget; pinned local prerequisites, no download |
| Native interface | Exact owning transport invocation and matching producer/consumer inputs | Declare total budget and semantic negatives before execution; host tests cannot substitute |

Tools and versions are in [DEVELOPMENT](DEVELOPMENT.md). Missing required tools or
runners are blocked coverage. Generic failure or timeout cannot satisfy a semantic
negative oracle. No new target command or advertised platform is introduced.

## Extended schedule: defined, not deployed

No CI/scheduler is installed for this plan. Record due but unexecuted runs as
not-run and keep TD-04 implementation open. Use the existing owned suite runner;
do not invoke unguarded check-fixtures.sh as the extended runner.

| Planned cadence | Workload | Budget and observations |
| --- | --- | --- |
| Daily during active development | One `sh tests/check.sh`, including source corpus seed 20260906 and transaction fault cases | 600 seconds; counts, semantic outcomes, elapsed time, cleanup and every failed attempt |
| Weekly and before candidates | Five sequential full-suite runs in distinct runner roots | 600 seconds each, 3000 seconds total; any failure stops qualification; retain every result |
| Before native candidates | Owning native fault/concurrency and assembled-workflow plan | Not provisioned; target workload, resource bounds and owner agreement required first |

The daily corpus is fixed regression exploration, not fresh fuzzing. Five host
repeats are repeated-lifecycle checks, not sustained native soak or performance
evidence. Fresh seeds/minimization, synchronized concurrency, resource accounting
and native soak drivers remain missing work. Never kill by process name or fill
a host disk to simulate failure.

## Freshness, metrics and retention

For this local plan, host evidence supporting a candidate must be at most seven
days old at review. Any relevant source, fixture, tool, configuration, plan or
candidate change invalidates affected evidence immediately. Recheck exact final
inputs. The assembled-release owner must separately approve its target plan and
freshness requirements; seven days is a local workflow default, not a safety guarantee.

Retain UTC times, command, HEAD plus dirty input hashes, tools/platform, seed,
expected/observed results, raw stdout/stderr, watchdog result and retained root for
every attempt. Distinguish pass, fail, not-run, timeout, infrastructure failure and
unknown. Keep initial failures when a corrected rerun passes. Failed cleanup,
authority bypass, unexpected data loss and input/evidence mismatch cannot be waived.

The maintainer's weekly review records attempted/passed/failed/not-run counts,
durations, flaky cases, escaped defects, uncovered requirements and resource
regressions. Link defects to original failing inputs and regression cases. No
metrics collector or weekly review has run merely because this process is defined.
Retain evidence while its experimental claim is active. Public releases still need
a support/security retention period; no automatic deletion policy is introduced.

ADP04-03 now has explicit schedule/workload/seed/budget/owner/freshness definitions.
Provisioning and actual extended coverage remain open. ADP04-02 gains enforced
critical-case locations, not complete case coverage: CLI signals/output and bounded native preflight/oracle
groups are mapped, while wider native, concurrency and full format mappings remain. No full draft conformance is claimed.


## One-time campaign qualification — 2026-09-07 UTC

[The five-full-suite campaign](evidence/full-campaign-2026-09-07/README.md) passed all
five sequential runs in distinct private roots. Each kept the existing 600-second
watchdog; the campaign completed in about 18 minutes within its 3000-second budget.
All input hashes/modes stayed stable. No failure was retried away. This establishes
one manually initiated host execution of the planned workload, not deployed cadence,
new fuzz exploration, native soak, or actual human review. Existing scope and evidence-
age rules are unchanged. The campaign's original exact plan bytes are hash-bound;
this appended result does not change the workload or its acceptance oracle.

## Runner deployment handoff

[The operator handoff](RUNNER-HANDOFF.md) defines the private source artifact, host
prerequisites, qualification commands, status propagation and retained evidence.
It prepares this plan for a supplied runner; it does not install a schedule or
qualify another host. VM/Forgejo details and actual operator execution remain open.
