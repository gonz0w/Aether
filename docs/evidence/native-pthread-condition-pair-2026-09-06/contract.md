# Multiple musl condition waiters

Aether owns this bounded conformance adapter; userland owns production libc.
Use existing two-child native grants and four-admission budget, no new kernel ABI.
Two actual musl pthreads wait on one private condition and normal mutex. First
batch signals one eligible waiter then the other; second broadcasts to both.
Observe both wait registrations before notification, mutex reacquisition blocking,
actual private requeue, joins, empty condition/mutex/thread records and full quota.
Reuse the objects across batches and supervised generations.

Only the new paired-condition fixture accepts private FUTEX_REQUEUE (wake zero,
move one, no sixth argument), preserving native pointer/count checks. Private
wake uses bounded wake count. Existing single-child and concurrent-only adapters
stay unchanged. Reject shared requeue, unsupported counts and reserved inputs.
No cancellation, timeout, process-shared condition or production pthread claim.

A deliberately substituted wake must complete but fail the exact missing-requeue
witness. Extend existing --pthread-lifecycle suite, both backing sizes, including
supervised replacement; retain all older cases. Run host/workflow checks and
Clang 21.1.8 reviewed formatting on the changed C file. Freeze runtime inputs for
qualification and retain failures. Kernel identity is unchanged from the memory
audit; its memory/pair/M4 evidence remains applicable.
