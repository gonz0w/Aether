# 0076 — Consume colliding terminal kinds from the pinned producer

Implemented standalone producer probes, 2026-09-06, BG-058 NT-01–02.

Add a distinct worker-status read to the existing Adapter trap and a standalone
bounded terminal sampler. A live first observation returns no fact after one read;
a terminal candidate uses observe/status/observe, checking revision, result,
historical readiness and the accepted kind/result pair. Preserve existing wait
status and observation APIs. This does not integrate binding or pending history.

Add fixture worker modes for normal exit 134/143/17 and invalid-opcode fault after
publishing readiness. Rebuild with the existing pinned worker builder using the
retained SDK input bytes. All existing worker modes remain behaviorally unchanged
and receive the optional-worker regression cases in the fresh run.

Terminal-fault-collision and terminal-stop-collision compare equal numeric terminal
results with distinct actual kinds. Terminal-live checks a silent live sample,
then actual stop and a coherent terminal sample. Positives must finish 100/3 after
explicit reader/worker disposal. Terminal-ignore-kind must fail 1036/reclaimed=0
when it mistakes a normal exit for a fault. Coherence/bounds errors use 1037;
cleanup uses 1038. Retain all prior oracles, 4096-byte raw bound and frozen pins.

No raw return is fabricated in these new probes. Their worker modes are controlled
stimuli, not production service behavior. The sampler is a trusted local helper;
NT-03–07 bound identity, interruption and pending-fact integration remain open.
Native kind 2 remains restricted to result 135 in this consumer. No POSIX signal
mapping, stop acknowledgment, journal acceptance or recovery is inferred.

Foundations O/I/E and the existing Distribution limits apply unchanged. No unsafe
trap, existing machine output, shared ABI/pin or dependency changes. The added
worker UD2 instruction is a deliberate fixture fault. Retain exact worker build,
source hashes, failures if any, full target run and development checks. No exception
or independent sign-off is claimed.

## Result and review

Decision 0076 passes 114 native cases: all 89 prior base cases, four new terminal
probes and 21 existing optional-worker regression cases. Actual normal exit 134
versus fault 134 and normal exit 143 versus stop 143 retain distinct kinds despite
equal encoded results. Live sampling reads once; terminal sampling checks three
coherent reads. The kind omission control hits 1036/0.
All 181 frozen inputs unchanged; 44 of 89 prior base clients match, and changed
clients retain their oracles. The rebuilt worker's old modes pass their consuming
regressions. This is standalone NT-01–02 coverage, not bound pending-fact or journal
integration. Next: NT-03 retained-target identity and sampling reservation; NT-04–07,
remaining NB/ND requirements and BG-033 recovery stay open.

The separate terminal module uses actual Worker wrappers and a fresh bounded
Sampler per call. It checks a positive terminal revision, exact observation/result
agreement and historical readiness across O1/status/O2, then validates the selected
kind/result pair. The separate worker_status method preserves the existing wait
status API and unchanged unsafe trap. Normal 134/143, invalid-opcode fault and
normal 17 worker modes publish readiness first; the silent live probe does not.
The stop collision permits either readiness history depending on when stop occurs,
while still requiring the three actual reads to agree.

Each positive retires three actual fixture workers and explicitly closes readers.
The omission control classifies result 135 as fault while the first worker actually
exited normally, reaching 1036 before any reclaim. It cannot pass via timeout or
missing tools. No journal or pending terminal history is executed. Runtime assertion
termination on contradictory samples is fixture behavior, not production handling.

The new method uses the existing Adapter Error shape. Its invalid-readiness guard
would locally construct operation 0x20001/errno 71; that is not a native errno
receipt. This valid-return slice does not qualify that failure path. NT-04 must
retain raw partial results and distinguish local guard cause from actual syscall
rejection before broader error/retention claims. NT-03 must bind the retained launch
identity and serialize sampling with driver effects; NT-05–07 retain interruption,
idempotence/conflicting history and capacity coverage. No gap is waived here.

The unchanged worker builder verified the reconstructed SDK: header/lib/startup
bytes, SDK receipt and tools lock came from the immutable standards-update-validation
worker inputs after checking their original input hashes. The SDK receipt remains
cd5342886674cd644db22dff0afe51bae46d24432403909953df5de407e21d34.
The new worker receipt is
83522cf0688b140442a7dc597a54ca53ccdcb63888ccdf63e417ede7ff3e9c97.
Its complete build, inputs, tools/options, ELF and logs are retained inside witness/
worker. The native runner validates the receipt and uses this ELF only for explicitly
selected terminal/optional-worker cases; prior base images remain the pinned helpers.

All 107 local configuration builds and the complete target/worker builds pass.
No failed build or execution occurred. Rust 1.98.0/2024 and C11 compiler-extension
profiles, the 4096-byte raw-client bound and existing third-party terms remain.
The extra UD2 is a deliberate worker fault stimulus, not a change to the supervisor
trap or kernel. Production language, authority and POSIX mapping remain unselected.

Evidence: `docs/evidence/native-terminal-collisions-2026-09-06/`. Documentation
impact covers terminal/worker references, native coverage, standards adoption,
quality inventory and work order. No shared pin, ABI, existing marker/exit contract,
exception or independent reviewer sign-off changes.

## Validation — 2026-09-06

The full pinned native run passes 114 cases: 89 previous base cases, four new
terminal probes and 21 existing optional-worker cases. All 181 frozen inputs are
unchanged. Eight current native consumer files match the executed snapshot; current
worker C and builder source match the retained successful worker build. New raw
sizes are 1784 (terminal-fault-collision), 2160 (terminal-stop-collision), 2000
(terminal-live) and 1752 bytes (terminal-ignore-kind), within 4096 bytes.

`python3 scripts/check-all.py` passes all eight gates in
`out/checks/run-jwemyt39`: 228 model tests, 23 negative controls, 1000 traces,
48 host tests and 37 harness tests. The catalog verifies 1407 historical outcomes
across 39 bundles and 17,565 listed files; these are not distinct current tests.
The catalog checks worker input/ELF correspondence for each optional-worker case.
`git diff --check` and local reference links pass. No failed build or execution
occurred. Full evidence is retained in
`docs/evidence/native-terminal-collisions-2026-09-06/`.

Only validation notes and evidence copies follow checks; runtime sources, tests,
inventory, catalog and pins remain as checked. Next is NT-03 retained-target identity
and sampling reservation, with NT-04–07 and remaining NB/ND/recovery still open.
