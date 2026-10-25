# Roadmap: x86_64 swarm POC

Updated: 2026-09-06. Current progress is recorded only in [STATE](STATE.md).

The first public release now ends at R1: boot to a serial shell with runner,
persistent filesystem and native package management. M1–M4 are foundations; M5–M6
remain optional later graphics work. This supersedes the earlier M4-only public
release boundary. Each milestone must produce executable evidence.

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
  [matched phase-one handoff](../docs/evidence/dash-phase-one-native-2026-09-13/README.md) now passes both native suites; [consumer descriptor closure](../docs/evidence/dash-consumer-closure-2026-09-13/README.md) now passes. Next define scoped /dev/null inheritance/exec for unchanged background wait, then continue failed-exec and writable descriptor workloads; independent replay remains open. General
  pipelines and independent SDK acceptance remain separate. Keep capability enforcement and exact-stop cleanup local and
  visible; extract a coherent responsibility only when the change needs it.
- **During the next affected harness change:** launch_smoke.py combines build,
  case selection and profile-specific oracles. Reuse its existing evidence and
  test-group records; clarify touched case/oracle ownership without introducing
  another harness/status system or weakening negative controls. Broad extraction
  and retirement of still-consumed fixtures are deferred.

## Current implementation order — 2026-09-07

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

Independent consumer pin/build/acceptance remains required for each handoff.
These prerequisites do not complete filesystem/package release requirements.

### Prior implementation order — 2026-09-06

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

## R1 — First release: persistent boot-to-shell system

Maintainer direction, 2026-09-06: boot into an interactive serial console is
acceptable; shell, runner, filesystem and package management are mandatory.
Native NVIDIA, desktop and network package fetching are not prerequisites.

| Workstream | Required outcome and owner boundary |
| --- | --- |
| R1-01 Console and terminal | Real bidirectional serial input/output with explicit grants, separate stdin/stdout/stderr, EOF/error behavior and the terminal operations the selected shell needs. Kernel owns bounded hardware access; userland owns terminal/line policy. No fabricated successful ioctl or signal setup. |
| R1-02 Shell/process runtime | Userland's selected shell (current dash candidate) runs interactively and executes external programs. Implement the process identity, launch/exec/wait, descriptor flags/duplication, pipes/redirection and signal behavior its actual code and package scripts require. Define any deliberate shell adaptation with userland; a fixed builtin prompt is not completion. |
| R1-03 Persistent storage and filesystem | Capability-scoped block read/write/flush on a disposable QEMU disk, then a Rust filesystem service with real paths/directories, metadata, create/write/truncate/rename/remove and persistence. Reuse an established engine; OpenZFS remains the evaluation direction, not a proven port. Engine and first-release snapshot/rollback scope need an explicit decision. RAM files are an intermediate step. |
| R1-04 Runner and executable loading | Integrate the userland public parser, copied startup, explicit I/O, observed results and failure handling. Run approved executables read from the filesystem, not only the current three fixed boot-image grants. Package names/paths never confer executable authority by themselves. |
| R1-05 Native package lifecycle | Run pkg-mgr on Aether to install a real package from local media/bundle, list/verify it, execute its program and remove it within an explicit target root. Package records and bytes persist; failure/interruption cannot report false success or silently damage unrelated files. Define supported update/recovery limits with pkg-mgr. Host-built artifacts alone do not close this. |
| R1-06 Boot/service assembly | sys-init starts storage/filesystem, terminal and process services in a supported dependency order, then launches the shell with scoped grants. Boot the same assembled image/storage layout tested by users. Failures surface without inventing general supervisor recovery. |
| R1-07 Candidate qualification | Frozen source/image identity, matching independent build, scoped reliability/interruption tests, third-party notices, security intake, user boot/package/recovery instructions and applicable release gates on the complete system. Publication remains separate. |

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

## Sys-init companion contract backlog

