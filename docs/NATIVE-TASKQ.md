# Bounded native taskq bridge contract

Status: **bounded native runtime qualified**, 2026-09-07.
The header/platform module and paired fixture now link as a native executable.
The seven hooks use existing scoped grants; no new syscall is introduced. Existing
[NATIVE-C](NATIVE-C.md) grants and limits remain authoritative. This is Aether's
kernel-conformance fixture contract, not production libc adoption or a shared
standard. Aether-userland retains production runtime ownership; a Rust service
will own filesystem policy. Shared normative changes still belong in
Aether-standards. Immutable pins and sibling repositories are unchanged.

## Requirement and exclusions

Execute the retained upstream libzpool taskq algorithm with a parent and two
native child workers, using actual musl synchronization/TSD and existing scoped
memory/thread grants. Preserve separate progress queues A/B, nonblocking entry
failure, whole-queue drain and explicit unsupported operations. Two generations
consume exactly the current four lifetime child admissions. There is no extra
drainer pthread, capacity increase, global kernel taskq object, host syscall
forwarding, general CPU topology API or full engine startup.

The [Linux witness](evidence/openzfs-taskq-drain-2026-09-06/README.md) establishes
algorithm behavior only. Its 68 system workers and third helper thread cannot be
copied into this native fixture. The [object review](evidence/native-taskq-contract-2026-09-06/README.md)
classifies all 27 imports of the retained Linux object; it is not native binary or
transitive symbol closure. The [native object evidence](evidence/native-taskq-build-2026-09-06/README.md)
now verifies headers, compilation, layout and relocatable linking. Queue/entry
sizes are 384/40 bytes. Executable closure and runtime controls remain required.

## Source and TSD bootstrap

Retain OpenZFS 2.4.4 commit 71a9f9578616a90c3c14bb59629fb4d31bfd68d1, its original
archive and CDDL notices. Build a private copy of lib/libzpool/taskq.c against a
small taskq-specific platform header using actual pinned musl pthread types.
Never link the Linux object, copy glibc pthread layouts, import all kernel.c
platform behavior, or replace the taskq algorithm with a lookalike implementation.
Copied/derived upstream definitions retain upstream terms; original bridge code
uses BSD-2-Clause. Record original and adapted source/header digests separately.

The first allowed source adaptation is two fixture-only helpers in the taskq
translation unit that create/delete its private taskq_tsd key independently of
system_taskq_init/fini. Appending an explicitly recorded helper fragment preserves
the original source prefix and avoids changing the default 64+4 startup behavior.
This is a derived translation unit, not a claim of unmodified compilation. Do not
call system_taskq_init, assume key zero is valid, rename private symbols via a
binary hack, or silently lower engine defaults. Helper declarations stay private;
these are not new standardized OpenZFS or native kernel APIs.

The parent initializes TSD once before queues or workers exist. It finalizes TSD
only after both generations have been destroyed and all child IDs confirmed
stopped and reaped. Double initialization/finalization and teardown while workers
or queues remain are fixture errors. The parent owns this state transition; keys
are not capability handles and never authorize kernel operations.

## Memory, failure and object ownership

Before workers start, reserve one 4096-byte arena through the existing domain
memory grant. Use eight 512-byte, suitably aligned slots and separate private
allocation metadata. This is a proposed fixture bound: native compile-time layout
checks must prove each queue object fits a slot and the exact live-object budget
fits eight slots before the experiment runs. If it does not fit, stop and revise
the contract with measured sizes; do not silently enlarge it.

Two queues, two worker-pointer lists and at most three allocated work entries
require seven slots in the selected workload. The spare slot supports deliberate
exhaustion/reuse controls. The arena excludes musl stack/TLS allocations, which
remain on the qualified mapping adapter and are counted by the domain quota.
It is not a whole-engine heap budget. Map taskq's kmem macros to this allocator;
do not interpose global musl malloc/free and accidentally route TLS through it.

