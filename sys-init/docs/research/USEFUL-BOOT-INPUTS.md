# Useful boot inputs: BG-066 review

2026-09-07. The direct service pair is ready for an integration adapter, but the
inspected deliveries do not supply a matching sys-init-owned useful boot profile.
BG-066 completes its source-review alternative; native integration is blocked on
BG-067. No runtime implementation, producer pin or released standard changes.

## Inspected evidence and compatibility

All citations below point to [captured inputs](../evidence/useful-boot-review-2026-09-07/README.md),
not live build dependencies. This is a selected source review, not complete
artifact qualification or an independent rerun of companion tests.

| Boundary | Existing coverage | Missing work |
| --- | --- | --- |
| Init image and launch | [Aether NATIVE-INIT](../evidence/useful-boot-review-2026-09-07/inputs/Aether/docs/NATIVE-INIT.md) defines AENIN003/ABI16: two ELF images, two worker slots, 16 KiB supervisor code, separate 4 KiB stack. Our [adapter](../evidence/useful-boot-review-2026-09-07/inputs/sys-init/prototypes/native-supervisor/adapter.rs) launches image grant 0xc001 in either slot with argv `s`, fixture mode and one transferred readiness writer. | A matched role/image inventory and entry grants that let init own the real runner/backend lifecycle. Slot selection does not select another image or compose profiles. |
| Real command | Userland's [four-role witness](../evidence/useful-boot-review-2026-09-07/inputs/Aether-userland/docs/evidence/four-role-native-2026-09-07/README.md) reports actual `bytecount --decimal`, exact `6\n`, unchanged `abcdef`, exit zero and six reclaims across two generations. Wrong-role and omitted-close controls reject. | Independently consume that application under the selected sys-init entry/ownership boundary. Its existing source-built owner is not the BG-065 coordinator. Six reclaims do not qualify init's three-reclaim fixture. |
| Startup and I/O | The [four-role plan](../evidence/useful-boot-review-2026-09-07/inputs/Aether-userland/docs/evidence/four-role-native-2026-09-07/sources/FOUR-ROLE-PLAN.md) validates a 160-byte AERIO001 carrier: stdout/write/512, stderr/write/256, child-input/read/6, child-output/read-write/64. Child retains its two-binding adapter. | Define who supplies those connections, owns each close, and observes terminal/reclaim after partial launch or stop. A readiness writer cannot substitute for these file references. |
| Profile composition | [Command runner](../evidence/useful-boot-review-2026-09-07/inputs/Aether/docs/NATIVE-COMMAND-RUNNER.md) explicitly leaves sys-init lifecycle integration separate. [Native parser](../evidence/useful-boot-review-2026-09-07/inputs/Aether/kernel/native_launch.zig) separates three-image connection envelopes from two-image init envelopes. | Producer/consumer agreement on the smallest composed boundary; no guessed syscall, extra image slot, or ownership transfer. Existing command protocol remains userland-owned. |
| Real shell | [Userland workloads](../evidence/useful-boot-review-2026-09-07/inputs/Aether-userland/docs/evidence/dash-workload-handoff-2026-09-07/README.md) mark twelve actual dash cases NOT RUN. Newer [signal frame work](../evidence/useful-boot-review-2026-09-07/inputs/Aether/docs/evidence/shell-signal-frame-2026-09-07/README.md) tests a CPU codec and explicitly enables no handler/syscall. | Full dash delivery and independent userland acceptance remain upstream work. They need not block a first bounded bytecount integration. Do not equate startup or codec tests with a shell. |
| Sustained init | [Wait implementation](../evidence/useful-boot-review-2026-09-07/inputs/Aether/kernel/native_wait.zig) rejects registration after generation 64. [nativeTick](../evidence/useful-boot-review-2026-09-07/inputs/Aether/kernel/arch/x86_64/native_c.zig) requires fewer than 3000 interrupts. | A qualified sustained execution/wait strategy and explicit exhaustion semantics. Polling avoids registration consumption but does not remove the watchdog or demonstrate acceptable idle cost. No millisecond timing claim. |
| Shutdown | BG-065 orders dependent stop, actual terminal, cleanup, then provider. Native owner death closes the domain and halts; normal fixture completion halts with supervisor mapped. | An authorized shutdown request source and final action for the selected profile. Neither `finish(100)` nor host QEMU exit is operator shutdown, filesystem flush or poweroff. |

## Smallest next delivery: BG-067

Use one existing real command as the first integration witness. Ask the Aether
mechanism owner and userland application owner for a matched packet containing:

1. Exact kernel/profile, supervisor entry registers, image roles and source-built
   runner/backend/command artifacts; source, SDK, tool and build identities plus
   existing positive/negative logs. State whether init replaces the fixture owner
   or supervises it, and which owner retains command/file protocol authority.
2. Startup argv/environment and connection transfer rules, authority validation,
   per-instance terminal observation, stop and partial-failure cleanup. Map every
   task, channel and file reference to one responsible owner and explicit bounds.
3. First workload: real bytecount, input `abcdef`, output `6\n`, actual exit zero,
   unchanged input and complete owned cleanup. Also empty input `0\n`, denied
   startup without admission, and stopped/faulted command with exact terminal kind
   and retained partial cleanup. Agree exact profile oracles before executing.
4. For subsequent sustained v1 acceptance, execution/wait/watchdog behavior and
   authorized shutdown delivery/final action. A bounded command demo may precede
   this packet section, but cannot close the sustained-boot or shutdown gaps.

Sys-init then freezes and verifies that packet, adapts only its native boundary,
reuses current-state ownership and ordering, and runs its own consuming cases.
Start with a build-time inert service table if no configuration transport exists;
select fields only after the role/launch contract is agreed. No filesystem, parser
framework, shell interpreter or general event journal is required for this step.
No sibling task, message, edit or owner approval was created by this review.

## Simplicity and standards review

Requirement: connect the existing small supervisor to an actual application with
honest boot/lifetime claims. Simpler alternative: swap the bytecount ELF into the
current fixture. It is insufficient because startup, file authority and ownership
are different. Choose a bounded existing command and a narrow native adapter once
its contract exists. Complexity removed now: none; avoid a second command broker,
a temporary shell, and speculative configuration/control machinery. The fixed
pair remains a tested policy component, not an imposed limit on the real service
inventory. POSIX intent remains; no new non-POSIX dependency is introduced.

Foundations O-01/03/04 and I-01/03/04/05 require named owners, enforcing authority,
explicit unsupported behavior and separate termination/cleanup. E-01/04/05/08
require exact input identity and separate source, companion and consuming evidence.
Distribution B-01–04's M4 transport is a different profile; SV-01–05 remains a
candidate descriptor experiment, not permission to infer a target filesystem or
milliseconds. No new exception is requested and no conformance/sign-off is claimed.
SE-01–05 are applied through this existing review. Documentation impact is this
map, current planning and quality gap; runtime/CLI bytes remain unchanged.

Validation: source snapshot hashes and local references are checked; full offline
repository results are retained with the evidence bundle. No new target run is
appropriate for this documentation-only review. BG-067 records the remaining
external dependency without expanding the shelved roadmap.
