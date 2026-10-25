# Native pending-signal frame retry

Before implementation: existing executable mappings are immutable, so invalidating
an installed handler would require changing the memory contract. Instead exercise
native frame preparation at invalid user stack positions, then retry on the normal
stack. Post once while blocked, unmask, reject repeated polls without changing the
record/mask or running a handler, then deliver exactly once without reposting.
A negative client deliberately discards the pending occurrence before retry and
must fail at client92/owner1501. Repeat through two generations and four reclaims.

Reuse the existing private self trap and frame bounds; no kernel change, mapping
relaxation, new authority, allocation or public interface. The naked C probe saves
its real RSP in r11, invokes the synchronous trap with an invalid RSP, then restores
RSP before returning; no C stack access occurs on the invalid stack. IF=0 owner
serialization and checked frame publication remain unchanged. This is the smallest
native retention experiment; broader automatic delivery remains deferred.

Select full command and host/pin checks, plus scoped C compile warnings and diff
checks. Existing C formatting is preserved; no Rust/Zig source changes. Fresh M4
is not required for a fixture-only change; prior self-delivery M4 evidence remains
scoped to its recorded bytes. Freeze runtime/fixture/harness sources during runs.

Reproduce from the repository root:

```sh
python3 scripts/launch_smoke.py --command-runner --libc-build /absolute/strict-sdk --tools-lock /absolute/native-tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The read-only SDK is Aether-userland/build/native-c-5olokhku; the retained lock
is zig-out/init-capacity-2026-09-06/tools.lock.json. Harness receipts capture
commands, source/tool hashes, target artifacts and serial output. collect.py
verifies the prior self-delivery packet and simplicity snapshot and every archived
source/artifact member. No sibling repository was modified.

Results: all 254 command-runner cases and host/pin checks (98 Python tests) pass.
The positive completes two generations/four reclaims; intentional discard fails
exactly at client92/owner1501/reclaimed0. Sources stayed frozen; there were no
failed or interrupted attempts. Scoped whitespace checks pass. This qualifies
invalid-stack retention/retry, not automatic delivery or signal termination.
