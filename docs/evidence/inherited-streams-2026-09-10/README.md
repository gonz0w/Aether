# First inherited-stream witness — 2026-09-10

The bounded copied child now inherits the real startup descriptor table and gets
fresh connection-local stream references. Parent and child use public read, close
and fcntl through the existing conformance adapter; the separate Rust backend
remains the owner of stream bytes. The Rust supervisor owns the shared input
position and final-holder accounting. Neither numeric FDs nor reference values
supply ambient authority.

The [pre-code selection and local records](../../NATIVE-SHELL-STARTUP.md#first-inherited-stream-witness-implementation--2026-09-10)
define this first slice. Both continuations wait for owner completion after child
rebinding acknowledgment. Parent a, child b, parent c demonstrate one read position.
After all parent aliases close, the child still reads d, locally closes FD 0 and
reads e through its saved FD 10. CLOEXEC survives inheritance; clearing it in the
child leaves the parent's flag set. Each of the three backend bindings closes only
on the final process holder. Terminal order is source0=71, child2=72, backend1=17
for each of two generations; all six workers and their channels are reclaimed.

All 25 connections cases, five launch cases, seven M4 cases and 431 command cases
pass: 468 target cases, alongside 98 Python host tests and Zig/pin/workflow checks.
The full command suite took 1,441.59 seconds, within its 1,800-second budget.
The two deliberately broken owners fail with the named outcomes: private child
position rejects1903 on b, premature backend close rejects1952 on d. Both require
zero reclaims. The owner images are 5,416 / 5,432 / 5,416 bytes, below 8,192.

The existing signal-mask guard requires native-runner-local. Composing it with
native copy exposed a fixture completion check that assumed four reclaims; the
kernel now preserves the copy profile's six-reclaim expectation. This is the only
kernel change: no new syscall, pool, authority rule or public SDK operation. The
broader command and M4 suites were selected because this check is shared. All 22
prior connection payloads match their prior report hashes and bytes outside the
exact fresh entropy interval [32,80). runtime.patch records the scoped source delta.

## Retained failures

- Attempt 1: Rust formatting/parser failure because `gen` is reserved in edition
  2024. The exact source and diagnostic are retained. Renamed to `generation` and
  the pinned formatter passed. No native run occurred in this attempt; no outer
  timestamp receipt was captured for the initial formatting command.
- Attempt 2: native product/profile failure in connections-suite-e3ysjchd. The
  first 22 cases passed, then source250/owner1950 rejected before copy because
  the reused startup adapter's mask guard was not enabled. Exact sources, report,
  log and timing are retained. Enabled the existing guard and corrected the copy
  completion composition as described above.
- Attempt 3: test-oracle failure in connections-suite-p9t_8zh4. The first guarded
  generation completed source71 and child72, then backend17/owner1953 rejected.
  The existing C bridge translates Rust service success0 to exit17; the new oracle
  incorrectly expected0. Exact source/report/log/timing are retained. Corrected
  only that expected status; the backend implementation remains unchanged.

This is a conformance witness, not a general descriptor-inheritance service or
installed SDK fork hook. The table is the exact tested initial layout, with custom
signal delivery disabled; signal-held preparation and arbitrary-table acceptance
are not implemented. Malformed records, omitted completion gates, copy and
post-publication failures, confirmed-stop cleanup and shared uncertainty poisoning
still need direct controls and recovery behavior. Public fork/exec/wait, pipes,
full dash, OpenZFS and assembled R1 remain unfinished. Independent owner acceptance
and extended test coverage remain pending. No sibling files or released pins changed.

The collector checks final source hashes, the previous packet manifest, scoped
changes, the pinned simplicity extension, and archive member readback. Failed
attempt sources and target directories are retained alongside final artifacts.
Per-suite timing records contain exact commands, UTC timestamps and exit status;
reports identify tool and SDK digests. Format/syntax and compatibility receipts
are separate from runtime acceptance. The final manifest binds the packet.

Reproduction uses the existing entry points:

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

Archive readback verified 231 final source files and
10,423 target artifacts, including both failed native directories
and the extracted musl headers/COPYRIGHT.
