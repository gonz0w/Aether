# Uncertain inherited writes and final closes — 2026-09-10

The bounded inheritance owner now handles malformed replies after an actual stdout
append and after the last holder closes backend input. The shared uncertainty latch
blocks subsequent backend operations. Neither an append nor close is replayed, and
an unresolved backend lifetime is retained until confirmed native stop143/kind3.

Write clients each require repeated EIO without changing their source buffers;
private flags and consuming-close checks remain. Parent final-close clients first
release only their holders successfully. The child's last input close receives EIO,
then remaining aliases close locally with EIO. Repeated closes require EBADF. Write
clients finish74/75, close clients76/77. Both paths repeat two generations with six
reclaims, all after confirmed backend stop. EIO does not prove the operation had
no effect, and consuming a local alias does not prove backend closure succeeded.

All 56 connections and five launch cases pass, plus 98 Python host tests and
Zig/pin/workflow checks. The seven new cases comprise two positives and five controls:

- Write replay sends another request after uncertainty; the backend rejects124 and
  the owner rejects1994 before reclaim.
- Close replay likewise rejects backend124/owner1995 before reclaim.
- False close success exposes zero instead of EIO and rejects child255/owner1996.
- Omitted backend stop in either path rejects owner1993 with zero reclaims.

The backend's replay guard runs before processing another request. Its malformed
reply is injected only after applying the selected append or close. The
[pre-code selection](../../NATIVE-SHELL-STARTUP.md#uncertain-inherited-writesfinal-closes-selection--2026-09-10)
records ownership, forbidden outcomes, resource bounds, tests and simplicity
tradeoffs. The write path reuses shared uncertainty; a bounded last-holder traversal
uses the same stop/dispose helper. No new kernel primitive, service, protocol opcode,
pool, dependency or unsafe boundary is introduced.

No failed attempt occurred. Connections-suite-k2plemn3 passes all 56 cases on frozen
sources. Earlier connection oracles remain intact. Kernel/build and ordinary client
images are unchanged; 22 older raw payloads match outside 48 fresh entropy bytes.
The ordinary backend and four rebuilt command-backend variants retain identical
executable code. Only two panic source-line records change (57→61 and74→78 relative
to the preceding slice;55→61 and72→78 relative to the older command packet).
This static comparison is not fresh command runtime acceptance. The previous full
431-command/M4 execution remains historical. Maximum owner size is 5,880 within
8,192. No siblings or released standards pins changed.

Missing/partial replies for writes and final closes, incomplete final publication,
arbitrary descriptor preparation and signal-aware copying remain open. Installed
SDK fork/exec/wait, full dash, independent consumer acceptance and R1 remain
unfinished. These selected invalid-reply witnesses are not an exactly-once guarantee.

Timings retain exact commands, UTC timestamps and exit status. Reports bind source,
tool and SDK identities. The collector verifies the preceding packet, pinned
simplicity snapshot, frozen inputs and archive readback. Native artifacts retain
musl notices; command-backend rebuilds have a separate verified archive. Formatting,
compatibility and final checks have their own receipts. manifest.json seals this
packet.

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --connections \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

Archive readback verified 225 source files and 1,099 native target artifacts.
All final suites met their documented review budgets.
