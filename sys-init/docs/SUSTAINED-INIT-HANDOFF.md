# Sustained init: next consumer handoff

**Current disposition:** [SI-07 and remaining v1 work](SI07-DISPOSITION.md)
supersedes earlier pending-replay and next-step notes below. Independent userland
producer/request-loop replays verify; the bounded useful-cycle core is accepted.
Full protocol acceptance and assembled product work remain. Next is a maintained
offline recipe for the existing ABI22 baseline.


**Failure checkpoint 2026-10-03:** [four native cases](evidence/si07-errors-2026-10-03/README.md)
qualify complete split replies, lost write-reply rejection and cleanup Unknown/no
replay. Maintained runtime is unchanged. Next consolidate SI-07 acceptance and
remaining v1 integration; earlier next-step entries below are historical.


**Request-loop checkpoint 2026-10-03:** [seven consumer cases](evidence/si07-loop-2026-10-03/README.md)
pass with halt before the first command or at any completed-cycle boundary.
The five-cycle cutoff is removed; epochs stay finite. Earlier fixed-fixture notes
below are historical. Next: partial/unknown reply and cleanup-failure controls.


**Consumer checkpoint 2026-10-03:** [four native owner cases](evidence/si07-owner-2026-10-03/README.md)
now qualify the fixed five-cycle sys-init path, including idle, reclamation, halt,
early/late cohort rejection and exhaustion. Next is quiescent request-loop policy
and focused failure controls; the producer intake dependency is resolved. This
checkpoint supersedes earlier pending-integration wording below.

**Matched intake available 2026-10-03:** [local verification and replay](evidence/si07-intake-2026-10-03/README.md)
close the missing producer/userland input dependency. The frozen ABI22 positive
replays five useful cycles, idle beyond3000 ticks,15 reclaims and authorized halt.
Next is sys-init-owned consuming integration with the explicit quiescent-shutdown
and partial-reply limits in that record. Producer replay is not our owner acceptance.
Earlier blocked/queued statements below retain their historical scope.

