# Native whole-cut acceptance review

BG-057 PH-07, decision 0156, 2026-09-07. Repository source research, not a new
runtime witness. [Frozen inputs](../evidence/native-cut-contract-2026-09-07/reviewed-files.json)
retain this checkpoint. Source links below describe the inspected implementations.

| Source boundary | Finding and consequence |
| --- | --- |
| [History and Sampling](../../prototypes/native-supervisor/binding.rs) | Closure preserves storage, and terminal sampling occupies the global pending position. No journal application or history retirement method exists. A new coordinator must authorize any change to that position while keeping the original sample. |
| [Private views](../../prototypes/native-supervisor/pending_history.rs) | Duplicate compares retained identity/content. It is neither journal reservation nor application acknowledgment. Closed inspection grants no replay authority. |
| [RoutedAttempt::deliver](../../prototypes/native-supervisor/attempt.rs) | Moving an Event to an empty Option clears local pending and marks outcome_delivered. This is its existing narrow route contract, not whole-cut application. Event carries generation/kind without full owner/token/worker identity. |
| [LifecycleDriver::terminal_reply/deliver](../../prototypes/runtime_model/lifecycle_driver.py) | Terminal can replace a pending launched event; deliver calls runtime.batch and clears non-cleanup events. This must not become the new native acceptance adapter unchanged. |
| [QueuedRuntime::batch/apply_next](../../prototypes/runtime_model/queued_runtime.py) | batch returns an intake serial before application; apply_next removes the retained cut after its superclass returns. Intake serial and empty inbox are not a bound application receipt. |
| [JournalRuntime::_run](../../prototypes/runtime_model/journal_runtime.py) | The trusted model reserves twenty effect credits before mutation, captures generated effects afterward, and closes on an exception with a retained ticket. It does not return the exact native observation cut or a receipt binding all applied members. |
| [Model::batch](../../prototypes/runtime_model/model.py) | Terminal events sort before launched. Stale epoch/generation can be recorded and skipped while batch returns. A successful call alone cannot certify that a particular native transition occurred. |
| [EventJournal::acknowledge](../../prototypes/runtime_model/event_journal.py) | Acknowledgment concerns an issued effect outcome; its 64-entry history can evict old outcomes. It cannot authorize clearing native observation history or replay an evicted observation receipt. |

Choose a separate private CutCoordinator contract. It must preserve complete
observation membership, distinguish application from intake/effect execution,
and check expected lifecycle transitions. For this first bounded profile, require
Launched, Terminal and Cleaned for one attempt in separate ordered cuts. Two
services may share a cut, but no attempt contributes two phases to one cut. This
avoids depending on existing sort/replacement behavior without rewriting it.

Retirement means ending live attempt eligibility after positively known cleanup
and matching applied Cleaned. It does not mean erasing samples, returning issuance
credits, resetting generations or reconstructing a closed owner. Keep tombstones
for this two-attempt owner. Six retained cut records bound three phase observations
per attempt; cancellations may consume that capacity and deny later progress.
This is a declared bounded experiment, not a production reuse policy.

Alternatives rejected: unbound boolean acknowledgment; accepting queue insertion
as application; allowing terminal to replace launch; rebuilding identity from a
hash/generation; replaying after uncertain application; importing the model's
64-entry effect eviction as native sample retention. Each loses either provenance,
ordering or retained uncertainty. No POSIX, BSD, illumos or Linux-specific facility
is needed for this local logical boundary; real adapters remain separately scoped.

Follow-ons captured before this review closes: BG-059 qualifies the pure bounded
coordinator with semantic controls; BG-057 retains actual lifecycle/journal and
native integration. BG-060 owns sustained history capacity/reuse design; BG-033
owns uncertain application/replacement-owner recovery. BG-058 full launch
composition remains required before an end-to-end lifecycle claim. The existing
185-case native witness and its producer source-closure limitation are unchanged.
