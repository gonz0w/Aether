# Musl 1.2.6 process and descriptor paths (UL-035)

This source audit follows the dash 0.5.13.5 imports in
[DASH-0.5.13.5.md](DASH-0.5.13.5.md). The source is the pinned musl archive with
SHA256 `d585fd3b613c66151fc3249e8ed44f77020cb5e6c1e635a616d3f9f82460512a`.
The witness extracts a fresh copy after digest verification and records exact
file hashes in [evidence](../evidence/process-reference-2026-09-05/evidence.json).
All paths below refer to that archive. These are consumer findings, not new
accepted cross-project standards or implementation assignments.

## Process entry and state

`src/process/fork.c` calls the atfork hook, blocks application signals, conditionally
acquires libc locks, invokes `_Fork`, repairs child state and restores masks.
The multithreaded branch handles loader/key/AIO/allocator/thread-list state;
these branches are outside the single-threaded witness.

`src/process/_Fork.c` blocks all signals, locks the abort lock, and on x86-64
calls SYS_fork. The SYS_clone(SIGCHLD, 0) path is the alternative for architectures
without SYS_fork; it is not the selected x86-64 source path. In the child,
`__post_Fork` calls set_tid_address, resets robust-list and thread-list fields,
and records the returned thread ID. A native implementation must support the
child's TLS/state transition and actual identities before this path is usable.

`src/signal/block.c` does not check the return from mask block/restore operations.
Returning ENOSYS for signal masking is therefore not enough to make ordinary
fork fail safely. Native adoption must implement the required behavior or
introduce a reviewed checked adaptation. No such patch is applied here.

`src/process/x86_64/vfork.s` is a separate assembly entry, containing a literal
Linux operation 58. It removes and restores the return address around the
operation and passes the result through __syscall_ret. Adapting only inline C
syscalls misses this path. Dash has both forkshell and vforkexec call sites;
launching a fresh fixed worker is not a substitute for copied shell state.
The nine-case witness exercises vfork/_exit/wait only; it does not establish its
shared-memory or suspension behavior, nor approve replacing vfork with fork.

`src/process/execve.c` calls the public syscall wrapper. Successful replacement
must not return; failure returns -1/errno with the caller still runnable.
The witness tests ENOENT/EACCES preservation and a real Linux exec into an
explicit emulator invocation. Dash's ENOEXEC retry through /bin/sh remains
separate, untested scope.

## Wait and cancellation

Dash's selected configuration imports `wait3`: `src/linux/wait3.c` calls
wait4(-1, ...), and `src/linux/wait4.c` reaches __sys_wait4. On x86-64,
`src/internal/syscall.h` maps that to a raw SYS_wait4 call.
`src/process/waitpid.c`, used by the new witness, instead uses sys_wait4_cp,
the cancellation-point path. They share the underlying operation but are not
identical libc wrappers. The earlier dash cases exercised wait3; this witness
adds specific-child status and repeated-reap ECHILD through waitpid.

`src/thread/__syscall_cp.c` has a weak non-cancelling implementation; threaded
link closure can select the cancellation machinery, including the separate
x86-64 syscall_cp assembly entry. No threaded cancellation result follows here.
SIGCHLD, blocking/wakeup, WNOHANG and interrupted waits require an explicit
native contract; this witness does not test wait interruption or scheduling races.

## Descriptors and failure assumptions

| Pinned source | Observed behavior | Adoption implication |
| --- | --- | --- |
| src/fcntl/fcntl.c | F_DUPFD_CLOEXEC first attempts the native operation; on success additionally sets FD_CLOEXEC without checking that setter | Atomic duplication must already establish the flag; do not rely on the unchecked extra setter |
| src/fcntl/fcntl.c | EINVAL triggers a probe to distinguish an invalid minimum FD from an unsupported operation; fallback uses F_DUPFD then an unchecked F_SETFD | A transport with duplication but denied/unsupported F_SETFD can expose an inheritable FD while reporting success; exercise and reject that path before adoption |
| src/unistd/pipe.c | x86-64 uses SYS_pipe | Buffer publication and both descriptor allocations need failure cleanup; the EMFILE witness covers a one-free-slot case |
| src/unistd/pipe2.c | ENOSYS fallback uses pipe, then unchecked F_SETFD/F_SETFL calls for CLOEXEC/NONBLOCK | Unsupported setter behavior must not silently weaken requested flags; atomicity/races are separate from single-thread error handling |
| src/unistd/dup2.c | x86-64 retries EBUSY and normalizes the final result | Native replacement, old==new, invalid-FD and shared-open-file semantics need specific tests; an endlessly returned EBUSY would loop |
| src/unistd/close.c | Runs the AIO hook and cancellation-point close; translates EINTR to success | Native close must have consumed the handle if this mapping is retained; otherwise a checked adaptation is needed |
| src/fcntl/open.c | Uses syscall_cp/open mapping, mode flags and large-file conventions | Imported open remains a path/authority boundary, not merely an integer-FD constructor |

These are source assumptions, not verified vulnerabilities in Linux or claims
that current Aether exposes these operations. In particular, errno choices can
activate fallback paths; simply returning honest unsupported errors at the
transport boundary does not guarantee the enclosing libc function fails.

The [nine-case witness](../../experiments/process-reference/README.md) exercises
copied program state, shared offsets/status flags versus descriptor flags,
exec inheritance/failure, child reaping, pipe lifetime and real FD exhaustion.
Three controls reject altered sharing/inheritance/lifetime. It does not exercise
the fallback setter denials described above.

## Follow-on and ownership

UL-035 is complete for this pinned source audit and bounded reference witness.
UL-036 completed [twenty fallback-error comparisons](../../experiments/descriptor-fallback/README.md)
with explicit injection. The checked adaptation remains experimental; UL-037
consolidates the findings into a shared owner-review proposal. Signal-mask and
close/EINTR assumptions remain open UL-003/015 gates. UL-007 still needs
owner-assigned native process/VFS/pipe support; UL-008 covers TTY/session behavior.
Shared requirements or ABI decisions belong in Aether-standards with affected
owners. No shared release/pin or sibling implementation changed in this work.
