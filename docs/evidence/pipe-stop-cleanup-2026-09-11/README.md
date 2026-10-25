# Stopping a pending pipe writer

Status: qualified for the scoped native producer cases below. See [pre-implementation review](PLAN.md).

The native owner fills the pipe with 256 committed bytes and receives the child's
complete next write, which remains Pending. It requests a capability-authorized
stop, observes kind3/detail143, verifies the exact pending request and empty route,
then discards that unapplied request and releases the child holders. The parent
retains and drains all 256 bytes through EOF before wait/ack and exit0. Two real
parent/backend/child lifetimes produce six reclaims. The private wait policy maps
this supervisor stop to status15; this is not native SIGTERM delivery evidence.

Omitting the stop must reject at owner2171 with zero reclaims. Retaining its pending
frame must reject retirement after parent0 at owner2166, also with zero reclaims.
Forced stop has retained state but emits no normal-exit/fault child serial marker;
the owner checks that state directly. Generic panic or timeout cannot pass.

Run with the existing pinned inputs:

```sh
python3 scripts/launch_smoke.py --connections --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/console_smoke.py --connections --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The focused positive and two semantic controls passed on their first attempt.
No kernel, SDK, sibling, released ABI/pin, resource quota or service change.
SIGPIPE, silent stalls, native copy rollback, same-client pipe reuse, actual dash
substitution and R1 assembly remain separate work. This is one named stop schedule,
not general cancellation, all delivery races or public kill/pipe acceptance.
Retained scripts are audit artifacts; use fresh outputs rather than overwrite
sealed packets. Only verified unpacked preflight duplicates may be removed;
archives, raw logs and qualified suite outputs remain.

Implementation review (implementing agent, not independent sign-off): the owner
holds a complete unchanged frame while the core reports Pending. Stop success
alone never authorizes retirement: both the immediate observation and cleanup
path require the exact retained terminal. The cleanup path validates all request
bytes and EOF after termination, and requires 256 committed/zero read bytes.
Only then can it discard the frame and drop holders. Parent EOF precedes wait,
but actual task reclaim still follows collection acknowledgment and route closure.
Existing partial-fault and normal exit paths are unchanged. No additional buffer,
service, allocation, unsafe block or cancellation protocol was introduced.

## Results

- Complete connections suite: 261 QEMU cases pass.
- Launch and console regressions: five plus two pass (268 target cases total).
- Focused preflight: pending-writer stop and both semantic controls pass.
- Host/harness, scoped Rust/C format, workflow, three pins and simplicity checks pass.
- Positive: parent0/backend17 in generations1/2; six real reclaims including
  the two children whose forced-stop state the owner explicitly verifies.
- Skipped-stop: owner2171 and zero reclaims, no terminal child marker invented.
- Retained-frame: parent0 then owner2166 and zero reclaims.

Owner sizes and artifact/source inventories are in qualification.json. The maximum
owner is 9944 bytes under the unchanged 16 KiB bound; image size is not a
worst-case stack or performance measurement. Runtime sources remained frozen.
Sources, patch, exact tool/command identities, raw logs, results and start/end
timings are retained; archives were read back and hash verified. No failed attempts
preceded qualification. Independent reader and consumer acceptance remain pending.
