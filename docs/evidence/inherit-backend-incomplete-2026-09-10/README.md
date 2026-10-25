# Missing/partial inherited backend replies — 2026-09-10

The shared uncertainty path now handles a live backend that publishes no reply or
only 17 of 32 bytes, then yields. The partial prefix contains count1 and data byte a;
its missing tail must not be treated as zero-filled completion. The bounded record
reader is shared with child readiness and requires a complete record within 256 read
attempts, yielding on EAGAIN. It retains exact incomplete counts 0/17. This is an
attempt budget, not a wall-clock deadline or general fairness guarantee.

Both clients require EIO with unchanged buffers through FD0 and FD10, preserve their
private CLOEXEC flags and consume local descriptors. The shared latch prevents
further backend operations. No offset is guessed, operation retried or backend close
fabricated. Source74/child75 and confirmed backend stop143/kind3 precede six reclaims
across two generations. Complete EIO does not assert the backend had no effect.

All 49 connections and five launch cases pass, plus 98 Python host tests and
Zig/pin/workflow checks. The partial-padding control exposes successful data and
requires source254 then owner1992 before reclaim. Missing-reply omitted stop must
reject owner1993 with zero reclaims. Earlier malformed-reply and alias-bypass
controls retain their existing oracles and pass.

The [pre-code selection](../../NATIVE-SHELL-STARTUP.md#missing-inherited-backend-reply-selection--2026-09-10)
records requirement, forbidden outcomes, ownership, tests and simplicity tradeoffs.
Reusing one bounded reader avoids another receive loop; existing shared uncertainty,
EIO, stop and dispose paths handle cleanup. The test-only FFI injection retains a
live stack reply, validates every short-write count and advances only within the
17-byte prefix. No new kernel primitive, protocol opcode, service or pool is added.

## Retained failed attempt

connections-suite-9ifkazbb passed the first 46 cases, including missing-reply recovery,
then rejected the partial-reply fixture with backend122/owner1994 and zero reclaims.
The fixture incorrectly required one write to transfer all 17 bytes. Native channel
I/O caps each transfer at 16 bytes, so this was a fixture implementation failure.
The two new negative cases were not run in that attempt. Exact source snapshot,
report, logs, timings and artifacts are retained. The correction accumulates checked
short writes over a bounded loop before stalling; owner and harness oracles are
unchanged. Final connections-suite-j6bx_vxa passes all 49 cases. Host and launch
checks were repeated on the corrected sources.

Kernel/build and ordinary client/backend images are unchanged. The 22 earlier raw
connection payloads match outside 48 fresh entropy bytes. All four command-backend
variants rebuild byte-identically to the preceding slice; relative to the older
431-command packet, they retain only the previously recorded two panic source-line
changes. Static comparison is not fresh command runtime acceptance. Prior full
command/M4 execution remains historical. Maximum owner size is 5,848 within 8,192.
No sibling sources or released standards pins changed.

Uncertain writes/final closes, incomplete final publication, arbitrary descriptor
preparation and signal-aware copying remain open. Installed SDK fork/exec/wait,
full dash, independent consumer acceptance and R1 remain unfinished.

Sources stayed frozen during each target attempt. Timings retain exact commands,
UTC timestamps and exit status. Reports bind source/tool/SDK identities. The
collector verifies the preceding packet, pinned simplicity snapshot, final inputs,
failed source snapshot and archive readback. Native artifacts retain musl notices;
command-backend rebuilds have a separate verified archive. Compatibility, format
and final checks have separate receipts; manifest.json seals this packet.

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --connections \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

Archive readback verified 225 final source files and 1,920 native target artifacts,
including the failed attempt. All final suites met their review budgets.
