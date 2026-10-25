# Public runner integration review (UL-059)

2026-09-06. Userland technical review of the producer's combined startup/result
bundle; bounded integration input selected, not native consumer acceptance.
The [review lock](evidence/runner-owner-review-2026-09-06/review-input.lock.json)
binds the producer report, command report and 293-file source archive. All archive
members and both report identities were verified before inspecting extracted
sources. The default command-runner/native.py path retains its original producer pin;
explicit boundary/startup flags select the reviewed bundle.

## Accepted direction for the next local experiment

Use Aether's opt-in AERUN001 carrier as the private trampoline's input to the
userland parser. The kernel still starts argv=["client"]; the carrier supplies
logical aether-run arguments. This resolves the six-string requirement without
changing ABI 9 or pretending kernel argv has widened. Userland agrees to evaluate
this exact carrier for the bounded experiment; public API/release acceptance
requires the consumer witnesses below.

The authoritative carrier and mapped-result formats remain in the pinned
producer docs/NATIVE-COMMAND-IO.md (inside the retained source archive). No new
shared standard, grant, wire field or environment API is introduced locally.
The carrier arrives before the ordinary two-binding bootstrap. Its 224 bytes
contain magic, count, reserved zeros and six 32-byte slots; logical argv[0] is
exactly aether-run. Validate the whole record, private copy and binding pair before
invoking CLI logic. Parent startup is not a child argument vector.

The current native_bootstrap() initializes its private transport fields itself.
Reading the carrier by pre-initializing those fields and then calling that function
would trip its re-entry guard. Introduce an explicitly separate opt-in entry path
with one initialization owner, rather than bypassing that guard. Preserve the
legacy 32-byte bootstrap entry and old exit-29 suite. Failed startup publishes no
arguments or descriptors. Do not replay a partially consumed stream.

The producer's mapped_results mode accepts a parent only after child admission,
termination and consumed collection. It preserves kind 1/detail 0–255 and maps
faults to 1, with independent backend readback and six reclaims. This is suitable
for the first successful-command integration. It cannot yet qualify local usage,
help, missing command, denied admission or unknown collection: an early parent
exit necessarily fails its admitted/collected gate. Those public outcomes require
separately agreed producer observation and lifecycle behavior, not relaxed success
assertions in our harness.

## Evidence and remaining gaps

| Boundary | Producer evidence inspected | Independent consumer work |
| --- | --- | --- |
| Carrier | Three/six logical strings, full-record rejection, private copies | New decoder, all carrier field boundaries, partial reads, publication and re-entry |
| Argument forwarding | Fixture-selected slot 1/2, two/four child strings, empty/31-byte values | Actual parser chooses offset; independent observer verifies complete argv/env |
| Results | Normal 0/1/2/64/125/126/127/134/255 and actual fault 134/kind 2 | Decoder preserves raw facts; actual userland runner maps status and consumes once |
| Combined | Three accepted combined cases and one fourth-argument corruption control | Userland runner and observer against the exact new producer bundle |
| Legacy | Producer reports all earlier cases passing (55 command cases total) | Retain and rerun our separate nine-case suite for affected adapter changes |
| Pre-admission/local actions | Not covered by mapped_results acceptance | Owner proposal for zero admissions, aliases, early parent exit and cleanup |
| Unknown/stop/cleanup failures | No general resolution contract; wide normal detail is host policy only | No replay; retain unknown state; owner-defined cleanup/recovery before unattended use |
| Help and diagnostics | No new output/stderr grant | Real delivery capacity and explicit streams before native help acceptance |
| Packaging/init | No consumer assembly or lifecycle evidence here | UL-012 with respective owners; artifact identity does not activate services |

The producer uses a different recorded SDK build from our strict SDK. A matching
source archive does not establish SDK equivalence. The new consumer driver must
verify its own existing SDK/tool closure and retain freshly built artifacts; do not
reuse producer ELFs as if they were our independent clients. No producer test was
rerun during this document review.

## Implementation order and ownership

1. Complete local UL-058 bootstrap/transport controls using the
   [boundary plan](../experiments/command-runner/BOUNDARY-PLAN.md). Preserve source
   review findings and pending independent reviews; tests may expose corrections
   requiring a separate reviewed change.
