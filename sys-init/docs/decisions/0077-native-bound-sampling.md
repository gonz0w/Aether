# 0077 — Reserve terminal sampling against retained launch identity

Implemented bounded sampling fixture, 2026-09-06, BG-058 NT-03 slice.

Bind sample admission to the live owner, full original launch token, applied launch
phase and actual retained Worker. Reuse the driver's single pending position;
record sample start before reads, retaining the qualified fact or native error in
the attempt. This first bounded slice allows one sample per attempt (two attempts,
six reads maximum). A live result releases the sampling position but does not
replenish that attempt's sample budget. Terminal/pending history retirement and
ongoing polling remain NT-06/07 and ND-03 before production use.

Sampling-preflight rejects foreign owner/index; sampling-target rejects token and
actual foreign worker before reads. Sampling-held verifies applied-launch gating, single reservation,
three-read fact retention and duplicate denial. Sampling-stale consumes actual
0x25001/9 after known fixture reclaim/replacement, retaining the original target
and error without inventing a reclaim acknowledgment. All positives finish 100/3.
Sampling-skip-token and sampling-skip-pending must reach 1040/0 and 1039/0;
checks use the same guards as the real sample path. State/cleanup oracles use 1041.

Fixture-owned foreign/replacement workers are explicit test interference in an
initially empty domain, not production nonempty-inventory adoption. Existing
worker build, all 114 prior case oracles, 4096-byte bound and producer pins remain.
NT-04 raw partial receipts and local-versus-native error origin remain open; invalid
coherence still terminates the fixture. NT-05–07 and remaining NB/ND/BG-033 stay open.
Foundations O/I/E and Distribution limits apply unchanged; no shared ABI, unsafe
primitive, dependency, output protocol or exception changes. Fresh native evidence
and full development checks are required; no independent sign-off is claimed.

## Fixture scope refinement before target execution

Size probes exceeded the unchanged 4096-byte linker bound when the new cases
included full Driver reservation/channel/launch composition. The sampling fixture
now seeds one admitted record using an actual reader and Worker from the existing
fixture launcher, verifies the returned first-generation target, and assigns the
trusted original token and bounded counters explicitly. It does not construct a
Worker from the expected number. Sampling-held also tests rejection in the seeded
Returned phase before setting Applied. No production adoption API is introduced.

This isolates NT-03 sampling admission and retention; it does **not** qualify
end-to-end Driver launch-to-sampling composition. That integration gap remains
under BG-058/ND-02. The prior real Driver admission cases are regression witnesses
for their separate scope. Preflight reserves but does not read; held performs the
actual three-read sample. Explicit fixture disposal is not journal retirement.
All failed preflight attempts are retained. Read counters count sampler operations,
not fixture setup, terminal waits or disposal operations.

## Result and scoped review

Decision 0077 passes 120 native cases: all 114 prior cases and six sampling probes.
Owner/index and actual Worker/full-token checks reject before sampler reads. A
retained terminal fact takes three coherent reads and holds the single pending
position; duplicate reads/admission deny. Actual stale lookup 0x25001/9 closes the
driver while retaining the original target and error. Omission controls hit 1040/0
and 1039/0; four positive probes finish 100/3. All 181 frozen inputs unchanged.
65 of 114 prior clients match byte-for-byte; all prior oracles pass.

Fixtures seed admitted state from actual handles and trusted token/counters to
fit the unchanged 4 KiB bound. This qualifies bounded NT-03 sampling guards and
retention, not full launch-to-sampling composition, journal or recovery. Next is
NT-04 raw partial receipts and native/local error origin; composition, NT-05–07,
remaining NB/ND requirements and BG-033 remain open.

The Driver checks live owner identity, original full token, actual stored Worker,
applied launch phase, open state and pending position before reserving sampling.
It records sample_started before the first native read, retains the qualified fact
or actual Adapter error, and closes on the latter without clearing the pending
position. The stale probe tests a first-read native error only; raw successful
prefixes and local boolean-guard origin are not retained by this slice. Coherence
assertions remain fixture termination, not production malformed-input recovery.
A live result releases pending but does not replenish sample_started: the local
one-sample-per-attempt limit gives at most six reads across two attempts. Ongoing
polling, partial interruption, history conflict/idempotence and retirement remain
explicit follow-ons. No allocations, unsafe trap changes or concurrency claims.

Fixture cleanup uses separately known actual resources, including a replacement
whose returned generation is verified; it does not infer reclaim from sampling or
consume a journal fact. Preflight cases perform no sample reads. Sampling-held
retains kind 1/result 18/revision/ready and tests repeated reservation/read/admission
denial. Its Applied phase is explicitly seeded, not delivered through Driver.launch.

All failed size probes are retained with source snapshots, commands and logs.
The first native run passed 57 cases but failed binding-admission at its frozen
source path; the next run was interrupted after 19 cases to fix that known issue.
Both are retained in native-attempts/ and are not final acceptance. Review also
removed a confounding pending reservation from the phase-denial test. Final
admission compares directly with immutable issued tokens and borrows both
probe tokens instead of copying them; values and full-token comparison are unchanged.
The final admission image is 4088 bytes (eight bytes below the fixture bound),
so future composition still needs explicit size work. Thirteen preflight attempts
are retained; the last compiles all 113 configurations from retained source paths.
The final configuration and consuming target builds preserve Rust 1.98.0/2024,
producer/worker pins and the 4096-byte linker bound. The C worker and builder are
unchanged and their 25 existing terminal/optional cases pass. Documentation impact:
terminal reference, adoption, native catalog, inventory and work order. No shared
ABI, release pin, dependency, exception or independent reviewer sign-off changes.
Evidence: `docs/evidence/native-bound-sampling-2026-09-06/`.

All eight development gates pass in `out/checks/run-8a7x0aod`. Eight current
consumer files and unchanged worker/builder sources match the retained native
evidence in `docs/evidence/native-bound-sampling-2026-09-06/`.
