
## Actual bounded pthread lifecycle contract — 2026-09-06

Before implementation: source-rebuild musl 1.2.6 default pthread_create/start/exit
and untimed pthread_join with real native mask, memory and wait transport. This
is a kernel conformance adapter, not production userland adoption. Kernel/ABI
bytes, sibling files and immutable pins stay unchanged. Only default attributes,
one joinable child per domain lifetime, and no asynchronous signal/cancellation
producer are supported. Reject attributes/detach/cancel and repeated creation
explicitly; do not claim POSIX threads or emulate concurrency synchronously.

Reuse the retained preflight patch with an additional fixture admission check
before libc state changes. Rebuild required mask, memory, wait/lock, syscall-CP
and join sources unchanged from the verified archive; use the same disposable
architecture-header transport. Preserve originals/notices/manifests and exact
patches. Keep existing upstream-only warning exceptions; first-party C follows
pinned Clang21 formatting and strict warnings. No lock or VM stubs are allowed.

A first-party __clone adapter accepts only musl's expected flags and translates
the writable mapping (excluding its guard) into native descriptor 0x28006, with
actual FS, parent-TID output and clear-TID=musl's thread-list lock. A C trampoline
calls upstream start. The existing kernel validates and pins all stack/TLS pages.
Native child exit clears/wakes the thread-list lock only after user execution
stops. Upstream join waits for detach-state and thread-list completion before
unmapping; no use of the released pthread handle follows. Failed clone must
publish no child or output handle and restore allocation quota/thread-list/count.

Translate anonymous mmap/mprotect/munmap via memory grant, mask operations via
thread grant, and bounded-domain futex waits/wakes via existing native operations.
Non-private futex is accepted only for the internal thread-list lock; other shared
keys, timeouts and unsupported operations return ENOSYS. Wake-all is equivalent
to wake-one only within the enforced two-context bound. Child SYS_exit becomes
thread exit, not domain exit. Cancellation and signal sending remain unsupported;
the source-rebuilt generic syscall-CP route is used without a cancellation producer.

Target selection --pthread-lifecycle in both profiles: positive and supervised
replacement, forced clone-authority rejection with exact cleanup, live-pin bypass
rejected at assertion 216, and a child fault with peer completion. Require actual
pthread_self/TID/TLS/errno, child return value through join, native child completion,
thread-list unlink/clear, caller mask restoration and full quota recovery. Delay
the child so parent join reaches a real native wait. Reject a second creation
and unsupported attributes/cancellation without output mutation. Run all older
thread suites and host/format/standards checks on frozen sources; preserve every
attempt. Kernel unchanged: broader memory/image/M4 evidence may be reused by hash.
