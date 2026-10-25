# 0046 — Qualified native terminal event mapping

Accepted 2026-09-06 for the BG-058 model experiment.

## Requirement and decision

Decision 0045 preserves native normal, fault and stopped kinds. The lifecycle
model previously had only exit/fault observations: mapping native stopped to
normal exit 143 loses cause identity. Extend the local model with `stopped`, an
observed terminal event carrying an unsigned eight-bit adapter detail. It is not
a POSIX signal or wait status. Keep the existing five-field event format.

Process stopped at terminal priority, before launched/readiness, and only for the
current owned generation/epoch. Preserve terminal detail. Use ordinary bounded
failure/retry policy when still desired; cancelled intent disables retry. Stopped
never completes a one-shot successfully, invents readiness, releases ownership,
or proves cleanup. Startup-timeout remains the policy reason if already selected.
Terminal kind remains stopped in the ordinary case; this does not add a new
raw-native-kind field to Model status during timeout handling.

Add TargetRegistry.terminal_event(reply, owner=...) as a pure projection through
its existing status qualifier. Running returns None; normal maps to exit, fault
to fault and stopped to stopped, with the bound model generation and epoch.
No method accepts an unqualified detached fact as authority. Callers explicitly
submit the returned event through JournalRuntime.batch or QueuedRuntime.batch;
those retain their admission/backpressure rules. Repeated or delayed projection
is not exactly-once delivery. The model ignores stale/repeated terminal evidence.
The registry's native fault fact preserves detail; the legacy fault event policy
continues to discard its detail in Model state. Only the selected #UD native
fault projection remains supported.

## Cleanup and failed launch boundary

A terminal event requests reclaim; it does not acknowledge that effect. Native
reclaim success covers native target resources only (0042/0045), so do not yet
translate it automatically to model cleaned, which covers all owned generation
resources. A consuming driver must account for its channels, waits and helpers.
Likewise a confirmed pre-admission launch rejection cannot be followed by native
reclaim of its predicted handle: the target never existed. The existing generic
launch_failed event requests reclaim and therefore is not a complete native
rejection adapter. BG-058 next needs explicit driver resource accounting and a
no-target cleanup path. Unknown launch results remain reserved, with no inferred
cleanup or retry; BG-033 retains reconciliation.

## Alternatives, bounds and validation

Reusing exit 143 was rejected because normal return 143 and supervisor stop are
different facts. Automatically clearing ownership on stopped or launch rejection
was rejected because supervisor-owned resources may remain. This change adds no
queue, allocation policy, native ABI, dependency or actual native invocation.
Existing bounds (four events per cut, eight services, finite retries) remain.
Standard-library Python retains the portable model layer; native selection is
explicitly ABI-6, not a claim about POSIX/BSD/illumos/Linux process mechanisms.

Apply Foundations O-01/O-04, I-03–06 and E-04–08. Shared pins stay unchanged.
Test kind identity, terminal/readiness ordering, cleanup-before-retry, cancelled
intent, stale evidence and validation before mutation. Add a stopped-kind omission
control. Run the model runner and all development checks; retain sources, commands
and logs. Fresh native consumption remains required before a target claim.

Decision 0046 validation: 197 model tests / 19 distinct mutation controls,
48 host tests, 37 harness tests and all eight offline gates pass. Evidence:
`docs/evidence/terminal-mapping-2026-09-06/`. No fresh native execution.
