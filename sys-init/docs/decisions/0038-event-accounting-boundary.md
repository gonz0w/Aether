# 0038 — Characterize the event-accounting boundary

Accepted for BG-050/BG-033 research on 2026-09-06. Before connecting Model.batch
to AccountedDelivery, capture reachable counterexamples to the submission-only
assumptions. This changes tests and local design records, not lifecycle behavior.
Foundations I-01/04–06 and E-04–08 apply through STANDARDS.md.

The [source review](../research/EVENT-ACCOUNTING-BOUNDARY.md) identifies a reachable
twelve-effect cut, repeated force requests for one generation, and supervision
effects without an active operation. Eight credits and one kind bit per generation
cannot describe these cuts. The existing submission ledger remains scoped to
decision 0037; do not widen its bounds or change its token format silently.

Choose a separate bounded event journal experiment under BG-057. Specify an
occurrence identity, bounded retained cause, force policy and reservation before
observation mutation. Preserve ordering and distinct terminal/cleanup evidence.
Do not attach unrelated active operation IDs to background supervision effects.
A conservative twenty-slot per-cut bound is derived in the review; it is not a
change to the existing eight-slot ledger or a production resource budget.

Alternatives rejected for this integration: slicing a cut changes deadline/event
ordering; deduplicating force assumes invocation equivalence; reserving after
batch can leave mutations unaccounted; using active.id loses background identity;
automatically mapping executed/rejected acknowledgments to observations invents
producer guarantees. A model-copy transaction remains a possible test technique,
not the selected production architecture or a reason to duplicate lifecycle logic.

Add six independently specified characterization tests: twelve effects at a
deadline, two force requests in one cut, late force in another cut, effects after
completion, effects outside another operation's scope, and reclaim acknowledgment
without cleanup observation. These document current behavior, including limits;
they do not bless duplicate force as a native execution policy. A future deliberate
semantic change must update the contract and these oracles together.

Run model/full checks and retain source/log hashes. Existing mutation controls
remain required; no new runtime guard is introduced for a new mutation control.
No new dependency, unsafe code, CLI, shared standard, pin or native ABI changes.
The work is portable deterministic Python model evidence only, not POSIX or
Aether process behavior. BG-057 retains implementation and BG-032/BG-033 retain
exact producer mapping and recovery; no kernel mechanism request follows yet.

Validation: 134 model tests, twelve mutation controls, 48 host tests, 37 harness
tests and all offline gates pass. [Retained evidence](../evidence/event-accounting-boundary-2026-09-06/README.md)
binds the reviewed model source and exact characterization tests. No new native
execution was performed; historical target evidence was audited only.
