# Repeated dash substitutions in one parent

Requirement: actual dash must execute two substitutions in one parent, retire the
first pipe only after EOF/close and acknowledged child terminal, then admit a
second child with fresh process, freeze-token and pipe generations. Command:
`a=$(echo pipe); b=$(echo pipe); echo "$a"; echo "$b"`. Both children exit0;
independent backend readback must be exactly `pipe\npipe\n` and stderr empty.
A second fresh shell/backend runs `echo clean` without any child; this checks fresh
stdio startup and actual backend storage reuse. Two parents, two backends and two
copied children produce the existing six actual reclaims without kernel changes,
quota increases or a dummy worker. The first parent stays generation1 while both
pipe and copied-child generations advance1→2; the second parent is generation2.

Keep existing single-substitution profiles unchanged. Extend the existing dash
owner with an opt-in two-cycle lifecycle rather than a second dispatcher. Count
child identity independently of parent identity. Reclaim each copied child only
after its real terminal and wait ACK. Retire and clear the pipe before the next
create, with no retained frames. Reuse only local FD slots3/4 whose previous live
references were closed. Canonical fork v2 and child readiness remain mandatory.
No live-pipe exec, generic fork server, serial input, new ABI, SDK or sibling change.

Forbidden: stale freeze token or pipe reference accepted after reuse; a child
reclaimed before ACK; synthetic child output; stale bytes crossing generations;
shared local bindings confused with backend holders; quota/pin/kernel changes.
Controls will replay freeze token1 on the second copy (reject before admission)
and send the old first-generation pipe reference on the second child receipt
(client rejects before readiness). Require exact fail-closed outcomes, not timeout
as a success. Unexpected failures remain contained fixture failures, not general
rollback/restart recovery. Actual empty no-child waits return ECHILD in shell2.

Affected owner: Aether private native producer; userland retains installed SDK and
independent acceptance. O-02–05, I-01/03–06, E-01–08 and local CE/TE/SE apply.
Reuse pinned dash parser/jobs, musl fork/wait3, pipe core, stream backend and private
handshake. No new dependency, unsafe block, allocation or authority boundary.
Buffers remain fixed stack-owned synchronous native-call borrows. Update native
reference/workflow, STATE/ROADMAP and retained evidence; preserve released pins.

Simpler alternative: two separate one-shot shells. It does not test reuse while
parent state survives. We choose the existing owner with explicit cycle counters
and conditional command strings. None of the old fault/stop/single-substitution
paths can be removed now; they retain distinct recovery/compatibility witnesses.
The fresh builtin-only shell verifies a real replacement lifetime while preserving
the existing kernel test's six-reclaim contract. Broader pipe/process services and
serial timing are deliberately outside this requirement.

Select focused positive plus two stale-generation controls before full 271-case
connections, five launch and two console regressions; host/build, scoped Rust/C
format, workflow and offline standards/simplicity integrity. Freeze sources during
qualified runs, retain every failed attempt and hash/archive before deleting any
unpacked temporary duplicate. Independent reader review remains open.
