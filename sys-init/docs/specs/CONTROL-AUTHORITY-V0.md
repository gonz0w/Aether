# Control authority v0 — local proposal

Derived from the [producer review](../research/CONTROL-AUTHORITY-HANDOFF.md).
BG-050 proposal only: no authenticated transport, new native rights or independent
owner sign-off. Foundations O-01–05/I-01–06 and Distribution ID-01–05 remain
authoritative. This specifies sys-init consumer behavior, not a shared ABI.

## Single-binding experiment requirements

A-01. Trusted bootstrap creates exactly one connection binding, tied to the
actual endpoint pair, client generation, manager epoch and policy revision.
The binding is supplied out of band by the enforcing producer. Payload caller,
UID, service name, sequence, endpoint number or operation ID cannot establish it.
No binding means denied; no fallback to manager-wide authority. Model tests may
use opaque object identity as a trusted fixture, explicitly not authentication.

A-02. Policy assigns explicit allowed verbs and service scope to the binding.
Start checks the complete dependency closure, stop every affected service, and
shutdown the whole manager domain. Observation requires read authority for the
operation's whole scope; unknown/not-owned lookup must not disclose a private
record. Mutation authorization never implies observation permission. Revalidate
at admission, before returning cached receipts, and before emitting response bytes.
Partial authorization has no effects and consumes no mutation sequence.
In particular, an otherwise authorized request can conflict with an operation
outside its scope: the current facade includes that active snapshot in a rejected
receipt. Do not expose it merely because the requested service was authorized.
The policy adapter must suppress unauthorized details or deny disclosure. A cached
lifecycle rejection can already have consumed its sequence; output denial cannot
rewind history or turn that request into a fresh dispatch.

A-03. Revocation is monotonic for the binding lifetime. At its serialized policy
cut, discard incomplete input and unsent response bytes, close further admission
and observation, and retain receipts, effect obligations and owned services.
Do not stop services implicitly. Bytes already delivered cannot be recalled;
record that limit rather than claiming total response revocation. Reconnect must
not clear revoke, widen scope or rebuild a facade. Native buffered-channel disposal
and delayed-request ordering need a matching target witness.

A-04. First native candidate has one client and an explicit reconnect exclusion
unless the producer defines reassociation to the same live manager session.
A replacement client/session needs fresh binding authority and a decision on old
request history. Do not reset sequence or manager epoch to make a retry pass.
Manager restart remains unsupported without an authoritative identity/inventory
contract; an unknown result must not trigger automatic mutation under a new ID.

## Effect acknowledgment requirements

A-05. Separate request admission, effect transfer, effect execution, terminal
observation and reclaim. For each driver obligation identify manager epoch,
operation, service generation and effect kind. An acknowledgment must match that
obligation; stale or duplicate acknowledgments cannot complete replacement work.
Define resource bounds and exhaustion before introducing any persistent ledger.

A-06. Distinguish rejection before effects, confirmed execution and unknown
execution. Loss after invoking a native mechanism is unknown until reconciled
against producer evidence. Acknowledgment must not pretend that stop means reclaim
or that handle closure means process termination. Retain ownership until the
relevant terminal/cleanup witness. Driver death needs an explicit cleanup/recovery
owner; the current fail-closed/fatal profiles cannot imply a replacement driver.

## Required witnesses and work order

| Case | Expected result | Owner/layer |
| --- | --- | --- |
| A01 | Missing/foreign binding, payload impersonation and stale generation deny before effects | BG-050 trusted policy model; BG-032 actual producer/consumer |
| A02 | Start dependency outside grant, stop outside scope, partial shutdown and read-without-right deny without sequence consumption | BG-050 model, then native broker |
| A03 | Revoke after partial input, after dispatch and after partial reply denies future progress; owned work/history retained | BG-050 model, then broker/channel ordering witness |
| A04 | Same live authorized session preserves replay; revoked/unknown/replaced binding cannot reopen old scope | BG-050/BG-032; native reconnect excluded until accepted |
| A05 | Wrong epoch/generation/kind and duplicate acknowledgment cannot complete another effect | BG-033 driver contract and model, then native execution |
| A06 | Failure before/after invocation, driver loss and failed reclaim retain explicit unknown ownership | BG-033/BG-032 matching execution/recovery profile |

Decision 0035 implements A01–A03 as a trusted single-binding policy experiment. Keep its
fixture identity out of request/reply wire data. Record denial delivery before
adding an authority error code; do not encode private operation details merely
to report denial. Actual producer selection and native binding witnesses remain
separate acceptance work. No real endpoint is exposed by this specification.

## Implemented model subset

[Decision 0035](../decisions/0035-control-authority-model.md) defines
AuthorizedStream's exact bootstrap, checks and close-on-denial behavior. The
opaque fixture binding is compared by object identity; independent immutable
mutation/read scopes are bounded. Replays recheck admission and disclosure.
Out-of-scope conflict snapshots never leave the connection, while consumed
sequences and effects remain retained. Null-operation disclosure conservatively
requires whole-domain read scope. Revocation immediately discards unsent data and
prevents reconnect; ordinary same-binding reconnect preserves replay history.

