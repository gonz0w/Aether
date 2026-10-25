# Trusted host-child runtime experiment

Scope authorized 2026-09-05: standards plus cross-project runtime implementation.
This implements a bounded portion of BG-054 and BG-040 using Python host tooling;
production init language and native interface decisions remain open.

Run `python3 scripts/check-host-runtime.py` from this repository. Thirty-eight real
child and descriptor cases run under an independent 30-second watchdog. Run
`python3 scripts/check-runtime-model.py` for the existing deterministic suite and
mutation controls. Evidence is in `docs/evidence/host-runtime-2026-09-05/`.

## Implemented contract

`prototypes.host_runtime.descriptors.Prepared(paths)` reads up to eight inert
Distribution v0.1.0 service descriptors, validates the entire graph, records their
content pins and validates executable hashes. `activate(cwd=...)` rechecks those
pins and returns a runtime. Explicit `start(names)` launches foreground children;
preparation and activation alone launch nothing. Call `pump()` to observe events,
and `stop(names, shutdown=True)` with the entire inventory for ordered shutdown.
Use `try/finally: runtime.close()` to kill and reap owned children when the caller handles an exception.
The API is an experiment, not a stable operator CLI or installation hook.

This narrower target is `host-posix-experiment-v1`: model IDs are lowercase ASCII
letters/digits/underscore/hyphen, beginning with a letter, at most 32 characters;
eight services, sixteen edges, two retries, positive delay milliseconds. Startup,
stop and cleanup budgets are each 1000 ms for descriptors. Unsupported values
reject, including all authority requests. No string grants host privileges.
The model remains bounded to 256 observations per runtime, with 64 retained
records. The adapter retains at most 128 effect records. This is not a perpetual
system daemon. Host environment starts with PATH and LC_ALL plus explicit data;
stdin/stdout/stderr go to the null device. Executables use absolute paths,
structured argv, content checks and no shell interpolation.

For notified readiness, each launch receives a fresh inherited pipe write end in
`AETHER_READY_FD`. The child writes the six-byte first frame `READY\n`; the adapter
accepts that frame once and closes its read end. A malformed first frame or EOF
before completion terminates that child. No later frame is accepted. Generation,
terminal evidence and deadlines are checked by the model. This is launch-scoped descriptor possession: a helper inheriting the writer can also signal. It is not main-PID authentication, health or authenticated IPC across unrelated processes.

Stop/force are signal requests only. Actual wait status establishes termination;
reaping and closing the owned readiness descriptor establish this host profile's
cleanup. The stubborn-child test exposed a model bug: after force marked cleanup
unknown, fresh terminal evidence did not reopen pending reclamation. That is now
fixed. The earlier operation remains incomplete even after later verified cleanup.

## Evidence and limits

Cases cover one-shot exit/reaping, readiness dependencies and reverse stop order,
finite retries, fresh readiness channels after replacement, invalid readiness,
startup timeout, forced termination, executable pins, stale preparation, malformed
JSON and graph rejection, unsupported authority/targets, and literal shell-shaped
arguments. The original 34 model tests also pass, including permutation and
seeded traces. Timing is host test duration, not boot performance.

Children are trusted fixtures running with the invoking user's authority on a
POSIX host; only macOS has been tested. This is not a sandbox, PID 1, arbitrary
process-tree containment, service privilege separation, authenticated package
selection, durable enablement, crash recovery or native Aether supervision.
Executable hashes protect this trusted-workspace experiment against accidental
changes; they do not close hostile filesystem races or authenticate a script's
interpreter inputs. Do not run untrusted descriptors with this adapter.

Remaining BG-054 work includes Linux/BSD evidence and CI. BG-028/040 retain native
ownership and readiness mapping; BG-035–037 retain package publication, durable
selection and reconciliation. Existing backlog IDs and production decisions are
preserved. The shared Distribution release is unchanged.

Standards review: the [host evidence fix](STANDARDS-REVIEW.md) now measures discovery/execution counts and rejects empty, partial or skipped suites under Foundations E-06. Fourteen cases passed at that review; the count is no longer hard-coded.

## Readiness framing and ownership follow-up

