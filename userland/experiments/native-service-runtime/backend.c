/* SPDX-License-Identifier: BSD-2-Clause */
#include "runtime.h"
#include "adapter.h"
#include "pthread_impl.h"
#include "real_time.h"
#include <stdarg.h>
#include <stdint.h>
#include <string.h>
#include <sys/auxv.h>
#include <sys/mman.h>

static unsigned long thread_cap, memory_cap;
static unsigned capacity;
static _Atomic unsigned live, admissions, initialized, closing, stopping;
static _Atomic unsigned events;
static _Atomic int broken;
static pthread_t reaper;
struct record {
    int (*function)(void *);
    void *argument;
    _Atomic(pthread_t) thread;
    unsigned id, joining, detached;
    unsigned long base, bytes;
    _Atomic unsigned published, pending, allow_exit;
};
static struct record records[82];
struct descriptor {
    unsigned version, size;
    unsigned long entry, base, bytes, rsp, fs, tid, argument;
    unsigned long tls_base, tls_bytes, parent_tid, reserved;
};
_Static_assert(sizeof(struct descriptor) == 96, "native descriptor96");

static _Noreturn void fatal(void)
{
    broken = EIO;
    memtrap(0x10000 + SYS_exit_group, 125, 0, 0, 0);
    __builtin_trap();
}
static void yield(void) { memtrap(0x1fffe, 0, 0, 0, 0); }
static void wake(volatile unsigned *word)
{
    if (memtrap(0x2800c, thread_cap, (uintptr_t)word, INT_MAX, 0) < 0)
        fatal();
}
static void wait(volatile unsigned *word, unsigned expected)
{
    long result = memtrap(0x28008, thread_cap, (uintptr_t)word, expected, 0);
    if (result && result != -EAGAIN)
        fatal();
}
static _Noreturn void trampoline(unsigned long argument)
{
    struct record *record = (void *)argument;
    while (!record->published)
        yield();
    record->function(record->argument);
    fatal();
}
int aether_pthread_admit(const void *attr)
{
    if (!initialized || broken)
        return broken ? broken : ENOSYS;
    if (closing || admissions >= 512 || live >= capacity)
        return EAGAIN;
    if (attr == __ATTRP_C11_THREAD)
        return ENOTSUP;
    if (attr) {
        const pthread_attr_t *given = attr;
        pthread_attr_t accepted;
        pthread_attr_init(&accepted);
        if (given->_a_stacksize < 16384 ||
            given->_a_stacksize > (capacity == 82 ? 262144 : 131072) ||
            given->_a_guardsize < 4096 || given->_a_guardsize > 8192 ||
            given->_a_guardsize % 4096 || given->_a_detach > 1)
            return ENOTSUP;
        accepted._a_stacksize = given->_a_stacksize;
        accepted._a_guardsize = given->_a_guardsize;
        accepted._a_detach = given->_a_detach;
        if (memcmp(given, &accepted, sizeof accepted))
            return ENOTSUP;
    }
    return 0;
}
int __clone(int (*function)(void *), void *stack, int flags, void *argument,
            ...)
{
    va_list arguments;
    va_start(arguments, argument);
    int *parent_tid = va_arg(arguments, int *);
    pthread_t td = va_arg(arguments, pthread_t);
    volatile int *clear_tid = va_arg(arguments, volatile int *);
    va_end(arguments);
    unsigned expected = CLONE_VM | CLONE_FS | CLONE_FILES | CLONE_SIGHAND |
                        CLONE_THREAD | CLONE_SYSVSEM | CLONE_SETTLS |
                        CLONE_PARENT_SETTID | CLONE_CHILD_CLEARTID |
                        CLONE_DETACHED;
    if ((unsigned)flags != expected || clear_tid != &__thread_list_lock ||
        __thread_list_lock != __pthread_self()->tid)
        return -ENOTSUP;
    if (closing || broken || admissions >= 512)
        return broken ? -broken : -EAGAIN;
    struct record *record = 0;
    for (unsigned i = 0; i < capacity; ++i)
        if (!records[i].thread) {
            record = &records[i];
            break;
        }
    if (!record)
        return -EAGAIN;
    unsigned long aligned = (uintptr_t)stack & ~15UL;
    if (!td->map_base || td->guard_size >= td->map_size ||
        td->map_size > UINTPTR_MAX - (uintptr_t)td->map_base)
        return -EINVAL;
    unsigned long base = (uintptr_t)td->map_base + td->guard_size;
    if (base > UINTPTR_MAX - 136 || aligned < base + 136)
        return -EINVAL;
    record->function = function;
    record->argument = argument;
    struct descriptor request = {1,
                                 96,
                                 (uintptr_t)trampoline,
                                 base,
                                 td->map_size - td->guard_size,
                                 aligned - 8,
                                 (uintptr_t)td,
                                 (uintptr_t)clear_tid,
                                 (uintptr_t)record,
                                 base,
                                 td->map_size - td->guard_size,
                                 (uintptr_t)parent_tid,
                                 0};
    long result = memtrap(0x28006, thread_cap, (uintptr_t)&request, 0, 0);
    if (result > 0) {
        record->thread = td;
        record->id = (unsigned)result;
        record->base = (uintptr_t)td->map_base;
        record->bytes = td->map_size;
        record->joining = 0;
        record->detached = td->detach_state == DT_DETACHED;
        record->pending = record->allow_exit = 0;
        ++live;
        ++admissions;
        record->published = 1;
    }
    return (int)result;
}
int __pthread_join(pthread_t, void **);
int pthread_join(pthread_t td, void **value)
{
    __tl_lock();
    struct record *record = 0;
    for (unsigned i = 0; i < capacity; ++i)
        if (records[i].thread == td && td) {
            record = &records[i];
            break;
        }
    if (!record || record->joining || record->pending || record->detached) {
        __tl_unlock();
        return record ? EINVAL : ESRCH;
    }
    record->joining = 1;
    unsigned id = record->id;
    __tl_unlock();
    int result = __pthread_join(td, value);
    __tl_lock();
    if (!result) {
        /* Upstream has unmapped td. Only saved native metadata is read. */
        if (memtrap(0x2800b, thread_cap, id, 0, 0) != 1 ||
            memtrap(0x2800a, thread_cap, id, 0, 0)) {
            broken = EIO;
            result = EIO;
        } else {
            record->published = 0;
            record->thread = 0;
            --live;
        }
    }
    record->joining = 0;
    __tl_unlock();
    return result;
}
int pthread_tryjoin_np(pthread_t td, void **value)
{
    (void)td;
    (void)value;
    return ENOTSUP;
}
int pthread_timedjoin_np(pthread_t td, void **value, const struct timespec *at)
{
    (void)td;
    (void)value;
    (void)at;
    return ENOTSUP;
}
int pthread_mutex_init(pthread_mutex_t *restrict mutex,
                       const pthread_mutexattr_t *restrict attr)
{
    if (attr && attr->__attr)
        return ENOTSUP;
    *mutex = (pthread_mutex_t){0};
    return 0;
}
int pthread_cond_init(pthread_cond_t *restrict condition,
                      const pthread_condattr_t *restrict attr)
{
    if (attr && (attr->__attr >> 31 || (attr->__attr != CLOCK_MONOTONIC &&
                                        attr->__attr != CLOCK_REALTIME)))
        return ENOTSUP;
    *condition = (pthread_cond_t){0};
    if (attr)
        condition->_c_clock = attr->__attr;
    return 0;
}
int pthread_rwlock_init(pthread_rwlock_t *restrict lock,
                        const pthread_rwlockattr_t *restrict attr)
{
    if (attr && (attr->__attr[0] || attr->__attr[1]))
        return ENOTSUP;
    *lock = (pthread_rwlock_t){0};
    return 0;
}
int pthread_cancel(pthread_t td)
{
    (void)td;
    return ENOTSUP;
}
int pthread_detach(pthread_t td)
{
    (void)td;
    return ENOTSUP;
}
_Noreturn void __unmapself(void *base, size_t bytes)
{
    unsigned id = (unsigned)memtrap(0x28007, thread_cap, 0, 0, 0);
    struct record *record = 0;
    for (unsigned i = 0; i < capacity; ++i)
        if (records[i].thread && records[i].id == id)
            record = &records[i];
    if (!record || record->base != (uintptr_t)base || record->bytes != bytes)
        fatal();
    /* Detached exit holds upstream list lock; only the charged reaper settles
     * it. */
    record->pending = 1;
    ++events;
    wake((void *)&events);
    while (!record->allow_exit)
        wait((void *)&record->allow_exit, 0);
    memtrap(0x28001, thread_cap, 0, 0, 0);
    fatal();
}
static void *reap(void *unused)
{
    (void)unused;
    for (;;) {
        unsigned observed = events;
        struct record *record = 0;
        for (unsigned i = 0; i < capacity; ++i)
            if (records[i].pending && records[i].published) {
                record = &records[i];
                break;
            }
        if (!record) {
            if (stopping)
                return 0;
            wait((void *)&events, observed);
            continue;
        }
        unsigned id = record->id;
        unsigned long base = record->base, bytes = record->bytes;
        if (memtrap(0x2800b, thread_cap, id, 0, 0) != 0)
            fatal();
        record->allow_exit = 1;
        wake((void *)&record->allow_exit);
        long status;
        while ((status = memtrap(0x2800b, thread_cap, id, 0, 0)) == 0)
            yield();
        if (status != 1)
            fatal();
        /* The exited worker has unlinked itself and stopped. Never acquire
         * musl's list lock here: another detached exit may hold it while
         * awaiting this reaper. This sole reaper owns the pending record until
         * native unmap/retire complete. Atomic thread publication protects free
         * record discovery by creators, which remain list-lock serialized. */
        if (memtrap(0x22003, memory_cap, base, bytes, 0) ||
            memtrap(0x2800a, thread_cap, id, 0, 0))
            fatal();
        record->published = record->pending = 0;
        --live;
        /* Publish free last: reuse cannot precede cleanup or live accounting.
         */
        record->thread = 0;
    }
}
int aether_runtime_init(void)
{
    if (initialized)
        return EALREADY;
    memory_cap = getauxval(0xa000);
    thread_cap = getauxval(0xa001);
    if (!memory_cap || !thread_cap ||
        memtrap(0x28007, thread_cap, 0, 0, 0) <= 0)
        return EACCES;
    unsigned long op = 0x22000, total = 0;
    register unsigned long r10 __asm__("r10") = 0;
    register unsigned long r8 __asm__("r8") = 0;
    register unsigned long r9 __asm__("r9") = 0;
    __asm__ volatile("int $0x81"
                     : "+a"(op), "+d"(total), "+r"(r10), "+r"(r8), "+r"(r9)
                     : "D"(memory_cap), "S"(0UL)
                     : "rcx", "r11", "memory", "cc");
    if ((long)op < 0 || (r8 != 8192 && r8 != 128))
        return ENOTSUP;
    capacity = r8 == 8192 ? 82 : 2;
    initialized = 1;
    pthread_attr_t attr;
    pthread_attr_init(&attr);
    pthread_attr_setstacksize(&attr, capacity == 82 ? 262144 : 131072);
    pthread_attr_setguardsize(&attr, 4096);
    int error = pthread_create(&reaper, &attr, reap, 0);
    pthread_attr_destroy(&attr);
    if (error) {
        broken = error;
        closing = 1;
    }
    return error;
}
int aether_runtime_finish(void)
{
    if (!initialized || broken)
        return broken ? broken : ENOSYS;
    __tl_lock();
    closing = 1;
    if (live != 1) {
        __tl_unlock();
        return EBUSY;
    }
    stopping = 1;
    ++events;
    __tl_unlock();
    wake((void *)&events);
    return pthread_join(reaper, 0);
}
unsigned aether_runtime_live(void) { return live; }
unsigned aether_runtime_admissions(void) { return admissions; }
int aether_libc_timedwait(volatile int *word, int value, clockid_t clock,
                          const struct timespec *at, int private)
{
    return aether_monotonic_wait(word, value, clock, at, private);
}

