# Native service retirement and TSD

Private producer qualification passes,2026-10-05. The
[packet](evidence/native-service-retirement-2026-10-05/README.md) and
[before-code scope](evidence/native-service-retirement-2026-10-05/contract.md)
extend the [real musl service witness](NATIVE-SERVICE-MUSL.md) with actual
thread-specific data/destructors and confirmed detached cleanup. Production
musl remains userland-owned; this adds no kernel/public ABI or SDK.

Six fresh final native cases cover joinable/detached TSD, descending82/two worker
completion, parked stop/replacement, actual removed destructor traversal351 and
premature unmap352. Mapping cost remains66/34 eager-backed pages per pthread,
with1024-byte actual TSD, two/four destructor calls and two retained allocator
pages. Full137 Python/Zig/Rust/pin/workflow checks pass. Both attempts remain;
archive readback precedes removal of only owned verified duplicate output.

From a fresh owned root, run the packet's `sdk-setup.py` then `qualify.py 1`, and
`zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`.
The primary must select any pending request, permit native exit, confirm the exact
ID stopped, then unmap/retire using saved metadata. It never dereferences an
unmapped TCB. Pending requests cannot authorize backing reuse.

Primary-driven reaping is an experiment, not engine startup or blocked-creator/
worker-origin concurrent progress. Native providers, feature/runtime closure and
measured peak, calibrated monotonic/UTC, production/independent consumer acceptance
and assembled R1 remain open. No companion SESSION handoff is delivered here.
