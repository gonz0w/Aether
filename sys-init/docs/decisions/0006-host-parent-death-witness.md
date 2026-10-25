# 0006: Witness parent death without claiming containment

Accepted 2026-09-05 for BG-028/BG-054's trusted host experiment. Existing
[ownership research](../research/BOUNDARY-HANDOFF.md) distinguishes a persistent
parent from an independent waiter. Pinned Foundations O-04 and E-03–E-06 apply;
this changes no shared standard or runtime implementation.

Run a disposable supervisor that creates exactly one bounded foreground child
through HostRuntime. The outer test owns and waits for that supervisor. The
supervisor owns its child while alive; the outer test never claims it can reap
that grandchild after owner death and never signals a PID taken from a file.
All processes inherit the host harness process group and never detach.

Use an exclusive temporary directory and fixed JSON receipts plus request files.
Receipts are written by rename after their contents are complete. The child first
reports its PID and original parent PID. Only after the outer test kills and
waits for the supervisor does it publish a probe request. A subsequent child
receipt with a changed parent PID witnesses execution after original-parent
death. The child's finally-cleanup is not the supervisor's finally-cleanup.

The child is a trusted fixture with a ten-second total lifetime. A release file
requests cooperative exit; the outer test publishes it in its own finally block.
A final receipt means cooperative exit was reached, not that the new system
parent has reaped the process. The external reaping outcome remains unobserved.
Polling uses explicit predicates and finite deadlines, not sleeps that assume
which side wins a race. The harness retains its independent 30-second watchdog.

A normal-exit control asks the supervisor to leave its try block. Its finally
calls close and records the actual child wait result and empty owned inventory.
The abrupt case uses SIGKILL on the directly owned supervisor and verifies its
finally receipt is absent. Survival is the expected finding: a passing test
must not be reported as parent-death containment or supervisor recovery.

Private files are inspectable fixture synchronization, not a production IPC or
authenticated control protocol. The child voluntarily stops; hostile or detached
descendants remain outside scope. Report host/platform, positive and control
outcomes, and preserve source fingerprints. BG-028 retains helper-chain,
exclusive-wait and measurement work; BG-033 retains native recovery. Platform
specific containment requires a separate decision and enforcement witness.

## Recorded result

Both parent-lifetime cases pass on macOS: SIGKILL bypassed supervisor finally cleanup and a fresh child receipt reported execution under a changed parent; normal exit recorded child wait status and an empty owned inventory. [Witnesses](../evidence/host-parent-death-2026-09-05/witnesses.json) are also retained in the host stderr log. A forged unchanged-parent receipt fails one assertion: [negative report](../evidence/host-parent-death-2026-09-05/negative.json), [log](../evidence/host-parent-death-2026-09-05/negative.log).

The [combined run](../evidence/host-parent-death-2026-09-05/positive/results.json) passes all three standards checks, 34 model tests/three mutation controls, 32 host tests and 10 harness tests. Runtime implementation and shared pins are unchanged. The containment gap is now demonstrated on this host; its remediation remains open.
