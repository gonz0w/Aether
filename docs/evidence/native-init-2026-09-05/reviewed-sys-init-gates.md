# Next readiness and supervision integration gates

2026-09-05. The local fixed-frame host slice now passes 48 tests on macOS arm64
and Linux aarch64 in a constrained Podman container, with identical recorded source
hashes. Native evidence remains the frozen BG-055-based fixtures; the offline
native audit does not execute Aether. [Evidence](evidence/host-diagnostics-linux-2026-09-05/README.md).
This checkpoint pauses expansion of the current readiness/supervision workstream;
other design/backlog work can still proceed independently.

## Required inputs for the next native slice

| Priority/gate | Owning scope | Concrete input needed before sys-init implementation |
| --- | --- | --- |
| 1. Wait and deadline contract | Aether mechanism, BG-032 policy consumption | Versioned clock units/monotonicity/wrap/suspend behavior; wait/wakeup and status-observation rules that prevent lost events; timeout/cancellation semantics and error results; bounded producer/consumer sample and negative oracle |
| 2. Delegated readiness | Aether authority, BG-032/BG-040 | Explicit transfer/delegation mechanism, holder and generation binding, revocation and queued-message semantics; late/stale/foreign sender denial witness. A numeric handle or payload field is insufficient |
| 3. Supervisor death and replacement | Aether lifetime/authority, BG-028/BG-033 | Who owns surviving workers and resources after supervisor death; fail-closed admission; recovery inventory and authority; terminal observation/reclaim and old-owner denial semantics |
| Cross-core extension | Aether SMP mechanisms, BG-032 | Accepted cleanup/translation/authority synchronization rules plus consuming target test. BSP passes cannot substitute |

These are questions and required acceptance inputs, not newly assigned syscall
numbers or a competing local ABI. A new seam should arrive with an exact source
revision or digest, versioned domain contract, offline build dependencies, expected
outcomes and producer artifacts. Sys-init can then freeze the inputs, write the
policy fixture and retain a consuming witness. Fixture PIT/watchdog bounds are
not service clocks. Current native supervision documentation explicitly excludes
recovery after sys-init death; the consumed stream profile is not a blocking
scheduler API. Newer memory work does not by itself satisfy these gates.

Current mutable companion documents were inspected for scope, not adopted as
execution evidence: Aether docs/NATIVE-SUPERVISION.md, docs/NATIVE-IO.md and
docs/NATIVE-MEMORY.md. Future shared rules belong in Aether-standards and require
explicit version/pin adoption; exact kernel ABI remains Aether-owned and exact
sys-init lifecycle policy remains here. No companion message or change was sent.

## Remaining host acceptance inputs

- A usable BSD and illumos execution environment for the same full checks, with
  identity, logs, actual counts and failures retained. No such target is configured
  for this task; no success is inferred from Python/POSIX similarity.
- A selected/configured CI provider and repository remote for hosted runs. There
  is no Git remote configured in this checkout. The offline runner is ready; a
  provider-specific deployment has not been fabricated.
- Production ownership/delegation requirements if stronger containment or sender
  authentication is required. Existing helpers can notify through inherited FDs;
  a helper can survive main death. Cooperative writer closure/exit-path progress
  is observed, external orphan reaping is not.

The existing running Podman VM and cached local image enabled Linux validation
without downloading/building images or starting another VM. Docker's absent
socket was not a blocker once this alternative was verified. No permanent service,
new CI job or background monitor was installed. Source was read-only, network
was disabled and resources bounded for the test container.

BG-040 remains active/partial for wider acceptance; BG-054 remains partial for
BSD/illumos and hosted CI. BG-032/BG-033 retain general native contracts. Resume
this workstream when one of the inputs above is available; do not add more
permutations of the frozen syscall fixture merely to imply those contracts exist.
