# Aether POC architecture

> Shared-standards migration, 2026-09-05: [Foundations adoption](STANDARDS.md) now routes the canonical shared ownership, interface and evidence rules. Domain mechanisms and exact implementation contracts below remain owned by this project. Shared-rule changes belong in a new standards release; adoption does not change implementation status.

Updated: 2026-10-04. This is the current baseline, including the accepted VM direction. Implemented behavior is tracked in [STATE](../.planning/STATE.md); nothing here is a runtime result by itself.

## Structure and ownership

Each participating CPU core runs the same small Zig kernel implementation with its own mutable local state. Rust user-space workers and services run above it. Start with one logical processor per physical core on real hardware; SMT is later work.

| State or responsibility | POC owner |
| --- | --- |
| Runnable threads, timer/preemption state | Local kernel instance |
| Task/address-space objects, capability tables | One authoritative local kernel instance |
| Backed memory and object pools | Fixed boot-partitioned owner; bounded allocation |
| User address spaces | Core-local; tasks remain pinned |
| Cross-core transport | Explicitly reserved and narrowly mapped buffers with fixed endpoints |
| Initial topology and grants | Trusted bootstrap, handed off as scoped capabilities |
| Work placement and worker restart | Capability-scoped user-space services |
| Normal display rendering | One user-space display service from M4 |
| Framebuffer access | Explicit boot-derived mapping delegated to that display service |

Kernel text may be shared read-only. Shared transport and bootstrap memory must be documented exceptions to local ownership. There is no global mutable task/capability table, replicated authority cache, or user-writable access to another core's private state. Cross-core coordination uses messages rather than remote mutation of those objects.

The executable M2 scope is defined by the [protection](../.planning/M2-PROTECTION.md), [endpoint capabilities](../.planning/M2-CAPABILITIES.md), and [task/memory lifetime](../.planning/M2-LIFETIME.md) contracts. A typed factory cap controls one worker and its backing bundle; these fixed fixtures do not define a general service ABI.

The [M3 per-core user runtime](../.planning/M3-USER-CORES.md) gives each CPU private user mappings, a saved context, runnable state, and a local timer. The [cross-core IPC contract](../.planning/M3-IPC.md) defines fixed local grants and bounded Rust request/results. The [mapping contract](../.planning/M3-MAPPINGS.md) defines dedicated supervisor RW/NX transport pages with boot direct mappings and old queue aliases removed. Shared kernel-image data remains trusted; this is not kernel-instance sandboxing.

## Companion ownership

[sys-init and pkg-mgr](COMPANION-PROJECTS.md) are components in this repository. Sys-init owns
service lifecycle policy, readiness, ordering and service definitions; Aether
provides scoped native lifecycle and authority mechanisms. The existing Rust
supervisor is a kernel conformance fixture, not the init implementation. Sys-init's
language remains its own design decision. Pkg-mgr owns artifacts, package state,
installation and trust policy; package metadata never creates capabilities or
implicitly activates services. The [native lifecycle v1 profile](../.planning/M4-LIFECYCLE-V1.md) now exposes a
separately supplied supervisor image and retained terminal records for a fixed
nine-cycle single-core conformance experiment. Sys-init has accepted that bounded
subset and its actual client passes on the current kernel. The separate SMP
supervisor fixture does not extend that accepted ABI or establish production init.

## Filesystem engine and R1 boundary

Maintainer decision, 2026-10-18: retain OpenZFS C behind the Rust filesystem
service for R1. Aether-userland owns the operational Rust filesystem service;
Aether supplies native OpenZFS engine integration and enforcing block contracts.
This is the maintainer's explicit owner assignment, not consumer implementation
or acceptance. Existing Rust namespace fixtures here remain conformance fixtures.
Rust owns scoped client identities, handles and service policy;
original OpenZFS owns on-disk decoding and transaction semantics. Kernel grants
remain the enforcing block authority. Paths, object numbers and file metadata do
not grant authority. Keep unsafe context ownership private and preserve the live
SPA borrow, serialized operations and original teardown/drain obligations.

