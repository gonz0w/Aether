# Native pending history v0

Accepted local experimental contract, 2026-09-06; decision 0084. Specified rules
and acceptance plan, not implemented storage, replay, conflict or retirement APIs.
Extends [terminal evidence](NATIVE-TERMINAL-EVIDENCE-V0.md) and preserves the
[binding identity](NATIVE-DRIVER-BINDING-V0.md) contract. Findings and alternatives
are in [the source review](../research/NATIVE-PENDING-HISTORY-REVIEW.md).

## Bound origin and lifetime

PH-01. A terminal-history view is privately minted only from the current bound
session's sealed Terminal Sample. Preserve all three raw signed-RAX/RDX/R8 triples,
their count and the qualified revision/result/kind/readiness. Bind the view to the
non-rebindable live owner reference, fixed profile and producer, exact ten-field
launch token, retained attempt index and actual Worker/full native generation.
Service generation, native generation, sample revision and token occurrence remain
distinct. Equal predicted numbers or copied token text cannot create a binding.
The actual resource wrappers remain owned by Driver; an evidence view adds no
stop/reclaim authority. No public constructor accepts an arbitrary Fact and token.

Caller-owned fixed storage may follow the existing exclusive-borrow arrangement,
but the implementation must make that storage and binding association outlive every
view and pending offer. Never recycle the store merely because a Sampling handle
was dropped. Checked owner/attempt identity plus Rust borrowing may enforce the
private boundary; language-specific layout remains implementation work. No owner
restart, relabeling, index reuse or storage reset is accepted in this slice.
Live, failed and interrupted samples cannot mint terminal views. Their histories
and any resource uncertainty remain retained under the existing failure rules.

## Offer and comparison rules

PH-02. Offers consume no kernel read, issue no lifecycle effect, and append no
journal event. The names below are local outcomes, not a wire or CLI schema.
Validate the live context and complete binding before comparing content. An offer
must refer to retained, qualified origin, not a caller assertion of provenance.

| Condition | Outcome and allowed state change |
| --- | --- |
| Owner already closed | Closed; preserve all histories/resources and perform no work |
| Wrong owner/profile/producer, token field, attempt, actual worker or service association; ineligible sample | Denied; no replacement, closure caused by that request, new reads or resource mutation |
| First eligible terminal sample in its pre-reserved primary slot | Held; associate exact raw history and fact with the original binding, keep global pending position occupied |
| Same binding, same complete qualified fact and exact three raw triples | Duplicate; retain the original view/storage and reservation, no append/counter advance/read/effect/acknowledgment |
| Same binding, different independently qualified terminal candidate, with reserved diagnostic capacity | Conflict; retain the first history unchanged and the conflicting raw sample separately; close admission and retain all resources |
| Capacity unavailable before candidate production/admission | Full (or Closed if already closed); deny before another read or owned history is created; preserve retained values |

Invalid external/request identity is ordinary denial, not evidence of a conflicting
fact. A violation of an internal minted-view invariant is a local failure that
closes the owner; it must not be reported as a native errno. Do not claim a hostile
caller can bypass the trusted Driver by constructing Rust-private state.

Duplicate means equality of original binding and retained terminal content, not
exactly-once execution. Comparing metadata does not authenticate the producer.
The first held sample was already qualified through its bound native path; later
replay reuses that origin. An equal-generation event from the other service cannot
replace, acknowledge or advance the first service's history even if every terminal
number matches. Denial must occur before content equality could hide that mismatch.

PH-03. A conflict preserves both original and first conflicting candidate, all
raw triples and binding association, and a distinct local conflict disposition.
It never emits a terminal policy event, clears pending, changes generation, releases
a worker/reader or invents stop/reclaim completion. Once closed, further offers
cannot replace either retained sample or acknowledge a duplicate as accepted work.
Read-only diagnostic inspection remains possible within the trusted owner lifetime.

