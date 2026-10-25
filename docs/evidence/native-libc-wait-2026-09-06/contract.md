 — 2026-09-06

Before implementation: source-rebuild musl 1.2.6 __wait unchanged from the verified
archive and use its real inline __wake through a fixture-only syscall transport.
This is the blocking loop used by libc's thread-list synchronization; it is not
pthread_create/join or a general Linux syscall layer. The existing native thread
grant owns access. No kernel, sibling, shared standard or immutable pin changes.

The adapter accepts only SYS_futex with FUTEX_WAIT_PRIVATE, a u32/int32 expected
value and null timeout, or FUTEX_WAKE_PRIVATE with count=1. Extra arguments must
be zero. Unsupported calls, shared futexes, other counts/flags and timed waits
return -ENOSYS, not successful no-ops. Translate wait to 0x28008 and wake to 0x28004
using the supplied domain-local thread grant. In the current two-context domain,
the calling waker leaves at most one other context blocked; wake-all therefore
implements this narrowly selected count-one case. This argument does not extend
to larger thread pools. Native pointer/authority/comparison errors are preserved.

Keep the upstream __wait source and original private-header hashes/notices; replace
only the disposable build's syscall_arch.h with a first-party adapter and retain
both header identities. Link the rebuilt __wait object ahead of the supplied libc
archive. Original C uses pinned formatting and -Wall -Wextra -Werror. Upstream
source formatting is preserved. The adapter stores only the fixture's existing
grant, not a new authority or global kernel registry. Shared counters use atomics.

Select --libc-wait in the existing thread harness: actual child __wait registration
must be observed blocked before the parent's inline __wake. Check positive syscall
counts, waiter-count cleanup, real libc TLS/errno, aliasing, guard fault and domain
stop/replacement. Retain wrong-self-pointer and pin controls; a dropped wake must
reject at the exact parent assertion, not timeout. Reject unsupported transport
requests explicitly before starting the child. Run both memory profiles and older
thread suites plus host/format checks on frozen inputs; retain every attempt.
No signal, cancellation, robust/process-shared futex, timed futex, thread-list
publication or general pthread acceptance is implied. Document the optional suite.
