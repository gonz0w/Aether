# Companion projects and integration boundaries


The [corrected matched phase-one producer set](evidence/dash-phase-one-native-2026-09-13/README.md)
now passes431 command-runner and287 connections cases on identical sources/SDK.
It supersedes the original replay handoff's failing runtime source set with one
bounded code-size correction; use its new source archive and the original pinned
support/SDK archives. Startup/syntax now match argument/signal qualification.
Independent userland replay and UL-081 SDK boundary acceptance remain open.


The [phase-one replay handoff](evidence/dash-phase-one-handoff-2026-09-13/README.md)
pins the argument/signal producer set, archived SDK and missing replay support.
Restored host checks pass. Startup/syntax remain historical command-runner coverage
until that suite runs on the same final sources. Independent userland acceptance
and UL-081's supported SDK integration boundary remain open; no sibling was changed.

[DASH-signal-table and corrected consumer environment](evidence/dash-consumer-signal-2026-09-13/README.md)
now have producer evidence: actual substitution/USR1 trap, exact backend readback,
scope/dropped-post controls and six reclaims. Both argv and signal-table use the
manifest environment, with all287 connections cases passing. Next consolidate the
phase-one matched handoff for independent userland replay. No SDK or sibling
changes; remaining workloads and R1 filesystem/package/sys-init assembly stay open.

[Unchanged DASH-argv](evidence/dash-consumer-argv-2026-09-13/README.md) now passes
producer-side execution through real dash and the pinned userland helper, with
argument/environment preservation, independent backend output readback and six
reclaims. Three semantic controls and all 284 connections cases pass. No sibling
or SDK changes were made. Next qualify unchanged DASH-signal-table before the
adapter handoff; independent acceptance and the full consumer workload gate remain.

[Serial external substitution](evidence/pipe-exec-serial-2026-09-13/README.md) now
qualifies two externally executed substitutions in one serial shell and a clean
replacement shell, with six actual reclaims and second-generation rejection
controls. All280 connections regressions pass. Next qualify the unchanged
DASH-argv and DASH-signal-table inputs before an adapter handoff. This private
producer packet does not update the SDK or mark independent userland acceptance;
filesystem/package/sys-init R1 assembly and general pipelines remain open.

[Native external substitution](evidence/pipe-exec-native-2026-09-13/README.md) now
qualifies actual dash executing a separate writer ELF through an inherited pipe,
after denied admission preserves descriptors. CLOEXEC, pipe bytes/EOF, real wait
status and six reclaims pass with two controls and complete connections regressions.
This dedicated producer profile is not yet serial adoption or an installed SDK
delivery; independent consumer acceptance and general pipelines remain open.

The [pipe execution boundary](evidence/pipe-exec-boundary-2026-09-13/README.md)
adds host-checked five-binding CLOEXEC preparation and local pipe-holder commit.
Existing native regressions pass, but native executable replacement with live
pipes is not wired yet. This is not a new SDK delivery or consumer unblock.

[Interactive serial pipe substitution](evidence/dash-pipe-serial-2026-09-13/README.md)
now has bounded producer evidence for two substitutions entered at returned prompts
and a fresh second shell. The owner validates stdio bytes and EAGAIN handling; the
UART backend survives both sessions and its replacement lacks the grant. This is
separate from the serial exec profile: combined exec/pipe support, installed SDK
handoff, independent consumer acceptance and R1 assembly remain open.

[Repeated actual dash substitution](evidence/dash-pipe-repeat-2026-09-11/README.md)
now has producer evidence for two pipe/child generations within one shell, with
EOF/wait acknowledgment before retirement and reclaim. This is a bounded stream
backend profile, not a serial substitution or installed SDK handoff. Existing
serial exec/redirection evidence remains separate; independent userland acceptance
and combined consumer delivery are still required.

The [native pipe producer probe](evidence/pipe-native-2026-09-11/README.md) adds a
private copied-process FIFO/EOF experiment. Its packet distinguishes current run
status from installed SDK or independent userland acceptance. Public pipe/SIGPIPE,
actual dash substitution and release assembly remain separate work.

The [native SIGPIPE adapter](evidence/pipe-sigpipe-2026-09-11/README.md) records
selected real signal-delivery schedules for the private producer. This is not an
installed SDK handoff: public pipe(), serial-dash adoption and independent consumer
acceptance still need completion.

The [interrupted-create cleanup probe](evidence/pipe-reply-cleanup-2026-09-11/README.md)
extends this producer boundary with reply EOF, no descriptor publication or retry,
and terminal-based teardown across three real replacement lifetimes. This does
not unblock consumers on public pipe/SIGPIPE or actual dash substitution; matching
SDK/consumer integration and acceptance are still required.

