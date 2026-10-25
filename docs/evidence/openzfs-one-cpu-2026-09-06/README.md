# One-CPU modeled service view

The [contract](contract.md) precedes implementation; the
[assessment](../../OPENZFS-FEASIBILITY.md#one-cpu-service-view-result--2026-09-06)
records results and remaining requirements. This is Linux/glibc under x86_64 user
emulation. A modeled query is not host affinity, actual one-CPU scheduling or a
native resource-discovery API.

One warmup and ten measured fresh processes pass in each population (22 positive
storage runs). Default discovery reports nine online CPUs and reproduces 102
first-init/740 full-workload creates. The modeled one-CPU view observes 99/548.
Each population has stable per-name counts across its ten samples. These are
cumulative requests, not live thread counts, peak memory or native budgets.
comparison.json retains both populations' complete per-stage summaries and groups;
qualified/results.json retains all samples and engine-query counts. No latency
or RSS comparison is claimed. Host caches are not flushed; builds are excluded.

CPU_VIEW adds an atomic query counter and link wrapper for sysconf. Only
_SC_NPROCESSORS_ONLN returns one; other queries call the real function directly.
The counter resets immediately before the unchanged owned-file workload and must
be nonzero afterward. The aether-libzpool-cpu-view-v1 record reports modeled CPUs,
real host online CPUs and engine query count. Existing environment-v1 reflects
what the executable sees; demand/name schemas and fixture markers are preserved.
Counter accesses use relaxed atomics because they measure calls, not publication
of engine state or synchronization. No engine objects are shared via the counter.

Controls pass: modeled value, page/physical-page routing, invalid-query result and
errno, deliberately wrong two-CPU response (exit 2, exact one-CPU-view diagnostic),
existing count/name controls and test-only count ceiling. The CPU rejection runs
before media creation. The default observer self-check also passes. Both profiles
run the same storage success oracle; modeled-profile existing-file and wrong-byte
controls plus independent read-only zdb pass with unchanged positive media digest.
No source or target failures occurred: build and qualification passed first attempt.

All 98 Python tests, Zig host tests, three pins, workflow and scoped Clang format
checks pass. Original engine sources (4063 files) and static archives match the
previous retained identity. No sibling, kernel capacity, release-pin or worker
constant changed. No new native QEMU qualification is claimed for this host-only
change. Delay-dispatch and queue-ID limitations are source-review findings, not
newly implemented or fully exercised APIs.

## Reproduction and retained evidence

Use the [retained cross-tool build](../openzfs-runtime-budget-2026-09-06/README.md)
and image c48ba36c2b92494aa7ebfb957cce38a26792507e26ed24ae1fa010038da53c74
(GCC 14.2.0, QEMU 10.0.11). It is a pinned local prerequisite, not an exported
image or newly installed dependency. engine-identity.json binds the source/archive
comparison. Upstream notices and licenses remain unchanged; new observer code is
BSD-2-Clause. artifacts.tar.gz retains the source copies, recipe, objects and six
executables. qualified/sources.tar.gz and results.json bind exact runtime inputs,
artifact digests, commands, exit codes and UTC receipts.

build.mk uses read-only retained engine work at /work, source copies and recipe
at /inputs:ro, and fresh owned outputs at /out:rw. From the retained engine source
directory, run `timeout 120 make -f /inputs/build.mk observe`. The build log retains
expanded commands. The modeled builds add CPU_VIEW and --wrap=sysconf; the default
build omits both. No engine source is patched or reconfigured.

qualify.py is a one-off runner with exact local paths and a new qualified output
directory. Preserve prior attempts under distinct names before rerunning; do not
overwrite them. It runs the modeled population first and the default second,
so this is a functional sizing comparison, not a randomized performance study.
Container flags are --pull=never, --network=none, --read-only, dropped capabilities,
no-new-privileges, 2-GiB memory/512-pid limits and bounded tmpfs. No host device is
passed through. Guest/subprocess bounds are 90/120 seconds. Each positive creates
fresh private regular-file media; disks remain in the owned zig-out tree and their
hashes are retained. Setup/build and warmups are separate from the ten samples.

Next is a bounded actual-taskq dependency/drain witness, preserving distinct
progress paths and explicit delayed-dispatch failure before queue consolidation
or native capacity work. Rust service/platform ownership, live resource peaks,
persistence qualification and release acceptance remain open.
