# Published Aether roadmap additions

Explicitly authorized and appended to [Aether’s roadmap](../../aether/.planning/ROADMAP.md)
on 2026-09-05 (UL-048). The entries below record the approved text; Aether’s
roadmap is authoritative for their subsequent status. Existing SI-04 priority
and the pending canonical PD review were preserved.

## Userland companion integration follow-ons

Recorded after Aether-userland UL-046 independently consumed the completed
ABI-5 launch broker. [Consumer results](../experiments/native-process/RUNTIME.md)
retain six exact target outcomes. These are queued integration/contract items,
not shared-standard adoption or a change to the existing SI-04 priority.
Canonical shared requirements remain in the pending
[PD proposal](../../../Aether-standards/drafts/distribution-v0.2.0/PROCESS-FD.md).

### UP-01 — Inherited file ownership and composable process/file capacity

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

Queued after the bounded broker/coexistence handoff, with affected-owner design
review before implementing a new ABI. A successful launch/collect request is not
fork, vfork, in-place exec or waitpid. The
[dash gap review](NATIVE-DASH-GAPS.md) records the current
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
