# 0176 — Execute and acknowledge the issued reclaim

Date: 2026-09-07. Owner: sys-init. BG-057/BG-058. Status: accepted for the bounded dependent lifecycle.

After decision 0175's generated-dependent Terminal application, consume exactly
its full Reserved reclaim token. Bind the original History/owner, generated
worker and retained launch identity before starting. Close the owned reader,
then invoke reclaim on that exact worker. Retain each actual register tuple
before interpretation. Clear each reference only after its own successful return;
advance Returned/Applied/Executed only after the corresponding observed work.
Do not use fixture disposal as the reclaim acknowledgment.

Preflight denies wrong token, foreign owner and early acknowledgment. Partial
close/reclaim errors retain their actual returns and remaining references, mark
the effect Unknown, and close History admission. Repeated delivery must issue no
additional close or reclaim. Controls cover token and acknowledgment omissions,
forgotten reader/worker clearance, and actual stale-reader/stale-worker errno.
The retained stale reference in those fixtures is not claimed to be a live grant.

Keep AENIN003/ABI 16, 16 KiB code, 4 KiB stack, compiler/tool/producer/worker and
shared release pins. Add no unsafe site or allocation. Use the existing native
trap boundary; local counters follow actual successful returns. Preserve all
older image bytes where possible, with explicit rebuild comparison and fresh
execution for affected/new images. Run all development gates and retain failures.
O-01–05, I-01/03–06, E-01–08 and existing developer-output scope apply. These are
native Aether operations, not POSIX wait or a persistent transaction.

Cleaned policy application follows this execution/acknowledgment qualification;
its admission must require actual cleared resources and the exact acknowledged
occurrence. Provider Terminal, mixed cuts and sustained recovery remain separate.

## Cleaned composition plan

Qualify Cleaned only after the same application retains Executed for the exact
reclaim occurrence and all generated resources are absent. Retire that occurrence
into original-owner metadata, reserve a single phase-3 cut for the same dependent,
and apply 2→3 without an effect. Check retained Terminal history and replay.
Core tests cover premature/foreign acknowledgment, wrong member, replay and
Unknown closure. Native controls cover resource-denial omission and transition
omission. Keep the 16 KiB/4 KiB bounds: a failed composition stays unaccepted.

## Scoped compiler decision and retained attempts

Reclaim fits the existing size-s profile. Initial target execution exposed a stack
fault from nested fixture reuse; moving that work to the caller resolves it. The
stale-reader oracle was corrected from EBADF to the kernel's ownership denial
EACCES (-13). A separate stale-worker fixture setup also needed moving to the
caller to avoid nested stack use. Those attempts remain retained.

Cleaned's unchanged size-s profile is 18,616 bytes and rejects at the 16 KiB
linker bound. Fat LTO with one codegen unit produces a 14,728-byte positive,
without changing code/stack bounds or native operations. Adopt those two options
only for the three new Cleaned probes, recording them in each compile command.
Earlier profiles and other probes keep their compiler options. This is an
explicit experimental build choice, not a whole-project toolchain migration.
Actual consuming execution, rather than linking, must qualify its stack paths.

## Result and next work

Decision 0176 executes the exact generated-dependent reclaim occurrence,
acknowledges it, and applies Cleaned. The driver checks the original source and
full Started token, records actual reader-close and worker-reclaim tuples before
interpretation, and clears each reference only after its own zero success.
Returned/Applied/Executed cannot precede the actual work. Repeated execution and
acknowledgment deny. Partial errors preserve Unknown, actual returns and remaining
references; History admission closes. Closed-reader EACCES (-13) and stale-worker
EBADF (-9) are observed kernel outcomes, not manufactured errno.

Cleaned requires the exact acknowledged reclaim, its original-owner retirement
metadata, a retained Terminal cut and no generated resource references. It moves
the dependent from phase 2 to 3, preserves the original Terminal history, emits
no effect and replays without mutation. Invalid resources/sources deny before
application. Unexpected transition or pool contents retain Unknown and close.
Raw reclaim tuples remain local through acknowledgment; this is not persistent
recovery or extended raw-return retention.

Ten new cases pass in fresh Aether execution: reclaim and Cleaned positives both
return 100/reclaimed 3; token/early-ack/reader/worker/error controls return exact
1100–1105 contexts, and Cleaned controls return 1108/1109 after one reclaim.
All 214 prior ABI-16, 208 ABI-15 and 151 ABI-6 images rebuild byte-identically.
Those 573 comparisons reuse earlier target evidence; this is not a new 224-case
execution campaign. The maintained composed suite now selects 224 cases with
the pinned service worker. All ten local gates pass in run-gsx2lahk; the Rust
core passes 25 tests and 17 omission controls across ten top-level Rust groups.

Default Cleaned linking rejects at 18,616 bytes. Only its three probes add fat LTO
and one codegen unit; positive is 14,728 bytes. Reclaim stays size-s (positive
13,912 bytes). Code stays bounded at 16,384 bytes and stack at 4096. All ten final
paths execute without guest faults; this is not a stack high-water/headroom or
performance claim. Storage/Application remain 1976/1992 bytes, with no allocation
or added unsafe site. Shared release, producer, worker and old profile pins stay
fixed; sibling repositories and historical evidence are unchanged.

Retained failures include the first nested fixture-launch stack fault, the stale
reader's incorrect EBADF oracle, a nested stale-worker fixture stack fault, the
three default-profile Cleaned link rejections, and the stale 22-test local oracle
after adding three passing core tests. Fixture preparation/reuse now runs in the
caller, the errno expectation matches the enforcing kernel, and the required
core count is 25. No failed attempt is counted as acceptance.

The provider is still disposed by fixture cleanup; it has not traversed policy
Terminal/Cleaned after dependent Cleaned. Next BG-057/BG-058: complete that
two-service teardown and preserve both histories. Then address fixed storage
retirement/reuse under BG-060. Recovery (BG-033), independent review and new-profile
catalog audit support (BG-056) remain separate. No current kernel blocker.

[Retained evidence](../evidence/issued-reclaim-cleaned-2026-09-07/README.md).

Technical review: full owner/token matches gate invocation; one started flag
prevents duplicate calls even after failure. Each raw return is stored before
interpretation, and local counters follow only kernel success. Cleaned verifies
retired Terminal identity and exact acknowledged occurrence before reservation;
Unknown is set before policy mutation and cannot reopen on failed verification.
The LTO exception is case-specific and actually target-tested. No independent
review is claimed. Documentation impact: adapter, native storage/coverage, CLI
compiler profile, standards disposition, quality records and work tracking.
