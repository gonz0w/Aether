# Queued wrong-version body teardown

All360 command cases and host/pin/workflow checks (98 Python tests) pass on final
frozen runtime sources. One failed earlier attempt is retained below.

This experiment targets consumer metadata row07 in both V1/V2 directions. A
fixture-only hook acknowledges the consumed header with an exact generation-tagged
record. The owner queues16 body bytes in one native write. The hook consumes one
marker byte, then the unchanged version check rejects with15 body bytes unread.
No remaining body bytes are decoded or drained by the client. The owner closes
its writer and requires terminal110, unpublished descriptors/metadata, no additional
client traffic, untouched backend streams and four reclaims across two generations.
A wrong-marker control requires client108/owner1501 and makes no reclamation claim.

This is bounded native disposal/reuse evidence, not direct inspection of physical
queue bytes or arbitrary parser fuzzing. Existing host channel zeroing and stale
handle tests remain complementary. No normal decoder behavior, kernel, sibling,
SDK default, released pin or upstream object change; no fresh M4 run is selected.
Existing C formatting and Rust edition2024 remain in use.

## Retained failed attempt

`command-runner-suite-i0ea5smr` passed71 cases before the first queued-body case
failed with owner1595. The harness labels its report incomplete, but the serial
log identifies an assertion failure, not a timeout or missing runner. Review found
the owner requested32 bytes and asserted32 returned; native calls cap transfers
at16 even though queue capacity is32. The correction requests/asserts16 and uses a
16-byte buffer, leaving15 unread bytes. No kernel limit was changed. The failed
attempt report, full artifacts, logs, preflight host log and frozen source archive
are retained. It is not accepted cleanup evidence.

## Reproduction

From the repository root:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --command-runner --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
rustfmt +1.98.0 --edition 2024 --check user/native-command/cat-roles.rs
python3 docs/evidence/shell-queued-body-2026-09-09/collect.py
```

The collector verifies the predecessor packet, final runtime source hashes and
simplicity snapshot, and reads back archived source/target members. The recursive
manifest seals the packet. See the [pre-code selection](../../NATIVE-SHELL-STARTUP.md#queued-wrong-version-body-selection--2026-09-09).
Userland must independently reproduce matching artifacts before extending its
acceptance. Actual-main secure ENV and exec/wait remain the next shell work;
persistent filesystem integration remains open.
