# 0082 — Bound malformed-sample retention

Accepted bounded experiment, 2026-09-06; BG-058 NT-04. Build on decision 0081's
retained-sampling-v1 profile and existing terminal/receipt contracts.

## Required behavior and evidence

Use a real fixture worker and reader with the existing seeded admitted Driver.
After a real terminal O1, omit exactly one selected S/O2 syscall and inject one
labelled raw triple into the same Sampling receive/qualification path. Preserve
all actual returns; do not read and silently replace a native result. Count only
actual Sampling reads in Driver.reads; fixture setup/terminal polling is separate. This is synthetic malformed-data testing executed on Aether,
not a claim that the kernel emitted malformed data or lost a reply.

Six cases: S readiness=2 (Boolean); S kind=4 (KindPair); S result=19 versus
actual O1 result=18 (Result); S reports live=0 after terminal O1 (Result);
O2 revision=O1+1 (Revision); O2 readiness=0 versus actual readiness=1 (Readiness).
All use the existing local failure enum. Assert exact received triples/length,
local cause, no fact, no native errno, closed driver, pending index, original
worker/reader/full token, applied launch phase, generation and consumed issuance.
Further sampling must deny with no new reads. Only after those assertions may
known fixture cleanup reclaim the worker and close the reader. Positive oracle:
100/reclaimed=1 plus PASS; this is explicit fixture disposal, not error recovery.

Three separately compiled omission controls use invalid S boolean: skip closure
must fail 1043/reclaimed=0; forget reader must fail 1044/reclaimed=0; invent native
errno must fail 1045/reclaimed=0. They must reach the exact assertion/panic, never
PASS, boot failure, missing-tool success or watchdog acceptance. Preserve all 127
previous native oracles and execute the complete 136-case candidate. Preflight
strict 4 KiB links, retain failures/maps/sources, then run the pinned consuming
producer/worker in a fresh private QEMU root. Run host validator controls and all
nine development checks before acceptance. No shared ABI, pin, unsafe primitive,
allocation, public injection API or source outside sys-init changes.

Foundations O-01/O-03/O-04, I-01/I-03–06 and E-01–08 apply. Existing Distribution
identity/fixture exclusions and Experience developer diagnostic contracts remain;
1043–1045 are local test assertions, not operator diagnostics or kernel markers.
No new renderer, portability, speed, recovery or independent review claim.
Full launch composition, NT-05 interruption, NT-06/07 pending-history bounds and
BG-057 consumer retirement remain follow-ons; unknown owner recovery is BG-033.

## Failed first completion and correction

The first positive probe passed its malformed-state/resource assertions and
reached 100/reclaimed=1, but the pinned kernel requires exactly three reclaims
for native init PASS. The original acceptance plan's one-reclaim finish was
incorrect. Preserve that failed attempt. Add the existing two ordinary fixture
cycles after the retained-resource checks/disposal, and require 100/reclaimed=3
without changing any kernel or prior oracle. Recheck strict image sizes and run
the complete candidate again in a fresh root.

## Result and scoped review

Decision 0082 passes 136 native cases: all 127 prior oracles plus six labelled
malformed-reply probes and three omission controls. Each probe omits exactly one
selected S/O2 syscall and injects a synthetic raw triple; other received samples
are real. Exact data and local causes survive while Driver closes admission and
retains worker, reader, token, pending index and generation, with no terminal fact
or invented native errno. Further sampling denies without another read.

Six positives finish 100/reclaimed=3 after asserted retention and known fixture
cleanup. Skip closure, forget reader and invent errno controls reach 1043/0,
1044/0 and 1045/0. All 183 frozen inputs unchanged; 90 of 127 previous images
are identical. Largest image remains 4048 bytes; new images fit 3760–3872 bytes.
The first run's one-reclaim completion was rejected by the kernel and is retained;
the corrected run preserves the required three-reclaim positive oracle.

This is synthetic NT-04 qualification executed in the native fixture, not malformed
kernel output or a lost reply. Admission is still fixture-seeded. Next: NT-05
explicit synthetic interruption after O1/S, retaining resources and partial history
without retry/application; NT-06/07 pending-history bounds, full launch composition,
BG-057 consumer retirement and BG-033 recovery remain open.

Reviewed touched code for syscall omission versus returned data, guarded single
sampling ownership, fixed receipt/loop bounds, native/local failure identity,
resource retention and exact independent omission assertions. Synthetic selectors
are compile-time fixture controls, not a public injection API. Ordinary configs
retain the actual raw Adapter path; no new unsafe block or authority is added.
The full native run, source comparison and historical-oracle audit qualify all
changed client images. No independent reviewer sign-off or broad conformance.

Documentation impact: terminal acceptance status, native coverage, quality
inventory, standards scope and owning backlog/STATE. Evidence is retained under
`docs/evidence/native-malformed-sampling-2026-09-06/`. NT-04 first-read malformed
revision/boolean boundaries remain covered by pure host tests, not a new bound
native injection at O1; additional hostile fields/schedules remain explicit scope
extensions rather than an exhaustive malformed-input claim.

Validation: all nine development gates pass in `out/checks/run-3o3jd65e`.
The offline audit now covers 1915 historical native outcomes across 43 bundles;
this is separate from the fresh 136-case target witness. Ten current consumer
inputs and unchanged worker/builder sources match their executed/build snapshots.
The 38 harness tests and nine named host validator tests with two omission
controls pass. Validation artifacts, current adoption records and the failed
first native attempt are retained with the evidence.
