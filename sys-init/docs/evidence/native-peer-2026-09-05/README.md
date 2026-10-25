# Known live-peer readiness — 2026-09-05

[Decision 0012](../../decisions/0012-native-peer-readiness.md), BG-032/BG-040.
[Four native cases](results.json) pass using the unchanged frozen BG-055 kernel
and musl I/O SDK. Native memory and SMP are disabled; companion working trees
and shared standards pins were not edited.

Both workers are live and unready before the supervisor gives each the other's
exact handle as eight little-endian input bytes. The first commanded worker
attempts eight operations against that known peer: status, reclaim, legacy output,
stop, input byte, input seal and both stream reads. Every operation must return
-13. It then calls worker-local readiness with the peer handle in both unused
arguments, writes a P acknowledgment and remains live. The supervisor observes
only the caller ready, with the peer still unready and its output unchanged.

The second worker performs the same checks while its peer remains live. Both
then show readiness. The supervisor explicitly stops/reclaims the first actor,
checks the survivor remains live-ready with retained output, and requests its
normal exit. Exact stdout `out:1\nP` and stderr `err:1\n`, open/EOF transitions,
terminal history, rejected terminal seals and six stale-handle operations are
checked. Both slot orders pass, each completing with result 100, two reclaims
and the established native I/O pass marker. Workers share one image and each
runs generation one; slot identity is distinguished by the supervisor handles.

The wrong-peer policy invents readiness for the untouched peer after the first
notification and rejects at `NATIVE supervisor result=607 reclaimed=0`. The
omitted-zeroing mutation rejects independently with the native-profile panic and
no pass marker. No command timed out.

[Compatibility checks](compatibility.json) rebuild the three older worker
profiles and eleven distinct retained-output/readiness/authority policy variants
byte-identically. The three-case authority suite runs again successfully
([target results](compatibility/results.json)). [Full checks](validation/results.json)
pass 38 host tests, 34 model tests/three mutations, 18 harness tests and all three
offline standards checks. The added input test isolates the peer profile from
every earlier worker profile.

## Reproduction and limits

Use the verified [BG-055 SDK, tool lock and kernel](../native-refresh-2026-09-05/README.md)
and retained source files:

```sh
python3 scripts/build-native-io-worker.py --peer --sdk IO_SDK --tools-lock TOOLS_LOCK --receipt-pin SDK_RECEIPT_SHA256 --output NEW_WORKER_DIRECTORY
python3 tests/native-io-stop.py --peer --aether AETHER_SNAPSHOT --sdk NEW_WORKER_DIRECTORY --receipt-pin WORKER_RECEIPT_SHA256 --work NEW_PRIVATE_DIRECTORY
```

The two pins identify the corresponding `evidence.json`. Peer mode is explicit
and mutually exclusive with other modes. The worker builder captures the separate
`io_peer_worker.c` source, leaving earlier worker behavior intact. Its
[receipt](worker/evidence.json) records actual SDK headers, link objects, libc,
source and executable tool pins checked before/after consumption. Static ELF64
x86-64/TLS/NX/no-WX/no-unresolved/no-relocation checks pass. Input copies, link map,
disassembly, worker ELF/envelope, producer receipt and licensing notices are
retained separately from target serial/command reports.

Frozen source manifests and ISO hashes are retained; large ISO files remain in
recorded private work directories. SHA256SUMS.json fingerprints the bundle.
Earlier trusted-SDK, host-library provenance and development-bootstrap limitations
remain. This is a controlled BSP-only noninterference witness, not a proof over
all interleavings, delegated grants, SMP, hostile SDKs or supervisor failure.

BG-032/BG-040 remain partial. Next consolidate native coverage and remaining
contract gaps before selecting another fixture. General event/deadline semantics,
delegated readiness and supervisor recovery remain separately owned work. No
production language or new shared standard is selected.
