# Musl service retirement and thread-specific data

Before-code scope,2026-10-05. R1-03 needs the actual engine's detached worker and
TSD behavior beyond the qualified82 joinable-worker trial. Aether owns this private
producer witness; production musl/runtime remains Aether-userland-owned. Existing
VM/musl/signal/clock/resource ownership designs remain authoritative. No new
kernel operation, public SDK, ABI, quota, sibling or released pin change.

Requirement: actual pinned musl1.2.6 keys/destructors with82 live service workers
and two small-peer workers; detached cleanup must follow confirmed native exit.
Native grants remain caller/owner-bound. Test each per-thread value/destructor,
repeated destructor assignment, deleted/recreated key isolation, parent state and
exact eager stack/TLS mapping accounting. Retain old joinable behavior and qualify
both ordinary retirement and stop/replacement with workers parked.

Borrow the existing bounded detached __unmapself/request/reaper seam. A detached
worker finishes upstream TLS destructors and list removal, publishes its saved
mapping/ID cleanup request, then waits for primary permission to perform native
exit. The primary permits exit, observes the exact ID stopped, then unmaps and
retires, never dereferencing the unmapped TCB. It must process requests individually:
waiting for every pending request would deadlock because musl retains its global
thread-list lock until native clear-TID. Mapping cleanup admission still occurs at
the kernel, not a user-local counter. This primary-driven fixture is not a complete
engine runtime: reaping during a blocked creator and worker-origin concurrent
creation need separate supported contracts before engine execution.

Untrusted application pointers, IDs or claimed cleanup cannot authorize reuse.
Pending request is not stopped. Omit the stop observation in a deliberate control:
actual unmap of the still-running requester must reject EACCES before reuse.
Omit the actual upstream destructor traversal in another control: exact recorded
destructor checks must reject; timeout/unrelated panic cannot pass either control.
Cancellation and detached transition by pthread_detach remain unsupported. No
ordinary join/detach wrapper may fabricate success.

Slots/requests remain bounded and owner-local, acquired by one primary. Callback
state remains valid through native stop; saved mapping/ID survive unmapping without
TCB dereference. Release/list/TID ordering uses pinned upstream functions and
existing native compare-wait/wake/exit/observe/retire. No cross-core behavior,
calibrated time, signal/thread cancellation or production TCB ABI is promised.

Tests: joinable TSD, detached TSD/reclamation, parked detached stop/replacement,
actual missing-destructor and early-unmap controls. Retain all failed attempts and
source/tool/SDK/artifact identities, fixed180-second build/30-second guest bounds,
full host/pins/workflow and scoped formatting/link checks. Older runtime suites
may bind byte-identical kernel/maintained-source inputs as historical coverage,
never fresh runs. Documentation impact: reference, workflow, STATE and roadmap.

Simplicity: existing primary-driven cleanup is the smallest adequate experiment;
new kernel self-unmap/reaper services or generalized VM changes are unnecessary
for measuring this bound. Bare cookies and joinable-only tests cannot cover real
TSD or detached cleanup. Reuse upstream functions and known native primitives;
none of the production paths is removed now. Do not promote this fixture into the
engine backend until blocked-creator/progress and actual feature closure qualify.

Before final ordering extension: the first five cases pass, but code review found
that ascending-slot reaping depended on the current completion schedule. Select
any pending request, preserving exact confirmed-stop/unmap/retire checks. Add an
actual reverse-order exit gate; all82/two workers must retire in descending order.
This is a test scheduling gate, not production cleanup policy or a new wait API.
