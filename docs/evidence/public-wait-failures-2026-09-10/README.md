# Retained wait transport failures — 2026-09-10

This bounded waitpid candidate rejects incomplete replies and ambiguous
acknowledgments with EIO, then rejects subsequent calls locally without replay.
Fault injection closes the owner's reply endpoint after the selected prefix; these
cases establish EOF handling, not a bound on a live but indefinitely silent peer.
The existing EFAULT/drain/no-ACK check precedes each injected exchange.

| Injected reply | First call's status output | Owner collection state |
| --- | --- | --- |
| Missing positive header | Sentinel unchanged | Retained |
| 16 of 32 header bytes | Sentinel unchanged | Retained |
| Full header, two of four status bytes | Low two bytes written; upper bytes unchanged | Retained |
| Missing ACK reply | Complete exit72 word | Consumed |
| ACK with nonzero reserved byte31 | Complete exit72 word | Consumed |

Every call returns -1/errno EIO, with mask16 restored. A second wait also returns
EIO and preserves its output sentinel. The owner verifies actual parent71,
child72, its retained/consumed state, and absence of any extra request before
finishing backend17 and reclaiming six resources over two generations. Collection
and resource reclamation remain separate. A lost ACK cannot guarantee exactly-once
application delivery; a failed call may already have changed the output word.

Two deliberate adapter mutations must fail precisely: bypassing poison produces
an extra request and owner2024; accepting a malformed ACK as success produces
parent82/owner2023. Both require zero reclaims. Timeout, generic panic or unrelated
client failure does not qualify these controls.

The [pre-code selection](../../NATIVE-SHELL-STARTUP.md#public-wait-transport-failure-selection--2026-09-10)
records the requirement, allowed effects, forbidden outcomes, owners, authority,
resource bounds, simpler alternative and tests. No new service, ABI, pointer probe,
allocation or runtime recovery framework was added. This extends existing fixture
controls around the adapter's existing poison behavior. Kernel, backend, installed
SDK, siblings and release pins remain unchanged. General wait4/wait3, interruption,
cancellation, live-peer loss/reconnection, exec and independent dash acceptance
remain open; this is not release readiness.

Commands and UTC timing/status are retained in the adjacent logs and timing JSON:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --connections \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

The collector verifies frozen sources, the prior packet and simplicity snapshot,
then reads back source and target archives. Compatibility compares all152 older
payloads outside entropy and exact kernel images. Maps/disassembly identify the
actual source-built public fork/waitpid and atfork objects. Formatting, pin/workflow
and source diff checks have receipts. Earlier command/M4 coverage is historical;
this client/owner/harness slice selects their complete affected connections and
launch suites. No earlier failed evidence is rewritten.

Attempt1 retains47 passing connections cases before an ineffective replay mutant
was rejected as unexpected success. Disabling only the wait guard left the existing
transport poison guard active. The corrected mutant bypasses both guards through
an existing test-only switch; ordinary adapter guards remain intact. Host and launch
passed in that attempt. Its213 sources and1,948 artifacts are retained and verified;
this target-test failure is not counted as a successful qualification.

Final qualification passes159 connections, five launch cases and host checks,
including98 Python tests plus Zig/pin/workflow checks. Final documentation/inventory
checks also rerun the host suite successfully. All suites met their review budgets.
Archive readback verifies226 final sources and3,058 final target artifacts, plus the
retained failed attempt. All152 older payloads match outside entropy bytes32–79;
all corresponding kernel images and the backend are identical. Maximum owner is
6,648 of8,192 bytes. No kernel, installed SDK, sibling or release pin changed.
