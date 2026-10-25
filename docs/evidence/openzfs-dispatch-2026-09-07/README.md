# Fixed system/delay queue dispatch observation — 2026-09-07

The [contract](contract.md) now passes with the original engine and worker counts.
One warmup plus 10 measured processes per CPU view pass (22 processes, three engine
lifecycles each). Every measured final snapshot has the same counts in both views:

| External fixed-queue call | system_taskq | delay_taskq |
| --- | ---: | ---: |
| Normal dispatch / preallocated calls | 0 / 0 | 0 / 0 |
| Delayed calls | 0 | 55 |
| Delayed accepted / rejected | 0 / 0 | 0 / 55 |
| Explicit wait / wait-id / wait-outstanding | 0 / 0 / 0 | 0 / 0 / 0 |
| Cancellation / ENOENT | 0 / 0 | 113 / 113 |

[summary.json](summary.json) records all counter column names and measured ranges.
Raw records retain every lifecycle snapshot and creation/retirement counts. This
is external-call observation, not callback execution, required concurrency or
coverage of same-object/internal calls. In particular, destroy's internal queue
wait is excluded. The source review explains the deadman/timer and teardown paths.
The 68 eager fixed-pool workers had no observed accepted dispatch in this workload;
other engine queues continue to perform its storage work.

## Checks and boundaries

A synthetic check runs real normal and preallocated work on both fixed queues,
drains through real wait APIs and verifies four callbacks. Delayed dispatch returns 0
and executes no callback; cancellation returns ENOENT. Deliberately dropped counts
reject exact `DISPATCH FAIL: observer count`; fabricated delayed success rejects
exact `DISPATCH FAIL: delayed result`, both exit 2. The existing worker count/name/
CPU/overlap/role controls, new-file requirement, wrong-byte rejection and read-only
zdb traversal pass. All 98 Python tests, Zig/pins/workflow 39 and scoped C formatting
pass. The successful driver completes 40 qualification commands in 81.5 seconds.
No native QEMU kernel run is claimed: only host observer code changed.

Attempt 1 failed compilation because new external observer definitions lacked
forward prototypes required by upstream -Wmissing-prototypes. The exact source,
recipe, driver, partial outputs and build-1.log are retained. Adding declarations
fixes the build without suppressing warnings. Attempt 2 builds and qualifies;
no failed attempt is counted as a measured sample. Both source archives verify.

Original 4063 engine source files and 13 static archives are unchanged. Compiler,
platform and dependencies use the prior pinned offline image; execution.json and
qualified/results.json retain expanded commands, identities, UTC times and raw
logs. All qualified runtime sources remain frozen. No sibling, native grant/ABI,
worker default or release pin was changed. Native handoffs remain immutable.

## Reproduction and retained inputs

Use the pinned image/engine from the preceding role-attribution experiment with
this build.mk and qualify.py. Freeze host-runtime.c, host-dispatch.c, host-owned.c,
signature.c and build.mk under /inputs; mount the engine read-only at /work and a
fresh owned /out. From the engine directory run
`timeout 120 make -f /inputs/build.mk observe`, then from this repository run
`python3 docs/evidence/openzfs-dispatch-2026-09-07/qualify.py` with its explicit paths
and an absent qualified output. Start the existing runner only when stopped; keep
startup/build/qualification in one session if the VM follows the launch lifetime.
Do not restart a running VM. execution.json retains the actual confined invocation:
no network/capabilities, read-only engine/image, owned media/output/tmpfs, 2 GiB/512 pids,
90-second inner and 120-second per-run bounds. No disk/device outside private media
is used. Longer qualification has an 1800-second outer review bound.

artifacts.tar.gz retains final sources, inputs, objects, eleven executables and
recipes. qualified/ retains receipts/logs/source snapshot; private vdev.raw files
remain in zig-out with their recorded hashes and are omitted from evidence copies.
archive-check.json verifies final and failed source identity. review-inputs retain
unchanged upstream source/LICENSE/COPYRIGHT; new observer code is BSD-2-Clause.
The JSON counts array uses the columns in summary.json, in enum order; accepted
and rejected counts can lag calls at an in-flight snapshot.

**Next:** the private host-only two-pool reduction described in
[source-review.md](source-review.md), preserving distinct progress queues and
explicit timer limitations. This does not select native capacity, qualify a
production filesystem/deadman watchdog or change full R1 acceptance.
