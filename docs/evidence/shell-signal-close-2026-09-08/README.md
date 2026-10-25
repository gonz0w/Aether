# Handler entry and nonlocal exit after ambiguous close

Before implementation: close the last input alias before copying, with malformed
or truncated owner replies. Local descriptor/binding retirement must precede handler
entry even though close is ambiguous. Check absent fd10, zero input alias count and
retired local binding inside the handler; attempted I/O remains poisoned/no-traffic.
Returning and siglongjmp handlers must both permit remaining local cleanup. Repeat
close must report EBADF, never resurrect the alias. Owner verifies zero copy/read
positions, backend/channel cleanup and two generations/four reclaims. A fixture
resurrection control must fail client100/owner1501.

Reuse the poisoned handler and existing close contract; no kernel or protocol change,
authority, allocation or quotas. Add only the early-close byte oracle to the existing
Rust owner; ordinary unknown-close expectations remain unchanged. This is smaller
than a new recovery protocol, and does not resolve arbitrary partial-request or
public signal adoption. Static jump storage remains authoritative for nonlocal cases.

Select full command and host/pin suites, Rust1.98.0 edition2024 formatting, strict C
compilation and scoped whitespace checks on frozen sources. Preserve attempts,
pins and siblings. Kernel unchanged: no fresh M4 claim beyond prior scoped evidence.

Reproduce from the repository root:

```sh
python3 scripts/launch_smoke.py --command-runner --libc-build /absolute/strict-sdk --tools-lock /absolute/native-tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

This run uses read-only Aether-userland/build/native-c-5olokhku and retained
zig-out/init-capacity-2026-09-06/tools.lock.json. Receipts retain commands, sources,
tools, artifacts and serial logs. collect.py verifies the previous poisoned-jump
packet, simplicity snapshot and every archive member before sealing.

Results: all 284 command-runner cases and host/pin checks (98 Python tests) pass.
All four close positives complete two generations/four reclaims. Alias resurrection
rejects client100/owner1501/reclaimed0. Sources stayed frozen; no failed or
interrupted attempts occurred. Rust format and scoped whitespace checks pass.
Public/raw routing, consumer adoption and arbitrary partial-request cancellation
remain unqualified.
