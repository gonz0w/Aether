# 0072 — Hold native channel receipts before application

Implemented bounded creation slice, 2026-09-06, BG-058/BG-057 IR-01–04.

Implement the creation subset of decision 0071 with a per-attempt channel phase
and one shared pending position. Record Started before the actual Adapter call;
retain returned endpoints/error before Returned. Apply once, retaining consumed
identity; a held receipt prevents launch and further reservation. A private local
application entry checks live owner, full token, index, operation and target.
Closure preserves phase and resources. The synchronous compatibility path uses
the same start/receive/apply methods. No new ABI, dependency, unsafe operation,
output protocol or production language decision.

Planned native positives receipt-channel, receipt-identity and receipt-close must
finish at 100/reclaimed=3 after explicit disposal plus three ordinary fixture
workers. This is local held-return/backpressure evidence, not lost kernel reply,
journal acknowledgment, Cleaned or recovery. Guard omission receipt-skip-phase
must fail at 1025/reclaimed=0 before any second syscall. Endpoint-loss omission
receipt-forget-writer must fail at 1026/reclaimed=0. Identity mismatch uses 1027;
closure/teardown uses 1028. All 75 prior cases must keep their exact oracles.
Native raw clients retain the 4096-byte bound and pinned Rust/producer profile.

Review scopes ownership, duplicate calls, cancellation, bounded capacity, error
origin and fixture teardown. Existing selected busy errors retain their previous
application semantics. The original creation success is represented by Returned
or Applied with no error plus retained pair, not a copied raw register transcript.
Launch receipt transfer IR-05–06, synthetic absence IR-07 and remaining NB/ND/BG-033
work remain open. Applicable Foundations O-01/O-03/O-04, I-01/I-03–06, E-01–08,
Distribution identity limits and existing pins remain unchanged. No exception or
independent sign-off. Documentation and quality inventory will record the fresh
witness and full development checks before completion.

## Result and review

Decision 0072 passes 80 native cases. Real channel returns remain owned before
local application; repeated invocation/launch authorization and mismatched local
application deny. Matched application happens once; injected closure preserves
phase, endpoints and consumed issuance. Controls hit 1025/0 and 1026/0.
All 178 frozen inputs unchanged; 44 of 75 prior raw clients match, and changed
clients pass their previous oracles. This qualifies the IR-01–04 creation slice,
not lost kernel replies, journal retirement or complete NB-09.
Next: IR-05–06 bounded launch receipt retention and writer transfer. IR-07 synthetic
absence, other NB/ND requirements and BG-033 recovery remain open.

The implementation retains a channel phase in each fixed attempt; the existing
pending index is the single driver-owned position. Channel success is represented
by retained pair plus Returned/Applied phase; selected native errors preserve their
operation/errno. No heap, queue or extra native call is added. Checked index and
phase invariants make private unwraps valid; there is no untrusted parser here.
Native Adapter and unsafe trap bytes are unchanged. The bound remains two consumed
entries and at most one pending creation; closure cannot reset it.

The start_channel guard is shared by the real receive path and the phase omission
probe. The latter catches forbidden authorization before issuing another syscall.
The can_launch predicate is shared with real launch and checked while a receipt
is held; the new probes do not make an additional launch call. The identity probe
separates mismatched owner/index/token/operation/target checks from repeat-call
checks to fit the fixed image. Private helper inlining and borrowing immutable
tokens reduce code size without changing compiler flags or the full token match.

Seven preflight source versions retain 161 probe attempts, including 14 link-size
failures and one invalid-cfg probe caused by overbroad tuple discovery. All 94
valid configs in the final preflight pass; that extra invalid string was not a
native runner case. The fifth version fit locally but left too little margin for the longer
frozen source path; the sixth reduced duplicate checks in the separate identity
probe. All five new clients fit in the actual consuming run. The first native run
passed 39 cases (including all five receipt cases), then failed while linking
binding-failure-client at the page bound. It is retained in failed-native-attempt.
Keeping acquire_checked out of line removed duplicate completion code; the fresh
full invocation then passed. No prior failure was overwritten.

The receipt is held across trusted sequential fixture calls, not an asynchronous
transport. Closure is injected through the private owner flag; no public cancel
request, timeout or recovery authority is implemented. Fixtures explicitly dispose
the retained pair and leave token/phase history consumed, then run three ordinary
workers for the required accounting oracle. Resource-loss controls terminate at
the designated failure and do not claim successful cleanup.

Evidence: `docs/evidence/native-channel-receipt-2026-09-06/`. Exact command,
producer/consumer pins, raw clients, serial logs and comparisons are retained in
its witness. Documentation impact includes the binding/receipt references,
standards adoption, native coverage, quality inventory and current work order.

## Validation — 2026-09-06

The fresh pinned native run passes 80 cases; all seven current consumer inputs
match its frozen source hashes. New raw sizes are 3824 (receipt-channel), 3912
(receipt-identity), 3984 (receipt-close), 3840 (receipt-skip-phase) and 3792 bytes
(receipt-forget-writer). All are within 4096 bytes.

`python3 scripts/check-all.py` passes all eight gates in
`out/checks/run-kod9o983`: 228 model tests, 23 negative controls, 1000 traces,
48 host tests and 37 harness tests. The catalog verifies 1120 historical outcomes
across 36 bundles and 14,708 listed files; these are not distinct current tests.
`git diff --check` and the new reference link checks pass. Full evidence is in
`docs/evidence/native-channel-receipt-2026-09-06/`, including the incomplete first
native run and local build failures. Only validation notes and final evidence
copies follow checks; runtime sources, tests, inventory, catalog and pins remain
as checked. Next is the separately scoped IR-05–06 launch receipt slice.
