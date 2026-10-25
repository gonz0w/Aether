# Native SIGPIPE adapter

Status: qualified for the scoped native producer cases below. See [pre-implementation review](PLAN.md).

New private pipe profiles use public write/sigaction/sigprocmask with existing
native signal actions, mask delivery, public action and termination flags. A
validated nonempty pipe EPIPE posts SIGPIPE once under the transaction mask;
mask restoration polls with signal0, without reposting. Successful public mask
changes also poll, enabling deferred default termination. Handler errno changes
must not leak through mask restoration. Other profiles retain their old behavior.

Each parent creates a pipe and closes the reader. It verifies zero-length write
success and invalid-FD rejection without signal; ignored EPIPE; a handled EPIPE;
two blocked writes coalescing into one handler on unblock; and a pending signal
discarded when ignore is installed. Handler mask, count and errno are checked.
Finally the default action must terminate with actual native kind4/detail13,
either directly from write or after unblocking a previously blocked SIGPIPE.

The Rust owner checks one reader close, one zero write and exactly six EPIPE writes,
then actual terminal/empty request route before releasing holders and closing the
backend. Three parent/backend lifetimes produce six real reclaims. There is no
fork, dummy child or increased quota. The missing-post and missing-poll controls
must reach parent94/owner2172 with zero reclaims, never generic timeout acceptance.

Run with existing pinned inputs:

```sh
python3 scripts/launch_smoke.py --connections --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/console_smoke.py --connections --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

All four focused cases passed on their first attempt. No kernel source, SDK,
sibling, released pin or quota change. Kernel build flags differ only for these
new profiles. The existing serial-dash profile has not yet adopted this adapter.
Public pipe(), same-client pipe generations, actual dash substitution, complete
EINTR/restart/pointer behavior and assembled R1 acceptance remain unqualified.
Retained scripts are audit artifacts; use fresh outputs, never overwrite sealed
packets. Only hash-verified unpacked preflight duplicates may be removed.

## Results

- Complete connections suite: 265 QEMU cases pass.
- Launch and console regressions: five plus two pass (272 target cases total).
- Focused preflight: direct/deferred default positives and two semantic controls pass.
- Host/harness, scoped Rust/C format, workflow, three pins and simplicity checks pass.
- Both positives: native signal13 terminal, backend17 in generations1–3; six reclaims.
- Missing post/poll: parent94 then owner2172 and zero reclaims.

Owner sizes and artifact/source inventories are in qualification.json. The maximum
owner is 9944 bytes under the unchanged 16 KiB bound; image size is not a
worst-case stack or performance measurement. Runtime sources remained frozen.
Sources, patch, exact tool/command identities, raw logs, results and start/end
timings are retained; archives were read back and hash verified. No failed attempts
preceded qualification. Independent reader and consumer acceptance remain pending.
