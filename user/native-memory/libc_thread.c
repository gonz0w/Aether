/* SPDX-License-Identifier: BSD-2-Clause */
/* Bounded consumer witness using private headers from the pinned musl archive.
 * This initializes only the fields needed by the selected operations. It is not
 * pthread_create and never registers a thread in libc's global thread list. */
#include "pthread_impl.h"
#include <stdio.h>

static _Thread_local volatile unsigned cookie = 0x2468;

unsigned long libc_child_prepare(unsigned long base, unsigned long bytes,
                                 unsigned id)
{
    if (libc.tls_size > bytes)
        return 0;
    pthread_t parent = __pthread_self();
    pthread_t child = __copy_tls((unsigned char *)base);
    child->self = child;
#ifdef LIBC_BAD_SELF
    child->self = parent;
#endif
    child->locale = parent->locale;
    child->canary = parent->canary;
    child->sysinfo = parent->sysinfo;
    child->tid = (int)id;
    return (unsigned long)child;
}

int libc_child_check(unsigned long fs, unsigned id, int initial)
{
    char text[32];
    if ((unsigned long)pthread_self() != fs ||
        __pthread_self()->tid != (int)id ||
        cookie != (initial ? 0x2468u : id) || (!initial && errno != (int)id))
        return 0;
    cookie = id;
    errno = (int)id;
    int length = snprintf(text, sizeof text, "%u", id);
    return length == 1 && text[0] == (char)('0' + id) && text[1] == 0;
}

int libc_parent_check(void) { return cookie == 0x2468 && errno == 71; }

void libc_parent_prepare(void) { errno = 71; }

#ifdef LIBC_WAIT
#include "adapter.h"
static unsigned long wait_cap;
static _Atomic unsigned waits_entered, wakes_entered;
#ifdef LIBC_LOCK
#include "lock.h"
static volatile int internal_lock;
static unsigned protected_value;
#else
static volatile int waiters;
#endif
static long last_wake;

long aether_wait_syscall(long n, long address, long op, long value,
                         long timeout, long extra, long tail)
{
    if (n != SYS_futex || timeout || extra || tail)
        return -ENOSYS;
    if (op == (FUTEX_WAIT | FUTEX_PRIVATE)) {
        if ((long)(int)value != value && (unsigned long)value > 0xfffffffful)
            return -ENOSYS;
        ++waits_entered;
        return memtrap(0x28008, wait_cap, (unsigned long)address,
                       (unsigned)value, 0);
    }
    if (op == (FUTEX_WAKE | FUTEX_PRIVATE) && value == 1) {
        ++wakes_entered;
#ifdef LIBC_DROP_WAKE
        last_wake = 0;
#else
        last_wake = memtrap(0x28004, wait_cap, (unsigned long)address, 0, 0);
#endif
        return last_wake;
    }
    return -ENOSYS;
}
int libc_wait_prepare(unsigned long cap, unsigned long key)
{
    wait_cap = cap ^ 3;
    if (aether_wait_syscall(SYS_futex, key, FUTEX_WAIT | FUTEX_PRIVATE, 1, 0, 0,
                            0) != -EACCES)
        return 0;
    wait_cap = cap;
    if (aether_wait_syscall(SYS_futex, key + 1, FUTEX_WAIT | FUTEX_PRIVATE, 0,
                            0, 0, 0) != -EINVAL ||
        aether_wait_syscall(SYS_futex, 0xdead0000, FUTEX_WAIT | FUTEX_PRIVATE,
                            0, 0, 0, 0) != -EFAULT ||
        aether_wait_syscall(SYS_futex, key, FUTEX_WAIT | FUTEX_PRIVATE, -1, 0,
                            0, 0) != -EAGAIN)
        return 0;
    int ready =
        aether_wait_syscall(SYS_futex, key, FUTEX_WAIT, 0, 0, 0, 0) ==
            -ENOSYS &&
        aether_wait_syscall(SYS_futex, key, FUTEX_WAIT | FUTEX_PRIVATE, 0, 1, 0,
                            0) == -ENOSYS &&
        aether_wait_syscall(SYS_futex, key, FUTEX_WAKE | FUTEX_PRIVATE, 2, 0, 0,
                            0) == -ENOSYS &&
        aether_wait_syscall(SYS_rt_sigprocmask, 0, 0, 0, 0, 0, 0) == -ENOSYS;
#ifdef LIBC_LOCK
    if (!ready)
        return 0;
    libc.need_locks = 1;
#ifdef LIBC_SKIP_LOCK
    libc.need_locks = 0;
#endif
    __lock(&internal_lock);
    protected_value = 1;
#endif
    return ready;
}
int libc_wait_child(unsigned long key)
{
#ifdef LIBC_LOCK
    (void)key;
    __lock(&internal_lock);
    int valid = protected_value == 1;
    protected_value = 2;
    __unlock(&internal_lock);
    return valid ? 0 : -1;
#else
    __wait((volatile int *)key, &waiters, 0, 1);
    return *(volatile int *)key == 1 ? 0 : -1;
#endif
}
long libc_wait_wake(unsigned long key)
{
#ifdef LIBC_LOCK
    (void)key;
    __unlock(&internal_lock);
#else
    __wake((volatile int *)key, 1, 1);
#endif
    return last_wake;
}
int libc_wait_check(void)
{
#ifdef LIBC_LOCK
    return waits_entered > 0 && wakes_entered == 1 && internal_lock == 0 &&
           protected_value == 2;
#else
    return waits_entered > 0 && wakes_entered == 1 && waiters == 0;
#endif
}
#endif
