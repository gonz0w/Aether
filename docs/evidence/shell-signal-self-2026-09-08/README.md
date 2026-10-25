# Private bounded self-delivery

Before implementation: add private trap 0x29002 to the opt-in action experiment.
RDI is a bounded self signal (1–31 excluding 9/19), or zero to poll; remaining
arguments must be zero. Post coalesces in the caller's existing owner state.
Deliver at most one unmasked custom handler per explicit trap. Ignore discards;
default termination/job control returns ENOTSUP without consuming pending state.
No automatic mask-return, timer or transport entry, public kill, remote authority,
new terminal kind or consumer adoption is included. Those remain later gates.

Reuse the checked frame builder, existing mask and owner pending bitmap. A failed
frame preparation must retain the post; commit only after validated preparation
under IF=0. No allocation, retained user pointer, new service or quota increase.
Explicit poll is the smallest executable integration step; automatic delivery
would introduce unqualified transport reentrancy. No obsolete path is removed yet.

Test native blocked duplicate posts, one delivery after unmask/poll, exact handler
signal/mask and return restoration, ignore, invalid/default rejection, and fresh
pending state across two generations. A skipped-poll control must fail the
same client oracle. Run full command suite, M4 and host/pin checks on frozen
sources. Preserve attempts. Rust unchanged; existing C formatting stays scoped.

Reproduce from the repository root:

```sh
python3 scripts/launch_smoke.py --command-runner --libc-build /absolute/strict-sdk --tools-lock /absolute/native-tools.lock.json
python3 scripts/regression.py
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

This run uses the read-only Aether-userland/build/native-c-5olokhku SDK and
zig-out/init-capacity-2026-09-06/tools.lock.json. Harness receipts retain tool and
source hashes, exact commands, artifacts and raw serial logs. collect.py verifies
the previous peer packet and simplicity snapshot, archives the final source and
target bytes, and checks every archive member. No sibling writes or pin changes.

Results: all 252 command-runner cases, seven M4 regressions and host/pin checks
(98 Python tests) pass. The new positive completes two generations and four
reclaims; skipped poll rejects at client91/owner1501/reclaimed0. Runtime sources
remained frozen. No failed or interrupted attempts occurred. Formatting and
scoped whitespace checks pass. This is explicit self-delivery qualification only;
native mapping-failure/retry, automatic delivery, signal termination and full
dash/consumer acceptance remain open.
