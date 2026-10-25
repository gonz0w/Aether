# 0061 — Routed live-worker cancellation and terminal delivery

Accepted 2026-09-06, BG-058/BG-057. Add a private mode-taking routed launch entry;
existing launch delegates with exit mode. Both use the same admission/event path.
No new native ABI, dependency, allocation or unsafe primitive.

## Required behavior

Cancellation of an admitted live worker records intent and requests native stop,
but does not fabricate a Terminal event or acknowledge its delivery. Retain worker,
reader, owned wait, pending event and outcome-delivery state. Successful stop is
not permission for cleanup. A separate native observation supplies terminal 144;
that fact supersedes pending Launched or fills an empty pending slot. Full inbox
retains Terminal. Only accepted terminal transfer permits existing cleanup;
reader closure, target reclaim and wait release all precede Cleaned. Full inbox
retains Cleaned; after delivery eligibility is true but cancelled retry remains
local 0/13. No replacement is acquired.

## Fresh witness

Three live workers in sequence, generations one through three, in slot zero.
Require native observation nonterminal and register an Attempt-owned wait. For
generation two deliver Launched before cancellation; otherwise retain Launched.
Cancel via route, verify exact pending/resource ownership and absent outcome ack,
then require cleanup denial before observation/delivery. Observe native terminal
144, route it, reject full inbox transfer without loss, accept Terminal, cleanup,
retain Cleaned under backpressure, accept Cleaned and deny cancelled retry.
All three actual targets are reclaimed and waits released: final 100/3.

Controls: fabricate Terminal from successful stop -> 1006/reclaimed=0; mark outcome
delivered from stop -> 1007/reclaimed=0. Require exact designated profile panic,
not generic timeout/build failure. Run all 48 previous cases plus these three on
pinned SI-04/Rust 1.98.0/2024/BSP-only, preserving the 4 KiB client bound. Retain
sources, artifacts, raw logs and prior-client comparisons, then full checks.

Review request/observation/delivery separation, partial resource ownership,
backpressure and persistent cancellation. Foundations O-04/I-03–06/E-01–08 apply;
shared pins, machine markers and CLI contracts unchanged. No external control
transport, graceful POSIX signals or native journal application is claimed.

BG-058 next qualifies routed stop-error preservation of pending events and intent.
BG-057 full journal/cut identity and BG-033 unknown-result recovery remain open.

## Validation — 2026-09-06

All 51 native cases pass, with all 177 frozen inputs unchanged. Thirty-five of 48
preceding clients match; thirteen changed clients pass their previous semantic
oracles, individually recorded in witness/comparison.json. New raw clients:
live-stop 2,544 bytes, stop-event 2,400 and stop-ack 624, within the 4 KiB bound.
No failed native attempts occurred.

All eight development gates pass in out/checks/run-4tp2khc2: 228 model tests,
23 negative controls, 48 host tests and 37 harness tests. Native catalog audits
591 outcomes across 28 bundles and 9,393 files. Development sources unchanged;
current native consumer bytes match the executed snapshot. git diff --check passes.
Only decision/planning validation notes were appended after checks; native source
unchanged. Retained evidence: docs/evidence/native-routed-live-stop-2026-09-06/.
