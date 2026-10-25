# Native driver binding v0

Local experimental contract, 2026-09-06; decision 0065, BG-058/BG-057 ND-01.
Specified contract; decision 0066 implements only the initial admission subset.
This is a private trusted-owner boundary, not a wire
format, kernel ABI, authentication service or production language decision.

## Basis and scope

The [integration review](../research/NATIVE-DRIVER-INTEGRATION-REVIEW.md) found
that native events carry only generation/kind. The
[model driver](../../prototypes/runtime_model/lifecycle_driver.py) already reserves
issued launches before acquisition and qualifies original calls through
[BoundCall](../../prototypes/runtime_model/confirmed_result.py) and
[TargetRegistry](../../prototypes/runtime_model/target_registry.py).
This contract specifies the corresponding native ownership boundary; it does not
change those model interfaces or claim they execute native calls.

The initial implementation profile is one trusted live owner, one fixed producer
digest and `aether-init-abi6` profile, one immutable epoch/revision and one or two
configured services. Kernel enforcement remains authoritative. Code able to bypass
the driver and invoke Adapter directly is inside the trusted computing base.
Names, hashes, token bytes and predicted handle values do not grant authority.
No concurrent calls, owner restart, inherited nonempty inventory, configuration
replacement or force operation is supported by this initial profile.

## Binding identity

Preserve the existing ten-element `event-effect-v1` token exactly:

```
(schema, epoch, revision, cut, index, service, generation, action, cause, operation)
```

Its scalar validation and issued membership come from
[EventJournal](../../prototypes/runtime_model/event_journal.py) and
[EffectLedger](../../prototypes/runtime_model/effect_ledger.py): epoch/revision are
nonempty strings up to 64 characters; configured service names match
`[a-z][a-z0-9_-]{0,31}`; cut, generation and operation are integers 1 through
2^64−1; index is an integer 0 through 19. Boolean values are not integer IDs.
Action for admission is `launch`; cause remains the exact issued activation/stop
cause and operation, not a new driver-generated provenance claim. Validate the
whole token, including exact scalar types, against its retained issuance entry.
Do not reduce identity to service/generation or cut/index alone.

The driver context additionally owns the exact producer digest (64 lowercase hex
characters), profile and a non-rebindable live owner reference. Owner identity is
trusted context, never supplied by an event payload. A native fixture may represent
configured strings as indexes only through a fixed, injective, retained table;
truncation, hashing as equality or remapping indexes during the run is forbidden.
Epoch, service generation, native target generation and channel generation remain
separate. The same predicted target can recur after a rejected launch because
that rejection does not consume a target generation.

An attempt record retains its full launch token, owner/context binding, selected
native slot and expected target, phase, optional acquired endpoints and admitted
worker, exact received result or unknown state, and pending route evidence. The
expected target is a reservation; only a matching successful native launch return
establishes an admitted worker. Retain the actual resource wrappers, not just
their diagnostic numbers. A later stop/reclaim needs its own issued occurrence
bound to this same attempt; retaining the launch token does not authorize it.

## Bounds and issuance lifetime

| Resource | Initial bound and exhaustion behavior |
| --- | --- |
| Live owner/context | One; closure is permanent for that context. No reconstruction with reused identity |
| Services and attempt records | At most two; at most one unresolved attempt per service and one reservation per native slot |
| Channel creation | One outstanding invocation; reserve the attempt before calling the factory |
| Native target slots/generations | Slots 0–1 and admitted generations 1–3 in the selected model/producer profile; never wrap |
| Channel slots/generations | Producer-selected slots 0–1 and generations 1–3; validate received pair, never infer which free slot was chosen |
| Pending events | One per retained attempt; ND-03 owns eventual whole-cut acceptance |
| Initial fixture issuance table | At most 20 exact entries for one predetermined cut, with retained consumed state until fixture termination |

The 20-entry fixture limit follows the model journal's per-cut bound; it is not
permission to keep issuing cuts without accounting. The first binding fixture
must label its table as trusted synthetic issuance. It does not execute the
journal, mint new obligations from caller input or prove journal integration.
No table eviction/reset or cross-cut replenishment is allowed in this first slice.
The table retains consumed/failed/unknown entries so a duplicate cannot regain
admission after local cleanup. Counters use checked increment and deny exhaustion
before acquisition. Owner restart and epoch allocation remain BG-033; an arbitrary
new epoch string cannot establish that old resources disappeared.

