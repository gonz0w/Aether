# Private copied continuation — 2026-09-09

This packet records the bounded supervisor-authorized copy/commit experiment in
[NATIVE-SHELL-STARTUP](../../NATIVE-SHELL-STARTUP.md#private-copycommit-implementation-selection--2026-09-09).
It is a local primitive witness toward the shell process path, not public fork,
unchanged DASH-argv, companion acceptance or release readiness.

All 17 connection cases, five launch cases, seven M4 cases and 431 command cases
pass: 460 target cases in total. Final-source host checks pass 98 Python tests plus
Zig/pin/workflow checks. The full command suite took 1,409.90 seconds, within the
1,800-second budget. Runtime sources remained frozen throughout qualification.
The final manifest binds this packet.

## Behavior and scope

Operation 0x23006 requires the existing supervisor factory, a live frozen source
handle with its exact request sequence, a vacant destination and two distinct
empty supervisor-owned channels with correct endpoint roles. It eagerly copies
owned private pages, preserves anonymous ownership, holes and protections,
rebuilds physical mappings and copies the saved frame/FX/FS/TLS state explicitly.
Fresh memory and endpoint grants are returned in child registers. Copied auxv or
cached grants do not acquire authority. The child records its actual fork parent
for this bounded lifetime; general reparenting is not implemented.

Two generations exercise parent/child return values, continued TLS/stack/FX state,
fresh authority, bidirectional memory isolation while both processes remain alive,
PROT_NONE contents, hole preservation, zeroed hole reuse and six final reclaims.
Validation trials reject bad factory, stale source/request identity, invalid or
occupied destinations, incorrect endpoint roles and queued channel data. A forced
failure after staging preserves source parking, endpoint ownership and destination
generation; cancellation and a fresh launch then succeed.

Deliberately shared writable anonymous backing must produce parent status 215 and
owner 1821 with zero reclaims. Lost anonymous metadata must produce child status
218 and owner 1820 with zero reclaims. Skipped rollback zeroing must hit the exact
`native copy rollback not zeroed` invariant. Boot failure and timeout do not count
as these expected rejections. Owners are 3,352–3,384 bytes within the existing
8,192-byte limit; no worker, channel or page pool grows.

## Retained failures

1. The first supervisor build failed on an i64/u64 handle comparison. No copy case
   booted. The comparison now uses the explicit signed return type. The first host
   run passed, but final-source host checks are required separately.
2. The second attempt booted its copy case and rejected child status 219: the
   witness incorrectly expected EINVAL when unmapping an already empty hole.
   The existing memory contract returns ENOMEM for that absent mapping. Only the
   witness expectation changed. The same revision strengthened live bidirectional
   isolation; the retry preserves exact mutation-rejection status checks.

Both failed source archives were read back against their original results.json
source hashes. Failed target directories and logs are retained with final artifacts.
No kernel memory error contract or existing acceptance marker was weakened.

## Verification and limits

Commands, UTC start/end, elapsed time and exit status are in each profile's timing
receipt. Native reports bind case identities, tools, commands, source hashes and
artifacts. M4 ran with permission for its private local QMP socket. Formatting,
Python syntax and the four-file simplicity snapshot check have separate receipts.
The collector verifies final sources against every report, the previous freeze
packet manifest, the exact changed/added runtime set and both archive readbacks.

The fixture checks FX continuation, not new independent floating-point mutation
isolation. Native generation exhaustion and maximum-capacity copying are not new
coverage. Public libc cached-grant/identity rebinding, inherited open descriptions,
descriptor/CLOEXEC semantics, transactional exec, parent wait, signal/thread copy
composition and independent userland acceptance remain subsequent work. Extended
fuzz/soak/hardware coverage and assembled-image release gates remain open. Sibling
sources and released standards pins are unchanged.

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

Verified archives retain 228 frozen sources and 9,597 target artifacts, including
both failed connection attempts. The source delta is four existing runtime/build
files plus two new copy fixtures; the build-policy classification and local
documentation are retained separately in the same source archive.
