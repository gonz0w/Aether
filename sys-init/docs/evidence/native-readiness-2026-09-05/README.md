# Native readiness ordering — 2026-09-05

[Decision 0010](../../decisions/0010-native-readiness-ordering.md), BG-032/BG-040.
[Seven target cases](results.json) pass against the frozen BG-055 kernel and musl
I/O SDK, with native memory and SMP disabled. Only sys-init and private test
copies changed. Shared standards pins remain unchanged.

| First generation | Terminal kind/detail | Historical readiness |
| --- | --- | --- |
| Exit without notification | exit / 0 | false |
| UD2 without notification | fault / 134 | false |
| Explicit stop without notification | stop / 143 | false |
| Notify then exit | exit / 0 | true |
| Notify then UD2 | fault / 134 | true |

Each positive first observes a live, unready worker with complete generation-
tagged stdout/stderr. Output is only a fixture rendezvous. The worker then
performs the commanded ordering, or the supervisor explicitly stops it. Terminal
polling accepts a terminal result without requiring observation of live-ready
status. Three subsequent observations verify the stable terminal tuple.

Both streams retain exact bytes through EOF; input/seal reject after termination.
Reclaim invalidates six operations on the old handle. A distinct second generation
starts unready, exposes its own output, then notifies and exits successfully.
This also checks that prior readiness does not leak into the replacement.

The invent-ready control expects a false historical claim for an unnotified exit
and rejects at exactly `NATIVE supervisor result=407 reclaimed=0`. The independent
omitted-zeroing mutation rejects with the established native-profile panic and
no pass marker. Actual fault cases contain vector 6, kind 2/detail 134. Each
positive completes with result 100, two reclaims and the existing I/O pass marker.
No command timed out. These are controlled single-core orderings, not exhaustive
interrupt/SMP race tests or supervisor recovery.

[Compatibility](compatibility.json) rebuilds all nine older supervisor variants
byte-identically, and the default retained-output worker envelope is unchanged.
The earlier retained-output suite also runs again with four passing cases
([target results](compatibility/results.json)). Older supervision and stop-client
execution remains in the linked historical witnesses. [Full checks](validation/results.json)
pass 38 host, 34 model/three mutation controls, 16 harness tests and the three
offline standards checks. The added input test isolates the readiness profile
from both older worker profiles.

## Reproduction and provenance

Use the trusted SDK and tool lock from the [BG-055 witness](../native-refresh-2026-09-05/README.md),
the matching frozen kernel, and the source files retained under `source/`:

```sh
python3 scripts/build-native-io-worker.py --readiness --sdk IO_SDK --tools-lock TOOLS_LOCK --receipt-pin SDK_RECEIPT_SHA256 --output NEW_WORKER_DIRECTORY
python3 tests/native-io-stop.py --readiness --aether AETHER_SNAPSHOT --sdk NEW_WORKER_DIRECTORY --receipt-pin WORKER_RECEIPT_SHA256 --work NEW_PRIVATE_DIRECTORY
```

The two receipt pins identify the respective `evidence.json` files. `--readiness`
is opt-in and mutually exclusive with the retained-output harness mode.
[Worker receipt](worker/evidence.json) records actual captured link/header/source
inputs and pinned tool executables checked before/after consumption. Inputs,
link map, static ELF inspection, disassembly, worker envelope and producer receipt
are retained. The existing static x86-64 ELF/TLS/NX/no-WX/no-unresolved/no-relocation
checks pass. Target execution is recorded separately in serial logs and reports.

These hashes identify trusted local bytes; they do not authenticate publishers or
close host shared-library provenance. Development bootstrap bytes retain their
previous limited scope. Source manifests identify the frozen kernel/client inputs;
ISO hashes are retained, while large ISO files stay in recorded private work paths.
SHA256SUMS.json fingerprints this bundle. First-party and musl notices are retained.

BG-032/BG-040 stay partial. Delegated readiness authority, late external messages,
readiness deadlines, general event invalidation and supervisor recovery remain
open. No production language, POSIX process API or new shared standard is selected.
