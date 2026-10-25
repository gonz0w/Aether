---
id: BG-050
title: Specify CLI and control request contract
status: active
created: 2026-09-05
source_type: research-follow-on
area: specification
---

## Problem and acceptance criteria

Specify exact grammar, service-name validation, exit codes, versioned machine results and finite client waits for the runtime draft. Define authorization, conflicting requests, stop supersession, deduplication and replay after uncertain receipt. Preserve distinctions between accepted/completed/client-timeout and persistent enablement/current activation. Coordinate BG-045 status and BG-037 enablement.

## Evidence

[Runtime v0 draft](../../../docs/specs/RUNTIME-V0.md) and [operator comparison](../../../docs/research/OPERATOR-INTERFACE.md). Draft completion does not accept production architecture.

## Shared standards gate

Apply pinned Experience COMMANDS/OUTPUT/LANGUAGE via [adoption](../../../docs/EXPERIENCE.md), including help/version, stream separation, new exit conventions and control escaping. Preserve existing internal protocols. Foundations I-01–I-06 govern requests; propose changed shared conventions in Aether-standards rather than invent local alternatives.

## Native policy follow-on — 2026-09-06

Decisions 0023–0025 exercise bounded budgets, local cancellation and dependency
loss, but do not implement operator request delivery. The next specification slice
should define a minimal operation envelope/state contract before choosing transport:
manager epoch, operation identity, desired state, bounded request history, join vs
conflict, cancellation observation cut and ownership of late launch completion.
Map each to existing R-11–R-16 model tests and identify missing cases. Separate
client timeout/disconnect from cancellation and persistent enablement. Document
required caller authority without assigning speculative native grant values.

An internal bounded model prototype can proceed here; real native transport needs
an explicit producer/consumer contract and fresh target evidence. Coordinate
BG-040/BG-045 for admission/status and BG-032 only for demonstrated mechanism gaps.

## Logical contract and model correction — 2026-09-06

[Control v0](../../../docs/specs/CONTROL-V0.md) defines C-01–C-05 and maps ten
acceptance cases. [Decision 0026](../../../docs/decisions/0026-control-operation-identity.md)
fixes a demonstrated stop/shutdown join mismatch; 37 model tests and three
controls pass. Same-kind stop joins preserve deadlines, conflicting shutdown
intent rejects without effects, and partial stop preserves pending start state.

Next implement a trusted in-process facade for C07–C09: exact logical payload
validation, single-session request sequences, bounded receipts/high-water mark,
identical replay, changed payload rejection, retired/unknown outcomes and finite
client waits without cancellation. Record limits and tests before coding. C10
real caller authority/native transport and public CLI grammar remain separate
unimplemented work. No sockets or production daemon is implied; story stays active.

## Trusted receipt facade — 2026-09-06

[Decision 0027](../../../docs/decisions/0027-control-receipts.md) implements
C07–C09 in-process: 64 receipts/high-water sequence, replay without effects,
changed-payload rejection, retired/unknown outcomes, finite nonblocking logical
waits and session failure after ambiguous effects. Twelve cases join the existing
37 model tests; all 49 tests and three lifecycle controls pass.

Next specify external byte/depth/encoding limits, authority/session establishment,
caller scope and ambiguous delivery before transport. The trusted caller is not
authenticated, client waits do not perform I/O, and receipt storage is not durable.
Keep C10/native delivery and public CLI grammar open. Select transport only after
those boundaries and producer/consumer tests are concrete; story remains active.

## Session ownership and external boundary — 2026-09-06

[Decision 0028](../../../docs/decisions/0028-control-session-ownership.md) prevents
constructing a second facade against the same Model, preserving retired receipts
and failed-session state. Three regressions reproduce the old missing guard.
[Control boundary v0](../../../docs/specs/CONTROL-BOUNDARY-V0.md) proposes bounded
UTF-8 JSON request framing, strict decoding, authority-before-dispatch/disclosure,
manager-owned reconnect and ambiguous-delivery rules.

