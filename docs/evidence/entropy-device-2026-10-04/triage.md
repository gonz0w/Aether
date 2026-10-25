# Attempt1 retained

`zig-out/entropy-hyyhjm5s` passed the first9 device cases and all11 build
rejections. The actual stalled-backend case timed out at the external30-second
watchdog before reaching AETHER M1/ENTROPY readiness. A1-byte/60-second backend
quota also constrains firmware RNG consumption, so it cannot isolate the kernel
failure path. This is test setup failure, not a qualified entropy timeout pass.
Owned VM termination completed without forced kill. No backing was recycled.

The next attempt gives firmware and initial kernel draws64KiB before replenishment
at60seconds. The300-draw kernel workload exceeds that quota and must reach its
own exact bounded timeout after readiness. Preserve all first-attempt source,
command, artifact and raw logs; do not overwrite the failed report.
