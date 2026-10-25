# 0001: Consume Aether lifecycle v1 as a bounded experiment

Accepted for this experiment, 2026-09-05. User requested resuming after the kernel handoff. BG-034 scope: independently authored sys-init conformance client, not production init.

Aether's `.planning/M4-LIFECYCLE-V1.md` now provides the fixed launch envelope, bootstrap registers, scoped factory rights, instance identity, retained terminal records, explicit cleanup/acknowledgment and finite workload required by our gate. Accept that subset for this experiment. BG-032/BG-033 remain open for general events, grants and supervisor recovery. Supervisor failure deliberately panics; readiness, arbitrary program loading, persistent recovery and SMP supervision remain unsupported.

Use Rust 1.98.0, no_std, x86_64-unknown-none with no Cargo dependencies for this client: its supported bare-metal toolchain fits the documented profile without a libc or shell. C remains a possible production choice; writing a second target runtime/toolchain setup would not improve this seam test. Python is host build/pack/test tooling, not a target dependency. Zig/QEMU and boot assets belong to the isolated Aether consumer test. These non-POSIX dependencies are justified only by the x86_64 Aether fixture; no portability claim follows.

Independently implement bootstrap validation, authority checks, nine-generation lifecycle, terminal retention and ordered cleanup. The kernel fixes worker outcomes, so this is conformance plus a small cleanup/observation policy, not configurable restart policy. Negative clients deliberately fault or expect the wrong terminal detail. Success requires the versioned kernel marker from our envelope; a negative image must fail rather than fall back to Aether's client.

Build/test in a private Aether source snapshot, pin its content and artifacts, and retain commands, logs and outcomes. Do not alter the companion checkout or share its mutable output directories. No claim of size/speed superiority or full init integration is warranted by passing.
