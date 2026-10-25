# Companion project boundaries

> Shared-standards migration, 2026-09-05: [Foundations adoption](STANDARDS.md) now routes the canonical shared ownership, interface and evidence rules. Domain mechanisms and exact implementation contracts below remain owned by this project. Shared-rule changes belong in a new standards release; adoption does not change implementation status.

Reviewed: 2026-09-05. The subsequent [BG-025 runtime checklist](research/AETHER-RUNTIME-CONTRACT.md) inspects newer M3 cross-core IPC progress and M2 lifecycle code; use it for current native-runtime detail. Proposed responsibility boundaries and open questions, based on local documentation. No cross-project runtime was tested or interface accepted during this review.

| Project | Proposed responsibility | Evidence reviewed |
| --- | --- | --- |
| Aether | Kernel objects, authority, task lifetime, IPC, loader and boot/runtime facilities | [README](../../README.md) |
| sys-init | Service lifecycle policy, ordering, readiness, supervision, operator diagnostics and recovery | [Project direction](../.planning/PROJECT.md), [earlier research](RESEARCH.md) |
| pkg-mgr | Artifact staging, package metadata and ownership, eventual install/update/remove policy | [README](../../pkg-mgr/README.md), [integration proposal](../../pkg-mgr/docs/ARCHITECTURE.md) |

Aether currently documents an x86_64 capability multikernel with a Zig kernel and Rust user-space experiments. Its README reports M1/M2 checks and a kernel two-CPU probe, while arbitrary executable loading remains unsupported. This does not yet supply a demonstrated POSIX process environment for sys-init. POSIX-facing distribution goals need an explicit mapping onto native tasks, capabilities, and user-space services.

pkg-mgr documents a local text-file staging fixture and metadata helpers, without an installed-package database, user-facing CLI, binary installer, or Aether runtime integration. Its proposed boundary separates inert service artifacts from activation. That is useful input for a shared contract, not an existing API.

| Contract question | Coordination owner | Tracking |
| --- | --- | --- |
| What starts the first service, and what authority does it receive? Is Unix PID 1 a compatibility role? | sys-init + Aether | BG-025; OQ-001 |
| How are task identity, exit, orphan ownership, cancellation, clocks, and capability revocation represented? | sys-init + Aether | BG-025 |
| Which console, filesystem, executable loader, shell/libc, logging, device, and shutdown facilities exist or must be supplied? | Aether + sys-init | BG-025, BG-003, BG-015 |
| What artifact/schema is validated before enablement, and how are service IDs and package ownership mapped? | sys-init + pkg-mgr | BG-027; OQ-002 |
| Who changes enablement, requests restart/reload, and handles failed upgrades/removal? What does rollback actually restore? | sys-init + pkg-mgr | BG-027 |
| Which experiment can run on a POSIX host, and which guarantees require target evidence? | all three projects | BG-017, BG-025, BG-027 |

Coordination owners identify where agreement is needed; they do not imply commitments by the companion repositories. Future answers must cite a concrete document or implementation revision, state missing behavior, and define a contract test. No fork/exec/wait, ambient root, Linux control API, or target shell should be assumed from the product's POSIX goal alone.

## Package evidence refresh

The subsequent [BG-027 proposal](research/PACKAGE-SERVICE-CONTRACT.md) reviews pkg-mgr's newer staged package records, ownership/dependency views and strict validators. This supersedes the earlier prototype description above for current package-state detail. Live update/remove/activation and full executable file metadata remain unimplemented. The proposal defines semantic questions, not an available shared API.

## Boot/runtime refresh and waiting boundary

The [boot/layout handoff](research/BOOT-AND-LAYOUT.md) records Aether's subsequently reported M3 completion and pkg-mgr's boot-artifact transport evidence. Those advances do not yet establish sys-init launch, lifecycle, rescue or filesystem APIs. Pause dependent native implementation until the listed contracts are available; independent readiness/schema research remains useful.

## Lifecycle v1 consumer result

The subsequent [BG-034 experiment](LIFECYCLE-V1.md) lifts the native wait for a bounded fixed-image lifecycle client. Our supplied client passes the nine-cycle Aether profile and two negative controls in an isolated kernel snapshot. Decision 0001 accepts only that subset; general loading, readiness, recovery and POSIX integration remain open. Use this report and its pinned kernel contract for current native evidence.