long aether_wait_syscall(long n, long a, long b, long c, long d, long e, long f)
{
    if ((n == SYS_nanosleep && !c && !d && !e && !f) ||
        (n == SYS_clock_nanosleep && !e && !f))
        return aether_sleep_syscall(n, a, b, c, d);
    if (n == SYS_write && a == 1 && !d && !e && !f)
        return memtrap(0x10000 + SYS_write, a, b, c, 0);
    if (n == SYS_rt_sigprocmask) {
        if (d != 8 || e || f)
            return -ENOSYS;
        return memtrap(0x28009, thread_cap, a, b, c);
    }
    if (n == SYS_mmap) {
        if (a || d != (MAP_PRIVATE | MAP_ANONYMOUS) || e != -1 || f)
            return -ENOSYS;
        return memtrap(0x22001, memory_cap, b, c, 0);
    }
    if (n == SYS_mprotect && !d && !e && !f)
        return memtrap(0x22002, memory_cap, a, b, c);
    if (n == SYS_munmap && !c && !d && !e && !f)
        return memtrap(0x22003, memory_cap, a, b, 0);
    if (n == SYS_futex && b == (FUTEX_REQUEUE | FUTEX_PRIVATE)) {
        if (c || d != 1 || !e || f)
            return -ENOTSUP;
        unsigned long op = 0x2800d;
        register unsigned long r10 __asm__("r10") = 1;
        register unsigned long r8 __asm__("r8") = (unsigned long)e;
        register unsigned long r9 __asm__("r9") = 0;
        unsigned long cap = thread_cap, address = (unsigned long)a;
        unsigned long count = 0;
        __asm__ volatile("int $0x81"
                         : "+a"(op), "+D"(cap), "+S"(address), "+d"(count),
                           "+r"(r10), "+r"(r8), "+r"(r9)
                         :
                         : "rcx", "r11", "memory", "cc");
        return (long)op;
    }
    if (n == SYS_futex && !d && !e && !f) {
        if (b != FUTEX_WAIT && b != FUTEX_WAKE &&
            b != (FUTEX_WAIT | FUTEX_PRIVATE) &&
            b != (FUTEX_WAKE | FUTEX_PRIVATE))
            return -ENOTSUP;
        if ((long)(int)c != c && (unsigned long)c > 0xffffffffUL)
            return -EINVAL;
        if (!(b & FUTEX_PRIVATE) && a != (long)&__thread_list_lock)
            return -ENOTSUP;
        if ((b & ~FUTEX_PRIVATE) == FUTEX_WAIT)
            return memtrap(0x28008, thread_cap, a, (unsigned)c, 0);
        if (c != 1 && c != INT_MAX)
            return -ENOTSUP;
        return memtrap(0x2800c, thread_cap, a, c, 0);
    }
    if (n == SYS_exit && !a && !b && !c && !d && !e && !f) {
        memtrap(0x28001, thread_cap, 0, 0, 0);
        fatal();
    }
    return -ENOSYS;
}
long __aether_io(unsigned long operation, unsigned long a, unsigned long b,
                 unsigned long c)
{
    return memtrap(0x10000 + operation, a, b, c, 0);
}
