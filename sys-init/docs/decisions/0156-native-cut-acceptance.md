# 0156 — Separate native cut acceptance from delivery

Accepted local experimental design, 2026-09-07; BG-057 PH-07. Research and contract
only; no runtime, native source, wire protocol, release pin or sibling change.

The [source review](../research/NATIVE-CUT-ACCEPTANCE-REVIEW.md) finds that current
native inbox delivery, model queue insertion and effect acknowledgment do not
establish a whole native observation cut's application. Model batching also sorts
terminal before launch and may skip stale events while returning successfully.

Adopt [NC-01–08](../specs/NATIVE-CUT-ACCEPTANCE-V0.md): a private serialized
CutCoordinator, exact owner/source/member receipts, pre-mutation whole-cut
reservation, separate ordered launch/terminal/cleanup cuts, retained uncertainty,
and retirement only after applied Cleaned and positively empty resources.
Retirement preserves tombstones/raw history; storage reuse is not authorized.
Two lifetime attempts and six retained cut records bound this first experiment.
The twenty-effect reservation is inherited model scope, not a native implementation.

Reject boolean acknowledgments, intake-as-application, terminal replacement of
launch, automatic retry after uncertainty and history eviction. This boundary
needs no OS-specific facility or new dependency. It preserves kernel authority
and does not infer POSIX mechanisms from companion implementation choices.

Foundations O-01/O-03/O-04, I-01/I-03–06 and E-01–08 apply. Distribution DS-01/03/05
limit claims: logical application is not durable commit or replacement-owner
recovery. No persistent writer, auth/session, boot/layout or UI behavior is added.
Draft quality requirements guide scoped review, not shared release adoption.

Before closing research, capture BG-059 for pure qualification and BG-060 for
sustained history/reuse design; retain BG-057 real adapter/native integration,
BG-058 full launch composition and BG-033 unknown recovery. Next: BG-059's
pure identity/reservation/application cases, before changing native History.
Run all local checks, retain frozen research inputs and verify all tracked native
inputs/pins unchanged. The decision 0155 target witness remains the runtime
checkpoint; no new QEMU execution is needed for unchanged runtime sources.

## Validation and review

All ten local gates pass in `run-onw3am8l`, with unchanged checked inputs. All
12 prior native consumer source files remain byte-identical to decision
0155. The native catalog and three release locks also remain unchanged. No new
native execution is claimed or required by this source-only review. Runtime
checkpoint: 185 QEMU cases, with the existing BG-056 producer source-closure caveat.

The source/contract review checks ownership, identity, whole-cut ordering, bounded
reservation, pre/post-commit failure and retirement without recycling. It does not
claim independent reviewer sign-off. Documentation impact includes this contract,
research, standards applicability, quality references and active planning handoff.
Next: BG-059 pure coordinator qualification; BG-057 native integration follows.
