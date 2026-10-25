# Provider-originated normal return — 2026-09-05

This sys-init-owned ABI-6 witness implements
[decision 0020](../../decisions/0020-native-provider-return.md). A provider becomes
ready, the supervisor admits and launches a dependent, then closes the provider's
readiness reader. The provider observes EPIPE on its next bounded write and
returns 17 from `main`; the supervisor observes normal terminal detail 18 without
issuing a stop to that provider. It then stops and reclaims the dependent, launches
a fresh provider generation, accepts only fresh evidence, triggers another normal
return and completes with three reclaims and `AETHER NATIVE INIT PASS`.

The trigger is deterministic fixture coordination, not a production health check,
signal or unprompted crash. It establishes worker-originated normal return after
dependent admission. A worker-originated exception remains a separate follow-on.

The [17-case report](results.json) passes the new positive path and two controls:

- `service-return-early` closes the reader before dependent launch and rejects at
  assertion 912 with zero reclaims.
- `service-return-bad-dependency` omits dependent stop after provider return and
  rejects at assertion 915 with zero reclaims.
- All fourteen prior service/adapter cases pass; their raw supervisor binaries
  are byte-identical to the preceding native-service bundle.

The new positive client is 2,960 bytes under the unchanged 4 KiB code bound.
All 178 frozen consumer inputs remain unchanged. The corrected Aether producer
summary stays `3a399587b34010302d25838d9f8e1cc73e2b93bec1ac673321326494bde1f155`.
Source, commands, tool logs, raw clients, envelopes and serial output are retained.
ISO hashes are recorded while ISO bytes are omitted.

The [worker receipt](worker/evidence.json) records a source-rebuilt strict-musl
ELF with SHA256 `3fa2cc70d5ef60f83b9916e7196298a1970f781e7195d9822b40efbd9e3e74bb`.
Its SDK receipt, libc, tool lock, exact build commands, source/header/library
inputs, structural ELF checks, disassembly and input-stability result are retained
under `worker/`. The consumer pins the receipt SHA256
`f482f64e8fe77abec871731d0194be0957f18bc1312c2ba2e04e46b66adc5068`
and verifies every listed worker-build input before use. Hashes establish byte
identity, not publisher authenticity or complete toolchain provenance.

Reproduce with explicit offline dependencies and a new private work directory:

```sh
python3 tests/native-init.py --producer docs/evidence/native-provider-return-2026-09-05/producer --summary-pin 3a399587b34010302d25838d9f8e1cc73e2b93bec1ac673321326494bde1f155 --deps PINNED_AETHER_DEPS --service-worker docs/evidence/native-provider-return-2026-09-05/worker --service-worker-pin f482f64e8fe77abec871731d0194be0957f18bc1312c2ba2e04e46b66adc5068 --work NEW_PRIVATE_DIRECTORY
```

No sibling repository, native ABI, shared standards pin or historical evidence
changed. No Linux, SMP or physical-hardware execution is claimed. General service
graphs, production framing/timing and recovery remain open under BG-032/BG-040.
