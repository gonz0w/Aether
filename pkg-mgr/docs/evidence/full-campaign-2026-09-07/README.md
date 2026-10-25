# Five-full-suite campaign — 2026-09-07 UTC

One explicitly initiated execution of the weekly/candidate workload in TEST-PLAN.
This is host qualification, not scheduled deployment, fresh fuzzing, native soak,
performance qualification, or acceptance of a production release.

## Selection and oracle

Run `sh tests/check.sh` five times sequentially. Each invocation creates a distinct
owned root and uses its existing 600-second process-group watchdog. The campaign
has a 3000-second total budget, stops on the first failed/incomplete/drifted result,
and retains every attempt rather than retrying failures away.

Each run must return zero, write a passing watchdog receipt, retain a distinct root,
and include the exact sixteen-fixture, pinned-standards, critical-case-location and
coverage-control completion markers exactly once. The fixture assertions own the
individual semantic oracles; generic failure cannot substitute for a negative case.
The normal suite includes fixed parser corpora, the three existing Origins suites,
manual checks, CLI signals/output and interrupted package transaction recovery.
Opt-in native QEMU and compiler examples remain outside this selected normal suite.

## Identity and retention

inputs.json captures the starting HEAD, dirty status, platform, Python identity and
exact hashes/modes for existing tracked and untracked inputs. Existing Origins edits
remain part of the tested working tree but are not included in this evidence commit.
Only this new evidence directory is excluded from its input snapshot. Every round
checks the original input set before and after execution; changed bytes or modes
stop qualification. This is an observation boundary, not a filesystem lock or proof
against transient concurrent writes. Do not reuse these results for different inputs.

results.json records each exact command, UTC times, elapsed duration, exit, watchdog
receipt, retained root, drift result and log digest. run-N.log and run-N.result.txt
preserve the complete outputs and watchdog receipts. driver.py.txt is the actual
one-off orchestration procedure; it does not install a scheduled service or replace
the existing runner. summary.json records the actual campaign outcome.

The watchdog checks owned process-group teardown. It is not confinement against a
child deliberately escaping its group. Intentional SIGKILL messages occur inside
recovery fault cases and are not hidden test failures. No installed payload deletion,
live-prefix writes, native storage guarantees or shared release pin changes occur.

## Remaining boundaries

One campaign does not establish a reliable recurring schedule, a measured native
resource budget or long-duration soak coverage. The fixed seed is not new fuzz
exploration. TD-04 deployment, complete format/concurrency mappings, Python minimum-
version execution, target qualification, security triage assignment and actual human
reviews remain open. Source/authenticity and successful source/build execution are
separate trust decisions. The elapsed samples are operational observations only.
