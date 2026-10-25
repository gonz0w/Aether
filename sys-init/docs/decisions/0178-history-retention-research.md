# Decision 0178: research checkpointed history retention

Status: accepted research direction; implementation unqualified.
Date: 2026-09-07. Owners: BG-060, follow-on BG-062.

The complete pair consumes six retained cuts. Effect-credit retirement cannot
admit another cycle, and reclaim raw outcomes are not retained in a durable or
long-lived archive. Accept the source review and proposed ordering in
[the research](../research/SUSTAINED-HISTORY-RETENTION.md).

Next implement a pure bounded two-cycle checkpoint/admission experiment: reserve
completion capacity before effects, retain exact raw outcomes, publish a complete
checkpoint before active-slot release, and reject all stale mutation receipts.
Preserve a stable controller and checked fresh identities. Two archived cycles
then Full is the intended model bound, not sustained production availability.

Rejected alternatives, failure boundaries, test oracles, applicable standards,
portability assumptions and remaining questions are in the research. No runtime
API, reset, retention eviction, shared interface, release-pin update or sibling
change is authorized by this decision. Native code/stack feasibility and fresh
consuming acceptance precede any native completion claim.

Technical review: active authority and historical inspection are separate;
unknown evidence cannot be evicted; optional sinks cannot acknowledge a checkpoint;
archive capacity is reserved before launch so a full archive does not strand an
already admitted cleanup. No independent reviewer sign-off is claimed.
Documentation impact: BG-060/062 sequencing, standards disposition and quality
inventory. Validation/evidence is recorded in the linked research bundle.

[Research evidence](../evidence/history-retention-research-2026-09-07/README.md).
