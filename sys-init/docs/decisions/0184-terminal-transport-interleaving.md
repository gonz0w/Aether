# 0184: Test terminal observation versus transport closure

Date: 2026-10-04. BG-067; before-code experiment scope, not established cause.

The initial owned-session failure follows the final helper terminal record and
precedes parent output/completion. The retained normal owner polls terminal state
before channel read/write in separate syscalls. The sealed kernel read returns0
on a sealed empty stream; write returnsEPIPE32 after reader closure. A child can
finish between its earlier nonterminal observation and the next transport call.
The current owner rejects these results without another terminal observation.

Test the actual boundary using the previously qualified full numeric diagnostic
image. Insert one existing cooperative-yield call after the nonterminal check
for the final helper (peer1/generation5) before transport. Freeze source/tool and
kit hashes; preserve the kernel/client/firmware and unchanged baseline image.
No shared ABI, sibling edit, resource increase or maintained runtime change yet.
Success for diagnosis means a fresh target trace identifies the failure site and
actual final-helper terminal before failure; startup, timeout and other diagnostic
sites cannot count as this reproduction. Keep all attempts and code/stack limits.

Simpler alternative: more identical healthy reruns. They cannot select the narrow
interleaving or explain the retained failure. A single scoped private yield uses
an already defined kernel operation instead of a scheduler or tracing framework.
No active product complexity is added or removed in this experiment.

If reproduced, consider the smallest identity-preserving repair: treat only read
EOF/writeEPIPE as candidates for a fresh terminal observation, then use existing
confirmed-terminal/cleanup machinery. A still-running peer or unexpected result
must retain failure/ownership; no speculative retry or reply completion. Native
before/after and relevant live-close denial controls are required before changing
maintained code. Original fault has no retained caller, so do not claim exact
historical attribution from a matching controlled interleaving alone.

Foundations O-03/04, I-03–06, E-01–08 and the existing internal ASCII Experience
exception apply. Exact lifecycle/transport remains local; released pins and the
ABI22 recipe are preserved. No POSIX, exhaustive timing, release or general shell
recovery claim. Update existing coverage and run full checks for affected work.

## Reproduction and repair scope before maintained change

The yielded delayed image fails at its channel-read size check after final helper
slot2/generation5 terminal. A second image captures actual read result0, then the
same rejection path. These are real matching kernel/client witnesses, not a mocked
EOF. The first value-instrumented compilation rejected a Rust borrow conflict;
using the already-borrowed peer's epoch corrected it without altering ownership.

Repair only the demonstrated read EOF boundary. Reobserve the exact existing
peer handle through the established terminal operation. Require confirmed terminal
before proceeding; reclaim only if the child was already collected, otherwise
leave it for the normal wait/delivery/cleanup path. A running peer still fails;
other negative results retain existing rejection. No new state, retry, synthetic
status, resource release on EOF alone, or transport-result widening. WriteEPIPE
race handling remains unqualified/deferred until its own current requirement and
witness; this read repair does not claim general closure recovery.

Native checks: repaired maintained immediate/delayed workload; private repaired
yielded immediate/delayed; original failed yielded image retained. An actual wrong
read-endpoint direction must still reject with no halt. A private live-peer EOF
control can inject only the read result (labelled synthetic), requiring terminal
observation to reject; it is not a kernel EOF-production witness. Inspect code,
stack, raw/ELF equality and immutable builtin sites, update existing unsafe/source
records and provenance, run full repository checks. Original historical caller
remains unavailable: this establishes and repairs a compatible concrete race, not
proof that every earlier failure or possible terminal interleaving has this cause.

## Results

Two actual kernel-produced yielded EOF failures are retained. The small maintained
repair adds10 lines plus a fresh frame borrow, with no new state or unsafe site.
Current linked owner15120/16384 code,3816/4088 scoped stack; private yielded and
control images remain below16KiB and3912 stack. Four exact repaired workloads
(normal and yielded, immediate and35-second delayed) pass90-byte UART, eight
admissions, ten terminal/reclaims and owner-authorized halt. Actual wrong read
endpoint returnsEBADF9; synthetic0 before final child exec fails the required
terminal confirmation. Both preserve failed ownership/no successful halt. Ten
trace corruptions reject; all attempts and commands are retained in the
[terminal/read packet](../evidence/terminal-read-race-2026-10-04/README.md).

The first oracle required diagnostics to begin at a raw line boundary, but negative
controls emit them immediately after the existing prompt. Matching the fixed token
along with exact prior UART prefix/marker counts corrects this oracle assumption.
Initial oracle and Rust borrow failures are retained; no guest trace was edited.

These witnesses repair a concrete compatible failure mode. Historical exact caller
attribution and untested transport/termination interleavings remain limits, not
newly completed protocol coverage. Next maintained candidate recipe and remaining
composition qualification; no broad restart/recovery or writeEPIPE handling added.
