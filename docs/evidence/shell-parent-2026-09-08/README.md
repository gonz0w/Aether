# Bounded direct-launcher parent identity

Final qualification: 295 command cases, seven M4 cases and host/pin/workflow checks
(98 Python tests) pass on frozen sources. The new native-parent-identity selection
requires runner-local and rejects native threads. In connections mode, 0x1006e
returns parent zero for the kernel-loaded root supervisor and its computed identity
for workers. Unused registers follow the zero-argument musl ABI. Disabled modes
remain ENOSYS. No new state, parent table, authority or wire format.

Actual musl/getppid and generated dash init agree with supervisor identity 4 in
this fixture. Both worker placements pass two generations/four reclaims. Disabled
routing and self-PID substitution reject client104/owner1501. The old diagnostic
retains PPID=-38; user/group metadata and cwd are still unsupported. Capability
and cleanup regressions pass. Full main and consumer acceptance remain open.

Two attempts are retained:

- attempt-1: swapped backend received slot-derived argv=client and exited189;
  owner1500 rejected before client launch. The test launcher now preserves the
  backend worker argument for the swapped profile only.
- attempt-2: swapped guest completed with four reclaims, but the host oracle still
  expected original slot order. Its swapped-case expectation was corrected.

Original sources, results and logs are retained per attempt; all native and M4
run artifacts, including these attempts, are archived. An intermediate successful
host log is also retained. A formatting-tool edit to the shared supervisor was
reduced to the scoped argv change before final qualification; no broad reformat.
The kernel query itself did not change between these attempts.

Commands from repository root:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --command-runner --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/regression.py
python3 docs/evidence/shell-parent-2026-09-08/collect.py
```

The collector verifies prior packet bytes, final frozen sources, attempt source
archives and the simplicity snapshot, then verifies every archived target member.
qualification.json names retained runs/counts; manifest.json seals the packet.
See the [pre-code contract](../../NATIVE-SHELL-STARTUP.md#bounded-startup-identity-contract-review--2026-09-08)
for limits, ownership and test selection. No detached-parent/reparenting support,
authentication, sibling change, released-pin update or independent owner acceptance.
Next: explicit launcher-supplied compatibility user/group metadata, then scoped cwd.
