# Native pending-history review

Source review, 2026-09-06; decision 0084, BG-058 NT-06/07 and BG-057 ND-03.
[Reviewed inputs](../evidence/native-pending-history-contract-2026-09-06/reviewed-files.json)
and source copies preserve this checkpoint. This is design evidence, not a new
native execution or independent reviewer sign-off.

## Findings

| Observed boundary | Consequence for the next slice |
| --- | --- |
| [Driver::begin_sample/launched](../evidence/native-pending-history-contract-2026-09-06/source/prototypes/native-supervisor/binding.rs) checks owner, full token, actual worker, applied launch and single pending position; sample_started forbids another sample | Repeated-read denial already exists. Idempotent delivery must not be implemented as another O1/S/O2 read |
| Sampling exclusively borrows Driver and caller-owned Sample; terminal receipt sets Binding.fact while leaving pending occupied | The first raw history needs an explicit lifetime spanning replay and future consumption. Copying Fact alone or dropping the borrow is not a retirement witness |
| [Sample](../evidence/native-pending-history-contract-2026-09-06/source/prototypes/native-supervisor/sample_receipts.rs) seals a fixed three-triple array and distinguishes Live, Terminal and Failed | Only a sealed Terminal sample can be offered as terminal history. Live/error/interrupted histories remain retained but cannot become terminal facts |
| [TargetRegistry.status](../evidence/native-pending-history-contract-2026-09-06/source/prototypes/runtime_model/target_registry.py) validates producer/profile/target/kind/result and projects service identity | Its synthetic input and event tuple do not preserve the native O1/S/O2 raw receipt or provide a native provenance constructor |
| [LifecycleDriver.terminal_reply](../evidence/native-pending-history-contract-2026-09-06/source/prototypes/runtime_model/lifecycle_driver.py) compares projected events and can replace an existing launched event; deliver clears non-cleanup events after batch | Do not import tuple equality or event clearing as native history acceptance. Raw conflict retention and launched/terminal ordering need explicit coordinator rules |
| [EventJournal/JournalRuntime](../evidence/native-pending-history-contract-2026-09-06/source/prototypes/runtime_model/event_journal.py) reserve, begin, capture and apply through a separate logical cut; errors can close the owner | Empty inbox, accepted offer, or matching token does not establish applied journal acceptance or permission to reclaim/retire |
| [Native Route](../evidence/native-pending-history-contract-2026-09-06/source/prototypes/native-supervisor/attempt.rs) transfers an Event containing generation and kind | It is insufficient for equal-generation cross-service replay. Its current witnesses remain valid for their narrower scope |

The pinned terminal-stability invariant and one-shot sampling policy supply no
ordinary second contradictory native sample for the same retained terminal worker.
Conflict tests must therefore label their candidate as synthetic; a passing
comparison cannot claim actual contradictory kernel output. A diagnostic candidate
must never replace the first fact or confer additional native authority.

## Choice and alternatives

Select a private bound-history comparison boundary and explicit fixed storage
accounting before journal integration. Reuse the current owner/context, full issued
token and actual Worker association. Keep one global sampling/effect reservation;
do not expand to two simultaneous terminal positions merely because two attempts
exist. An exact duplicate offers retained evidence without another read. One
reserved diagnostic slot captures a same-binding conflict and closes admission.

Rejected shortcuts: generation-only equality loses service/occurrence identity;
re-reading a duplicate violates the one-shot bound; overwriting the first fact
loses evidence; unbounded conflicting history violates resource limits; clearing
pending after inbox transfer invents journal acceptance. Moving the whole model
into the 4 KiB fixture would combine unqualified identity, delivery and retirement
changes. The new [local contract](../specs/NATIVE-PENDING-HISTORY-V0.md) separates
these obligations without choosing a production language or shared wire API.

## Follow-ons before closing this review

BG-058 owns PH-01–06 comparison, provenance, conflict and two-attempt capacity
qualification. First implement PH-01/02 with exact owner/token/worker denial and
duplicate no-op controls, then PH-03/04 conflict retention and PH-05 capacity.
Every native change needs all 143 existing oracles plus named new cases under
the unchanged 4 KiB profile. Split fixtures when needed; host-only logic is not
native integration. BG-057 owns PH-07 named whole-cut acknowledgment, application
failure, ordering and retirement; no clearing/replenishment API is accepted now.
BG-033 retains unknown-owner recovery. Additional O1 malformed injections and full
launch composition remain under BG-058. No new Aether operation is justified by
this review. These are native ABI-6 rules; POSIX/BSD/illumos/Linux adapter choices
remain separate, and no Linux-only dependency is introduced.
