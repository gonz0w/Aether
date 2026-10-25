# ABI29 startup identity input

abi29-startup.rs is copied verbatim from sys-init decision0194's sealed
`docs/evidence/abi29-dispatch-core-2026-10-21/startup.rs`. It is original Aether
BSD-2-Clause code and retains its SPDX notice. The complete56-member packet and
current maintained sibling source matched before copying. Pin/provenance:
`docs/evidence/filesystem-process-fds-2026-10-21/dependency-pins.json`; the process
checker also pins this source's exact SHA256 before compilation. No sibling code
is read during builds. Update only as an explicit new reviewed source input;
old sealed deliveries/evidence remain immutable.

This validates canonical labels and parents, not native authority/admission.
Trusted authenticated observations remain the dispatcher's responsibility.

## Kernel ELF parser snapshot — 2026-10-22

`native-elf-2026-10-22.zig` is the exact unmodified current
Aether/kernel/native_elf.zig, SHA256
`e3a2b1133af03dc3d835f0cc0f9a4bd0f8911d33e4c05edbfad05f8da696ee67`.
Original Aether source uses the shared BSD-2-Clause policy; root LICENSE applies.
Used only by host qualification of the actual shell ELF under unchanged default
limits. This snapshot does not change the kernel or a released standard/SDK pin.
