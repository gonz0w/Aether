# M2 bounded task and memory lifetime

This records the original M2 acceptance scope. The running factory is now
extended by [native lifecycle v1](M4-LIFECYCLE-V1.md): a separate versioned
supervisor image, instance queries, retained factory terminal records, and
acknowledgment before the next allocation. V1 defines the current consumer ABI.

One boot-CPU resource factory owns one reusable task/address-space slot and one
8 KiB backing bundle (one immutable code page, one writable stack page). A Rust
supervisor receives the factory capability at bootstrap. The factory cannot
create arbitrary tasks, load arbitrary images, map physical addresses, or grow
its quota; it instantiates the pinned worker fixture only.

Endpoint, factory, task, and memory handles share the same caller-local table
and generation scheme. Object type is checked before object-specific rights.
Derivation remains same-object and same-holder. Invalidating a task or memory
object removes all its capabilities before that object can be reused. Factory
revocation disables future invocations through revoked handles; already-created
objects have independent lifetime and are not descendants of the factory cap.

Factory rights: allocate memory=1, create task=2. Memory rights: attach=1,
release=2. Task rights: start=1, stop/destroy=2, inspect=16. The common derive=4
and revoke=8 rights retain their meaning. Only the factory's holder can create
from its single quota. Memory cannot be released while attached to a task.
Starting a runnable or completed task again fails; a stopped task must be freshly
created. Pool and generation exhaustion fail without partial effects.

Register ABI extends the endpoint contract: 10 allocate (factory); 11 create
(factory, memory in RSI); 12 start (task); 13 inspect (task; returns 0 pending,
1 worker exit, 2 worker fault); 14 destroy task (task); 15 release memory (memory).
RAX status/RDX result follow the existing ABI. Operation 20 yields the caller's
own timeslice. Object-type mismatches return Invalid. Bad lifecycle transitions
return Busy. Creation preflights both capability slots and physical quota.

Teardown runs with interrupts disabled on this single CPU:
1. Check stop authority and remove the worker from the runnable set.
2. Clear user page-table entries and saved context.
3. Reload the supervisor CR3, flushing non-global translations. PCID is disabled;
   worker pages are never global and no other CPU can run these address spaces.
4. Invalidate task capabilities and detach backing, then complete destruction.
5. Release accepts unused allocated or detached backing. Dirty detached backing
   cannot be attached to a new task until it is released and freshly allocated. Invalidate memory capabilities, zero both
   backing pages, verify zeroing, then make the one bundle available again.

The user supervisor performs repeated allocate/create/start/destroy/release
cycles. Each worker verifies clean backing, dirties its stack, then exits or
faults. Stack virtual addresses alternate between two locations. From the second
cycle onward the worker deliberately reads the preceding stack address and must
fault, after the same physical backing has been reused. This checks removal of
the old mapping in hardware, not merely a software ownership flag. A negative
image that omits zeroing must fail before the bundle becomes available again.

This is a deliberately fixed task-plus-memory contract: no independent thread
creation, arbitrary mappings, shared user pages, DMA, or remote ownership. Boot
fixtures remain reserved. Only the factory bundle is reused. General loaders,
blocking IPC, supervision policy and SMP are subsequent work. M2 completion
requires the executable evidence below; documentation alone closes nothing.

## Validation and precise limits

Nine QEMU cycles complete with seven stale-address faults, one normal exit, and
one authorized live stop. The same two physical pages and address-space slot
are reused; virtual stack addresses alternate. Full backing is checked zero in
the kernel, and workers check unused stack bytes before dirtying them. The
skip-zero negative build fails before release completion; the skip-unmap build
retains old page-table entries and fails the worker's stale-address check.

Revoking a derived handle stops future invocations through it; it does not undo
tasks/mappings already created through that handle. Attached backing stays Busy
until explicit task destruction completes. The single task contains one thread;
independent threads and arbitrary mappings have no current requirement or API.
The M2 criteria are met for this bounded experiment. Multi-core cleanup and DMA
remain outside its guarantees.