[Decision 0003](decisions/0003-host-readiness-fixture.md) records the exact first-frame and direct-parent ownership contract. The reader consumes at most the remaining bytes of `READY\n`, accepts once and closes; trailing bytes are not another frame. Fragmentation cannot change acceptance. A mismatching partial prefix or EOF before completion requests termination immediately, while actual wait/reclaim still establishes cleanup.

The previous seven-byte read rejected a valid first frame when trailing data was coalesced into that read. Six new fixtures cover that regression, forced single-byte reads over a real pipe, partial-frame EOF, early prefix rejection, closure of an unrelated inheritable descriptor, and terminal observation before buffered readiness. **20 host cases pass on macOS**. Restoring the old parser in a disposable copy causes both framing regressions to fail, as expected. [Readiness follow-up source hashes/results](evidence/host-readiness-2026-09-05/results.json), [negative control](evidence/host-readiness-2026-09-05/negative.json) and [assertion log](evidence/host-readiness-2026-09-05/negative.log) are retained.

The fragmentation fixture constrains actual read sizes; the known-exit fixture waits for the owned child's exit before polling, so neither depends on a sleep guessing the race winner. Existing pipe generation/retry and ordered stop/reap checks remain in the suite. Parent death, escaping descendants, native grant transfer and Linux/BSD/illumos execution remain outside demonstrated coverage. BG-040/BG-028/BG-054 remain partial; no shared standard or pin changed.

The [combined development runner](DEVELOPMENT-CHECKS.md) executes this harness with pinned standards, model and harness-evidence checks. Its platform table distinguishes the tested macOS host from pending cross-host coverage.

## Request clock follow-up — 2026-09-05

[Decision 0004](decisions/0004-host-request-clock.md) fixes stale deadlines after idle periods. Each start/stop first performs one bounded observation cut that synchronizes model time. Independent lifecycle progress therefore precedes request validation, including rejected requests. New budgets start at that cut; joining a pending request preserves its original deadlines. Four controlled-clock tests with real children bring the host suite to **24 passing cases**. Removing the fix produces four expected assertion failures. [Combined evidence](evidence/host-deadlines-2026-09-05/positive/results.json) and the decision record distinguish controlled-time tests from actual host timing guarantees.

## Emergency cleanup follow-up — 2026-09-05

[Decision 0005](decisions/0005-host-emergency-close.md) makes `close()` permanently close admission before cleanup. `start`, `stop`, `pump` and late adapter observations reject afterward; repeated `close()` retries retained failures. Other tracked children still receive cleanup after one failure. The model remains a diagnostic snapshot, not an orderly-stop success record. Six new tests bring host coverage to **30 passing cases**; exception/finally cleanup, descriptor closure, retryable injected failures and an unrelated child are covered. [Combined evidence](evidence/host-cleanup-2026-09-05/positive/results.json) and a guard-removal negative control are retained. Abrupt supervisor death remains untested and unsupported as a containment claim.

## Parent-death witness — 2026-09-05

[Decision 0006](decisions/0006-host-parent-death-witness.md) adds a bounded abrupt-owner-death experiment and normal-exit control. On macOS, the child survives its original supervisor's SIGKILL and responds to a later probe under a changed parent. Normal supervisor exit runs finally cleanup and waits for its child. The abrupt case requests cooperative child exit through a private fixture file; external reaping remains unobserved. These are **32 passing host cases**, including a test that demonstrates missing containment. [Witnesses](evidence/host-parent-death-2026-09-05/witnesses.json) and [combined results](evidence/host-parent-death-2026-09-05/positive/results.json) are retained. Production parent-death containment and native recovery remain open; no runtime or shared-standard change was made.

## Terminal accounting and exec-failure follow-up — 2026-09-05

Three new test methods bring host coverage to **35 passing cases**. Eight already-terminal children cross multiple four-observation cuts with exact launch/terminal/cleanup accounting, including signal versus normal exit. Real malformed-image/missing-interpreter failures close all recorded pipes and block dependents. Changed executable bytes reject before spawning. [Evidence and two negative controls](evidence/host-accounting-2026-09-05/README.md) distinguish bounded polling from signal-handler testing. No runtime behavior or shared pin changed.

## Exclusive-wait and helper follow-up — 2026-09-05

