# Cancellation closes native retry admission — 2026-09-06

[Decision 0024](../../decisions/0024-native-retry-cancellation.md) tests local
activation cancellation after malformed-readiness cleanup and after collecting
a valid frame from a still-live provider. Cancellation is idempotent and closes
both retry reservation and frame admission without resetting the attempt count.
Actual stop, observation, close and reclaim remain separate required operations.

Three explicitly created activations each launch and reclaim one provider; no
dependent or retry launches. The previous activation stays cancelled after the
next begins. This arrangement satisfies the existing three-reclaim fixture marker;
it does not reset or automatically restart a cancelled activation.

Ignoring cancellation during reservation must reject at 936 with one reclaim.
Ignoring cancellation during frame admission must reject at 937 with zero reclaims.
The latter frame was actually read before cancellation; this does not establish
asynchronous command transport or late notification delivery. Exact contexts
distinguish expected semantic rejection from boot failure or watchdog timeout.

Producer summary:
`3a399587b34010302d25838d9f8e1cc73e2b93bec1ac673321326494bde1f155`.
Worker receipt:
`e2f989eb90782016624d4230e6320cc85e04c52a13bee9410e0fd54fd37ec474`.
Both remain unchanged. Reports, commands, logs, producer and worker inputs,
source snapshots, raw supervisors, envelopes and serial output are retained.
ISO hashes are retained without ISO bytes. `comparison.json` records older raw
supervisor identity separately from semantic outcomes in `results.json`.

```sh
python3 tests/native-init.py --producer docs/evidence/native-retry-cancellation-2026-09-06/producer --summary-pin 3a399587b34010302d25838d9f8e1cc73e2b93bec1ac673321326494bde1f155 --deps PINNED_AETHER_DEPS --service-worker docs/evidence/native-retry-cancellation-2026-09-06/worker --service-worker-pin e2f989eb90782016624d4230e6320cc85e04c52a13bee9410e0fd54fd37ec474 --work NEW_PRIVATE_DIRECTORY
```

Run from sys-init with verified offline boot dependencies replacing
`PINNED_AETHER_DEPS`, and a fresh private output directory. This is BSP-only QEMU
policy evidence, not a real control CLI, full model port, POSIX session, SMP or
physical-hardware result. Shared pins, sibling files and historical evidence stay
unchanged. See the [policy review](../../NATIVE-POLICY-REVIEW.md) for remaining gaps.
