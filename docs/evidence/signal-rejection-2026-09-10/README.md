# Live-handler returning rejection — 2026-09-10

Added an explicit observer path for signals delivered while returning from known
unpublished failures: preparation78 or child receipt/completion251. The wrapper
selects abort state while still masked, restores the saved mask and errno, and
requires exactly one observer and zero descriptor operations. The observer checks
that publication did not occur without inspecting or repairing descriptor state.
Recovered parents continue through the normal checked handler and local dup/close.
This is behavior of the fixture's chosen handler, not a kernel restriction on
arbitrary user callbacks or an installed SDK contract.

All 118 connections and five launch cases pass, plus host/Zig/pin/workflow checks
including 98 Python tests. The three new positive cases preserve exact lifecycles:
preparation gives source78/backend17 over three generations; malformed child receipt
and completion give child251/recovered parent73/backend17 over two generations.
Each yields six reclaims. Five deliberate controls omit abort selection or actually
query FD10 from the aborted callback. They require source79/owner2010 or child79/
owner1960 with zero reclaims. Counters distinguish observer delivery from real FD
access; generic panic, timeout or nonzero exit is not accepted. No qualified attempt
failed, and all final suites met their review budgets.

The [pre-code selection](../../NATIVE-SHELL-STARTUP.md#live-handler-returning-rejection-selection--2026-09-10)
records scope, authority, state, pointer lifetimes, test selection and simplicity.
A private publication/abort distinction reuses existing mask/action APIs and avoids
kernel transport policy or a recovery framework. No kernel, Rust owner, backend,
shared adapter, wire contract, dependency or quota changes. Only inherit-client.c
and launch_smoke.py runtime sources changed from the preceding composition packet.

All 110 earlier kernel images are identical and payloads match outside their 48
entropy bytes. The backend image is identical and maximum owner remains 5,880 bytes
within 8,192. Prior full command/M4 execution remains historical. No sibling source,
released pin or independent consumer acceptance changed.

Missing/partial-record forced-stop containment with live handlers is next; stopped
processes do not return a callback. Installed SDK fork/exec/wait and independent
dash acceptance remain open. This packet does not establish full shell or R1 readiness.

Reports bind source, tool, SDK and artifact identities. Timings retain commands,
UTC boundaries and status. The collector verifies the preceding packet, final source
hashes, pinned simplicity snapshot and archive readback. Native artifacts retain
musl notices; formatting, compatibility and final checks have separate receipts.
`runtime.patch` records the change and manifest.json seals the packet.

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --connections \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

Archive readback verified 225 source files and 2,143 native target artifacts.
