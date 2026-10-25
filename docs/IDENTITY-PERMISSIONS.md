# Identity and permissions over capabilities

Status: accepted architectural direction, 2026-10-04, by the maintainer after
the UID/GID and permissions review. Implementation remains queued/partial under
[UP-06](../.planning/ROADMAP.md#up-06--identity-and-permissions-over-capabilities).
[STATE](../.planning/STATE.md) records progress. Acceptance establishes the native
authority and service-policy boundaries; authenticated multiuser credentials,
credential transitions and exact interfaces remain scoped future work.

## Decision and responsibility

Keep capabilities as Aether's security foundation. Authenticated identity informs
user-space resource policy; musl exposes supported POSIX credentials and permission
operations. Resource access requires delegated authority even when a credential
or file permission policy would otherwise allow the operation. UID zero provides
no universal kernel bypass, global namespace access or implicit administrative grant.

| Concept | Meaning and owner |
| --- | --- |
| Authenticated principal | Identity established by a trusted launch/session authority and observed through a caller-bound process or connection record. Exact issuer and production placement remain open. |
| POSIX credential view | Real/effective UID and GID, plus saved IDs and supplementary groups only when implemented; adapted by Aether-userland's musl/runtime from its admitted record. |
| Capability or authorized reference | Enforceable resource scope, operations, holder binding and lifetime, owned by the kernel or the applicable capability-enforcing service. |

Aether owns native enforcement, IPC and lifecycle mechanisms. Resource services
own namespace, filesystem and device policies and their authoritative state.
Aether-userland owns musl/POSIX adaptation and the agreed bounded runtime.
Sys-init retains boot/session launch and supervision policy within its agreed
contracts; pkg-mgr retains artifact and installation policy. This direction does
not assign an unagreed account/credential service to a companion or introduce a
global mutable kernel user table, universal POSIX broker or new service topology.

## Existing compatibility metadata remains advisory

The [launcher-supplied metadata review](NATIVE-SHELL-STARTUP.md#launcher-supplied-usergroup-metadata-review--2026-09-08)
defines an explicit developer-only, unauthenticated compatibility view. Preserve
its exact admitted startup records, generation binding, source-kind restrictions,
validation, SDK/profile limits and existing evidence. Queries succeed only within
the declared profile and reflect its validated record; no convenient account
constant, environment value, descriptor role or PID arithmetic supplies identity.

These values, including zero, do not authenticate a principal or confer native
rights. A validated transport carrying advisory metadata does not make those
labels an authenticated multiuser credential. Existing fixtures do not implement
login, setuid/setgid, supplementary groups or general account policy, and this
acceptance does not promote them to Distribution ID-01/ID-02 runtime conformance.

An initial fixed declared credential view is sufficient for consumers needing
queries. Keep its unauthenticated status explicit. When authenticated users become
a requirement, establish trusted issuer provenance and bind the credential record
to the admitted process/instance and enforcing connection. Resource services obtain
that identity from trusted state rather than a UID/GID field supplied in a request.
Use immutable records or an explicitly revisioned transition contract; define
issuer failure, lifetime, stale/reused instances and bounded observation before
exposure. No cryptographic token framework or wire encoding is selected here.

## Resource policy and delegated authority

A delegated directory/namespace reference permits seeking child references only
within its supported scope and rights ceiling. The owner applies any authenticated
credential policy before granting a new open, creation or metadata operation.
Identity policy cannot widen the source authority. A shell with a project-directory
grant and a display service with GPU grants can have the same UID and different
access. A world-readable file outside the shell's delegated namespace remains
unreachable through pathname lookup.

Filesystem owner/group/mode metadata should be meaningful for supported shared
storage. Check ordinary opens against the applicable credential view and mode
policy at the authoritative service. File write permission does not automatically
permit chown or chmod: ownership/permission changes require the distinct metadata
authority and policy defined for that operation. Delete/rename checks include the
containing directory; sticky-bit and other special-mode behavior require an enabled
contract before they are advertised. Service administration and pool/snapshot
control remain separate from ordinary file access.

New files/directories apply the requested mode and the complement of the process
creation mask, subject to service policy and the enabled ownership/group rules.
Define persisted owner/group/mode values rather than fabricate stat results.
The runtime's process-wide umask is an application preference, inherited across
fork and preserved across exec when those semantics are enabled. A caller can
change its mask; mandatory restrictions must be enforced by the resource service
below musl. A default nonzero mask is not confinement evidence.

Ordinary chmod changes govern subsequent access requests. Existing authorized
open references retain their granted access under the [descriptor contract](FILE-DESCRIPTORS.md);
changing a mode does not implicitly revoke those references or existing mappings.
If strong revocation is required, define reference/mapping and in-flight-operation
effects and qualify cleanup separately. Authorized descriptor passing delegates
existing access without reopening the path, within its supported transfer ceiling.

An executable mode bit alone does not grant process creation, loading or executable
mapping authority. Device names and socket paths do not grant hardware or service
access. Image, device and connection admission still require their native grants
and owner checks; [service I/O](SERVICE-IO.md), [VM backing](VIRTUAL-MEMORY.md) and
[Unix sockets](UNIX-SOCKETS.md) preserve those boundaries.

## Directory references and safe pathname operations

Keep actual directory references for the runtime's root and current working
directory. Relative operations resolve from the applicable directory reference;
absolute POSIX paths resolve within the delegated namespace view. Names and PWD
strings describe locations and never replace that authority. Directory-relative
native operations provide the foundation for supported openat-style adaptation.

The namespace owner must define traversal scope across parent steps, symlinks,
rename and mount/namespace crossings. Lexically rejecting '..' does not establish
confinement. A held directory reference and a permanently confined subtree have
different lifetime/traversal requirements; do not promise full chroot semantics
from a bounded private-directory fixture. Lookup and reference acquisition must
check the authoritative object and applicable policy together, with concurrent
mutation and cleanup defined, rather than rely on a previous path-string check.

POSIX access() checks real credentials; ordinary open checks the applicable
effective credentials. Supported faccessat options need their own declared view.
Both remain bounded by delegated native scope. A precheck can race the actual
operation and is not authorization for it. Derive permission-query answers from
the owner contract, not guessed stat bits that omit scope or policy. Unsupported
queries/flags fail explicitly; no fabricated success or privilege bypass.

The accepted [device-service and scoped /dev direction](DEVICE-SERVICES.md), under
[UP-08](../.planning/ROADMAP.md#up-08--device-services-and-scoped-dev), applies this
namespace boundary to device acquisition. A delegated view may permit opening
selected providers within a rights ceiling; names, device numbers, installed nodes,
mknod or UID zero cannot manufacture authority. Lookup/acquisition must coordinate
with provider generation and removal as well as traversal policy.

## Credential changes and privileged execution

Begin with accurate queries and immutable declared credentials. Reject unsupported
setuid, setgid and group-changing operations explicitly; rewriting libc's cached
numbers cannot implement an authenticated transition. Saved IDs, supplementary
groups and the precise supported setter semantics are future consumer-driven work.

When transitions are enabled, credentials are process-wide and threads observe a
consistent committed state. A forked child inherits the applicable credential view
and creation mask but subsequent changes do not mutate its parent's credentials.
Successful exec follows the declared launch/credential contract; failed preparation
preserves the old usable state. Define how new requests, already admitted work,
connection caches and credential revisions interact with a transition. A stale
connection credential must not authorize new privileged requests after a committed
drop under a contract claiming that drop. Exact routing and cross-core coordination
remain future implementation work with one authoritative owner.

Changing identity and dropping authority are separate actions. A UID change does
not implicitly close open descriptors, remove namespace grants or unmap existing
memory. Do not tell an application that all authority was dropped while it retains
administrative references. A supported authority-drop operation needs explicit
grant issuance, retention/closure/revocation, mapping and in-flight-work semantics;
general revocation is not inferred from setuid or a timeout.

Prefer narrow helper/resource operations for privileged work. Defer setuid/setgid
executable support until a consumer needs a complete, trusted launch policy.
Executable ownership or special mode bits cannot mint capabilities. Any future
elevation must define authenticated credentials, allowed grant changes, inherited
descriptors, loader/search behavior, environment handling and failure/commit rules.

Review the actual musl, loader and dash paths that use effective identity or secure
execution. Existing advisory IDs are insufficient for the pinned dash interactive
ENV guard noted in the roadmap. Define the supported adaptation with userland;
secure-execution state must come from the trusted launch/transition policy, with
environment filtering and loader behavior implemented before an elevated profile
is exposed. This document selects no new secure-exec ABI field or successful stub.

## Simplicity and borrowed ideas

The simpler initial alternative is the existing validated developer-only identity
view with capability-scoped resources. Choose it while consumers only require
queries; a full account database or login server is unnecessary for that slice.
Persistent shared filesystem permissions and authenticated multiuser sessions need
authoritative metadata and identity policy, so add only their justified contracts.
Their total cost includes credential provenance/observation, namespace checks,
transition ordering and failure/cleanup, not just a UID field in libc.

Borrow delegated namespace access from
[Capsicum](https://man.freebsd.org/cgi/man.cgi?format=html&query=capsicum&sektion=4)
and narrowing directory-rights ceilings from
[Fuchsia directory capabilities](https://fuchsia.dev/fuchsia-src/concepts/components/v2/capabilities/directory).
These illustrate authority boundaries; no external framework or global service is
adopted. [POSIX open](https://pubs.opengroup.org/onlinepubs/9799919799/functions/open.html)
guides supported file-creation mode/ownership semantics and
[POSIX access](https://pubs.opengroup.org/onlinepubs/9699919799/functions/access.html)
guides real-credential queries and the precheck race. Compatibility semantics do
not define native authority or establish full POSIX/Linux-binary compatibility.

No code or experimental path is removed now. Qualified replacement can later
retire duplicate credential caches or fixture-only adaptation after identifying
users, migration and recovery obligations. Keep policy outside the kernel, one
owner per mutable resource and explicit cross-core messages.

## Dependencies and implementation sequence

[UP-06](../.planning/ROADMAP.md#up-06--identity-and-permissions-over-capabilities)
coordinates [UP-02](../.planning/ROADMAP.md#up-02--native-shell-process-semantics-and-first-executable-workload)
process/startup semantics, UP-01 descriptor references, UP-03 resource operations
and UP-05 namespace/peer identity where needed. Preserve the current backing/storage
implementation order. R1-02 shell queries and secure-environment adaptation, R1-03
filesystem modes/creation masks and R1-04 loader policy select their required slices;
full authenticated multiuser operation is not a blanket first-release prerequisite.

First preserve the declared query profile and review real consumers. Then qualify
service-enforced metadata, creation masks and scoped pathname operations with the
filesystem implementation. Introduce authenticated credentials and consistent
transitions when a concrete multiuser/session requirement warrants them. Device
and mapping consumers use their relevant VM-01/VM-02 slices; basic queries and
filesystem permission work do not wait for every VM or graphics feature.

Defer login/account management, broad name-service integration, setuid execution,
general saved-ID/group transitions, ACLs, additional mandatory policy systems and
ID namespaces until justified. Exact ABI, issuer/service placement, state bounds,
credential observation, recovery and revocation protocols remain scoped work.
Require matching native/resource-owner and independent userland positive/denial
witnesses for each enabled slice. Documentation acceptance does not close native,
companion, shared-standard adoption or release gates.