PH-04. Current legitimate capture remains one-shot. A retained terminal fact
occupies the sampling position, so this contract authorizes no second native
O1/S/O2 sequence to search for conflicts. A test-only candidate producer may supply
a separately qualified synthetic triple set with explicitly bound fixture identity
into the pre-reserved diagnostic slot. Label this as synthetic conflict evidence;
it is not a claim that the pinned stable terminal producer contradicted itself.
Do not silently overwrite a real return or expose that test constructor publicly.
Native-source provenance, local comparison and diagnostic retention are separate
acceptance layers. Future independent observation producers need their own contract.

## Fixed capacity and retention

PH-05. Maintain these bounds before sampling or accepting any candidate:

| Storage/position | Bound and consequence |
| --- | --- |
| Attempts and primary raw samples | Two fixed attempt-associated slots; one sample of at most three triples per attempt; no reset/replenishment in this slice |
| Active sampling/effect position | One globally, preserving current Driver.pending serialization |
| Terminal pending position | At most one under current serialization; a terminal result keeps the global position occupied |
| Conflicting diagnostic sample | One extra pre-reserved sample of at most three triples for the owner; first conflict closes admission |
| Total raw retention | At most nine triples across two primary slots plus diagnostic slot, with fixed metadata; no allocation or unbounded queue |

A live first observation releases the active position but consumes that attempt's
one-shot sample and leaves its raw history retained. The other admitted attempt
may then sample into its own reserved slot. A terminal, failed or interrupted
sample blocks subsequent conflicting driver effects; failures close the owner.
The two-attempt bound does not promise two pending terminal facts or continued
polling. An unused diagnostic slot does not authorize resampling a terminal worker.
Reserve capacity before producing a synthetic candidate; if the diagnostic slot
is occupied the closed-owner check prevents another candidate production. A denied
offer transfers no ownership to the history store. Byte layout/stack cost and strict
4 KiB image fit require implementation measurements; nine triples is a logical
retention bound, not evidence that this storage is already allocated/enforced.

PH-06. Denials, duplicate replay and conflict closure preserve consumed issuance,
slot/native generation and original raw sample. No eviction, wrapping counter,
service substitution or "latest wins" behavior. Fixture cleanup may dispose
positively known resources after assertions but does not qualify retirement.

## Consumer acceptance boundary

PH-07 (BG-057, deferred). Held/Duplicate is not journal reservation, capture,
application, delivered terminal policy, issued reclaim or applied Cleaned. Keep
pending/history until a named coordinator contract specifies the exact accepted
owner/binding, whole-cut identity, event ordering, applied acknowledgment, failures
after application, stale/replayed acknowledgment and resource-retirement order.
In particular, terminal-before-launched ordering cannot be inferred from the
model's event-slot replacement. No acknowledgment struct, clearing method, reset
or replenishment API is accepted here. Reclaim still requires its separately issued
bound obligation; accepted terminal history never authorizes it. Unknown owner
recovery remains BG-033 and cannot be implemented by dropping borrowed storage.

## Qualification sequence

| Step | Required independent oracle and control |
| --- | --- |
| PH-01/02 first slice | Actual bound terminal sample mints its private view; exact duplicate changes no raw bytes, reads, issuance/generation, pending state or resource ownership. Wrong owner/index/each token field/actual worker and equal-generation other-service substitution deny. Control omitting full identity must fail the identity assertion |
| PH-03/04 conflict | Separately labelled, valid synthetic contradictory candidate retains both raw samples and original fact, closes admission and preserves resources. Controls overwriting the first sample or omitting closure must fail distinctly; further candidate production denies before reads/storage mutation |
| PH-05 two-attempt capacity | While a terminal position is occupied, the other admitted service cannot sample. A live first sample permits one second-service sample while retaining the first live raw history; each attempt remains one-shot. Controls bypassing capacity or resetting the first slot must fail |
| PH-06 sealing | Partial/error/interrupted samples cannot become a terminal view; no reset or retirement follows from duplicate, closed-state inspection or fixture disposal. Retained identity/content survives all denials |
| PH-07 future gate | Full/busy journal, two-service ordering, replay/stale acknowledgments, post-application failure and matching applied Cleaned retirement require a separate contract and fresh consuming evidence |