Foreign binding leaves the legitimate connection unchanged. Denial is a fixed
local exception, not a new network response. Unguarded model APIs remain trusted
fixtures; direct object access bypasses policy. These tests do not establish a
native client generation or authenticated principal. Next specify bounded effect
execution acknowledgment (A05/A06) and matching producer acceptance before real I/O.

## Effect acknowledgment model subset

[Decision 0036](../decisions/0036-effect-acknowledgment-model.md) specifies an
isolated bounded ledger for A05/A06. Tokens distinguish operation, generation,
kind and serial; reserved/issued/unknown work and bounded terminal history stay
separate. Unknown cannot auto-retry and driver loss closes mutation. Acknowledgment
never substitutes for terminal/reclaim evidence. Delivery still transfers its
legacy effects directly; ledger admission/driver integration is the next contract,
not established by these isolated tests. Native execution/recovery remains open.

## Submission accounting integration

[Decision 0037](../decisions/0037-accounted-delivery.md) adds opt-in
AccountedDelivery. It reserves eight logical credits before fresh dispatch,
requires all previous obligations resolved, and transfers issued ledger tokens
instead of raw effects. Retained replay needs no new credits. This conservative
policy can defer fresh stop/shutdown; it is not production scheduling. Existing
Stream/AuthorizedStream still construct baseline Delivery. Accounting effects
from Model.batch and mapping producer results remain the next acceptance slice.

## Event accounting boundary

[Decision 0038](../decisions/0038-event-accounting-boundary.md) and the
[source review](../research/EVENT-ACCOUNTING-BOUNDARY.md) show why submission
accounting cannot be extended implicitly: twelve-effect cuts, repeated force and
background lifecycle cause need separate identity/capacity rules. A-05 operation
identity must represent the retained cause, not whichever operation is active.
BG-057 owns that journal experiment; the review's producer mapping table is a
consumer checklist, not an implemented decoder or a shared ABI.

## Isolated event journal

[Decision 0039](../decisions/0039-event-journal.md) adds a separate event-effect-v1
model token and twenty-credit cut reservation. It retains a supplied activation or
stop cause and identifies each occurrence independently. This is not a network
schema, automatic provenance or Model.batch integration. BG-057 owns lifecycle
cause/admission and unknown observation progress; existing submission tokens and
the authority/stream fixtures remain unchanged.

## Journal-owned lifecycle experiment

[Decision 0040](../decisions/0040-journal-runtime.md) supplies per-service cause
from the lifecycle owner and reserves each whole cut before Model mutation in
JournalRuntime. It is a separate API: start/stop return operation ID, batch returns
None, and issue_obligations transfers event journal tokens. It is not a Control,
Delivery or AuthorizedStream backend. Unknown obligations block observation cuts;
BG-057/BG-033 must define bounded reconciliation/progress before native composition.

## Observation retention experiment

[Decision 0041](../decisions/0041-observation-inbox.md) adds opt-in QueuedRuntime:
batch returns a bounded intake ID and apply_next applies one FIFO cut only when
journal admission permits. Intake does not prove effect execution, terminal state
or cleanup. Four accepted cuts are retained on overflow; the owner then closes.
Producer reconciliation remains a separate BG-033/BG-032 contract. This API is
not composed with Control or exposed as an authenticated wire protocol.

## Producer evidence qualification

[Decision 0042](../decisions/0042-reconciliation-evidence-review.md) and the
[frozen review](../research/UNKNOWN-EFFECT-RECONCILIATION.md) distinguish confirmed
ABI-6 execution/cleanup returns from later terminal or retained-wait facts. None
of EOF, timeout, EBADF or queued terminal data is a general unknown-effect receipt.
No unknown-to-terminal journal transition is accepted. BG-058 specifies bounded
confirmed-result evidence tied to the original owner/issued token/target; BG-033
and BG-032 retain authoritative reconciliation and fresh consuming witnesses.

## Confirmed-return model subset

[Decision 0043](../decisions/0043-confirmed-result-qualification.md) defines a
pure BoundCall qualifier for selected launch/stop/reclaim returns. The exact
issued obligation, original opaque owner, producer hash/profile and expected
native target must match. Returned postcondition facts do not call Model.batch or
acknowledge the journal. Unknown, force, arbitrary status/wait evidence and profile
mixing reject. BG-058 retains serialized application and actual native binding.

## Result application model subset

[Decision 0044](../decisions/0044-confirmed-result-application.md) adds one
ResultApplier per runtime. It retains BoundCall contexts, requalifies raw replies
and acknowledges under a reentry/lifecycle guard. Foreign or recreated contexts
and already-unknown results cannot apply. Acknowledgment exceptions close the owner
while preserving known terminal results and uncertain issued obligations. No
observation is synthesized; native target/terminal/cleanup mapping remains BG-058.

## Native target registry model subset

[Decision 0045](../decisions/0045-native-target-registry.md) adds an initially
empty two-slot TargetRegistry per ResultApplier. Issued launch reservations bind
expected native slot/generation to service generation. Confirmed returns control
adoption; model cleanup is still required for retirement. Status facts preserve
normal, selected #UD fault and stopped kind/detail; they do not acknowledge effects
or apply Model events. BG-058 retains actual native binding/fact application and
failed-launch cleanup; this fixture is not an authentication or recovery boundary.