## Admission and result transitions

1. Validate live context, producer/profile, exact issued launch token, configured
   service and selected native slot. Confirm service generation/launch intent
   against the trusted issuer. Check attempt capacity, no duplicate service/slot,
   no outstanding creation and remaining native generation capacity. Preflight
   denial performs no factory call and changes no pending event or ownership.
2. Reserve the attempt, target slot and single creation position together. Bind
   the original token to this reservation before invoking channel creation. Mark
   invocation started before crossing the syscall boundary, preventing re-entry
   or duplicate invocation even while the journal obligation remains issued.
3. On received channel success, retain both returned endpoints immediately in the
   reserved attempt before fallible validation or launch binding. Validate their
   pair and next channel generation against the selected producer. Mismatch closes
   the owner and retains all received references/raw result for diagnosis; it is
   not evidence that either reference may safely be discarded or reused.
4. On a selected, confirmed pre-effect creation rejection, retain exact operation
   and error with the unacquired attempt and empty inventory. Release the creation
   position and provisional target reservation; do not advance native target or
   channel generations. Do not emit Cleaned or reopen the issued occurrence.
   ND-04 supplies its lifecycle translation; until then this outcome is retained.
5. Bind the launch invocation to the same context/token, expected target and
   retained writer. Prevent duplicate invocation. On matching successful return,
   retain Worker, record writer transfer and advance that target's admitted
   generation exactly once. Keep reader ownership. On a selected confirmed launch
   rejection, retain both endpoints and exact error, release the provisional target
   slot and leave target generation unchanged. The attempt remains unresolved.
6. An unexpected return, lost reply or failure after invocation begins closes new
   admission and retains the invocation, reservation, any acquired resources and
   raw available result. Unknown is not pre-effect rejection, success or cleanup.
   Closing admission must not erase diagnostic ownership. This contract does not
   authorize automatic retry, native replay or an unqualified cleanup procedure.

Preflight invalid input and a mismatched result received for an already invoked
operation have different dispositions: the former denies without mutation; the
latter may represent effects and closes the owner with retained state. Local guard
errors keep their local origin. Do not manufacture a native errno to represent
token validation or pretend an Adapter ownership guard executed a kernel call.

## Routed evidence and retirement boundary

An event submitted to the future consumer must resolve to a retained attempt and
include or carry a retained reference to its exact context and launch identity.
For admitted observations it must also bind the actual worker. A received effect
result carries its own issued operation token/action. A terminal observation is
not a stop/reclaim result and must not acknowledge either operation implicitly.
The consumer checks live context, full binding, phase and event category before
accepting evidence; a self-consistent payload alone is insufficient.

Reject cross-service, wrong epoch/revision/producer/profile/occurrence/action,
unbound target and retired identity without replacing pending evidence or changing
resource ownership. Equal generations never override another service's binding.
ND-02 separately qualifies terminal kind/detail; `Terminal(144)` alone must not
be projected as a stopped lifecycle event by this binding implementation.

Retain pending events until the explicitly named consumer accepts them. A fixture
inbox may demonstrate transfer only. ND-03 must specify journal cut application
and actual retirement before exposing either as an implemented operation. The
initial ND-01 fixture has no public `retire`, attempt replacement or replay-history
reset operation. Local resource cleanup at fixture termination does not permit
another launch under the same token. Cancellation retains identity, resources and
pending history and cannot restore consumed admission.

## Acceptance plan

These are required future tests, not current passing cases. Record exact native
assertion markers and build inputs in the implementation decision before execution.

| ID | Required oracle |
| --- | --- |
| NB-01 | Two distinct services at generation one bind distinct issued occurrences and slots; correct actual acquisition/launch succeeds and retains the matching resources |
| NB-02 | Wrong owner, epoch, revision, producer/profile, action/cause/operation, cut/index, unknown service and malformed scalar types deny before acquisition; factory invocation count and full ownership snapshot remain unchanged |
| NB-03 | Duplicate occurrence, same-service second attempt, reserved slot, third attempt and pending creation deny without consuming endpoints or changing the first reservation |
| NB-04 | Matching channel success retains the pair before an injected later binding failure; owner closes, endpoints/reservation remain recorded and no launch occurs |
| NB-05 | Confirmed creation failure retains empty-inventory outcome; confirmed launch failure retains both endpoints and leaves target generation unchanged; neither permits same-token retry |
| NB-06 | An admitted return binds the actual worker exactly once; wrong/unsupported post-call return retains unresolved state and closes new admission |
| NB-07 | Swap equal-generation events between the two services, substitute occurrence or target, and replay a consumed identity; reject while retaining the original pending event/resources |
| NB-08 | Exhaust identity/native generation/table bounds and deny before effects; consumed entries survive cleanup until fixture end, with no reset path |
| NB-09 | Missing channel/launch reply retains outstanding ownership and denies additional invocation; no fabricated terminal, acknowledgment or Cleaned |