Allocation is serialized with a real mutex, validates size/alignment before
mutation and zeroes reused storage. Free validates exact base, live slot and
original allocation size, scrubs the slot, then makes it reusable. No realloc,
coalescing, dynamic arena growth or borrowing another domain's memory is needed.
Objects remain private to one domain; the parent owns queue lifetime, while
upstream mutexes protect queued entries shared with its children.

TQ_NOSLEEP exhaustion returns NULL/dispatch zero without mutation. Upstream
KM_SLEEP object allocations must either succeed within the reserved arena or
terminate the fixture domain with an exact failure status; never return NULL to
an unchecked caller or fabricate successful storage. Parent preflight reserves
normal-case capacity before publishing workers. Required-allocation failure is
not recoverable in this first bridge: supervisor stop/reclaim must prove that
remaining children and mappings are cleaned before replacement.

Reject sleeping dispatch and unsupported flag combinations before entering the
algorithm. Source task_alloc can exceed maxalloc after a timed throttle for
TQ_SLEEP; it cannot implement a hard capability budget. Prepopulation,
CPU-percentage/dynamic/synced queue modes and arbitrary worker counts are outside
the first fixture. Only explicit one-worker A/B, minalloc=0, maxalloc=2/1 and
flags=0 are admitted. Internal required object allocations remain distinguished
from public sleeping dispatch.

## Synchronization and platform imports

| Retained object imports | Native binding and required checks |
| --- | --- |
| malloc/calloc/free | These arise from retained kmem/umem macros; native taskq-only macros must instead bind the bounded allocator above, preserving allocation flags. No global libc allocator override. |
| mutex_init/enter/exit/destroy | Actual musl normal mutexes plus correct owner tracking; reject unsupported initialization modes. No no-op lock path. |
| rw_init/enter/exit/destroy | Actual musl rwlocks with native pthread types and explicit reader/owner bookkeeping. Preserve lock semantics even though this fixture only exercises taskq reader acquisition. |
| cv_init/wait/signal/broadcast/destroy | Actual musl private conditions with mutex-owner bookkeeping released/restored around wait. Preserve atomic unlock/wait and reacquisition. |
| cv_timedwait | The sleeping dispatch path is forbidden. Reaching this function must fail explicitly, not report a fake timeout or success. Timed allocation is a later contract. |
| clock_gettime | Reuse only the existing declared virtual-monotonic adapter if retained native link paths need it; unsupported clock identities fail. No Linux realtime or calibration claim. Reaching forbidden throttle logic still fails. |
| pthread_key_create/delete/get/setspecific | Actual pinned musl key routines; the explicit TSD bootstrap/lifetime above applies. |
| zk_thread_create / pthread_exit | Two fixed parent-owned startup records, actual detached musl create/exit and the qualified native exit/reaper path. Stack/guard bounds stay within NATIVE-C; select 128 KiB plus one guard page for this fixture. |
| strlcpy | Pinned libc bounded copy for trusted fixed queue names; validate fit, never silently alias truncated names. |
| sysconf | Only the fixture's explicitly declared one-core online-CPU view is allowed if referenced. Other requests reject; no host resource discovery. Queue CPU-scaling flags remain forbidden. |
| libspl_assertf | Preserve failing invariant as exact fixture/domain failure. Never suppress assertions or continue with corrupted state; keep existing native panic/test marker contracts. |

These bindings are implemented in the bounded platform/fixture modules. The native
link must enumerate every unresolved reference after compiling the adapted unit
and platform bridge. New imports require review; a Linux object inventory does
not establish closure through musl or the native adapter. Keep function/type
signatures, pointer bounds, no-unwind behavior and header provenance explicit.

## Native worker and queue lifetime

Create children only through the existing domain thread grant and validated
stack/TLS descriptors. Upstream queue membership may use its live pthread token;
that token is not a native capability. Parent reaper records independently save
the exact native ID and mapping base/length before the worker can depart.

