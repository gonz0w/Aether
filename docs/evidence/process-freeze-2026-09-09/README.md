# Cooperating process freeze boundary

All 12 connections, five launch, seven M4 and431 command cases pass, along with
98 Python host tests and Zig/offline-pin/workflow checks. The full command run took
about1411 seconds within the1800-second review ceiling. New owners are1544–2408
bytes within8192. See the timing and coverage limitations below.

The opt-in connections profile implements self-freeze, supervisor query and
cancellation of a saved worker continuation. It preserves the existing factory,
image and lifecycle authority boundaries. Freeze allocates nothing, grants nothing,
and returns no successful fork result. Cancel resumes the worker with EAGAIN;
stop invalidates the pending request. Exact local operations and bounds are in
NATIVE-SHELL-STARTUP; the connections reference records the case oracles.

The positive worker completes two freeze/cancel cycles per generation with its
TLS/stack sentinels intact. Query remains stable while the supervisor yields;
malformed fields, worker attempts to query/cancel, invalid/stale handles and stale
request tokens reject. Stop/reclaim and reuse cannot revive old handles. Disabled
operations return ENOSYS; the supported signal-action profile returns ENOTSUP from
self-freeze. Existing connections bootstrap still rejects thread composition.

Most positives require six reclaims across two generations. The signal-action
runner-local case uses its existing four-reclaim oracle and two workers. Deliberate
missing parking and stale-token acceptance must reject owner1710/1712 with zero
reclaims. No panic caused by boot failure or timeout counts as those rejections.

## Retained attempts

- Attempt1: a dummy ELF lacked the TLS segment required by the existing loader;
  it was rejected before execution. The fixture now reads its TLS sentinel. The
  first host check also identified the unclassified feature and negative flags;
  their explicit classifications were added to the existing policy test.
- Attempt2: the unsupported-state case selected threads in a connections envelope,
  which the current bootstrap rejects. The test now uses supported signal-action
  composition; the bootstrap restriction was preserved.
- The first M4 attempt could not bind its local QMP socket under the sandbox. It
  did not establish a target result. The retry with socket permission passed all
  seven M4 cases; both attempts are retained.

No page copying, child publication, libc grant rebinding, exec/CLOEXEC, waitpid,
full DASH-argv, consumer adoption or release readiness is established by this
slice. These remain next steps. FX save/restore is the existing implementation;
this fixture directly checks stack/TLS continuity, not new FP isolation coverage.
The sequence ceiling is enforced at signed63-bit maximum; no native exhaustion
run is claimed. No sibling source or released pin changed.

The existing commands run the host, connections, launch, M4 and command suites.
Sources remained frozen during target runs. run-timing.json records the sequential
host/launch/failed-M4 wrapper; command-timing.json records the full command run.
No outer timing receipt is claimed for the directly invoked connections/M4 retry.
Scoped formatting, Python syntax and simplicity snapshot checks are separate
receipts. collect.py verifies source identity and archive readback and preserves
all failed target directories. The final manifest binds this packet.

## Commands

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --connections \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/regression.py
python3 scripts/launch_smoke.py --command-runner \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

Verified archives retain226 frozen source files and9,521 target artifacts,
including both failed connections attempts and the blocked M4 attempt. Failed
source snapshots were checked against their original run reports.