At least two semantic omission controls must independently demonstrate that the
cross-service binding check (NB-07) and reservation-before-acquisition guard
(NB-03/04) affect the observed result. A generic timeout/build failure is not an
accepted negative oracle. Model tests can exercise injected replies and scalar
validation; native tests must consume pinned producer returns for actual resource
ownership claims. Do not claim a native wrong-owner transport test from a trusted
fixture's local context substitution.

## Implementation order and standards

First implement the bounded binding fixture and its identity/admission controls,
keeping synthetic issuance explicitly separate from runtime journal execution.
ND-02 then supplies exact terminal qualification; ND-03 supplies real cut acceptance
and retirement; ND-04/05 retain error and policy composition. BG-058/BG-057 remain
active. Native changes require fresh target evidence and all development checks.

Foundations O-01/O-03/O-04, I-01/I-03–06 and E-01–08 apply under the unchanged
[adoption](../STANDARDS.md). Shared rules remain in Aether-standards. This local
contract adds no dependency, unsafe primitive, output change, distribution/session
API or persistent format. No POSIX/BSD/illumos/Linux process mapping is selected.
The 4 KiB native fixture limit remains an experiment constraint, not a production
budget. If the selected case cannot fit, split independent probes without weakening
identity or ownership oracles and retain unsuccessful attempts.

## Initial implementation scope — decision 0066

`prototypes/native-supervisor/binding.rs` implements two immutable synthetic issued
tokens and local owner binding, reservation before acquisition, admitted resource
retention and a read-only launched-event qualification predicate. See
[decision 0066](../decisions/0066-native-binding-admission.md) for exact witnesses.
This is NB-01 and selected NB-02/03/07 coverage, not the complete contract.
There is no pending-event queue, predicted-target validation or error-result
classification here. Typed tokens exclude parser/type tests. NB-04–06/08/09 and
remaining NB-02/03/07 cases stay open; next is NB-04 post-acquisition failure
retention with a semantic resource-loss control. The full contract's selected
rejection transitions and later ND-02–05 remain required before broader claims.

## Post-acquisition retention scope — decision 0067

[Decision 0067](../decisions/0067-native-binding-failure-retention.md) adds the
NB-04 injected local binding-completion failure after a real channel return.
Both endpoints and original reservation remain owned; a separate local cause
closes admission. A writer-loss control distinguishes retention from forgetting
the resource. This is not malformed producer-reply qualification or complete
channel-generation validation. Earlier "next" statements are historical; next
is NB-05 selected creation/launch rejection with consumed identity retained.
Remaining ND-01 and ND-02–05 gates are unchanged.

## Selected busy returns — decision 0068

[Decision 0068](../decisions/0068-native-binding-busy-rejection.md) implements only
received creation 0x24000/16 and launch 0x23001/16. The provisional slot claim is
released while the original issuance/error remain retained; creation has empty
inventory and clears its creation position, launch keeps both endpoints. A
different issued service may use the slot after explicit fixture disposal.

The two probes deliberately occupy resources outside the driver after constructing
it in an empty domain. That inventoried, trusted interference is test-only; it
does not authorize production adoption of a nonempty or unknown inventory. No
other error outcome, target-generation prediction or journal cleanup is accepted
by these probes. Next NB-06 binds the expected native target to the received
launch result; remaining NB/ND requirements stay open. Earlier next-work notes
describe their own checkpoints.

## Expected target binding — decision 0069

[Decision 0069](../decisions/0069-native-expected-target.md) reserves the expected
worker identity from the native slot generation, retains the actual launch return
before matching, and advances the counter only on a match. Wrong-slot/generation
expectations are injected only in the tests. Their mismatch closes the driver
with actual worker/reader retained, writer transferred and no invented errno.