The order is: finish callbacks and drain queues; destroy upstream queue objects;
observe each exact native child ID stopped; unmap its saved stack/TLS through the
memory grant; retire its ID; only then reuse backing/startup records for the next
generation. The departing child publishes a request and exits through 0x28001,
without unmapping its executing stack. A queue's zero nthreads or destroy return
is not stop confirmation. Reaping must never dereference the departed pthread_t
or the freed queue/thread-list storage. Retain the current early-unmap denial and
clear-TID/list-unlock controls. Delete taskq TSD only after all reaping completes.

## Executable acceptance plan

Use the existing paired pthread-lifecycle harness, both default and large memory
profiles, plus supervisor replacement. Add no new launch ABI. Port only the
fixture adapter needed for this experiment; do not mix unrelated pthread tests
or production service policy into the platform header.

1. Prove original-source prefix/helper identity, native layouts, object-slot budget
   and actual native link closure before boot. Reject unknown imports and size
   overflow, rather than changing limits to make compilation pass.
2. Bootstrap TSD and reserve the arena. Create A/B with one detached worker each.
   Verify actual owner TSD and denied third-worker admission without allocation.
3. A dispatches B and waits. B yields until the parent's instrumented A-condition
   wait has been entered, then finishes. A's queued tail also finishes before the
   parent drain returns. This replaces the Linux helper pthread, not the real
   wait. Instrumentation must distinguish the parent and exact watched condition;
   bounded yields and native watchdog failures are not accepted negative results.
4. Verify duplicate constant task IDs, whole-queue completion, nonblocking entry
   rejection without state mutation, delayed-dispatch zero/no callback, explicit
   unsupported cancel result and entry reuse. Never expose stronger per-ID rights.
5. Destroy, observe stop and reap both children; verify quota and arena restoration.
   Repeat once (four total child admissions), then finalize TSD and unmap the arena.
6. Deliberate premature drain, false delayed success, allocator exhaustion/required
   allocation failure, invalid free and premature reaping must fail at their exact
   named oracles. Supervisor replacement must recover all-child resources on
   fatal paths. Preserve existing full lifecycle regressions and source freeze.

The bounded target cases below now pass in both profiles, including supervisor
replacement and exact failure controls. Independent production consumer acceptance
and full-engine resource sizing remain **missing coverage**, not waived.
`zig build test` alone does not qualify runtime behavior. Do not select
full-engine capacity without live thread/stack/allocator measurements and a wider
queue-dependency review.

## Native integration and invocation

`user/native-taskq/fixture.inc` is included only in the taskq mode of the shared
conformance adapter. It binds parent authority, arena map/unmap, actual detached
worker creation, saved-ID reaping, exact wait observation and fatal domain exit.
The other lifecycle test bodies are excluded from this mode. No policy moves
into the kernel. The musl pthread_create, keys, rwlock and condition routines
are rebuilt through the existing restricted syscall adapter.

Run the extended lifecycle suite from the repository root (repeat with `--large`):

```sh
python3 scripts/thread_smoke.py --pthread-lifecycle \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock /Users/cam/DEV/Aether-userland/experiments/musl-reference/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The SDK is an explicit read-only local producer input; receipts bind its archive,
compiler and source identities. The build retains the original taskq source and
appended version plus hashes of the private module. Full suite snapshots now
include `user/native-taskq`. Existing output markers remain unchanged. Runtime
results and failed attempts belong in the [integration evidence](evidence/native-taskq-runtime-2026-09-07/README.md).

Taskq controls use exact terminals: 328 premature drain, 329 false delayed
success, 303 invalid free, 302 required allocation exhaustion, 312 early unmap.
Other statuses 308–335 identify authority, startup, reaping, callback, resource
or bounded-progress failures and are not accepted negative results. Fatal exit
terminates the whole fixture domain. The allocation-failure supervisor expects
that exact failure again after replacement; it proves teardown and re-admission,
not recovery of the interrupted task's application state.

Final [runtime qualification](evidence/native-taskq-runtime-2026-09-07/README.md)
passes 92 lifecycle cases (46 per profile, eight taskq cases each), plus 98 Python
tests and Zig checks. Kernel inputs and resource limits remain unchanged.
