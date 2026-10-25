# Model-aligned native dependency loss — 2026-09-06

[Decision 0025](../../decisions/0025-native-dependency-loss.md) follows runtime
R-07: loss of a provider blocks new admission while its admitted dependent remains
owned/running. The supervisor records loss against the exact provider binding,
reclaims that provider and launches a fresh generation. The old binding stays
lost; only new evidence authorizes the recovered binding. The dependent's live
state is checked after loss, reclamation and replacement. It is then explicitly
stopped, observed and reclaimed, followed by the replacement provider.

The two positive schedules use native stop and reader-close/normal return for
the original provider. Each completes with three reclaims. Automatic dependent
stop must reject at 940 with zero reclaims; bypassed new-admission policy rejects
at 941 with zero reclaims. Neither control can pass through a generic timeout or
unrelated boot failure. The thirty-one earlier schedules remain compatibility
cases, including their separate historical stop-on-loss policy.

Loss is an in-memory manager record, not an operator event stream or provider RPC.
No queued consumer is actually launched after recovery; the fresh binding predicate
is checked while the original dependent remains running. General graph rebinding,
operation identity, asynchronous control delivery and late launch ownership remain
separate contracts. This is an allocation-free BSP-only QEMU fixture.

Producer summary remains
`3a399587b34010302d25838d9f8e1cc73e2b93bec1ac673321326494bde1f155`;
worker receipt remains
`e2f989eb90782016624d4230e6320cc85e04c52a13bee9410e0fd54fd37ec474`.
The report, raw logs/serial, source snapshots, worker build inputs, producer,
supervisors and envelopes are retained. ISO hashes are retained without ISO bytes.
`comparison.json` records prior binary identity independently of semantic outcomes.

```sh
python3 tests/native-init.py --producer docs/evidence/native-dependency-loss-2026-09-06/producer --summary-pin 3a399587b34010302d25838d9f8e1cc73e2b93bec1ac673321326494bde1f155 --deps PINNED_AETHER_DEPS --service-worker docs/evidence/native-dependency-loss-2026-09-06/worker --service-worker-pin e2f989eb90782016624d4230e6320cc85e04c52a13bee9410e0fd54fd37ec474 --work NEW_PRIVATE_DIRECTORY
```

Run from sys-init with verified offline boot dependencies and a fresh private
output directory. No kernel ABI, shared pin, sibling or historical evidence change.