Read-only checkpoint, 2026-09-11: userland now records independent serial-dash
qualification through resumed prompts and exit0/7 in its
[consumer packet](../../Aether-userland/docs/evidence/dash-serial-consumer-2026-09-11/README.md).
This review did not rerun its tests. Its current STATE requests the completed
repeated-child delivery next; Aether has sealed repeated-child and builtin
redirection packets, while independent acceptance of those extensions remains
separate. The [pipe design](NATIVE-SHELL-STARTUP.md#bounded-pipe-and-command-substitution-contract--2026-09-11)
is a local implementation plan, not an installed SDK or a new shared standard.

[Serial dash producer evidence](evidence/dash-console-2026-09-11/README.md) adds an
explicit native input configuration for independent SDK/userland review. It proves
interactive command input and child stdin in a private kernel harness; it does not
install an SDK, change sibling contracts or establish sys-init/R1 assembly.

The [ordinary dash command producer handoff](evidence/dash-command-config-2026-09-11/README.md#sdk-and-userland-handoff) binds the explicit native fork configuration, private process adapters and matched QEMU evidence for UL-007 review. This is a producer candidate; independent SDK/userland acceptance remains separate.

The [BG-067 command producer handoff](NATIVE-INIT-COMMAND.md) specifies the real
runner/bytecount profile, frozen inputs, capacity limits and cleanup obligations
for sys-init adapter work. Current acceptance and next action remain in STATE.

> Update 2026-09-05: the [five-artifact v2 handoff](../../pkg-mgr/docs/BOOT-HANDOFF-V2.md) now passes current target smoke and pixel validation. Earlier pair/mismatch descriptions below are historical evidence; the legacy adapter remains unchanged.

> Shared-standards migration, 2026-09-05: [Foundations adoption](STANDARDS.md) now routes the canonical shared ownership, interface and evidence rules. Domain mechanisms and exact implementation contracts below remain owned by this project. Shared-rule changes belong in a new standards release; adoption does not change implementation status.

Reviewed working files on 2026-09-05. This records Aether's integration direction,
not acceptance or implementation on behalf of the sibling repositories. Their
working trees are changing; repository HEAD alone does not identify reviewed
behavior. No sibling files were changed. The sys-init positive client was rebuilt
and booted against current Aether as recorded below; full companion test suites
were not rerun.

## Ownership

| Project | Owns | Does not obtain implicitly |
| --- | --- | --- |
| [Aether](../.planning/PROJECT.md) | Kernel objects, capability enforcement, image/launch contracts, instance lifetime, IPC, stop/quiescence/reclaim mechanisms | Service restart/ordering policy or package trust policy |
| [sys-init](../../sys-init/.planning/PROJECT.md) | Init/bootstrap policy, supervision, dependency ordering, readiness, service definitions, diagnostics and recovery policy | Ambient root authority, POSIX process semantics, or a language choice from Aether's fixtures |
| [pkg-mgr](../../pkg-mgr/docs/ARCHITECTURE.md) | Package build/staging, artifact and ownership evidence, package records, eventual install/update/remove and trust policy | Capability grants, service enablement, or permission to start/restart services |

Package dependency graphs, service dependency graphs, and native capability
relationships represent different facts. Installing bytes is not activation;
a package/service name or hash is not authority. Sys-init owns descriptor syntax
and lifecycle validation. Keep package artifacts and definitions inert until
separately authorized operations consume them.

## What exists in the companions

**sys-init:** independently accepted bounded ABI-6 interrupt-time observation,
supervisor-launched helper transfer and whole-domain fail-closed shutdown in
[decision 0017](../../sys-init/docs/decisions/0017-native-init-consumer.md), then
accepted [sequential reuse](../../sys-init/docs/evidence/native-slot-reuse-consumer-2026-09-05/README.md)
and a bounded service/dependent workload. Its current
[decision 0042](../../sys-init/docs/decisions/0042-reconciliation-evidence-review.md)
selects confirmed-result mapping (BG-058); unknown-result reconciliation remains
unsupported. It has not requested a new kernel API for that local step. Production
clocks, arbitrary delegation, replacement supervisors and SMP recovery remain
separate. These are inspected owner records, not fresh QEMU results from this review.

**pkg-mgr:** its current [STATE](../../pkg-mgr/.planning/STATE.md) reports host
zlib/zpipe builds, mode-aware package records, binary transport, explicit recovery,
update preflight and retained replacement in private staging roots. These results
were not rerun by Aether. Native target installation, service activation and a
current multi-module boot handoff are not established by those host results.
Its boot adapter still accepts the older kernel/protection pair described below.

## Concrete boot-handoff mismatch

pkg-mgr's [recorded handoff](../../pkg-mgr/docs/AETHER-HANDOFF.md) and
[adapter](../../pkg-mgr/mk/aether-boot.sh) accept a pinned kernel plus one
`protection.bin` module. Their retained two-core evidence is valid for that older
pair. It is not evidence that the same bundle works with today's image builder.

Aether now requires this ordered set from one matching build (updated after the separate SMP supervisor slice):

1. x86_64 kernel ELF.
2. Immutable `protection.bin` flat image, 1–4096 bytes.
3. Immutable `display.bin` flat image, 1–4096 bytes.
4. `lifecycle.bin`: the validated 32-byte v1 supervisor envelope plus 1–4096 code bytes.
5. Immutable `smp-supervisor.bin` flat image, 1–4096 bytes.

The current consumer invocation is:

```sh
python3 scripts/image.py KERNEL OUTPUT_ISO PROTECTION_BIN DISPLAY_BIN LIFECYCLE_BIN SMP_SUPERVISOR_BIN
python3 scripts/emulator.py smoke OUTPUT_ISO --cpus 2
```

The image builder includes the four modules in that order; the kernel requires four.
Default smoke requires `AETHER FAULT RECOVERY PASS` and actual Rust-rendered pixels.
Protection/display/SMP-supervisor remain fixed unversioned images; the lifecycle client uses
the explicit v1 profile. Neither is a general loader or package ABI. Artifact hashes must bind
all five matching inputs; hashes alone do not prove compatibility or provenance.
Do not silently source an unpinned display, lifecycle or SMP-supervisor image from a cache or accept the old
pair as current. Updating pkg-mgr's bundle/receipt/tests belongs in that project,
followed by a new consuming Aether smoke test. No such updated handoff is claimed.

## Native lifecycle seam and remaining companion work

The [implemented v1 conformance profile](../.planning/M4-LIFECYCLE-V1.md) now supplies a replaceable supervisor image, scoped bootstrap, instance identity, terminal retention/acknowledgment and bounded failure behavior. Aether's client and sys-init's actual positive client pass the fixed nine-cycle workload. Sys-init accepts this bounded subset in decision 0001; this is not acceptance of general or SMP supervision.

Preserve this accepted narrow interface while the internal SMP experiment evolves.
Align it with sys-init BG-032 (lifecycle), BG-033 (bootstrap/recovery), and BG-034
(native integration experiment). The smallest first consumer experiment can be
single-core and fixed-image, reusing M2 mechanisms without requiring POSIX or a
general loader. M4's final cross-core restart/display demonstration still remains
required; this is implementation ordering, not a reduction of that milestone.

The coordination checklist remains (v1 answers a bounded subset, with explicit exclusions):

| Checklist | Aether obligation for the bounded experiment |
| --- | --- |
| AR-01/02: bootstrap and launch | Explicit fixture ABI/version, image identity/layout, entry/configuration handoff, initial scoped grants, resource bounds, and rejection/cleanup outcomes |
| AR-03/04: identity and observation | Instance generation distinct from service name and holder-scoped handle; inspectable terminal reason/status with a defined retention/collection lifetime |
| AR-05/06: progress and stop | Poll/yield or notification semantics, honest watchdog/time limits, and forced-stop completion distinct from a cooperative service request |
| AR-07/08: reclaim and grants | Stop, mapping removal, reference invalidation and zeroing before reuse; explicit initial dependency grants and replacement semantics |
| AR-09/10/11: readiness, owner failure, quota | No queue-test readiness claim; explicit supervisor-death outcome and resource ownership; predictable quota exhaustion without partial launch |

The original M2 result values and destruction ordering are reference evidence.
V1 separates the supervisor image and retains a factory-owned terminal record
through destruction/release until acknowledgment; the task-local inspection
value still disappears when its task capability is invalidated. M3 static namespace
handles are not M2 generational handles. Do not export these differences as a
coherent lifecycle API without resolving and testing them.

Aether may keep conformance fixtures to exercise its mechanisms. Actual init
policy and its language remain sys-init-owned. A copied/renamed Rust test
supervisor is not sys-init integration. Resume the companion's dependent native
work only once the documented seam and target evidence exist and its own
experiment requirements are met; do not change its pause state on milestone
names alone. Supervisor recovery, service readiness and SMP cleanup must each
have explicit limits rather than inferred guarantees.

## Current sys-init client consumption

Rebuilt the current sibling source without modifying it, then booted its supplied
envelope on the current one-core Aether kernel:

```sh
python3 ../sys-init/scripts/build-lifecycle.py "$PWD/zig-out/sys-init-client"
zig build smoke -Dsmp=false -Dlifecycle-image="$PWD/zig-out/sys-init-client/pass.bin" -p zig-out/sys-init-current --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The client emits the expected completion accepted by `AETHER LIFECYCLE V1 PASS`;
all nine cycles complete. The source SHA-256 is
`e9c9fb8274e85cc594c8451053a95495de4fdcb164ba1434e661502bad0cbe65`;
the 2,512-byte envelope SHA-256 is
`cf7fbc9ab62c310428442ad419771506e1238b363a0f05a1293f7392d8120382`.
Generated evidence is under `zig-out/sys-init-current` and may be overwritten.
The companion's own negative-client results remain its separately retained
[evidence](../../sys-init/docs/LIFECYCLE-V1.md); they were not rerun here.

Aether's [SMP supervisor experiment](../.planning/M4-SUPERVISOR.md) now uses its
own separate Rust image and discards a queued old-generation result after
owner-confirmed stop, before reclaim/replacement. The [fault recovery extension](../.planning/M4-FAULT-RECOVERY.md) adds five
generations, two #UD faults and retained reason/detail records. Its bootstrap and control
operations are a different fixture, not an extension of lifecycle v1 or sys-init
SMP acceptance. General rootfs installation, production init, readiness and
POSIX execution remain later contracts.