**Request queued 2026-09-24:** the maintainer authorized adding
[Aether SI-07](../../.planning/ROADMAP.md#si-07--sustained-sys-init-lifetime-reuse-and-authorized-shutdown)
to the producer backlog. Aether ROADMAP/STATE now track lifetime/idle-wakeup,
reclaim/reuse and authorized shutdown, with a frozen producer packet and independent
sys-init consumption required. This supersedes the historical "not a sent request"
wording below. Producer implementation and acceptance remain pending; current
runtime inputs, released pins and earlier evidence are unchanged.

Reviewed 2026-09-08 under BG-067. The bounded command integration is qualified;
the next v1 requirement is to remain available between useful commands and accept
an authorized orderly shutdown. The current producer command handoff still leaves
this separate. This is a local proposal for coordination, not a new ABI, a sent
request, an accepted shared standard or authorization to change Aether.

## Evidence and exact gaps

Sources are preserved in the [review snapshot](evidence/sustained-handoff-review-2026-09-08/README.md).

| Boundary | What exists | What the consumer needs next |
| --- | --- | --- |
| Lifetime | Frozen [nativeTick](evidence/sustained-handoff-review-2026-09-08/inputs/frozen/kernel/arch/x86_64/native_c.zig) requires total_ticks <3000 independently of worker progress. The [current command contract](evidence/sustained-handoff-review-2026-09-08/inputs/Aether/docs/NATIVE-INIT-COMMAND.md) explicitly leaves watchdog/idle acceptance open. | A selected sustained profile that distinguishes the external test deadline from healthy guest lifetime; documented clock/deadline behavior. Simply lengthening a counter is not a sustained-init contract. |
| Wait/wakeup | Yield0x1fffe rotates execution. The frozen kernel also contains timed/indefinite address waits0x28003/0x28008 and wake0x28004. [SI-01](evidence/sustained-handoff-review-2026-09-08/inputs/Aether/.planning/ROADMAP.md) retains a bounded accepted scope and requests a concrete workload before extension. | Explicit eligibility and authority in the selected supervisor profile, and a race-safe way to wake for command/shutdown input or worker terminal state. An address wait or older ABI6 observation API alone does not prove that composition. Reuse mechanisms where sufficient; no new event daemon is requested. |
| Reuse | launchOperation returns ENOSPC after three worker generations; channel allocation selects only slots below generation3. Existing owner budgets are deliberately bounded per experiment. | Confirm live-object quotas versus lifetime counters, exact stale-handle protection and finite-ID exhaustion policy. Healthy completed cycles must not hit the fixture's three-generation ceiling. Keep bounded restart policy distinct from normal successful command reuse. |
| Final action | Supervisor0x20006 accepts result100 plus exactly six reclaims in this connection profile, checks cleanup, prints PASS and calls serial.halt. | A documented authorized shutdown request source and actual supported final action (halt, poweroff or reboot as selected by the producer). Name unsupported actions. PASS, QEMU harness termination and worker stop are not operator shutdown. |

The [seven-case stop witness](evidence/command-owner-stop-2026-09-08/README.md)
proves cancellation before a backend effect, exact stopped status, alias retirement
and complete cleanup. It does not settle interruption of an already issued backend
effect. For the first sustained workload, finish an outstanding bounded request
before stopping clients, or define another explicit interruption policy with its
owners. Do not infer idempotent replay or flush/persistence from this memory backend.

## Smallest requested workload and acceptance

Keep the existing runner, bytecount command and memory backend, with sys-init
owning direct startup/observation/cleanup. No shell, descriptor framework, journal,
new service or extra platform is necessary for this boundary review.

1. Boot the matched sys-init/application image and publish its usable entry point.
   Keep essential services available while no command is pending; demonstrate
   actual blocking/idle and an eventual wake beyond the old fixture lifetime.
2. Run sequential useful commands past the current three-generation ceiling.
   Verify exact output/status and bounded live resources; stale handles must still
   reject. A finite test checks the selected reuse mechanism, not infinite uptime.
3. Exercise input/terminal state before registration and during the wait transition,
   including spurious wake and cancellation behavior supported by the contract.
   State observed before waiting must not cause a lost wake or fabricated progress.
4. Deliver a shutdown request through the selected authorized input. Stop new
   admissions, settle outstanding work, stop/observe/clean clients before backend,
   and invoke only the documented final action. Denied/foreign requests must not
   change lifecycle intent. Retain a failure if cleanup or authority is unresolved.
5. Retain exact profile/version, entry grants, supported operations/errors, live
   and lifetime limits, source/build hashes, runnable positive and semantic-negative
   cases. Freeze that packet locally and run a sys-init-owned consuming witness.
   Preserve old profile bytes, regression markers and released standards pins.

Aether owns native wait/authority/lifetime/final-action mechanics. Userland owns
application/input transport semantics. Sys-init owns admission, restart limits,
shutdown ordering and consuming acceptance. A real shutdown input may be a scoped
existing connection; do not assume a privileged textual command or invent a syscall.
Future shared normative rules belong in Aether-standards; exact native contracts
belong with their producer. No owner approval is inferred from this proposal.

## Local disposition and simplicity review

BG-067 remains active but native sustained integration is blocked on this matched
handoff. Existing bounded acceptance remains complete and retained. Current Aether
signal work is a separate boundary; do not adopt candidate kind4 into ABI9 or wait
for full dash as a substitute for these requirements. Recheck when a matching
contract/evidence packet arrives, not on every unrelated producer milestone.

The simpler alternative is the existing bounded finish fixture. It remains useful
for regression but cannot satisfy v1 idle or operator shutdown. The chosen next
work is to extend only the workload's needed mechanisms through an explicit
handoff; there is no local runtime change now and no speculative machinery to add.
Remove stale current-next-step text, retain historical evidence. Applicable O-01/04,
I-01/03/04/05 and E-01–08 require owner boundaries, truthful unsupported behavior,
bounds and frozen evidence. No new exception or conformance claim is introduced.
