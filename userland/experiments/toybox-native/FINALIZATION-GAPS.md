# UL-067 / CAT-06 remaining consumer requirements

Checkpoint2026-09-07: [local close-policy qualification](../../docs/evidence/toybox-close-consumer-2026-09-07/README.md)
now exercises the named diagnostic, uncertainty and repeat-hook requirements.
The candidate explicitly selects `cat: close failed\n`; the proposed text below
is historical. Broader CAT/review/regression and recursive/signal behavior remain
separate. Do not reopen these qualified cases as optional utility refinement.

2026-09-07. Local implementation proposal for the next matched producer/consumer
slice, not a shared API or accepted owner contract. The captured finalize delivery
qualifies callback output and selected flush/known-close cases; it explicitly
leaves the following gaps. Preserve its existing source, modes and receipts.

## Close failure and diagnostic ordering

Keep Toybox callbacks and real flush before closing any stream. Consume input0
then output1 once. A complete EIO close response confirms consumption and leaves
other roles usable. If either fails this way, preserve any prior nonzero result;
otherwise promote to1. While diagnostic2 is still live and transport unpoisoned,
attempt one bounded diagnostic through real public stdio, then flush and consume2.
Proposed exact text: `cat: close: I/O error\n`. This text needs an opt-in owner
expectation before native acceptance; it is not a changed upstream error string.
Do not register this experimental artifact as general cat.

A malformed/cut close reply is unknown completion: retain failure, poison shared
transport, retire remaining local aliases without further channel calls, and let
the supervisor verify remote cleanup. Do not retry the close or attempt a wire
message through a poisoned diagnostic role. Local alias retirement is not remote
acknowledgement. If diagnostic close itself fails, it is already consumed; retain
failure with no invented fallback sink. Preserve64 from earlier command failure
through all diagnostic/close failures.

Require owner cases for close0/close1 plus complete diagnostic, diagnostic EIO/EINTR
or unknown completion, close2 failure, unknown close0/1, prior64 and ordinary0.
Expected input/output bytes stay fixed; only explicitly selected diagnostic bytes
and status change. Zero/partial diagnostic progress must terminate finitely.
Negative controls must reject false0, omitted diagnostic when authority is usable,
repeated close, traffic after poison and omitted alias retirement. Verify both
generations, remote inventories and exact four reclaims for accepted outcomes.

## Re-entry result policy

The delivered private-hook test returns120 from a second hook call but allows the
outer call to return0. That does not meet the local requirement that repeated
finalization cannot produce success. Propose a process-local failure latch: set
entry state before cleanup effects; a second entry latches failure and produces no
new channel calls; the outer completion observes that latch and cannot return0.
Retain earlier nonzero command status. Qualify one injected repeat with exact
terminal1, no extra effects and normal supervisor cleanup, plus a control that
ignores the latch and must reject. This proposal covers only the private cleanup
hook. Recursive Toybox xexit/callback entry and signal-safe finalization require
separate supported semantics and must not be claimed from this test.

## Ownership and next execution

Userland owns the private finalizer, public-stdio use and terminal mapping; Aether
owns opt-in verifier modes, scoped transport and remote resource oracle. Coordinate
these expectations through this explicit proposal; no sibling edits or messages
are authorized by the document itself. Use a new isolated, receipt-pinned pair.
Run finalizer, actual cat, error and usage regressions after relevant changes.
Independent review and full producer/backend rebuild remain required. These are
release-path correctness requirements, not deferred PRF tuning.