Status reconciled 2026-09-06: SI-01–03 have independent bounded ABI-6 acceptance
under [sys-init decision 0017](../../sys-init/docs/decisions/0017-native-init-consumer.md).
[SI-04 consumer refresh](../../sys-init/docs/evidence/native-slot-reuse-consumer-2026-09-05/README.md)
also passed. The remaining requirements below describe broader scope, not a queue
to reimplement accepted primitives. Sys-init's [decision 0042](../../sys-init/docs/decisions/0042-reconciliation-evidence-review.md)
selected local confirmed-result mapping first. The later sys-init decision 0088
now requests the separate init-compatible fixture capacity decision tracked in SI-05;
this does not reopen the already accepted SI-01–04 primitive work.

Added 2026-09-05 at the maintainer's request. These were ordered companion follow-ons,
not blanket R1 prerequisites beyond the actual composed workload or a replacement for the current file-service
work. Progress is recorded only in [STATE](STATE.md). Motivation and required
consumer inputs: [sys-init integration gates](../../sys-init/docs/INTEGRATION-GATES.md).
Sys-init owns service/readiness/recovery policy; Aether owns the minimal enforcing
mechanisms. Shared normative changes belong in Aether-standards, with explicit
version/pin adoption. Preserve existing native profiles and their smoke markers.

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
See the [capacity handoff](../../sys-init/docs/INIT-CAPACITY-HANDOFF.md),
[retained failed builds](../../sys-init/docs/evidence/native-terminal-capacity-2026-09-07/README.md)
and [consumer qualification](../../sys-init/.planning/backlog/captured/BG-061--qualify-expanded-init-capacity.md).

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
operation dispatch. See the [consumer findings](../../sys-init/docs/research/NATIVE-CONFLICT-GUARD-LAYOUT.md)
and [capacity request](../../sys-init/docs/research/NATIVE-INIT-IMAGE-CAPACITY-REQUEST.md).

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
[Consumer evidence](../../sys-init/docs/evidence/native-slot-reuse-consumer-2026-09-05/README.md)
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
[consumer checkpoint and handoff](../../sys-init/docs/NATIVE-ADAPTER.md#kernel-order-gate-and-handoff)
retain a minimal no-wait ABI-6 probe: launch slot 0, observe exit 17, close reader,
reclaim; do the same for slot 1; then reuse slot 0. It failed against producer
summary SHA256 `86d52e49898fcb859fcb7ffd7af46310152381590753f72e6ba690f17a14c9e4`
with kernel vector 14, CS=8, error=3, RIP `ffffffff80030af0`, after both terminal
records. LLVM 21 resolves the faulting instruction to `memset`; the caller/root
cause is not established. Reprotecting reclaimed backing via `aliases(owner,
false)` during another slot's load is an investigation lead, not a confirmed fix.
This is a frozen-producer finding, not a claim that an untested current checkout
still has the bug.

Evidence: [failed report](../../sys-init/docs/evidence/native-adapter-2026-09-05/order-probe/results.json),
[serial log](../../sys-init/docs/evidence/native-adapter-2026-09-05/order-probe/cases/adapter-edges/native-serial.log),
[minimal source](../../sys-init/docs/evidence/native-adapter-2026-09-05/order-probe/source/prototypes/native-supervisor/init.rs).
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
ABI-5 launch broker. [Consumer results](../../Aether-userland/experiments/native-process/RUNTIME.md)
retain six exact target outcomes. These are queued integration/contract items,
not shared-standard adoption or a change to the existing SI-04 priority.
Canonical shared requirements remain in the pending
[PD proposal](../../Aether-standards/drafts/distribution-v0.2.0/PROCESS-FD.md).

### UP-01 — Inherited file ownership and composable process/file capacity

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

#### UL-067 intake: bounded native cat producer (2026-09-06)

User-requested planning intake from Aether-userland. The
[native cat review packet](../../Aether-userland/docs/TOYBOX-OWNER-HANDOFF.md)
and [CAT-01–08](../../Aether-userland/docs/TOYBOX-NATIVE-CAT.md#proposed-native-acceptance-matrix)
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
[dash gap review](../../Aether-userland/docs/NATIVE-DASH-GAPS.md) records the current
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
