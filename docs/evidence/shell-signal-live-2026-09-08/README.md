# Signal termination with live command resources

Before implementation: reuse the existing abnormal command lifecycle hooks before
copy, after an 11-byte copy, and after a 16-byte diagnostic prefix. The client
self-terminates with signal15 through the private signal-capable profile instead
of executing UD2. Retain kind4/detail15 through repeated observe/idempotent stop;
verify exact backend bytes, retire live backend handles, close channels, reclaim,
reject stale handles and repeat across two generations/four reclaims.

Use existing client hooks and owner cleanup without kernel changes, new service
policy, allocation, quotas or authority. This is simpler than a new cancellation
protocol. No in-flight partial request or asynchronous handler interruption is
claimed: hooks execute between completed transport operations while descriptors
are still live. Corrupt-prefix and skipped-backend-close controls must reject at
owner1505 and1506 respectively after signal15 termination, reclaimed0.

Run full command and host/pin suites on frozen sources, Rust1.98.0 edition2024
format and scoped diff checks. Prior M4 evidence remains scoped to unchanged
kernel bytes; no fresh M4 is needed for fixtures/harness only. Existing C style is
retained. Preserve attempts, pins and sibling repositories; no consumer adoption.

Reproduce from the repository root:

```sh
python3 scripts/launch_smoke.py --command-runner --libc-build /absolute/strict-sdk --tools-lock /absolute/native-tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

This run uses read-only Aether-userland/build/native-c-5olokhku and the retained
zig-out/init-capacity-2026-09-06/tools.lock.json. Harness receipts bind commands,
tool/source hashes, artifacts and serial logs. collect.py verifies the previous
termination packet, simplicity snapshot and every archived source/artifact member.
The existing Rust owner is unchanged and checked with rustfmt1.98.0 edition2024.

Results: all 262 command-runner cases and host/pin checks (98 Python tests) pass.
The three signal15 positives each complete two generations/four reclaims.
Corrupted prefix and skipped backend close reject after kind4/detail15 at
owner1505/1506 respectively, reclaimed0. Source hashes stayed frozen; no failed
or interrupted attempts occurred. Rust format and scoped whitespace checks pass.
This qualifies live-descriptor cleanup between operations only.
