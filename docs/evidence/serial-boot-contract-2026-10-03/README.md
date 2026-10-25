# Sys-init / serial-shell composition review — 2026-10-03

Before-work requirement: trace the qualified ABI22 init and ABI23 serial SESSION
paths, capture exact sources/owner contracts, identify the smallest next kernel
mechanism and a consuming experiment. No runtime edit, new ABI allocation, sibling
write, released-pin update or consumer approval is inferred from this review.
Host/pin/workflow and scoped links/source-snapshot checks qualify the documentation;
no new QEMU run is needed for this source/contract review.

## Source findings

| Boundary | AENSI001 / ABI22 | AENMX008 / ABI23 |
| --- | --- | --- |
| Boot envelope | Three images,80-byte header; owner16KiB | Three images,112-byte header; owner24KiB |
| Owner / workers | Supervisor slot3; three worker slots | Supervisor slot5; five worker slots; SESSION parent0, copied participants2/3/4 |
| Task/channel identities | Typed full-width identities; native generation limit0x0fffffff; private v2 epoch1..65535 | Existing SESSION encodings;15 task/channel lifetimes; bounded pipe epochs and descriptor/process facade |
| Actual workload | Runner/bytecount/memory backend with sys-init paired ownership and r/h request loop | Native dash/input/process/memory facade, copy/rebind/exec, two pipes and scoped volatile scratch |
| Input | Owner UART; one-byte run/halt requests between completed commands | Owner UART routes application stdin/stdout/stderr; shell/children have connection-local references |
| Lifetime | Healthy total ticks are not limited to3000; retained owner observe/park | nativeTick still rejects total_ticks>=3000; owner run/transfer loops also have100000-step fixture budgets |
| Final action | Owner snapshot/park/halt0x2a000–2; separate final-action grant; closed console and complete settlement | end(100)/0x20006 requires fixture observation totals; three parent generations and expected workload counters |

Captured native_c.zig shows that both launch/process authority and the default
console holder are checked against supervisorSlot(). The new kernel cannot be
obtained by enabling `native-init-sustained` alongside the SESSION build: start()
explicitly rejects the conflicting process-copy/exec/memory/capacity closure.
The ABI23 owner checks23 at entry; ABI22 owner checks22. Different supervisor
images, bootstrap headers and private reference/receipt protocols cannot be mixed.

The captured sys-init table binds Backend/Runner/Command role/image/order. It is
not a shell table; even its bounded retry variant is specific to that command
path. Captured userland guidance assigns bounded libc/POSIX runtime implementation
to userland while Aether retains the existing fixture and native enforcement.
The runtime candidate explicitly admits008, not an arbitrary new boot profile.
No newly discovered bypass, corruption or stale reuse defect is claimed here.

## Selected bounded direction

Use one boot supervisor protection domain for the first experiment: actual sys-init
policy and the existing bounded SESSION dispatch responsibility must compose
explicitly in that domain. Keep policy ownership with sys-init, client/libc/POSIX
runtime ownership with userland, and native grant/lifetime enforcement with Aether.
This is a constrained composition direction, not approval to rename the current
fixture as sys-init or to assign its dispatcher implementation to another owner.
Sys-init must supply a genuine consuming entry/loop; userland must qualify the
matching client/runtime component closure. The first Aether producer may use a
clearly labelled private owner witness while those consumers adapt.

This arrangement preserves the current owner-only factories/UART. It grants no
child permission to launch/copy/exec/reclaim or access UART. Putting the dispatcher
in an ordinary child is insufficient; handing that child supervisor authority
would need a separately reviewed delegation/domain contract. Do not build that
new process server/delegation framework for the first bounded boot experiment.
Co-location makes runtime dispatch part of the supervisor TCB and shares its
failure domain; it is not restartable-service fault containment. A later split
needs explicit delegated factory/image/console scope and independent cleanup.

The next kernel slice is a **separately selected serial SESSION lifecycle profile**:
retain the current process/descriptor/memory/IPC behavior and SESSION identities,
live quotas and finite lifetime limits. Add only owner-scoped monotonic snapshot/
compare-park and authorized quiescent halt, reusing the SI-07 event-state core.
Separate healthy lifetime from the external watchdog in this profile. Do not set
the existing sustained flag, change SESSION IDs to ABI22 typed IDs, raise resource
limits or silently widen old ABI23. Assign exact new envelope/owner ABI/build
selection in that implementation, and reject absent/wrong/mixed selection. No new
identifier or executable support is allocated by this design record.

