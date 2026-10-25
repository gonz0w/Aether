# Private action-copy mapping transitions

Before implementation: use the existing explicit memory grant to place a 32-byte
action across two anonymous pages. Reject old-output copies when the second page
is read-only, inaccessible or unmapped, preserving the first page and owner state.
Reject unreadable cross-page input without output/state mutation. Read-only input
remains a valid control. Restore mappings to inspect unchanged bytes; remapped
backing must be zero. Reject inaccessible/unmapped handler and restorer addresses.
A writable-output negative control must fail the exact missing-rejection stage.

No new mappings rights, syscall or delivery behavior. Reuse the current private
operation and existing kernel copy checks; this is fixture coverage, not another
abstraction. Select full command suite and host/pin checks. Runtime kernel logic
is unchanged; update the stale pending-state header to distinguish live opt-in
record copies from still-host-only pending delivery. Freeze sources during runs.

Existing C indentation is retained; no wholesale formatter migration or new
source dependency. The two-page buffer uses the existing granted map/protect/unmap
operations. User code never dereferences the removed tail; inaccessible tails
are inspected only after restoration, and remapped bytes are checked before use.
The first-page prefix stays live during rejection checks. Successful cleanup
unmaps both pages; the deliberately failing control retains zero reclaims before the harness ends
its VM. This is rejection evidence, not recovered cleanup.

Reproduce with the matching strict SDK and native tool lock:

```sh
python3 scripts/launch_smoke.py --command-runner --libc-build /absolute/strict-sdk --tools-lock /absolute/native-tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The run uses read-only Aether-userland/build/native-c-5olokhku and
zig-out/init-capacity-2026-09-06/tools.lock.json, with commands/tool/source digests
retained in command-results.json. collect.py archives sources/artifacts, verifies
the previous packet and simplicity snapshot, and checks that the pending module
changed only its header. No fresh M4 run is selected for C probe/harness coverage
and a kernel comment; the prior seven-case qualification is preserved.
Native peer isolation and actual handler/termination behavior remain open.

All 248 native command cases and 98 Python host tests pass. The positive completes
two generations and four reclaims. The writable control rejects at exact terminal
90/owner 1501/reclaimed0. No failed or interrupted attempts occurred. Runtime
sources remained frozen; format, workflow, syntax and pinned snapshot checks pass.
