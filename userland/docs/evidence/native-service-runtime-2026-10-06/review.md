# UL-003/015/081 maintained service-runtime candidate

Before code,2026-10-06. Aether engine-entry gate needs a userland-owned exact
SDK/backend/tool lock, not its private probe definitions. Build a separate opt-in
bounded static service runtime atop the pinned guarded musl SDK. Keep the base
archive/default pins intact; publish a supplemental archive and explicit grouped
link recipe. No kernel, sibling, service policy, filesystem or package edits.

Source directions: qualified native descriptor96, owner word waits/count wakes/
requeue, held-grant stop/retire, actual musl upstream create/exit/join/TSD and
real-time backend. Extract mechanism, never test main/TSD observations, witness
barriers or magic successful control values. Pthread admission supports bounded
normal stack/guard/joinable/detached attributes; other semantics reject. Count one
ordinary joinable reaper against82/two worker capacity. Reaper handles detached
requests while callers block, confirms stop before unmap/retire, never reads an
unmapped TCB. Upstream list lock serializes record publication/reuse; atomics
publish pending/permission and usage. Join saves metadata, waits upstream, then
confirms stopped and retires before reuse. Dynamic lifecycle is new work requiring
fresh tests, not inherited private producer acceptance. Cancellation/dynamic detach,
realtime UTC/signals/robust/priority/scheduling attributes remain unsupported.

Init explicitly obtains and checks native grants, one reaper is visible in counts.
Shutdown closes admission, denies outstanding joinable ownership, drains detached
requests, joins/retires reaper, and reports only confirmed cleanup. Native errors
stay errors. Failure/uncertain retirement poisons admission; no silent recovery.
Absolute timespec conversion is checked; monotonic/native waits retain deadlines.
No kernel/no-SDK success claims for unsupported semantics or new public conformance.

Test plan: independently authored app using delivery headers and archives only;
join/TLS/TSD, worker-origin concurrent create, detached cleanup while primary joins,
creation/reuse cycles, contention/condition timed wait/spurious/broadcast/relock,
200ms relative/absolute sleeps, invalid/realtime/cancel/detach/attr failures,
shutdown busy/final accounting. Native disabled-clock and early-completion exact
controls. Pin SDK6458-entry manifest before consumption, source/tool/flags/ABI,
firmware/kernel inputs and all results. Use QEMU one CPU, fresh owned paths under
build, bounded builds/guests/groups and complete cleanup. Focused tests plus local
quality/C-format/minimum/current Python checks; broader integration at handoff.
Keep compact receipts/logs and the sealed candidate; no new whole-run archives.
Missing native cases or reader/owner acceptance remain incomplete.

SE questions: a probe-object SDK would be shorter but carries test entry/policy and
would not supply a reusable backend. A supplemental runtime avoids rebuilding or
silently promoting the base SDK while exposing the exact link boundary. No active
path is removed; this step replaces test-only composition for selected consumers.
Foundations O/I/E, TD/TC/TE, CC/CP apply. BSD-2 original/imported Aether mechanisms;
upstream musl terms remain. Actual agent technical review and independent human/
owner acceptance must be recorded separately after testing; no approval invented.


## Actual technical review and disposition

Codex reviewed native trap clobbers, explicit grant selectors, descriptor size,
publication/pending atomics, upstream list-lock serialization, saved metadata after
unmap, live versus lifetime counts, admission rollback, reaper slot cost and fail-
stop paths. Reaper never dereferences a retired TCB; a slot is released only after
confirmed native retirement. API requires serialized initial-thread init/finish;
concurrent initialization and handle use after join are outside this private
contract. Finish closes admission even on EBUSY, then requires caller collection
and retry; it does not implement service policy. Admission checks run before
upstream thread-mode mutation and kernel creation rechecks the bounded records.

Review caught an unobservable detached-child result in the independent test;
final code traps that assertion and checks exact retained115/three admissions.
The provisional four-VM checkpoint/12 app lifetimes, full-capacity rejection, contended broadcast,
long-wait segmentation,16 blocked-primary detached cycles and shutdown pass.
Source/SDK/output denials and trace mutation controls run on actual minimum/current
Python; their runtime archives are identical. Copied sealed-source reproduction
is checked separately from native execution. Compiler suppressions are confined
to preserved upstream files; original C uses strict diagnostics and formatting.
No host sanitizer claim is made for native trap/FS/TLS code; bounded native
isolation, semantic failures and confirmed reclamation provide scoped evidence.

Independent Aether owner intake/actual-engine entry and human reader review are
were pending at that checkpoint.512-admission exhaustion, broader interruption/malformed/concurrent
schedules, realtime/signals/cancellation, general synchronization, identity/
configuration/resource/entropy/storage and full engine/helper/ARC life remain
open. No wholesale POSIX, security, recovery/performance or release claim. The
source/runtime complexity replaces test-only composition for selected consumers;
no existing default paths were removed. Applicable canonical docs and the draft
coverage entry were updated; no shared standard, consumer pin or sibling changed.

Final extension: five fresh VMs/15 successful app lifetimes now include all512
lifetime admissions per owner and exact unchanged513th rejection. Review adds
saved original-detach metadata before upstream join, explicit try/timed join
denials, unchanged unsupported synchronization initialization and operation-entry
guards. The native robust setter's existing ENOSYS is separately asserted.
The early-control test uses2s requests to observe dishonest completion before
expiry; the original legitimately late observation/failure is retained. Both
interpreters pass seven input/output/usage controls, three actual CLI checks and
60 corruptions. CLI control characters escape, streams/exits stay plain; no
renderer/whole-project Experience conformance claim. Broader schedules and owner/
reader acceptance remain pending;512 exhaustion is no longer a missing case.
