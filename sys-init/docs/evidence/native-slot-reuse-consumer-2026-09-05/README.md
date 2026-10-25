# SI-04 independent consuming refresh — 2026-09-05

Sys-init now accepts the corrected Aether producer for the bounded ABI-6 reuse
seam. These are new sys-init-run QEMU results, distinct from Aether's earlier
companion-source verification. The previously failing forward probe, reverse
order and all nine unchanged adapter cases pass.

Producer: Aether `docs/evidence/native-program-2026-09-05`, summary SHA256
`3a399587b34010302d25838d9f8e1cc73e2b93bec1ac673321326494bde1f155`.
Before building, the runner verifies the summary, source archive, producer report,
envelope and both ELF correspondences. Each run uses a private extracted snapshot
and explicitly supplied offline boot dependencies. All **175 frozen input files
per run** remain unchanged. The retained producer copies are sufficient for the
same verification; no build follows the mutable sibling checkout.

| Run | Result | Scope |
| --- | --- | --- |
| [Forward](forward/results.json) | Pass, one case | Original no-wait slot-0/reclaim, slot-1/reclaim, slot-0 probe; three reclaims and INIT PASS |
| [Reverse](reverse/results.json) | Pass, one case | Only source change is `[0, 1, 0]` to `[1, 0, 1]`; same required completion |
| [Adapter](adapter/results.json) | Pass, nine cases | Original overlap, adapter edges, false-cleanup control, deadline/readiness controls, both owner-death cases and cleanup-zeroing control |

All nine adapter raw supervisor binaries match the previous accepted bundle
byte for byte. The forward binary matches the historical failing probe exactly.
The reverse source differs only in the declared order, so its binary is expected
to differ. Each run retains source copies, commands, source/artifact hashes,
binaries, envelopes and QEMU serial logs. Compiler options, ABI 6 and the 4 KiB
immutable code bound are unchanged; the main policy remains 3,952 bytes.
The producer receipt includes other native work, but this consumer adopts only
the exercised ABI-6 semantics, not ABI-8/9 composition or new process/file APIs.

Historical failed evidence, older producer artifacts and shared standards pins
are unchanged. Each of these three new evidence directories has a separate
manifest/catalog pin. The offline audit now covers **49 recorded outcomes across
10 bundles and 1,827 listed files**; repeated runs are not distinct features.
ISO hashes are recorded but ISO bytes are not retained. Hash identity does not
establish publisher authenticity or a production security claim. No Linux,
physical hardware or SMP execution is claimed for this refresh.

[Full development validation](validation/results.json) passes on macOS arm64:
48 host tests, 34 model cases/three mutation controls, 30 harness tests, all three
standards checks and the 49-outcome offline audit. Validation is outside the three
catalog-pinned sub-bundles to avoid a catalog/manifest cycle.

## Reproduction

From the sys-init repository, choose explicit verified boot dependencies and a
fresh private output directory for each command:

```sh
python3 tests/native-init.py --producer docs/evidence/native-slot-reuse-consumer-2026-09-05/adapter/producer --summary-pin 3a399587b34010302d25838d9f8e1cc73e2b93bec1ac673321326494bde1f155 --deps PINNED_AETHER_DEPS --work NEW_ADAPTER_DIRECTORY
python3 docs/evidence/native-slot-reuse-consumer-2026-09-05/forward/source/tests/native-init.py --producer docs/evidence/native-slot-reuse-consumer-2026-09-05/forward/producer --summary-pin 3a399587b34010302d25838d9f8e1cc73e2b93bec1ac673321326494bde1f155 --deps PINNED_AETHER_DEPS --work NEW_FORWARD_DIRECTORY
python3 docs/evidence/native-slot-reuse-consumer-2026-09-05/reverse/source/tests/native-init.py --producer docs/evidence/native-slot-reuse-consumer-2026-09-05/reverse/producer --summary-pin 3a399587b34010302d25838d9f8e1cc73e2b93bec1ac673321326494bde1f155 --deps PINNED_AETHER_DEPS --work NEW_REVERSE_DIRECTORY
```

SI-04's local consuming gate is lifted within these demonstrated orders. Next:
define exact readiness bytes, generation binding and failure schedules for
[decision 0018's service/dependent workload](../../decisions/0018-native-adapter-boundary.md)
before implementation. Production elapsed clocks, general delegation, supervisor
recovery, SMP and broader POSIX portability remain open under existing stories.
