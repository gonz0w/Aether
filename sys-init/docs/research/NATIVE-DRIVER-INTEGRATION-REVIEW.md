# Native route and model driver integration review

Reviewed 2026-09-06 under BG-058/BG-057. The native resource and event experiments
are ready to inform a driver contract. They are not yet a native implementation
of `LifecycleDriver`. First bind issued operations to retained attempts and native
targets; then qualify terminal evidence before integrating journal delivery.

This is a local source/evidence review, with no independent reviewer sign-off.
[Reviewed source identities](../evidence/native-driver-review-2026-09-06/reviewed-files.json)
and copies retain the exact comparison inputs. The current target witness remains
[decision 0063](../decisions/0063-native-routed-partial-cleanup.md): 57 cases,
177 unchanged frozen inputs. The catalog's 702 outcomes across 30 bundles include
historical repeated cases; they are not 702 distinct behaviors or a conformance score.

## Evidence crosswalk

| Boundary | Model implementation and tests | Native implementation and evidence | Integration gap |
| --- | --- | --- | --- |
| Admission and acquisition | `reserve_channel` reserves an issued service launch, target slot and attempt before the caller creates a channel; one creation pending, at most two attempts | `Attempt::acquire` obtains an actual channel and retains endpoints; decisions 0051–0052 cover selected acquisition/launch failures | No journal-issued service reservation before native acquisition |
| Operation identity | `EventJournal` token includes owner epoch, definition revision, cut/index occurrence, service, generation, action and cause; `ResultApplier` binds the original token, producer and native target | `Event` contains only generation and kind; ownership is the trusted Rust object and Adapter context | Equal generations from different services or activations cannot be distinguished by the event value |
| Received result | `BoundCall` and `ResultApplier` qualify and acknowledge the retained issued call; lifecycle observation remains separate | Actual Adapter launch/stop/reclaim returns preserve operation and errno; route emits only the selected busy-launch rejection | No native journal acknowledgment or complete selected-error translation |
| Terminal evidence | `TargetRegistry::status` validates the retained target and 0x20001 status kind/result, then projects normal, fault or stopped | Route observes 0x25001 and emits `Terminal(u64)` from the flattened terminal value; decisions 0057/0061 exercise values 18/144 | Observation value alone does not supply the model's native kind/detail contract |
| Delivery | `LifecycleDriver::deliver` calls `JournalRuntime.batch` with all pending events, bounded by two attempts; rejection retains pending state | One caller-owned `Option<Event>` accepts an in-process transfer; full inbox retains both values | Empty inbox is not successful journal reservation, capture or application |
| Cleanup | Issued matching reclaim plus qualified resource completion gates Cleaned; successful model delivery retires admitted registry entry and removes attempt | Reader/writer/worker/wait ownership clears only on successful steps; delivered outcome gates cleanup; decisions 0062/0063 retain failures without Cleaned | No issued reclaim binding, applied Cleaned acknowledgment or coordinator-owned retirement |
| Replacement and policy | Model delivers cleanup before later timed retry; readiness, stop and force coordination remain outside this driver | Decision 0059 admits one explicit busy-failure replacement; 0060–0063 preserve cancellation; `service.rs` separately exercises readiness/dependency policy | Separate fixtures do not demonstrate a composed service scheduler or operator transport |

Source references: [native Attempt/route](../../prototypes/native-supervisor/attempt.rs),
[Adapter](../../prototypes/native-supervisor/adapter.rs),
[separate service fixture](../../prototypes/native-supervisor/service.rs),
[LifecycleDriver](../../prototypes/runtime_model/lifecycle_driver.py),
[TargetRegistry](../../prototypes/runtime_model/target_registry.py),
[ResultApplier](../../prototypes/runtime_model/result_applier.py),
[BoundCall](../../prototypes/runtime_model/confirmed_result.py),
[EventJournal](../../prototypes/runtime_model/event_journal.py),
[JournalRuntime](../../prototypes/runtime_model/journal_runtime.py).
The [model tests](../../tests/test_runtime_model.py), particularly
`ChannelAcquisitionTests` and `LifecycleDriverTests`, distinguish synthetic
reservation, pending delivery, wrong owner, conflicting terminal and wait cleanup.
The [native runner](../../tests/native-init.py) and
[coverage catalog](../native-coverage.json) identify actual target oracles.

## Prioritized follow-ons

