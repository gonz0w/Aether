# 0093 — Native history capacity

Accepted bounded experiment, 2026-09-06; BG-058 PH-05 after decision 0092.

Introduce a private History owner owning Driver and exactly
[Sample; 2] primary stores plus one diagnostic Sample and a diagnostic attempt
index. Sampling borrows these stores; dropping a Sampling/Pending handle never
recycles them. Keep Driver.pending as the single global position. No allocation,
new native operation, unsafe code or producer/standards pin is introduced.

Use the pinned service worker in silent mode for attempt 0 and the same worker in terminal-exit17 mode for attempt 1. Capture Live once in primary 0, allowing the other
already-admitted attempt its Terminal sample. Retain primary 0 even after its
worker is explicitly stopped later. Deny index 2 and resampling while Terminal
occupies pending, with no additional reads. Conflict into the pre-reserved third
store closes admission; a second offer cannot produce again. The fixed capacity
is nine triples; this legal scenario fills seven (1 Live + 3 Terminal + 3
synthetic diagnostic), not two terminal histories.

Positive completes at 100/3 after known fixture cleanup/reuse. Losing Live history,
recycling its primary and recycling the diagnostic must reject at 1058/0, 1059/0
and 1060/0 respectively. Use the actual producer-entry counter. Four new cases
plus all 162 prior ABI-15 cases must execute on frozen inputs. Recheck legacy
151 image bytes and all nine local gates. Record measurements and every attempt.
PH-06 broader sealing and BG-057 PH-07 retirement remain separate; neither owner
recovery nor a general admission API follows from this fixture-seeded workload.

Preflight review: the first borrowed-Driver layout fits but leaves Driver and raw
storage lifetimes separate. Before native execution, make History own Driver by
value alongside the three stores; temporary sessions borrow its fields. Retain
the first four build results and qualify this stronger ownership layout instead.

The initial full run passed 162 prior cases, then the capacity positive reached
805/0: Adapter uses c001 for both slots, so service-worker mode exit waits rather
than exits. Correct both terminal roles to its existing terminal-exit17 mode.
Retain the failed attempt; no native timeout is accepted as a semantic result.

## Results and remaining scope

Decision 0093 passes all 166 native cases: 162 prior cases and four capacity
probes. History owns Driver, two primary Sample stores and one diagnostic Sample.
Temporary Sampling/Pending borrows cannot outlive this owner, and dropping those
handles does not replenish storage. The diagnostic retains its attempt index;
Driver retains the original token, worker/generation and reader association.

The native positive retains a Live observation in attempt 0, then a Terminal
history in attempt 1. Live releases the global position without freeing its
history; Terminal keeps pending at 1. Resampling and index 2 deny without extra
sampling returns. A synthetic conflict occupies the one reserved diagnostic and
closes admission; another offer cannot invoke its producer. Both primaries and
resources remain intact, including the old Live history after explicit worker
stop. Cleanup and ordinary reuse finish at 100/3. Losing Live history, recycling
a primary and recycling the diagnostic reject exactly at 1058/0, 1059/0 and 1060/0.

The owner provides nine fixed triple slots; this legal scenario fills seven
(1 Live + 3 Terminal + 3 synthetic diagnostic). It does not claim two simultaneous
terminal facts. Separate x86-64 LLVM constant-return inspection measures History
at 760 bytes: Driver 336, three Samples at 136 each, plus diagnostic association.
Raw payload layout is 24 bytes. These are target type-layout measurements, not
peak stack usage or a production memory budget; transient values remain separate.

All 151 ABI-6 images rebuild byte-identically. No producer, ABI bound, shared
standard pin, syscall, heap allocation or sibling source changes. PH-05's bounded
Live/Terminal/conflict capacity slice now has native evidence. Next BG-058 PH-06:
qualify denial of Live/Failed/Interrupted promotion while retaining histories,
issuance, pending state and resource ownership in this container. BG-057 PH-07
whole-cut retirement and BG-033 recovery remain open. Full launch composition,
all failure combinations and retirement are not established by fixture seeding.

The corrected complete native run passes: 502 commands, 421 frozen inputs unchanged,
maximum image 7248 bytes under the unchanged 8192 limit. All 162 of 162
prior ABI-15 images remain identical; every case has fresh execution. Both four-link
preflights are retained; the owned-Driver layout needed the documented fixture-mode correction. Nine host
wrapper cases and 42 harness tests pass. The initial failure and focused correction are retained; no oracle was weakened.

## Final validation

All nine repository gates pass in `out/checks/run-7h_vacv9`, including the offline audit of 2,844 recorded native outcomes across 49 bundles. These host checks supplement the fresh 166-case native run. Final evidence is retained under `docs/evidence/native-history-capacity-2026-09-06/`.
