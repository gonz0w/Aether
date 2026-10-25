# Real musl service-origin creation

Private producer qualification passes,2026-10-05. The
[packet](evidence/native-service-origin-2026-10-05/README.md) and
[before-code scope](evidence/native-service-origin-2026-10-05/contract.md) extend
[worker-driven cleanup](NATIVE-SERVICE-REAPER.md) with actual musl worker-origin
creation and concurrent preflight. Two creator workers each create40 detached
peers within82 service slots; small companions use one creator/one peer. A single-
creator service variant creates81. Creator masks, exact native origins, TSD,
independent parent state and confirmed cleanup while the primary joins pass.

Creation completes before cleanup. Upstream list-lock ownership serializes clone/
publication; atomic admission counters support concurrent preflight reads. Dynamic
overlapping creation/reuse remains unsupported. Ten fresh final cases include
old joinable/reaper regressions, ordinary/single/reverse origin and parked stop/
replacement, plus parent-only359, actual wrong-grant clone360, early-unmap352 and
omitted-primary-park356. Full137 Python/Zig/Rust/pin/workflow and scoped checks pass.
Both attempts, including the negative-variable compile failure, remain sealed
before owned duplicate cleanup. No kernel/public ABI/SDK, sibling, quota or pin
change. All82/two slots include the creators; this is not82 detached engine workers.

From a fresh owned root run the packet's `sdk-setup.py`, `qualify.py 1`, then
`zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`.
Production runtime/reaper resource cost, dynamic lifetime/progress, actual engine
providers/configuration, calibrated clocks, feature closure/startup/peak and
independent consumer/R1 acceptance remain open. No companion SESSION is delivered.
