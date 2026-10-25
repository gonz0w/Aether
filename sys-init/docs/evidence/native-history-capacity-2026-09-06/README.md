# Native history capacity evidence

2026-09-06; decision 0093.

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

`preflight/` retains the earlier borrowed-Driver build; `preflight-owned/` retains
the owned layout before the mode correction. `attempt-1/` retains the failed full
run, and `correction/` retains four passing focused cases. `witness/` holds the
corrected final source and execution. `layout/` is a separate private-source measurement that adds
exported constant size functions and emits target LLVM IR; it is not native runtime
source or a stack high-water measurement. `legacy-build/` and `legacy-build-final/` hold initial and corrected-source 151 identical
ABI-6 rebuilds. `witness/` retains the full fresh 166-case run, source/producer/
worker pins, commands, raw supervisors/envelopes and serial/QEMU logs, with its
own catalog-pinned manifest. ISO identities are recorded; private ISOs are not
archived. `validation/` and `adoption/` retain full checks and final records. The
root manifest seals this bundle; historical evidence and sibling sources remain
unchanged.

All nine repository gates pass in `out/checks/run-7h_vacv9`, including the offline audit of 2,844 recorded native outcomes across 49 bundles. These host checks supplement the fresh 166-case native run. Final evidence is retained under `docs/evidence/native-history-capacity-2026-09-06/`.
