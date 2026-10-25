# Roadmap: x86_64 swarm POC

This file owns capability gates and accepted product constraints. The
[system index](STATE.md#system-work-index) selects work and links its owning record
for current status and continuation. Dated progress and next-step narration below
is historical context, not a competing assignment; accepted gates remain binding.

Integration now spans the kernel root, `userland/`, `sys-init/` and `pkg-mgr/` in
one repository. Stable component backlog IDs still apply; another folder's work
is locally actionable. Aether-standards remains separate. Repository consolidation
is not a release milestone or a replacement for the persistent Zsh acceptance below.


Updated: 2026-10-19. Current progress is recorded only in [STATE](STATE.md).

The first public release now ends at R1: boot to a serial shell with runner,
persistent filesystem and native package management. M1–M4 are foundations; M5–M6
remain optional later graphics work. This supersedes the earlier M4-only public
release boundary. Each milestone must produce executable evidence.

## Filesystem service lifetime acceptance — 2026-10-20

STATE owns current results. Private AF05/AF06 are finite producer selections,
not operational service or R1 acceptance. Preserve old seals, all authority/
memory/VM bounds, complete framed-body validation before effects, irreversible
outcomes and success-only retirement. The delegated-directory gate must verify
actual-parent/alias metadata, directory link/entry counts and ACL, exact original
and new file data, complete allocation/namespace inventory, independent fresh-media
recovery, ordered export/drain and every native reclaim. Native work remains
exactly9 mutations/96 requests, with writer60s6000/readers30s3000 and existing
8192 controller/observer,4096 stack,no statics,8192-page engine and other limits.
Capture actual emulator/tool/boot identities and stop unexpected failures for triage.
The separately approved operational-lifetime qualification may select AENBD005/
controller27 with unchanged engine26/AF06, cross6000 healthy ticks and run one120s
writer containing6500-tick idle and post-idle I/O. Its matching oracle window is
120s while readers stay30s3000; all other limits and old profiles remain fixed.
This acceptance does not imply operational main/shutdown or R1 readiness.

R1 additionally requires a matched operational executable/ABI/resources and
authenticated provisioning, usable-namespace readiness and explicit admission/
drain/export/block-quiescence/reclaim handoff, package-required metadata and
cross-directory promotion, persistent loading/runner, native package management,
Zsh/TTY/sys-init composition and independent acceptance. Keep installation policy
in pkg-mgr and activation policy in sys-init. Do not substitute a finite or RAM-only
test shell for the accepted persistent Zsh ISO. Snapshot/rollback remains post-R1.

## Tagged fork prerequisite for persistent shell — 2026-10-22

For sys-init BG-069/070, follow the [Aether fork ordering/child rebind contract](../docs/NATIVE-C.md#tagged-fork-ordering-and-child-rebinding-contract--2026-10-22).
Acceptance requires a separately versioned serialized-inheritance library contract,
authenticated owner gate from snapshot through child binding publication, armed
child-only native grant/auxv/context transition, matching private producer/consumer
and complete real shell link. Preserve old API bytes and upstream musl repair.
Test actual-library resumed-parent mutation and known/unknown copy/cleanup schedules,
shared offsets/flags/holders, child rebinding, truthful refusals and no replay.
Require complete code/stack/heap/workspace/backing/channel fit in current limits,
then fresh native positive/refusal/unknown/continued-parent/wait/cleanup witnesses.
No linker stub, context reset, new kernel hold promise or quota expansion substitutes.
STATE owns results; independent owners' acceptance and R1/ISO stay separate.

## Simplicity triage for the bootable-shell path — 2026-09-07

Apply the [adopted extension](../docs/standards-review/2026-09-07-simplicity/README.md)
in the existing design review; these are scoped delivery findings, not a cleanup
program. Aether's implementing contributor owns the review, with affected consumer
acceptance still required.

- **Before custom shell signals:** use the current
  [public routing review](../docs/NATIVE-SHELL-STARTUP.md#public-signal-routing-review--2026-09-08).
  Prove real musl sigaction/native-record agreement next, preserving private and
  legacy profiles. Resolve signal() flags, authorized signal production, child
  notification, broader delivery/indefinite-I/O interruption and terminal consumer
  adoption before full dash. STATE records completed private frame, pending and
  guarded/nonlocal transport evidence. Preserve consumed fixtures until qualified
  replacement; do not add another successful compatibility stub.
- **Before positive real-main startup:** follow the
  [generated-init review](../docs/NATIVE-SHELL-STARTUP.md#actual-maininit-prerequisites-review--2026-09-08).
  Real init diagnostics are recorded in STATE; supply truthful parent/user metadata
  and directory authority before accepting PPID/PWD or a builtin exit as startup.
  Apply the [directory review](../docs/NATIVE-SHELL-STARTUP.md#scoped-directorycwd-contract-review--2026-09-08)
  next. Before actual-main acceptance, resolve the pinned Linux-target interactive
  ENV guard configuration recorded by userland; advisory UID/GID is insufficient.
- **Before shell exec/wait composition:** native_c.zig dispatch and fixture mode
  combinations couple lifecycle, image admission and I/O routing. Trace the exact
  current shell path and justify retained modes/service boundaries before adding
  another profile. Use the [pipe execution boundary](../docs/NATIVE-SHELL-STARTUP.md#pipe-descriptors-at-execution-commit--2026-09-13)
  for descriptor retention; require native admission/replacement evidence before
  enabling live-pipe exec. The [bounded native pipe-exec contract](../docs/NATIVE-SHELL-STARTUP.md#bounded-native-pipe-exec--2026-09-13)
  and [serial composition](../docs/NATIVE-SHELL-STARTUP.md#serial-external-substitution--2026-09-13)
  scope the private producer path. The [unchanged DASH-argv workload](../docs/NATIVE-SHELL-STARTUP.md#unchanged-consumer-dash-argv--2026-09-13)
  and [DASH-signal-table](../docs/NATIVE-SHELL-STARTUP.md#unchanged-consumer-dash-signal-table--2026-09-13)
  have producer evidence with the consumer environment. Next consolidate the
  [matched phase-one handoff](../docs/evidence/dash-phase-one-native-2026-09-13/README.md) now passes both native suites; [consumer descriptor closure](../docs/evidence/dash-consumer-closure-2026-09-13/README.md) now passes. [Live read-only null](../docs/evidence/null-native-wait-2026-09-13/README.md) passes a private foreground subshell and all294 connections cases. Unchanged background wait reaches helper7 but times out; [native null lifetime probes](../docs/evidence/null-lifetime-2026-09-13/README.md) now pass all 296 connections cases. [Null denied-exec rollback](../docs/evidence/null-rollback-2026-09-14/README.md) now passes real denial and retry with all 298 connections cases. [Null fault cleanup](../docs/evidence/null-stop-2026-09-14/README.md) now passes the pre-exec idle-boundary fault with all301 connections cases. [Signal/suspend design and frame preparation](../docs/evidence/suspend-frame-2026-09-14/README.md) now pass host preparation checks. [First native background wait](../docs/evidence/native-suspend-2026-09-14/README.md) now passes the unchanged script with opt-in terminal posting and handler suspension. [Forced notification ordering](../docs/evidence/suspend-order-2026-09-14/README.md) now passes both sides of parking. [Parked-stop and notification cleanup](../docs/evidence/suspend-cleanup-2026-09-14/README.md) now pass. [Stale-parent replacement](../docs/evidence/suspend-stale-2026-09-14/README.md) now passes. [Failed-frame recovery](../docs/evidence/suspend-recovery-2026-09-14/README.md) passes; [matching runner coverage](../docs/evidence/suspend-runner-2026-09-14/README.md) now passes; finish remaining signal behavior and consumer handoff before full background-wait acceptance; other interruption schedules remain open. [Failed-exec owner contract and pinned intake](../docs/NATIVE-SHELL-STARTUP.md#unchanged-failed-exec-owner-review--2026-09-14) now have [native producer qualification](../docs/evidence/failed-exec-native-2026-09-14/README.md); follow the [writable descriptor owner review](../docs/NATIVE-SHELL-STARTUP.md#writable-shell-descriptor-owner-review--2026-09-14) for backend integration and unchanged leak/redirection workloads while independent acceptance remains open. Independent replay remains open. General
  pipelines and independent SDK acceptance remain separate. Keep capability enforcement and exact-stop cleanup local and
  visible; extract a coherent responsibility only when the change needs it.
- **During the next affected harness change:** launch_smoke.py combines build,
  case selection and profile-specific oracles. Reuse its existing evidence and
  test-group records; clarify touched case/oracle ownership without introducing
  another harness/status system or weakening negative controls. Broad extraction
  and retirement of still-consumed fixtures are deferred.

## Closing the bounded dash workload handoff

The [composed SESSION producer delivery](../docs/evidence/session-native-2026-09-25/README.md)
now contains the unchanged one-parent workload, explicit reuse/identity/argv/FD
contracts, semantic controls and matching producer qualification. STATE owns the
counts and current evidence. [Verified consumer acceptance](../docs/evidence/session-acceptance-review-2026-09-25/README.md)
now closes SESSION-01–06 for the private scripted profile. Shared SDK and R1 gates
remain separate. Do not substitute component tests for the next composed workload.

The [early-reader recovery producer](../docs/evidence/recovery-native-2026-09-25/README.md)
now runs EPIPE/pipefail recovery followed by argv and a healthy pipeline within the
same parent, repeated three times. Independent RECOVERY-01–06 replay is accepted;
the verified intake is in the [next integration packet](../docs/evidence/failed-exec-session-2026-09-29/README.md).
The [failed-exec producer composition](../docs/evidence/failed-exec-session-2026-09-29/README.md)
now has [verified independent acceptance](../docs/evidence/failed-exec-acceptance-review-2026-09-29/README.md)
for EXEC-SESSION-01–06. The unchanged scratch redirection composition now has a
[producer delivery](../docs/evidence/scratch-session-2026-09-29/README.md), including
owner-backed denial, shared offsets, reopen/EOF, exact phase cleanup and semantic
controls. [Verified independent acceptance](../docs/evidence/scratch-acceptance-review-2026-09-29/README.md)
now closes SCRATCH-SESSION-01–06 for the private volatile profile. The [real serial SESSION handoff](../docs/evidence/serial-session-2026-09-29/README.md) now supplies frozen consumer workload bytes, authority, lifetime/cleanup
expectations and negative oracles. Producer qualification and
[verified independent acceptance](../docs/evidence/serial-acceptance-review-2026-09-29/README.md)
now close SERIAL-SESSION-01–06 for private AENMX008/ABI23, including prompt ordering
and cancellation. Userland's SDK boundary assessment is now
[verified](../docs/evidence/session-sdk-intake-2026-09-29/README.md).
Userland now records agreed bounded runtime ownership and supplies the sealed
opt-in008 bundle, including mandatory memory-adapter/component checks. The
[Aether-side review and isolated rebuild](../docs/evidence/session-runtime-review-2026-09-29/README.md)
pass within the recorded scope. Next obtain actual independent technical/reader
findings and SSDK-01–06 consumer/owner disposition. The sustained bootstrap/transport and rebuilt runner/bytecount now pass the
bounded SI-07 kernel contract; full SUSTAIN-01–06 and sys-init/shell assembly
remain separate work. Existing per-script acceptance
and AENMX006 interactive pipeline evidence remain component evidence. AENMX007
selects bounded fifteen-use process/channel/participant and nine-use pipe lifetimes;
old profiles retain their limits. The 007 observation operation is fixture-only,
not a public SDK logging API or UART grant.

The [sys-init/serial-shell composition review](../docs/evidence/serial-boot-contract-2026-10-03/README.md)
now selects the next bounded producer experiment: a separate serial SESSION
lifecycle profile with owner-only observe/park/halt, unchanged SESSION identities/
quotas and a single boot-owner domain. Existing ABI23 tick/iteration/three-parent/
fixture-finish cutoffs cannot provide a healthy manual prompt. No identifier,
runtime support or owner acceptance is allocated by that review. Qualify the
kernel mechanism first, then matching actual sys-init and userland composition;
ordinary workers gain no factory/UART authority. Full protocol and R1 gates remain.

The [kernel lifecycle producer](../docs/evidence/session-lifecycle-2026-10-03/README.md)
now qualifies separately selected AENMX009/ABI24 observe/park/halt with unchanged
SESSION limits. Private long-idle/wake/authority/rejection/cleanup controls, host
checks, ABI22 regression, all11 ABI23 serial cases and seven M4 regressions pass.
Next replace fixture iteration/parent/finish assumptions on the selected009 owner
path, then consume through actual sys-init and matching userland. Full new-profile
shell/finite-exhaustion/resource matrices and independent acceptance remain open.


The [selected owner experiment](../docs/evidence/session-owner-lifecycle-2026-10-03/README.md)
now runs one real shell through cleanup/halt and removes009 fixture output limits.
It exposes the remaining100000-attempt **client** transport limit on long stdin
idle. Prioritize a capability-scoped channel wait plus matching userland adaptation:
read/write readiness must atomically bind live endpoint holder/rights/generation;
close/terminal/stop/interruption must wake safely with no fabricated transferred
bytes or replay of partially progressed requests. Keep single-context009 bounds.
[Endpoint waiting](../docs/evidence/session-channel-wait-2026-10-03/README.md) and
[private delayed dash composition](../docs/evidence/session-client-wait-2026-10-03/README.md)
now qualify the bounded producer path. Canonical userland runtime adoption and
actual sys-init entry/policy composition remain next; private prompt idle is not
assembled R1 acceptance. Short-input
success is component evidence, not complete boot-to-shell acceptance.

[Asynchronous child notification](../docs/evidence/session-wait-notification-2026-10-03/README.md)
now qualifies an actual copied child's SIGCHLD waking a parked unmasked parent,
while a masked parent stays blocked until real input and retains the signal.
Two fresh parent/child generations, exact failed-expectation control, four reclaims
and authorized halt pass. No new kernel operation or runtime signal policy is
added. Explicit disabled-op coverage, wider schedules and independent review
remain open alongside the canonical runtime and genuine sys-init handoffs.

The [matched companion intake](../docs/evidence/abi24-companion-intake-2026-10-03/README.md)
now verifies the canonical009 runtime and genuine sys-init entry. Missing delivery
is resolved. A fresh delayed normal boot passes the shell/ten-reclaim halt, but
normal immediate boot reproduces a real owner failure after the final helper.
Prioritize a deterministic terminal-observation/channel-transfer interleaving
witness and the smallest evidence-backed dispatcher correction before integration
acceptance. Passing diagnostic/rerun images cannot close the unexplained failure.
Sys-init still owns its recipe/policy and consuming qualification; no sibling
source is changed by this intake. Full cleanup-negative and independent review
remain separate alongside storage/packages.

The [bounded polling correction](../docs/evidence/session-poll-terminal-2026-10-03/README.md)
now proves real terminal publication between observation and read/write: the old
dispatcher fails on EOF/EPIPE, corrected code confirms the same task terminal
before using existing settlement, and still-live closed peers reject. Three real
canonical-client dash compositions and all11 old serial cases pass. Next sys-init
must consume the producer source patch, inspect its actual linked entry/stack and
requalify normal immediate/delayed schedules plus cleanup negatives. The original
failed call site and absence of other defects are not established by producer
tests; matching composition acceptance remains separate.

Before calling dash complete for R1, integrate accepted paths into the shared native
SDK/runtime and assembled serial-shell boot flow, preserving console authority and
reviewed signal/terminal limits. Private per-script fixtures and sh -c success alone
do not meet that boundary. Persistent filesystem, native package installation and
sys-init assembly retain their existing owners and release gates.

## Exec dispatch integration budget — 2026-09-23

The private owner budget review is qualified: AENMX005 allows24 KiB of immutable
supervisor code while AENMX004 remains16 KiB. Existing backing pools, ABI and grants
are unchanged. Boundary and mapping controls pass; see STATE and the
[review](../docs/NATIVE-SHELL-STARTUP.md#private-owner-code-budget-review--2026-09-23).
Use005 when implementing the extended owner, retaining004 compatibility witnesses.
Retained exec phases are now qualified in the sequential driver (see STATE).
Proceed with dispatcher integration and the held-reply/I/O overlap witness,
including combined stack and frame-ownership review. Further
resource growth requires explicit review; do not remove authority or cleanup checks
or rely on repeated compiler-layout tuning to add behavior.

## Current implementation order — 2026-09-07

The [constant-size plans](../docs/evidence/native-memory-plans-2026-10-04/README.md)
and [fresh-root alias experiment](../docs/evidence/native-backing-alias-2026-10-04/README.md)
qualify stack headroom and physical/permission/translation prerequisites. R1 still
requires explicit one-service backing/metadata/table ownership and sufficient live
workers, actual native allocation/stack evidence, provider identity/configuration,
feature closure and complete engine lifecycle. Keep this before persistent
filesystem/package assembly; do not enlarge every static State or count the
64MiB isolated reservation as a measured service/engine budget.

Accepted VM direction, 2026-10-04: [VM-01](#vm-01--vm-objects-address-space-mappings-and-pmap)
queues the core-kernel memory foundation before general mmap, COW and later
Xorg/Mesa/GPU userspace integration. The bounded work below keeps its priority;
VM implementation is scheduled by those concrete dependencies.
[VM-02](#vm-02--native-mapping-contract-and-musl-backend) records the accepted
small musl backend and direct-memory/service-backing boundary as its consumer
follow-on; exact contracts and native acceptance remain queued.
The accepted [UP-01 descriptor direction](#up-01--inherited-file-ownership-and-composable-processfile-capacity)
builds on existing owner-bound I/O and supplies descriptor bindings for applicable
VM-02 consumers; it does not require every VM feature before basic descriptor work.
[UP-03](#up-03--service-io-completion-and-typed-device-control) records accepted
service I/O/control alongside UP-01/UP-02 for required R1 consumers. Copied I/O
uses existing native foundations; bulk/async extensions follow justified needs.
[UP-04](#up-04--readiness-and-native-wait-many) and
[UP-05](#up-05--unix-sockets-and-authorized-descriptor-passing) record accepted
readiness/waiting and local communication. Required consumers select bounded
slices; general sockets/transfer/waitsets do not block the whole R1 path.
The accepted [UP-02 signal direction](#up-02--native-shell-process-semantics-and-first-executable-workload)
coordinates checked musl delivery with UP-03 interruption and UP-04 atomic waiting;
required slices preserve the current implementation order and completed evidence.
[UP-06](#up-06--identity-and-permissions-over-capabilities) records accepted identity/
permission boundaries for required shell/filesystem/loader slices. Existing advisory
credentials remain advisory; full multiuser/login/setuid support does not block R1.
The accepted [SI-01 clock/timer direction](#si-01--native-wait-and-service-deadline-contract)
sequences calibrated monotonic/deadline and required musl/storage work with UP-04.
Existing tick/virtual-clock receipts remain bounded; future timer/power features
do not displace current backing/storage priorities or block all R1 consumers.
[UP-07](#up-07--native-tty-sessions-and-seat-boundaries) records accepted terminal/
session/seat boundaries and leading package candidates. Required serial TTY slices
coordinate existing R1/UL-008/009 work; general PTYs, local graphics and seats follow
consumer dependencies without changing current implementation priority.
[UP-08](#up-08--device-services-and-scoped-dev) records accepted device/provider/
namespace separation. Required console/runtime/storage/startup bindings precede
applicable consumers; full registry/hotplug/graphics follow demonstrated needs
without displacing the current physical-backing/storage sequence.

The maintainer authorized a bounded BG-067 bytecount producer detour to open
sys-init adapter work; see [handoff](../docs/NATIVE-INIT-COMMAND.md) and STATE.
Consumer composition/size and independent acceptance remain gates. Resume the
planned dash path after this producer packet.

The consumer's phase-one argv script already launches an external helper, and its
signal-table script uses command substitution. Preserve those workloads: native
child creation/exec/wait and substitution pipes are prerequisites, not later work
that can be bypassed with builtin substitutes. Qualify the independent syntax-error
case first, then design the bounded process/descriptor composition before argv and
signal-table execution. See the dependency review in NATIVE-SHELL-STARTUP.

The maintainer prioritized unblocking actual dash ahead of the OpenZFS build audit.
Userland independently qualified the bounded startup pair and supplied twelve
native workload candidates. Implement descriptor replacement, then checked actual
dash initialization/custom signal behavior, child creation/exec/wait and real
redirection/pipes with scoped memory-backed files and granted helper images.
Persistent OpenZFS is not a prerequisite for this bounded shell handoff; it remains
required filesystem evaluation work for R1. No builtin-only or spawn-only fixture
is full-dash acceptance. SI-06 and earlier UL-059/067 handoffs remain preserved.

After the shell producer path, resume the private static musl/platform engine
startup audit selected by the native capacity review. Independent consumers retain
their own qualification and acceptance responsibilities.

The [2026-10-04 build audit](../docs/evidence/openzfs-musl-startup-2026-10-04/README.md)
now produces177 of178 declared libzpool C objects with private header adaptations;
strict startup link rejects missing native libraries/compression and the I/O hook.
Next rebuild those dependencies and review native feature configuration before a
startup admission proposal. No native engine, persistence or capacity gate closes.

The [supporting-library follow-on](../docs/evidence/openzfs-native-support-2026-10-04/README.md)
adds native Zstd/zlib and crypto objects; all178 declared engine C files have objects.
Strict link remains blocked on real nvpair/XDR, diagnostic/platform linkage and the
SDK I/O hook. Qualify those next; compiled libraries do not establish native runtime,
CPU-state safety, persistence or a numeric capacity budget.

The [memory-XDR follow-on](../docs/evidence/openzfs-native-xdr-2026-10-04/README.md)
rebuilds six real libtirpc1.3.6 units and both remaining nvpair units. Bounded native
roundtrip/byte/boundary/allocation-failure checks and broken-encoder/assertion controls
pass in two isolated contexts. Engine startup still fails on four diagnostic/device/
I/O imports. Next qualify native diagnostics, review discovery reachability and real
SDK I/O binding; native feature/config and startup/fini/restart remain required.
Upstream accepts unknown root versions: the future Rust metadata ingress must
validate supported schema/version before persisted/untrusted data consumption.
Parser fuzz/recursion/overflow, sanitizer and wider exhaustion/interruption coverage
remain required before that exposure. No engine, filesystem or release gate closes.

The [startup link/prerequisite audit](../docs/evidence/openzfs-native-startup-link-2026-10-04/README.md)
now links a genuine static engine image and qualifies minimal private fatal SPL
diagnostics. Existing large loader geometry passes; actual engine startup remains
blocked. Current SDK realtime clock falsely succeeds after denied gettimeofday;
physical-page sysconf reads an uninitialized failed sysinfo result. Userland must
correct/qualify error handling and supply a matched SDK. Aether still needs real
scoped providers, native feature/CPU-state review, selected-profile composition and
measured resource/thread admission before startup/fini/restart and granted storage.
No fake clocks/entropy, ambient discovery or quota increase is adopted. All failures
are retained; [owner requirements](../docs/evidence/openzfs-native-startup-link-2026-10-04/source-review.md)
separate SDK fixes from absent runtime capabilities. No filesystem/release gate closes.

The [guarded-SDK independent intake](../docs/evidence/openzfs-sdk-guards-intake-2026-10-04/README.md)
now closes the two error-path consumption gates: candidate realtime/physical/
available-page ENOSYS and exact old-library240/241 controls pass natively. Only two
libc objects differ, including all duplicate occurrences in the comparison. Real
startup relinks with unchanged geometry; no engine entry runs or pin is promoted.
Native CPU-state guards are source-reviewed only; real scoped providers, selected
engine feature/profile qualification and measured admission remain the next local
work. Independent guard consumption is no longer an external SDK blocker.

The [granted-provider/time preflight](../docs/evidence/openzfs-native-provider-preflight-2026-10-04/README.md)
now passes five native provider/selector cases and eight checked helper cases.
Explicit virtual time advances and grant-page accounting restores after allocation;
upstream selectors deny AVX even on an AVX-advertising CPU with OSXSAVE absent.
Private gethrtime checks its grant result; all unavailable wall-time helpers fail125.
These are helper consumers, not rebuilt full engine objects or engine execution.
Calibrated time/entropy/identity/configuration, full feature closure and measured
owner-local memory/thread admission remain. Current8-MiB/two-child/four-admission
limits do not fit the host profile; no quota/ABI/SDK pin is changed. Local port work
can continue; no new sibling block or filesystem/release gate closure is claimed.

The [actual generic AES component](../docs/evidence/openzfs-native-aes-2026-10-04/README.md)
now passes qemu64/max known-answer128/192/256-bit encryption/decryption, in-place
and canary/immutability checks across advancing ticks; encryption241/decryption242/
frozen244 controls reject exactly. Real compiled generic object has no extended-state
instructions. Generic secret-indexed tables are not production encrypted-pool approval;
accelerated AES/GCM and whole-engine dispatch/feature/admission remain unqualified.
Kernel/SDK/quotas/pins are unchanged; no engine/volume or filesystem gate closes.

The [AES-NI/public dispatcher qualification](../docs/evidence/openzfs-native-aesni-2026-10-04/README.md)
passes five direct and13 final dispatcher cases using unchanged crypto and real
atomic code. Default/named/cycling choices, denied names/CPU, actual pre-init fatal
assertions, exact guarded key/block sizes and misaligned in-place buffers qualify
this subset. AES instructions fit the existing XMM context contract; no XSAVE/AVX
support is added. Full engine/GCM/side-channel/admission remain open. Next bounded
owned entropy-device work, followed by real provider/identity/configuration and
measured resource/thread admission. No filesystem/release gate closes.

Independent consumer pin/build/acceptance remains required for each handoff.
These prerequisites do not complete filesystem/package release requirements.

### Prior implementation order — 2026-09-06

The isolated [entropy device](../docs/ENTROPY-DEVICE.md) now passes real QEMU draws,
partial completion and exact device/completion/timeout rejection. Unknown DMA stays
reserved until VM teardown; all lab modes are excluded from release artifacts.
This is hardware transport only. Native owner capability/buffer/lifetime binding
is next, before an engine entropy consumer; no quality certification, fixed seed,
ambient authority or physical-hardware/IOMMU claim is adopted.

[Native entropy binding](../docs/NATIVE-ENTROPY.md) now passes exact draw/preflight/
quota/close/disabled controls and actual supervised generation1→2 replacement.
The4096-byte fixture budget is not an engine admission decision. Next rebuild the
actual libzpool random boundary against explicit checked grants; no ambient random
paths or fixed fallback. Public SDK facade/consumer adoption remains owner work;
private producer evidence does not close the engine/filesystem gate.

[Checked libzpool random helpers](../docs/evidence/openzfs-native-random-2026-10-04/README.md)
now pass15 native cases, real partial-progress fatality, three fresh supervised
admissions and actual backend exhaustion. Only the selected helper block is compiled;
no full-engine execution or public SDK adoption. Next measure an explicit bounded
task-queue/memory service policy, then implement owner-local admission; preserve
older limits and avoid blind inflation/serialization. Provider identity/config,
remaining feature closure and whole-engine lifecycle still gate R1-03.

Maintainer selected **SI-05 only**, then a return to planned R1-03 work.
The [ABI-15 producer bundle](../docs/evidence/init-capacity-2026-09-06/README.md)
is qualified; sys-init must independently review/pin it and execute its consumer
acceptance. Producer completion does not mark its guard story accepted.

Bounded concurrent child slots and all-child cleanup are qualified in STATE.
Concurrent musl create/join and bounded wake count are qualified in STATE.
Bounded requeue and actual multiple musl condition waiters are qualified in
STATE. Runtime reassessment identifies explicit remaining engine requirements.
Actual musl read/write-lock contention and key/destructor isolation/cleanup are
qualified in STATE. A bounded virtual-clock/timed-condition witness is also
qualified; general wall-clock/duration support remains open. Bounded detached
exit/reaping and cleanup are qualified in STATE. A repeated Linux engine demand
baseline records cumulative creates and allocator snapshots; named attribution
now reconciles every measured creation. A one-CPU engine-view comparison passes
with unchanged queue defaults; fixed floors remain above native limits. On resumption:
system/delay dispatch activity and callback/wait review before a smaller
explicit host worker profile or native budget selection. Role attribution now
reconciles the simultaneous census and identifies system/delay cleanup tails. The Linux observer measures peaks of 171/235 registered
workers for modeled one-CPU/host views; stack requests and event-sampled heap
fields are not resident stack usage, true heap peaks or native exit quiescence.
The bounded NATIVE-TASKQ runtime passes both profiles and failure/replacement
controls within existing grants; this does not establish full-engine capacity.
UL-059 runner-local outputs/no-child lifecycle and UL-067 child diagnostics/native
cat now take priority as recorded above. Resume this filesystem work after their
producer handoffs; independent consumer acceptance remains separately owned.
Pkg-mgr still needs actual shell/tools, filesystem and artifact/publication
contracts. R1 release scope is unchanged.

## M1 — Boot and framebuffer

Build a freestanding Zig x86_64 kernel and boot it using Limine under QEMU q35/OVMF. Validate boot information, print a serial milestone marker, draw a deterministic framebuffer pattern, and report failures clearly.

Complete when a documented build/run path works from a clean checkout, a headless serial smoke check has a bounded timeout and correct pass/fail behavior, and visible framebuffer output has been inspected. Pin the working toolchain, bootloader/protocol, firmware, and emulator setup. Kernel framebuffer code is permitted solely for bring-up; M4 removes normal rendering from the kernel.

Next task: [M1 implementation plan](M1-BOOT.md).

## M2 — One-core protection and local capabilities

Implement the minimum backed-memory, address-space/task, thread, capability-table, and bounded IPC contracts. Launch small freestanding Rust services from a boot module. Add user faults and basic timer preemption. Use a small local preemptive scheduling rule; defer policy frameworks.

Complete when two user tasks communicate, unauthorized operations and stale capabilities fail, a user memory fault is contained, a busy user task can be preempted, resource exhaustion fails predictably, and local derivation/revocation plus teardown have executable checks. Specify ABI and object lifetime details immediately before implementing them. No page can be reused while an old mapping remains effective.

## M3 — Two-core ownership and communication

Start a second CPU kernel instance. Partition mutable scheduler, task, capability, and allocation state by owner. Keep user address spaces core-local and tasks pinned. Bootstrap a fixed set of cross-core endpoint grants, then exchange bounded data messages through a narrowly mapped transport. Defer arbitrary remote capability transfer and shared application address spaces.

Complete when both cores run user workers, authorized work/results cross cores, forged routes or missing endpoint rights are rejected, full transport queues produce defined backpressure, and one worker's exit does not stop unrelated work. Inspect ownership and transport mappings to ensure a global mutable task/capability table has not replaced the intended design. Test ordinary user faults; kernel-instance fault containment is not claimed.

## M4 — Internal graphical POC and supervised workers

Fresh-source reproduction now rejects added/changed/removed/symlinked source
inputs and passes host checks, seven target cases and one-core boot on fresh local
caches. [Evidence](../docs/evidence/source-inventory-2026-09-06/README.md). This is a
working-tree snapshot using installed tools, not independent release reproduction.
Selected tool executables and the actual Rust compiler now have before/after
path/hash checks; [fresh qualification](../docs/evidence/reproduction-tools-2026-09-06/README.md)
retains their identity separately from full toolchain closure.

Move normal drawing into a Rust display service holding an explicit framebuffer mapping. Other services submit bounded display messages through delegated endpoints. Show two workers' progress and results on screen, with serial diagnostics retained. Keep the UI a small status/demo surface; keyboard input and window management are not release prerequisites.

Coordinate production supervision policy with the sys-init companion. First expose a narrow versioned native lifecycle seam for its fixed-image experiment, then extend the mechanisms to M4 cross-core restart. Kernel conformance fixtures do not count as sys-init integration. See [companion boundaries](../docs/COMPANION-PROJECTS.md).

The [fault recovery slice](M4-FAULT-RECOVERY.md) extends the separate supervisor experiment to five generations with retained fault records and bounded queued-result recovery.

Add a capability-scoped supervisor for a stateless worker. Demonstrate authorized termination, a fresh worker generation, rejection of stale handles, and continued work by the other worker. Kernel panic diagnostics may retain a documented emergency console, but normal graphical clients cannot invoke an unrestricted kernel rendering API.

Complete when a clean-checkout build, graphical run, and automated isolation/IPC/restart checks are reproducible; resource use stays bounded across repeated worker restarts; and README accurately describes the limits. Add contribution instructions, a project license decision, and concrete contributor tasks before public distribution. Publishing remains a separate action.

Actual selected random helpers now pass four native worker-context cases:
real draw, shared domain quota/close and whole-domain fatality125. Exact old
memory/TLS/output/64-yield checks stay intact. Two fixture failures are retained;
[worker packet](../docs/evidence/openzfs-native-random-workers-2026-10-04/README.md)
binds unchanged runtime/SDK/helper bytes. Next remove the four-lifetime-admission
obstacle through a bounded opt-in profile with unchanged live-slot/memory limits,
then caller-origin and owner-local resource geometry before whole-engine startup.

[Opt-in lifetime admission](../docs/NATIVE-THREAD-REUSE.md) now supports512
successful creations while preserving ordinary four/two-live-slot/memory bounds.
Fresh five-case matrix passes safe reuse, exact exhaustion, same-ID mutant254 and
supervised fresh budgets. Worker-origin creation and owner-local backing geometry
remain; this is a private producer profile, not a whole-engine capacity decision.

[Worker-origin profile](../docs/NATIVE-THREAD-ORIGIN.md) now qualifies nested
creation and exact-ID reaping while primary is parked, under the same domain grant,
with actual creator mask inheritance and unchanged slot/quota/lifetime bounds.
Legacy denial and omitted-mask mutant254 pass. Concrete upstream sync→async code
justifies the extension. Boot-owned backing/alias/metadata geometry remains the
next local capacity work; public SDK/engine/service/release adoption is separate.

[Boot backing prerequisite](../docs/NATIVE-BACKING.md) now qualifies usable-only
64MiB reservation/zero verification, malformed map rejection and exact corruption/
omitted-clear controls. This is isolated BSP boot, not native service admission.
Constant-size plans and fresh-root alias proof are qualified separately. The
[external native binding](../docs/NATIVE-EXTERNAL-BACKING.md) now also passes
existing-quota operations and supervised reuse. [One larger service memory owner](../docs/NATIVE-SERVICE-MEMORY.md) now qualifies off-stack metadata, 32 MiB
service/128-page companion bounds, image admission and storage lifetime checks.
[Larger-owner scans](../docs/NATIVE-SERVICE-SCANS.md) now have linear record/arena
work and three full-budget generations pass the existing watchdog; measured
syscall latency/WCET remains open. [Owner-local live workers](../docs/NATIVE-SERVICE-WORKERS.md) now qualify82
service records with two per small companion, exact capacity/pins/retirement and
park/wake/stop/replacement. [Actual musl service storage](../docs/NATIVE-SERVICE-MUSL.md)
now qualifies82 joinable pthreads,66-page stack/TLS/guard mappings, TLS/list
isolation, failed realloc preservation, counted park/wake, joins and stop/fault
replacement. This synthetic workload is not native engine peak/high-water or
production port adoption. [TSD and detached retirement](../docs/NATIVE-SERVICE-RETIREMENT.md)
now qualify actual keys/destructors, any-pending confirmed cleanup, descending82/
two completion and exact missing-destructor/early-unmap controls. Primary-driven
reaping alone does not prove blocked-creator or worker-origin progress.
[Worker-driven cleanup](../docs/NATIVE-SERVICE-REAPER.md) now qualifies real primary
join-blocking with one joinable helper counted within82/two and81/one detached
peers, descending cleanup and exact authority/unmap/omitted-park controls. This
is one bounded schedule, not82 detached engine workers or production reaper policy.
[Actual musl origin](../docs/NATIVE-SERVICE-ORIGIN.md) now qualifies two concurrent
creator preflights,40 detached descendants each, distinct mask inheritance and
confirmed worker-driven cleanup, with single-creator/small-peer variants. Creation
finishes before cleanup in that witness. [Dynamic lifetime](../docs/NATIVE-SERVICE-DYNAMIC.md)
now qualifies two full rounds,162 admissions/160 retirements and80 reused records
while actual next-round creation overlaps old cleanup. Atomic record ownership,
pending-peer native park/wake, primary join and exact controls pass. One ordinary
service/small-peer replacement and separate one-round capacity stop/replacement
qualify in the original bounded packet. [Checked native inputs](../docs/NATIVE-SERVICE-COPY.md)
copy masks/descriptors by separately validated page fragments; its eleven controls
and190 regressions pass, while its repeated-service result remains partial.
[Owner-local mapping pins](../docs/NATIVE-SERVICE-PINS.md) subsequently validates
unchanged coverage once and retains every per-context pin. Fifteen final native
cases qualify repeated full-service replacement and four-round322-admission reuse
under30 seconds, with a matching failed baseline and actual pin-bypass373 control.
Selected190 maintained targets, sixteen memory models and full host/scoped checks
pass separately. Old sealed results remain unchanged. Helpers leave80 of82
detached-peer slots; actual engine/stop-reuse/production acceptance remains open.
[Profile/admission reconciliation](../docs/evidence/openzfs-admission-review-2026-10-05/README.md)
now traces the guarded startup ELF to baseline queue objects; selected reduced
trial objects were never linked. The82-worker reduced host population plus one
additional helper needs at least83 child slots, and image-plus-fixture arithmetic
does not measure native heap/ARC. Rebuild the deliberately selected native profile
without host observers before adopting its resource assumptions; measure actual
helper placement, native demand and required providers before changing quotas.
[Selected native profile](../docs/evidence/openzfs-native-profile-2026-10-05/README.md)
now reconstructs the baseline byte-identically and replaces exactly three objects
with four reviewed queue-count expressions. Actual ELF instructions/data and old-
object/observer-link controls verify selection;1309 initial pages remain. This is
nonexecuted build/loader-model proof. Real provider caller adaptation, scoped
resources/configuration, production helpers and measured native heap/ARC/feature
closure still precede startup; historical host82 is not a native budget.
[Checked inline callers](../docs/evidence/openzfs-native-time-callers-2026-10-05/README.md)
now rebuild234 real header consumers after272 original byte-identical compilations;
37 objects change. Wall helpers directly check realtime, bypassing musl's ignored
gettimeofday clock failure. Four native125 denials, forty host boundary/precision
cases and actual old-header controls pass. Final ELF retains selected counts,
1312 initial pages and loader/W+X/TLS controls; no engine entry runs. Direct
cv_timedwait/cv_timedwait_hires/tpool clock callers and overflow-safe deadlines
still need adaptation before execution; full137 checks and failed attempts remain.
[Direct wait callers](../docs/evidence/openzfs-native-wait-clocks-2026-10-05/README.md)
now compare expiry before subtraction, check CV carry/seconds and tpool linger,
and deny failed clocks before wait/owner effects. Exactly two inputs change after
original/baseline byte identity.53 host cases/three old-source controls, six native
caller cases and both loader/W+X/TLS models pass; full137 checks and failures remain.
Test-only clock/wait/lbolt models do not qualify native timed blocking. Real
calibrated clocks/UTC and honest timed-wait/delay semantics, including the inherited
poll-based delay's ignored failure/arithmetic, remain before engine entry.
[Delay caller](../docs/evidence/openzfs-native-delay-2026-10-05/README.md) now checks
negative/oversized ticks before multiplication/narrowing and requires poll timeout0;
unsupported/interrupted/unexpected outcomes terminate125. One actual engine input
changes; previous image/original object byte identity,27 host cases/two old-source
controls, six actual native cases, full137 host/pin/scoped checks and final1312-page
loader/W+X/TLS models pass. Retained8ms/tick is not calibrated119Hz or elapsed-wait acceptance;
real clock/deadline parking/musl timed conditions remain required before entry.

[BSP elapsed source and absolute word waits](../docs/NATIVE-CLOCKS.md) now pass11
selected native cases and214 unchanged maintained target regressions. Reported-period
q35 HPET conversion replaces no legacy clock; real scheduler parks, matching wake,
deadline-preserving requeue, mapping pins and semantic controls are witnessed.
This private kernel prerequisite does not bind actual engine/libc clocks, establish
UTC, certify effective resolution/physical accuracy or qualify expanded service
workers. Actual musl conditions/sleep, production provider/SDK adoption and native
engine resource/startup acceptance remain required.

[Actual musl elapsed backend and service-scale timing](../docs/NATIVE-CLOCKS.md)
now qualify the private conditions/sleep prerequisite at82/two real pthreads,
including original-deadline retries, broadcast/mutex cleanup, timed stop/replacement
and exact early/disabled controls. Ordinary/repeated/spurious/stopped cohorts retain
TLS/TSD/join/mapping accounting and existing quotas. Maintained SDK adoption and
selected engine clock-domain/provider binding remain separate; no engine entry,
truthful UTC, physical calibration or production latency acceptance is claimed.
Compact results replace disposed archive recipes under the maintainer's retention
policy; historical evidence statements above are not current replay instructions.

[Selected OpenZFS elapsed callers](../docs/NATIVE-CLOCKS.md#openzfs-elapsed-caller-scope--2026-10-05)
now qualify actual libzpool monotonic CVs, retained absolute hires deadlines,
relative/tick waits and exact8388608ns tick delays at82/two-worker scale. Only
kernel.c/libtpool objects change in a byte-checked selected-engine relink; the full
engine is not entered. The actual libtpool initializer/deadline blocks pass, while
full pool lifecycle remains unqualified. Before engine entry, bind maintained
providers/SDK and qualify native heap/ARC/helpers plus truthful UTC and required
long waits. The private one-second backend explicitly rejects longer requests;
it cannot satisfy production idle linger by claiming those errors are timeouts.
Keep the owned port transforms for the next build; preserved current input bytes
and all released pins remain unchanged. Compact results and current progress
are recorded in STATE.

[Selected OpenZFS entropy binding](../docs/NATIVE-ENTROPY.md#selected-openzfs-binding-scope--2026-10-05)
now removes random-device opens and the EOF retry loop from the private port.
Actual init/fill/fini use existing delegated draws, exact bounded chunks, shared
4096-byte lifetime accounting and permanent close. Fresh domains receive fresh
authority; init/fini require quiescent callers. This does not add public getentropy,
scoped /dev, entropy-health/physical certification or a measured full-engine entropy
budget. The elapsed port remains in the derivative; selected full-engine relink
is build-only. Required resource/assigned-CPU/identity/configuration/volume bindings,
native heap/ARC/helpers, longer waits and truthful UTC still precede engine entry.

[Native malloc fallback measurement](../docs/OPENZFS-FEASIBILITY.md#native-allocation-measurement-scope--2026-10-06)
now qualifies actual default allocations, zero/aligned blocks, successful cache
callbacks, denied64MiB requests, free and stop/replacement under unchanged grants.
The82-worker fixture has2740 free pages before the probe and1706 at peak; its
1034-page probe cost is not a full-engine/ARC budget. Its32 image pages differ from
the selected engine's1312. Existing memory query already reports total grant quota.
[Bounded allocation failure](../docs/OPENZFS-FEASIBILITY.md#bounded-allocation-failure-scope--2026-10-06)
now qualifies one-attempt fatal NOFAIL and DEFAULT constructor-error cleanup on
actual native musl. Twenty-two cases and15 unchanged regressions pass, including
real exhaustion/metadata/constructor125, old-constructor410 and omitted-free399.
All198 inline-header consumers rebuild with original byte reproduction; full-engine
relink remains build-only. The private fatal policy is not blocking KM_SLEEP,
transaction rollback or recovery; full-engine adapter acceptance remains separate.
[Scoped resources and native ARC pressure](../docs/OPENZFS-FEASIBILITY.md#scoped-resource-binding-scope--2026-10-06)
now qualify checked total/free domain backing and one eligible CPU, replacing
unchecked host-wide queries and simulated pressure in the private port. Actual
user-space ARC initialization sets page-rounded10-percent headroom; native adapter
observations cross zero and negative pressure without entropy consumption or hidden
reclaim. Final28 cases and26 resource regressions pass. Header consumers and actual
ARC initializer rebuild; full selected relink remains build-only, fixture stats are
not a started ARC. Headroom is a target rather than reservation, and the32MiB floor
is unchanged. Review that target against actual engine/thread/helper needs.
The next [runtime integration gate](../docs/COMPANION-PROJECTS.md#native-storage-runtime-integration-gate--2026-10-07)
requires a matching maintained SDK/backend input before engine-entry qualification.
[Independent v2 intake](../docs/NATIVE-CLOCKS.md#maintained-runtime-intake-scope--2026-10-06)
now closes that delivery gate: sealed supplement rebuild and independent native
lifecycle/full81/one application capacity/charged reaper/stop/shutdown cases pass,
with named disabled804 and early802 controls. Default pins remain unchanged.
Strict whole-engine replacement link passes; old-adapter overlap rejects. Runtime
init/finish, selected provider/profile composition and measured engine/helper/ARC
admission still precede execution. The old82-worker host measurement plus reaper
requires83 records against the unchanged82 limit; no quota increase is selected.
[Actual OpenZFS waits with the maintained archive](../docs/NATIVE-CLOCKS.md#maintained-runtime-openzfs-waits-scope--2026-10-06)
now pass normal/stop/replacement at81/one application workers plus reaper, disabled804
and actual OpenZFS early-expiry125. Pinned baseline and actual caller map bindings,
21 focused host checks and frozen input verification pass. This closes caller
composition for the selected long CV/mutex paths; whole-provider composition,
explicit initialized engine lifecycle and measured native admission remain ahead.
[Whole-engine composition](../docs/OPENZFS-FEASIBILITY.md#maintained-engine-composition-scope--2026-10-06)
now builds all implemented ports with the maintained archive and an explicit
initial-thread runtime entry point. Actual map origins, old-adapter/archive-omission
controls and kernel structural parser pass;204 host checks pass at this integration
checkpoint. Host-controlled lifecycle failures reject false cleanup. No engine
is executed; required identity/configuration, native admission and actual linger/
retirement precede execution, with volume/UTC still required for persistence.
[Explicit startup metadata](../docs/OPENZFS-FEASIBILITY.md#explicit-storage-startup-metadata-scope--2026-10-06)
now replaces selected Linux discovery and implicit cache fallback with a validated
service-owned snapshot and declared empty cache; native lifecycle and missing/
malformed/unsupported controls pass. [Actual empty-engine admission](../docs/OPENZFS-FEASIBILITY.md#empty-engine-native-admission-scope--2026-10-06)
now executes startup/fini and three serial large-owner generations with the
maintained runtime. All18 symbol origins, small-image denial, exact reclaim/stale
checks, bounded detached settlement and zero-live finish pass. Omitted-fini224,
omitted-finish225 and missing-entropy125 reject. This closes empty-engine entry
under current grants, not pool lifecycle, measured peak heap/ARC budget or R1.
Scoped volume composition and truthful UTC now gate persistent pool experiments;
retain one authoritative volume owner and explicit generation-bound authority.
[Large-service region composition](../docs/NATIVE-BLOCK.md#large-service-region-composition-scope--2026-10-06)
now qualifies existing ABI14 region operations under8192-page service backing with
unchanged clients and transfer/lifetime rules. Six cases, five small-region Rust
regressions and a maintained-runtime regression pass;214 host checks pass at the
kernel composition checkpoint. This is raw transport, not engine vdev integration
or maintained pthread/block composition. Aether-userland now owns shared UTC establishment/policy by the maintainer
decision on2026-10-06; bounded raw source intake and maintained UTC remain work.
[Raw RTC intake](../docs/NATIVE-CLOCKS.md#raw-rtc-intake-scope--2026-10-06) and
[maintained runtime/volume composition](../docs/NATIVE-BLOCK.md#maintained-runtime-and-volume-scope--2026-10-06)
now pass explicit-date/replacement and same-disk fresh-VM/attenuation/corrupt controls.
No volume regrant, UTC estimate or pool follows; shared UTC delivery, checked engine
timestamp consumers and actual vdev/Rust service binding remain.
[Actual Rust volume/file-vdev binding](../docs/OPENZFS-FEASIBILITY.md#readwrite-startup-and-vdev-binding-scope--2026-10-06)
now passes actual open/size/reopening/close, positioned partial-I/O/flush, complete
write/fresh-VM disk readback, read-only and corrupt-input controls. The earlier
kernel_init(1) run is correctly READ-only; separate mode3 startup/fini now passes.
31 origins, three reclaims, replacement/close/bounds denials and223 host checks
pass. TRIM is unavailable; no host-path fallback, SDK, kernel-operation or sibling
change. Actual ZIO/pool/transaction/reboot persistence, shared UTC, production Rust
service/recovery and measured budgets remain; the8MiB vdev fixture is not a pool.
[Queued volume helper lifetime](../docs/OPENZFS-FEASIBILITY.md#queued-volume-helper-lifetime-scope--2026-10-06)
now passes real taskq-thread C/Rust I/O, read-only denial, NOSLEEP single-entry
exhaustion and parked-before-I/O revoke/drain. Actual inline dispatch rejects846;
38 origins, three successful reclaims and37 focused checks pass. Default volume
ELF stays byte-identical. This is no actual ZIO/pool, issued-device cancellation,
production service or general recovery acceptance. Next actual ZIO/completion;
shared UTC still gates persistent transactions/reboot.
[Actual no-UTC SPA gate](../docs/OPENZFS-FEASIBILITY.md#actual-spa-wall-time-gate--2026-10-06)
now identifies checked allocator timestamp rejection before activation.
[Shared UTC intake](../docs/OPENZFS-FEASIBILITY.md#shared-utc-engine-intake-scope--2026-10-06)
independently rebuilds the new opt-in userland candidate; four final native cases
pass normal/leap actual timestamp/SPA/taskq cleanup and source/policy denials.
The candidate is provisional: one initial missing-terminal observation remains
unexplained despite later green runs. Resolve that native/runtime liveness gate
before persistence qualification. The later [detached-reaper witness](../docs/NATIVE-CLOCKS.md#result-and-maintained-owner-handoff)
confirms a candidate runtime lock cycle under ordered overlapping exits; the
serial control passes clean retirement/reclaim. Aether-userland owns the fix and
a new sealed elapsed supplement plus UTC rebuild; independent intake and actual
helper reuse must pass before SPA/ZIO/persistence. The newer
[corrected v3 intake](../docs/NATIVE-CLOCKS.md#corrected-candidate-intake-result)
now independently passes both identical archive rebuilds, seven elapsed cases
and six actual UTC cases, including overlapping/serial/exhaustion/stop and eight
helper cycles per owner. [Actual empty SPA activation/root ZIO](../docs/OPENZFS-FEASIBILITY.md#empty-spa-activation-and-root-zio-scope--2026-10-06)
now passes on this explicit base: original activation/deactivation, exactly one
real synchronous completion,57 origins, three clean owner reclaims and exact
857/858 controls. This carries no data. The [real-vdev checkpoint](../docs/OPENZFS-FEASIBILITY.md#authoritative-vdev-and-physical-read-scope--2026-10-06)
now passes original allocation/open, healthy state/identity and completed open-probe
reads on64MiB, with exact867/401/zero reclaims; actual8MiB minimum rejection861 also
passes. These intentionally unclean checkpoints do not qualify the later512-byte
read/callback/data or retirement. Watchdog failures (including missing-callback
control) leave physical liveness open; neither teardown-only attribution nor a new
sibling delivery blocker is established. Zero-case false-green selection is fixed
and retained as invalid coverage. [Stage observations and physical qualification](../docs/OPENZFS-FEASIBILITY.md#physical-read-stage-observation-scope--2026-10-06)
now pass actual512-byte data/provider/callback/wait/borrow and full teardown,66
origins,18 first-owner rows plus two denied replacements and3 clean reclaims.
The four-case group passes exact861/862/860 rejections; separate closed-grant
ENXIO/buffer/callback/teardown passes. Whole media stays readonly. Root regression
passes three full lifetimes with its previous byte-identical ELF. The initial
missing-callback diagnostic fails at allocation C before healthy-open O/read Q;
identical engine/supervisor bytes later pass. Original open variability remains
unexplained. Next locate open/probe/child-taskq liveness under unchanged bounds;
passing physical/error lifetimes do not waive attribution or reader acceptance
before pool/create/import/transactions/reboot persistence. The later
[original probe/copy investigation](../docs/OPENZFS-FEASIBILITY.md#original-open-probe-observation-scope--2026-10-07)
locates long successful8192-byte provider calls and removes repeated per-byte
native page-record scans using at most two fully validated fragments per sector.
24 selected native cases and238 host tests pass, including cross-page/no-partial-
effect checks, physical controls and revoked ZIO. The paired checkpoint's engine
is identical; clock context near open falls from19.4s to1.4s, not an exact latency
measurement or replay of the old failure. Normal/control/revoked engine bytes also
remain identical. Next prepare the minimal writable-pool flush/order/uncertain-
write/recovery contract. The [prepared contract](../docs/OPENZFS-FEASIBILITY.md#writable-pool-preparation-contract--2026-10-07)
now requires actual leaf/provider flush evidence instead of parent-wait success,
explicit upstream bypass/error handling, exact partial effects/no adapter replay
and confirmed VM teardown before fresh authority after uncertain issued I/O.
Focused host body checks cover callback/provider errors and bypasses; synthetic
queue/device transport does not qualify native flush or durability. The native
physical write-ZIO/flush witness now [passes](../docs/OPENZFS-FEASIBILITY.md#native-physical-write-and-flush-scope--2026-10-07):
six selected native cases plus byte-identical read regression; actual original
write/callback/provider flush, fresh-VM readonly readback, exact512-byte media
effect, clean29/3/3 and18/3/3 lifetimes, and exact868/869/871 unclean controls.
Focused38 host tests pass; all1934 generated files are removed after compact
results. No pool or transaction follows. Next audit pool-create/import/TXG runtime
and resource closure, then measured create/export/fresh import and interrupted/
full/corrupt-media recovery after the remaining gates. Prior UTC
attribution and independent reader acceptance still gate persistent acceptance;
no initialized pool/service or release acceptance follows. The
[pool dependency audit](../docs/OPENZFS-FEASIBILITY.md#pool-dependency-and-resource-audit--2026-10-07)
now retains18 original pool/DMU/TXG roots on corrected UTC v3, with static imports,
relocations and native-loader structure checked. It executes no pool. Source
review records four DSL queues, two TXG workers, MMP despite multihost=off and five
auxiliary zthr workers; their runtime/resource peaks and drains remain unmeasured.
Before create/import acceptance resolve or independently bound prior UTC attribution,
obtain independent human review and qualify a concurrent TXG/provider completion
oracle. Then measure original create/commit/export/fresh import within existing
bounds and run the planned persistence integration/recovery checkpoint.
The [UTC assessment](../docs/OPENZFS-FEASIBILITY.md#utc-timeout-evidence-assessment--2026-10-07)
now verifies the initial failure's report/serial and v2/v3 defect/correction scope.
The original trace cannot identify its cause. The selected persistence path is
blocked on actual independent human disposition of that bounded superseded-v2
observation before the disposable v3 pool experiment. Preserve unknown attribution
even after any limited acceptance; no new sibling delivery blocker is established.
The [concurrent ledger preparation](../docs/OPENZFS-FEASIBILITY.md#concurrent-pool-io-witness-preparation--2026-10-07)
now passes focused host completion/reuse/error controls and a freestanding x86_64
build. It is not selected by the native runner. Actual provider/file-vdev/TXG
hooks, ordering and suppression/lifetime qualification remain local work while
human review is pending; no native pool or durable transaction is accepted.
The [file-vdev hooks](../docs/OPENZFS-FEASIBILITY.md#file-vdev-pool-observation-hooks--2026-10-07)
now observe admission before dispatch and original provider/leaf completion before
interrupt release. Actual-body host controls and target compilation pass, including
missing/bypassed flushes after prior success. The [TXG/label observations](../docs/OPENZFS-FEASIBILITY.md#original-txg-and-label-ordering-observations--2026-10-07)
now pass original-body host wait/order/retry controls and target object compilation.
Actual constructor identity/assigned DMU TXG publication, root/child/provider
association, native transport and full concurrent oracle qualification remain
before pool acceptance. Stage markers alone cannot establish durability.
The [deferred target binding](../docs/OPENZFS-FEASIBILITY.md#deferred-transaction-target-binding--2026-10-07)
now preserves early I/O/errors until the selected transaction supplies its actual
target once. Host denials/concurrency and target compilation pass; constructor
publication and phase/provider association remain native integration prerequisites.
The [constructor publication](../docs/OPENZFS-FEASIBILITY.md#constructor-identity-publication--2026-10-07)
now acquires actual SPA/leaf/file identity from successful original open and retires
it before original close; the old private plain bind path is removed. Host original-
body publication/foreign/reopening/retirement controls and target compilation pass.
The
[selected transaction join](../docs/OPENZFS-FEASIBILITY.md#selected-transaction-identity-join--2026-10-07)
now checks original DMU/DSL/SPA identities and getter target before commit can
release the transaction; foreign/closed/repeated joins and numeric-target bypass
reject in host checks.38 affected tests and target object build pass. The [ordering association](../docs/OPENZFS-FEASIBILITY.md#ordering-root-and-provider-association--2026-10-07)
now passes43 focused host tests,21 graph modes/five semantic mutations and three
target object builds. Actual original child/destructor/physical request/provider
bodies run over synthetic host graph execution;64 live tags/128 operations fit8KiB.
Native original pipeline, resource/drain and pool execution remain.
The [first native creation checkpoint](../docs/OPENZFS-FEASIBILITY.md#native-pool-creation-resource-checkpoint--2026-10-07)
passes static composition/loader checks but returns terminal872 before successful
creation; export and engine/provider/runtime retirement are unconfirmed. Exact
native errno/final media effects were not captured. Execution stopped and the
maintainer was notified under the uncertain-cleanup condition. Pinned original
validation rejects our explicit version5000 property; default selection by omission
and original errno/final media diagnostics are prepared and host/build checked,
with no native retry. Renewed human disposition is the next checkpoint. No sibling
handoff, resource-fit, durability or filesystem acceptance follows.
One [approved corrected-input run](../docs/OPENZFS-FEASIBILITY.md#approved-corrected-input-checkpoint--2026-10-07)
now reaches creation then returns generic125 without a client creation result or
confirmed export/engine/runtime retirement. Final media hash equals the seed and
outside canaries are intact; transient I/O/flush/quiescence remain unqualified.
Execution stopped and the maintainer was notified. Localize the shared125 failure
site before another disposition/run; do not infer exhausted quotas or widen limits.
The one-run approval is consumed. No original errno, resource-fit, filesystem or
companion acceptance follows.
[Failure125 diagnostics](../docs/OPENZFS-FEASIBILITY.md#failure125-localization-plan--2026-10-07)
now cover36 selected guard/fatal/panic sites, with failed allocation request/error
bits and unchanged125. One approved diagnostic run also returns125 with no site;
cleanup remains uncertain and execution stopped/reported. Eight omitted assertion/
time exits are now covered, bringing the private catalogue to44 sites.234 actual
time-header consumers are rebuilt and checked; diagnostic `C` exercises the raw
emitter without adding a phase. Seven diagnostic/26 runtime/two pool controls and
four allocation/four elapsed tests plus build-only composition pass. The corrected
image adds10,448 bytes/three pages over uninstrumented; no second guest run or
site attribution in that earlier attempt. One newly approved corrected44-site run
now identifies original `pthread_create` assertion failure in `zk_thread_create`,
joined by exact PC/disassembly/selected-source hash. Exact returned error/denial
branch remains unknown; cleanup unconfirmed and native execution stopped/reported.
The earlier108-worker source estimate used unselected upstream globals; the selected
profile correction below supersedes it.
The next approved diagnostic measures original pthread11/EAGAIN and actual
admission-live-limit value82 against82 capacity, joined by caller tid1 across32
bounded rows.47 focused host checks and fresh composition pass; native125 remains
failed, retirement unconfirmed, QEMU stopped and maintainer notified. No automatic
retry. Selected-source review corrects the earlier upstream-default estimate: actual
checked taskq globals are already1/1, with a conservative steady subtotal83.
Only the FREE-issue floor32-to8 changes in the private pool profile, preparing59
steady workers/62 including one-leaf helpers. Actual selected queue host progress,
drain and source-slot/hash controls pass (59 focused checks total); final build-only
origins/omission/loader and135 frozen inputs pass. No guest executed in this
preparation. [Compact receipt](../docs/evidence/openzfs-pool-workers-2026-10-07.json)
retains failures/hashes; owned outputs removed. Native map/backing/retirement and
create/export remain unqualified; reviewed composition and renewed disposition
precede another native attempt. No blanket queue clamp, quota/floor change or
persistence acceptance.
One approved worker-sized attempt now reaches first-owner create/export and
terminal0, but supervisor401/reclaimed0 prevents reclamation/replacement acceptance.
[Harness investigation](../docs/OPENZFS-FEASIBILITY.md#worker-sized-checkpoint-and-harness-correction--2026-10-07)
finds raw C padding/resource-row incompatibility and a wrong final-snapshot path.
Historical pool seed/canary conclusions concern unused media; executed final bytes
are unavailable after compaction. Exact diagnostic-frame/case-media corrections
pass39 host checks and build-only full native supervisor compilation (2299/4096).
Engine/runtime and resource policy unchanged. No second guest; renewed disposition
precedes corrected ownership/media qualification. Native execution/resource/recovery
qualification remains before pool acceptance.
The newly approved corrected diagnostic run now passes the complete bounded
create/export checkpoint: first-owner20 phases, two storage-denied BNR replacements,
three terminal0 owners, supervisor100/reclaimed3 and native pass. Actual attached
media changes with intact outside canaries; QEMU termination/wait confirmed.
All135 source inputs and reviewed engine/runtime/supervisor hashes match.
[Corrected native receipt](../docs/evidence/openzfs-pool-harness-run-2026-10-07.json)
retains compact results; previous failed/media-path evidence stays superseded.
Full `zig build test` passes once at this integration milestone, including302 Python
harness tests. Fresh import/readback,
assigned transaction/TXG/provider closure and interruption/full/corrupt recovery
remain before persistent filesystem/service/package or R1 acceptance.
The [fresh-import label reader preparation](../docs/OPENZFS-FEASIBILITY.md#fresh-import-label-intake-preparation--2026-10-07)
now passes six focused tests over33 synthetic provider/decoder scenarios and two
named missing-guard controls, plus selected-header native object compilation.
It is outside the passing create/export profile; real XDR/checksum/native intake,
SPA root construction, import helper/retirement budget and the paired same-disk
fresh-VM readback remain. No pool import or persistence follows from host decoding
scaffolding or object generation.
The [paired readonly import preparation](../docs/OPENZFS-FEASIBILITY.md#readonly-fresh-vm-import-preparation--2026-10-07)
passes49 focused methods and both actual engine/supervisor builds. One native pair
attempt then stopped in the creator after three terminal0 records without final
supervisor/reclamation/pass markers before the30-second watchdog. Fresh import was
not started; QEMU teardown confirmed. Actual shared disk changes/canaries and frozen
inputs are retained in a compact failure receipt, not a persistence pass. The
terminal precedes context stop/parent return and remaining checks/reclaim; failure
boundary and cause are unknown. Investigate/review that boundary and obtain renewed
human disposition before affected execution; no retry or limit increase. R1-03 and
filesystem/package/service acceptance remain open.
The [cleanup boundary preparation](../docs/OPENZFS-FEASIBILITY.md#final-cleanup-boundary-diagnostics-preparation--2026-10-07)
adds default-off scalar observations without changing cleanup/authority/limits.
43 focused checks and both actual trace-on/off kernel builds pass; current creator
engine/supervisor/runtime hashes match prior preparation. The full host attempt's
sole failure (new boolean classification) is retained and fixed with its focused
policy test; unchanged322 Python/158 Zig passes are reused. No guest ran or root
cause was fixed. Renewed disposition for one bounded create-only diagnostic comes
before another native attempt; paired import and R1-03 acceptance remain open.
One newly approved [diagnostic creator guest](../docs/evidence/openzfs-pool-cleanup-run-2026-10-07.json)
now passes all21 cleanup checkpoints, three terminal0 records,100/reclaimed3 and
native block marker within unchanged30s. Prelaunch artifact/frozen input/tool hashes
match; actual case media/canaries and host teardown are confirmed. Earlier timeout
did not reproduce and remains unattributed; no claim that it is fixed. No second
guest/import or resource/authority/pin change. Prepare the current readonly pair,
then obtain renewed disposition before native execution; single-run approval consumed.
The [current pair build preparation](../docs/evidence/openzfs-pool-import-cleanup-preparation-2026-10-07.json)
now verifies both original engine/supervisor profiles and exact prior ELF/runtime
hashes, startup WRITE/READ macros, origin/omission/loader and137 source/13 tools.
No paired guest ran. Same once-executed trace kernel is retained as a hash, not an
archived image. Renewed disposition is pending for one fresh two-guest same-disk
pair with READ-only import, first-failure stop and existing bounds. No import/R1
qualification or attribution of the old timeout follows from compilation.
The newly approved traced pair stops in its creator after generation2 completed
zeroing/phase5; verification/reclaim2 and final success are absent. Importer never
starts. [Compact failure](../docs/evidence/openzfs-pool-import-cleanup-run-2026-10-07.json)
records exact artifacts/frozen inputs, changed shared media/canaries and confirmed
host teardown; cause unknown, no silent retry or wider limits. A scoped full backing
u64 verification replaces the Debug per-byte assertion loop. Six focused tests
include every byte offset/two dirty bit values and named last-word/page omission
controls; actual trace-on/off kernels and one broad host check (324 Python methods
plus wired kernel/pins) pass. [Correction preparation](../docs/evidence/openzfs-backing-verification-preparation-2026-10-07.json)
qualifies host/build coverage only. Renewed disposition for one create-only diagnostic
precedes native qualification; paired import, transactions/recovery, FS and R1 stay open.
The [approved full-word verification creator run](../docs/evidence/openzfs-backing-verification-run-2026-10-07.json)
now passes all21 cleanup checkpoints on32MiB backing, three terminal0 owners,
final-live0, supervisor100/reclaimed3 and native block pass within unchanged30s.
Exact prepared artifacts/frozen inputs/tools, actual media/canaries and host teardown
are confirmed; outputs disposed. Earlier timeout causes remain unknown. No native
speed comparison or retrospective failure cleanup proof. The [current pair review](../docs/evidence/openzfs-pool-import-word-verification-preparation-2026-10-07.json)
binds this kernel to exact unchanged prior actual importer engine/supervisor builds;
no unnecessary rebuild/suite or guest. Renewed disposition for one fresh same-disk
create/export → readonly import/MOS readback pair precedes execution. First failure
stops; READ1/whole-disk equality/all cleanup and existing bounds remain mandatory.
No transaction/TXG/provider/recovery/filesystem or R1 acceptance yet.
The [latest paired native attempt](../docs/evidence/openzfs-pool-import-word-verification-run-2026-10-07.json)
passes creator lifecycle, then fresh readonly original SPA/MOS5000 readback on the
same exported disk. Importer873/supervisor401/reclaimed0 rejects final export/removal;
no importer reclaim. Entire import disk unchanged/canaries intact and both VMs
stopped; failure reported, no retry. Original spa_export requires global WRITE mode.
The [readonly shutdown correction](../docs/OPENZFS-FEASIBILITY.md#readonly-import-shutdown-correction--2026-10-07)
uses original spa_evict_all for a sole readonly/unreferenced private pool, requiring
empty namespace after retirement. READ1/global READ and all limits remain; no force
export or claim of on-media export for importer.87 focused methods and both actual
engine/supervisor builds pass; creator/kernel/supervisors/runtime stay exact, new
importer4,425,128 bytes/1316 pages. [Compact preparation](../docs/evidence/openzfs-readonly-retirement-preparation-2026-10-07.json)
records frozen hashes/checks and disposed outputs. Renewed disposition for one
corrected same-disk pair precedes native qualification, then a full integration
checkpoint. Transactions/TXG/recovery/filesystem and R1 remain open.
The [approved corrected readonly pair](../docs/evidence/openzfs-readonly-retirement-run-2026-10-07.json)
now passes creator export and fresh original SPA/MOS5000 readback/private retirement
on the same disk after confirmed VM teardown. Both guests complete all21 ordered
cleanup checkpoints, three terminal0 owners/final-live0/100/reclaimed3/native pass;
READ1/global READ and30s/82-context/32MiB remain. Entire import disk unchanged,
canaries intact; exact artifacts/frozen sources/tools and both host stops confirmed.
The [one full host checkpoint](../docs/evidence/openzfs-readonly-retirement-host-2026-10-07.json)
passes329 Python methods plus wired Zig/pins/workflow on410 frozen inputs. Outputs
disposed; no retry/extra guest/limit or sibling change. Earlier failed attempts remain
unqualified and earlier timeout causes unknown. Metadata-only import/retirement
closes this bounded prerequisite; importer retirement is not on-media export.
Next assigned application transaction/fresh data readback with actual TXG/root/child/
provider ordering, then interruption/full/corrupt recovery and Rust filesystem service.
No data durability, mounted filesystem, companion handoff or R1 acceptance yet.
The [assigned dataset helper preparation](../docs/OPENZFS-FEASIBILITY.md#assigned-dataset-data-probe-preparation--2026-10-07)
now passes51 focused methods, all64 single-byte corruptions/five named compiling
omissions and strict native object/build-only engine closure. Original dataset
ownership supplies a valid non-sync application transaction; actual getter/identity
join precedes commit, unassigned abort and assigned commit/error paths are explicit.
No guest/data transaction runs; original metadata pair/defaults stay unchanged and
its137 native sources match. Frozen140 preparation inputs/13 tools and loader/
supervisor bounds pass; outputs disposed, first host failures preserved. Next wire
opt-in writer/fresh readonly reader, compare assigned/recovered TXG, require actual
ordered provider/root evidence after drain/export, then qualify data/recovery/FS.
The [opt-in assigned-data pair](../docs/evidence/openzfs-pool-data-pair-run-2026-10-08.json)
now passes writer target6/strict ordering/nonforce export/full cleanup; fresh readonly
reader observes matching record/target6, then fails873 before retirement D with
reclaimed0. Both VMs stopped; whole import disk unchanged/canaries intact. Native
qualification stopped/reported, no retry or data-pair/FS/R1 acceptance. The
[data-only retirement drain correction](../docs/OPENZFS-FEASIBILITY.md#assigned-data-readonly-retirement-drain--2026-10-08)
waits original queued user eviction outside locks after closed borrows, preserving
actual-reference guards/default metadata/READ1/bounds. [Final correction preparation](../docs/evidence/openzfs-pool-data-drain-preparation-2026-10-08.json)
passes99 affected host methods and metadata/data build-only origin/artifact/budget
checks. Default metadata, passing writer/data supervisors and private runtime stay
exact; corrected importer4,426,240 bytes/1316 structural pages. Sources/tools match,
outputs removed. Renewed human disposition blocks another native pair; no corrected
guest or broad suite repeat. Recovery and FS remain next.
The [approved corrected assigned-data pair](../docs/evidence/openzfs-pool-data-drain-run-2026-10-08.json)
now passes actual original TXG6/64-byte data/strict ordered writer export, confirmed
VM stop and fresh READ-only matching record/TXG readback/queued-user drain/retirement.
Both guests pass all21 cleanup checkpoints/three terminal0/final-live0/100/reclaimed3;
whole import disk unchanged/canaries intact, both VMs stopped, artifacts/138 inputs/
13 tools exact. READ1/global READ/30s/82-context/32MiB/SDK/ABI/pins fixed; outputs removed.
The earlier873 failure stays unqualified; its actual reference count and earlier
unknown timeout causes were not directly measured. [The full host checkpoint](../docs/evidence/openzfs-pool-data-drain-host-2026-10-08.json)
passes341 Python methods and wired Zig/pins/workflow on413 frozen inputs/13 tools.
Next interruption/full/corrupt recovery, then Rust FS/runner/package/sys-init.
This closes a bounded data prerequisite, not mounted filesystem or R1 acceptance.
[The malformed label header control](../docs/evidence/openzfs-pool-corrupt-labels-run-2026-10-08.json)
now passes one normal data writer/export/full cleanup/VM stop, four encoding-byte
changes and fresh unchanged READ-only pre-import rejection. Exact BIUVWL/873/
cleanup1,2/401/reclaimed0/panic is expected; no guest reclaim/import/data recovery.
Entire corrupted import disk unchanged/canaries intact, both host finally waits
returned;144 frozen inputs/13 tools/QEMU and healthy artifact hashes exact.
103 focused methods, build-only exact identities and workflow115/experience/syntax/
simplicity checks pass; outputs removed, no broad suite repeat or sibling change.
Only unsupported header encoding is covered; interrupted commit acknowledgment,
full-media/deeper corruption and Rust filesystem/companion/R1 gates remain open.
[Active-label intake preparation](../docs/evidence/openzfs-active-label-preparation-2026-10-08.json)
now passes107 focused methods and native-header default/ACTIVE objects9,832 bytes/
identical23 imports. ACTIVE config stays ACTIVE; default EXPORTED object and both
healthy data-pair engines/supervisors/runtime remain byte-exact. State/geometry/
feature/errno/allocation cleanup and named omitted-state/forged-export controls
pass;145 inputs/13 tools/formatter/workflow115/simplicity match, outputs removed.
Two host test setup/errno-oracle failures are preserved and corrected. No active
native/CLI profile, envelope/ISO/guest or new rights/limits/pins/sibling handoff.
Next prepare explicit interrupted writer completion/ordered boundary, confirmed
VM stop and exact same-media guard before fresh ACTIVE-only READ import. This
prerequisite is not interrupted recovery, cross-label state agreement or R1 acceptance.
[Controlled after-sync/pre-export recovery](../docs/evidence/openzfs-interrupt-run-2026-10-08.json)
now passes one original assigned TXG6/data/strict ordered writer checkpoint, no
export or guest writer reclaim, confirmed host VM stop and exact same-media fresh
ACTIVE-only READ import. Reader recovers identical target/record and completes
queued-user drain/readonly retirement/all21 cleanup/three terminal0/final-live0/
100/reclaimed3. Whole import disk unchanged/canaries intact;145 native inputs/13
tools/QEMU/prelaunch artifacts match, outputs disposed, no unexpected outcome/retry.
[Preparation](../docs/evidence/openzfs-interrupt-preparation-2026-10-08.json) passes114
focused methods and preserves healthy default build hashes; [one full host checkpoint](../docs/evidence/openzfs-interrupt-host-2026-10-08.json)
passes362 Python methods plus wired Zig/pins/workflow on416 inputs/13 tools.
QEMU teardown may drain host caches: no physical power-loss/cache-loss durability,
public commit acknowledgment or live writer reclaim. Next before-ack interruption
contract/allowed recovered state, then full-media/deeper corruption before Rust
filesystem and persistent runner/package/sys-init/R1. Pins/SDK/ABI/rights/bounds
unchanged; no companion handoff. Earlier failures remain unqualified.
[Dirty pre-commit recovery](../docs/evidence/openzfs-uncommitted-run-2026-10-18.json)
now passes one baseline TXG6/data/strict ordered sync, dirty assigned TXG7 held
before commit and confirmed host writer VM stop, followed by fresh ACTIVE-only
READ import of baseline6/exact record and full readonly retirement/21 cleanup/
three terminal0/final-live0/100/reclaimed3. Whole import disk unchanged/canaries
intact;151 native inputs/13 tools/QEMU/artifacts exact, outputs disposed. No writer
export/guest reclaim, unexpected native outcome or retry. [Preparation](../docs/evidence/openzfs-uncommitted-preparation-2026-10-18.json)
passes129 focused methods and both after-sync/new build-only pairs; old after-sync
engines, importer/supervisors/runtime unchanged. Last full host checkpoint reused
for unchanged infrastructure only; next broad integration checkpoint is filesystem
service or earlier shared risk. One held transaction is not all pre-ack/after-commit
schedules or physical power-loss/cache-loss durability. Next full-media/deeper
corruption then Rust FS/runner/package/sys-init/R1; no public ABI/pin/rights change.
[Capacity/checksum batch](../docs/evidence/openzfs-storage-batch-run-2026-10-18.json)
now passes four guests: original128MiB dataset-reservation ENOSPC/property-data
preservation/export/fresh TXG6 readback/full cleanup, then a separate normal writer
and original SPA ENXIO6 rejection of16 declared checksum-bit changes. Both import
disks unchanged/canaries intact;169 inputs/13 tools/QEMU/artifacts exact and all VMs
stopped. Corrupt-reader guest reclaim is unqualified. [Preparation/review](../docs/evidence/openzfs-storage-batch-preparation-2026-10-18.json)
records141 focused methods, actual32-row supervisor/empty-case retention checks and
preserved failed/superseded preparations. New capacity reader is qualified fresh;
no prior reader/default equivalence is asserted for it. No full-suite repeat or
new ABI/SDK/pin/rights/quota. Next actual OpenZFS namespace/file layer and Rust
service/consumer contract, preserving mature on-disk semantics. Near-full file
writes, payload/parser/physical durability and persistent runner/package/sys-init/
R1 qualification remain; reservation denial is not a filled filesystem test.
[Real ZPL native namespace read](../docs/OPENZFS-FEASIBILITY.md#native-namespace-fixture-contract--2026-10-18)
now passes one READ1 QEMU import of the pinned upstream 1GiB fixture: complete
780,248-byte file SHA256, stale/traversal/missing/EOF/type denials, original objset
close/queued-user drain/readonly retirement and all 21 cleanup boundaries/three
terminal0/final-live0/100/reclaimed3. Entire media/guards unchanged; VM stopped.
Default data engines/supervisors remain byte-exact; kernel/SDK/ABI/rights/quotas/
pins unchanged. Preparation includes nine new methods/six compiling omissions,
actual Rust supervisor checks and one broad checkpoint: 158 Zig tests pass,
411/412 Python methods pass initially, then all seven recovery methods pass after
a test-only AST scaffold correction. Failed attempts retained, generated outputs
removed. Next minimal Rust connection/rights/generation-scoped read handles over
this real namespace, then original writable ZPL semantics and persistent consumer
composition. No general filesystem service, namespace writes, hostile-media/full-
storage/physical-power-loss or R1 acceptance is implied.
[Private Rust namespace owner core](../docs/OPENZFS-FEASIBILITY.md#rust-namespace-owner-contract--2026-10-18)
now passes ten host Rust scenarios/eight named compiling omission controls and
optimized no_std x86_64 codegen with1,048-byte fixed owner state. Four connections/
sixteen handles enforce peer/session/service epoch, rights attenuation, serial and
table exhaustion, bounded relative lookup/read, stale reuse and explicit teardown.
This unselected module has a synthetic provider, no transport or public API. Next
original-C context ownership/native composition, then authenticated service
publication; peer provenance and never-reused provisioning epochs remain required.
Prior native ZPL/C coverage is unchanged and does not qualify this new Rust path.
No kernel/SDK/ABI/limits/pins/default/sibling change or R1 gate closure follows.
[Rust owner/original-C composition](../docs/OPENZFS-FEASIBILITY.md#rust-zpl-composition-contract--2026-10-18)
now passes the upgraded opt-in namespace guest: full real-file SHA through Rust
handles, local peer/session/rights/stale/epoch denials, two owned contexts closed,
original drain/readonly retirement, all21 cleanup/three terminal0/live0/100/reclaimed3.
Entire guarded disk unchanged and VM stopped. Build-only required100 origins/
static loader plus exact default data engines/supervisors and full418-method host
checkpoint pass on695 frozen inputs; generated outputs removed. Original kernel,
SDK, ABI, released pins and resource limits stay fixed. Internal peer/epoch labels
remain synthetic; next authenticated request/reply/holder-generation composition,
then ZPL mutation/ordered persistence and consumers. No operational service,
credential/hostile-media/full-storage/physical-durability or R1 acceptance follows.
The
[human UTC disposition](../docs/OPENZFS-FEASIBILITY.md#required-independent-disposition)
is accepted for bounded disposable corrected-v3 pool experiments; original v2
cause stays unknown. Unexpected v3 stalls/missing terminals, unmatched completion or
uncertain cleanup stop affected qualification and must be reported to the
maintainer before further persistence acceptance.
The8MiB raw fixture cannot qualify a pool;
no default promotion, initialized pool or persistence follows. Attribution of the
original stall remains unknown under the accepted limited disposition. Eight actual
UTC SPA/taskq cycles per owner and exact short847 control retain their original scope. Separate actual-body host tests cover signed
nanosecond overflow; the requested2263 native date was observed as2063 and cannot
qualify it. Released/default pins, authority and budgets stay unchanged. Physical ZIO/error/
borrow lifetime, pool/create/import/transactions/reboot and Rust service/recovery
remain; this does not close R1 storage or boot-to-shell acceptance.
Working private probes do not constitute SDK integration. [Private segmented long waits](../docs/NATIVE-CLOCKS.md#segmented-long-wait-scope--2026-10-06)
now qualify two-second primary sleep/condition calls using unchanged one-second
native parks. Four selected cases and focused host checks pass; default ELF stays
byte-identical. [Expanded long sleep/stop](../docs/NATIVE-CLOCKS.md#service-long-sleep-and-stop-scope--2026-10-06)
now qualifies two-second sleep at82/two-worker scale, confirmed second-chunk stop
and fresh replacement, plus actual old-backend384 rejection. Final producer ELF
identity permits reuse of the passing cases; one default native regression and
focused host checks pass. Shared condition cohorts remain900ms. This does not
qualify82-worker long conditions, production30-second linger or a maintained SDK delivery.
Aether retains required
native provider/clock/budget work; this is not a whole-repository block.
Do not guess a larger quota,
lower the documented ARC floor or treat free backing as physical RAM/reserved heap.

Next acceptance requires measured
native operation/progress cost, engine281-lifetime coverage and total reaper
resource cost, provider identity/configuration and engine feature/runtime closure
including required heap behavior,
calibrated monotonic/UTC, then measured native engine startup/fini/restart. Keep supervisor domains
small; retained pool size is not an observed engine budget.

## Core-kernel memory backlog

### VM-01 — VM objects, address-space mappings and pmap

Added 2026-10-04 at the maintainer's request.
**Status: accepted architectural direction; implementation queued.**
Owner: Aether kernel; userland owns POSIX translation, filesystem/device services
retain backing policy, and sys-init retains admission/supervision policy. See the
[accepted design](../docs/VIRTUAL-MEMORY.md) and
[architecture contract](../docs/ARCHITECTURE.md#accepted-virtual-memory-direction).
Progress and executable evidence belong in [STATE](STATE.md).

Priority: core-kernel memory foundation, after protection/capability and explicit
backing-ownership prerequisites, before general mmap/file/shared/device mapping,
COW fork and Xorg/Mesa/GPU userspace integration. Preserve the current bounded
shell/storage order; schedule the smallest VM slice when its concrete consumer
needs it. This is accepted design, not optional later research or a new desktop
requirement for R1.

Dependencies and consumers:

1. Build on M2 protection, typed capabilities and task/backing lifetime, M3
   mapping/owner isolation, and the current boot/native backing ownership work.
   The [backing reservation experiment](../docs/NATIVE-BACKING.md) still requires
   qualified native binding; its trial is not a general allocator.
2. Deliver generic VM objects, internal address-space mappings in a balanced
   range tree, x86_64 pmap, 4 KiB demand-zero anonymous memory, bounded admission,
   security defaults and correct TLB cleanup first. Specify exact interfaces
   before code; preserve existing native memory/profile compatibility.
3. Add COW fork and shared VM-object mappings for broader R1-02 process/memory
   requirements. Add file backing with an authorized filesystem contract for
   R1-03/R1-04 mmap and executable loading; this is not a cyclic requirement
   that the filesystem port must use file-backed mmap to bootstrap.
4. Add device-backed objects/cache/teardown contracts before general Xorg/Mesa/GPU
   mappings. M5/M6 and later graphics keep their existing hardware acceptance
   gates. Implement aarch64 pmap when that target is brought up; it does not
   block the first x86_64 slice.

Acceptance for each enabled slice:

- Preserve the separation of object/backing, mapping metadata and hardware pmap;
  VM objects carry handle authority while mappings remain internal structures.
- Native witnesses and exact denial controls cover demand-zero, sharing/COW as
  enabled, mapping splits, bounds/offsets, stale/wrong-type/missing rights,
  allocation/metadata/table exhaustion and admission rollback.
- Enforce NX/W^X including aliases, guard pages and no page-zero mapping. Placement
  stays ASLR-ready; actual randomized placement needs its own entropy/evidence.
  No routine API or diagnostic discloses physical addresses.
- Unmap/protect/COW/teardown complete required TLB invalidation before reuse;
  references and device access are accounted for, RAM is cleared before exposure
  to another domain, and repeated lifetimes retain resource bounds. Cross-core
  sharing and device backings require their additional invalidation/quiescence
  witnesses before enablement.
- Qualify matching userland/loader consumers for enabled semantics. Do not infer
  general POSIX, file durability, GPU isolation or release readiness from a
  bounded fixture. Existing native/isolation regressions remain passing.

Deferred: huge pages, swap and sophisticated reclamation, userspace pagers,
Maple Tree/advanced mapping indexes and TLB optimizations until justified. Exact
rights/ABI, tree balancing, backing/writeback, COW and synchronization details
remain scoped implementation work. Architectural acceptance closes no runtime
milestone.

### VM-02 — Native mapping contract and musl backend

Added 2026-10-04 following maintainer agreement on the mmap design.
**Status: accepted architectural direction; implementation queued.**
Owner: Aether kernel for native VM enforcement; Aether-userland for the production
musl backend/POSIX adapters; filesystem/device services for backing policy.
See the [accepted design](../docs/MUSL-VM-BACKEND.md) and
[architecture boundary](../docs/ARCHITECTURE.md#accepted-musl-backend-and-mapping-boundary).
Progress is recorded only in [STATE](STATE.md).

Priority: follow the required [VM-01](#vm-01--vm-objects-address-space-mappings-and-pmap)
slice at the core-kernel/runtime boundary, before broader musl mmap and file/device
mapping consumers. R1-02 allocator/process memory and R1-03/R1-04 file-backed
execution are consumers; later Xorg/Mesa/GPU integration retains its own gates.
Preserve current bounded shell/storage/backing priorities and existing adapters;
initial anonymous support does not wait for all VM-01 backing classes or filesystem
completion. HO-01's provisional general object-table research is not a dependency.

Dependencies and acceptance:

1. Specify caller/resource/address-space authority, mapping/handle lifetime,
   bounds, errors, rollback, protection and TLB completion with the first native
   VM-01 slice. Anonymous creation/mapping/unmapping/protection use native calls;
   demand-zero faults stay in the kernel. Add no separate per-page memory RPC.
2. Qualify the small source-rebuilt musl backend against actual allocator metadata,
   PROT_NONE/guard protections, allocation/free and failed realloc preservation.
   Review internal symbols and assembly entry/teardown paths as enabled. Keep
   brk/remap unsupported with tested fallback until required; do not fake success.
3. Agree descriptor-to-authorized-backing and capability-transfer/cleanup contracts
   with existing owners before file/device mapping. Demonstrate denied authority,
   stale identity, service failure, resource exhaustion and admission rollback.
4. Require coherent writable shared-file/writeback/msync semantics before claiming
   them; copied buffers do not satisfy MAP_SHARED. Device mappings require cache,
   DMA quiescence and safe teardown evidence. General userspace pagers are deferred.
5. Preserve native-profile regressions and obtain matching userland witnesses for
   enabled semantics. Exact ABI/rights, placement/hints/fixed replacement, file
   coherence protocols and wider thread/process coverage remain scoped future work.

No new kernel code, ABI identity, rights bit, service topology, SDK pin, quota or
affected-consumer acceptance follows from this documentation decision.

## R1 — First release: persistent boot-to-shell system

Implementation checkpoint2026-10-23: decision0213's separate guarded owner now
fits measured code/resident/stack and implements bounded immutable-helper exec
and startup readiness on host/build checks. Fresh AF07 source intake/native
composition qualification remains before runtime acceptance; this does not close
persistent executable loading, writable public descriptors, Zsh/TTY/packages or
any R1 workstream. Root STATE records exact failures and next action.

Maintainer confirmation2026-10-19: persistent OpenZFS and interactive Zsh are the
VM-image target. No RAM-only interim image closes or replaces this work. Preserve
the existing post-R1 snapshot/rollback boundary; Zsh adds required consumer/TTY
qualification, not kernel-owned shell or filesystem policy.

Maintainer direction, 2026-09-06: boot into an interactive serial console is
acceptable; shell, runner, filesystem and package management are mandatory.
Native NVIDIA, desktop and network package fetching are not prerequisites.

| Workstream | Required outcome and owner boundary |
| --- | --- |
| R1-01 Console and terminal | Real bidirectional serial input/output with explicit grants, separate stdin/stdout/stderr, EOF/error behavior and the terminal operations the selected shell needs. Kernel owns bounded hardware access; userland owns terminal/line policy. No fabricated successful ioctl or signal setup. |
| R1-02 Shell/process runtime | Zsh is the required interactive boot shell and executes external programs. Aether-userland owns UL-008/009 TTY/ncurses/Zsh source/build/startup and editing/job-control qualification; retain existing dash process/system-shell coverage as a foundation, not Zsh acceptance. Implement the process identity, launch/exec/wait, descriptor flags/duplication, pipes/redirection and signal behavior its actual code and package scripts require. Define any deliberate shell adaptation with userland; a fixed builtin prompt is not completion. |
| R1-03 Persistent storage and filesystem | Capability-scoped block read/write/flush on a disposable QEMU disk, then an Aether-userland-owned Rust filesystem service over Aether's native engine/block contracts, with real paths/directories, metadata, create/write/truncate/rename/remove and persistence. Maintainer decision2026-10-18: retain OpenZFS C behind Rust for R1. Deliver persistent shell/runner/packages first; snapshot/rollback is post-R1. Bounded native existing-file overwrite, zero/nonzero shrink, initialized4096-byte extension, finite two/eight4096-byte writes and private empty-file create/same-directory rename/remove with clean-export/fresh-read pass; longer sustained/broader mutations, operational service and consumer assembly remain unqualified. RAM files are intermediate. |
| R1-04 Runner and executable loading | Integrate the userland public parser, copied startup, explicit I/O, observed results and failure handling. Run approved executables read from the filesystem, not only the current three fixed boot-image grants. Package names/paths never confer executable authority by themselves. |
| R1-05 Native package lifecycle | Run pkg-mgr on Aether to install a real package from local media/bundle, list/verify it, execute its program and remove it within an explicit target root. Package records and bytes persist; failure/interruption cannot report false success or silently damage unrelated files. Define supported update/recovery limits with pkg-mgr. Host-built artifacts alone do not close this. |
| R1-06 Boot/service assembly | sys-init starts storage/filesystem, terminal and process services in a supported dependency order, then launches the shell with scoped grants. Boot the same assembled image/storage layout tested by users. Failures surface without inventing general supervisor recovery. |
| R1-07 Candidate qualification | Frozen source/image identity, matching independent build, scoped reliability/interruption tests, third-party notices, security intake, user boot/package/recovery instructions and applicable release gates on the complete system. Publication remains separate. |

General memory expansion in R1-02 and file-backed mapping/loading in R1-03/R1-04
follow [VM-01](#vm-01--vm-objects-address-space-mappings-and-pmap) and its
[VM-02 musl mapping consumer](#vm-02--native-mapping-contract-and-musl-backend). Existing bounded
anonymous mmap/ELF/process-copy fixtures remain intermediate mechanisms, not
evidence that the accepted demand-paged/COW/object architecture is complete.

R1-03 current engine gate, 2026-10-19: the
[matched native Rust callback pair](../docs/evidence/rust-fs-recovery-stage-run-2026-10-19.json)
now passes pristine baseline, one actual Rust-policy16-byte write with independent
full file/hash/metadata/EOF, ordered target788/export, all21 cleanup boundaries and
fresh READ1 import/full recovery at TXG798 with unchanged whole media. Reviewed
images/sources/tools match; all VMs joined and outputs disposed. Writer60s/6000 is
standing-approved; readers/other profiles remain30s/3000. This opens the bounded
callback consumer handoff, not independent acceptance or an operational service.
Prior reader873 remains unfixed/unattributed. The
[writer-window correction](../docs/evidence/recovery-writer-window-2026-10-19.json)
now passes176 focused methods and fresh native baseline/Rust-write/recovery: the
selected reader accepts the paired writer's30s or60s timestamp horizon while
retaining its30s/3000 execution limit and all other checks. Default canonical reader
bytes and baseline/writer engines/all supervisors are unchanged. The next [native truncate-to-zero sequence](../docs/evidence/zpl-zero-2026-10-19.json)
also passes after184 focused methods: original target788/export, independently
checked size0/empty hash/metadata/two EOF, freshTXG798 and all21 cleanup per guest,
with exact recovered whole media and outputs disposed. Operational service delivery
and matched init consumption now gate end-to-end assembly; independent engine
nonzero shrink/extension, sustained work and broader namespace semantics remain open.
The [namespace batch](../docs/evidence/zpl-namespace-mutations-2026-10-19.json)
passes193 focused methods and one broad `zig build test` checkpoint with640 harness
tests. Seven prepared-before-launch guests qualify empty0600 create788/recover798,
same-directory no-replace rename804/recover814 and remove820/recover830 with exact
original object inventory restored, original file hash/EOF, private ACL/metadata,
ordered export/all21 cleanup per guest and exact whole-media/guards. First seeded
writer873 before import was a pristine782-label selector mismatch; the compiled798
regression and fresh corrected batch pass. First failure stays recorded, including
its missing actual QEMU-command retention; corrected commands are retained. Sources/
tools frozen, VMs stopped and generated outputs disposed. No permission/resource/
transaction-limit or pin lift. Authenticated Rust transport/reply-loss retirement, remaining
mutations/sustained IO, interactive Zsh and persistent runner/packages/ISO assembly
remain open; see STATE for the current result. No passing fixture substitutes for
matching consumer acceptance or assembled-system qualification.

The [file-size batch](../docs/evidence/zpl-file-sizes-2026-10-19.json) also passes:
202 focused methods, one652-method broad checkpoint and seven guests qualify
shrink780248->65539 at788/798, initialized zero-extension->69635 at804/814,
and two4096-byte writes->73722 at last821/831. Independent full content hashes,
metadata/two EOF, ordered export/all cleanup/media/guards pass. Sources/tools and
reviewed baseline/supervisors stay fixed; original C/two-record defaults unchanged;
owned outputs disposed. Longer same-engine work is not accepted from two writes.
The separately approved fixed eight-record/10240-byte observer result follows; all
other limits remain. No operational Rust service, consumer or R1 acceptance.

The separately approved [eight-write batch](../docs/evidence/zpl-eight-writes-2026-10-19.json)
also passes215 focused methods and seven fresh guests: shrink788/798,
extension804/814, eight4096-byte appends to102403/last827/fresh837. Full independent
intermediate/final hashes, metadata/two EOF, consuming close/reopen, ordered I/O/
export/all cleanup/media/guards pass. The fixed eight-record observer uses9704 of
10240 bytes; old two/8192 defaults are unchanged. No reset/retry. Six default C
objects and native shrink/extension engines/all supervisors remain exact; inputs
frozen, outputs disposed. Writers60s/6000/readers30s/3000 and other limits unchanged.
The prior652-method broad checkpoint is not a current full-suite claim for this
isolated extension. Operational userland delivery/matched init still gate assembly;
continuous service requires a bounded record-lifetime contract, not a count increase.

The [successful-record lifetime batch](../docs/evidence/zpl-write-lifetimes-2026-10-19.json)
now passes seven native guests and one broad checkpoint including674 harness tests.
One record/7596-byte combined observer within8192 supports eight4096-byte appends
to102403 at last827/fresh837 after the same shrink/extension seeds. Independent
full content/metadata/two EOF, consumed contexts and checked retirement, ordered
I/O/export/all cleanup/media/guards pass. Epochs and permanent outcome/device/
operation identities survive reuse; failed or borrowed records cannot retire.
Host64-write and concurrent/stale/failure/overflow controls pass; no general native
uptime claim. Old modes/artifacts/pins stay exact; frozen inputs, all VMs joined,
owned outputs disposed, compact commands/observations retained. Userland's current
one-write/context and no-observer-recycling contract still gates service adoption.
Its new filesystem-service candidate's25-member seal and bounded native
writable+IPC/client/negative/full-recovery matrix now pass as recorded below.
Operational service policy/exact executable and init consumption remain next;
this does not authorize a service call-bound lift or complete R1-03. See the current
[handoff](../docs/COMPANION-PROJECTS.md#userland-filesystem-service-native-handoff--2026-10-19).

The [userland-service native batch](../docs/evidence/fs-service-native-2026-10-19.json)
now qualifies the exact25-member AFSRPC01 candidate through the original engine
and authenticated writable AENBD003/ABI25 selection. All12 guests across normal,
lost-reply, partial-request and injected close-failure pass one16-byte write at37,
assigned788/fresh798, full780248-byte file/hash/metadata/EOF, writer ordered export/drains,
all cleanup/media/guards. Current686-method broad checkpoint passes; sources/tools
frozen, normal C/baseline/recovery artifacts exact, joined outputs disposed. This
closes the bounded producer matrix, not R1-03 or independent owner acceptance.
The maintainer approved a separate eight16-byte service profile. Its27-member
candidate and matched opt-in producer integration preserve the old delivery,
4096-byte API and observer7596/8192. Host lifetime/entry/intake/oracle and controller
size checks and the original-engine12-guest/fresh-recovery matrix pass.
Operational delivery still needs namespace operations, idle waiting, exact
executable/provisioning/readiness/shutdown and matched sys-init consumption.
The separately selected AFSRPC02 one-attempt namespace candidate now has its
[explicit authority/lifetime contract](../docs/OPENZFS-FEASIBILITY.md#namespace-service-implementation-contract--2026-10-19).
Require matching original-engine create/rename/remove with independent file/
namespace/allocation/metadata/EOF and fresh recovery, plus lost-reply and injected
close-failure recovery before accepting this bounded producer slice. This does
not permit zero-staged recycling or close the operational mixed-lifetime gate.
Persistent Zsh/package/runner/ISO acceptance remains open. [Current producer handoff](../docs/COMPANION-PROJECTS.md#userland-filesystem-service-native-handoff--2026-10-19).

R1-03 owner assignment, 2026-10-18: Aether-userland owns the operational Rust
filesystem service, including authenticated client/handle authority, writable alias
coherence and POSIX adaptation. Aether owns the native engine/block producer
contracts and qualification. [Producer handoff and remaining gates](../docs/OPENZFS-FEASIBILITY.md#filesystem-service-owner-and-producer-handoff--2026-10-18)
distinguish usable private prerequisites from a published service or SDK. Sys-init
and pkg-mgr retain lifecycle and installation policy. No sibling acceptance is
inferred from this assignment.

For R1-03, follow the [source-reviewed engine sequence](../docs/OPENZFS-FEASIBILITY.md#recommended-executable-sequence): supported-host engine measurements, bounded native runtime, grant-bound engine I/O, then filesystem/service composition. Current transport passes do not close R1-03.

Implementation order: define the serial console contract and bring up real input;
in parallel at the project level, userland supplies shell/process requirements and
pkg-mgr supplies its smallest native package workload. Implement block/storage and
file-backed execution as concrete dependencies require. Compose one executable
vertical slice before adding more permutations of isolated demo fixtures. Keep
policy in its existing companion owner; this plan does not authorize messages or
claim owner agreement on new APIs.

Release acceptance uses one candidate: boot to a prompt, create/read a file,
execute an external command through the runner, exercise required redirection/
pipeline behavior, install and run a package from local media, reboot and verify
file/package persistence, then verify/remove that package. Exercise declared
storage/package interruption recovery and denied authority with data verification.
Complete the matching sys-init/userland/pkg-mgr consuming witnesses. Existing
isolation, IPC and worker-restart regressions remain required. No fixture-only,
Linux-emulated, host-only or RAM-only result substitutes for this native path.

## M5 — Physical x86_64 display baseline

Boot the same project on the intended RTX 3060 machine through a removable UEFI boot medium. Record the machine/firmware details and confirm which adapter supplies the boot framebuffer. Validate visible output on the connected monitor, geometry/pitch/pixel format handling, CPU startup, and user isolation.

Complete only with observed results on that machine. Firmware-initialized output through the 3060 does not establish native NVIDIA modesetting or acceleration. Emulator results do not close this milestone. Instructions for creating physical boot media must identify the chosen device explicitly.

## M6 — Native RTX 3060 display feasibility and first enablement

Investigate one exact GPU/device and connected output before promising a driver architecture. Identify usable hardware documentation/source, firmware dependencies, PCI/BAR access, device memory, interrupts, reset behavior, and isolation requirements. Decide a narrowly scoped native display approach and keep device policy/large driver code in user space where feasible.

The first feasibility result must say whether an implementable route exists and list concrete gaps. Native enablement is a separate acceptance point: demonstrate the selected connector/mode and framebuffer scanout under Aether-controlled display setup, with capability-scoped resources and explicit failures. If feasibility is blocked, retain M5 framebuffer support and record the blocker; do not substitute a mock driver or claim completion.

Accelerated rendering, a compositor/window system, and broader hardware support require later scope. AI/CUDA compute follows graphics and is not part of M6.

## Later research, without POC dependencies

Persistent filesystem implementation is now required by R1, following the accepted
[filesystem direction](../docs/ARCHITECTURE.md#future-filesystem-service-direction).
Existing immutable/RAM file-service experiments are intermediate foundations.
Establish durable block I/O before evaluating retained upstream OpenZFS C in a
user-space service on disposable disk images. Acceptance requires recovery/data
verification under interruption and resource failure, scoped authority, and explicit
unsupported-feature behavior. Choose the default persistent engine only after port evidence; add other engines
when a concrete contributor experiment justifies them. System rollback and
DTrace compatibility each need their own later acceptance criteria.

Evaluate remote capability transfer/revocation, shared address spaces, placement policies, SMT/NUMA, richer graphics, POSIX source compatibility, and AI workloads only when a runnable experiment motivates them. Use specific programs or workloads to justify each addition.

### HO-01 — Handle/object model and POSIX compatibility review

Added 2026-10-04 at the maintainer's request. **Status: research / provisional;
review deferred.** Owner: Aether maintainer, with affected native and userland
consumer review before any interface adoption. The
[research document](../docs/HANDLE-OBJECT-RESEARCH.md) captures candidate resource
entries, native generation-tagged handles, the POSIX fd view, rights/delegation,
selective revocation, lifetime safety and performance tradeoffs. It is not a final
architectural decision or a request to implement a general object manager now.

Priority: below every R1 workstream and the current core-kernel delivery queue.
Revisit only after M2 protection/local capabilities and lifetime, M3 owner-local
IPC, and M4 stop/reclaim/restart are qualified; R1-01–07 acceptance is complete;
and a concrete post-R1 consumer motivates the broader contract. Current backing/
metadata/alias work, R1-02 process/FD runtime, R1-03 grant-bound persistent storage,
R1-04 loading and R1-06 sys-init assembly come first. Component evidence alone
cannot open the gate. M5/M6 graphics hardware milestones are not prerequisites.
HO-01 adds no dependency to M1–M4 or R1 and changes no active next action.

Review outcome: compare reuse of bounded typed capabilities with a thin general
resource table; resolve entry/handle layout, authorization and reference/transfer/
revocation semantics; specify bounds, failures, cleanup and concrete consumer
witnesses. Promote a selected design through a separate reviewed architectural
decision and scoped executable experiment. No new syscall, ABI identity, rights
bit, runtime behavior or companion acceptance is allocated by this backlog entry.

## Sys-init companion contract backlog

Status reconciled 2026-09-06: SI-01–03 have independent bounded ABI-6 acceptance
under [sys-init decision 0017](../sys-init/docs/decisions/0017-native-init-consumer.md).
[SI-04 consumer refresh](../sys-init/docs/evidence/native-slot-reuse-consumer-2026-09-05/README.md)
also passed. The remaining requirements below describe broader scope, not a queue
to reimplement accepted primitives. Sys-init's [decision 0042](../sys-init/docs/decisions/0042-reconciliation-evidence-review.md)
selected local confirmed-result mapping first. The later sys-init decision 0088
now requests the separate init-compatible fixture capacity decision tracked in SI-05;
this does not reopen the already accepted SI-01–04 primitive work.

Added 2026-09-05 at the maintainer's request. These were ordered companion follow-ons,
not blanket R1 prerequisites beyond the actual composed workload or a replacement for the current file-service
work. Progress is recorded only in [STATE](STATE.md). Motivation and required
consumer inputs: [sys-init integration gates](../sys-init/docs/INTEGRATION-GATES.md).
Sys-init owns service/readiness/recovery policy; Aether owns the minimal enforcing
mechanisms. Shared normative changes belong in Aether-standards, with explicit
version/pin adoption. Preserve existing native profiles and their smoke markers.

### SI-07 — Sustained sys-init lifetime, reuse and authorized shutdown

Queued 2026-09-24 at the maintainer's explicit request to unblock sys-init BG-067.
**Status: complete for the original bounded kernel backlog contract, 2026-10-03.**
The [completion review](../docs/evidence/si07-completion-review-2026-10-03/README.md)
verifies sustained idle/wakeup, useful reuse, finite/stale/foreign authority,
authorized quiescent halt and matching actual sys-init-owned consumption against
unchanged kernel sources. This closes the kernel dependency below, not full
SUSTAIN-01–06, production init, SDK or boot-to-shell/R1 acceptance. Those broader
protocol/product gates remain open under their existing interface/R1 work and
companion dispositions; no sibling item is closed on its owner’s behalf.
See the [2026-10-03 checkpoint](../docs/evidence/si07-native-2026-10-03/README.md).
Seeded native255/256/65534/65535 completion and both parent-carrier mismatch
directions now pass with cleanup/halt. This does not demonstrate65535 sequential
cycles or all malformed/stale/foreign/partial schedules; the child-profile
checkpoint below supplies its scoped mismatch witnesses.
[Verified companion intake](../docs/evidence/si07-handoff-review-2026-10-03/README.md)
now records nine producer and seven request-loop independent userland replays,
sys-init’s quiescent shutdown policy and four partial/Unknown error controls.
[Four native child-profile cases](../docs/evidence/si07-child-profile-2026-10-03/README.md)
now qualify both mismatch directions and matched controls.
[Four private-dispatch controls](../docs/evidence/si07-request-denial-2026-10-03/README.md)
qualify count/padding -13 and foreign/stale selectors -9, real reply and confirmed
cleanup/halt; stale follows one actual completed/reclaimed generation. This is
complete-frame fault injection, not forged native-endpoint coverage.
[Two composed wait schedules](../docs/evidence/si07-wait-composition-2026-10-03/README.md)
qualify retained readiness, delayed input, future-sequence denial and deadline
alongside one real command/cleanup. Lifecycle event retention includes channel/
terminal retirement. Next is matching sys-init/serial-shell contract reconciliation
and useful-session integration. Truncated-frame/cancellation/race coverage stays
open; these checkpoints do not close SUSTAIN-01–06.
The [v2 reconciliation](../docs/evidence/si07-v2-review-2026-09-29/REVIEW.md) accepts
AERIO002/NIO2/0x7b as an experimental design with full-width cohort checks and16-bit
retirement. It selects no new kernel operation/grant/quota and does not adopt
runtime bytes or supply sys-init approval.
See the [scoped review](../docs/NATIVE-INIT-COMMAND.md#si-07-sustained-profile-review--2026-09-25). Treat this
as the next sys-init dependency to schedule at a qualified checkpoint; preserve the
current shell work and its evidence. Do not infer completion from unrelated shell,
signal or pipeline milestones. Canonical consumer requirement and workload:
[sys-init sustained handoff](../sys-init/docs/SUSTAINED-INIT-HANDOFF.md).

Sys-init has qualified bounded script startup, partial-start rollback and stop on
ABI17, with old ABI9 compatibility. Its image-capacity blocker is resolved. The legacy
bounded fixtures retain total_ticks <3000, three worker/channel lifetime generations
and finish(100) with fixed reclaims. The opt-in AENSI001/ABI22 mechanism and matched
sys-init loop now qualify sustained idle/reuse/shutdown without changing those
legacy profiles; assembled useful-shell integration remains separate.
Earlier SI-01–06 acceptance remains valid within its recorded scope.

Required producer decisions and evidence, in dependency order:

1. **Lifetime and idle/wakeup.** Select an explicit sustained supervisor profile
   and clock/deadline contract, separating an external harness timeout from healthy
   guest lifetime. Specify supervisor eligibility/authority for existing wait/wakeup
   operations and race-safe wakeup for input, terminal state and shutdown. Reuse
   existing primitives where sufficient; do not merely raise the fixture counter.
2. **Reclaim and reuse.** Separate bounded live quotas from historical launch/channel
   counters. Qualify useful completed cycles beyond the current three-generation
   ceiling with bounded live resources, stale-handle rejection and an explicit
   finite-ID exhaustion policy. Keep policy retry limits owned by sys-init; normal
   completed work must not consume a fixture-only lifetime budget.
3. **Authorized shutdown.** Select a scoped request source and supported final action
   (halt, poweroff or reboot). Specify grant checks, errors and the conditions for
   finalization after dependent services stop and resources are settled. Foreign or
   denied requests must not alter lifecycle intent. Unsupported actions remain
   explicit. finish(100), worker stop and QEMU teardown are not operator shutdown.
4. **Matched handoff and consumer acceptance.** Freeze exact profile/version,
   grants, operations/errors, bounds, tool/build identities, sources and artifacts.
   Provide runnable positive and semantic-negative witnesses. Sys-init then pins,
   rebuilds and runs its own owner; producer completion is not consumer acceptance.

Minimum acceptance: boot existing real command/service artifacts, idle and wake
beyond the old guest deadline, complete more than three clean launch/channel reuse
cycles, exercise readiness before and during wait registration without lost wake,
and deliver an authorized shutdown after outstanding bounded work is settled.
Test stale/foreign authority, exhaustion behavior and denied final actions; preserve
old profile admission, smoke markers, existing mappings and released standards pins.
No capacity, quota, syscall number or ABI encoding is selected by this request.

Aether owns enforcing mechanisms; userland owns application/input semantics;
sys-init owns service ordering, restart policy, shutdown ordering and consuming
qualification. Reuse the existing bounded workload first; full shell expansion,
persistent storage and package assembly are separate R1 work. No journal, general
recovery manager, extra service, new platform or broad retrospective test campaign
is requested. Any future shared normative change belongs in Aether-standards.

Simplicity: keeping the bounded fixture is the simpler baseline but cannot meet
idle/reuse/shutdown requirements. Prefer a small explicit profile over duplicating
supervision policy inside Aether. No old path is retired by this planning change.
Documentation impact is ROADMAP/STATE plus the existing consumer handoff. No runtime,
unsafe boundary, dependency, authority or resource-budget change is authorized as
implemented by this entry. Planning checks: inventory/pin integrity, links and diff
whitespace; implementation requires the scoped native and consumer witnesses above.

### SI-06 — Composed init lifecycle capacity (16 KiB proposal)

Requested 2026-09-07 from sys-init BG-061 / decision 0174. The separately
versioned, opt-in **16,384-byte init supervisor code profile** now has a
[qualified producer packet](../docs/evidence/init-composed-capacity-2026-09-07/README.md):
AENIN003 / ABI 16, preserving V1/V2 and the 4 KiB stack. Producer qualification
and copied-candidate execution do not substitute for independent sys-init intake. Aether owns the exact envelope/ABI and mapping
contract; sys-init owns
Terminal/reclaim policy and independent consuming acceptance. SI-05 stays accepted
within its existing scope; this item does not silently enlarge ABI 15.

The composed consumer retains launch acknowledgment/history, captures the actual
terminal sample and records its reclaim obligation. Its refined baseline linker
span is 11,680 bytes against its pinned 8,192-byte bound; diagnostic size/LTO
options still exceed that limit. At intake the candidate had not been executed
or adopted; the producer packet
now retains a private, minimally adapted six-case witness. Independent adoption
remains pending. The additional headroom is intended for reclaim/Cleaned
integration, not a claim
that those future stages will fit or that 16 KiB is a production memory budget.
See the [capacity handoff](../sys-init/docs/INIT-CAPACITY-HANDOFF.md),
[retained failed builds](../sys-init/docs/evidence/native-terminal-capacity-2026-09-07/README.md)
and [consumer integration gates](../sys-init/docs/INTEGRATION-GATES.md).

Acceptance:

- Define an opt-in init-compatible profile at 16,384 code bytes. Producer assigns
  identifiers. Preserve AENIN001/ABI 6 at 4,096 and AENIN002/ABI 15 at 8,192,
  including old oversize rejection, lifecycle semantics, grants and smoke markers.
  Do not substitute a general native-C profile or silently add worker authority.
- Specify checked envelope lengths/arithmetic, all four code-page mappings,
  immutable RX code, read-only/NX aliases, zero tails, entry and complete cleanup.
  Preserve the two-worker/init-observer ownership contract unless a separate
  reviewed change explicitly replaces it.
- Validate stack capacity separately. The candidate root frame alone is 3,288
  bytes before caller/saved-register/nested frames; a larger code mapping is not
  a 4 KiB stack witness. Keep the stack limit unchanged unless separately specified
  and qualified; retain actual composed stack execution evidence.
- Test execution from added code pages, below/at/above-limit and old-profile
  oversize rejection, malformed/truncated/overflow input, code write/alias and
  stack execute denial, tail zeroing, normal/closed cleanup and older regressions.
- Supply complete immutable producer, SDK, tool, source and raw-result artifacts
  for offline consumer pinning. Preserve failed attempts; do not extend older
  source-closure exceptions to the new handoff.
- Require sys-init's independent rebuild and consuming Terminal/reclaim-capture
  witness, including owner/unsealed/partial-source and incomplete-capture controls,
  before claiming integration. Issued reclaim execution and Cleaned follow next;
  producer completion alone does not complete those consumer steps.

This producer unblock is available for independent BG-061 consumption;
current status and exact qualification counts are recorded in STATE. Resume the
planned R1-03 ARC serial-eviction experiment while sys-init owns its intake. Shared standards remain
in Aether-standards with unchanged release pins; no shared-rule adoption is implied.

### SI-05 — Init-compatible supervisor image capacity

Queued 2026-09-06 from sys-init BG-058 / decision 0088. Next producer decision
for the blocked native conflict-guard experiment. Producer qualification is now
[available](../docs/evidence/init-capacity-2026-09-06/README.md); independent sys-init
consumption remains open. Resume R1-03 concurrency next per maintainer direction. Aether owns the profile and loader contract; sys-init owns guard policy,
its resource/lifetime checks and independent consuming acceptance.

The consumer's bounded 80-link study found no complete guard variant within the
existing 4096-byte supervisor limit; its best maximum is 4528 bytes. AENPG001's
8192-byte allowance is not a substitute: ABI 8 supplies a third executable grant,
uses different slots/oracles and does not enable the init clock/observation/wait
operation dispatch. See the [consumer findings](../sys-init/docs/research/NATIVE-CONFLICT-GUARD-LAYOUT.md)
and [capacity request](../sys-init/docs/research/NATIVE-INIT-IMAGE-CAPACITY-REQUEST.md).

Acceptance:

- Decide a separately versioned init-compatible bounded profile, proposed at
  8192 supervisor bytes, or record a concrete alternative with the consumer.
  Producer selects magic/ABI identity; this backlog does not allocate either.
  Preserve existing AENIN001/ABI 6 bytes, 4096-byte rejection and old profiles.
- Define bootstrap grants, caller/slot identity and init operation semantics,
  checked envelope arithmetic, exact lengths/reserved fields, code-page and
  stack limits. Code remains immutable RX with no writable alias; stack remains
  non-executable. Define tail initialization and cleanup for every mapped page.
- Preserve lifecycle, pending-wait ownership, generation isolation and owner-death
  semantics, or explicitly version replacements with migration and exact oracles.
  Keep all old profile exit contracts and smoke markers unchanged.
- Retain target execution on the second code page, below/at/above-limit cases,
  malformed/truncated/overflow rejection before admission, mapping/cleanup evidence
  and affected older regressions. Supply source/tool/input pins and exact raw
  outcomes; parsing or linking alone is insufficient.
- Require sys-init's fresh consuming acceptance of all 151 existing semantic
  cases and five proposed guard cases before claiming that integration. Denied
  construction and closed reoffer remain additional consumer qualification work.
  Preserve failed link evidence; it is not semantic rejection coverage.

This is an experimental image-capacity dependency, not a production memory budget,
new lifecycle-policy API, accepted shared standard or producer implementation.
Future shared normative changes use Aether-standards; exact native contract stays
in Aether. Progress belongs in STATE and the consumer's BG-058.

### SI-01 — Native wait and service-deadline contract

Accepted architectural direction, 2026-10-04:
[clocks and timers](../docs/CLOCKS-TIMERS.md).
**Status: architecture accepted; broader calibrated clock/timer implementation
queued/partial under this existing item.** Separate source observation, local
hardware deadline delivery and user-space UTC policy. Aether owns native mechanisms;
musl/runtime owns POSIX adaptation; sys-init retains supervision policy. Exact UTC
maintainer/provider placement remains affected-owner work. Preserve bounded ABI-6,
init/ABI24 and virtual-clock evidence below without promoting it to calibrated time.

Priority/dependencies: preserve current backing/storage/boot-to-shell order. Qualify
a calibrated monotonic provider, then [UP-04](#up-04--readiness-and-native-wait-many)
elapsed deadline/park semantics and required musl/storage consumers. Coordinate
UP-02 signal interruption and R1-02 runtime/R1-03 engine and timestamps/R1-06 startup.
Truthful realtime follows required calendar consumers; timer handles, one-shot hardware
and broader SMP follow concrete workloads. Whole-feature clock/timer completion is
not a blanket R1 prerequisite. No new ABI, clock ID, rights bit or quota is allocated.

Additional acceptance for enabled slices:

The first [BSP q35 elapsed-clock/absolute-word slice](../docs/NATIVE-CLOCKS.md)
has private producer proof for repeated interrupt-independent reads, real deadline
expiration, wake/requeue/pinning and fail-closed controls. This preserves old ABI-6/
virtual time. It does not complete libc timed conditions, UTC, effective resolution,
independent consuming-owner acceptance or broader SMP/provider qualification.

- Qualify source frequency/stability, checked 64-bit conversion, actual resolution,
  ordering, delayed interrupt behavior, range/overflow and supported QEMU fallback.
  Counted interrupts and virtual ticks cannot satisfy calibrated elapsed/UTC claims.
- Keep deadline queues/hardware per-core; qualify common-timeline or counter-conversion
  semantics before cross-core exposure. Remote control uses authorized messages and
  one owner; unrelated local tick epochs cannot satisfy system-wide monotonic time.
- Qualify absolute deadlines, no early expiration under the declared rounding rule,
  already expired/indefinite waits, event/timeout ties, registration races and spurious
  wakeups without extending the original deadline. Retain cancellation/interruption
  outcomes and cleanup; timeout cannot prove I/O cancellation, stop or quiescence.
- Match actual musl clock/sleep/timed-thread semantics, including realtime condition
  defaults, atomic mutex release/wait/reacquisition, errors and untouched outputs on
  failure where required. Rebuild actual engine helper consumers with checked providers;
  guarded SDK/virtual-time evidence alone does not qualify unchanged engine bodies.
- Establish truthful UTC/source validity and distinct adjustment authority; retain
  monotonic independence and reevaluate supported realtime deadlines on adjustment.
  Qualify one-shot timer owner/arm generation, rearm/cancel/late-delivery, capacity,
  teardown and retained expiration semantics when an independent timer is required.
- Require native and independent affected-owner positive/semantic denial witnesses.
  Defer exact hardware/ABI/calibration publication, broad SMP/power/recovery, periodic
  adapters, coalescing, CPU clocks, fast reads and advanced indexes until justified.
  Nanosecond units and timer readiness do not establish hard real-time scheduling.

Bounded ABI-6 interrupt-time/registered-observation scope accepted by sys-init.
Elapsed/suspend-aware clocks and blocking waits remain outside that scope; a
concrete consumer workload is needed before extension. Original priority was
first in this queue; coordinates sys-init BG-032/BG-040.
Define the smallest BSP-local clock and wait/observation seam needed by an actual
sys-init readiness timeout or terminal-wait workload. Fixed PIT/APIC fixture
watchdogs do not establish a service timing API.

Acceptance:

- Specify clock units, monotonicity, range/wrap and suspend assumptions; deadline
  boundaries; required authority; wait registration/status-observation ordering;
  cancellation, spurious wakeups, resource bounds and failure results. Prevent
  lost events between observing state and waiting. Declare unsupported semantics.
- Demonstrate event-before-wait, event-during-registration, timeout at the exact
  boundary, cancellation, stale/foreign handle denial and bounded exhaustion.
  Keep service retry/admission policy out of the kernel.
- Supply a versioned domain contract, pinned source/build inputs and runnable
  producer/consumer artifacts. Retain positive and designated semantic-negative
  QEMU evidence, then require a sys-init-owned consuming witness before claiming
  integration. Do not infer SMP behavior from this initial local slice.

### SI-02 — Review channel transfer for delegated readiness

Supervisor-launched helper transfer and generation-bound readiness mapping are
accepted in the ABI-6 consumer. Arbitrary delegation/revocation remains unsupported,
not an outstanding request to add a parallel grant API. Original second-priority
review could proceed independently of SI-01. Coordinates sys-init
BG-032/BG-040 and userland's process/descriptor work. Start from
[NATIVE-CHANNEL](../docs/NATIVE-CHANNEL.md) and
[NATIVE-FILES](../docs/NATIVE-FILES.md), which already implement validated launch
transfer of one endpoint or an endpoint pair. Do not introduce a parallel grant
mechanism merely because the older sys-init fixture lacked transfer.

Acceptance:

- Map an actual first-party/helper readiness workload onto existing endpoints:
  who owns each end, which generation it identifies, who may notify, and how
  worker/reader closure and buffered messages affect readiness admission.
- Record exactly which transfer, helper delegation, revocation and stale-message
  requirements are already met, unsupported or require an extension. A numeric
  handle/payload field is not authority; endpoint transfer is not arbitrary
  duplication, implicit inheritance or general revocation.
- Exercise failed-launch ownership preservation, successful-transfer denial to
  the old holder, foreign/stale sender rejection, helper/owner termination,
  buffered late notification and replacement-generation isolation. Reuse existing
  mechanisms where sufficient; specify only demonstrated missing primitives.
- Retain kernel enforcement evidence and an actual sys-init consumer with matching
  artifacts. If no extension is needed, close the item with the mapping and
  consuming witness rather than adding machinery. Readiness/dependency policy
  remains in sys-init; any wait/deadline dependency is explicit under SI-01.

### SI-03 — Supervisor death, surviving ownership and recovery seam

Whole-domain fail-closed shutdown is independently accepted for ABI 6. Replacement,
recovery inventory and unknown-result reconciliation remain unimplemented and need
an owner-selected contract; decision 0042 explicitly does not infer them from
terminal observations. Original third priority coordinates sys-init BG-028/BG-033.
Current native profiles treat
supervisor death as fatal; the M4 worker-restart fixture is not supervisor
recovery. First select a bounded single-core owner/recovery experiment with the
consumer, without assuming ambient root authority or automatic restart policy.

Acceptance:

- Specify who retains worker, endpoint, terminal-record and backing ownership
  after supervisor exit/fault; when admission closes; and how an authorized
  replacement may obtain a bounded inventory and observation/reclaim authority.
  Distinguish termination, revocation, mapping cleanup and reclamation.
- Define old-supervisor/grant invalidation, incomplete or lost observations,
  recovery resource exhaustion and failure of the replacement itself. State
  whether recovery is supported or an explicit fail-closed outcome is the first
  accepted scope; do not label a panic as successful recovery.
- Exercise supervisor death with live and terminal workers, queued bytes/events,
  stale owner attempts and bounded cleanup. Retain designated negative controls
  and a sys-init-owned policy witness before expanding integration claims.
- Describe the later cross-core ownership/cleanup questions using existing M4
  evidence, but keep SMP recovery out of the local acceptance unless separately
  specified and executed. Do not introduce a global mutable ownership table.

### SI-04 — Fix sequential cross-slot reuse after reclamation

Producer correction and independent sys-init consuming refresh verified.
[Consumer evidence](../sys-init/docs/evidence/native-slot-reuse-consumer-2026-09-05/README.md)
passes forward/reverse no-wait orders plus all nine adapter cases against the same
corrected producer pin. SI-04 is resolved for these bounded orders; general
lifecycle/recovery expansion remains separate.
The existing metadata-clear fix now passes the exact retained no-wait probe,
the reverse order and all nine sys-init adapter cases against pinned producer
summary `3a399587b34010302d25838d9f8e1cc73e2b93bec1ac673321326494bde1f155`.
Aether's regular `--init` suite also includes both sequential orders, with nine
cases passing. [Results and reproduction](../docs/evidence/native-slot-reuse-2026-09-05/README.md).
The earlier Aether-run companion-source checks remain distinct from sys-init's
subsequent independent refresh and decision 0019 service/dependent workload.

Originally queued 2026-09-05 at the maintainer's request. Highest-priority sys-init integration
follow-on before broadening service/dependent replacement orders; coordinates
sys-init BG-032/BG-040. Aether owns native alias/mapping/reclaim correctness;
sys-init owns policy and the consuming refresh. This does not change unrelated
process/descriptor work or add a new shared standard.

Original failure investigation (superseded by the correction and consumer refresh):
[consumer checkpoint and handoff](../sys-init/docs/NATIVE-ADAPTER.md#kernel-order-gate-and-handoff)
retain a minimal no-wait ABI-6 probe: launch slot 0, observe exit 17, close reader,
reclaim; do the same for slot 1; then reuse slot 0. It failed against producer
summary SHA256 `86d52e49898fcb859fcb7ffd7af46310152381590753f72e6ba690f17a14c9e4`
with kernel vector 14, CS=8, error=3, RIP `ffffffff80030af0`, after both terminal
records. LLVM 21 resolves the faulting instruction to `memset`; the caller/root
cause is not established. Reprotecting reclaimed backing via `aliases(owner,
false)` during another slot's load is an investigation lead, not a confirmed fix.
This is a frozen-producer finding, not a claim that an untested current checkout
still has the bug.

Evidence: [failed report](../sys-init/docs/evidence/native-adapter-2026-09-05/order-probe/results.json),
[serial log](../sys-init/docs/evidence/native-adapter-2026-09-05/order-probe/cases/adapter-edges/native-serial.log),
[minimal source](../sys-init/docs/evidence/native-adapter-2026-09-05/order-probe/source/prototypes/native-supervisor/init.rs).
The bundle also retains the kernel ELF, frozen producer archive and command/input
hashes. From the sys-init repository, reproduce with explicit offline dependencies
and a fresh private work directory:

```sh
python3 docs/evidence/native-adapter-2026-09-05/order-probe/source/tests/native-init.py --producer docs/evidence/native-adapter-2026-09-05/producer --summary-pin 86d52e49898fcb859fcb7ffd7af46310152381590753f72e6ba690f17a14c9e4 --deps PINNED_AETHER_DEPS --work NEW_PRIVATE_DIRECTORY
```

Acceptance:

- Reproduce/localize the retained failure, or demonstrate that newer pinned
  producer inputs already correct it. Keep the failed historical evidence intact.
- Correct the enforcing ownership/alias cleanup boundary without widening grants
  or weakening zeroing, immutable-page protection, stale rejection or code bounds.
  Add a regression for sequential slot-0/slot-1/slot-0 reclaim/reuse and exercise
  the reverse slot order; retain the original overlapping-worker order as well.
- Require `NATIVE supervisor result=100 reclaimed=3` and
  `AETHER NATIVE INIT PASS` from the consumer's minimal order probe. A kernel
  panic, build/boot failure or watchdog is failure, not an expected passing control.
- Run relevant kernel tests and affected native regressions, including deadline,
  readiness, supervisor-death and cleanup-zeroing controls. Publish a new pinned
  producer receipt with source/build/artifact correspondence and retained results.
- Sys-init consumes that exact producer, reruns the minimal ordering probe and
  all nine adapter cases, then resumes the service/dependent lifecycle workload.
  Keep kernel producer completion distinct from consumer integration acceptance.

## Userland companion integration follow-ons

Recorded after Aether-userland UL-046 independently consumed the completed
ABI-5 launch broker. [Consumer results](../userland/experiments/native-process/RUNTIME.md)
retain six exact target outcomes. These are queued integration/contract items,
not shared-standard adoption or a change to the existing SI-04 priority.
Canonical shared requirements remain in the pending
[PD proposal](../../Aether-standards/drafts/distribution-v0.2.0/PROCESS-FD.md).

### UP-01 — Inherited file ownership and composable process/file capacity

Accepted architectural direction, 2026-10-04:
[per-process descriptors and shared open-file ownership](../docs/FILE-DESCRIPTORS.md).
**Status: architecture accepted; broader implementation remains queued/partial
in this existing item.** Aether-userland owns the descriptor/musl view; Aether
owns native enforcement; one user-space resource owner holds each shared open
instance. Production owner placement per resource class and exact protocols
remain implementation/affected-owner decisions. This acceptance supplements the
bounded evidence below; it neither closes UP-01 nor reopens completed fixtures.

Priority/dependencies: retain the current implementation order. Build on existing
capabilities, lifecycle and owner-bound I/O; basic descriptor work is not blocked
on all VM features or HO-01's provisional general object-table research.
Coordinate descriptor-to-authorized-backing with the relevant
[VM-02](#vm-02--native-mapping-contract-and-musl-backend) slice, and fork/exec
with UP-02/R1-02. R1-04 loading and later mapping/readiness/descriptor-passing
consumers depend on the applicable enabled semantics.

Additional architectural acceptance for enabled slices:

- Preserve per-descriptor flags, shared open-file position/status and enforceable
  reference rights as distinct state. Independent opens stay independent; dup
  and inherited aliases retain the same open instance without copying offsets.
- Qualify lowest-free duplication, atomic destination replacement, same-FD cases,
  whole-list child admission/rollback and atomic close-on-exec creation as enabled.
  Failed exec preserves old bindings; successful commit consumes marked entries.
- Enforce caller/alias authority below libc. Exercise malformed/foreign/stale
  requests, rights-widening denial, reference/table exhaustion and safe FD reuse.
- Preserve surviving aliases and admitted operations across close/process death;
  prove final backend cleanup and generation-safe in-flight requests. Retain
  explicit ambiguity/cleanup obligations for lost launch/I/O/close replies.
- Keep a bounded indexed table with straightforward synchronization, retained
  references across IPC and no table lock across blocking service calls. Add no
  global POSIX broker just for integer allocation. Production topology, detailed
  synchronization, broader flag/locking/transfer and recovery semantics remain
  scoped future work, with matching native/userland witnesses required.

One-entry parent-requested admission delivered:
[inherited launch](../docs/NATIVE-INHERITED-LAUNCH.md) validates the source and
restricted child binding before effects, rolls back both partial channel
reservation and actual rejected native launch, and passes successful retries.
Seven native cases and both lifetime orders pass on unchanged ABI 9. Independent
userland consumption, broader descriptor lists/selection and production ownership
remain open; this does not close every acceptance item below.

Shared-position/lifetime prerequisite delivered: the
[native shared-file bootstrap](../docs/NATIVE-SHARED-FILES.md) passes both alias
exit orders, scoped-reference denials and real final-backend-close checks across
two generations, with four semantic controls. This uses unchanged ABI 9 and
fixed supervisor-provided aliases. Parent-requested admission, dynamic inheritance
list validation/rollback and independent userland consumption remain open.

Transport prerequisite delivered: [AENMX001 / ABI 9](../docs/NATIVE-CONNECTIONS.md)
adds a separately bounded six-channel profile. Two private file clients and a
backend run through two generations; an incomplete client request does not prevent
the other client completing real file I/O. Six producer cases pass. Shared open-file
ownership, inherited descriptor bootstrap and independent userland adoption remain
open; this is not the inherited-file acceptance described below.

Active, partial: Aether's [mechanism review and executable host oracle](../docs/NATIVE-INHERITANCE-REVIEW.md)
now specify one user-space open-file owner, separate caller-bound descriptor
tables, restricted inheritance, admission rollback and final-close obligations.
Twelve host workloads and three semantic mutation controls cover the candidate
behavior; this is not native inheritance or affected-owner sign-off. ABI 8 has
enough worker slots for two clients plus backend, but the proposed separate-pair
topology needs six channels and an incremental multi-client broker (the finite
transport witness above now supplies those). Agree inherited descriptor
bootstrap/protocol with userland before a new native profile; retain ENOTSUP in
existing profiles. Canonical shared PD review remains pending.

Queued for affected-owner review. Userland owns descriptor/libc policy; Aether
owns native enforcement and its broker conformance fixture; sys-init retains
service lifecycle policy. Consume and reconcile the newer coexistence work before
requesting additional capacity changes; the completed ABI-5 broker only permits
empty inheritance and cannot host both channel pairs within its two-channel cap.

Acceptance for the next agreed experiment:

- Identify where mutable open-file positions and reference counts live when two
  independently loaded clients share a file. Numeric FD/handle copying is not
  native delegation. Specify rights restriction, lifetime and final-close effects.
- Choose explicit process/channel/open-file/descriptor bounds from the actual
  workload, including dash's use of descriptor index 10. Keep larger bounds and
  composed-service readiness distinct from inherited-file semantics.
- Supply owner-produced artifacts and an independent userland witness for shared
  positions, denied rights widening, alias/child exit and final-close cleanup,
  malformed/stale references, admission exhaustion and rollback. If inheritance
  is still unsupported, retain ENOTSUP and do not promote the shell tier.
- Keep broker/file lifecycle separate from ABI-6 init policy until an explicit
  consuming integration proves their composition; retain SI-04's separate order gate.

### UP-02 — Native shell process semantics and first executable workload

Accepted architectural direction, 2026-10-04:
[signals and interruption](../docs/SIGNALS.md).
**Status: architecture accepted; broader signal implementation queued/partial
under this existing item.** Prefer native events for services and a scoped musl
signal runtime. Aether owns native record/pending/delivery and checked restoration;
userland owns POSIX adaptation; process/lifecycle owners enforce authorized targeting.
Production state placement and broader routing remain affected-owner work. This
acceptance supplements bounded signal evidence below without closing UP-02.

Priority/dependencies: preserve current backing/storage/boot-to-shell order. Build
on the existing checked frame, native records, parent provenance and scheduler;
coordinate [UP-03](#up-03--service-io-completion-and-typed-device-control) I/O outcomes
and [UP-04](#up-04--readiness-and-native-wait-many) atomic signal-aware waiting.
Required R1-02 shell/R1-01 terminal slices select their supported set; the whole
future signal design is not a blanket R1 prerequisite. Relevant VM-01 frame/fault
backing is explicit; basic signals do not wait for all VM features or HO-01.

Additional acceptance for enabled signal slices:

- Qualify actual musl/dash disposition/mask agreement, checked entry/restorer/return,
  nesting and sigsetjmp/siglongjmp escape without a permanent active-handler slot.
  Reject malformed frames/mappings/privileged context before unsafe publication;
  preserve supported FP/SIMD, stack/red-zone and mask state and owned failure outcomes.
- Keep process-wide dispositions, per-thread masks and process/thread pending scope
  distinct. Enforce sender/target generation and delegated rights below libc; qualify
  self/parent-linked notification first, then authorized broader targeting/delivery.
  CPU-bound asynchronous delivery needs real preemption-path evidence.
- Coordinate partial request/reply progress, descriptor publication and retained
  buffer/reference cleanup across interruption, handler reentry and nonlocal exits.
  Unknown effects are not false EINTR or safe replay. SA_RESTART must preserve each
  operation's effects/deadline contract; reject unsupported semantics honestly.
- Qualify atomic sigsuspend/pselect/ppoll mask-and-wait with before/during-registration
  events, blocked/ignored occurrences, restoration and teardown. Retain child status
  across coalesced SIGCHLD; ignore/no-child-wait/reap effects need explicit contracts.
- Preserve fork parent state/empty child pending boundary and copied-handler support;
  commit exec disposition/mask/pending transitions without old-image delivery or lost
  new posts. Failed preparation preserves usable state. Distinguish requested signals,
  resolved VM faults, unresolved exceptions, signal death and ordinary exit.
- Defer exact ABI/state placement, process-group job control, general multithreaded/
  cross-core routing, alternate-stack fault handling, real-time queues, advanced flags
  and broad restart/recovery until consumers justify them. Match native and independent
  userland positive/rejection witnesses; documentation acceptance closes no release gate.

#### UL-067 intake: bounded native cat producer (2026-09-06)

User-requested planning intake from Aether-userland. The
[native cat review packet](../userland/docs/TOYBOX-OWNER-HANDOFF.md)
and [CAT-01–08](../userland/docs/TOYBOX-NATIVE-CAT.md#proposed-native-acceptance-matrix)
now define the next bounded consumer request under UP-02. Track this alongside
R1-04; it remains queued after the maintainer-selected SI-05 diversion. R1-03
concurrency resumes next; filesystem-engine work remains required.

- Review an opt-in cat artifact/admission profile with copied bounded startup;
  preserve bytecount, existing carrier/mapped modes and consumer pins.
- Define distinct child input/output/diagnostic roles, complete bootstrap validation,
  rights, generation, capacities and lifetime. UL-059 runner-local outputs remain
  a separate workload; their acceptance does not imply child stderr support.
- Review initial process-mask ownership (userland proposes0077), exact environment
  and memory/TLS grants, without successful unsupported-call stubs.
- Supply independent exact-byte/prefix/no-read-rejection verification and actual
  resource accounting for normal/error/uncertain-close/abnormal-stop outcomes
  across two generations. Include skipped-copy/wrong-prefix/omitted-close controls.
- Return immutable reviewed contract/source/tool/SDK/artifact and raw test/cleanup
  evidence, including failed attempts and explicit CAT case status, for independent
  userland pinning and adoption. Userland owns its libc/stdio/termination adaptation;
  pkg-mgr and sys-init retain package and supervision policy.

The combined Toybox Linux fixture is reference evidence only. This entry records
receipt and required work, not owner design approval, native execution or CAT
acceptance. Native CAT-01–08 remain NOT RUN; no ABI, wire ID or reclaim total is
allocated by this intake. Owner review/implementation and independent consumer
qualification are still required before unblocking native UL-067.

Atomic bootstrap coverage rejects three malformed second bindings without making
any local descriptor usable or sending file traffic. The early-publication control
is caught. Thirty command cases now pass, including a 22-entry malformed complete-launch
corpus in both generations, a bad-version acceptance control, seven parent-live
EOF prefixes and a rejected zero-padding control. EOF is fatal with no recovery
claim. UL-059 now supplies the userland proposal. An opt-in AERUN001 startup carrier
passes three/six-string producer witnesses without widening native Args. A
collected-result variant preserves normal statuses and fault identity. Combined
carrier/forwarding/result witnesses now pass (55 total command cases), including
exact wide argv/environment and corrupt-forwarding rejection. Public parsing
and independent consumer adoption remain open; peer-exit races and general
recovery are separate. These producer witnesses do
not close independent consumer failure testing or general startup recovery.

The reply-failure extension verifies no read-byte publication and no channel
traffic after selected malformed/discarded replies, plus consuming local close.
A disabled-guard control is caught. These rejected workloads establish local
fail-closed behavior, not recovery or remote reclamation after unknown delivery.

The command terminal-kind extension adds normal exit 134 versus actual #UD
(detail 134/kind 2), with inherited-alias cleanup and six reclaims in each case.
Misclassifying that fault as normal exit is rejected. This covers a post-output
fault; arbitrary-phase recovery, POSIX wait/signal mapping and UP-02 remain open.

A [real libc command-I/O candidate](../docs/NATIVE-COMMAND-IO.md) now passes nine
native cases with two standard-file bindings, copied startup, actual output,
short/full writes and rejection/retry. Its runner is a conformance probe; public
CLI mapping, independent userland acceptance, remaining recovery/fault coverage
and package reconstruction are still required. UP-02 remains open.

A separate [bounded file-I/O producer](../docs/NATIVE-FILE-IO.md) now supplies
ordinary 0–16-byte reads, short reads/EOF and parent writes at the broker-owned
shared offset. This addresses the owner extension identified by userland UL-052;
public libc I/O, two-entry standard-FD admission and CR-01 remain open.

Implementation proposal prepared: [CR-01 command runner](../docs/NATIVE-COMMAND-RUNNER.md)
selects a spawn-only runner and userland-owned `bytecount` using actual public libc
I/O, copied argv/environment, two explicit inherited standard-file references,
exact output and terminal results. Current native worker/channel capacity suffices;
the next change is the agreed broker/userland contract. Aether recommends eager-copy
fork followed by transactional exec for the later dash tier, with explicit
signal/vfork/libc gates. This is an Aether proposal, not affected-owner agreement
or command runtime acceptance; no new native ABI is allocated.

Bounded precursor: inherited-launch now supports a connection-owned, one-shot
collection of its child's observed terminal result, including pending/stale/repeat
rejection and independence from file-reference closure. Two designated controls
reject altered results and repeated success. This is not waitpid, process-state
copying or exec; the broader acceptance choices below remain open.
[Contract and evidence](../docs/NATIVE-INHERITED-LAUNCH.md).

Queued after the bounded broker/coexistence handoff, with affected-owner design
review before implementing a new ABI. A successful launch/collect request is not
fork, vfork, in-place exec or waitpid. The
[dash gap review](../userland/docs/NATIVE-DASH-GAPS.md) records the current
consumer requirements and unchecked signal-setup paths.

Public fork precursor (2026-09-10): [source-built candidate](../docs/evidence/public-fork-2026-09-10/README.md)
now passes actual return paths and known-error unwinding with musl repair and
inherited CLOEXEC. Live handlers/atfork callbacks now pass their
[bounded composition](../docs/evidence/public-fork-callbacks-2026-09-10/README.md); [normal-exit waitpid collection](../docs/evidence/public-wait-2026-09-10/README.md)
now passes pending/EFAULT/NULL/repeat cases. Exit134/#UD/SIGTERM now have
[distinct retained wait statuses](../docs/evidence/public-wait-causes-2026-09-10/README.md).
[Reply truncation and ACK ambiguity](../docs/evidence/public-wait-failures-2026-09-10/README.md)
now reject without replay. [Public wait4/wait3 entry points](../docs/evidence/public-wait34-2026-09-10/README.md)
now qualify NULL-rusage collection with explicit accounting rejection. The [native image gate](../docs/evidence/native-exec-gate-2026-09-10/README.md)
now supplies same-identity parked replacement. The [descriptor preparation routine](../docs/evidence/exec-descriptors-2026-09-10/README.md)
now composes with the [native descriptor witness](../docs/evidence/exec-streams-2026-09-10/README.md).
[Incomplete final-close containment](../docs/evidence/exec-close-containment-2026-09-10/README.md)
now passes, as does [bootstrap-stall containment](../docs/evidence/exec-bootstrap-stalls-2026-09-10/README.md).
[EOF/malformed bootstrap cleanup](../docs/evidence/exec-bootstrap-rejection-2026-09-10/README.md)
now passes. [Shared-holder preservation across exec](../docs/evidence/exec-shared-holders-2026-09-10/README.md)
now qualifies the source-first exit order. [Peer-first exit and #UD cleanup](../docs/evidence/exec-peer-terminal-2026-09-11/README.md)
now pass. [Incomplete shared final-close containment](../docs/evidence/exec-shared-close-2026-09-11/README.md)
now passes for normal and faulted peers. The [first libc exec call path](../docs/evidence/libc-exec-stage-2026-09-11/README.md)
now runs with valid stable buffers; [caller-mask guarding and restoration](../docs/evidence/libc-exec-mask-2026-09-11/README.md)
now qualify masks0 and16. The [composed public fork/exec/wait witness](../docs/evidence/libc-fork-exec-wait-2026-09-11/README.md)
now qualifies child replacement and parent collection. [Bounded post-fork dispatch](../docs/evidence/post-fork-dispatch-2026-09-11/README.md)
now permits parent wait while child exec/I/O progresses in two request orders.
[Pre-fork I/O/wait dispatch](../docs/evidence/pre-fork-dispatch-2026-09-11/README.md)
now carries positions into fork/exec/wait using explicit AENMX002 / ABI 17 owner
capacity; old-format limits remain unchanged. [Actual dash's explicit subshell command](../docs/evidence/dash-fork-command-2026-09-11/README.md)
now executes /next and collects its real status with private adapters.
[The native ordinary-command configuration](../docs/evidence/dash-command-config-2026-09-11/README.md)
now selects existing forkshell from source and passes `/next; exit $?`. Next obtain
matching SDK/dash adoption and complete transactional exec under the
[SDK staging selection](../docs/NATIVE-SHELL-STARTUP.md#sdk-process-integration-selection--2026-09-10).
Native vfork/configuration and independent SDK/dash acceptance remain explicit gates;
OpenZFS is not a prerequisite for the process candidate. This is producer selection,
not affected-owner sign-off or an installed SDK API.

Acceptance planning:

- Select copied-process-state/fork-vfork semantics or explicitly label a spawn-only
  intermediate tier. Define executable authority, argv/env, parent-child identity,
  descriptor inheritance and failed-exec state before calling it a dash port.
- Resolve signal/mask/child-notification and interrupted wait/close behavior with
  userland's musl audit. Do not substitute successful stubs for unsupported calls.
- Publish exact startup/external-helper/wait and failure-cleanup workloads, followed
  by the inherited-FD, redirection/pipeline/substitution cases required for the
  native script tier. Keep TTY jobs and packaged/authenticated release acceptance
  in their separately owned follow-ons.


### UP-03 — Service I/O completion and typed device control

**Status: architecture accepted, 2026-10-04; general implementation queued/partial.**
The maintainer accepted [capability-authorized service I/O](../docs/SERVICE-IO.md)
with a synchronous musl facade, owner-held file/stream/device state, explicit
acceptance/completion/durability and typed native device commands. Aether-userland
owns POSIX adaptation; Aether owns native enforcement and fixtures; production
resource-service placement and exact interfaces require affected-owner contracts.
Sys-init retains supervision/recovery policy; pkg-mgr retains artifact/install policy.
This local decision changes no shared standards release or companion acceptance.

Priority/dependencies: use the existing current implementation order and native
capability/IPC/lifecycle foundations. Coordinate UP-01 reference/shared-position
ownership and UP-02 shell consumers. Required copied-I/O/control slices support
R1-01 console, R1-02 shell, R1-03 filesystem and R1-04 runner/loading; the whole
future I/O design is not a prerequisite for each bounded milestone. Basic copied
I/O is not blocked by full VM-01/VM-02 or provisional HO-01. Bulk buffers depend
on the needed [VM-01](#vm-01--vm-objects-address-space-mappings-and-pmap) slice;
POSIX mapping consumers coordinate with [VM-02](#vm-02--native-mapping-contract-and-musl-backend).
General Xorg/Mesa/GPU consumers remain later than R1.

Acceptance and sequence for enabled slices:

- First qualify musl file/pipe read/write with actual counts, short/EOF/nonblocking
  and interrupted-progress behavior, authorized references, admission bounds,
  owner-ordered shared positions and safe close/process-death cleanup. Native
  explicit-offset operations do not mutate the shared cursor; enabled append/
  PIPE_BUF/vector semantics must survive transport framing and concurrency.
- Distinguish admitted, completed and durable results. Retain bounded outcomes
  and references before effects; reject stale/foreign/rights-widening requests
  and capacity exhaustion. Exercise late replies, partial frames and unrelated
  client progress. Unknown effects/positions prohibit unsafe replay or guessed
  continuation; transparent recovery is not required for the first slice.
- Qualify blocking/wakeup and cancellation-versus-completion ordering. Keep
  admitted work bound to its original generation across FD reuse and closure;
  prove buffer access ends before reuse. Device timeout/cancel/close requires
  separate quiescence accounting, not an inferred successful cleanup.
- Enable a required typed control operation, such as terminal attributes, with
  versioned bounded schemas, independent owner authority checks, malformed/
  unknown-command rejection and honest unsupported errors. No unrestricted
  ioctl tunnel, fabricated success or automatic Linux DRM compatibility claim.
- Add authorized VM-object bulk transport only for measured consumer needs,
  enforcing offset/length/direction and actual grant scope, stable control
  metadata, mutable-alias rules and backing/mapping/DMA lifetime. Preserve all
  existing profile limits until an explicit producer/consumer-qualified change.
- Defer exact wire ABI, service placement, quotas, general recovery, vector/flag
  expansions, registration, batching, out-of-order execution and submission/
  completion rings. Readiness/waitsets and descriptor passing are separate
  contracts. Match native and independent userland witnesses before enabling
  each slice; documentation acceptance closes no runtime/release gate.

Existing [streams](../docs/NATIVE-IO.md), [file I/O](../docs/NATIVE-FILE-IO.md),
[command adapters](../docs/NATIVE-COMMAND-IO.md) and
[block I/O](../docs/NATIVE-BLOCK.md) remain evidence for their bounded profiles.
Consume that progress rather than reopen completed fixtures or promote it to
general concurrent I/O, POSIX, persistent durability or DMA-isolation acceptance.

### UP-04 — Readiness and native wait-many

**Status: architecture accepted, 2026-10-04; general implementation queued/partial.**
The maintainer accepted [capability-based readiness and waiting](../docs/READINESS-WAITS.md):
level-triggered observations, resource-owner semantics, native park/wakeup and
musl poll/select adaptation. Begin with bounded wait-many scanning; no global
event service or mandatory kernel waitset object is selected. Aether owns native
enforcement, Aether-userland owns adapters, and sys-init retains startup-readiness
and supervision policy. Exact ABI/placement and wider concurrency remain open.

Priority/dependencies: preserve current backing/storage/boot-to-shell order. Reuse
existing endpoint waits, capability/IPC/scheduler and UP-01/UP-03 references and
I/O. Coordinate [SI-01](#si-01--native-wait-and-service-deadline-contract) deadline/
clock work and [SI-02](#si-02--review-channel-transfer-for-delegated-readiness)
service-readiness mapping; do not duplicate or reopen their bounded acceptance.
Enable the required R1 consumer slices, then local sockets and later Xorg/Mesa.
The whole general wait design is not a blanket R1 or VM prerequisite.

Acceptance for enabled slices:

- Select a real multi-source consumer; define bounded list/source/interest rights,
  owner subscriptions and musl event/result/error/count semantics. Preserve
  readable/writable/peer-close versus operation-completed/lifecycle distinctions.
- Qualify level readiness, buffered drain, event-before-registration and event-
  during-registration with atomic comparison/park and wake/rescan. Service-owned
  observation/subscription must bridge to kernel waiting without lost notifications.
- Enforce holder/generation identity, retain watched references, and qualify stale/
  foreign denial, FD/source reuse, cancellation/close/teardown and delayed delivery.
  Coalescing cannot discard the only operation outcome; bounds/overflow are explicit.
- Qualify monotonic deadlines and tie ordering when exposed; pselect/ppoll wait
  atomically with their temporary signal masks under the scoped signal contract.
  Old interrupt-time clocks and BSP-only waits do not prove general time or SMP.
- Add multiple-waiter/fairness and authenticated cross-core ordering only with
  matching native/consumer evidence. Defer persistent queues, edge triggering,
  specialized indexes, exact ABI/quotas and broader recovery until justified.

Existing [ABI24 channel waiting](../docs/evidence/session-channel-wait-2026-10-03/README.md)
and [init observations](../docs/NATIVE-INIT.md) keep their profile limits. Architecture
acceptance is not general waitset implementation, companion sign-off or R1 closure.

### UP-05 — Unix sockets and authorized descriptor passing

**Status: architecture accepted, 2026-10-04; general implementation queued.**
The maintainer accepted [local sockets over native IPC/resource services](../docs/UNIX-SOCKETS.md)
and SCM_RIGHTS as enforced reference delegation to the same open instance.
Musl owns POSIX adaptation; Aether and resource owners enforce reference/connection
authority. Exact production service placement, native ABI and supported resource
classes remain scoped affected-owner work; no universal POSIX broker is chosen.

Priority/dependencies: keep current implementation order. Build connected stream
pairs for a real consumer using required UP-01/UP-03 slices; readiness uses UP-04
as needed. Then qualify a real file/buffer passing consumer and named listeners
when needed. Named sockets depend on authorized namespace/filesystem lookup;
VM-object passing uses the relevant VM-01 slice and mapped POSIX consumers VM-02.
Basic pairs do not wait for all VM features or arbitrary transfer/HO-01 research.
SI-02 launch delegation remains distinct. Concrete R1 needs select their subset;
general local communication/Xorg/Mesa work is not a blanket release prerequisite.

Acceptance for enabled slices:

- Qualify connected-stream ordering, short counts, queue/backlog bounds,
  backpressure, half-close, buffered drain, EOF/errors, readiness and peer death.
  Add named lookup/bind/listen/connect and other socket types only with consumers.
- Enforce delegation permission, holder/generation, resource type and non-widening
  rights below musl. Preserve shared open-instance position/status and sender FDs;
  new recipient FDs reference the same instance, not a copied token or reopened path.
- Specify sender/queue/receiver references, reservation/rollback, recipient native/
  FD capacity and delivery commit/acknowledgment. Sender close after admission
  preserves queued access; discard/receiver death performs owned cleanup.
- Qualify attachment-to-stream association, short-send retries without duplicate
  delegation, ancillary truncation/discard, exhaustion, received-FD flags and
  enabled atomic close-on-exec receipt. Unknown delivery cannot justify blind replay.
- Restrict supported attachment types until their enforcement/lifetime contract
  is qualified. Endpoint passing needs unreachable-cycle reclamation or an
  enforced cycle-excluding restriction; quotas alone do not establish cleanup.
- Require matching native and independent userland semantic witnesses. Defer exact
  ABI/topology/quotas, credential modes, global namespaces, general recovery,
  cross-core transfer and unrestricted endpoint passing. Existing launch/channel
  evidence does not establish arbitrary SCM_RIGHTS or graphics/DRM compatibility.

### UP-06 — Identity and permissions over capabilities

**Status: architecture accepted, 2026-10-04; general implementation queued/partial.**
The maintainer accepted [identity and service-enforced permissions](../docs/IDENTITY-PERMISSIONS.md).
Capabilities bound native access; authenticated principal policy and POSIX credentials
remain distinct. Existing validated UID/GID fixtures stay advisory and retain their
exact qualification. Aether owns enforcing mechanisms, userland owns musl/runtime
adaptation, resource owners own permission/namespace policy. Production credential
issuer/service placement remains affected-owner work; no new global broker is chosen.

Priority/dependencies: preserve current backing/storage/boot-to-shell order. Reuse
UP-02 startup/process identity and UP-01/UP-03 reference/resource contracts. Select
R1-02 query/secure-environment, R1-03 mode/creation-mask/path and R1-04 loader slices
with the actual consumers. UP-05 uses trusted peer/namespace identity when needed.
VM-01/VM-02 apply to relevant device/mapping consumers, not every identity query.
Authenticated multiuser operation, login and setuid execution are not blanket R1
prerequisites. No native ABI, quota, rights bit or shared profile is allocated here.

Acceptance for enabled slices:

- Preserve admitted record provenance/lifetime and accurate real/effective UID/GID
  queries. Reject malformed/stale records and unsupported setters/groups; caller
  numbers, environment values, roles and UID zero cannot confer authority. Advisory
  metadata must never satisfy an authenticated-principal requirement.
- Enforce namespace scope and rights ceilings below libc alongside supported owner/
  group/mode policy. Qualify real create/open/metadata/delete/rename behavior and
  persisted ownership, requested mode/umask and inherited process mask. File write
  does not imply ownership administration; names/special bits do not mint grants.
- Qualify directory-relative/root/CWD traversal, symlinks, parent steps and concurrent
  namespace mutation for the declared scope. Check lookup/acquisition at the owner;
  access/open credential semantics remain distinct and prechecks cannot authorize
  later effects. Unsupported options fail rather than guess successful permission.
- Preserve existing-reference access across ordinary chmod and authorized passing;
  identity changes cannot falsely claim descriptor/grant/mapping revocation. Explicit
  authority dropping or strong revocation needs its own retained-work/cleanup contract.
- Review actual musl/dash/loader secure-execution and ENV behavior with userland before
  enabling elevated launch. Future authenticated transitions require trusted caller-
  bound records, process-wide commit, fork/exec/failure behavior and stale connection
  rejection for new requests under the claimed drop semantics.
- Require matching native/resource-owner and independent userland positive/semantic
  denial witnesses. Defer exact issuer/ABI/topology, login/accounts, broad group/saved-ID
  transitions, setuid execution, ACLs, additional mandatory policy, ID namespaces and
  general revocation/recovery until justified. Acceptance closes no runtime/release gate.

### UP-07 — Native TTY sessions and seat boundaries

**Status: architecture accepted, 2026-10-04; general implementation queued/partial.**
The maintainer accepted [TTY/session/seat separation](../docs/TTY-SEATS.md): a native
Rust user-space TTY owner, musl typed terminal adaptation and capability-enforced
process/session/device relationships. Ncurses/terminfo is the leading application
candidate; libtsm is the later local-emulation candidate. No package version, native
adoption, new ABI, quota or production service topology is selected. Userland owns
its assigned adapters/package acceptance; general service ownership is affected-owner
work. Sys-init retains supervision/session-admission policy and pkg-mgr artifacts.

Priority/dependencies: preserve current backing/storage/boot-to-shell order. Required
R1-01 serial modes/transport, R1-02 shell control and R1-06 assembly use UP-01 refs,
UP-03 I/O/control, UP-04 waits and UP-02 process/signals. UP-06 covers identity/scoped
namespace and SI-01 enabled timed reads. Coordinate existing userland
[UL-008/UL-009](../userland/.planning/BACKLOG.md) without changing their
status or pins. Sequence serial TTY, ncurses/terminfo consumers, session/job control,
PTYs, libtsm local-console evaluation and graphical seat compatibility. Whole future
Zsh/PTY/graphics/seat completion is not a blanket R1 prerequisite.

Acceptance for enabled slices:

- Qualify canonical/raw/echo, erase/kill, line/queue bounds, overflow/backpressure,
  short I/O, separate stream/control roles and EOF versus empty-open/disconnect.
  VMIN/VTIME/nonblocking/readiness must match the declared profile and real clocks
  where needed. Accepted bytes are distinct from transmission/rendering/completion.
- Enforce input/output/mode/foreground/recovery rights below musl; unsupported mode
  and control requests reject without fabricated success. Define mode revision,
  drain/flush effects and normal/handled-signal restoration. Stale snapshots cannot
  overwrite a successor; owner death needs authorized recovery without old-input replay.
- Qualify session/groups/controlling terminal and trusted foreground selection before
  Ctrl-C/Z, background reads/writes or fg/bg claims. Actual stop/continue, PID/group
  reuse and fork/exec relationships follow UP-02. A prompt is not TTY/job-control/login
  acceptance; /dev/tty lookup remains scoped to the authorized caller relationship.
- Qualify master/slave pair authority, buffers, alias lifetime, resize/hangup and
  cleanup when PTYs are enabled. Ncurses/terminfo needs pinned musl build/data and
  real consumers; TERM describes the actual terminal. Keep GNU stty evaluation first
  with BusyBox comparison; a saved stty string is not complete generation-bound state.
- Require native owner and independent userland positive/semantic denial witnesses;
  test modes, stale/foreign control, exhaustion, partial progress, disconnect and
  teardown. Follow pinned Experience/TX requirements, plain/narrow/UTF-8/paste tests
  for claimed modes. Host PTYs/serial byte witnesses do not establish native TTY tiers.
- Defer exact ABI/topology, broad PTYs/Zsh modes and recovery until consumers need
  them. Libtsm/FFI/rendering and libseat backends require separate evaluation. Graphical
  seat switching needs effective device/input/mapping/command cleanup before reassignment;
  notification alone cannot revoke access. No package, standards or release gate closes.

### UP-08 — Device services and scoped /dev

**Status: architecture accepted, 2026-10-04; general implementation queued/partial.**
The maintainer accepted [native device services](../docs/DEVICE-SERVICES.md) with
typed, capability-routed access and a scoped POSIX /dev view. Separate hardware
discovery/resource assignment, authorized provider access and compatibility names.
Choose explicit bindings and a small native Rust namespace adapter first; no
external package, general registry, new native ABI/quota or service topology is
selected. Aether owns enforcing mechanisms/fixtures; userland owns assigned musl
adapters/consumer work. General device/namespace service ownership is affected-owner
work; sys-init retains supervision and pkg-mgr installation without implicit activation.

Priority/dependencies: preserve current physical-backing/storage/boot-to-shell order.
Required R1-01/R1-02/R1-03/R1-06 console/runtime/storage/startup bindings use UP-01
references, UP-03 I/O/control, UP-06 namespace/policy and UP-07 terminal relationships.
Use UP-04 for needed waits and later snapshot/watch; VM-01/VM-02 apply to actual
device-mapping consumers, not every pseudo-device open. Explicit inherited/boot
bindings may precede the full filesystem namespace. Sequence minimal shell/TTY
view, qualified randomness/bounded block providers, device-backed mappings and
specific display/input access, then dynamic discovery and seats. Whole hotplug,
USB/general driver frameworks, sysfs/udev compatibility and graphics do not block R1.

Acceptance for enabled slices:

- Enforce authenticated provider publication, caller namespace/binding, generation,
  rights ceilings, policy and capacity below musl. Metadata enumeration, connecting,
  I/O, mapping and administration remain distinct; names, UID zero, mknod/device
  numbers or package bytes cannot grant access. Lookup/acquisition must account for
  concurrent removal/replacement and actual traversal scope.
- Qualify supported null/zero/TTY/console/random/device entries against real consumers,
  descriptor aliases and exact I/O/error semantics. /dev/tty resolves the authorized
  caller relationship. Randomness needs readiness/failure/quality trust declarations;
  current entropy receipts retain scope and cannot qualify a whole namespace.
- Qualify bounded block-region and device-backed VM mappings as their consumers need
  them; no ordinary physical-memory namespace or unrestricted ioctl/mapping tunnel.
  Xorg/Mesa/seat integration requires actual commands, synchronization and cleanup,
  not inferred Linux DRM/NVIDIA support.
- Distinguish physical identity, provider generation and open instance. Reject stale/
  foreign references without retargeting old FDs on name reuse. Retain actual partial/
  unknown outcomes; no blind effect replay. Unpublish/close/revoke/stop/detach/DMA
  quiescence differ; retained backing cannot be reused under unknown device access.
- Require native owner and independent consumer positive/semantic denial witnesses
  for supported opens, malformed/stale/foreign operations, alias cleanup, bounded
  exhaustion and removal/restart races. Bound sessions, records and pending work.
  Physical DMA isolation/reset/recovery require separate qualification.
- Defer exact ABI/layout/ownership/bounds, general discovery/watch and hotplug until
  needed. Later snapshot/revision/watch must avoid lost changes; discovered/published
  is distinct from ready. No native/companion/shared-standard/release gate closes.

## Standards process and conformance gates

The approved-content [development workflow](../docs/DEVELOPMENT.md) applies to new
work. `zig build test` includes the inventory/review gate; affected target and
consumer checks remain mandatory by risk. The [standards assessment](../docs/STANDARDS.md#updated-drafts-and-local-process)
records migration and release coverage gaps. Manuals/offline lookup, independent
reviews, unsafe/style baseline review, complete resource/dependency inventory,
extended test infrastructure and assembled candidate gates must be resolved in
scope before full conformance/release claims. Approved content is not a published
release pin or runtime acceptance. Existing native milestones retain their bounded
evidence; these gates do not allocate new kernel interfaces.

Console/process integration evidence: [AENMX003 / ABI18](../docs/evidence/console-process-profile-2026-09-11/README.md)
now qualifies UART handoff and third-image slot reuse in the three-image layout.
Actual dash stdio routing and interactive input remain R1 acceptance work; this
transport result does not close the shell milestone.

[Pending-read evidence](../docs/evidence/stream-pending-2026-09-11/README.md)
qualifies child progress while a parent read waits on backend EAGAIN, shared
positions, exact cleanup and false-EOF/retry rejection controls. This is the
private deterministic stream fixture. Apply it to actual dash/UART next, including
pre-fork reads and one console-grant lifetime; interactive acceptance remains open.

[Actual serial dash](../docs/evidence/dash-console-2026-09-11/README.md) now qualifies
two interactive command sessions, real child stdin and wait status, one UART
backend lifetime and denied slot reuse. The native input selection uses upstream
one-byte fallback; it does not implement pipes or TTY semantics. Continue with
consumer review and general session/command lifecycle, then sys-init/persistent
loader integration. R1 is not assembled by this harness result.

[Shell continuation](../docs/evidence/shell-resume-2026-09-11/README.md) qualifies
a fresh prompt after child completion, a separately entered status/exit command
and parent exit0/7 with cleanup. The repeated-command result below extends this to three external children
in one shell. Keep terminal observation, wait acknowledgment, stale-route
rejection and existing generation/channel quotas; R1 assembly remains separate.

[Repeated commands](../docs/evidence/shell-repeat-2026-09-11/README.md) now qualify
three external children in one parent lifetime, collected-child slot reuse,
independent parent/child identity and retained console descriptions. Exact
terminal-plus-wait acknowledgment precedes reclaim; unchanged quotas still bound
the fixture. The descriptor-redirection checkpoint below extends this result;
consumer and sys-init/persistent-loader integration remain separate.

[Builtin descriptor redirection](../docs/evidence/shell-redirect-2026-09-11/README.md)
qualifies stdout-to-stderr redirection/restoration followed by repeated fork/exec.
Canonical absent FD entries preserve strict wire validation without changing the
shared facade. The [selected pipe contract](../docs/NATIVE-SHELL-STARTUP.md#bounded-pipe-and-command-substitution-contract--2026-09-11)
now defines one-child substitution within the current participant budget. Next
implement owner-local endpoints, terminal-driven holder retirement and the named
EOF/backpressure/failure tests; then execute actual dash substitution. Concurrent
pipeline participants and external/file redirection still need review. R1 assembly
remains open.

The [pipe owner core](../docs/evidence/pipe-owner-core-2026-09-11/README.md) now has
host-tested FIFO/lifetime semantics and a no_std x86_64 compile check. Native
integration remains open: connect authenticated callers and observed terminals,
add the private adapter/fork-plan v2, then run real endpoint and substitution cases.
Host tests do not replace that target evidence or change the R1 acceptance gates.

[Native pipe transfer](../docs/evidence/pipe-native-2026-09-11/README.md) now proves
actual copied-process FIFO/backpressure, descriptor aliases and terminal-driven EOF
before wait collection across two complete lifetimes. Continue with abnormal and
partial-reply cleanup and SIGPIPE, then actual dash substitution with repeated
pipe/child generations and ordinary stdio forwarding. This is a private producer
probe; installed SDK acceptance and the filesystem/package/sys-init R1 assembly
remain open.

[Interrupted pipe creation cleanup](../docs/evidence/pipe-reply-cleanup-2026-09-11/README.md)
now covers reply EOF at zero/one/31 bytes, unpublished FDs, mask preservation,
no retry, confirmed-terminal holder release and three real replacement lifetimes.
Continue with abnormal in-flight child cleanup and SIGPIPE, then actual dash
substitution. Silent stalls, poisoned-client reuse and native copy rollback are
not covered by this producer result. R1 assembly and consumer adoption remain open.

[Partial pipe request at child fault](../docs/evidence/pipe-fault-cleanup-2026-09-11/README.md)
now preserves committed bytes through EOF before wait, reports real SIGILL, and
clears a partial frame only after confirmed fault/route drain. Two complete
lifetimes reclaim six real tasks; retained-frame and false-status controls reject.
Next qualify fully pending write stop and SIGPIPE, then actual dash substitution.
Other interruption schedules, native copy rollback and R1 assembly remain open.

[Stopping a pending pipe writer](../docs/evidence/pipe-stop-cleanup-2026-09-11/README.md)
now preserves committed bytes through EOF before collection, drops a complete
unapplied write only after actual stop observation, and finishes six real reclaims.
Skipped-stop and retained-frame controls reject. Next qualify SIGPIPE, then actual
dash substitution; native copy rollback, other interruption schedules, same-client
pipe reuse and R1 assembly remain open.

[Native SIGPIPE](../docs/evidence/pipe-sigpipe-2026-09-11/README.md) now covers
ignored/handled/blocked/coalesced delivery, pending-ignore discard, errno/mask
preservation and actual default termination directly and on unblock. Missing
post/poll controls reject. Next integrate pipes into actual dash substitution,
with ordinary stdio forwarding and repeated generations. Installed SDK/public
pipe, general interruption semantics, copy rollback and R1 assembly remain open.

[Actual dash substitution](../docs/evidence/dash-pipe-2026-09-11/README.md) now passes
pipe/fork/dup2/EOF/wait3 and independent stdout readback in two complete lifetimes.
Invalid header and false wait status reject with zero reclaims. Next prove repeated
pipe/child generations in one shell parent, then adopt serial input. Installed SDK,
live-pipe exec, broad failure recovery and R1 assembly remain open.

[Repeated dash substitutions](../docs/evidence/dash-pipe-repeat-2026-09-11/README.md)
now preserve one parent across two pipe/child generations, with EOF/wait ACK before
retirement/reclaim and exact backend readback. A fresh builtin-only shell verifies
stdio/backend reuse; stale token and pipe receipt controls reject. Next integrate
serial substitution, then complete SDK/consumer acceptance and R1 assembly.

[Serial pipe substitution](../docs/evidence/dash-pipe-serial-2026-09-13/README.md)
now drives two substitutions at returned prompts and a fresh shell through the
scoped UART backend. EAGAIN handling, stream offsets, exact output, grant denial
and six reclaims pass; changed input and stale copy token reject. Next combine
serial exec and substitution with an explicit descriptor/exec contract before
SDK/consumer handoff. Filesystem/package/sys-init R1 assembly remains open.


The2026-10-19 fixed mixed service gate now passes its7-image/12-guest native matrix
and720-method broad checkpoint. Bounded namespace authority/alias coherence and
typed0/16 success-only retirement have matching producer evidence. R1 stays open:
next obtain the operational executable/ABI/provisioning/idle/larger-transport/
readiness/shutdown contract and compose it with sys-init/runner/packages/Zsh.
See STATE and the remaining operational handoff in OPENZFS-FEASIBILITY. No
implicit quota/profile expansion, independent acceptance or boot ISO completion.

R1-03/R1-06 composition,2026-10-20: maintainer approved the separate fixed
AENFS002/owner28 storage+SESSION profile (7 domains/35MiB admitted backing,
12 channel records). Implementation/host preparation now preserve five small
process roles alongside the real Rust/OpenZFS owner and enforce role restrictions
at native copy/exec/block/channel operations. Existing profiles and released pins
remain unchanged. Initial native9-mutation96-request plus process exec/wait and
fresh recovery qualification passes (TXG796/806); it does not close the operational
service, actual sys-init consumer, Zsh payload fits, persistent runner/package
metadata/promotion or R1 acceptance. See STATE and NATIVE-C for current results.


R1-03/R1-06 follow-on,2026-10-20: approved separate AENFS003/owner29 raises only
owner code to16384, preserves old8192 profile and all other limits. Four-page
conformance/native persistence796/806 passes with scoped1808/4088 stack inspection;
actual old sys-init15120 bytes now fits its immutable linker unchanged. Await
sys-init-owned ABI29 role/provisioning/lifecycle adaptation and fresh code/stack/
consumer evidence. This clears the size blocker, not sys-init/Zsh/ISO acceptance.
