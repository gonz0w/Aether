# Readiness cleanup and one retry — 2026-09-05

[Decision 0022](../../decisions/0022-native-readiness-retry.md) defines this bounded
ABI-6 workload. Silent or malformed readiness must reject before dependent launch.
The supervisor stops the failed provider, observes terminal status, closes its
reader and reclaims it before starting generation two in the same slot. Only that
generation's valid frame, live state and deadline authorize the dependent launch.
Both remaining workers are stopped, closed and reclaimed for exactly three reclaims.

The report contains two positive schedules and two omission controls in addition
to all nineteen earlier cases. Retaining the first reader must reject at result
927 with one reclaim; skipping fresh readiness must reject at 929 with one reclaim.
An unrelated assertion or watchdog timeout cannot satisfy either oracle.

This is one explicit retry and at most two simultaneous workers. It does not
establish automatic restart budgets/backoff, production framing or deadlines,
general graphs, supervisor recovery, SMP or physical-hardware behavior.

The frozen producer summary remains
`3a399587b34010302d25838d9f8e1cc73e2b93bec1ac673321326494bde1f155`.
The unchanged worker ELF is consumed through bounded-build receipt
`e2f989eb90782016624d4230e6320cc85e04c52a13bee9410e0fd54fd37ec474`.
Source snapshots, full worker inputs/receipt, producer identity, commands, logs,
serial output, raw supervisors and envelopes are retained. ISO hashes are retained
without ISO bytes. `comparison.json` measures prior supervisor byte identity
separately from the semantic case outcomes in `results.json`.

Reproduce offline with explicit boot dependencies and a fresh private output root:

```sh
python3 tests/native-init.py --producer docs/evidence/native-readiness-retry-2026-09-05/producer --summary-pin 3a399587b34010302d25838d9f8e1cc73e2b93bec1ac673321326494bde1f155 --deps PINNED_AETHER_DEPS --service-worker docs/evidence/native-readiness-retry-2026-09-05/worker --service-worker-pin e2f989eb90782016624d4230e6320cc85e04c52a13bee9410e0fd54fd37ec474 --work NEW_PRIVATE_DIRECTORY
```

Replace `PINNED_AETHER_DEPS` with the verified local boot dependency directory.
Historical bundles and shared standards/ABI pins remain unchanged.
