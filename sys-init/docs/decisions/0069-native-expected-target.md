# 0069 — Qualify admitted workers against reserved native targets

Accepted experiment plan, 2026-09-06, BG-058/BG-057 NB-06.

Reserve the expected ABI-6 worker identity from the native slot and its next
generation before acquisition. Keep native generation counters separate from
service generation. Deny native generation exhaustion before effects. After a
successful launch, retain the actual Worker and reader and record writer transfer
before checking the returned identity. Advance the native counter only on a match.
A mismatch closes admission with a separate local target failure and retains the
actual resources, original token and expected identity; never fabricate errno or
construct an owned Worker from the prediction.

Add a read-only Worker identity comparison with no native syscall or authority
grant. The existing launch-busy fixture explicitly records its known independently
admitted generation-one worker before reserving a target; no arbitrary inventory
adoption or public generation setter is introduced. Failed busy calls do not
advance the counter. Historical fixture disposal remains distinct from retirement.

New matching case accounts for a generation-one fixture worker, disposes it, then
admits two services at service generation one: native slot zero generation two
and slot one generation one. Require exact expected/actual matches and counter
advancement once, including duplicate-launch denial. Two mismatch positives alter
the retained expected target only in test setup: wrong slot or wrong generation.
The real successful launch must leave its actual worker and reader retained,
writer absent, native counter unchanged and owner closed. Later launch/acquisition/
reservation and launched-event qualification must deny. Explicit fixture disposal
uses the actual worker; complete accounting at 100/reclaimed=3.

Controls: omit expected-target comparison -> exact 1021/reclaimed=0; forget actual
Worker on mismatch -> exact 1022/reclaimed=0. Require the designated native profile
panic/context, not an unrelated failure. Run all 67 prior cases plus five new
cases using pinned SI-04, Rust 1.98.0/2024, BSP-only and unchanged 4 KiB clients.
Retain all attempted builds, source/input identities and serial oracles, compare
prior clients, then run all repository checks.

These probes exercise consumer binding failure, not a kernel returning a fabricated
handle. Unknown/lost replies, native exhaustion witness, other errors, terminal
kind and journal integration remain open. O-04, I-03–06 and E-01–08 apply; no
new unsafe block, dependency, shared ABI or output protocol. NB-08/09 remain next
after this bounded NB-06 slice. No complete native driver or recovery claim.

## Implementation review

`Worker::matches_target` compares identity without exposing a constructor or making
a native call. The driver stores expected identity at reservation and retains the
actual successful return before comparison. `target_failed` is separate from local
binding failure and native errno. A failed comparison leaves the actual slot
advanced in the kernel but the local counter uncommitted; permanent owner closure
prevents reusing that unresolved state. No reconciliation is inferred.

The launch-busy fixture verifies its independently returned worker as slot zero
generation one before explicitly recording that history. The new matching probe
does the same before disposal. These are private test assignments with known live
returns, not a generation-import API. Counter increment is bounded by reservation
(<3), successful matching admission and duplicate-launch exclusion; its exhaustion
branch still requires the separate NB-08 witness.

Two compile-only source versions left a prior busy probe oversized. Sharing
fixture disposal and borrowing complete input tokens removed redundant copying;
all fields are still compared and retained issuance is immutable. No guard or
4 KiB limit was removed. Initial sources/logs and final local probes are retained.
Private method signatures changed, not a public/model token or wire contract.
No new unsafe block, allocation, dependency or independent sign-off.

## Validation — 2026-09-06

All 72 native cases pass with all 178 frozen inputs unchanged. Forty-four of 67
preceding raw clients match; twenty-three changed clients pass their prior semantic
oracles and are individually listed in witness/comparison.json. New sizes: 3,352
bytes (matching), 3,400 (wrong slot), 3,416 (wrong generation), 3,368 (skip-match
control), 3,416 (forget-worker control). All fit 4 KiB; exact controls 1021/0 and
1022/0 pass. No native execution failed.

All eight gates pass in `out/checks/run-cbc_p3dd`: 228 model tests, 23 negative
controls, 48 host tests and 37 harness tests. The native catalog verifies 965
historical outcomes across 34 bundles and 13,219 listed files. Both targeted
native-input harness tests, new document references and `git diff --check` pass.
Seven current consumer source entries match the executed snapshot.

Evidence is retained in `docs/evidence/native-expected-target-2026-09-06/`, including
two compile-only size versions and final consuming artifacts. Only validation
notes and evidence copies follow checks; runtime sources, tests, catalog and
quality inventory remain unchanged. Next NB-08 exhaustion, then NB-09 lost replies;
other error/terminal/cut/recovery requirements remain open.
