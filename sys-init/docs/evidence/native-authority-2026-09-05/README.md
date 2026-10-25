# Native readiness authority — 2026-09-05

[Decision 0011](../../decisions/0011-native-readiness-authority.md), BG-032/BG-040.
[Three target cases](results.json) pass using unchanged BG-055 kernel/musl SDK
inputs, native memory disabled and SMP off. Only sys-init and private build copies
were edited. Shared standards pins remain unchanged.

The positive worker checks eight supervisor-only operations with three holder/
argument combinations before emitting its output rendezvous: launch, status,
reclaim, legacy output, completion, stop, input and stream read. Each returns
-13. Thus both generations must pass 24 worker-side denials before the supervisor
can observe complete output. An unexpected result exits before that rendezvous.

The supervisor checks worker-local notification and generation-query denial with
zero, factory-shaped, current/stale and malformed holder values before launch,
while live, after terminal and after reclaim. Live state remains unready after
these attempts. Generation one exits without notifying and retains false history.
Generation two notifies twice using nonzero ignored arguments and exits with true
history. The arguments cannot designate a readiness recipient in this profile.
Terminal tuples remain stable through repeated observation. Exact per-generation
stdout/stderr, EOF, rejected terminal input/seal, reclaim and six stale operations
retain their earlier checks. The positive ends with result 100/two reclaims and
the exact native I/O pass marker.

The allow-notify control incorrectly expects supervisor success and rejects at
exactly `NATIVE supervisor result=501 reclaimed=0`. Skipped backing zeroing rejects
with the existing native-profile panic and no pass marker. It is an independent
kernel mutation, not an assertion-localized policy failure. No command timed out.

[Compatibility byte checks](compatibility.json) preserve both older worker
profiles and all nine distinct retained-output/readiness supervisor variants.
The seven-case readiness suite runs again successfully
([target results](compatibility/results.json)). [Full checks](validation/results.json)
pass 38 host tests, 34 model tests/three mutations, 17 harness tests and all three
offline standards checks. The new profile test rejects mixing authority inputs
with the older profiles.

## Reproduction and evidence boundaries

Use the verified [BG-055 SDK/tool lock/kernel inputs](../native-refresh-2026-09-05/README.md)
and the source files retained here:

```sh
python3 scripts/build-native-io-worker.py --authority --sdk IO_SDK --tools-lock TOOLS_LOCK --receipt-pin SDK_RECEIPT_SHA256 --output NEW_WORKER_DIRECTORY
python3 tests/native-io-stop.py --authority --aether AETHER_SNAPSHOT --sdk NEW_WORKER_DIRECTORY --receipt-pin WORKER_RECEIPT_SHA256 --work NEW_PRIVATE_DIRECTORY
```

Receipt pins identify the corresponding `evidence.json`. Worker and harness modes
are explicitly selected and mutually exclusive with readiness mode. The
[worker receipt](worker/evidence.json) records actual captured headers, objects,
libc, source and executable tool pins checked before/after build. Static ELF64
x86-64/TLS/NX/no-WX/no-unresolved/no-relocation inspection, link map, disassembly,
worker bytes and input copies are retained separately from execution logs.

Source manifests identify frozen kernel/client inputs. Target commands, serial
logs, supervisor images, artifact hashes, producer receipt and licensing notices
are retained. ISO bytes remain at recorded private work paths. SHA256SUMS.json
fingerprints the retained bundle. Trust and development bootstrap limitations
remain those of the earlier witness; this does not authenticate SDK publishers or
close host shared-library provenance.

This tests caller-local rules using guessed numeric values, not transferred
grants or an exhaustive live-peer noninterference proof. No delegated readiness
API exists in the frozen profile. BG-032/BG-040 remain partial: live-peer cases,
external/delegated notifications, event/deadline contracts, SMP and supervisor
recovery remain separate. No production language or new shared standard is chosen.
