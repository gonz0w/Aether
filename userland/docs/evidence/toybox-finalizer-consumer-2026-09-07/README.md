# UL-067 local finalizer qualification

The completed producer handoff is captured in a new private snapshot. Its18
finalizer cases pass locally with rebuilt Toybox objects, probe, stdio callback,
xwrap adaptation and selected supervisors. Thirteen non-mutant cases verify both
generations and four native reclaims; five mutants require exact rejection context.
This is partial CAT-06 evidence, not full acceptance.

| Cases | Observed behavior |
| --- | --- |
| buffered / short | Callbacks buffer32 bytes without channel traffic; real xexit flushes exact output before alias closes and terminal0. |
| flush EIO/EINTR | Read32/output16, exact upstream diagnostic and terminal1. Failed fflush legitimately short-circuits ferror. |
| malformed/cut flush | Output16 may commit without confirmation; poison forbids further channel traffic; terminal1 and supervised reclaim. |
| close input/output/diagnostic | Known consumed-close error promotes0 to1; other aliases retire. |
| prior status64 | Preserved through successful cleanup, failed flush and failed close. |
| repeat hook | Second private-hook call returns120 without traffic; outer terminal remains0 under the delivered contract. This does not satisfy the remaining re-entry terminal requirement. |
| corrupt / skip-flush / early-flush / skip-close / force-zero | Exact client/owner rejection contexts; zero-reclaim negatives are not recovery claims. |

[Finalizer results](finalize/results.json) retain exact per-case expected/observed
status, command records and raw serial/QEMU logs. The normal-copy regression on
the same source is recorded separately under [cat](cat/results.json). The buffered
finalizer mode itself does not call cat_main; the actual applet is a separate test.

## Inputs and review

[Intake](intake.json) verifies the new archive
eaf855dc35ac4a9a9b3db86a187f72875ec8791fd6be2f9e06d71bc0c8584a86 and its native
receipt/source identities. Exactly two runtime files changed from the prior
consumer: toybox-cat-probe.c and opt-in cat-roles.rs branches. Earlier snapshots
and evidence remain intact. SDK, CRT and backend are verified reuse; local owners
and all baseline applet translation units are rebuilt. The producer's retained
backend comparison supports byte equality with its own fresh build, not a local
backend rebuild claim. Full producer/regression qualification remains open.

The [driver](run.py) adds only finalize profile selection and pinned Rust resolution
already used by errors. [Plan](PLAN.md), generated recipes and per-execution
identities are retained. Existing180-second owned-process limits,30-second guest
watchdog, clean environment and process cleanup apply. No installation, sibling
edit, interface/pin change or network fetch. Original/imported licenses and
existing ASCII output/boot markers are preserved.

Codex technical review: callback data has static lifetime and real xexit owns/frees
callback nodes. New flush observation preserves short-circuit behavior. Close
consumption and poison remain in the existing transport; the repeat guard prevents
additional calls but does not latch an outer failure. Reviewed owner expectations
retain exact bytes/status and resource checks. Foundations O/I/E and quality
C/CP/TD/TE apply. Independent reader/maintainer review remains pending.

## Remaining CAT-06 work

[Concrete continuation](FINALIZATION-GAPS.md) specifies the next proposed matched
slice: one final close-error diagnostic while stderr is live and unpoisoned;
failed/uncertain diagnostic and close outcomes; and a repeat-entry failure latch
that prevents outer success. Diagnostic2 close failure cannot invent another sink.
Prior nonzero status must survive, unknown completion must not replay, and local
retirement must stay distinct from remote acknowledgement. This proposal has not
been implemented or accepted by the owner. Recursive/signal-safe xexit remains
separate. UL-067 and M3 stay active; optional tuning stays deferred.
