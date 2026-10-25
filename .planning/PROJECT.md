# Aether project

This file owns product direction. [Root engineering policy](../PROJECT.md) owns
development decisions; [STATE](STATE.md#system-work-index) selects current work.

Source organization decision,2026-10-22: kernel, userland, sys-init and pkg-mgr now
share this repository. Keep Aether-standards separate, component responsibilities
and runtime authority boundaries intact, original histories and released pins
preserved. See [the repository guide](../docs/REPOSITORY.md).


Updated: 2026-10-19. VM direction accepted; first-release scope revised by the maintainer on 2026-09-06.

## Purpose

Build a new OS kernel to learn systems engineering and attract a community through a runnable, understandable POC. Explore whether a small capability kernel with explicit per-core ownership makes a useful foundation for cooperating services.

Aether's swarm is a collection of kernel instances on CPU cores or hardware threads, not a separate kernel per application thread. Measure the benefits and costs of that structure rather than assume superior performance or fault tolerance.

## Accepted direction

| Choice | Decision |
| --- | --- |
| Kernel ownership | New Aether kernel; no existing kernel as the native foundation |
| Structure | Capability microkernel with core-local state and explicit cross-core messages |
| Languages | Zig kernel, Rust user-space services |
| Initial CPU target | x86_64 |
| Device services and /dev | Accepted typed capability-routed providers and a scoped musl compatibility view; explicit bindings/small native Rust adapter first. [Design](../docs/DEVICE-SERVICES.md); [UP-08](ROADMAP.md#up-08--device-services-and-scoped-dev) supplies required shell/storage bindings before general discovery/hotplug/graphics |
| TTY sessions and seats | Accepted native Rust user-space TTY and musl typed controls; ncurses/terminfo leads application evaluation and libtsm later local emulation. [Design](../docs/TTY-SEATS.md); [UP-07](ROADMAP.md#up-07--native-tty-sessions-and-seat-boundaries) sequences required serial/session slices before general PTYs and graphical seats |
| Clocks and timers | Accepted source/event/UTC-policy separation, per-core deadlines and a coherent calibrated monotonic timeline; musl preserves API-specific clocks. [Design](../docs/CLOCKS-TIMERS.md); existing [SI-01](ROADMAP.md#si-01--native-wait-and-service-deadline-contract) coordinates UP-04 and required runtime/storage slices |
| Identity and permissions | Accepted capability-bounded access, service-enforced permission policy and a truthful musl credential view; existing UID/GID labels remain advisory. [Design](../docs/IDENTITY-PERMISSIONS.md); [UP-06](ROADMAP.md#up-06--identity-and-permissions-over-capabilities) sequences required slices before future authenticated multiuser transitions |
| Signals and interruption | Accepted native events for services and a scoped musl signal runtime with checked delivery/return, authorized targeting and explicit I/O interruption. [Design](../docs/SIGNALS.md); existing [UP-02](ROADMAP.md#up-02--native-shell-process-semantics-and-first-executable-workload) tracks required slices |
| Readiness and waiting | Accepted level readiness, capability-scoped bounded native wait-many and musl poll/select adapters. [Design](../docs/READINESS-WAITS.md); [UP-04](ROADMAP.md#up-04--readiness-and-native-wait-many) tracks required slices |
| Local sockets and descriptor passing | Accepted Unix sockets over native IPC/services; queued, authorized references preserve shared open instances. [Design](../docs/UNIX-SOCKETS.md); [UP-05](ROADMAP.md#up-05--unix-sockets-and-authorized-descriptor-passing) tracks consumer-driven implementation |
| Service I/O and device control | Accepted capability-authorized resource services, explicit completion/buffer lifetime and typed device control through the musl backend. [Design](../docs/SERVICE-IO.md); [UP-03](ROADMAP.md#up-03--service-io-completion-and-typed-device-control) tracks required slices |
| Descriptor ownership | Accepted per-process userland FD tables, shared open-file descriptions with one user-space owner, and capability-enforced native references. [Design](../docs/FILE-DESCRIPTORS.md); existing [UP-01](ROADMAP.md#up-01--inherited-file-ownership-and-composable-processfile-capacity) tracks implementation |
| C runtime and mapping backend | Accepted small musl port with an Aether-native OS backend; direct anonymous VM operations and service-authorized file/device backing. [Design](../docs/MUSL-VM-BACKEND.md); [VM-02](ROADMAP.md#vm-02--native-mapping-contract-and-musl-backend) follows the required VM-01 slice |
| Virtual memory | Accepted VM object/internal mapping/pmap separation; VM-object handles, balanced range tree, 4 KiB demand-zero and COW/shared/device backing. [Design](../docs/VIRTUAL-MEMORY.md); implementation queued as [VM-01](ROADMAP.md#vm-01--vm-objects-address-space-mappings-and-pmap) |
| Development machine model | QEMU q35 using software emulation as the reproducible baseline |
| Boot path | UEFI/OVMF in QEMU with Limine; versions pinned and validated during M1 |
| First public release | Boot through sys-init into interactive Zsh on the serial console, with a working runner, native package management and persistent OpenZFS filesystem |
| Physical graphics target | NVIDIA RTX 3060 in an x86_64 UEFI system |
| Graphics sequence | Boot framebuffer, user-space display service, physical framebuffer validation, then native NVIDIA display investigation |
| AI/compute | Later than graphics/display; no early CUDA compatibility promise |
| Persistent storage goal | Developer workstation with snapshots and recoverable system upgrades |
| Filesystem direction | Commit to retained upstream OpenZFS C behind an Aether-userland-owned Rust filesystem service for R1; Aether supplies native engine/block contracts. Deliver persistent shell/packages first; snapshot/rollback follows R1. Future engines may use the Rust service boundary through separately scoped work; general filesystem integration remains unqualified |

All components are built for Aether only (maintainer decision, 2026-10-22).
Other-OS product support and portability campaigns are out of scope. Host tooling
and POSIX conventions support development without expanding runtime targets.

## Release boundaries

The kernel mediates CPU execution, memory protection, capabilities, IPC, and essential hardware events. User-space services own work placement, supervision, and display composition. Begin with fixed resource pools, pinned tasks, static topology, and explicit boot grants.

The M1–M4 two-core graphical demonstration is an internal foundation, not the
first-release boundary. The first release requires the libc/process/descriptor/TTY
behavior needed by the selected real shell, external programs, runner and package
manager, plus persistent files and installed packages surviving reboot. An in-memory
filesystem, builtin-only prompt or host-only package assembly is an intermediate
checkpoint and does not satisfy this release.

The initial release console is serial in x86_64 QEMU, explicitly accepted by the
maintainer. Maintainer confirmation2026-10-19: the boot shell is Zsh; no interim
RAM-only shell image replaces the persistent target. Aether-userland owns Zsh and
its TTY/ncurses/startup integration (UL-008/009). Existing dash process/system-shell
evidence remains useful but cannot qualify interactive Zsh. Snapshot/rollback
stays post-R1 under the prior decision. Local package media/bundles suffice; networking is not a prerequisite.
A desktop, accelerated graphics, native NVIDIA modesetting, AI, dynamic membership,
live migration, SMT, gang/deadline scheduling and full-kernel formal verification
remain outside this release. RTX 3060 work remains a later direction.

Maintainer decision, 2026-10-18: commit to retained OpenZFS behind the Rust
service for R1. Persistent shell, runner and packages come first; snapshots and
rollback follow R1. The bounded native write/fresh-read result supports this
direction but does not qualify the complete service, filesystem operations or
consumer assembly. RAM-file fixtures remain intermediate evidence.

Graphics support must name its level: writing a framebuffer set up by firmware/bootloader is basic display output; programming connectors and modes is native display control; accelerated rendering and compute are additional capabilities.

## Success

A contributor can build and boot the release into its serial shell, run external
commands through the runner, install and run a package from local media, and
reboot with files/package state preserved. Capability-denial and worker-fault
regressions remain passing. Native state ownership and documented limitations
must match the delivered system, and starter tasks remain available.

Use the [architecture](../docs/ARCHITECTURE.md) for contracts and the [roadmap](ROADMAP.md) for completion criteria. Historical research is in the [archive](../docs/archive/README.md).

## Shared experience

Adopt Aether Experience v0.1.0 and the Hearth palette for new first-party user-facing work. `docs/EXPERIENCE.md` records the pin, scope and migration status. This shared presentation contract does not change kernel authority, service lifecycle, package state or upstream interfaces. Existing surfaces migrate through separately tested implementation work.
