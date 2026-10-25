 — 2026-09-06

Before implementation: source-rebuild unchanged musl 1.2.6 __lock.c with the
existing private-futex adapter. Exercise real contention, including its signed
lock-word values and congestion/wake rules. This is an internal-libc lock witness,
not pthread_mutex, thread-list publication, pthread_create/join or signal support.
No kernel, sibling, shared standard, dependency or immutable pin changes.

In optional --libc-lock mode, enable libc.need_locks in the bounded fixture,
acquire an initially zero lock in the parent, write a protected value, and launch
the existing native child. The child must block in upstream __lock; the parent
must observe native blocked registration before calling upstream __unlock.
The child then acquires, checks/updates the protected value and unlocks. After
native join, require a zero lock word, updated protected value and observed
adapter wait/wake calls. The kernel continues to enforce the supplied thread
grant. All operations occur inside the existing two-context domain bound.

Extract __lock.c from the same verified musl archive, preserve its bytes/license,
and link its object ahead of the supplied libc. The architecture-header adaptation
is unchanged from --libc-wait. Counter/lock storage stays in the user domain;
no backing quota or global kernel state is added. Normal first-party C formatting
and warnings remain; upstream source formatting remains untouched.

Select both memory profiles with existing TLS/alias/fault/stop/pin/self-pointer/
dropped-wake checks, plus deliberate lock disabling: it must fail at assertion
286 because the child never registers as blocked, not at an external watchdog.
Run older thread suites and host/format checks on frozen inputs. Preserve every
attempt and source identity. This does not qualify all libc locks, recursive or
robust mutexes, cancellation, larger thread pools or arbitrary exit while locked.
The existing experiment-wide watchdogs remain in force.
