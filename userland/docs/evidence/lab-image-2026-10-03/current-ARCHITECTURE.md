# Architecture and integration requirements


> Current scope, 2026-09-05: the [bounded native experiment](../experiments/native-c/README.md) now demonstrates startup, private TLS/FP context, partial output and cleanup. The [kernel-owned contract](../../aether/docs/NATIVE-C.md) defines its exact ABI and narrower limits. Requirements and earlier gap snapshots below remain proposals for broader support; they do not negate that witness. Shared requirements are owned by [Aether-standards](../../Aether-standards/docs/CATALOG.md), consumed through the [Distribution adoption](DISTRIBUTION.md). Native allocation, service-owned I/O and general POSIX integration remain open.

> Shared-standards migration, 2026-09-05: [Foundations adoption](STANDARDS.md) now routes the canonical shared ownership, interface and evidence rules. Domain mechanisms and exact implementation contracts below remain owned by this project. Shared-rule changes belong in a new standards release; adoption does not change implementation status.

Proposed consumer requirements, reviewed 2026-09-05. Not accepted sibling APIs.

## Layering and ownership

TTY applications use libc and a POSIX runtime that must ultimately operate through
Aether capability-controlled primitives. The selected experiment is a native transport adapter retaining musl internal
conventions; see [decision 002](decisions/002-native-musl-experiment.md). The final
ABI and runtime implementation remain open. Prefer keeping policy
outside the kernel; do not freeze a single global POSIX server or distributed
service topology before the required semantics and authority costs are understood.

| Owner | Responsibility |
| --- | --- |
| Aether | Native objects, grants, execution context, memory, IPC, loader mechanisms |
| sys-init | Bootstrap, lifecycle policy, readiness, supervision and recovery policy |
| pkg-mgr | Source recipes, artifact identity, staged payloads, install/trust policy |
| Userland | Package requirements/evaluation, SDK experiments, TTY acceptance suite |
| Unassigned pending agreement | POSIX process/FD/VFS/TTY adapters, libc OS adaptation |

Do not import ambient native root privilege through a POSIX compatibility layer.
Path lookup is constrained by delegated namespace authority. Descriptor inheritance,
process creation and exec must define which capabilities survive. Package hashes
identify bytes, not grants; installation is not service enablement.

## Current compatibility gap

Aether's [lifecycle v1](../../aether/.planning/M4-LIFECYCLE-V1.md) now specifies a
third boot module with a 32-byte envelope and at most 4096 code/constant bytes,
one stack page, fixed worker selection and scoped factory operations. Its initial
registers carry fixture information, not a C process environment. It explicitly
excludes argv/env, console handles, filesystems, shared user memory and FP/SIMD.
This is useful sys-init conformance progress, not a musl execution target.

The older package boot-pair receipt does not prove compatibility with the current
kernel/module set. Refresh exact producer/consumer artifacts before any handoff.
pkg-mgr's documented host zlib linkage is static zlib with the host system runtime,
not a fully static musl executable. No sibling tests were rerun in this review.

## Companion refresh

Sys-init now demonstrates an independently authored lifecycle v1 client, and
pkg-mgr records ordinary file modes plus private-root binary transport/replacement.
Aether reports bounded remote replacement as well as live display. These supersede
earlier broad wait/status descriptions but do not provide a general C runtime.
See the [native handoff](NATIVE-C-HANDOFF.md) for current consumer requirements.

## Required contracts and acceptance witnesses

| Area | Required behavior / witness | Work |
| --- | --- | --- |
| Image/startup | ELF segments, zeroed BSS, stack alignment, argv/env/auxv, bounded rejection, entry/exit | UL-003/006 |
| CPU context | TLS/thread pointer, FP/SIMD preservation before ordinary x86-64 C, interruption correctness | UL-003/006 |
| Memory | Allocation/mapping limits, invalid pointers, zeroing and exhaustion failures | UL-003/006 |
| libc boundary | Error mapping, partial/interrupted I/O, required startup calls, honest unsupported results | UL-002/006 |
| Processes | fork semantics or justified shell adaptation, exec, retained status, wait, reaping | UL-007 |
| Descriptors/VFS | pipes, dup, close-on-exec, shared offsets, paths, cwd, modes, links, EOF | UL-007 |
| TTY/session | canonical/raw mode, echo, controlling terminal, groups, Ctrl-C/Z, stop/continue | UL-008 |
| Identity | UID/GID views, credential transitions, namespace/grant inheritance and denial | UL-010 |
| Lifecycle | sys-init-owned launch/session cleanup/restart with explicit failure authority | UL-010 |
| Packaging | target ABI and complete file metadata; inert descriptors; incompatible payload rejection | UL-005/012 |