Next implement B01/B02 as a pure bounded codec plus facade tests, with no socket.
B04–B06 remain unimplemented: enforcing caller/scope/revocation, response codec,
stream deadlines/backpressure, restart identity and recovery. Coordinate BG-032
only for concrete native needs and BG-033/BG-045 for recovery/status. No native
rights or shared ABI are assigned by this local proposal; story remains active.

## Bounded request decoding — 2026-09-06

[Decision 0029](../../../docs/decisions/0029-control-request-decoding.md) implements
B01/B02: complete-frame decoding with 4096-byte body, pre-parser depth check,
strict UTF-8/JSON and numeric token bounds. Logical fields remain validated by
Control.submit. Nine cases verify parsing and facade integration; two mutation
controls catch missing depth and duplicate-key guards. Total: 61 tests/five controls.

Next specify bounded response projection/encoding, excluding internal effects,
then implement matching encode/decode tests. B04–B06 remain open for enforcing
caller/scope/revocation, stream deadlines/backpressure and restart/recovery. The
pure decoder is not a transport or authentication boundary; story remains active.

## Bounded client receipts — 2026-09-06

[Decision 0030](../../../docs/decisions/0030-control-receipt-encoding.md) implements
receipt encoding/decoding with exact fields and bounded leaves before serialization.
Internal submission/effects reject; original/replay receipts have identical bytes;
output failure preserves owned work. Eight tests and one field-check mutation
bring the suite to 69 cases and six controls.

Next specify observation/wait response schemas and bounded encoding, retaining
unknown/timeout/completion distinctions and operation identity. Transport error
replies, enforcing caller scope, revocation, deadlines/backpressure and restart
identity remain open. No real transport or shared ABI is accepted; story stays active.

## Observation and wait replies — 2026-09-06

[Decision 0031](../../../docs/decisions/0031-control-observation-encoding.md) adds
bounded observation/wait codecs with exact fields, nested identity checks and
state/outcome consistency. Eight cases and one identity mutation bring the suite
to 77 tests/seven controls. Unknown and client timeout remain distinct from
terminal outcomes; serialization has no lifecycle effects.

Next specify bounded transport error replies and an in-memory delivery experiment:
finite buffers, dispatch ownership, interrupted replies and explicit backpressure.
Do not expose a socket until enforcing caller binding/scope/revocation has a
matching contract and witness. Restart identity/recovery and real deadline sources
remain open. Logical codecs do not close B04–B06 or C10; story stays active.

## Error replies and memory delivery — 2026-09-06

[Decision 0032](../../../docs/decisions/0032-control-memory-delivery.md) implements
fixed error replies and complete-frame in-memory delivery. One reply and one
bounded effect batch preserve ownership through backpressure/disconnect and
serialization failure. Twelve cases and one error-disposition mutation bring the
suite to 89 tests/eight controls. Effect transfer is not execution acknowledgment.

Next define bounded incremental framing with logical read/write deadlines and
interruption cases before real I/O. Actual caller binding/scope/revocation,
execution acknowledgment and crash/restart identity remain open; memory delivery
does not close native C10/B04–B06. Story stays active.

## Incremental stream and logical deadlines — 2026-09-06

[Decision 0033](../../../docs/decisions/0033-control-incremental-stream.md) adds
bounded header-first buffering, partial reply output and read/write deadline
edges without extensions on progress. Ten cases and a deadline mutation bring
coverage to 99 tests/nine controls. Timeout and reconnect preserve owned work.

Next inspect current producer caller-binding facilities and specify required
scope/revocation semantics before real I/O. Also define driver effect execution
acknowledgment/recovery; transfer alone is not execution. Route concrete mechanism
gaps to BG-032 and crash/restart ownership to BG-033. Logical time and trusted
stream calls do not satisfy C10/B04–B06; no socket is authorized by these tests.

## Producer authority review — 2026-09-06

[Decision 0034](../../../docs/decisions/0034-control-authority-review.md) and
[Control authority v0](../../../docs/specs/CONTROL-AUTHORITY-V0.md) record existing
owner-bound connection mechanisms and separate sys-init policy gaps. Next implement
A01–A03 in a trusted single-binding model: missing/foreign binding, dependency
closure and whole-shutdown scope, independent read rights, response disclosure
(including conflicting active-operation details) and revocation cuts before input,
admission and output. Preserve history and owned work on denial/revoke.

