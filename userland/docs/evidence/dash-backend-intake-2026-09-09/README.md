# UL-007 malformed-backend consumer intake preparation — 2026-09-09

Static intake preparation is complete. **Native qualification is NOT RUN here.**
At capture, Aether reports its401-case suite still running and its backend-recovery
packet awaiting sealed command-results.json/manifest.json. Last local runtime
acceptance remains the [397-case known-result recovery](../dash-file-recovery-consumer-2026-09-09/README.md).
The ten [captured review inputs](review-inputs.json) have matching before/after
hashes. These are intermediate static-review snapshots, not approved runtime pins.

## Reviewed recovery order

The selected service mutations perform a real open/read/close and corrupt reserved
reply byte12. Reviewed forwarding code validates the complete reply before
publishing the backend handle, updating the read offset or clearing a closed record.
A failed checked exchange or invalid reply closes client reply delivery, records
uncertainty and blocks subsequent client requests. It does not replay the operation,
guess an unverified handle or forward a partial reply.

The existing poison client must terminate with1 before the owner requests scoped
file-service stop. The owner checks encoded terminal status144/kind3, then clears
local descriptions. Later cleanup checks decoded143/kind3 again before reclaim.
Normal stream termination remains17. Forced stop emits no normal file-exit log, so
successful serial records contain only client1 and stream17 per generation plus
supervisor100/reclaimed6. This absence alone is not proof of stop: the owner query,
source identity, omitted-stop control and reclaim outcome must agree.

[Four prepared case expectations](expected-cases.json) distinguish open/read/close
successfully contained failures from omitted-stop rejection1601 after client1 with
zero reclaims. They contain expected arrays only; no observations or runtime pass
are fabricated. Reuse the original poison-client buffer/publication/mask/no-traffic
checks when the completed matching packet arrives. Keep the prior known-result
client-leg recovery cases as separate regressions.

## Source and size assessment

The checked exchange and existing fatal wrapper share request encoding. Private
callers supply a zeroed32-byte reply buffer; incomplete data is not published.
File forwarding passes the checked buffer through validation, avoiding duplicate
aggregate copies. Explicitly outlined helpers retain the existing8192-byte owner
limit. The producer currently reports a largest8120-byte size preflight, leaving
72 bytes; that is compilation evidence only, not a local target result. Verify
actual final new and affected old owner images without relaxing the bound.

No new kernel API, service policy, quota or general restart mechanism is selected.
The reviewed changes remain the existing single-client fixture and scoped service.
This review does not approve a future full source migration or replace independent
technical/reader sign-off.

## Intake gate and follow-ons

Before local runtime reproduction:

1. Require a completed sealed packet and verify every manifest/source/archive byte.
2. Compare the final frozen sources with this review snapshot and the locally
   accepted397-case runtime. Reassess any differences rather than assuming identity.
3. Retain producer image-bound failures, size-only preflights and the lifecycle-oracle
   failure/correction. An observed supervisor100/reclaimed6 in that earlier run is
   not a passing full suite. Preserve its report as recorded.
4. Select the matching full original suite with pinned SDK/tools/main object and
   unchanged limits, then check the completed receipt, exact serial expectations,
   source/SDK identity, native reclaim and host cleanup separately.

Missing/partial backend replies and bounded timeout injection still need native
witnesses. A checked uncertainty branch is not proof those paths execute correctly.
Malformed complete replies must not be promoted to complete backend-recovery coverage.
Then qualify actual-main ENV loading/suppression/unsupported -p and existing dash
argv/signal/syntax/external-child/exec/wait/redirection/pipeline workloads. General
filesystem/persistence, M3 and UL-016/063/081 broader gates remain open.

No runtime source, sibling, default, released pin or existing evidence was changed.
[Review plan](review.md) records scope and test selection. No monitoring or native
run was started for the unfinished delivery.

Local quality, captured-input integrity, JSON inventory and tracked-document
whitespace checks pass. These validate this preparation, not producer runtime.
