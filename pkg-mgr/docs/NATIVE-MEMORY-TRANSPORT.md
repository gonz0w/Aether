# Native-memory consumer transport

The opt-in host transport now supports the userland-adopted native-memory v1
consumer with the descriptor/supervisor envelope `AENFD001`. The existing
`AENSUP01` supervised profile and its receipt bytes remain separate.

```sh
python3 mk/aether-supervised.py stage-memory ROOT BASE_RECEIPT_SHA256 NATIVE_BIN NATIVE_SHA256
python3 mk/aether-supervised.py verify ROOT/aether-memory-v1 RECEIPT_SHA256
```

ROOT must be an initialized private root with a verified five-artifact boot v2
bundle. `stage-memory` creates `aether-memory-v1`, containing `receipt.json` and
six payloads: aether, protection.bin, display.bin, lifecycle.bin,
smp-supervisor.bin and native-c.bin. It preserves exact base/native hashes and
rejects existing publication. The receipt uses `aether-memory-transport-v1` and
requires `required_kernel_options` exactly `{ "native-memory": true, "smp": false }`.
Verification checks the complete inventory, receipt/payload pins, envelope lengths,
ELF identity and this profile. Booleans must be actual JSON booleans.

The kernel options describe required build configuration. Transport cannot infer
compiled options or grant authority by adding a JSON field. Pair the envelope
with the matching tested kernel and retain source/build/consumer evidence.
Hash pins prove byte identity, not release authenticity. Stage/verify never launch
a service; only the separate explicit boot experiment below does so.

## Completed consumer witness

Userland UL-032 records nine memory-enabled outcomes and four legacy descriptor
regressions. The package-side harness consumes its exact pinned results/source
inventory, checks the accepted positive ISO hash, and extracts its boot payloads.
It stages those six exact files, rebuilds the image with the pinned producer tools,
and boots through the existing descriptor oracle. It additionally requires memory
admission (24 used / 104 remaining), successful terminal results for generations
1 and 2, reclaimed=2, and the exact `AETHER NATIVE IO PASS` marker.

The [retained package evidence](evidence/native-memory-transport-2026-09-05/README.md)
records the successful run and complete private-root location. This establishes
transport and native execution of the adopted bounded consumer. It does not run
pkg-mgr natively, install a live filesystem, implement a shell, or grant general
service activation, POSIX, SMP memory or durable/release-trust guarantees.

## Reproduction and checks

The regular sixteen-fixture gate includes the synthetic memory transport checks
through `tests/aether-supervised.sh`. Native execution remains opt-in:

```sh
python3 tests/native-memory-integration.py \
  --producer /absolute/userland-accepted-work \
  --results-sha256 EXTERNALLY_REVIEWED_RESULTS_PIN \
  --sources-sha256 EXTERNALLY_REVIEWED_SOURCES_PIN \
  --root /absolute/new-private-root
```

The producer must retain its accepted nine-case results, sources.json, isolated
Aether snapshot, positive ISO and pinned boot dependencies. Root must not exist;
its parent must exist. Use locally installed matching Python/xorriso/QEMU tools.
No archive download or kernel recompilation occurs. The source-pinned image/smoke
scripts validate their installed tools and boot dependencies. Results, commands,
raw logs, staged bundle and image remain in the private root, including on failure.

The synthetic fixture accepts both explicit profiles and rejects wrong profile
envelopes, memory options, missing options, changed payload and repeated publication,
in addition to the older integrity/inventory controls. A valid `AENFD001` envelope
alone does not prove that it exercises allocation; consumer/boot evidence supplies
that fact. Neither its shared envelope nor package metadata silently enables
memory in a kernel built with the option disabled.

Owner contracts: [userland adoption](../../userland/docs/NATIVE-MEMORY.md),
[kernel ABI](../../docs/NATIVE-MEMORY.md), and
[existing transport boundaries](SUPERVISED-HANDOFF.md). Shared normative work
remains in Aether-standards; no immutable release or pin changes here.
