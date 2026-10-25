# Sustained history retention: source review

Date: 2026-09-07. BG-060; research only. Decision 0177 establishes one complete
pair lifecycle. This review proposes a next experiment, not a reusable native
owner, shared ABI, durable archive or production restart policy.

## What the current implementation establishes

The [reservation core](../../prototypes/native-supervisor/cut_reservation.rs)
uses six append-only records, twenty reusable effect credits, owner-bound keys,
and separate serial/journal counters. `reserve_phase` rejects record exhaustion
and counter exhaustion before mutation. Cancellation retains a record;
`retire_effect` and `retire_empty` release credits without erasing records.
The six-cut test checks every before/after state and still receives Full after
retiring final Cleaned credits. A larger effect pool alone cannot add a cycle.

The [native binding](../../prototypes/native-supervisor/binding.rs) retains two
primary observation samples and original launch associations in History.
`IssuedReclaim` retains actual close/reclaim returns while its local executor
runs through acknowledgment. Those values are not a long-lived completion
archive. `RetainedEffect` preserves occurrence identity, not the full raw return
history. An archive assembled only from final phase flags would lose evidence.
The fixed member selectors 0/1 identify slots in this experiment, not an
unbounded series of instance generations. Current phase and effect generation
also assume the initial pair. Reinitializing Storage alone cannot implement retry.

[Decision 0177](../decisions/0177-complete-two-service-teardown.md) supplies the
consuming witness and exact limits: six records for one pair, 16,360-byte positive
image under 16 KiB and a 4 KiB stack. It does not demonstrate space for another
History or Application. A second stack-resident copy is not an accepted design.
The new research source manifest records inspected local input bytes; retained
0177 evidence remains authoritative for its execution claims.

## Alternatives and disposition

| Alternative | Consequence | Disposition |
| --- | --- | --- |
| Increase the append-only record array | Defers exhaustion; still finite, increases memory | Useful measurement control, not sustained retention |
| Reset/reconstruct the current owner when workers disappear | Loses uncertainty and can repeat identities; empty adapter is not an exact completion checkpoint | Reject |
| Evict oldest records on a timer or ring overwrite | Age alone proves neither resource quiescence nor safe replay disposition | Reject for authoritative records |
| Require a file/logger to accept every record | Introduces unavailable persistence semantics and couples progress to an optional sink | Defer durable export to BG-033 and persistence owners |
| Explicit process-local completion checkpoint plus fresh cycle admission | Separates evidence retirement, slot reuse and identity; exposes finite archive capacity | Select for a synthetic bounded experiment |

A bounded store cannot retain every raw event forever while admitting infinitely
many cycles. Production must eventually specify a loss/compaction policy for
*resolved* historical diagnostics, or an authoritative retention service and
backpressure. Neither is selected here. Unknown operations never become resolved
because their records are old. Optional diagnostic export is separate from the
mandatory evidence used to authorize lifecycle mutation.

## Proposed checkpoint contract for the experiment

Use one stable controller owner, a checked monotonically increasing cycle number,
and separate member/instance and occurrence identities. A slot number is only a
storage coordinate. Keys bind owner, cycle, member generation, cut serial, journal
and complete occurrence identity at every effect boundary; no counter wraps.
Kernel worker generations remain separately validated native identities.
No reset, replacement owner or import from an archive grants authority.

1. Before launching a cycle, reserve its completion archive capacity as well as
   active cut/effect/sample capacity. Exhaustion rejects admission without effects
   or consuming an identity. Capacity reserved for existing cleanup cannot be
   taken by new work. Optional logger availability is not an admission input.
2. Preserve raw acquisition/launch/observation and close/reclaim outcomes as they
   happen under their original identities. Started or interrupted operations with
   no authoritative completion remain Unknown. The model must distinguish no
   call, successful return, failed return and missing return.
3. A checkpoint requires both exact Cleaned receipts; all obligations acknowledged
   and retired; no active reservation or pending release; complete source samples;
   and fresh, exact empty resource ownership for both instances. Global adapter
   emptiness is only supplemental. Final empty Cleaned credits must be retired.
4. Prepare the checkpoint by copying the full bounded evidence into the reserved
   archive slot while the source remains intact. Validate owner/cycle, membership,
   record count/order, occurrence dispositions and actual return association.
   A digest may detect corruption but cannot replace missing fields or authority.