These are stable review IDs owned by existing active stories, not completed work.
They are recorded in those stories before closing this review.

1. **ND-01 — Issued identity and admission (BG-058, with BG-057).** Specify a
   private, bounded native driver binding contract. Separate trusted live owner,
   producer/profile, service, revision, generation, occurrence and target identity.
   Reserve ownership before acquisition; retain acquired resources on later failure.
   Define what happens when owner/identity counters or capacity exhaust. No digest,
   service name or user-space token grants kernel authority. First acceptance must
   reject same-generation cross-service evidence, wrong occurrence/action/profile,
   wrong owner/revision, unissued calls and retired/reused targets without effects
   or resource loss. Reuse existing logical token semantics; do not create a new
   external wire ABI or silently change model tokens.
2. **ND-02 — Exact terminal qualification (BG-058).** Map the selected producer's
   status kind/result and observation revision into retained target evidence.
   Normal exit can have the same numeric result as fault or stopped; do not infer
   kind from 135/144. Specify how an additional status read is tied to the still
   retained target, plus failure/interruption behavior. Test colliding numeric
   results with distinct kinds, stale target, malformed kind/detail and conflicting
   pending history. Confirm the mapping against the frozen producer before coding;
   this review identifies a consumer gap, not a demonstrated missing kernel API.
3. **ND-03 — Whole-cut acceptance and retirement (BG-057, with BG-058).** Define
   retention through journal reservation/capture/application and post-application
   failure, with explicit acknowledgment and bounded outstanding state. Reclaim
   must use the matching issued obligation. After applied Cleaned, retire the old
   binding; test full journal, two-service cuts, replay and late old-generation
   events. `eligible()` alone does not retire anything. Source inspection also
   finds that another observe after terminal transfer can queue Terminal again,
   and cleanup after Cleaned transfer can queue Cleaned again. These calls are
   outside the current fixture sequence; specify idempotence/denial at the
   coordinator boundary before allowing general callers. This review adds no
   native replay witness or claim that the model eliminates every replay.
4. **ND-04 — Selected errors and unknown ownership (BG-058; recovery BG-033).**
   Compose channel pre-effect rejections, launch errors and partial cleanup under
   the bound operation. Keep local guard denial distinct from actual syscall
   rejection. Lost/ambiguous results retain obligations; the model's closed owner
   and native fixture accounting are not reconciliation. Use the existing
   [recovery research](UNKNOWN-EFFECT-RECONCILIATION.md) before proposing mechanisms.
5. **ND-05 — Policy composition (BG-040/BG-057).** After ND-01–04, connect readiness,
   dependency loss, cancellation and bounded timed retry to the same owner.
   Require an end-to-end target sequence rather than combining separate fixture
   passes. External control authority, general sessions and production scheduling
   retain their existing acceptance gates.

The next deliverable is the ND-01 local contract and test plan, followed by a
bounded model/fixture implementation with semantic identity controls and a fresh
consuming target witness for any native change. ND-02 must precede interpreting
native terminal events as model lifecycle events. ND-03 must precede calling inbox
transfer journal acceptance. Local contract work is unblocked; this review supplies
no basis for a new Aether kernel backlog request.

## Alternatives, portability and review limits

Wiring the present inbox directly to the model would leave identity and terminal
classification unresolved. Adding more isolated policy fixtures first would not
close that boundary. Porting the entire Python model at once would combine too
many ownership, scheduling and evidence changes. The selected sequence keeps each
claim testable without choosing the production implementation language.

The comparison concerns the pinned Aether ABI-6 experiment. It imports no Linux
process, pidfd, cgroup or signal assumptions. POSIX/BSD/illumos/Linux adapter
selection remains separate research; these native handles and operations are not
POSIX processes, file descriptors or wait semantics. The 4 KiB client limit is an
experiment bound, not a production memory or performance budget. No new dependency,
unsafe operation, CLI, descriptor, persistent format or shared interface is added.

Foundations O-01/O-03/O-04, I-01/I-03–06 and E-01–08 govern the review's scope,
identity distinctions, bounds and evidence claims. Distribution ID clauses remain
unimplemented session/authentication requirements, not guarantees supplied by
driver identity. Shared rules stay in the unchanged offline releases; exact local
binding algorithms belong here. BG-056 retains broader quality adoption and
BG-054 retains cross-platform/extended testing.
