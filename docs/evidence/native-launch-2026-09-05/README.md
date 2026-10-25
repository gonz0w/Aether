# Bounded executable launch witness

2026-09-05: five launch cases, eleven existing memory cases and twelve frozen
userland consumer cases pass. Kernel host tests (including the three launch
input/layout tests), 44 Python tests and three standards checks pass. Default
two-core smoke and framebuffer acceptance pass after allowing QEMU's local socket.

[Owner contract and commands](../../NATIVE-LAUNCH.md) define the exact profile.
`summary.json` binds retained files; the launch/memory results bind sources,
commands, tools and image/serial digests. Consumer evidence retains the existing
owned adapter and sys-init I/O fixture commands. Large ELF/ISO artifacts remain
at the private paths in the reports. The new launcher is kernel conformance only;
consumer regression uses the previous profile and does not claim adoption of the
new launch ABI. No companion source or standards pin changed.
