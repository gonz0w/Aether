# 0070 — Exhausted native generation denies before acquisition

Accepted experiment plan, 2026-09-06, BG-058/BG-057 NB-08.

Qualify the existing native-generation reservation guard with actual fixture
history. Construct the driver in an empty Adapter domain, then explicitly account
for three independently launched and reclaimed workers in native slot zero.
Check each returned identity (generations one through three) before recording it.
No inferred, unknown or externally imported ownership is accepted.

The first issued service at generation one must be denied on exhausted native slot
zero before a channel call. Repeat denial and require counters, unused issuance,
empty attempt records, pending position and owner status unchanged. The same token
must then reserve unexhausted native slot one with expected generation one and
acquire a real channel. Do not launch a fourth worker: the existing fixture oracle
requires exactly three reclaimed workers. Explicitly dispose the newly acquired
pair while retaining the consumed token/reservation. This is neither retirement
nor a completed service lifecycle. Finish 100/reclaimed=3 with Adapter clean.

Controls: skip generation guard -> exact 1023/reclaimed=3; consume the first token
while returning denial -> exact 1024/reclaimed=3. Both require the designated native
profile panic/context; unrelated failure or timeout does not qualify. Run all 72
prior cases plus these three, using pinned SI-04, Rust 1.98.0/2024, BSP-only and
unchanged 4 KiB clients, then all repository checks. Retain frozen inputs, exact
oracles, attempted builds and prior-client comparisons.

This covers the native-generation exhaustion part of NB-08 only. General 64-bit
token/cut/owner exhaustion and journal-table replenishment are not supplied by
the fixed two-token fixture. Existing duplicate/capacity witnesses retain their
own scope. Next NB-09 needs a bounded lost-reply ownership design before execution;
other errors and ND-02–05 remain open. O-04, I-04–06 and E-01–08 apply. No new
dependency, unsafe operation, shared ABI, output protocol or recovery claim.

## Implementation review

The normal driver guard is unchanged except for two designated omission controls.
The positive accounts each actual fixture Worker against the exact expected
identity before recording its generation and disposing it. Exhaustion denies
before slot/attempt/token mutation and before channel acquisition. The successful
reservation on the other slot uses the same full issued token and leaves that
native slot's generation unchanged because no worker is launched there.

The added test owns and explicitly closes the pair acquired on the other slot.
Its retained reservation and consumed token are not represented as journal cleanup.
No new unsafe block, allocation, dependency or runtime output contract. All selected
local compile probes fit without failed builds; no independent sign-off is claimed.

NB-09 design constraint: current acquisition is a synchronous direct call. A
lost-reply fixture must first specify invocation versus receipt/application state
and who retains any actual returned handles. It must not simply drop a successful
return or label a withheld local completion as proof of kernel reply loss. An
unresolved invocation must prevent replay of the same pending acquisition.

## Validation — 2026-09-06

All 75 native cases pass with all 178 frozen inputs unchanged. Forty-four of 72
preceding raw clients match; twenty-eight changed clients pass their prior oracles
and are individually recorded in witness/comparison.json. New sizes: 3,192 bytes
(exhaustion), 3,224 (guard control), 3,208 (consumption control), within 4 KiB.
Exact 1023/reclaimed=3 and 1024/reclaimed=3 controls pass. No failed builds or
native executions occurred.

All eight gates pass in `out/checks/run-ge7504x4`: 228 model tests, 23 negative
controls, 48 host tests and 37 harness tests. The native catalog verifies 1,040
historical outcomes across 35 bundles and 13,946 listed files. Both targeted
native-input harness tests, new document references and `git diff --check` pass.
Seven current consumer source entries match the executed snapshot.

Evidence: `docs/evidence/native-generation-exhaustion-2026-09-06/`. Only validation
notes and retained evidence copies follow checks; runtime sources, tests, catalog
and inventory remain unchanged. Next NB-09 bounded invocation/receipt ownership
design; broader NB/ND requirements remain open.
