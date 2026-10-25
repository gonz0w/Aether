# Persistent boot input review — 2026-10-18

BG-067. The new storage handoff permits integration preparation. It does not yet
provide a filesystem service that sys-init can launch. The existing bounded
[serial recipe](../AETHER-SESSION.md) remains usable; continued ordinary shell use
still needs the [wider SESSION delivery](../SESSION-LIFETIME-HANDOFF.md).

## What changed

Aether now assigns the operational Rust filesystem service to Aether-userland;
Aether retains native engine/block mechanisms. Its [owner handoff](../../../docs/OPENZFS-FEASIBILITY.md#filesystem-service-owner-and-producer-handoff--2026-10-18)
reports one clean native overwrite/export followed by independent fresh-VM
readonly readback. The old creator/import failures are historical, not a reason
to wait before reviewing the current service inputs. OpenZFS is selected for R1;
snapshot/rollback is post-R1 in that handoff. This review does not independently
replay the pair or promote the candidate.

Userland's [maintained policy contract](../../../userland/experiments/filesystem-service/README.md)
describes a no_std library, with four sessions, sixteen handles, explicit WRITE
attenuation, trusted UTC, alias coherence and one nonempty provider call per
context. Its published slice reports thirteen host tests and eight omission
controls. Bridge and native-probe sources are also present in the working tree;
their presence alone is not a qualified daemon or authenticated service delivery.
The probe explicitly uses fixed internal test principals, not native transport
authentication. No public writable opcode, startup command or readiness frame is
accepted by this review.

[Input observations](PERSISTENT-BOOT-INPUTS.json) record exact source/document
identities. All five engine/namespace source hashes and the paired receipt match
userland's policy intake pins at observation time. These hashes are research
observations, never mutable sibling build inputs. Host policy and producer-native
evidence remain distinct from sys-init native consumption.

## Smallest next activation delivery

Keep one filesystem policy owner in userland. Do not copy the engine, add a
filesystem broker here, or assign a new wire/boot ABI merely to connect fixtures.
Use existing direct lifecycle primitives once a matched service is delivered.

| Boundary | Delivery needed before sys-init wiring | Consuming witness |
| --- | --- | --- |
| Executable and startup | Userland supplies an exact executable/entry, build/tool/dependency/notice closure and matching kernel profile; declare service resources and provisioning inputs | Verify frozen selection, build and boot the actual service; wrong/missing component rejects before dependent admission |
| Authority | Producer supplies actual block/dataset and authenticated endpoint provisioning, with explicit rights and nonreused identities; paths, PIDs and test peer labels confer no grants | Denied/wrong-generation provisioning cannot admit a filesystem-backed consumer; old handles stay denied |
| Readiness | Userland defines an observable readiness contract tied to the selected service generation and usable namespace, with failure outcomes and wait bounds | Admit the filesystem-backed runner/shell only after that evidence; malformed, absent or stale readiness closes admission |
| Failure | Match committed/uncertain engine outcomes to permanent context retirement and unavailable service state | Lost reply/unknown cleanup cannot trigger automatic replay, reopen/reset or replacement against the old storage authority |
| Shutdown | Define how admission closes, dependents settle, and service drain/export, block completion/quiescence and native reclaim are observed separately | Stop dependents before providers; request halt only after required confirmations. Rust Drop, terminal text and host emulator reap alone are insufficient |
| Persistence | Userland supplies filesystem-backed execution and pkg-mgr supplies exact persistent package bytes/records, under their own contracts | Boot the composed workload, modify real files, settle/export and verify contents/records after a fresh boot; do not substitute a host-policy test |

This table describes required semantics, not invented operation numbers or a
launch-order ABI. Physical engine/block layering and the startup dependency graph
must come from the matched composition; do not infer them from package dependency
metadata. Keep scope to the selected persistent shell/runner/package workload.
General mounts, storage plugins, service publication frameworks and recovery
remain outside this intake.

## Compatibility and current stop point

ABI22 request-loop, ABI24 serial-session and private ABI14 block/readonly witnesses
are distinct closures. Their successes cannot be combined by mixing envelopes,
flags or grants. Keep released standards, developer locks, old images and boot
markers unchanged. The shared package/service proposal remains candidate.

The current kernel still selects fifteen SESSION child lifetimes. Userland still
names wider SESSION separately; new storage progress does not change the serial
identity encoding. Two concrete deliveries remain: wider SESSION for continued
shell use, and the executable/provisioned filesystem service for persistent boot.
BG-067 retains both missing-work items and the acceptance table above. No sibling
files or messages were changed; this is a local intake, not a sent owner request.

Foundations O-01–05, I-01/03–06/08 and E-01–06/08 apply: preserve domain ownership,
explicit bounds/unknown cleanup and exact consuming identities. Distribution
RL-01/02/05 applies to the experimental evidence; this does not adopt its B/SV
proposal as a new runtime interface. No new shared standard or exception follows.

Simplicity review: the simpler alternative is to wait for a launchable delivery.
Choose a short intake now because the owner assignment and available evidence
changed; it prevents duplicate implementation and removes stale storage blockers
from planning. No runtime layer, dependency or additional harness is needed.
Independent assembled/reader review and release authorization remain separate.

Validation: select local quality-record checks, applicable offline standards and
the repository-required full development checks. No native behavior changes or
new VM campaign are part of this documentation review.

Result: all ten `python3 scripts/check-all.py` gates pass with unchanged checked
sources (`out/checks/run-xvgzezob/results.json`). The input record retains its
digest and compact outcomes. All five intake links/anchors resolve and
`git diff --check` passes. No native VM or sibling checker was executed here.
