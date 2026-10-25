# File-backend EOF recovery

All408 command cases and98 Python host tests pass with offline pin/workflow
checks. Final run: command-runner-suite-pec2l20l. Scope: AECAT004 backend replies that end after zero or16
bytes following a real open/read/close. This is native producer fixture evidence,
not consumer acceptance, general service recovery or release readiness.

The service executes the operation, optionally sends exactly16 reply bytes, closes
its delegated reply endpoint and keeps yielding. It does not exit: EOF is not a
terminal-state witness. The unchanged owner rejects incomplete transfers, closes
client delivery, observes client1 and verifies file-service stop kind3/detail143
before clearing descriptions. It does not retry or guess unknown handles. The
unchanged poison client requires EIO, unchanged read buffers, no partial open
publication, consuming local close, restored mask and no further channel traffic.

All six positive cases require exact client1/stream17 logs in two generations and
six reclaims. Native forced stop has no normal-exit line; retained-state queries
provide its witness. A seventh case omits stop after a half open reply and must
reject owner1601 after client1 with zero reclaims. Existing malformed-reply and
other command regressions remain required.

Run the established commands with the captured SDK and lock:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --command-runner \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

Only the command helper adds a private close bridge over existing0x24003, alongside
its included process-helper bridge. No kernel API, shared wire version, quota,
SDK/upstream object, dependency, sibling or released pin change. Original C follows
the existing scoped style; Rust uses edition2024. The8192-byte owner limit remains.
No fresh M4 run is selected because no kernel or M4 path changes.

Initial attempt command-runner-suite-pzeo5kcd stopped at link with zero executed
cases: the close bridge was placed in the standalone file helper, which the command
fixture does not link. That change was removed and the wrapper placed in the command
helper. Full failed inputs, compiler log, report and generated artifacts are kept.
No target behavior or test expectation was relaxed by the correction.

collect.py verifies final frozen inputs, the prior sealed packet and the four-file
simplicity snapshot, then reads back the source/artifact archives. manifest.json
binds the completed packet. The reference records the before-code requirement,
forbidden outcomes, ownership, unsafe/resource implications and simplicity review.

A silent service with its reply endpoint still open, timeout and late delivery
remain unqualified. Embedded fixture files are not persistent storage or OpenZFS;
actual-main ENV, full dash exec/wait/pipeline workloads and consumer intake remain.

All seven new owner images match their prior qualified counterparts byte-for-byte,
verified against the previous sealed artifact hashes in owner-identity.json.
recovery-receipts.json retains the seven exact serial outcomes. The largest final
cat owner remains8120 bytes within the8192-byte limit.

The sealed snapshot retains213 sources and8726 target artifacts, including the
initial failed build. review-checks.json records the final scoped checks.