R1 requires ordinary persistent filesystem operations and shell/runner/package
integration. The maintainer reaffirmed on2026-10-19 that the interactive boot
shell is Zsh. Aether-userland owns its build, startup/terminal behavior and consumer
qualification (UL-008/009); dash remains a possible system shell and existing
process test foundation. Native dash success cannot substitute for Zsh acceptance.
No RAM-only interim ISO replaces this persistent target. Snapshot/rollback is post-R1; filesystem snapshots alone will not
coordinate package/service/boot generations. Future engines remain separately
scoped work through the Rust boundary. Current implementation/qualification is
recorded in STATE, not implied by this decision.

Maintainer decision,2026-10-23: the interactive shell has a writable home;
changing the system tree requires an explicit installer/admin operation. Readable
system paths and a writable home must be scoped by actual delegated filesystem
objects/rights, not by path prefixes, UID/HOME text or package metadata. Do not
upgrade the existing read-only shell connection into a mutable system-root grant.
Provisioning and bounded CWD/descriptor inheritance remain implementation work;
this policy does not expand channel, worker, memory or workload limits.

## Minimal local mechanisms

Initial object families are capability storage, tasks/address spaces, threads, backed memory, and IPC endpoints. Timer/interrupt delivery supports preemption and essential target events. Fixed pools and fixed-size messages are acceptable restrictions. No dynamic growth occurs implicitly when a pool or queue fills.

Before implementing each operation, write its required rights, valid states, successful effects, resource cost, and failure outcome. Check user pointers, sizes, object types, and authority before exposing partial effects. Start with a basic local preemptive scheduler; CPU-time reservations, priority donation, and gang scheduling are deferred.

## Accepted virtual memory direction

Accepted 2026-10-04 at the maintainer's request. The
[virtual memory architecture](VIRTUAL-MEMORY.md) separates VM objects (what
memory), internal mapping/address-space metadata (where it appears), and an
architecture-specific pmap/MMU layer (how hardware represents it). VM objects are
first-class kernel objects accessed through capability handles; mappings are
internal address-space structures, not handles. Start with a simple balanced
range tree, demand-zero allocation and 4 KiB pages. Generic VM semantics cover
anonymous, file-backed, shared and device-backed memory, shared-object mappings
and copy-on-write fork; x86_64 and later aarch64 implement the pmap boundary.

NX, W^X, guard pages, no page-zero user mapping, ASLR-ready placement and no
routine physical-address exposure are defaults. Correct/simple TLB invalidation
and completed cleanup precede reuse. Huge pages, swap/reclamation sophistication,
userspace pagers and advanced mapping indexes remain deferred. Exact interfaces
and implementation details require scoped contracts and evidence. Existing
bounded/eager [native anonymous memory](NATIVE-MEMORY.md) and process-copy
fixtures retain their documented limits; this accepted direction is not a claim
that general VM or COW already runs.

