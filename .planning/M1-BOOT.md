# M1 implementation plan: boot and framebuffer

Status: completed 2026-09-05. See [STATE](STATE.md) for measured results and [ROADMAP](ROADMAP.md) for the acceptance boundary. The work sequence below records the implemented milestone scope.

## Target and decisions

- Freestanding Zig kernel for x86_64, initially one CPU.
- QEMU q35, software emulation (TCG), OVMF UEFI, and Limine. TCG keeps the initial run path independent of host CPU virtualization support.
- Serial output is the machine-readable diagnostic path. A bootloader-provided linear framebuffer is the visible demonstration.
- No custom bootloader, Rust service framework, GPU driver, or multi-architecture abstraction in this milestone.

Limine supplies a documented [boot protocol](https://github.com/limine-bootloader/limine-protocol/blob/trunk/PROTOCOL.md), including framebuffer information. OVMF is part of [TianoCore EDK II](https://github.com/tianocore/edk2/tree/master/OvmfPkg); QEMU documents its [x86 machine targets](https://www.qemu.org/docs/master/system/target-i386.html). Pin exact compatible revisions during implementation rather than tracking these moving documentation branches at build time.

## Work sequence

1. Validate Zig and obtain QEMU, firmware, Limine, and required image-building tools through the environment's normal dependency workflow. Choose exact versions/revisions and record their origin/checksums where applicable. Keep firmware variable state disposable per run. Do not install or modify bootloaders on the host's disks.
2. Add only necessary build files, linker configuration, boot protocol declarations, x86_64 entry point, and serial/panic code. Suggested initial locations are `build.zig`, `kernel/arch/x86_64/`, `kernel/main.zig`, and `boot/`; create files only as used.
3. Boot to a clear serial marker and controlled halt. Confirm boot protocol support before interpreting response structures. Record memory-map entries and framebuffer metadata without treating arbitrary physical addresses as user authority. Reserve kernel, module, firmware/device, and boot-information memory appropriately; no general allocator is required yet.
4. Draw a deterministic pattern using the reported pitch, dimensions, bits per pixel, and color masks. Bounds-check arithmetic and validate the supported format before writes. Reject missing/unsupported framebuffer information explicitly rather than assuming a fixed layout.
5. Add a bounded headless serial smoke check and a graphical run path. Use one documented successful configuration; test the failure/timeout path as well so a hang or missing success marker fails the check.
6. Inspect visible output, document setup and verified commands in README, and update STATE with exact results and remaining limitations.

## Implemented command interface

`zig build`, `zig build run`, and `zig build smoke` provide image build, graphical run, and automated boot checking. `zig build test` checks framebuffer safety and failure detection. See [README](../README.md) for setup, dependency pins, and the intentional-panic test.

## Completion evidence

- A clean build produces a bootable image without undocumented local files.
- The selected UEFI/QEMU configuration reaches the success marker within a fixed timeout; launch failure, panic, and missing markers fail the smoke check.
- The framebuffer pattern is visibly correct, with dimensions and pixel format matching reported metadata.
- Panic or invalid boot information produces useful serial diagnostics.
- Document privileged bring-up shortcuts and prevent them from becoming user-accessible APIs. Framebuffer drawing moves to user space in M4.

No user-mode isolation or swarm claim is made by M1. After these checks pass, move to M2; do not expand M1 into native NVIDIA support.
