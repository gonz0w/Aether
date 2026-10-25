# Private signal termination

Before implementation: separately select native-signal-termination (requiring
native-signal-actions) for the private Rust owner only. Default terminating self
signals retain kind4/detail signal, never shell-style 128+signal or CPU-fault kind2.
Legacy action builds still reject default termination. Stop/continue and remote
posting remain unsupported; the supervisor cannot self-terminate through this trap.

Reuse pending selection, finish, observe, stop and reclaim. Block/post/unmask/poll
must terminate the client after its normal I/O cleanup. Rust checks exact signal
2 or15 through repeated observe and idempotent stop, then reclaim rejects the old
handle and a second generation repeats. A normal exit130 control must fail the
kind/cause oracle. No public ABI/profile adoption, consumer decoder changes,
service policy, allocation, quota or automatic asynchronous entry is introduced.

This is the smallest retained-cause experiment using the existing owner. A generic
signal subsystem would add unneeded remote routing and consumer migration now;
no old path can yet be removed. IF=0 serializes dequeue and terminal publication.
Apply existing O/I/E and simplicity review; preserve pins and sibling files.
Run full command, M4, host/pin and Zig/Rust format checks on frozen sources.
Rust uses 1.98.0 edition2024; existing C style is retained. Record attempts and
source/artifact hashes. Independent consumer acceptance remains pending.

Reproduce from the repository root:

```sh
python3 scripts/launch_smoke.py --command-runner --libc-build /absolute/strict-sdk --tools-lock /absolute/native-tools.lock.json
python3 scripts/regression.py
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

This run uses read-only Aether-userland/build/native-c-5olokhku and
zig-out/init-capacity-2026-09-06/tools.lock.json. Receipts retain tool/source hashes,
commands, target artifacts and serial logs. collect.py verifies the previous retry
packet, simplicity snapshot and archived source/artifact members. No sibling edits.
Abrupt termination during live I/O remains a separate next qualification; this
client closes its normal I/O first. Public profiles and consumer acceptance remain
unchanged.

Results: all 257 command-runner cases, seven M4 regressions and host/pin checks
(98 Python tests) pass. Both signal positives retain their exact cause across
two generations and four reclaims. Normal exit130 rejects at kind1/detail130,
owner1501/reclaimed0. Formatting and scoped whitespace checks pass. Runtime
sources stayed frozen and no failed or interrupted qualification attempts occurred.
This does not qualify consumer kind4 adoption, live-I/O signal cleanup or automatic
handler delivery.
