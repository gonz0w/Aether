# Tagged descriptor fork staging: owner transaction review

2026-10-22 / BG-067 / OQ-025. Source review and proposal, not an accepted wire,
implemented native transaction or independent replay of userland's link attempt.
[Exact input audit](../evidence/tagged-fork-stage-review-2026-10-22/README.md)
verifies18 userland source deliveries/570 members and unchanged linked ABI29 v2
580-member closure. No sibling or retained runtime bytes changed.

The new [libc contract](../evidence/tagged-fork-stage-review-2026-10-22/libc-contract.txt)
reports all application/startup/FD/wait/exit imports resolve except
`__aether_fork_stage` from `_Fork.c`. The source call is confirmed in the
[sealed fork wrapper](../evidence/tagged-fork-stage-review-2026-10-22/old-fork.txt).
The missing symbol alone neither proves a kernel primitive is missing nor permits
reusing the old descriptor stage. Libc/startup helpers now exist; prior general
requests for their existence are superseded by this concrete transaction gap.

## Available pieces and exact limits

| Piece | Available behavior | Missing composition |
| --- | --- | --- |
| `_Fork` | Blocks all signals, takes abort lock, calls stage, repairs child TID/list, restores signals | New stage and correct copied context/TLS rebind |
| Kernel freeze/copy | Caller0x23003 parks; owner0x23004 observes exact freeze token; owner0x23006 copies owned backing to fresh child with fresh channels | Tagged descriptor ownership, service views, startup/readiness/shutdown policy |
| ProcessFiles | `inherited_child` shares descriptions/offsets with separate process flags, after actual copy/admission; no extra AF07 lookup | Authentication, freeze/serialization proof and matching child source/channel readiness |
| Pipe owner | Existing staged holder reservation and readiness/known-copy-refusal completion; ambiguous copy is not failure | New tagged map validation, exact generation/holder correspondence and actual owner integration |
| Startup0200 | Checked304-byte envelope with exact seven-domain identity, tagged128 map, source records/history | Child copied-context transition and sole consumer selected in linked runtime |
| Context/libc | One stable4952-byte boot object, guarded operations, inert snapshot, wrappers | Safe child rebind; no generic reset/copy of an admitted context |

Sources: [kernel freeze/copy excerpt](../evidence/tagged-fork-stage-review-2026-10-22/kernel-copy.txt),
[process view](../evidence/tagged-fork-stage-review-2026-10-22/process-view.txt),
[pipe owner](../evidence/tagged-fork-stage-review-2026-10-22/old-pipe.txt),
[old staging](../evidence/tagged-fork-stage-review-2026-10-22/old-stage.txt) and
[TLS/auxv rebind](../evidence/tagged-fork-stage-review-2026-10-22/old-rebind.txt).
Old owner algorithms are precedents, not the selected seven-domain dispatcher.
Do not copy their old six-domain PID arithmetic or64-byte descriptor encoding.

## Ordering conflict requiring an owner decision

The current pinned `ProcessFiles::inherited_child` explicitly requires the caller
to freeze the parent between native copy and local binding copy. The reviewed
kernel `copyOperation` succeeds by publishing the child, clearing `source.frozen`,
and installing the child's PID in the parent result before returning to scheduling.
Thus a direct call to `inherited_child` after native copy does not by itself meet
that literal precondition. `_Fork`'s signal mask does not prove that remote broker
views cannot change. This is a contract/composition mismatch, not a demonstrated
kernel bug, exploit or requirement for a new kernel operation.

A possible resolution is one serialized owner transaction: snapshot while the
parent is parked, exclude parent/child broker and stream admissions through copy
and view installation, never reread parent mutable memory after copy, and admit
queued requests only after local binding publication. This could preserve service
view consistency even if the kernel resumes the parent. That is a proposed proof
obligation, not an exception to the current library's freeze precondition. It
needs affected-owner agreement, a newly versioned library/contract if relaxed,
and tests that schedule resumed-parent requests at the boundary. Alternative:
explicitly retain native quiescence through service publication if the kernel
owner selects and supplies such a contract. Do not silently choose either option.