[Decision 0007](decisions/0007-host-exclusive-wait.md) fixes false exit-zero synthesis after another waiter consumes a child status. The adapter now checks uncached status with waitpid; observed wait loss produces unknown/incomplete, closes readiness, and prohibits signalling or successful reclamation of the lost identity. Closure retains that unresolved object and reports failure. This remains a trusted single-threaded/exclusive-wait contract, not protection against concurrent handlers or forged cached statuses.

Three new tests bring host coverage to **38 passing cases**, including independent-helper wait rejection and deliberately delegated helper readiness with parent-owned helper reaping. [Combined evidence](evidence/host-wait-ownership-2026-09-05/positive/results.json) and a fallback-restoration negative control are retained. Native recovery, cross-host coverage and parent-death containment remain open.

## Exploratory measurements — 2026-09-05

[Host measurement baseline](HOST-MEASUREMENTS.md) records two warmups and ten measured repetitions each for one and eight children, with raw samples, readiness/cleanup witnesses, CPU, traced manager allocations and process inventory. A deliberately silent worker is censored by the outer watchdog. No timing budget, native performance or total-RSS claim is introduced.

## Readiness acceptance checkpoint

[Host readiness acceptance](HOST-READINESS-ACCEPTANCE.md) retains `READY\n` and
adds real-pipe/child coverage for early registration, exact deadlines, post-stop
notification and old-writer/replacement isolation. All 42 host tests pass; an
isolated exact-deadline policy mutation fails the intended subcase. No runtime or
model behavior changed. Remaining helper/flood/cross-host limits are explicit.

[Writer acceptance](HOST-READINESS-ACCEPTANCE.md#writer-follow-through) now covers
repeat-write EPIPE, bounded junk pressure and a real helper notification after
main exit. The three tests pass, bringing the host suite to 45. Known terminal
state still wins; an isolated contrary mutation fails. Orphan-helper reaping is
unobserved, and no descendant containment is claimed.

## Readiness diagnostics and Linux validation

Decision 0015 adds `ReadinessDiagnostic(code, service, generation, received_bytes)`
to a separate `diagnostics` deque retaining at most 128 recent observations. The
existing `('invalid-ready', name, generation)` log event remains unchanged.

| Code | Observation |
| --- | --- |
| `SYSINIT-READY-CLOSED` | EOF with zero frame bytes |
| `SYSINIT-READY-INCOMPLETE` | EOF during a valid partial prefix |
| `SYSINIT-READY-MALFORMED` | Prefix mismatch |

The byte count is bounded by six; raw payload, descriptor and capability values
are absent. These are internal records, not an operator CLI/schema. A record
means rejection and a termination request, not observed terminal state or reclaim.
Valid first-frame/trailing-byte behavior and dependency admission remain unchanged.

[Cross-host evidence](evidence/host-diagnostics-linux-2026-09-05/README.md) now
passes all 48 host tests on macOS arm64 and Linux aarch64 (Python 3.13.12, Podman
container), with identical recorded source hashes. Model/harness/native-audit and
standards checks pass on both. This supersedes earlier Linux-not-run statements
for these exact inputs only. [Remaining integration gates](INTEGRATION-GATES.md)
require actual BSD/illumos execution and accepted broader native contracts.

The canonical [source-checkout manual](man/sys-init-check-host.1) documents the
current invocation, streams, failure paths and artifact lifetime. See
[documentation coverage](DOCUMENTATION-INVENTORY.md) for review status.

The [host descriptor reference](HOST-DESCRIPTORS.md) now records the full local
field schema and parse/prepare/activate/start ownership boundary. Decision 0106
adds six contract tests and a runnable temporary oneshot example without changing
runtime implementation. Historical case counts above remain snapshot counts.

Decision 0109 bounds inner host/model worker capture to 4 MiB of combined raw
stdout/stderr and 30 seconds through pipe drain/exit. Host capture failures
replay diagnostic stderr only; model failures keep passed/error fields and
include bounded prefixes in error detail. Capture exceptions clean the owned
group and reap the direct child; abrupt outer termination and detached groups
remain separate gaps. The helper is included in successful source hash maps.
See decision 0109 and the updated host/model command manuals.
