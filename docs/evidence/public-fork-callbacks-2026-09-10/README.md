# Public fork live callbacks — 2026-09-10

The isolated public fork candidate now composes actual musl pthread_atfork
registration/dispatch with native signal delivery. Two callback registrations
require reverse preparation and forward parent/child order. The private trace
observes signal delivery after staging completion and libc child repair, before
post callbacks on this pinned implementation. Handlers inspect rebound references,
endpoints, cached/kernel TID, CLOEXEC and private FD counts. Post callbacks check
mask16 and identity. Handler and callback code preserve errno.

Parent posts coalesce under musl's full mask, and the child receives a fresh post.
Earlier signal-copy controls remain the separate witness for empty child pending
state: checking a zero callback count while masked alone would not establish it.
This packet does not claim a portable libc guarantee about delivery versus callback
order, nor safety of arbitrary callbacks. Atfork registration allocates before fork
through the existing native allocator; staging and callbacks add no allocations.

The [pre-code selection](../../NATIVE-SHELL-STARTUP.md#public-fork-callbacks-selection--2026-09-10)
records scope, bounds, ownership, lifetimes and simplicity. One private trace and
completion gate reuse existing native APIs and libc state; no new service, kernel
mechanism or recovery path is added. The link map proves pthread_atfork and
__fork_handler come from the SDK archive while fork/_Fork are the private source-
built candidate. Upstream sources and licenses remain unchanged from the prior run.

Six new cases:

| Case suffix | Required result |
| --- | --- |
| public-fork-live | Parent71/child72/backend17 over two generations, six reclaims |
| rollback-public-fork-live | Recovered parent73/backend17/replacement17 over two generations, six reclaims |
| prepare-public-fork-live | Source78/backend17 over three generations, six reclaims |
| public-fork-live-order | Reversed registrations: source81/owner1950, zero reclaims |
| public-fork-live-no-post | Missing child post: child81/owner1950, zero reclaims |
| public-fork-live-repair | Omitted libc repair: child81/owner1950, zero reclaims |

Generic panic, nonzero exit or timeout cannot satisfy these controls. All cases
use the existing owner lifecycle/cleanup oracle. Prior malformed/incomplete-message
fixtures remain separate; they are not automatically public-call acceptance.

Only fork-client.c and the harness runtime sources changed. No kernel, Rust owner,
backend, rebind helper, shared adapter, installed SDK, sibling or released pin
changed. All137 older payloads/kernel images are compared in compatibility.json.
Prior full command/M4 execution remains historical. Remaining admission/failure
coverage, arbitrary callbacks, contention, recursion, threaded fork, native wait/
exec/vfork and independent SDK/dash acceptance remain open; R1 is unfinished.

Exact commands, UTC timing/status, source/tool/SDK identities and native artifacts
are retained. The collector verifies the previous sealed packet, simplicity pin,
final source hashes and archive readback. The preceding public-fork packet retains
its three compile failures; no attempt from this packet was discarded. The final
checks include strict first-party C formatting. runtime.patch records this change;
manifest.json seals this evidence.

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --connections \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

Final qualification passes 143 connections and five launch cases plus host/Zig/pin/
workflow checks including 98 Python tests. No qualified attempt failed; all suites
met review budgets. Archive readback verified 226 final sources and 2,783 target
artifacts. Maximum owner remains 5,880 of 8,192 bytes. The inspected upstream
pthread_atfork source and COPYRIGHT are retained with their verified archive digest.
