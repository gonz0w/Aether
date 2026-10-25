# Device services discovery and scoped /dev

Status: accepted architectural direction, 2026-10-04, by the maintainer after
the device-service and /dev review. General implementation remains queued/partial
under [UP-08](../.planning/ROADMAP.md#up-08--device-services-and-scoped-dev).
[STATE](../.planning/STATE.md) records progress. Accept typed capability-routed
native device services and a scoped POSIX compatibility view. Exact protocols,
production service ownership/placement, bounds and deferred features require
scoped implementation contracts and matching consumer evidence.

## Decision and responsibility

Separate hardware discovery, native device access and compatibility naming.
Native clients use delegated resource/service interfaces directly. Musl resolves
supported /dev names within the caller's actual namespace authority, acquires an
authorized resource reference and installs a process-local descriptor binding.
The [descriptor](FILE-DESCRIPTORS.md) and [service I/O](SERVICE-IO.md) contracts
then govern aliases, operations, completion and cleanup. /dev is a compatibility
projection of authorized providers; it is not the native authority foundation.

| Responsibility | Direction |
| --- | --- |
| Hardware enumeration and resource assignment | Trusted bootstrap/bus resource owner identifies hardware and delegates bounded MMIO/PIO, IRQ and DMA resources |
| Device operation and state | One authoritative driver/resource owner exposes typed, versioned operations and enforces rights, bounds and lifetime |
| Discovery and connection policy | Scoped owner publishes permitted provider information and authorizes acquisition within an explicit delegation ceiling |
| POSIX namespace and FD adaptation | Musl/runtime uses authorized namespace lookup and descriptor references; enforcement remains below libc |
| Startup and recovery policy | sys-init supervises selected services and arranges agreed startup/dependency grants |
| Artifact and installation policy | pkg-mgr installs selected bytes/records; installation does not activate drivers or create hardware authority |

Kernel mechanisms protect mappings, resource grants, IPC, interrupt delivery and
execution. Prefer Rust user-space drivers/services where practical, retaining
essential kernel mechanisms and current bounded Zig hardware fixtures. This
decision does not migrate existing drivers or create one process per device,
provider, pseudo-device or open instance. Per-core state stays local; cross-core
clients message the authoritative owner rather than mutate remote state.

Aether owns native enforcement and its fixtures. Aether-userland owns its assigned
musl/runtime and package/consumer work. General device/namespace/driver production
service placement and project ownership require explicit affected-owner agreement;
accepting a native Rust adapter does not transfer an unassigned subsystem. Keep
sys-init supervision distinct from hardware binding/access policy. Scoped services,
drivers and hardware remain trusted for properties they enforce; user-space
placement is not proof of isolation from DMA or exclusion from the system TCB.

## Delegated discovery and open

Device paths, class names, PCI IDs, serial strings, numeric object/device IDs,
major/minor metadata and advisory UID zero do not confer authority. Distinguish
permission to inspect/enumerate metadata, permission to acquire a client session,
data/command access, device-backed mapping and device administration/reset.
Publication must be bound to an authenticated authorized provider; a worker cannot
self-register a foreign device or spoof an owner by supplying a name or label.

Begin with explicit inherited provider references or a bounded namespace binding.
A delegated namespace may authorize acquisition of new sessions within a defined
provider/resource/rights ceiling. Each successful open uses that authority and
applicable owner policy; discovery metadata alone cannot authorize the connection.
Child references never widen scope or rights. The enforcing owner validates caller
binding, current provider generation, supported operation and capacity before effects.

Lookup and reference acquisition must coordinate with the authoritative namespace/
provider state and concurrent removal or replacement. A prior path existence or
access check is insufficient. Root/cwd and directory-relative traversal follow
[identity and namespace rules](IDENTITY-PERMISSIONS.md#directory-references-and-safe-pathname-operations),
including parent steps, symlinks and crossings. A bounded boot binding may precede
the general filesystem namespace; it must state its narrower lookup contract.

Different process views may expose different authorized providers under the same
compatibility name. Scope is explicit in the held namespace/relationship, not a
global pathname convention. Copying or installing a node and inventing major/minor
values cannot mint access. Any future mknod adaptation must preserve already
delegated authority; deny unauthorized requests and report unsupported operations
honestly. Do not promise Linux device-number or ioctl ABI compatibility.

## Minimal compatibility view

Publish only supported entries needed by actual consumers. A shell need not receive
raw disk or GPU-administration access. A filesystem service can receive a bounded
block region directly; a graphical session later receives selected display/input
connections with separate data, mapping and control rights.

| Entry or class | Contract when enabled |
| --- | --- |
| /dev/null | Reads return EOF; successful writes discard the actual accepted byte count, with supported descriptor and access semantics |
| /dev/zero | Reads supply zero bytes; anonymous allocation and any supported mapping use the VM contract rather than physical-memory access |
| /dev/tty | Resolve the caller's authorized controlling-terminal relationship under the TTY/session contract |
| /dev/console | If needed, resolve the explicitly delegated normal console; this cannot expose the emergency kernel diagnostic bypass |
| Random-device entries | Bind a qualified randomness provider with declared readiness, failure, partial-progress and lifetime semantics |
| Block/display/input entries | Expose only explicitly authorized providers and the operations qualified for their consumers |

Reuse the [TTY/session direction](TTY-SEATS.md) for terminal modes, readiness and
foreground policy. /dev/tty cannot select another terminal by name. Pseudo-devices
may share a reviewed implementation/runtime boundary, but their resource references
and effects still obey the supported descriptor and enforcement contracts.

The [entropy transport](ENTROPY-DEVICE.md) and [native entropy](NATIVE-ENTROPY.md)
receipts establish only their named profiles. Transport completion alone does not
establish a production randomness provider or general random-device namespace.
Prefer a supported provider operation for getentropy/getrandom-style consumers;
compatibility aliases need separately declared behavior. Missing or unready
randomness cannot become a fixed/time/PID seed, assumed-ready RDRAND source,
unchanged output presented as success, or fabricated entropy-quality claim.

Exclude /dev/mem and /dev/kmem from ordinary process views. Device mappings obtain
approved device-backed [VM objects](VIRTUAL-MEMORY.md), ranges, rights and cache
attributes through the owner; no arbitrary physical-address mapping interface
follows from a device FD. [Native block](NATIVE-BLOCK.md) region grants constrain
storage access independently of filename selection. Flush completion remains its
declared device contract, not filesystem transaction or power-loss durability.

Xorg/Mesa need actual device-specific operations, buffer mappings, synchronization
and seat contracts. Typed commands and device-backed VM supply foundations without
claiming Linux DRM compatibility, NVIDIA support or acceleration.

## Generations removal and outstanding work

Distinguish physical-device identity, selected driver/provider generation and
client/open-instance identity. Hardware identifiers are discovery inputs and can
be untrusted; a stable label or identical pathname does not authenticate a new
driver or authorize a different physical device. Driver restart or hotplug must
not silently retarget existing references to a replacement generation.

Removal/restart rejects new admission and reports disconnection/failure through
the declared session contract. New lookup may acquire a new generation only under
the explicit binding/policy for that target. In-flight outcomes remain known,
partial or unknown as actually observed; lost replies cannot become success or
blind replay of writes, control commands or shared-position effects.

Closing an FD, withdrawing publication, revoking a grant, stopping a driver,
detaching CPU mappings and proving DMA quiescence are distinct obligations. Keep
needed resource/buffer references until outstanding operations and device access
are accounted for. A timeout or driver acknowledgment alone cannot authorize
memory reuse or seat handoff. Without qualified containment/quiescence, retain
backing and fail closed under the scoped fixture's declared failure policy.
Device-specific reset/recovery and IOMMU isolation need their own evidence before
broader caller access or physical-hardware claims.

Bound published records, client sessions, pending operations, observation retention
and queued notifications. Exhaustion must fail explicitly without partial authority
publication or leaked references. Independent userland/native witnesses must cover
foreign/stale authority, open/remove races, alias cleanup, malformed commands,
partial/unknown results and resource exhaustion for each enabled tier.

## Static bindings first and deferred discovery

Start with explicit boot-time provider bindings for the selected consumer. Sys-init
orders startup and observes actual service readiness; a discovered device or
published record is not proof of a ready service. Package installation remains
distinct from driver selection, resource delegation and activation.

Later dynamic discovery uses a bounded snapshot plus revisioned change observation
with registration/recheck rules from [readiness](READINESS-WAITS.md). Coalesced hints
require re-reading authoritative state; watch registration cannot lose a change
between snapshot and park. Exact publication/watch/reconciliation protocols remain
future work. No mandatory global mutable registry, new lifecycle policy service,
udev-style framework, sysfs clone or general hotplug manager is introduced now.

## Simplicity and implementation sequence

The simpler alternative is inherited provider references plus a fixed table of
the few compatibility bindings required by the shell/storage workload. Choose it
first. A global general-purpose devfs/driver framework adds publication, policy,
protocol, state, recovery and maintenance costs before consumers require them.
Use a small native Rust device-namespace adapter on the existing resource/service
contracts; no external device-management package is selected by this decision.
Add shared discovery infrastructure only when multiple actual consumers justify it.
No code is removed now; qualified replacement can retire fixture-only binding
paths after identifying their consumers and recovery obligations.

Borrow Fuchsia's principle of routing typed services independently of device paths,
not its component framework. Its [devfs migration guide](https://fuchsia.dev/fuchsia-src/contribute/open_projects/drivers/devfs_to_service)
describes protocol restriction, topology leakage and dependency-tracking reasons.
The [seL4 device/DMA explanation](https://sel4.systems/About/FAQ.html) illustrates
separate kernel mechanisms, user-space drivers and DMA trust/containment; it is
not evidence that Aether already supports isolated or restartable physical drivers.

[UP-08](../.planning/ROADMAP.md#up-08--device-services-and-scoped-dev) coordinates
UP-01 descriptors, UP-03 typed I/O/control, UP-06 scoped namespace/policy and UP-07
terminal relationships. UP-04 supplies required waits and later discovery watches;
VM-01/VM-02 supply relevant mapping slices, not a prerequisite for /dev/null.
Preserve current physical-backing/storage priorities. Sequence explicit providers
and minimal shell/TTY bindings, qualified randomness and bounded storage-provider
access, required device-backed mappings/display/input, then dynamic discovery and
graphical seats. R1-01/R1-02/R1-03/R1-06 select necessary console, runtime, storage
and startup slices; general hotplug/USB/framework/graphics are not blanket R1 gates.

Exact ABI, namespace layout, driver/service ownership, quotas, publication and
revocation protocols, physical isolation and recovery remain scoped future work.
No existing native profile, companion, standards-adoption or release gate closes
through this documentation acceptance; immutable pins/evidence remain unchanged.
