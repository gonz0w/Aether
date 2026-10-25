# Native retained-output evidence — 2026-09-05

[Decision 0009](../../decisions/0009-native-retained-output.md), BG-032/BG-040.
Sys-init now owns the worker and supervisor fixtures for nonempty output retention
across explicit stop and actual CPU fault. The frozen BG-055 kernel and I/O musl
SDK are unchanged; native memory and SMP are disabled. No companion working tree
or shared standard pin was edited.

[Four target results](results.json) pass: stop then normal replacement, invalid-
opcode fault then normal replacement, wrong-fault-kind rejection, and omitted-
zeroing rejection. Both positive clients check `out:1\n` / `err:1\n` while live
with EAGAIN at the next offset, then the same bytes with EOF after termination.
They check historical readiness, terminal kind/detail, rejected input/seal,
explicit reclaim, six stale-handle operations and a fresh generation exposing
`out:2\n` / `err:2\n`, followed by normal exit and reclaim.

The fault trace records `NATIVE fault vector=6` and terminal kind 2/detail 134.
The wrong-kind control records the same real fault, then exactly
`NATIVE supervisor result=307 reclaimed=0`. Skipped zeroing causes the existing
native-profile panic without a pass marker; it is a kernel mutation control, not
an assertion-localized sys-init failure. Both positives finish with result 100,
two reclaims and the exact `AETHER NATIVE IO PASS` marker. No command timed out.
The stop/fault policy images are 1,412/1,364 bytes within the 4 KiB limit; these
sizes and this single-core test are not production performance measurements.

[Compatibility](compatibility/results.json) reruns the earlier four-case stop
suite, including original I/O. Three original supervision variants rebuild byte-
identically to BG-055 ([comparison](legacy-compatibility.json)); their target
execution remains the earlier BG-055 witness. [Full checks](validation/results.json)
pass 38 host tests, 34 model tests/three mutation controls, 15 harness tests and
all three offline standards checks. The added profile test rejects accidental
mixing of upstream I/O probes and the sys-init-owned retained-output worker.

## Inputs and reproduction

The [worker receipt](worker/evidence.json) records the actual captured SDK
headers, startup objects, native I/O object, libc archive, local source, tools and
compile/link commands. `worker/inputs/` retains those bytes, including the SDK
receipt and tool lock; all consumed captured inputs and used tool executables
were checked before/after build. The libc archive and tool lock also match the
trusted producer receipt. The upstream source/rebuild provenance remains the
[BG-055 witness](../native-refresh-2026-09-05/README.md). These hashes identify
trusted local inputs, not publisher authenticity or complete host-library closure.
Musl and first-party notices are retained alongside the artifacts.

The worker is static ELF64 x86-64 with TLS and an NX stack, no dynamic interpreter,
no writable-executable load, no unresolved externals and no relocations. Link map,
disassembly, object, ELF and development envelope are retained under `worker/`.
The 32 bootstrap bytes are reused from the development SDK; they are not a
production entropy mechanism. Static inspection and target execution are separate.

With the matching verified BG-055 SDK, tool lock, frozen kernel and retained
sys-init sources, run:

```sh
python3 scripts/build-native-io-worker.py --sdk IO_SDK --tools-lock TOOLS_LOCK --receipt-pin SDK_RECEIPT_SHA256 --output NEW_WORKER_DIRECTORY
python3 tests/native-io-stop.py --retained --aether AETHER_SNAPSHOT --sdk NEW_WORKER_DIRECTORY --receipt-pin WORKER_RECEIPT_SHA256 --work NEW_PRIVATE_DIRECTORY
```

Pins refer to each directory's `evidence.json`; the second is the newly built
worker receipt. The harness requires explicit `--retained` selection. Its default
still accepts the original upstream I/O profile. Exact target commands, frozen
source hashes, copied policy sources, client images and build/serial logs are
retained here. ISO hashes are in the reports; large ISO bytes remain at the
recorded private work paths. SHA256SUMS.json fingerprints the retained bundle.

These are bounded x86 fixtures, not a production language selection or POSIX
signal/TTY implementation. Termination before readiness, broader readiness
ordering, general deadlines, SMP and supervisor recovery remain separate work.
BG-032/BG-040 remain partial. New shared rules belong in Aether-standards; this
fixture consumes existing contracts and introduces no shared standard.
