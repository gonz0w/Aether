# Incomplete child publication recovery — 2026-09-10

The owner now requires a complete 32-byte readiness acknowledgment. It accumulates
short reads over at most 256 attempts and yields on EAGAIN. Missing or incomplete
publication requires a confirmed child stop (status143/kind3) before child holder
release and parent recovery. This fixture uses an attempt budget, not a wall-clock
deadline or general scheduler fairness guarantee.

Four positive cases withhold or publish only 16 bytes of the binding receipt or
acknowledgment. The parent preserves FD10/CLOEXEC, reads a/b, exits73 and performs
backend17 cleanup. Each case repeats two generations with six reclaims. A broken
receiver accepting a zero-padded partial acknowledgment rejects owner1982; skipping
the stop rejects owner1981. Both negative cases require zero reclaims.

All 42 connection cases and five launch cases pass, plus 98 Python host tests and
Zig/pin/workflow checks. No failed attempt occurred in this slice. Sources stayed
frozen during these qualified runs. Maximum owner size is 5,848 bytes within 8,192.
The 22 older raw payloads match outside envelope entropy bytes32–79; all earlier
inheritance cases retain their oracles and pass. Kernel/build and other runtime
sources are unchanged. Prior 431-command and M4 execution remains historical,
not freshly qualified by this packet. No siblings or released pins changed.

The [pre-code selection](../../NATIVE-SHELL-STARTUP.md#incomplete-child-publication-selection--2026-09-10)
records scope, forbidden outcomes, owners, resource bounds, test selection and
simplicity tradeoffs. No new protocol opcode, kernel primitive, pool or SDK API is
introduced. Shared backend uncertainty, incomplete final completion, unrelated
terminal children, arbitrary FD tables and signal-aware preparation remain open.
Installed SDK fork/exec/wait, full dash, consumer acceptance and R1 remain unfinished.

Timings retain commands, UTC timestamps and exit status. Reports bind tools, SDK
and source hashes. The collector verifies the preceding packet and pinned simplicity
snapshot, freezes current sources, archives target artifacts and checks readback.
Formatting and raw-payload compatibility have separate receipts. manifest.json
seals this packet.

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --connections \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

Archive readback verified 225 source files and 836 target artifacts. All three
selected suites completed within their documented review budgets.