2. Build a pure bounded carrier decoder and CLI selector under C17. Host controls
   include all AR-02/03 syntax cases, zero publication on failure, copied input
   and deliberately broken decoder controls. Host success is not native startup.
3. Add an opt-in combined startup path and a separate pinned integration driver.
   Replace the producer fixture FORWARD_FIRST input with parser selection. Start
   with bytecount --decimal and leading --, then use an independent child observer
   for the four-argument shape; bytecount itself correctly rejects extra arguments.
4. Qualify mapped terminal results, exact output and cleanup with matching native
   artifacts. Keep raw kind/detail independent of the public numeric exit. Preserve
   old markers and the legacy suite, and retain semantic controls.
5. Submit concrete producer requirements for zero-admission/local exits and unknown
   recovery if needed; no sibling edit or message occurs through this document.
   Keep AR-01/06/09–11/14 incomplete until their actual boundaries are exercised.

Current task supplies this technical review. Independent technical/reader review
and full affected-owner acceptance remain pending. UL-059 is unblocked for the
bounded consumer work above; it is not complete and no public CLI is installed.


## Consumer startup adoption — 2026-09-06

Steps 1–3 now have scoped witnesses: the pure parser and opt-in carrier entry
validate before publishing; actual selector output determines launch slots.
[Four new native cases](evidence/runner-startup-2026-09-06/summary.json) cover
bytecount with and without leading delimiter, a separate full argv/environment
observer, and an intentionally corrupted fourth argument. All 34 combined cases
and nine original-pin regressions pass. The 25 prior client ELF hashes remain
identical. Parent29 is retained: producer runner_startup is enabled for these
cases, but mapped_results is not. This checkpoint replaces the earlier pending
consumer startup note without claiming full CLI acceptance.

Next is step 4, starting with pure validated admission/collection results and
terminal policy. Keep raw detail/kind and receipt ownership distinct from public
exit values. Step 5 zero-admission/local output and unknown recovery remains
owner work; the current positive producer gate must not be relaxed to claim it.


## Consumer mapped-result adoption — 2026-09-06

Step4 now has [scoped native evidence](evidence/runner-mapped-2026-09-06/summary.json):
actual userland admission/collection decoders, preserved normal statuses and fault
mapping, raw facts across a local cleanup-error report, independent output and
six reclaims. No producer source was changed. New cases explicitly enable both
runner_startup and mapped_results; legacy parent29 remains intact. The close-error
case deliberately fails the producer's positive gate, so it does not extend owner
acceptance to cleanup failure. Likewise, generic early return1 is only bounded
experiment abort, not an accepted public precondition or recovery outcome.

Next is step5: specify concrete owner observations for local/zero-admission exits,
explicit output grants and alias cleanup, without weakening admitted/collected
checks for completed children. Unknown admission/collection and resource resolution
remain separate requirements. Native mapped-path malformed/unknown reply controls,
independent technical/reader review and package/init handoff also remain open.


## Local-outcome handoff prepared — 2026-09-06

[RL-01–12 proposal](RUNNER-LOCAL-OUTCOMES.md) is ready for owner review, not sent or
accepted. Current command contract/broker/backend hashes match our consumed
producer. It specifies separate local lifecycle verification, zero-admission
proof, bounded explicit stdout/stderr roles, exact output readback and distinct
cleanup accounting. Candidate plain help is472 bytes, so the existing64-byte
backend cannot deliver it. Proposed capacities512/256 and role transport need
owner acceptance; no ABI/binding fields or default pins are allocated here.

Exact text fixtures and rejection controls are retained; all RL runtime cases
remain NOT RUN. Next local work: mapped-runner malformed/lost-reply and pending
budget controls. Native local outcome adoption requires the owner extension, but
that dependency does not block these independent local tests.

## Consolidated owner handoff — 2026-09-06

[Current review packet](RUNNER-OWNER-HANDOFF.md) supersedes older next-action notes
above: mapped uncertainty/budget, native startup rejection and host local
parser/delivery integration now have retained scoped evidence. All four relevant
owner contract/runtime inputs still match the consumed producer. Native local
help/error outcomes are waiting for the explicit output-role/lifecycle extension
and new owner evidence bundle. No sibling edit, message or pin update was made.
UL-059 is waiting for that named prerequisite; local UL-067 work can proceed while
UL-069 stays deferred. Reassess against the returned bytes, not a milestone label.
