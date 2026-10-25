# Live-handler incomplete publication — 2026-09-10

All 132 connections and five launch cases pass, plus host/Zig/pin/workflow checks
including 98 Python tests. Fourteen new combinations exercise existing incomplete
publication containment with live copied signal handlers. No qualified attempt
failed; all three suites stayed within their review budgets.

Missing or partial child receipt/readiness confirms child stop before holder
recovery. The surviving parent restores its checked callback, saved mask and errno,
validates its private descriptor state and performs local dup/close before continuing.
These four cases retain parent73/backend17 over two generations and six reclaims.
Missing or partial final completion on either side confirms both stops before
draining the complete peer's queued request and releasing shared backend handles.
These four cases retain only backend17 terminals over two generations and six
reclaims. A complete peer may execute its callback before containment. Silence
alone is not evidence that an incomplete client's callback never ran.

Six deliberate controls accept padding or omit required stops. Readiness padding
requires1982, omitted readiness child stop1981, final padding2001, omitted final
parent stop2002 and omitted final child stop2003. Every control requires zero
reclaims; generic panic, timeout or nonzero exit is insufficient. Stopped contexts
do not return through client cleanup. The owner verifies confirmed terminal state
before recovery and channel EOF after draining final-publication traffic.

The [pre-code selection](../../NATIVE-SHELL-STARTUP.md#live-handler-incomplete-publication-selection--2026-09-10)
records requirements, forbidden outcomes, authority, lifetime and test scope.
Only C fixture aliases and harness combinations/oracle routing changed. Existing
recovery code remains the single implementation; no kernel, Rust owner, backend,
shared adapter, wire, dependency, allocation or quota changes were needed.
This is bounded fixture qualification, not arbitrary-handler safety or SDK adoption.

All 118 previous payloads match outside their 48 entropy bytes, and all previous
kernel images are identical. Backend identity and the 8,192-byte owner limit are
checked separately in compatibility.json. Prior command/M4 execution remains
historical. Siblings and released standards pins are unchanged. Installed SDK
fork/exec/wait, independent full-dash acceptance and R1 remain unfinished.

Reports bind final runtime sources, SDK/tool identities and artifacts. Timings retain
exact commands, UTC boundaries and status. The collector verifies the preceding
sealed packet, the four-file simplicity snapshot, final source hashes and archive
readback. Formatting and final checks have separate receipts. runtime.patch records
this scoped runtime change; manifest.json seals the evidence. An initial editing
helper assertion stopped before writing the harness; it was corrected before any
qualification. No runtime test attempt was discarded.

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --connections \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

Archive readback verified 225 source files and 2,381 native target artifacts.
Maximum owner remains 5,880 bytes within 8,192.
