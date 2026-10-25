# Shared inherited backend uncertainty — 2026-09-10

A complete malformed read reply from the real Rust stream backend now makes the
shared owner block all later backend operations through either process. Parent and
child each read FD0 and FD10 and require EIO with an untouched buffer. Their private
CLOEXEC flags survive; closing the final local binding reports EIO and a repeated
close reports EBADF. No unknown position is advanced or backend close fabricated.
Complete EIO permits local alias release; it does not prove the backend had no effect.

The owner observes source74/child75 and requests native backend stop. It verifies
status143/kind3 before reclaiming any worker. Two generations finish with six
reclaims, using the existing pools and authority boundaries. The conservative latch
covers the entire three-stream backend, not just the requesting client.

All45 connections and five launch cases pass, plus98 Python host tests and
Zig/pin/workflow checks. Two deliberate broken variants test the critical boundaries:

- Child-only bypass forwards another backend read. The child rejects successful
  data instead of EIO with254, then the owner rejects1992 before reclaim.
- Omitted backend stop leaves a live service and rejects owner1993 before reclaim.

The [pre-code selection](../../NATIVE-SHELL-STARTUP.md#shared-inherited-backend-uncertainty-selection--2026-09-10)
records ownership, contracts, forbidden outcomes, resource limits, test selection and
simplicity tradeoffs. One shared latch reuses the existing channel, EIO, stop and
dispose paths; there is no retry framework, new opcode, pool or unsafe boundary.

## Retained failed attempt

connections-suite-64yg3sm2 passed the first43 cases, including the new recovery
case. Its alias mutant produced child254 then owner1992, but the harness required
these two markers in reverse order. The result is a failed oracle check, not a
successful qualification. The omitted-stop case was not run in that attempt.
Exact sources, report, logs, timings and artifacts are retained. The correction
changes only the expected marker order. Final connections-suite-y9pg0hdg passes
all45 cases; host and launch checks were also repeated on the corrected harness.

Kernel/build hashes and22 previous raw connection payloads match the preceding
packet, excluding48 fresh entropy bytes. The ordinary client image is unchanged.
The ordinary backend and all four affected command-backend variants retain identical
executable code: their only ELF byte differences are source lines55→57 and72→74 in
two panic-location records. Static comparison rebuilt those four backend variants
using hash-verified retained link inputs; it is not fresh command runtime acceptance.
The previous431-command/M4 execution evidence remains historical. Maximum owner
size is5,848 within8,192 bytes. No sibling sources or released pins changed.

Missing/partial backend replies, uncertain writes and final closes, incomplete
publication completion, arbitrary descriptor tables and signal-aware preparation
remain future coverage. Installed SDK fork/exec/wait, full dash, independent consumer
acceptance and R1 are not complete.

Sources stayed frozen during each target attempt. Timings retain exact commands,
UTC start/end and exit status. Reports bind tool/SDK/source identities; archives
retain final and failed native artifacts, source snapshots and musl notices.
Formatting, compatibility and simplicity checks have separate receipts. The
collector verifies the preceding packet, frozen inputs and archive readback.
manifest.json seals this evidence packet.

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --connections \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

Archive readback verified225 final source files and1,774 native target artifacts,
including the failed attempt. The four command-backend rebuilds have their own
verified artifact archive. All final suites met their documented review budgets.
