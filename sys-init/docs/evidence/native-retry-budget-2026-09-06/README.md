# Finite attempts and exhausted readiness — 2026-09-06

[Decision 0023](../../decisions/0023-native-retry-budget.md) defines a budget of
three total attempts, including the first launch. Silent and malformed workloads
each reject all three attempts, with stop/terminal observation/close/reclaim before
each replacement. Reservation happens before acquiring resources. Generation
replacement does not reset the activation's budget. A fourth reservation must
be denied without changing the count or launching a worker. No dependent launches.

The positive completion marker describes a successful exhausted-policy test,
not a service becoming ready. The two controls allow an extra reservation or
stop after only two cleanups; they must reject at 931 with three reclaims or 934
with two reclaims, respectively. Timeouts and unrelated assertions cannot satisfy
these expected outcomes. All prior twenty-three schedules remain regression cases.

The producer summary is
`3a399587b34010302d25838d9f8e1cc73e2b93bec1ac673321326494bde1f155`;
worker receipt is
`e2f989eb90782016624d4230e6320cc85e04c52a13bee9410e0fd54fd37ec474`.
Both are unchanged. This bundle retains exact commands, frozen source identity,
worker build inputs, raw supervisors, envelopes and serial logs. ISO digests are
retained without ISO bytes. `results.json` records semantic outcomes;
`comparison.json` records preceding supervisor byte identity separately.

Reproduce with offline boot dependencies and a fresh private output directory:

```sh
python3 tests/native-init.py --producer docs/evidence/native-retry-budget-2026-09-06/producer --summary-pin 3a399587b34010302d25838d9f8e1cc73e2b93bec1ac673321326494bde1f155 --deps PINNED_AETHER_DEPS --service-worker docs/evidence/native-retry-budget-2026-09-06/worker --service-worker-pin e2f989eb90782016624d4230e6320cc85e04c52a13bee9410e0fd54fd37ec474 --work NEW_PRIVATE_DIRECTORY
```

Replace `PINNED_AETHER_DEPS` with the verified local boot dependency directory.
Scope is the allocation-free, BSP-only ABI-6 fixture. No production retry default,
backoff, cancellation interface, POSIX timing, physical hardware or SMP claim.
No sibling, shared pin, native ABI or historical evidence changed.
