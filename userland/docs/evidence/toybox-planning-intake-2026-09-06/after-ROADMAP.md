# Roadmap: x86_64 swarm POC

Updated: 2026-09-06. Current progress is recorded only in [STATE](STATE.md).

The first public release now ends at R1: boot to a serial shell with runner,
persistent filesystem and native package management. M1–M4 are foundations; M5–M6
remain optional later graphics work. This supersedes the earlier M4-only public
release boundary. Each milestone must produce executable evidence.

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
selects local confirmed-result mapping first and requests no new kernel API yet.

Added 2026-09-05 at the maintainer's request. These were ordered companion follow-ons,
not blanket R1 prerequisites beyond the actual composed workload or a replacement for the current file-service
work. Progress is recorded only in [STATE](STATE.md). Motivation and required
consumer inputs: [sys-init integration gates](../../sys-init/docs/INTEGRATION-GATES.md).
Sys-init owns service/readiness/recovery policy; Aether owns the minimal enforcing
mechanisms. Shared normative changes belong in Aether-standards, with explicit
version/pin adoption. Preserve existing native profiles and their smoke markers.

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
R1-04; it does not replace the current R1-03 filesystem-engine work.

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
