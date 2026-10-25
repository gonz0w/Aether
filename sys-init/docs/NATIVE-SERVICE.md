# Native provider/dependent workload

Current extension: [dependency loss](decisions/0025-native-dependency-loss.md)
keeps the admitted dependent running, records loss and blocks new admission under
provider stop and normal return. All 35 target cases pass. The controlled-stop
baseline below remains an earlier, stronger stop-on-loss fixture. See the
[model comparison](NATIVE-POLICY-REVIEW.md) for remaining operation/control gaps;
this fixture series is not a complete implementation of the model.

2026-09-05. [Decision 0019](decisions/0019-native-service-dependency.md) now has a
consuming target witness on the corrected SI-04 producer. The
[policy module](../prototypes/native-supervisor/service.rs) uses the unchanged
adapter to launch a provider, admit an actual dependent from readiness, invalidate
that dependent on observed provider termination, clean up both workers, then ready
and clean up a fresh provider generation.

This is launch ordering and lifetime policy for one hard dependency. The dependent
does not call a provider API or receive a provider capability. There is no parsed
service descriptor, configurable graph, automatic retry loop or production daemon.
Existing producer workers supply the one-byte fixture readiness frame (42); they
are not authored or rebuilt by this change. No POSIX timing/signal semantics are
inferred. The positive failure schedule uses explicit native stop, not a spontaneous
worker fault or graceful termination.

## Policy demonstrated

A local record binds each frame to its provider worker, channel reader and
generation. Admission requires matching identities, the expected byte, observed
liveness and a final clock observation strictly before the absolute deadline.
Expired-deadline, terminal-provider and old-generation evidence reject. The same
predicate authorizes the actual dependent launch. A read/liveness/time observation
is a cut, not atomic admission or a guarantee against subsequent provider death.

The provider-stop injection completes a registered lifecycle wait. Policy observes
terminal detail 144, releases the wait, then stops the dependent and requires its
terminal detail 144 before reclaiming resources. Closing both readers and reclaiming
both workers must empty adapter accounting. Replacement generation 2 uses fresh
worker/channel identities; generation-1 evidence rejects and its own frame accepts.
The replacement is then explicitly stopped, closed and reclaimed. Exactly three
reclaims and empty resources precede `AETHER NATIVE INIT PASS`.

Deadline arithmetic remains checked delivered-interrupt counts. Frame polling has
a 100-tick deadline plus a bounded iteration count and independent harness watchdog;
expiry during expected readiness is a failed workload, not successful cleanup.
No wait token is allocated per channel byte or left retained through completion.

## Results

[Fourteen-case target report](evidence/native-service-2026-09-05/results.json):

| New case | Required outcome |
| --- | --- |
| Service lifecycle | Provider readiness → dependent launch → observed provider stop → dependent stop/cleanup → fresh ready provider → three reclaims and INIT PASS |
| Bypass deadline | Assertion 901, reclaimed=0 |
| Accept terminal readiness | Assertion 902, reclaimed=0 |
| Skip dependent stop | Assertion 903, reclaimed=0 |
| Ignore generation/worker/channel binding | Assertion 904, reclaimed=2 |

The four mutation cases require the exact assertion and designated panic; generic
boot failure or watchdog cannot pass. Nine earlier adapter cases also pass and
all nine raw supervisor binaries are unchanged. The new positive client is
**2,960 bytes** under the unchanged 4 KiB bound. All **176 frozen input files**
remain unchanged. These sizes are not speed, total memory or production claims.

Source, exact commands, tool logs, raw binaries, producer envelopes, serial output,
producer archive/receipts and per-file hashes are retained. The producer summary
remains `3a399587b34010302d25838d9f8e1cc73e2b93bec1ac673321326494bde1f155`.
ISO hashes are recorded; ISO bytes are not retained. No sibling changes, shared
standards pin updates, Linux execution or older ABI-2 target rerun are claimed.
The offline catalog now verifies **63 recorded outcomes, 11 bundles, 1,946 listed
files**, including repeated compatibility/negative cases rather than unique features.

Reproduce from this repository with explicit verified dependencies and a new
private work directory:

```sh
python3 tests/native-init.py --producer docs/evidence/native-service-2026-09-05/producer --summary-pin 3a399587b34010302d25838d9f8e1cc73e2b93bec1ac673321326494bde1f155 --deps PINNED_AETHER_DEPS --work NEW_PRIVATE_DIRECTORY
```

[Full development validation](evidence/native-service-validation-2026-09-05/README.md)
passes 48 host tests, 34 model/three mutation controls, 30 harness and all standards
checks, including the 63-outcome offline audit.

## Follow-ons and shared standards

The first decision-0018 workload is implemented in this scope. BG-032/BG-040 remain
partial for worker-originated exception schedules after actual dependent admission,
silent/malformed readiness, repeated replacement and more general dependency
invalidation. Define a controlled worker stimulus and consuming artifacts before
claiming those schedules. Decision 0020 now covers normal worker return; a
supervisor-issued stop does not substitute for an exception schedule.
Broader graph configuration, descriptor selection, backoff and production clocks
remain separately specified work. No new kernel gate was encountered here.

Foundations O/I/E adoption remains unchanged. Distribution SV-01–05 describe a
separate proposed descriptor/publication profile: this hard-coded lifecycle does
not implement that parser or claim descriptor conformance. Exact policy and
fixture evidence remain sys-init-owned; shared standards belong in Aether-standards.

## Terminal collision worker modes — decision 0076

The fixture worker now supports terminal-exit134, terminal-exit143,
terminal-exit17 and terminal-fault after readiness publication. The new pinned
build and consuming optional-worker regressions are retained with
[decision 0076](decisions/0076-native-terminal-collisions.md). These are controlled
native terminal stimuli, not a production service descriptor or CLI interface.
Existing service-return/readiness/retry modes keep their consuming oracles.

The canonical [builder manual](man/sys-init-build-native-service-worker.1) covers current
inputs, options, output lifetime, receipts and build-only limitations. See
[documentation coverage](DOCUMENTATION-INVENTORY.md) for review status.