Native reassociation, real enforcement and effect execution acknowledgment remain
BG-032/BG-033 work. OQ-021/022 record those unresolved contracts. This review slice
is complete; the owning story remains active and runtime authority is unimplemented.

## Single-binding policy model — 2026-09-06

[Decision 0035](../../../docs/decisions/0035-control-authority-model.md) implements
trusted A01–A03. Eleven cases and one binding mutation bring coverage to 110 tests/
ten controls: full mutation scope, independent read authority, conflict snapshot
disclosure, revocation cuts and same-binding replay. Denial cannot reset a cached
sequence or discard owned effects. Foreign binding does not alter the live view.

Next specify bounded effect acknowledgment and failure/unknown handling under
A05/A06 with BG-033. Native binding/revocation witnesses remain BG-032 work; the
opaque Python object is not an authenticated caller. C10/B04–B06 remain partial.

## Effect acknowledgment model — 2026-09-06

[Decision 0036](../../../docs/decisions/0036-effect-acknowledgment-model.md) adds
nine isolated ledger tests and an issued-state mutation: 119 cases/eleven controls.
Tokens and generation retirement reject repeated/stale effects; unknown retains
slots, driver loss closes mutation and acknowledgment never changes model ownership.

Next specify ledger/delivery admission integration with capacity rejection before
model effects, and exact producer-result mapping to separate lifecycle observations.
Delivery.take_effects remains unchanged, so this is not integrated execution
accounting. Native binding and driver replacement/recovery remain BG-032/BG-033 gates.

## Capacity-gated submission accounting — 2026-09-06

[Decision 0037](../../../docs/decisions/0037-accounted-delivery.md) adds nine tests
and one gate mutation: 128 cases/twelve controls. Opt-in AccountedDelivery reserves
worst-case logical credits before fresh requests, preserves retained replay and
transfers issued tokens rather than raw effects. Unknown/capture/output failures
retain explicit accounting. Capacity denial consumes no sequence or model effects.

Next specify accounting for Model.batch effects and exact producer-result mapping,
with capacity checks before observation cuts. Existing Stream/AuthorizedStream
still use baseline Delivery; a conservative pending-ack gate is not production
stop/shutdown scheduling. Native invocation/recovery remains BG-032/BG-033 work.

## Event accounting boundary — 2026-09-06

Decision 0038 characterizes twelve-effect cuts, repeated force occurrences and
background effects without a related active operation. Six tests retain these
integration constraints. BG-057 is captured for a separate event journal with
whole-cut capacity and lifecycle cause. BG-032/BG-033 retain exact native result
mapping and recovery. The submission-only ledger and native code are unchanged.

## Event journal checkpoint — 2026-09-06

Decision 0039 implements an isolated twenty-credit occurrence journal. Supplied
cause survives operation-history eviction; repeated force occurrences are distinct.
BG-057 is active for lifecycle-owned cause and Model.batch admission, with retained
observations on denial and unknown-progress policy. Native mapping remains open.

## Journal-owned lifecycle checkpoint — 2026-09-06

Decision 0040 integrates a separate JournalRuntime with existing Model hooks:
retained per-service cause, whole-cut reservation before mutation and token-only
transfer. Ten tests cover bounds, history-independent cause, restart/retry and
failure ownership. Capacity-denied observations remain caller-owned and unchanged.
Unknown currently blocks terminal observations too. BG-057 remains active with
BG-033 for bounded unknown-observation/reconciliation policy before liveness or
recovery claims; control composition and BG-032 producer mapping remain separate.

## Observation inbox checkpoint — 2026-09-06

Decision 0041 supplies four-cut trusted retention, FIFO whole-cut application and
fail-closed overflow without dropping accepted data. Unknown is not reconciled;
commands cannot pass queued observations. Nine tests and a capacity omission
control cover the bounds and failures. BG-033/BG-032 next review exact producer
reconciliation evidence; BG-057 remains active for that policy and control
composition. No native queue, progress guarantee or replacement owner is claimed.