Record exact assertion/cleanup results before each implementation run. Preserve
all 143 current native oracles, the retained-sampling-v1 profile and 4096-byte bound.
Host tests may establish comparison logic and omission detection; only a fresh
native witness can qualify bound capture and resource retention. Split probes
without weakening assertions if size requires it. No kernel change is presently
needed for PH-01–06. This contract does not select a production language, Linux-only
facility or POSIX/BSD/illumos/Linux adapter. Foundations O-01/O-03/O-04,
I-01/I-03–06 and E-01–08 govern this scope under STANDARDS.md; shared rules remain
in Aether-standards and existing released pins/Distribution exclusions are unchanged.


## PH-01/02 implementation slice — decision 0085

The private `Sampling::terminal_view` factory and nested `pending_history::View`
implement origin binding and read-only replay within the current borrowed session.
The factory requires open pending state, Applied launch, a started terminal sample
and matching retained fact. Owner identity fixes immutable profile/producer;
full token, attempt index and actual Worker are checked before Duplicate. The view
borrows the session and Sample; it exposes no mutation or public Fact/token packet
constructor. Its sample accessor preserves exact raw history and qualification.

This slice compares requests for the same privately retained view. It does not yet
accept a second candidate, compare two independently qualified sample histories,
implement Held/Conflict/Full storage, close on an internal minted-view conflict,
or retain storage across session destruction. PH-03–06 must establish those
boundaries before claiming the complete nine-triple store. PH-07 still owns
whole-cut journal acceptance and retirement. Native fixture cleanup is not that
retirement. See decision 0085 for acceptance results and unchanged limitations.


## PH-03/04 host core — decision 0086

Private Held now compares two independently qualified views, retains the first
conflict and closes its local store. Its explicitly synthetic producer callback
runs only after open/capacity and request identity checks; produced identity is
revalidated. Equality includes Sample state/count and all raw triples. Duplicate
preserves the primary; closed-state inspection does not acknowledge new work.

This is host-qualified borrowed retention only. It references at most one primary
and one diagnostic Sample without allocating either; caller storage lifetime is
not a physical reserve guarantee. Native guard integration must own Driver and
sample associations, reserve storage before production, propagate closure without
letting views escape, and preserve actual resources in fresh target evidence.
The existing 151 native clients rebuild identically and do not consume this core.
PH-05–07, whole-cut retirement and storage across guard destruction remain open.


Decision 0087 attempts native guard integration but remains an unqualified build
study: every new probe exceeds the current 4096-byte fixture limit. The prototype
and alternative layouts are retained outside accepted runtime sources. PH-03/04
native closure, guard lifetime and physical diagnostic reservation remain open;
the host core and 151-case native checkpoint are unchanged. Do not treat the
proposed native omission codes as executed outcomes.


## Capacity adoption — decision 0093

The owned Driver/two-primary/one-diagnostic container now qualifies the bounded
PH-05 Live/Terminal/conflict scenario and exact recycling controls. Its nine-slot
capacity holds seven actual triples in this serialized workload; it does not add
a second terminal pending position. Decision 0090's explicitly selected ABI-15
profile permits 8192 bytes; historical/default ABI-6 4096-byte bounds remain intact.
The target container layout is 760 bytes, separate from peak stack use. PH-06
promotion/failure combinations and PH-07 retirement remain open. See decision 0093
and its fresh 166-case evidence; earlier build-only status above is historical.


## Sealing adoption — decision 0094

History replay now delegates to the private Sampling terminal-view factory.
Six native owner scenarios deny Live, partial Awaiting, malformed-status Failed
and local Interrupted samples while retaining exact history and ownership. The
three omission controls detect false acceptance, erased history and lost reader.
The status error slot is synthetic and is not a native errno witness. Native errno
history and closed-terminal inspection remain PH-06 follow-ons; PH-07 whole-cut
retirement remains unimplemented. Fixture cleanup grants no reset/acknowledgment.
See decision 0094 and its fresh 175-case source-pinned run for precise coverage.