5. Publish the complete checkpoint before making active slots eligible for reuse.
   Failure/interruption before publication retains source evidence and closes
   admission; a partial archive is not a completion receipt. After publication,
   interrupted local release leaves the checkpoint intact and admission closed
   until the exact release completes. No kernel operation is replayed to finish it.
6. Admit the next cycle only after checkpoint publication and complete local slot
   release, a new archive reservation, and checked fresh identity allocation.
   Old receipts can be inspected in their retained window but all mutation APIs
   reject them, including start, acknowledgment, retirement and checkpoint replay
   against a new cycle. Repeating exact checkpoint inspection is read-only.

This ordering is a single-owner model requirement. It is not crash-atomic storage
or a claim that copied Rust keys are automatically revoked. A future implementation
must enforce the cycle check in every path, including internal helpers, and retain
controller identity across active-storage replacement. The current constructors
are not an authorized rotation API. Arbitrary service restarts while a dependency
remains live require a different retention unit; whole-pair completion does not
answer that case.

## Bounds and failure oracles

The first model experiment admits at most two cycles, each with two members and
six cuts. It has six active cut slots, twenty active effect credits and two
completion archive slots. Each archive holds exactly one complete bounded cycle,
including associated raw outcomes; it cannot borrow space from the active pool.
Reserve one archive slot per admitted cycle. After two completed cycles, a third
admission returns Full with no mutation. Two archive slots are an experiment bound
to distinguish fresh identity from first-cycle replay, not a production sizing
recommendation. The archive representation must declare field/count limits and
measure its byte layout before any native proposal. No allocation or stack budget
is inferred from a Python model's logical bounds.

Required tests: two independently expected six-cut traces; rejection of old owner,
cycle, member generation and each altered occurrence field; archive full; counter
exhaustion; missing raw returns; unresolved/failed cleanup; outstanding reservation;
nonempty resource inventory; omitted final retirement; and interruption on both
sides of checkpoint publication/release. Every rejected prepare/admission compares
source state before/after. Post-publication interruption must preserve the committed
checkpoint and block new mutation. Mutation controls must omit publication,
identity qualification and uncertainty checks and fail the appropriate tests.
No timeout, synthetic empty flag or diagnostic acknowledgment proves native cleanup.

Process death loses this volatile store. Replacement-owner reconciliation, power
loss, storage ordering and outstanding I/O stay under BG-033. Native qualification
also needs storage/code/stack measurements and fresh consuming runs; the current
24-byte code margin is a known constraint, not yet a proven kernel blocker.

## Standards and portability disposition

Pinned [Foundations ownership](../vendor/aether-foundations/v0.1.0/OWNERSHIP.md)
O-01/O-03/O-04 keep mechanism authority separate, require checks at use and deny
stale reuse. [Interfaces](../vendor/aether-foundations/v0.1.0/INTERFACES.md)
I-04–06 require distinct generation/operation identity, bounded exhaustion and
preserved uncertainty. [Evidence](../vendor/aether-foundations/v0.1.0/EVIDENCE.md)
E-01/E-04–08 require pinned inputs, layer-specific claims and failure controls.
[Persistence](../vendor/aether-distribution/v0.1.0/PERSISTENCE.md) DS-01/03/05
exclude inferred durability or replacement-owner recovery.
[Observability](../vendor/aether-distribution/v0.1.0/OBSERVABILITY.md) OB-02/03
separate non-authoritative diagnostics and optional sink loss from lifecycle state.
No new exception, shared rule or pin is introduced; unpublished candidates remain
review inputs. Future shared retention/export contracts belong in Aether-standards.

This design uses local finite-state identity and capacity rules, no OS-specific
queue, filesystem or process primitive. POSIX/BSD/illumos/Linux adapters still need
their own authority and cleanup witnesses; no compatibility execution is claimed
or scheduled. Aether remains the next target. External init-system comparisons
are unnecessary to establish the inspected code's finite capacity and missing
checkpoint; this review cites local primary sources rather than importing another
system's retention semantics.

## Follow-ons and open questions

BG-062 owns the bounded checkpoint/admission model and omission controls. BG-060
remains active for production retention: which resolved evidence may be compacted,
for how long, under whose authority, and how independent member restart affects
reachability. BG-057/BG-058 own eventual native storage/identity integration;
BG-033 owns replacement and unresolved operation reconciliation. Do not close
BG-060 on the strength of a two-cycle model. No native behavior changed here.
