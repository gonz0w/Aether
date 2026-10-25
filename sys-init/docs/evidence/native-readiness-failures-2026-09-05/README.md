# Silent and malformed readiness — 2026-09-05

[Decision 0021](../../decisions/0021-native-readiness-failures.md) passes all
19 ABI-6 target cases on the frozen Aether producer used by decision 0020.
The two added cases exercise the same polling helper as successful admission:
silent mode reaches its 10-interrupt deadline at result 920; malformed mode
supplies byte 41 instead of 42 and rejects at result 921. Neither launches a
dependent. EOF, adapter errors, iteration exhaustion and unexpected valid data
have distinct results and cannot satisfy these expectations.

Both negative cases stop at rejection with zero reclaims. Cleanup and retry after
rejected readiness remain follow-on work. These are one-byte fixture frames and
delivered-interrupt timing, not a production protocol or wall-clock guarantee.
All seventeen earlier cases retain their expected outcomes; binary comparisons
are recorded in `comparison.json`, separately from semantic compatibility.

The report, exact commands, source snapshots, build logs, serial output, raw
supervisors and envelopes are retained. All 178 frozen consumer inputs remain
unchanged. ISO hashes are recorded; ISO bytes are omitted. The worker directory
retains its strict-musl SDK/tool/source receipts, ELF checks and build outputs.
Worker receipt SHA256 is
`ffabbc55075469d8bffa1ae6a5a23b9905f752c72037c8df348e320a3ea29c9a`.
Producer summary SHA256 remains
`3a399587b34010302d25838d9f8e1cc73e2b93bec1ac673321326494bde1f155`.

Reproduce with explicit offline dependencies and a fresh private directory:

```sh
python3 tests/native-init.py --producer docs/evidence/native-readiness-failures-2026-09-05/producer --summary-pin 3a399587b34010302d25838d9f8e1cc73e2b93bec1ac673321326494bde1f155 --deps PINNED_AETHER_DEPS --service-worker docs/evidence/native-readiness-failures-2026-09-05/worker --service-worker-pin ffabbc55075469d8bffa1ae6a5a23b9905f752c72037c8df348e320a3ea29c9a --work NEW_PRIVATE_DIRECTORY
```

This is BSP-only QEMU evidence. No shared standards, sibling repository,
historical bundle or ABI changes; no Linux or physical-hardware claim.
