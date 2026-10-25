# Native service musl storage

Private producer qualification passes, 2026-10-05. The
[packet and before-code scope](evidence/native-service-musl-2026-10-05/README.md)
exercise actual pinned musl pthread/TLS and allocator behavior under the existing
[owner-local worker profile](NATIVE-SERVICE-WORKERS.md). Production musl remains
Aether-userland-owned. This does not implement VM-01/VM-02 or a new SDK/ABI.

Four final native cases pass:82 simultaneous joinable pthreads, full-owner park/
wake/stop/replacement, actual self-pointer rejection and guard #PF/replacement.
Each service mapping costs66 eager-backed pages for256 KiB requested stack, actual
TLS/TCB and4 KiB inaccessible guard; each small peer mapping costs34 pages. Exact
grant accounting, TLS/errno isolation,240 KiB synthetic touched stacks, failed
realloc byte preservation, joins and two retained allocator pages qualify this
fixture. It does not measure engine stack high-water, native peak or final capacity.

From an empty owned output root, run the packet's `sdk-setup.py`, then
`qualify.py 1`, and `zig build test --cache-dir .zig-cache --global-cache-dir
.zig-cache/global` from the repository root. Recipes require pinned offline musl/
compiler/firmware inputs. All failures and actual commands/artifacts are retained;
archive readback precedes cleaning this run's verified duplicate output.

All eleven accepted2026-10-04 designs were reviewed. They preserve the bounded
storage-first sequence and capability enforcement below musl, while keeping VM
objects/mappings/pmap separate and resource/FD/TTY/device policy in user space.
HO-01 remains provisional post-R1 research. Existing eager memory/grants and
virtual ticks are not relabelled as general VM or calibrated time.

Next actual engine runtime/feature closure and provider identity/configuration,
including required detached/TSD/thread/heap behavior, before native startup/fini/
restart and grant-bound persistence. Production SDK, calibrated clocks/UTC,
independent reader/consumer acceptance and assembled boot-to-shell remain open.
