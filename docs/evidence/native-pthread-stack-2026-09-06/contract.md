
## Bounded pthread stack-attribute contract — 2026-09-06

Before implementation: extend the existing lifecycle conformance adapter to accept
initialized, joinable musl attributes with page-aligned stack sizes from 128 KiB
through 256 KiB inclusive and exactly 4096 guard bytes. NULL retains the default
path. Reject other sizes/alignment, guards, caller-owned stacks, detach, scheduling
policy/priority and nonzero reserved fields with ENOTSUP before libc state changes
or allocation. Explicitly reject the internal C11 sentinel without dereferencing
it. Caller supplies a valid pthread_attr_t object; this is not a kernel pointer
validation interface. Existing kernel grants, one-child lifetime limit and source
patch remain unchanged. Userland owns production adoption; no sibling/pin changes.

Use actual libc pthread_attr_init/setstacksize/setguardsize to construct the
accepted request. Compare against the canonical initialized attribute representation
after rejecting unsupported fields, including reserved bytes. The stack and TLS
remain allocated by upstream pthread_create and admitted/pinned by native clone.
Reject unsupported attributes with unchanged output, errno, list/count/mask/quota.
For the explicit 256 KiB case, first reserve backing to leave only 32 free pages:
actual creation must fail with EAGAIN, publish nothing and leave that quota intact.
Release the reservation, retry successfully, touch/check 240 KiB of child stack
across yields and recover full backing after join. No used-slot reuse is introduced
by retrying a creation that never published a child.

Extend --pthread-lifecycle in both profiles with explicit-stack, its supervised
replacement and guard-fault cases, retaining all five older lifecycle cases. The
guard case must fault at vector 14 in one actual pthread and permit peer completion;
no timeout substitutes. Check reported stack and guard geometry and live mapping
pins before releasing the child. Preserve existing machine/64-yield completion
contracts. Run all thread-family suites plus host/standards/format on frozen
sources. Kernel unchanged: reuse earlier memory/image/M4 evidence by exact hash.
Record all attempts; use the existing pinned C formatter without unrelated changes.
This qualifies stack attributes and allocation-failure recovery, not repeated
successful creation, larger pools or libzpool execution.
