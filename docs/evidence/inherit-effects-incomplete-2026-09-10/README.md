# Incomplete inherited write/close replies — 2026-09-10

The owner now handles missing or 17-byte replies after actual stdout appends and
last-holder input closes. It retains exact received counts and requires all 32 bytes
within the existing 256-read-attempt bound, yielding on EAGAIN. A partial close reply
can be entirely zero-filled and still must not be accepted as complete. EIO does not
prove the backend operation had no effect.

Shared uncertainty blocks later backend operations through both clients. Parent
closes release only parent holders successfully; child final closes consume local
aliases with EIO while the backend lifetime stays unresolved. Confirmed backend
stop143/kind3 precedes six reclaims over two generations. Write clients finish74/75,
close clients76/77. Private flags and repeated-close EBADF checks remain.

All 64 connections and five launch cases pass, plus 98 Python host tests and
Zig/pin/workflow checks. The eight new cases comprise four positives and four controls:

- Missing/partial replies for each operation complete the bounded recovery path.
- Write partial-padding exposes success and requires source254/owner1992.
- Close partial-padding falsely reports closure and requires child255/owner1996.
- Both missing-reply omitted-stop controls require owner1993 with zero reclaims.

Each of these negative controls requires zero reclaims. Earlier malformed-reply, replay and
alias-bypass cases retain their oracles and pass. No failed attempt occurred.
Connections-suite-ff7307tp completed on frozen runtime sources.

The [pre-code selection](../../NATIVE-SHELL-STARTUP.md#incomplete-inherited-effect-replies-selection--2026-09-10)
records ownership, forbidden outcomes, test selection and simplicity tradeoffs.
The write path reuses existing behavior; the close path now handles incomplete
records explicitly. Existing backend injection and client checks are reused.
No kernel, backend, C, command-source, opcode, pool, dependency or unsafe-boundary
change is introduced. The runtime patch contains only the owner and harness changes.

Ordinary client/backend and existing write/close backend images match the preceding
slice byte-for-byte. The 22 older raw connection payloads match outside 48 fresh
entropy bytes. Maximum owner size remains 5,880 within 8,192. The previous full
431-command/M4 execution and backend static comparisons remain historical; no fresh
command runtime acceptance is claimed. No siblings or released pins changed.

The read bound is an attempt budget, not a wall-clock deadline or fairness guarantee.
These selected missing/partial-effect witnesses do not prove exactly-once operation
or all backend failure interleavings. Incomplete final publication, arbitrary
descriptor preparation and signal-aware copying remain open. Installed SDK
fork/exec/wait, full dash, independent consumer acceptance and R1 remain unfinished.

Timings retain exact commands, UTC timestamps and exit status. Reports bind source,
tool and SDK identities. The collector verifies the preceding packet, frozen inputs,
pinned simplicity snapshot and archive readback. Native artifacts retain musl
notices. Formatting, compatibility and final checks have separate receipts;
manifest.json seals this packet.

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --connections \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

Archive readback verified 225 source files and 1,255 native target artifacts.
All final suites met their documented review budgets.
