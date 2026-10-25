# 0057 — Native result routing and retained pending events

Accepted 2026-09-06, BG-058/BG-057. Consume decision 0049's pending-event rules
in a bounded native admitted-attempt route, without claiming a native JournalRuntime.

## Contract

A private RoutedAttempt owns one Attempt and one pending Event. Successful launch
queues Launched with the logical generation. Native observation queues Terminal
with that generation and the adapter's exact terminal value; running emits nothing.
Terminal supersedes an undelivered Launched event. Repeated equal terminal facts
are harmless; a conflicting pending event is rejected without replacement.
Generation is local identity, not kernel authority or a complete issued-effect token.

Delivery uses one caller-owned Option<Event> inbox. A full inbox is backpressure:
return false without changing either side. An empty inbox accepts one event before
the route clears pending. This is in-process bounded transfer, not transport,
journal execution acknowledgment or lifecycle policy application. No allocations,
threads, dependencies, new unsafe primitives or shared ABI are added.

Cleanup refuses a pending event or absent terminal-delivery acknowledgment before
native effects. Delivery of Launched alone cannot authorize cleanup. After the admitted terminal
event is delivered, explicit cleanup runs existing Attempt cleanup; only successful,
complete inventory cleanup queues Cleaned. Retirement eligibility requires both
clean resources and no pending event. A full inbox therefore cannot lose Cleaned
or make a route eligible early. No automatic retry or retirement is implemented.
Launch errors stay in Attempt and return unchanged; routing rejected-launch events
and missing/malformed replies remains future work, not silently accepted here.

## Fresh witness and oracles

Three sequential exit workers (the third additionally delivers Launched and
checks that cleanup remains denied before Terminal delivery): queue Launched; reject delivery to a full inbox
without loss; reject cleanup while pending; observe terminal 18 superseding launch;
repeat observation; accept exactly that generation's Terminal in empty inbox;
explicit cleanup queues Cleaned; reject delivery to full inbox and retirement;
deliver Cleaned, verify eligible and actual adapter clean. Finish 100/3.

Omission controls: dropping pending on full inbox must hit 994/reclaimed=0;
retaining Launched instead of selecting Terminal must hit 995/reclaimed=0.
Timeout/build failure/generic panic cannot satisfy either. Run all 35 previous
native cases plus these three with pinned SI-04, Rust 1.98.0/2024, BSP-only and
4 KiB clients. Retain raw logs, source/artifact identity and previous comparisons,
then run all development checks. Review success-before-clear, partial cleanup,
identity and backpressure. Foundations O-04/I-03–06/E-01–08 apply unchanged.

BG-058 next routes known rejected launches through pending failure and cleanup
notification. BG-057 retains journal/cut integration and complete operation identity;
BG-033 recovery and unknown-effect reconciliation remain open. This does not add
production service control, POSIX process semantics or native full-driver equivalence.

## Validation — 2026-09-06

All 38 final native cases pass; all 177 frozen inputs unchanged. Twenty-seven of
35 preceding clients are byte-identical. Eight changed Attempt clients pass their
previous semantic oracles; witness/comparison.json identifies each. New clients:
native-events 2,376 bytes, event-drop-busy 384, event-keep-launch 2,344, all under
4 KiB. Both initial and final native runs passed. Source review added explicit
terminal-delivery acknowledgment and the Launched-only denial probe before final
acceptance; the initial run remains separately retained.

All eight development gates pass in out/checks/run-3gt845lb: 228 model tests,
23 negative controls, 48 host tests and 37 harness tests. Native catalog audits
406 outcomes across 24 bundles and 7,298 files. Development sources unchanged;
current native consumer bytes match the executed snapshot. git diff --check passes.
Only decision/planning validation notes were appended after checks; no native
source changed. Retained evidence: docs/evidence/native-pending-events-2026-09-06/.