[VM-01](../.planning/ROADMAP.md#vm-01--vm-objects-address-space-mappings-and-pmap)
places the enforcing foundation at the core-kernel stage before general mmap,
file-backed loading, COW and Xorg/Mesa/GPU userspace work. It preserves the
current shell/storage implementation order and existing per-core authority.

## Accepted musl backend and mapping boundary

Accepted 2026-10-04: use a small, maintained musl port with an Aether-native OS
backend. [The mapping design](MUSL-VM-BACKEND.md) sends anonymous memory through
direct capability-scoped VM operations, with demand-zero faults in generic VM.
File/device mappings obtain authorized backing through the relevant user-space
service, then use the same enforcing kernel mapping path. Musl owns POSIX
interpretation; Aether kernel/services enforce authority even when libc is bypassed.
Native Rust/Zig callers can use those contracts directly.

[VM-02](../.planning/ROADMAP.md#vm-02--native-mapping-contract-and-musl-backend)
follows the required VM-01 slice before broader mmap/file/device integration.
Exact ABI, backing protocols and coherent writable shared-file/msync semantics
remain implementation work; general userspace pagers remain deferred. Existing
bounded musl/native-memory profiles are preserved and no Linux-binary or full
POSIX compatibility is claimed by this accepted direction.

## Accepted descriptor and open-file ownership

Accepted 2026-10-04: [the descriptor design](FILE-DESCRIPTORS.md) separates
per-process userland descriptor tables, shared open-file descriptions with one
authoritative user-space owner, and capability-enforced native references.
Descriptor flags such as FD_CLOEXEC remain per entry; position/status state is
shared across duplicates and inheritance. The kernel has no POSIX FD table.
The musl backend translates operations; native services enforce access even
when callers bypass libc.

Duplication/replacement and inheritance preserve actual resource references;
exec closes marked descriptors at successful commit and preserves them on failed
replacement. Close, process-death cleanup and in-flight operations distinguish
local retirement, last reference and confirmed backend cleanup. Internal
generations isolate reused bindings. Production owner placement and exact
interfaces remain future work under existing
[UP-01](../.planning/ROADMAP.md#up-01--inherited-file-ownership-and-composable-processfile-capacity).
Coordinate mapping consumers with VM-02; basic descriptor work need not wait for
all VM features. Existing bounded evidence and current priorities are preserved.

## Accepted service I/O and device control

Accepted 2026-10-04: [the service I/O design](SERVICE-IO.md) uses capability-
authorized file, stream and device operations with a synchronous musl facade.
Native clients use the same contracts. Resource state has one authoritative
service owner; the kernel supplies protected IPC, mappings, authority and native
blocking/wakeup mechanisms. Native seekable-file operations favor explicit
offsets; POSIX transfer/position updates are coordinated at the shared open-file
owner, and enabled append requires file-wide atomicity.

Request acceptance, I/O completion and durability are distinct. Retain outcomes,
resource references and buffers through declared completion/cleanup; lost replies
cannot justify blind replay or an assumed cursor. Start with bounded copied
messages and simple ordering. Authorized VM-object bulk buffers, batching and
multiple outstanding requests follow justified consumers. Device DMA requires
its own completion/quiescence and isolation evidence before reuse.

Native device control is typed, versioned and rights-checked. Musl translates
supported ioctl commands; unsupported behavior fails explicitly. Exact ABI,
production placement, cancellation/recovery and extended transport remain scoped
work under [UP-03](../.planning/ROADMAP.md#up-03--service-io-completion-and-typed-device-control).
It supports the required R1 console/shell/filesystem/runner slices alongside
UP-01/UP-02; copied I/O does not wait for all VM features. Existing bounded evidence
and current implementation priority remain separate from this accepted direction.

## Accepted readiness and local communication direction

Accepted 2026-10-04: [readiness and native waiting](READINESS-WAITS.md) use
capability-authorized sources, level-triggered readiness and an initially bounded
wait-many list. Resource owners define readiness; the kernel parks/wakes threads
on authorized native observations; musl adapts poll/select without a kernel FD
table. Registration/recheck/park ordering prevents lost wakeups. Coalesced hints
cause rescans; they cannot discard retained operation outcomes. Generations,
closure/cancellation cleanup, monotonic deadline semantics and atomic signal-mask
waiting require scoped contracts. Local interrupt exclusion does not qualify
remote sources. [UP-04](../.planning/ROADMAP.md#up-04--readiness-and-native-wait-many)
builds on existing endpoint waits and coordinates SI-01/SI-02 without rewriting
their bounded evidence. Persistent queues and edge-triggered extensions are deferred.

Accepted 2026-10-04: [Unix sockets and descriptor passing](UNIX-SOCKETS.md) adapt
native IPC/resource services, beginning with connected local streams. Named
listeners and other types follow concrete consumers. Namespace lookup/connection
policy yields authorized access; names alone confer none. SCM_RIGHTS delegates
enforced references to the same open instance into recipient-local FDs. Queue
ownership, delivery commit, attachment/data association, exhaustion/truncation and
peer-death cleanup must be explicit. General endpoint passing requires qualified
cycle reclamation or enforced restrictions. [UP-05](../.planning/ROADMAP.md#up-05--unix-sockets-and-authorized-descriptor-passing)
coordinates UP-01/UP-03/UP-04 and applicable VM/namespace consumers. Exact ABI,
service placement, recovery and general cross-core behavior remain implementation
work. Current implementation priorities and scoped runtime evidence stay intact.

## Accepted signal and interruption direction

Accepted 2026-10-04: [signals and interruption](SIGNALS.md) prefer explicit native
events/lifecycle outcomes for services and a scoped POSIX signal runtime for musl
applications. Preserve authoritative native records and checked user-stack entry/
return. Dispositions are process-wide; masks are per thread; process/thread pending
state and interrupted execution have distinct scopes. Targeting requires delegated
authority and generation checks, including parent-linked SIGCHLD and authorized
terminal groups. Names/PIDs do not confer signal access.

Handler frames preserve user architectural state without restoring kernel authority;
supported nonlocal exits cannot leave a permanent kernel active-handler slot.
Interruption preserves partial/unknown I/O outcomes and owned reply/reference/buffer
cleanup. SA_RESTART needs operation-specific semantics; atomic mask-and-wait supports
sigsuspend/pselect/ppoll only in qualified slices. Coalesced SIGCHLD remains distinct
from retained wait status. Fork/exec and unresolved hardware faults use their explicit
state/commit contracts. Broader delivery, groups, thread/core routing, alternate stacks,
real-time queues and recovery remain implementation work under existing
[UP-02](../.planning/ROADMAP.md#up-02--native-shell-process-semantics-and-first-executable-workload),
coordinated with UP-03/UP-04. Current priority, ABIs and bounded evidence stay intact.

## Accepted identity and permission direction

Accepted 2026-10-04: [identity and permissions](IDENTITY-PERMISSIONS.md) keep native
capabilities as the authority foundation. Authenticated principals inform user-space
resource policy; musl exposes the supported POSIX credential view. Existing launcher
UID/GID records remain explicitly unauthenticated compatibility metadata, including
UID zero. Identity, paths and file modes cannot widen delegated rights or scope.

Resource owners enforce filesystem open/create/metadata and namespace policy below
libc. Directory references anchor root/CWD and pathname acquisition; authoritative
lookup handles traversal/concurrent mutation. Creation masks are process preferences,
not mandatory confinement. Ordinary mode changes do not implicitly revoke existing
open references/mappings; descriptor passing preserves authorized existing access.
Identity changes do not automatically drop capabilities. Narrow helpers precede
consumer-justified privileged executable support and complete secure-launch policy.

[UP-06](../.planning/ROADMAP.md#up-06--identity-and-permissions-over-capabilities)
sequences declared queries, required R1 filesystem/shell/loader slices, then trusted
multiuser credentials/transitions. Exact issuer/service placement, protocol, broader
groups, login, ACLs and revocation remain future work. No global kernel user table,
ambient root privilege or new shared-standard adoption is selected.

## Accepted clock and timer direction

Accepted 2026-10-04: [clocks and timers](CLOCKS-TIMERS.md) separate calibrated
clock sources, local hardware deadline events and user-space calendar-time policy.
On2026-10-06 the maintainer assigned shared UTC establishment/policy to
Aether-userland; Aether supplies raw source mechanisms and enforcement.
Monotonic elapsed time comes first; realtime/UTC is established truthfully for
required consumers. Suspend-aware elapsed time and CPU clocks remain deferred.
Checked 64-bit values have explicit units/range/resolution; nanosecond representation
does not promise that precision or wake latency. PIT/APIC counts and virtual clocks
retain their bounded scope and are not promoted to calibrated providers.

Each core owns bounded pending deadlines and timer programming. A qualified common
timeline or counter conversion preserves cross-core absolute-deadline meaning;
local ticks alone do not establish it. Native waiting uses absolute deadlines with
atomic observation/registration/park and explicit timeout/event/cancel ordering.
Expiration makes a thread eligible; user callbacks remain outside the kernel.
Reusable timer handles follow a consumer; simple waits can retain internal records.

Clock adjustment needs distinct delegated authority and does not alter monotonic
deadlines. Realtime adjustment behavior and musl API clock semantics remain explicit;
unsupported UTC cannot become zero/uptime or fabricated success. Existing
[SI-01](../.planning/ROADMAP.md#si-01--native-wait-and-service-deadline-contract)
tracks implementation with UP-04/UP-02 and actual storage/runtime consumers.
Exact hardware, ABI, calibration and wider timer/SMP/power features remain scoped
work; no global timer queue, new mandatory service or hard real-time promise is made.

## Accepted TTY session and seat direction

Accepted 2026-10-04: [TTY sessions and seats](TTY-SEATS.md) separate grant-scoped
device transport, a native Rust user-space TTY owner, application support, screen
emulation and graphical device policy. Musl adapts supported terminal controls to
typed owner operations. Canonical/raw/echo, queues, timed reads, readiness, EOF and
actual hangup have explicit bounds/semantics. Mode restoration is terminal/generation/
revision-bound; unsupported controls cannot become successful no-ops.

Process/session owners coordinate controlling terminals and authorized foreground
groups with the TTY owner. Ctrl-C/Z and background policy require actual signal and
stop/continue contracts. Pty master/slave references reuse the TTY model; names,
PIDs, UID zero and FD numbers cannot confer control. Recovery is explicitly owned;
old input/mode snapshots cannot mutate a replacement session.

Ncurses/terminfo remains the leading application-support candidate through musl;
versions, data and native adoption require userland qualification. Libtsm is the
leading later local-emulation candidate, not a TTY service or adopted renderer.
Serial rendering remains external. Graphical seats enforce input/display handoff
at device owners before reassignment; libseat compatibility follows a consumer.
[UP-07](../.planning/ROADMAP.md#up-07--native-tty-sessions-and-seat-boundaries)
tracks required R1 serial slices with UP-01/02/03/04/06 and SI-01. Production service
placement/ownership, exact ABI, general PTYs, graphics and seats remain scoped work.

## Accepted device service and scoped /dev direction

Accepted 2026-10-04: [device services and discovery](DEVICE-SERVICES.md) separate
trusted hardware/resource assignment, typed capability-routed native providers and
a scoped /dev compatibility view. Musl acquires authorized references through the
caller namespace; enforcing owners check access below libc. Enumeration, connection,
data/command, mapping and administration rights remain distinct. Names, device
numbers, labels, node creation/package installation and UID zero cannot mint access.

Begin with explicit provider grants and minimal shell/TTY/storage bindings. Device
mappings use approved device-backed VM objects; random aliases require a qualified
provider contract. Provider generations and open instances remain distinct; restart
or pathname reuse cannot retarget old references. Unknown effects cannot be blindly
replayed; publication withdrawal/FD closure do not prove mapping or DMA cleanup.

[UP-08](../.planning/ROADMAP.md#up-08--device-services-and-scoped-dev) coordinates
required R1 slices with UP-01/03/06/07, required UP-04 waits and relevant VM-01/02.
Keep authoritative resource state local and message its owner across cores. A small
native Rust adapter precedes general registry/hotplug/graphics; no external package
or production service topology is selected. General service ownership, exact ABI,
physical containment and recovery remain affected-owner implementation work.

## Capability and lifetime contract

- Names, numeric addresses, task/core IDs, and discovery records grant no resource authority. Invocations require a valid capability and appropriate rights.
- Creation consumes explicit bounded creation/resource authority. Child capabilities cannot gain rights or resource scope beyond their source.
- References belong to a holder's capability table. Stale references cannot become valid when slots/objects are reused; slots retire on generation exhaustion instead of wrapping.
- Closing a slot, revoking descendants, tearing down an object, and removing a mapping are different operations. The bounded local descendant model removes handles; it does not destroy tasks or detach existing mappings. Explicit task destruction removes mappings and references before backing release.
- Revocation completion identifies which access paths are disabled. Memory reuse requires completed CPU mapping cleanup, removal of relevant references, and zeroing before exposure to another protection domain.
- Arbitrary remote capability copy/move/lease operations are outside the initial two-core POC. Cross-core endpoints are explicitly bootstrapped; messages carry bounded data. Resource objects retain one authoritative owner.

Cross-core receive validates the endpoint's trusted route/authority binding. Caller-supplied sender IDs or capability-shaped bytes cannot create authority. Specify which kernel/transport state authenticates delivery; ordinary workers must not write trusted transport metadata.

## IPC, failures, and supervision

Use one small bounded local IPC mechanism initially; specify blocking/wakeup behavior alongside scheduling. Delivery has explicit success/failure; full queues report backpressure. General RPC frameworks and multiple kernel IPC families are not needed.

A user-space supervisor holds only capabilities needed to start/stop its workers and delegate dependencies. Restart creates a fresh instance. Old handles fail; clients obtain replacements through an existing authorized supervisor path. Demonstrate stateless work first, with job identifiers and explicit interrupted-work handling. Do not promise transparent retry of arbitrary side effects.

Static core membership is sufficient. Kernel swarm descriptors, discovery gossip, heartbeats, bidding, live migration, and recovery consensus are deferred. Service liveness and placement policy can use ordinary endpoints when needed.

## Trust and limits

For the POC, firmware, bootloader, all kernel instances, and the selected hardware/emulator form part of the trusted foundation. User tasks can be buggy or malicious. The supervisor is trusted for its delegated worker scope; the display service is trusted for visible output and its framebuffer mapping. User-space placement limits authority but does not automatically remove a service from the TCB for every property.

Checks cover unauthorized access, stale capability use, user memory faults, malformed IPC, bounded resource exhaustion, and worker termination/restart. Kernel-instance compromise, physical attacks, side channels, transparent recovery of a failed CPU kernel, and device DMA isolation are not established by the CPU POC. Per-core ownership alone is not a hardware security boundary between equally privileged kernels.

## Graphics progression

M1 draws directly into the framebuffer supplied by Limine for bring-up. The [first M4 display slice](../.planning/M4-DISPLAY.md) delegates only the approved framebuffer page range to a separate Rust display domain and moves default drawing there. The [live display slice](../.planning/M4-LIVE-DISPLAY.md) then runs a fresh AP publisher concurrently, with checked result/acknowledgment messages and progress rendering. The [separate supervisor fixture](../.planning/M4-SUPERVISOR.md) now adds a private BSP supervisor domain, AP-owned stop/reclaim and repeated generations on reused backing. The [fault recovery extension](../.planning/M4-FAULT-RECOVERY.md) demonstrates five generations with two unrequested #UD faults and terminal records retained through reclamation. Only supervisor holds lifecycle control; display refreshes its data endpoints through a scoped binding grant. A queued old result is discarded only after both endpoints are disabled and the AP publishes stopped. Reclaim and replacement follow transport cleanup. This remains a fixed stateless experiment; arbitrary in-flight stop and recovery from other fault/I/O states remain unproven. Other workers use capability-controlled display messages and receive no device-wide MMIO or DMA authority. A tiny emergency kernel diagnostic path is permitted and must remain distinct from normal graphics APIs.

For physical output, first validate the firmware-initialized framebuffer on the RTX 3060 machine. This supports pixels in the boot-selected mode, not native mode changes, connector management, accelerated rendering, or CUDA. M6 investigates native display control for one actual output before establishing a larger driver design.

Future DMA-capable drivers require concrete containment and teardown before memory reuse. Quiescence cannot be inferred from capability deletion, a timeout, or a driver acknowledgment alone. GPU execution units are not assumed to run Aether CPU kernel instances; a future GPU service coordinates device work from a CPU.

## Future filesystem service direction

Release-scope update, 2026-09-06: R1 now requires a persistent filesystem for the
serial shell and native package lifecycle. This heading retains its existing link;
the implementation is no longer wholly post-release research. The engine is not
yet selected by port evidence, and the interface/policy boundaries below still apply.

The accepted storage goal is a developer workstation with snapshots and rollback.
OpenZFS is the leading engine to evaluate, retaining upstream C behind an Aether
Rust user-space service instead of rewriting the filesystem. This is a direction,
not an implemented port or a selected R1 engine. R1 requires persistent storage;
a mature engine still needs a service runtime and integration beyond the bounded
block-transport fixtures.

Keep the client-facing service protocol independent of the engine's language and
internal structures. The Rust-to-C adapter is a private implementation detail,
not the client ABI. Future filesystems should be able to implement the same small
file-operation contract. Define that contract with the first runnable consumer;
do not build a plugin framework, dynamic loader, or universal filesystem trait
hierarchy in advance.

The initial contract must make directory-relative lookup authority, file rights,
buffer ownership, operation completion, errors, and durability explicit. Paths
and filesystem object numbers alone confer no authority. Keep snapshot/clone and
pool-management operations separately authorized from ordinary file access.
Advertise supported optional operations with explicit semantics and return an
unsupported result when absent; never silently emulate a stronger durability or
atomicity guarantee. A common file interface does not imply every backend has
ZFS datasets, snapshots, or equivalent rollback behavior. POSIX translation
belongs in user space.

Begin with one authoritative service owner for each pool or volume, accessible
from other cores through scoped endpoints. Do not let independent engines write
the same volume concurrently. Bound cache and outstanding-I/O resources. The
Rust adapter must document C pointer lifetimes, allocation ownership, callbacks,
and concurrency assumptions; wrapping C does not establish memory safety for the
engine. User-space containment also does not remove the filesystem service from
the trust boundary for its data.

Before writable persistence, specify flush/order guarantees, uncertain write
outcomes, device quiescence and recovery. Restart must invalidate old service
handles and account for outstanding I/O before replacement accesses the device;
replaying an unacknowledged write is not automatically safe. Require disposable
image tests for interruption, recovery, full storage, malformed metadata, and
data verification before adopting an Aether port for valuable data. Upstream
maturity does not establish correctness of our integration.

The [writable-pool preparation contract](OPENZFS-FEASIBILITY.md#writable-pool-preparation-contract--2026-10-07)
now scopes that next experiment: actual leaf/provider flush evidence is required
because upstream parent ZIO success can hide flush errors or bypasses. Issued
device uncertainty retains DMA and halts the current kernel; replacement access
requires confirmed VM teardown and fresh authority, with no automatic write replay.
Native raw write-ZIO/leaf/provider flush and fresh-VM readback now
[pass](OPENZFS-FEASIBILITY.md#native-physical-write-and-flush-scope--2026-10-07).
The [pool dependency audit](OPENZFS-FEASIBILITY.md#pool-dependency-and-resource-audit--2026-10-07)
retains original create/import/DMU/TXG paths at link time only. Runtime/resource fit,
pool transactions and persistent recovery remain unqualified.

Pkg-mgr owns preparing coherent package/system state; sys-init owns activation
and recovery policy. Snapshot support enables those policies but does not define
their transaction. Future boot environments must bind matching kernel, services,
package contents and package records, with user data outside system rollback as
appropriate. Coordinate the exact layout with the companions when implemented.

DTrace remains an independent future observability goal. Plan capability-scoped
observation and correlation across IPC, filesystem and block-I/O operations;
neither a ZFS port nor basic trace events establish DTrace compatibility.

Research starting points: [upstream OpenZFS](https://github.com/openzfs/zfs),
its [user-space libzpool build](https://github.com/openzfs/zfs/blob/master/lib/libzpool/Makefile.am),
and [HAMMER2](https://www.dragonflybsd.org/hammer/). Pin and review the actual
source, dependencies and license obligations when evaluating a port.

## Scope changes

Choose mechanisms in response to runnable experiments. Record a brief rationale and update this file when ownership or authority changes. Keep POSIX, richer graphics, accelerators, and whole-kernel proof outside the POC dependency chain. Adopt archived ideas only for a current reason, not an old completion label.


### Filesystem executable owner boundary

The separate filesystem executable keeps trusted immutable dataset/principal/
rights policy and main in Aether-userland. Aether supplies direct native provider
and original libzpool lifecycle calls. The exact bootstrap, private typed borrow,
truthful failure/readiness and separate drain/export/helper/block/UTC/runtime plus
native reclaim obligations live in
[NATIVE-C](NATIVE-C.md#launchable-filesystem-owner-and-sys-init-intake--2026-10-20).
No process-local result becomes a new kernel/RPC ABI. Current storage and SESSION
profiles remain incompatible; a new composition needs explicit role/resource
review rather than globally enabling helper exec or granting ambient storage.
