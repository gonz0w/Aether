# Control authority producer review — 2026-09-06

BG-050/BG-032/BG-033 review of selected current Aether source, not a new native
run. [Frozen inputs](../evidence/control-authority-review-2026-09-06/reviewed-files.json)
record file hashes, rechecked after capture; Git HEAD is context only because
the checkout contains ongoing work. These selected files are not a build pin.
sys-init's ABI-6 consumer pins and retained native outcomes remain unchanged.

## Finding

Existing Aether channels can supply a **launch-bound private connection** for a
bounded control experiment. They do not by themselves implement authenticated
operator sessions, service authorization, reconnect or receipt recovery. No
new kernel syscall is justified merely to parse sys-init requests. Composition
and caller lifetime need a concrete consumer contract first.

| Reviewed source | Mechanism and limit relevant to sys-init |
| --- | --- |
| [Channel contract](../evidence/control-authority-review-2026-09-06/reviewed/Aether/docs/NATIVE-CHANNEL.md) | Endpoints bind owner, channel identity and generation; launch transfers authority, old holder loses access. Short transfers are at most 16 bytes over a 32-byte queue. Endpoint closure is consuming; reader closure stops further writes but does not make buffered requests authorized. No arbitrary reverse transfer or delegation tree. |
| [Channel implementation](../evidence/control-authority-review-2026-09-06/reviewed/Aether/kernel/native_channel.zig) and [trap implementation](../evidence/control-authority-review-2026-09-06/reviewed/Aether/kernel/arch/x86_64/native_c.zig) | Channel.lookup compares stored owner and encoded generation/identity. channelOperation obtains owner from kernel active state and calls ownedChannel(active, handle), not a payload sender field. This source review supports the documented boundary; it is not a fresh execution witness. |
| [Process broker](../evidence/control-authority-review-2026-09-06/reviewed/Aether/docs/NATIVE-PROCESS.md) | One requester connection selects the private worker namespace. Numeric tickets are broker policy, not authority. No reconnect/replay IDs; lost launch/collection reply is unknown. Its client-death teardown stops children, unlike sys-init's disconnect-preserves-work policy. Do not copy that teardown algorithm. |
| [Connections ABI 9](../evidence/control-authority-review-2026-09-06/reviewed/Aether/docs/NATIVE-CONNECTIONS.md) | Two private client pairs and a backend pair demonstrate separate incremental request buffers. Six channels/three worker slots remain finite. Backend/reply loops are still synchronous and can fail on stalled peers; this does not prove our deadline/backpressure behavior. |
| [Command I/O](../evidence/control-authority-review-2026-09-06/reviewed/Aether/docs/NATIVE-COMMAND-IO.md) and [broker source](../evidence/control-authority-review-2026-09-06/reviewed/Aether/user/native-command/owner.rs) | Caller-bound aliases, validation-before-reservation and generation-scoped launch receipts offer useful examples. Terminal collection consumes once and native reclaim is separate. Failed replies abort with unknown outcome; there is no automatic replay/recovery. These are command/FD policies, not service control authorization. |
| [Init ABI 6](../evidence/control-authority-review-2026-09-06/reviewed/Aether/docs/NATIVE-INIT.md) | Registered observations use owner-bound authority and delivered-interrupt time. Supervisor death closes the local domain with no replacement/recovery. Do not silently combine ABI-9 capacity with ABI-6 timing/failure semantics. |

The latest captured [Aether state](../evidence/control-authority-review-2026-09-06/reviewed/Aether/.planning/STATE.md)
reports newer command-frame rejection cases and explicitly calls their result
fatal bounded rejection, not reconnect recovery. That producer report is useful
review input; none of its test totals are added to sys-init native coverage.

## Authority and recovery conclusions

An initial experiment can identify a single supervisor-launched client by the
private endpoint pair established during validated launch. This establishes a
particular domain/connection, not a human identity or rights to every service.
sys-init must bind its own immutable service scope and allowed verbs to that
connection, checking the complete effective scope before admission and disclosure.
An authenticated administrative product would additionally need a real session
authority; [pinned ID-01–05](../vendor/aether-distribution/v0.1.0/IDENTITY.md) forbids
equating UID, console possession or caller-provided names with that authority.

Closing the request reader can prevent future writes. It cannot retroactively
authorize queued data, delete already published response bytes or undo a launched
service. Local revocation therefore needs a policy observation cut: after revoke,
deny queued/new mutations and further response bytes; retain already-owned work.
The effect of bytes delivered before that cut cannot be reversed. A full native
witness must establish this ordering at the broker, not only channel closure.

Our model reconnect method currently means trusted reattachment to the same
retained owner. The reviewed producers do not establish replacement-client binding
to an old service-control session. Initial native work should either explicitly
exclude reconnect or first define an owner-validated reassociation contract.
No reusable numeric client ID or default boot-1 value is an acceptable substitute.

take_effects in our model transfers responsibility but records no execution result.
A native adapter needs matching operation/generation identity, result retention,
explicit failure/unknown handling and reclaim observations. A lost syscall reply
cannot be treated as failure-before-effects. A broker's terminal collection is
not automatically an acknowledgment protocol for sys-init's lifecycle effects.

## Standards and follow-on disposition

The captured [release registry](../evidence/control-authority-review-2026-09-06/reviewed/Aether-standards/tools/releases.json)
still lists the same three v0.1.0 pins. Newer approved draft references in Aether
do not create a released consumer ABI. Shared normative changes remain in
Aether-standards; exact service policy and experiment rules stay here.

[Authority proposal](../specs/CONTROL-AUTHORITY-V0.md) supplies the next acceptance
matrix. BG-050 now owns a single-binding policy model with revocation-at-admission
and revocation-before-output tests; BG-032 owns selection of one actual producer
profile and matching consumer witness; BG-033 owns effect acknowledgment and
driver-death/restart reconciliation. OQ-021/022 record the unresolved questions.
These follow-ons are recorded before closing this review slice. No companion
backlog, source, shared release or existing evidence bundle was modified.