An early single-threaded program still requires auditing libc TLS initialization.
Deferring pthread applications does not justify skipping that audit. General C
code may use vector registers even without explicit floating-point expressions.
The integer-only compile probe deliberately avoids claiming those facilities.

## First boot profile

Propose a serial console, immutable staged base, explicitly bounded writable
scratch area and small authorized recovery payload. No general filesystem layout
is accepted yet. Read-only media does not replace source authenticity or runtime
confinement. Define how console possession becomes authorization before shipping
an administrative prompt. A developer-only QEMU session must be labeled as such.

## Public command-runner proposal (UL-059)

[The local aether-run contract](AETHER-RUN.md) separates CLI parsing/result policy
from the existing finite exit-29 native conformance runner. It proposes explicit
startup and result handoffs, delegated I/O, preserved child status and distinct
unknown/cleanup evidence. It is not an approved producer API or native CLI.
Shared changes require canonical standards and affected-owner review; current
frames, pins and test markers remain unchanged.

## Toybox native candidate boundary (UL-067)

The [bounded cat proposal](TOYBOX-NATIVE-CAT.md) records the local experimental
scope, startup/diagnostic/finalization ownership and current domain gaps. It adds
no accepted native ABI or package policy. Its CAT-01–08 acceptance cases live with
the proposal and are linked from ROADMAP; all native cases remain NOT RUN.

## Current session SDK boundary — 2026-09-29

[UL-081 assessment](SESSION-SDK-BOUNDARY.md) binds the accepted private008/ABI23
application link closure. Explicit startup/process/descriptor/memory adaptation
complements native musl; omitting memory adaptation can still link and must not
satisfy component admission. The future opt-in runtime/application split requires
owner agreement and sealed artifacts before consumer SSDK-01–06. Existing exact
private acceptance remains valid; no public libc/POSIX runtime owner or SDK support
is assigned by inference. Shared SDK implementation and independent review are open.

## Bounded runtime ownership agreement — 2026-09-29

Aether-userland implements the bounded libc/POSIX runtime extension by explicit
maintainer assignment. The initial extraction uses the accepted AENMX008/ABI23
session protocol, with process/FD/bootstrap/mask state in a runtime object and
dash startup/environment/helper-path policy in an application object. Component
checks reject omitted memory adaptation before linking; these are build admission,
not native enforcement. Aether retains ABI/grants and fixture authority. Native
requalification and independent review are required before SDK promotion.

### SI-07 maintained client profile, 2026-10-03

`NATIVE_SUSTAINED_V2` explicitly selects AERIO002 parent roles, NIO2 child
bootstrap and0x7b receipts. Both adapters reject native generation outside1..65535
at full return width before narrowing/record transfer; wire epoch must equal that
cohort. Public client symbols are versioned, so legacy/v2 mixed links reject.
Bindings publish only after complete validation; single-attempt bootstrap, poisoning,
consumed close, bounded framing and existing runner selection remain authoritative.
[Client delivery](evidence/sustained-runtime-2026-10-03/README.md) contains rebuilt
runner/bytecount and host evidence. Native enforcement, retirement, coherent cohort
provisioning, reclaim and halt require matching Aether hooks; sys-init policy remains
separate. Default legacy client artifacts remain byte-identical.

## Bounded lab-image build boundary — 2026-10-03

experiments/lab-image consumes an externally selected boot-input manifest and
sealed AENMX008/ABI23 SDK candidate. It rebuilds the clients, requires whole ELF
equality with the qualified payload, extracts/verifies all actual ISO boot modules,
then copies the qualified ISO/firmware/workload/notices into a new build/ kit.
The receipt records incomplete/failed/pass build state and exact inputs/tools.
Build success and native boot success remain separate. This developer tool does
not implement package state, install to a prefix, write physical media, define
sys-init policy, or add native authority. It is not a source-execution sandbox;
selected recipe/support bytes are trusted code. Concurrency against hostile host
mutation, physical hardware, persistence and unrestricted sessions are unqualified.