Observe/park must validate the actual supervisor and its clock grant, reserve
fields, atomically compare/register with IF=0, and publish only owned serial/channel/
terminal changes. Completion is a rescan hint, not an I/O result or terminal proof.
Halt uses a distinct owner grant and must reject live/admitted workers, open/queued
channels, open UART or pending park. Unsupported actions and denied grants have
no lifecycle effect. Fixture observation counts must not become product policy;
retain the old observation/finish gates for the old profiles and its tests.

Keep one shell initially; no automatic restart of unknown-effect work. The existing
15-lifetime/pipe bounds remain explicit and failures must retain ownership and
stop admission. This kernel slice does not claim an indefinitely extensible shell.
Consumer owner loops must remove the fixed three-parent/workload checks and their
idle iteration cutoff on the selected path, using observe/drain/park instead.
Do not spin forever or merely lengthen a counter. Separate current test witnesses
from normal boot: the30-second SI-07 probe and scripted nine-prompt schedule are
not product initialization or user instructions.

## Next executable acceptance

First qualify the new kernel profile with a private native owner witness and exact
old-profile regressions: valid/malformed envelopes, wrong owner ABI/selector, code/
stack bounds, owner/worker grant denial, real timer idle beyond3000, serial readiness
on both sides of registration, retained channel/terminal wake, deadline/no fabricated
progress, stale identities, busy/unsupported halt and actual clean authorized halt.
Freeze source/tool/firmware/artifact pins and retain failed attempts. This producer
mechanism witness is not the completed sys-init/shell composition.

Then compose an actual sys-init-owned owner with matched userland runtime payloads:
boot straight to an interactive serial prompt, preserve one parent across input,
execute the existing external-program/redirection/pipeline workload, delay input
beyond the old lifetime, exit and reclaim the session before owner-only shutdown.
Shell exit is not by itself a kernel final-action request; sys-init selects the
policy after confirmed settlement. Denied/wrong-profile/missing-component and
interrupted/unknown cleanup controls must fail explicitly without granting broader
authority or replaying an unknown effect. Record current finite limits visibly in
the experimental guide. Independent consuming acceptance remains owner-specific.

This is the next R1-01/02/06 integration slice, not completion of full SUSTAIN-01–06,
SDK/reader review, persistent filesystem, package lifecycle or assembled R1. The
shared Distribution boot profile remains a proposed separate transport contract;
native envelopes do not acquire service/package semantics from that document.

## Security and simplicity

Untrusted shell input reaches the bounded userland facade/owner protocol; only
native holder checks authorize kernel effects. Preserve connection identity,
partial frame/reply ownership, masks/TLS/CLOEXEC, strict memory adaptation and
stop/terminal/close/reclaim order. Unknown cleanup blocks further admission.
No new unsafe/FFI boundary, dependency, authority or resource increase is made by
this review; implementation must document the new selected dispatch boundary.

Simpler alternatives: reuse ABI23 unchanged for a short demonstration, but its
3000-tick/iteration/three-parent/fixture-finish restrictions cannot provide a healthy
manual prompt. Reuse ABI22 unchanged, but it lacks the SESSION copy/exec/memory/pipe
closure. A separate privileged dispatcher would add delegation and recovery work
before a current consumer can use it. The chosen narrow profile reuses existing
kernel event state and keeps one authority owner. No maintained mechanism is removed
now; scoped consumer changes can remove production dependence on test cutoffs.
Foundations O-01–05/I-01/03–06/E-01–08 and local SE-01–05 apply. No independent owner
sign-off or standards adoption follows from these findings.

## Verification

Captured inputs and origins are bound by inputs.json; current-source comparison,
local host/pin/workflow/link checks and source findings are recorded in checks.json.
Run `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global` and
`python3 scripts/check_workflow.py` from the repository root. This review reads
mutable companion documents only at capture; checks use those local copies. Source
snapshots remain reference material, not new build/runtime dependencies. The packet
is sealed by SHA256SUMS; no sibling files/tasks are modified or messaged.
