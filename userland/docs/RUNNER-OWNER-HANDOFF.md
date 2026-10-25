# UL-059 owner review packet: native local outcomes

Prepared 2026-09-06 for the Aether owner of UP-02 / command I/O. This packet is
ready for review, but has not been sent, inserted into a sibling backlog, accepted
or implemented there. Userland's native local-outcome path is waiting for the
owner extension below. The existing [RL-01–12 proposal](RUNNER-LOCAL-OUTCOMES.md)
remains the acceptance specification; this packet consolidates evidence and the
requested next work, without allocating a second contract or task ID.

## What is ready

| Consumer evidence | Demonstrated scope | Limit |
| --- | --- | --- |
| [Native consumer](evidence/runner-native-budget-2026-09-06/summary.json) | 66 combined and nine legacy cases; native startup, child argument observation, status mapping, rejection/publication and bounded pending control flow | Injected uncertainty/budget failures do not establish remote timeout or recovery; default pins unchanged |
| [Local delivery](evidence/runner-local-delivery-2026-09-06/summary.json) | 6,130 UBSan host scenarios and four mutants; exact fixture bytes, short writes, unknown-result stop, separate close facts | Logical callback sinks only; no native grants or resource release |
| [Local frontend](evidence/runner-local-frontend-2026-09-06/summary.json) | 280 UBSan host scenarios and three mutants; actual parser/admission decoder chooses pinned text, forwards owned invocation once and preserves accepted receipt | Not linked into the native runner; AF_LOCAL is an attempt whose delivery status may be1; accepted receipt is not child completion |
| [Current input review](evidence/runner-owner-handoff-2026-09-06/verification.json) | 6,956 retained evidence files verified; current command contract, owner, supervisor and backend match the consumed producer bytes | Integrity/read-only review, not a fresh target run or affected-owner sign-off |

The [host candidate guide](../experiments/command-runner/LOCAL-OUTPUT.md) identifies
source and reproduction commands. Native reproductions remain in
[the native guide](../experiments/command-runner/NATIVE.md). No new compiler, libc,
shared release or package dependency is requested by this handoff.

## Why the current producer cannot qualify local outcomes

The reviewed [command owner](../../aether/user/native-command/owner.rs) requires
`admitted && collected` and the child's exit before accepting the mapped parent.
Its final lifecycle gate also requires that child and the existing file positions.
The [backend](../../aether/user/native-files/service.rs) supplies a 64-byte scratch
buffer. The parent has the existing input/output bindings, without a separate
runner stderr role. Proposed help is472 bytes. Changing the expected parent exit
alone would bypass the workload oracle while still leaving output authority,
capacity and no-child resource accounting unresolved.

The current owner contract still describes userland parser adoption as pending;
the consumer evidence above updates that scope for review. The canonical owner
files were not edited here. Aether currently tracks UP-02 in its ROADMAP/STATE,
not a BACKLOG.md. Use those existing records rather than inventing a duplicate ID.

## Decisions requested from Aether

| Decision | Existing proposal / required observable result |
| --- | --- |
| Explicit runner output roles and versioning | RL-09: choose the role carrier, write/close authority, validation and generation rules. Preserve current child inheritance; logical host sink0/1 is not a native FD assignment. |
| Bounded separate storage | RL-01/02/06/07: review proposed stdout512/stderr256 capacities, exact readback and failure prefixes; keep opposite sink empty and command input unchanged. |
| No-child lifecycle and baseline | RL-03/05/11: enumerate aliases, handles, endpoints, parent/backend and any quota helper; decide actual per-generation reclaim totals. Proposed four reclaims is unaccepted, not copied from the six-reclaim child test. |
| Independent admission observations | RL-01–05/10: distinguish request count, successful admission, allocation and collection. A local action needs zero requests/admissions/collections; a complete denied launch needs its exact error and zero admissions. |
| Trusted verifier inputs and markers | RL-10/11/12: bind expected action/text to trusted fixture input, not the parent's claimed status; reject skipped/corrupted/misrouted output, unexpected launch and missing close. Preserve existing markers and exit contracts. |
| Unknown delivery and cleanup | RL-07/08/11: specify what remains owned after ambiguous transfer/close and how the owner observes it. Do not convert an unknown admission into no child, or a failed test into successful recovery. |

These are domain implementation decisions. If review introduces new cross-project
requirements, route them through Aether-standards' contribution/versioning process.
No vendored pin is changed here. The recorded combined broker is7544/8192 bytes;
any different implementation budget/profile needs explicit owner justification
and qualification, not a silent relaxation in the consumer.

## Suggested UP-02 follow-on, ready to copy into owner planning

Implement an opt-in native local-outcome producer for userland UL-059 using the
RL-01–12 proposal. First review and record the output-role transport, object
inventory, capacities and independent verifier contract. Deliver real `--help`
and `--version` output without admitting a command child, with observed complete
cleanup. Then qualify usage and known ENOENT/EACCES/EBUSY outcomes, positive short
writes, delivery/close failures and semantic negative controls. Preserve existing
finite/startup/mapped profiles and all prior pins. Return an immutable producer
source/evidence bundle for independent userland consumption.

A no-output/no-child lifecycle prerequisite is useful if needed, but it is not
accepted help/version delivery. Proposed text bytes remain in
[the fixture manifest](proposals/runner-local/manifest.json); changing them needs
an explicit reviewed identity and consumer update. Userland owns the actual parser
and frontend, so the producer need not duplicate that policy to verify its effects.

## Return package and consumer acceptance

Return the reviewed exact contract/profile identity, compatible role/version and
bounds, the actual resource inventory and expected lifecycle markers, plus owner
review decisions and unresolved cases. Include a complete regular-file source
archive/manifest, tool/SDK/flags/environment identities, exact test commands,
artifact hashes, raw serial/verifier results, cleanup facts and every failed or
incomplete attempt. Identify which RL cases passed and which remain unimplemented.
Do not update userland's existing producer pin on its behalf.

Userland will verify the returned bytes before building, review the exact contract,
explicitly select a new pin and adapt native role validation/transport. It will
build its own clients, wire the real parser/local frontend to real libc output,
and independently rerun relevant RL cases plus existing child/legacy regressions.
Only then can native local outcomes advance from waiting to scoped acceptance.
Unknown recovery, independent review, package transport, sys-init policy and a
working POSIX/TTY shell remain separate gates.

No message, owner task, sibling edit, monitoring automation or sign-off was created
by preparing this packet. While that dependency is outstanding, local UL-067
Toybox/native dependency audit can proceed; UL-069 remains deferred. Reassess
UL-059 first when a concrete new owner contract/bundle becomes available.