Known fixture admissions are explicitly accounted before subsequent reservation;
there is no nonempty-domain recovery or public history-import API. Input token
borrowing preserves the full ten-field comparison. Native generation remains
distinct from service generation. Next: NB-08 bounded exhaustion with denial before
effects, then NB-09 lost-reply ownership; other errors and ND-02–05 remain open.
This is a bounded NB-06 slice, not arbitrary producer-reply validation.

## Native generation exhaustion — decision 0070

[Decision 0070](../decisions/0070-native-generation-exhaustion.md) supplies the
native-generation part of NB-08. Three actual slot-zero admissions are explicitly
accounted by the fixture. Repeated exhausted-slot denial leaves the issued token,
attempt inventory and acquisition count unchanged; the same token can reserve
slot one and acquire a channel without advancing its native generation.

The guard and token-consumption omission controls distinguish correct denial from
false admission or state mutation. This is not general 64-bit/cut/history exhaustion
or journal replenishment coverage. Next NB-09 requires a bounded invocation/receipt
ownership design; direct calls must not be reinterpreted as a tested lossy transport.
Other error, terminal, cut and recovery gates remain open.

## Receipt ownership design — decision 0071

Decision 0071 (`docs/decisions/0071-native-receipt-ownership.md`) specifies
a single driver-owned invocation/receipt position and non-repeatable phases.
Next, BG-058/BG-057 implement IR-01–04 actual channel-return retention and
local application backpressure; launch transfer IR-05–06 and synthetic absence
IR-07 follow. NB-09 is not yet qualified. ND-02–05 and BG-033 remain open.
The 75-case decision 0070 witness remains unchanged; no native execution is added.
Foundations O-01/O-03/O-04, I-01/I-03–06 and E-01–08 retain their existing scope;
no shared pin, API, exception, output or unsafe primitive changes. Review evidence
is `docs/evidence/native-receipt-contract-2026-09-06/`.

## Channel implementation — decision 0072

[Decision 0072](../decisions/0072-native-channel-receipt.md) implements IR-01–04
for channel creation: explicit phases, retained native pair/error and shared
start/launch guards. Local delivery checks the original owner/token/operation/target.
Three positive and two semantic omission probes pass in a fresh 80-case witness.
The pause is local after a real return; closure is injected in trusted fixture
state. No missing kernel reply, public cancellation or full NB-09 is demonstrated.
Earlier future-work wording describes the design checkpoint. IR-05–06 launch
receipt transfer is next, followed by IR-07 synthetic absence; other NB/ND and
BG-033 recovery remain open. See the decision for exact tests and size limits.

## Launch receipt implementation — decision 0073

[Decision 0073](../decisions/0073-native-launch-receipt.md) implements IR-05–06:
launch success retains actual worker/reader and records writer transfer before
application; generation and launched-event qualification wait for matching
application. Closure keeps the pending receipt. Two positive and two semantic
omission probes pass in a fresh 84-case witness. This is local retention after a
real synchronous return, not a lost kernel reply, public cancel API or recovery.
IR-07 synthetic absence is next; remaining NB/ND and BG-033 work stays open.
Earlier future-work statements describe their own checkpoints.

## Synthetic absence — decision 0074

[Decision 0074](../decisions/0074-native-synthetic-missing-return.md) executes IR-07
as a synthetic schedule in the native fixture: real start guard, omitted syscall,
retained Started/pending state and closed admission without invented result/error.
Two positives and three controls pass within a fresh 89-case witness. This does
not lose an actual kernel reply or authorize unknown-transfer cleanup.
The [binding acceptance review](../research/NATIVE-BINDING-ACCEPTANCE-REVIEW.md)
keeps remaining NB gaps explicit. Next is ND-02 terminal-kind contract work;
ND-03–05 and BG-033 remain open. Earlier next-work wording is historical.

## Terminal evidence contract — decision 0075

Decision 0075 specifies exact terminal kind/result and bounded observe/status/observe coherence. Next: BG-058 NT-01–02 actual colliding terminal-kind probes, then NT-03–07 bound retention/identity. ND-01 gaps, ND-03–05 and BG-033 remain open. No native source or shared pin changes; the 89-case witness remains unchanged.

The local contract is `docs/specs/NATIVE-TERMINAL-EVIDENCE-V0.md`; source review
and validation are retained in `docs/evidence/native-terminal-contract-2026-09-06/`.
Foundations O-01/O-03/O-04, I-01/I-03–06 and E-01–08 apply in unchanged scope;
no new exception, dependency, output, unsafe primitive or shared ABI is adopted.
