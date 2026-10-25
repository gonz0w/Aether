# Silent backend and late-reply recovery

All413 command cases, six native connections cases and98 Python host tests pass,
with offline pin/workflow checks. Final runs: command-runner-suite-o7kt_hkb and
connections-suite-80dw17uz. Scope: bounded AECAT004 file-backend silence after
open/read/close and a deterministic late-open reply. This is producer fixture
coverage, not general timeout/latency guarantees or consumer/release acceptance.

Every command-backend send/receive now uses a real4096-attempt polling budget.
Generic transport retains100000 attempts, and the native3000-tick guard and
30-second harness watchdog remain unchanged. This is real command policy, not a
failure-case override. The prior command budget could not fit the fixture guards.

The backend executes the operation and leaves its reply endpoint open. The
unchanged client requires EIO, unchanged buffers, no partial publication, consuming
local close, restored mask and no later client traffic. The owner does not replay.
For late-open delivery only, the owner closes its backend request writer after
exchange failure. The service waits for that EOF, rejecting intervening request
bytes, then sends a valid reply and stays alive. The owner consumes one zero status
byte solely as a fixture witness. At least15 bytes of the atomic first chunk remain
unread; the outcome stays poisoned and no handle is published. No extra channel,
wire operation or guessed delay is added.

Four positive cases require client1/stream17 logs across two generations, queried
file stop143/kind3 and six reclaims. The late-open omitted-stop control requires
owner1601 after client1 with zero reclaims. Forced stop has no normal-exit line;
the retained-state query must precede clearing descriptions and reclaim. Earlier
malformed/EOF/command cases remain required regressions. The six-case native
connections suite also checks the shared generic transfer path.

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --command-runner \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py --connections \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

The before-code reference and its explicit budget revision record ownership,
forbidden outcomes, buffer/unsafe implications, bounds and simplicity. The shared
bounded helper advances a remaining mutable slice and handles both32-byte frames
and the one-byte witness, preserving partial-EOF/invalid-count rejection. Generic
transfer remains an outlined100000-attempt wrapper to avoid duplicated code. No
kernel API, bridge, dependency, SDK/upstream object, shared wire version, resource
quota, sibling or released pin changes. Three workers/six channels/two records
remain. The final late-owner preflight is8152 within8192. C sources are unchanged;
Rust uses edition2024. No fresh M4 run: no kernel or M4 path changes.

## Retained attempts

- command-runner-suite-7g2bqdib:11 cases passed; silent-open reached generation2
  but exceeded the30-second harness watchdog. Full input snapshot/report/log and
  target artifacts are retained.
- command-runner-suite-4h4e1anm:11 cases passed; an experimental90-second watchdog
  exposed the independent native3000-tick guard during silent-open generation2.
  Its source snapshot/report/log and artifacts remain. The unused90-second
  override was removed; native_smoke.py matches the prior sealed source exactly.
- Size preflights rejected intermediate bounded-transfer/witness layouts. Their
  logs, linker maps, commands and source overlays remain. Each overlay replaces
  the named files in the first full failed input snapshot; all other runtime
  sources are unchanged. Final wrapper and compatibility preflights fit the
  unchanged8192-byte limit. Preflights are compilation evidence, not native runs.

collect.py verifies final frozen inputs, the preceding sealed packet and the
four-file simplicity snapshot, then reads back source and target archives.
manifest.json binds the completed packet. No wall-clock service deadline,
arbitrary late operation, general service-fault recovery, consumer acceptance,
full dash or persistent storage is established by this bounded experiment.

The verified archives retain 213 frozen sources and 17,236 target artifacts.
See review-checks.json for the final checks and unchanged fixture limits.