## Minimal transaction requirements to agree

1. Authenticate the shell instance/channel and current generation. Take a full
  128-byte tagged snapshot under the public fork/context guard before native
  parking; preserve cloexec flags on fork (omit-cloexec projection is for inert
  exec preparation, not fork inheritance). Version/length must distinguish the
  old opcode83/length64 path. No new opcode/wire assignment is made here.
2. Observe the exact parent's nonzero freeze sequence from the kernel. Bound
  waits and stop/watchdog behavior. Validate the entire snapshot against actual
  file view and stream holdings/history; labels/snapshot bytes confer no grants.
  Reserve a free child2–4/next epoch and exact two fresh channel endpoints. Exhaustion
  before copy leaves parent FD state unchanged and owns all reservation cleanup.
3. Stage only existing parent stream holders; no broader rights. Perform actual
  kernel copy with exact parent/token/child slot/endpoints. Known refusal with no
  child permits known staged-holder rollback and explicit token-matched thaw.
  Current kernel thaw returns parent-11; preserve the actual owner-side copy error
  separately and agree how the public stage maps errors. Do not invent ENOMEM
  delivery merely because the owner saw-12. Unknown copy forbids thaw/rollback or
  release based solely on absence of a success reply; retain obligations/fail-stop.
4. For confirmed child, install exact shared file descriptions/offsets and separate
  flags, stream holders and fresh file-channel generation under the agreed ordering
  rule. The parent snapshot is immutable transaction input; no post-copy parent
  memory reread may change child initialization. Failure after copy requires actual
  child termination/endpoint settlement before releasing its held resources; local
  record removal is insufficient. Do not call exec-close during copy failure.
5. Child validates actual copy-result memory/channel grants and native PID/PPID,
  repairs auxv/TLS using the pinned upstream ordering, and transitions only its
  copied context metadata to the exact new sole startup consumer. Never run finish
  on inherited parent channel labels, erase parent state, allocate a second live
  ledger, or treat `memset`/getpid alone as native rebind authority. Current startup
  rejects an already admitted copied object: an explicit child-only transition is
  still needed. Preserve pipe histories and bind fresh file/channel generations.
6. Publish child readiness only after304-byte startup validates and owner records
  match the kernel child. Preserve exact child wait/terminal/collected/reclaim
  barriers. Define resumed-parent admission before returning a successful stage,
  with no stale reply reuse or replay. Full dispatcher shutdown/fit remain separate.

Immutable executable admission and failed/unknown-exec preservation are separate
work. Fork completion must not fabricate exec capability or public POSIX dup2.
No generic process framework, new service, larger quota or extra OS campaign is
needed to resolve this bounded parent/three-child transaction.

## Required acceptance and follow-ons

[BG-069](../../.planning/backlog/active/BG-069--agree-tagged-fork-staging.md)
owns exact producer/consumer wire, ordering proof and child transition agreement.
[BG-070](../../.planning/backlog/active/BG-070--compose-tagged-fork-transaction.md)
then owns implementation and full link/native cases. Remain under BG-067/v1;
these are essential product prerequisites, not shelved framework work. No completion
or owner approval is asserted by capturing them.

Before acceptance: deterministic actual-library schedules around snapshot/freeze/
copy/thaw/local clone/readiness, resumed-parent FD mutations, every known/unknown
copy and cleanup boundary, invalid/stale tokens/epochs/rights, capacity/no mutation,
shared file offsets/per-process flags/last close, independent pipe-holder EOF,
child TLS/auxv/generation rebind and parent preservation. Reject old64-byte frames
and malformed tagged snapshots. Require a complete exact shell link without old
runtime/ignored imports/stubs, full resource fit, then fresh matched Aether native
positive/refusal/unknown cleanup/continued-parent/child wait cases. Reuse retained
unrelated evidence within its original scope; do not replay broad campaigns.

This review stops at the ordering/child-transition contract. Sys-init owns matching
coordination and dispatcher work; userland owns the matching stage/client/libc
transition, Aether the native primitive guarantees and consuming witnesses. Local
handoff only: no sibling edit/message or invented independent sign-off.
