/* SPDX-License-Identifier: BSD-2-Clause */
/* Restricted kernel conformance adapter, not production pthread support. */
#include "adapter.h"
#include <stdarg.h>
#include <string.h>
#include <sys/auxv.h>
#include <sys/mman.h>
#include <unistd.h>
#include "pthread_impl.h"

#ifdef LIFE_TASKQ
#define LIFE_PAIR
#define PAIR_DETACHED
#endif

#if defined(LIFE_PAIR_TIME) || defined(LIFE_TIME_FROZEN) ||                    \
    defined(LIFE_REAL_TIME)
#define LIFE_PAIR
#define PAIR_TIME
static pthread_mutex_t time_mutex[2] = {PTHREAD_MUTEX_INITIALIZER,
                                        PTHREAD_MUTEX_INITIALIZER};
static pthread_cond_t time_cond[2];
static _Atomic unsigned time_waits[2], time_done[2], time_error[2], time_relock;
static unsigned time_predicate;
#endif

#if defined(LIFE_PAIR_DETACHED) || defined(LIFE_REAP_EARLY)
#define PAIR_DETACHED
#endif

#if defined(LIFE_PAIR_KEYS) || defined(LIFE_KEYS_BYPASS) ||                    \
    (defined(PAIR_DETACHED) && !defined(LIFE_TASKQ))
#define LIFE_PAIR
#define PAIR_KEYS
static pthread_key_t value_key, loop_key, deleted_key;
static unsigned parent_value, deleted_calls;
static struct key_record {
    unsigned calls, loops, error, tid;
} key_records[2];
static void key_destructor(void *value)
{
    struct key_record *record = 0;
    for (unsigned i = 0; i < 2; ++i)
        if (value == &key_records[i])
            record = &key_records[i];
    if (!record)
        __builtin_trap();
#ifdef LIFE_KEYS_BYPASS
    return;
#endif
    if (pthread_getspecific(value_key) ||
        (unsigned)pthread_self()->tid != record->tid)
        record->error = 1;
    ++record->calls;
    if (record->calls == 1 && pthread_setspecific(value_key, record))
        record->error = 2;
}
static void loop_destructor(void *value)
{
    struct key_record *record = value;
    if ((value != &key_records[0] && value != &key_records[1]))
        __builtin_trap();
    if (pthread_getspecific(loop_key) ||
        (unsigned)pthread_self()->tid != record->tid)
        record->error = 3;
    ++record->loops;
    if (pthread_setspecific(loop_key, record))
        record->error = 4;
}
static void deleted_destructor(void *value)
{
    (void)value;
    ++deleted_calls;
}
#endif

#if defined(LIFE_PAIR_RW) || defined(LIFE_RW_BYPASS)
#define LIFE_PAIR
#define PAIR_RW
static pthread_rwlock_t rw = PTHREAD_RWLOCK_INITIALIZER;
static _Atomic unsigned rw_waits, rw_arrived, rw_active, rw_writer;
static unsigned rw_batch;
#endif

#if defined(LIFE_PAIR_COND) || defined(LIFE_PAIR_REQUEUE_BYPASS)
#define LIFE_PAIR
#define PAIR_CONDITION
static pthread_mutex_t pair_mutex = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t pair_condition = PTHREAD_COND_INITIALIZER;
static _Atomic unsigned pair_waits, pair_relocks, pair_returned, pair_requeues;
static unsigned pair_tokens;
#endif

#if defined(LIFE_COND) || defined(LIFE_COND_BYPASS)
#define LIFE_MUTEX
#define LIFE_COND_TEST
#endif

#if defined(LIFE_MUTEX) || defined(LIFE_MUTEX_BYPASS)
#define LIFE_REPEAT
#define LIFE_MUTEX_TEST
#endif

#if defined(LIFE_GUARD_FAULT) || defined(LIFE_REPEAT)
#define LIFE_STACK_ATTR
#endif

static unsigned long thread_cap, memory_cap;
static unsigned used;
#ifdef LIFE_PAIR
static unsigned admissions, parent_id;
static struct startup {
    int (*function)(void *);
    void *argument;
    pthread_t thread;
    unsigned id;
#ifdef PAIR_DETACHED
    unsigned long map_base, map_bytes;
    _Atomic unsigned pending, allow_exit;
#endif
} startups[2];
#endif
#ifdef LIFE_REPEAT
static unsigned native_id, retired_id, completed;
static pthread_t active_thread;
#endif
#ifdef LIFE_MUTEX_TEST
static pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
static _Atomic unsigned mutex_waits, mutex_entered, mutex_attempted;
static unsigned protected_value, parent_yields;
#endif
#ifdef LIFE_COND_TEST
static pthread_cond_t condition = PTHREAD_COND_INITIALIZER;
static _Atomic unsigned condition_waits, condition_attempted,
    condition_returned;
static unsigned predicate;
#endif
static _Atomic unsigned waits_entered;
#ifndef LIFE_PAIR
static _Atomic unsigned release_child, child_error;
#endif
static _Thread_local volatile unsigned cookie = 17;
#ifndef LIFE_PAIR
static int (*start_function)(void *);
static void *start_argument;
#endif
struct descriptor {
    unsigned version, size;
    unsigned long entry, base, bytes, rsp, fs, tid, argument;
    unsigned long tls_base, tls_bytes, parent_tid, reserved;
};
_Static_assert(sizeof(struct descriptor) == 96, "native descriptor");

#ifdef PAIR_TIME
#ifndef LIFE_REAL_TIME
int __clock_gettime(clockid_t id, struct timespec *out)
{
    if (id != CLOCK_MONOTONIC) {
        errno = ENOTSUP;
        return -1;
    }
    long ns = memtrap(0x2800e, thread_cap, 0, 0, 0);
    if (ns < 0) {
        errno = (int)-ns;
        return -1;
    }
#ifdef LIFE_TIME_FROZEN
    ns = 0;
#endif
    out->tv_sec = ns / 1000000000;
    out->tv_nsec = ns % 1000000000;
    return 0;
}
int clock_gettime(clockid_t id, struct timespec *out)
{
    return __clock_gettime(id, out);
}
#endif
static unsigned long time_ns(void)
{
    struct timespec t;
    if (clock_gettime(CLOCK_MONOTONIC, &t))
        __builtin_trap();
    return (unsigned long)t.tv_sec * 1000000000 + t.tv_nsec;
}
#endif

#ifdef PAIR_DETACHED
_Noreturn void __unmapself(void *base, size_t bytes)
{
    unsigned id = memtrap(0x28007, thread_cap, 0, 0, 0);
    struct startup *slot = 0;
    for (unsigned i = 0; i < 2; ++i)
        if (startups[i].id == id && startups[i].thread)
            slot = &startups[i];
    if (!slot || slot->map_base != (unsigned long)base ||
        slot->map_bytes != bytes)
        __builtin_trap();
    // Request only: the child still executes on this mapping until native exit.
    slot->pending = 1;
    while (!slot->allow_exit)
        memtrap(0x1fffe, 0, 0, 0, 0);
    memtrap(0x28001, thread_cap, 0, 0, 0);
    __builtin_trap(); // Successful child exit must never return to this stack.
}
static long reap_detached(unsigned i)
{
    struct startup *slot = &startups[i];
    if (!slot->thread || !slot->pending)
        return 0;
#ifndef LIFE_REAP_EARLY
    long status = memtrap(0x2800b, thread_cap, slot->id, 0, 0);
    if (status == 0)
        return 0;
    if (status != 1)
        return -1;
#endif
    long result =
        memtrap(0x22003, memory_cap, slot->map_base, slot->map_bytes, 0);
    if (result)
        return result;
    if (memtrap(0x2800a, thread_cap, slot->id, 0, 0))
        return -2;
    // Never dereference this pthread_t: only the saved private token survived.
    slot->thread = 0;
    slot->pending = 0;
    --used;
    return 1;
}
#endif

int aether_pthread_admit(const void *attr)
{
    if (attr == __ATTRP_C11_THREAD)
        return ENOTSUP;
    if (attr) {
#ifndef LIFE_SKIP_ATTR_CHECK
        const pthread_attr_t *a = attr;
        if (a->_a_stacksize < 128 * 1024 || a->_a_stacksize > 256 * 1024 ||
            a->_a_stacksize % 4096 || a->_a_guardsize != 4096)
            return ENOTSUP;
        pthread_attr_t canonical = {0};
        canonical._a_stacksize = a->_a_stacksize;
        canonical._a_guardsize = a->_a_guardsize;
#ifdef PAIR_DETACHED
        if (a->_a_detach != PTHREAD_CREATE_DETACHED)
            return ENOTSUP;
        canonical._a_detach = PTHREAD_CREATE_DETACHED;
#endif
        if (memcmp(a, &canonical, sizeof canonical))
            return ENOTSUP;
#endif
    }
    if (!thread_cap || !memory_cap)
        return ENOSYS;
#ifdef LIFE_REPEAT
    if (completed == 4)
        return EAGAIN;
#endif
#ifdef LIFE_PAIR
    if (memtrap(0x28007, thread_cap, 0, 0, 0) != parent_id)
        return ENOSYS;
    return used == 2 || admissions == 4 ? EAGAIN : 0;
#else
    return used ? EAGAIN : 0;
#endif
}
int __pthread_join(pthread_t, void **);
int pthread_join(pthread_t t, void **value)
{
#ifdef PAIR_DETACHED
    (void)t;
    (void)value;
    return ENOSYS;
#else
#ifdef LIFE_PAIR
    if (memtrap(0x28007, thread_cap, 0, 0, 0) != parent_id)
        return ENOSYS;
    struct startup *slot = 0;
    for (unsigned i = 0; i < 2; ++i)
        if (startups[i].thread == t && t)
            slot = &startups[i];
    if (!slot)
        return ESRCH;
    unsigned token = slot->id;
    int status = __pthread_join(t, value);
    if (status)
        return status;
    slot->thread = 0; // Upstream join unmapped t; use only the saved ID below.
    if (memtrap(0x2800b, thread_cap, token, 0, 0) != 1 ||
        memtrap(0x2800a, thread_cap, token, 0, 0) != 0)
        return EIO;
    --used;
    return 0;
#else
#ifdef LIFE_REPEAT
    if (!used || t != active_thread)
        return ESRCH;
    unsigned token = native_id;
#endif
    int status = __pthread_join(t, value);
#ifdef LIFE_REPEAT
    if (status)
        return status;
    // Upstream join unmapped t. Close the handle even if retirement fails.
    active_thread = 0;
    // Use the admission token, never t->tid.
    if (memtrap(0x28002, thread_cap, 0, 0, 0) != 1 ||
        (retired_id && memtrap(0x2800a, thread_cap, retired_id, 0, 0) != -9) ||
        memtrap(0x2800a, thread_cap, token, 0, 0) != 0 ||
        memtrap(0x2800a, thread_cap, token, 0, 0) != -2 ||
        memtrap(0x28002, thread_cap, 0, 0, 0) != -2)
        return EIO;
    retired_id = token;
    ++completed;
    used = 0;
#endif
    return status;
#endif
#endif
}
int pthread_cancel(pthread_t t)
{
    (void)t;
    return ENOSYS;
}
int pthread_detach(pthread_t t)
{
    (void)t;
    return ENOSYS;
}
static _Noreturn void trampoline(unsigned long unused)
{
#ifdef LIFE_PAIR
    struct startup *slot = (void *)unused;
    slot->function(slot->argument);
#else
    (void)unused;
    start_function(start_argument);
#endif
    __builtin_trap();
}
int __clone(int (*function)(void *), void *stack, int flags, void *arg, ...)
{
    va_list arguments;
    va_start(arguments, arg);
    int *parent_tid = va_arg(arguments, int *);
    pthread_t tls = va_arg(arguments, pthread_t);
    volatile int *clear_tid = va_arg(arguments, volatile int *);
    va_end(arguments);
    const unsigned expected = CLONE_VM | CLONE_FS | CLONE_FILES |
                              CLONE_SIGHAND | CLONE_THREAD | CLONE_SYSVSEM |
                              CLONE_SETTLS | CLONE_PARENT_SETTID |
                              CLONE_CHILD_CLEARTID | CLONE_DETACHED;
#ifdef LIFE_PAIR
    struct startup *slot = 0;
    for (unsigned i = 0; i < 2; ++i)
        if (!startups[i].thread) {
            slot = &startups[i];
            break;
        }
    if (!slot)
        return -EAGAIN;
#endif
    if ((unsigned)flags != expected ||
#ifndef LIFE_PAIR
        used ||
#endif
        clear_tid != &__thread_list_lock)
        return -ENOSYS;
    pthread_t td = tls;
    unsigned long aligned_stack = (unsigned long)stack & ~15UL;
    unsigned long base = (unsigned long)td->map_base + td->guard_size;
    unsigned long bytes = td->map_size - td->guard_size;
    if (!td->map_base || td->guard_size >= td->map_size ||
        aligned_stack < base + 136)
        return -EINVAL;
#ifdef LIFE_PAIR
    slot->function = function;
    slot->argument = arg;
#else
    start_function = function;
    start_argument = arg;
#endif
    struct descriptor request = {1,
                                 96,
                                 (unsigned long)trampoline,
                                 base,
                                 bytes,
                                 aligned_stack - 8,
                                 (unsigned long)tls,
                                 (unsigned long)clear_tid,
                                 0,
                                 base,
                                 bytes,
                                 (unsigned long)parent_tid,
                                 0};
#ifdef LIFE_PAIR
    request.argument = (unsigned long)slot;
#endif
    unsigned long cap = thread_cap;
#ifdef LIFE_BAD_CAP
    cap ^= 3;
#endif
    long result = memtrap(0x28006, cap, (unsigned long)&request, 0, 0);
    if (result > 0) {
#ifdef LIFE_PAIR
        ++used;
        ++admissions;
        slot->thread = td;
        slot->id = result;
#ifdef PAIR_DETACHED
        slot->map_base = (unsigned long)td->map_base;
        slot->map_bytes = td->map_size;
        slot->pending = slot->allow_exit = 0;
#endif
#else
        used = 1;
#endif
#ifdef LIFE_REPEAT
        native_id = (unsigned)result;
        active_thread = td;
#endif
    }
    return (int)result;
}
#ifdef LIFE_REAL_TIME
#include "real_time.h"
static _Atomic(volatile int *) time_words[2];
int aether_libc_timedwait(volatile int *word, int val, clockid_t clock,
                          const struct timespec *at, int priv)
{
    unsigned index = (unsigned)__pthread_self()->tid == startups[0].id ? 0 : 1;
    time_words[index] = word;
    ++time_waits[index];
    ++waits_entered;
    int error = aether_monotonic_wait(word, val, clock, at, priv);
    time_words[index] = 0;
    return error;
}
#endif
long aether_wait_syscall(long n, long a, long b, long c, long d, long e, long f)
{
#ifdef LIFE_REAL_TIME
    if ((n == SYS_nanosleep && !c && !d && !e && !f) ||
        (n == SYS_clock_nanosleep && !e && !f))
        return aether_sleep_syscall(n, a, b, c, d);
#endif
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
#if defined(PAIR_CONDITION) || defined(LIFE_TASKQ)
    if (n == SYS_futex && b == (FUTEX_REQUEUE | FUTEX_PRIVATE)) {
        if (c != 0 || d != 1 || !e || f)
            return -ENOSYS;
#ifdef LIFE_PAIR_REQUEUE_BYPASS
        return memtrap(0x2800c, thread_cap, a, 1, 0);
#else
        unsigned long op = 0x2800d;
        register unsigned long r10 __asm__("r10") = 1;
        register unsigned long r8 __asm__("r8") = e;
        register unsigned long r9 __asm__("r9") = 0;
        // Native validation owns both pointer lifetimes; no user borrow
        // survives.
        __asm__ __volatile__("int $0x81"
                             : "+a"(op), "+r"(r10), "+r"(r8), "+r"(r9)
                             : "D"(thread_cap), "S"(a), "d"(0UL)
                             : "rcx", "r11", "memory");
#ifdef PAIR_CONDITION
        if ((long)op > 0)
            ++pair_requeues;
#endif
        return (long)op;
#endif
    }
#endif
#if defined(PAIR_TIME) && !defined(LIFE_REAL_TIME)
    if (n == SYS_futex && b == (FUTEX_WAIT | FUTEX_PRIVATE) && d && !e && !f) {
        const struct timespec *t = (void *)d;
        if (t->tv_sec < 0 || t->tv_sec > 1 || t->tv_nsec < 0 ||
            t->tv_nsec >= 1000000000 || (t->tv_sec == 1 && t->tv_nsec))
            return -ENOSYS;
        unsigned long ns = (unsigned long)t->tv_sec * 1000000000 + t->tv_nsec;
        if (!ns)
            return -ETIMEDOUT;
        unsigned index =
            (unsigned)__pthread_self()->tid == startups[0].id ? 0 : 1;
        ++time_waits[index];
        ++waits_entered;
        return memtrap(0x28003, thread_cap, a, (unsigned)c,
                       (ns + 9999999) / 10000000);
    }
#endif
    if (n == SYS_futex && !d && !e && !f) {
        if (b != FUTEX_WAIT && b != FUTEX_WAKE &&
            b != (FUTEX_WAIT | FUTEX_PRIVATE) &&
            b != (FUTEX_WAKE | FUTEX_PRIVATE))
            return -ENOSYS;
        if ((long)(int)c != c && (unsigned long)c > 0xffffffffUL)
            return -ENOSYS;
        int op = b & ~FUTEX_PRIVATE;
        if (!(b & FUTEX_PRIVATE) && a != (long)&__thread_list_lock)
            return -ENOSYS;
        if (op == FUTEX_WAIT) {
#ifdef PAIR_TIME
            if (a == (long)&time_mutex[1]._m_lock)
                ++time_relock;
#endif
#ifdef PAIR_RW
            if (a == (long)&rw._rw_lock)
                ++rw_waits;
#endif
#ifdef PAIR_CONDITION
            if (a == (long)&pair_mutex._m_lock)
                ++pair_relocks;
            else if (a != (long)&__thread_list_lock)
                ++pair_waits;
#endif
#ifdef LIFE_MUTEX_TEST
            if (a == (long)&mutex._m_lock)
                ++mutex_waits;
#endif
#ifdef LIFE_COND_TEST
            if (condition_attempted && a != (long)&mutex._m_lock &&
                a != (long)&__thread_list_lock)
                ++condition_waits;
#endif
            ++waits_entered;
            return memtrap(0x28008, thread_cap, a, (unsigned)c, 0);
        }
        if (op == FUTEX_WAKE && (c == 1 || c == INT_MAX))
#if defined(PAIR_CONDITION) || defined(PAIR_RW) || defined(LIFE_TASKQ)
            return memtrap(0x2800c, thread_cap, a, c, 0);
#else
            return memtrap(0x28004, thread_cap, a, 0, 0);
#endif
    }
    if (n == SYS_exit && a == 0 && !b && !c && !d && !e && !f) {
        memtrap(0x28001, thread_cap, 0, 0, 0);
        __builtin_trap();
    }
    return -ENOSYS;
}
long __aether_io(unsigned long op, unsigned long a, unsigned long b,
                 unsigned long c)
{
    return memtrap(0x10000 + op, a, b, c, 0);
}
#ifndef LIFE_PAIR
static void *worker(void *arg)
{
#ifdef LIFE_STACK_ATTR
    volatile unsigned char stack_probe[240 * 1024];
    for (unsigned i = 0; i < sizeof stack_probe; ++i)
        stack_probe[i] = (unsigned char)(i + 31);
#endif
    unsigned long mask = 0;
    if (arg != (void *)0x123 || cookie != 17 ||
        __pthread_self()->tid != memtrap(0x28007, thread_cap, 0, 0, 0) ||
        pthread_self() != __pthread_self())
        child_error = 201;
    if (memtrap(0x28009, thread_cap, 0, 0, (unsigned long)&mask) ||
        mask != (1UL << 10))
        child_error = 202;
#ifdef LIFE_REPEAT
    if (memtrap(0x2800a, thread_cap, __pthread_self()->tid, 0, 0) != -13)
        child_error = 205;
#endif
    cookie = 37;
    errno = 37;
    while (!release_child)
        memtrap(0x1fffe, 0, 0, 0, 0);
#ifdef LIFE_GUARD_FAULT
    if (__pthread_self()->tid == 3)
        (void)*(volatile unsigned char *)__pthread_self()->map_base;
#endif
#ifdef THREAD_FAULT
    if (__pthread_self()->tid == 3)
        __asm__ __volatile__("ud2");
#endif
#ifdef LIFE_MUTEX_TEST
    mutex_attempted = 1;
#ifndef LIFE_MUTEX_BYPASS
    if (pthread_mutex_lock(&mutex))
        child_error = 206;
#endif
    mutex_entered = 1;
    if (protected_value != completed * 2 + 1)
        child_error = 207;
    ++protected_value;
#ifdef LIFE_COND_TEST
    condition_attempted = 1;
#ifndef LIFE_COND_BYPASS
    while (!predicate)
        if (pthread_cond_wait(&condition, &mutex)) {
            child_error = 209;
            break;
        }
    if (!predicate || pthread_mutex_trylock(&mutex) != EBUSY)
        child_error = 210;
#endif
    condition_returned = 1;
#endif
#ifndef LIFE_MUTEX_BYPASS
    if (pthread_mutex_unlock(&mutex))
        child_error = 208;
#endif
#endif
    for (unsigned i = 0; i < 32; ++i)
        memtrap(0x1fffe, 0, 0, 0, 0);
#ifdef LIFE_STACK_ATTR
    for (unsigned i = 0; i < sizeof stack_probe; ++i)
        if (stack_probe[i] != (unsigned char)(i + 31))
            child_error = 204;
#endif
    if (cookie != 37 || errno != 37)
        child_error = 203;
    return (void *)0x456;
}
#define CHECK(x, n)                                                            \
    do {                                                                       \
        if (!(x))                                                              \
            return (n);                                                        \
    } while (0)
int main(int argc, char **argv)
{
    CHECK(argc == 2 && argv && !used && !child_error, 180);
    thread_cap = getauxval(0xa001);
    memory_cap = getauxval(0xa000);
    CHECK(thread_cap && memory_cap, 182);
    pthread_t self = pthread_self(), td = (pthread_t)0x1234;
    CHECK(aether_wait_syscall(SYS_futex, (long)&release_child, FUTEX_WAIT, 0, 0,
                              0, 0) == -ENOSYS &&
              aether_wait_syscall(SYS_futex, (long)&release_child,
                                  0x100000000L | FUTEX_PRIVATE, 0, 0, 0,
                                  0) == -ENOSYS &&
              aether_wait_syscall(SYS_futex, (long)&release_child,
                                  FUTEX_PRIVATE, 0, 1, 0, 0) == -ENOSYS &&
              aether_wait_syscall(SYS_tkill, self->tid, 1, 0, 0, 0, 0) ==
                  -ENOSYS,
          222);
    pthread_attr_t attr = {0};
    CHECK(pthread_create(&td, &attr, worker, 0) == ENOTSUP &&
              td == (pthread_t)0x1234 && !libc.threaded,
          183);
    CHECK(pthread_attr_init(&attr) == 0 &&
              pthread_attr_setstacksize(&attr, 256 * 1024) == 0 &&
              pthread_attr_setguardsize(&attr, 4096) == 0,
          223);
    long initial_quota = memtrap(0x22000, memory_cap, 0, 0, 0);
    errno = 71;
    CHECK(pthread_create(&td, __ATTRP_C11_THREAD, worker, 0) == ENOTSUP &&
              td == (pthread_t)0x1234,
          224);
    for (unsigned i = 0; i < 11; ++i) {
        pthread_attr_t bad = attr;
        switch (i) {
        case 0:
            bad._a_stacksize = 127 * 1024;
            break;
        case 1:
            bad._a_stacksize = 257 * 1024;
            break;
        case 2:
            bad._a_stacksize = 128 * 1024 + 1;
            break;
        case 3:
            bad._a_guardsize = 0;
            break;
        case 4:
            bad._a_guardsize = 8192;
            break;
        case 5:
            bad._a_stackaddr = 0x200000;
            break;
        case 6:
            bad._a_detach = 1;
            break;
        case 7:
            bad._a_sched = 1;
            break;
        case 8:
            bad._a_policy = 1;
            break;
        case 9:
            bad._a_prio = 1;
            break;
        default:
            ((unsigned char *)&bad)[sizeof bad - 1] = 1;
            break;
        }
        unsigned long rejected_mask = ~0UL;
        CHECK(pthread_create(&td, &bad, worker, 0) == ENOTSUP &&
                  td == (pthread_t)0x1234 && errno == 71 && !libc.threaded &&
                  !libc.threads_minus_1 && !libc.need_locks &&
                  self->next == self && self->prev == self &&
                  memtrap(0x22000, memory_cap, 0, 0, 0) == initial_quota &&
                  memtrap(0x28009, thread_cap, 0, 0,
                          (unsigned long)&rejected_mask) == 0 &&
                  rejected_mask == 0,
              225);
    }
    unsigned long mask = 1UL << 10, old = 0;
    CHECK(memtrap(0x28009, thread_cap, 2, (unsigned long)&mask, 0) == 0, 184);
    long quota = memtrap(0x22000, memory_cap, 0, 0, 0);
    errno = 71;
#ifdef LIFE_REPEAT
    CHECK(memtrap(0x2800a, thread_cap, 3, 0, 0) == -2 &&
              memtrap(0x2800a, thread_cap ^ 0x100, 3, 0, 0) == -13 &&
              memtrap(0x2800a, thread_cap, 0, 0, 0) == -22 &&
              memtrap(0x2800a, thread_cap, 0x100000000UL, 0, 0) == -22 &&
              memtrap(0x2800a, thread_cap, 3, 1, 0) == -22,
          231);
    for (unsigned cycle = 0; cycle < 4; ++cycle) {
        release_child = 0;
        child_error = 0;
        waits_entered = 0;
        td = (pthread_t)0x1234;
#endif
#ifdef LIFE_STACK_ATTR
        CHECK(quota > 32, 226);
        unsigned long reservation_bytes = (unsigned long)(quota - 32) * 4096;
        long reservation =
            memtrap(0x22001, memory_cap, reservation_bytes, 3, 0);
        CHECK(reservation > 0 && memtrap(0x22000, memory_cap, 0, 0, 0) == 32,
              227);
        CHECK(pthread_create(&td, &attr, worker, (void *)0x123) == EAGAIN &&
                  td == (pthread_t)0x1234 && !used && !libc.threads_minus_1 &&
                  self->next == self && self->prev == self &&
                  __thread_list_lock == 0 &&
                  memtrap(0x28002, thread_cap, 0, 0, 0) == -2 &&
                  memtrap(0x22000, memory_cap, 0, 0, 0) == 32,
              228);
        CHECK(memtrap(0x22003, memory_cap, reservation, reservation_bytes, 0) ==
                      0 &&
                  memtrap(0x22000, memory_cap, 0, 0, 0) == quota,
              229);
        errno = 71;
        int result = pthread_create(&td, &attr, worker, (void *)0x123);
#else
    int result = pthread_create(&td, 0, worker, (void *)0x123);
#endif
#ifdef LIFE_BAD_CAP
        CHECK(result == EAGAIN && td == (pthread_t)0x1234 && !used, 210);
        CHECK(!libc.threads_minus_1 && self->next == self &&
                  self->prev == self && __thread_list_lock == 0 &&
                  memtrap(0x28002, thread_cap, 0, 0, 0) == -2,
              211);
#else
    CHECK(result == 0 && td != (pthread_t)0x1234 && used, 181);
    CHECK(pthread_cancel(td) == ENOSYS && !td->cancel &&
              pthread_detach(td) == ENOSYS && td->detach_state == DT_JOINABLE,
          212);
    CHECK(memtrap(0x22002, memory_cap,
                  (unsigned long)td->map_base + td->guard_size,
                  td->map_size - td->guard_size, 3) == -13,
          216);
#ifdef LIFE_STACK_ATTR
    CHECK(td->guard_size == 4096 && td->stack_size >= 256 * 1024 &&
              (unsigned long)td->stack - td->stack_size ==
                  (unsigned long)td->map_base + td->guard_size,
          230);
#endif
#ifdef LIFE_REPEAT
    CHECK(native_id == (unsigned)self->tid + 2 + cycle * 8 &&
              native_id != retired_id && td->tid == (int)native_id,
          233);
    CHECK(memtrap(0x2800a, thread_cap, native_id, 0, 0) == -16 &&
              (!retired_id ||
               memtrap(0x2800a, thread_cap, retired_id, 0, 0) == -9) &&
              memtrap(0x28002, thread_cap, 0, 0, 0) == 0,
          234);
#endif
#ifdef LIFE_MUTEX_TEST
#ifdef LIFE_COND_TEST
    predicate = 0;
    condition_waits = condition_attempted = condition_returned = 0;
#endif
    mutex_waits = mutex_entered = mutex_attempted = 0;
    CHECK(pthread_mutex_lock(&mutex) == 0 &&
              pthread_mutex_trylock(&mutex) == EBUSY,
          241);
    ++protected_value;
#endif
    release_child = 1;
#ifdef LIFE_MUTEX_TEST
    for (unsigned spin = 0; spin < 8 && !mutex_waits && !mutex_entered;
         ++spin) {
        ++parent_yields;
        memtrap(0x1fffe, 0, 0, 0, 0);
    }
    CHECK(mutex_attempted && mutex_waits && !mutex_entered &&
              protected_value == completed * 2 + 1,
          242);
    CHECK(pthread_mutex_unlock(&mutex) == 0, 243);
#ifdef LIFE_COND_TEST
    for (unsigned spin = 0; spin < 4 && !condition_waits && !condition_returned;
         ++spin) {
        ++parent_yields;
        memtrap(0x1fffe, 0, 0, 0, 0);
    }
    CHECK(condition_attempted && condition_waits && !condition_returned, 252);
    CHECK(pthread_mutex_lock(&mutex) == 0 && !predicate, 253);
    predicate = 1;
    unsigned before_relock = mutex_waits;
    CHECK((cycle % 2 ? pthread_cond_broadcast(&condition)
                     : pthread_cond_signal(&condition)) == 0,
          254);
    for (unsigned spin = 0;
         spin < 4 && mutex_waits == before_relock && !condition_returned;
         ++spin) {
        ++parent_yields;
        memtrap(0x1fffe, 0, 0, 0, 0);
    }
    CHECK(!condition_returned && mutex_waits > before_relock, 255);
    CHECK(pthread_mutex_unlock(&mutex) == 0, 256);
#endif
#endif
    void *value = 0;
    CHECK(pthread_join(td, &value) == 0 && value == (void *)0x456, 213);
#ifdef LIFE_MUTEX_TEST
    CHECK(mutex_entered && protected_value == completed * 2 &&
              mutex._m_lock == 0 && mutex._m_waiters == 0 &&
              pthread_mutex_trylock(&mutex) == 0 &&
              pthread_mutex_unlock(&mutex) == 0,
          244);
#endif
#ifdef LIFE_COND_TEST
    CHECK(condition_returned && predicate && !condition._c_head &&
              !condition._c_tail && !condition._c_lock,
          257);
#endif
    /* td is now unmapped; do not dereference or reuse that handle. */
    CHECK(!child_error && waits_entered > 0 && cookie == 17 && errno == 71,
          214);
    long expected_child = 1;
#ifdef LIFE_REPEAT
    expected_child = -2;
#endif
    CHECK(self->next == self && self->prev == self && !libc.threads_minus_1 &&
              __thread_list_lock == 0 &&
              memtrap(0x28002, thread_cap, 0, 0, 0) == expected_child,
          215);
#ifndef LIFE_REPEAT
    td = (pthread_t)0x1234;
    CHECK(pthread_create(&td, 0, worker, 0) == EAGAIN &&
              td == (pthread_t)0x1234,
          217);
#endif
#endif
        CHECK(memtrap(0x22000, memory_cap, 0, 0, 0) == quota, 218);
        CHECK(memtrap(0x28009, thread_cap, 0, 0, (unsigned long)&old) == 0 &&
                  old == mask,
              219);
#ifdef LIFE_REPEAT
    }
    td = (pthread_t)0x1234;
    CHECK(completed == 4 && !used &&
              pthread_create(&td, &attr, worker, 0) == EAGAIN &&
              td == (pthread_t)0x1234 &&
              memtrap(0x28006, thread_cap, 0, 0, 0) == -28 &&
              memtrap(0x22000, memory_cap, 0, 0, 0) == quota,
          235);
#endif
    unsigned already_yielded = 0;
#ifdef LIFE_MUTEX_TEST
    already_yielded = parent_yields;
#endif
    for (unsigned i = already_yielded; i < 64; ++i)
        memtrap(0x1fffe, 0, 0, 0, 0);
    CHECK(write(1, "AETHER MUSL NATIVE PASS\n", 24) == 16, 220);
    CHECK(write(1, &"AETHER MUSL NATIVE PASS\n"[16], 8) == 8, 221);
    return 0;
}

#endif

#ifdef LIFE_TASKQ
#include "../native-taskq/fixture.inc"
#elif defined(LIFE_PAIR)
static _Atomic unsigned entered[2], gates[2], errors[2];
static void *pair_worker(void *arg)
{
    unsigned i = (unsigned long)arg;
    if (i > 1)
        __builtin_trap();
    if (cookie != 17 ||
        pthread_self()->tid != memtrap(0x28007, thread_cap, 0, 0, 0))
        errors[i] = 1;
    pthread_t forbidden = (pthread_t)0x1234;
    if (pthread_create(&forbidden, 0, pair_worker, 0) != ENOSYS ||
        forbidden != (pthread_t)0x1234 ||
        pthread_join(pthread_self(), 0) != ENOSYS)
        errors[i] = 3;
    cookie = 100 + i;
    errno = 80 + i;
#ifdef PAIR_KEYS
    key_records[i].tid = pthread_self()->tid;
    if (pthread_getspecific(value_key) || pthread_getspecific(loop_key) ||
        pthread_getspecific(deleted_key) ||
        pthread_setspecific(value_key, &key_records[i]) ||
        pthread_setspecific(loop_key, &key_records[i]) ||
        pthread_setspecific(deleted_key, &key_records[i]))
        errors[i] = 8;
#endif
    entered[i] = 1;
    while (!gates[i])
        memtrap(0x1fffe, 0, 0, 0, 0);
#ifdef PAIR_KEYS
    if (pthread_getspecific(value_key) != &key_records[i] ||
        pthread_getspecific(loop_key) != &key_records[i] ||
        pthread_getspecific(deleted_key))
        errors[i] = 9;
#endif
#ifdef PAIR_CONDITION
    if (pthread_mutex_lock(&pair_mutex))
        __builtin_trap();
    while (!pair_tokens)
        if (pthread_cond_wait(&pair_condition, &pair_mutex))
            __builtin_trap();
    if (pthread_mutex_trylock(&pair_mutex) != EBUSY)
        errors[i] = 4;
    --pair_tokens;
    ++pair_returned;
    if (pthread_mutex_unlock(&pair_mutex))
        errors[i] = 5;
#endif
#ifdef PAIR_RW
    if (pthread_rwlock_rdlock(&rw))
        __builtin_trap();
    if (rw_writer)
        errors[i] = 6;
    ++rw_active;
    ++rw_arrived;
    // Batch zero releases only after the writer enters its actual wait seam.
    // Batch one holds both readers until each has entered concurrently.
    while (rw_batch ? rw_arrived != 2 : !rw_waits)
        memtrap(0x1fffe, 0, 0, 0, 0);
    --rw_active;
    if (pthread_rwlock_unlock(&rw))
        errors[i] = 7;
#endif
#ifdef PAIR_TIME
    if (pthread_mutex_lock(&time_mutex[i]))
        __builtin_trap();
    unsigned long duration = i ? 500000000UL : 30000000UL;
#ifdef LIFE_REAL_TIME
    if (!i)
        duration = 200000000UL;
#endif
    unsigned long deadline = time_ns() + duration;
    struct timespec until = {deadline / 1000000000, deadline % 1000000000};
    int result = pthread_cond_timedwait(&time_cond[i], &time_mutex[i], &until);
    if ((!i && result != ETIMEDOUT) || (i && (result || !time_predicate)))
        time_error[i] = 1;
    if (!i && time_ns() < deadline)
        time_error[i] = 2;
    if (pthread_mutex_trylock(&time_mutex[i]) != EBUSY)
        time_error[i] = 3;
    time_done[i] = 1;
    if (pthread_mutex_unlock(&time_mutex[i]))
        time_error[i] = 4;
#endif
    for (unsigned j = 0; j < 4; ++j) {
        memtrap(0x1fffe, 0, 0, 0, 0);
        if (cookie != 100 + i || errno != (int)(80 + i))
            errors[i] = 2;
    }
    return (void *)(0x500UL + i);
}
#define PC(x, n)                                                               \
    do {                                                                       \
        if (!(x))                                                              \
            return n;                                                          \
    } while (0)
int main(int argc, char **argv)
{
    PC(argc == 2 && argv, 180);
    thread_cap = getauxval(0xa001);
    memory_cap = getauxval(0xa000);
    parent_id = memtrap(0x28007, thread_cap, 0, 0, 0);
    PC(thread_cap && memory_cap && parent_id, 181);
#ifdef PAIR_TIME
#ifdef LIFE_REAL_TIME
    int sleep_error = aether_sleep_probe();
    PC(!sleep_error, sleep_error);
#endif
    long observed = memtrap(0x2800e, thread_cap, 0, 0, 0);
    if (observed == -38)
        return 274;
    PC(observed >= 0 && memtrap(0x2800e, thread_cap ^ 3, 0, 0, 0) == -13 &&
           memtrap(0x2800e, thread_cap, 1, 0, 0) == -22 &&
           memtrap(0x2800e, thread_cap, 0, 1, 0) == -22 &&
           memtrap(0x2800e, thread_cap, 0, 0, 1) == -22,
       270);
    struct timespec invalid = {0, 1000000000}, expired = {-1, 0};
    pthread_condattr_t ca;
    PC(pthread_condattr_init(&ca) == 0 &&
           pthread_condattr_setclock(&ca, CLOCK_MONOTONIC) == 0 &&
           pthread_cond_init(&time_cond[0], &ca) == 0 &&
           pthread_cond_init(&time_cond[1], &ca) == 0 &&
           pthread_condattr_destroy(&ca) == 0,
       275);
    PC(clock_gettime(CLOCK_REALTIME, &invalid) == -1 && errno == ENOTSUP &&
           pthread_mutex_lock(&time_mutex[0]) == 0 &&
           pthread_cond_timedwait(&time_cond[0], &time_mutex[0], &invalid) ==
               EINVAL &&
           pthread_cond_timedwait(&time_cond[0], &time_mutex[0], &expired) ==
               ETIMEDOUT &&
           pthread_mutex_unlock(&time_mutex[0]) == 0,
       276);
#ifdef LIFE_REAL_TIME
    pthread_cond_t utc = PTHREAD_COND_INITIALIZER;
    unsigned long future = time_ns() + 2000000000UL;
    struct timespec too_far = {future / 1000000000, future % 1000000000};
    struct timespec overflow = {LONG_MAX, 0};
    PC(pthread_mutex_lock(&time_mutex[0]) == 0 &&
           pthread_cond_timedwait(&utc, &time_mutex[0], &too_far) == ENOTSUP &&
           pthread_mutex_trylock(&time_mutex[0]) == EBUSY &&
           pthread_cond_timedwait(&time_cond[0], &time_mutex[0], &too_far) ==
#ifdef AETHER_LONG_WAITS
               ETIMEDOUT && time_ns() >= future &&
#else
               EINVAL &&
#endif
           pthread_mutex_trylock(&time_mutex[0]) == EBUSY &&
           pthread_cond_timedwait(&time_cond[0], &time_mutex[0], &overflow) ==
               EOVERFLOW &&
           pthread_mutex_trylock(&time_mutex[0]) == EBUSY &&
           pthread_mutex_unlock(&time_mutex[0]) == 0 &&
           pthread_cond_destroy(&utc) == 0,
       341);
#endif
#endif
#ifdef PAIR_CONDITION
    // Only the exact private requeue subset is implemented by this adapter.
    PC(aether_wait_syscall(SYS_futex, (long)&pair_tokens, FUTEX_REQUEUE, 0, 1,
                           (long)&pair_mutex._m_lock, 0) == -ENOSYS &&
           aether_wait_syscall(SYS_futex, (long)&pair_tokens,
                               FUTEX_REQUEUE | FUTEX_PRIVATE, 1, 1,
                               (long)&pair_mutex._m_lock, 0) == -ENOSYS &&
           aether_wait_syscall(SYS_futex, (long)&pair_tokens,
                               FUTEX_REQUEUE | FUTEX_PRIVATE, 0, 2,
                               (long)&pair_mutex._m_lock, 0) == -ENOSYS &&
           aether_wait_syscall(SYS_futex, (long)&pair_tokens,
                               FUTEX_REQUEUE | FUTEX_PRIVATE, 0, 1,
                               (long)&pair_mutex._m_lock, 1) == -ENOSYS,
       240);
#endif
    long quota = memtrap(0x22000, memory_cap, 0, 0, 0);
    pthread_t self = pthread_self();
    unsigned yields = 0;
    for (unsigned batch = 0; batch < 2; ++batch) {
#ifdef PAIR_KEYS
        memset(key_records, 0, sizeof key_records);
        deleted_calls = 0;
        PC(pthread_key_create(&value_key, key_destructor) == 0 &&
               pthread_key_create(&loop_key, loop_destructor) == 0 &&
               pthread_key_create(&deleted_key, deleted_destructor) == 0,
           260);
        PC(pthread_setspecific(value_key, &parent_value) == 0 &&
               pthread_setspecific(deleted_key, &parent_value) == 0,
           261);
#endif
        pthread_t threads[2];
#ifdef PAIR_DETACHED
        pthread_attr_t detached;
        PC(pthread_attr_init(&detached) == 0 &&
               pthread_attr_setstacksize(&detached, 128 * 1024) == 0 &&
               pthread_attr_setguardsize(&detached, 4096) == 0 &&
               pthread_attr_setdetachstate(&detached,
                                           PTHREAD_CREATE_DETACHED) == 0,
           290);
#endif
        for (unsigned i = 0; i < 2; ++i) {
            entered[i] = gates[i] = errors[i] = 0;
            PC(pthread_create(&threads[i],
#ifdef PAIR_DETACHED
                              &detached,
#else
                              0,
#endif
                              pair_worker, (void *)(unsigned long)i) == 0,
               201 + i);
            PC(startups[i].id == parent_id + 2 + (batch * 2 + i) * 8, 203);
        }
        pthread_t rejected = (pthread_t)0x1234;
        long full_quota = memtrap(0x22000, memory_cap, 0, 0, 0);
        PC(pthread_create(&rejected, 0, pair_worker, 0) == EAGAIN &&
               rejected == (pthread_t)0x1234 &&
               memtrap(0x22000, memory_cap, 0, 0, 0) == full_quota,
           204);
        for (unsigned spin = 0; spin < 8 && (!entered[0] || !entered[1]);
             ++spin) {
            ++yields;
            memtrap(0x1fffe, 0, 0, 0, 0);
        }
        PC(entered[0] && entered[1] && used == 2 && libc.threads_minus_1 == 2,
           205);
#ifdef PAIR_KEYS
        PC(!key_records[0].calls && !key_records[1].calls &&
               pthread_getspecific(value_key) == &parent_value,
           262);
        PC(pthread_key_delete(deleted_key) == 0 && !deleted_calls &&
               pthread_key_create(&deleted_key, 0) == 0 &&
               !pthread_getspecific(deleted_key),
           264);
#endif
        errno = 71;
#ifdef PAIR_CONDITION
        pair_waits = pair_relocks = pair_returned = pair_requeues = 0;
        pair_tokens = 0;
#endif
#ifdef PAIR_RW
        rw_batch = batch;
        rw_waits = rw_arrived = rw_active = rw_writer = 0;
        if (batch) {
#ifndef LIFE_RW_BYPASS
            PC(pthread_rwlock_wrlock(&rw) == 0, 245);
#endif
            rw_writer = 1;
        }
#endif
#ifdef PAIR_TIME
        time_waits[0] = time_waits[1] = time_done[0] = time_done[1] = 0;
        time_error[0] = time_error[1] = time_relock = time_predicate = 0;
#endif
        gates[0] = gates[1] = 1;
#ifdef PAIR_TIME
        for (unsigned spin = 0; spin < 12 && (!time_waits[0] || !time_waits[1]);
             ++spin) {
            ++yields;
            memtrap(0x1fffe, 0, 0, 0, 0);
        }
        PC(time_waits[0] && time_waits[1] && !time_done[1], 277);
#ifdef LIFE_REAL_TIME
        // Wake without changing musl's barrier: it must retry the same
        // deadline.
        unsigned before_retry = time_waits[0];
        long woke = 0;
        for (unsigned spin = 0; spin < 8 && !woke; ++spin) {
            volatile int *word = time_words[0];
            PC(word, 339);
            woke = memtrap(0x28004, thread_cap, (uintptr_t)word, 0, 0);
            PC(woke >= 0, 339);
            if (!woke) {
                ++yields;
                memtrap(0x1fffe, 0, 0, 0, 0);
            }
        }
        PC(woke == 1, 339);
        for (unsigned spin = 0; spin < 8 && time_waits[0] == before_retry;
             ++spin) {
            ++yields;
            memtrap(0x1fffe, 0, 0, 0, 0);
        }
        PC(time_waits[0] > before_retry, 340);
#endif
        PC(pthread_mutex_lock(&time_mutex[1]) == 0, 278);
        time_predicate = 1;
        PC(pthread_cond_signal(&time_cond[1]) == 0, 279);
        for (unsigned spin = 0; spin < 8 && !time_relock; ++spin) {
            ++yields;
            memtrap(0x1fffe, 0, 0, 0, 0);
        }
        PC(time_relock && !time_done[1], 280);
        PC(pthread_mutex_unlock(&time_mutex[1]) == 0, 281);
#endif
#ifdef PAIR_RW
        if (!batch) {
            for (unsigned spin = 0; spin < 12 && rw_arrived < 2; ++spin) {
                ++yields;
                memtrap(0x1fffe, 0, 0, 0, 0);
            }
            PC(rw_arrived == 2 && rw_active == 2, 246);
            int before = rw._rw_lock;
            PC(pthread_rwlock_trywrlock(&rw) == EBUSY &&
                   rw._rw_lock == before && !rw._rw_waiters,
               247);
            PC(pthread_rwlock_wrlock(&rw) == 0 && !rw_active && rw_waits, 248);
            rw_writer = 1;
        } else {
            for (unsigned spin = 0; spin < 12 && rw_waits < 2 && !rw_arrived;
                 ++spin) {
                ++yields;
                memtrap(0x1fffe, 0, 0, 0, 0);
            }
            PC(!rw_arrived && !rw_active && rw_waits == 2, 251);
        }
        int before = rw._rw_lock;
        PC(pthread_rwlock_tryrdlock(&rw) == EBUSY && rw._rw_lock == before,
           249);
        rw_writer = 0;
        PC(pthread_rwlock_unlock(&rw) == 0, 250);
#endif
#ifdef PAIR_CONDITION
        for (unsigned spin = 0; spin < 12 && pair_waits < 2; ++spin) {
            ++yields;
            memtrap(0x1fffe, 0, 0, 0, 0);
        }
        PC(pair_waits == 2 && !pair_returned, 230);
        PC(pthread_mutex_lock(&pair_mutex) == 0, 231);
        unsigned before = pair_relocks;
        pair_tokens = batch ? 2 : 1;
        PC((batch ? pthread_cond_broadcast(&pair_condition)
                  : pthread_cond_signal(&pair_condition)) == 0,
           232);
        for (unsigned spin = 0; spin < 8 && pair_relocks == before; ++spin) {
            ++yields;
            memtrap(0x1fffe, 0, 0, 0, 0);
        }
        PC(!pair_returned && pair_relocks > before, 233);
        PC(pthread_mutex_unlock(&pair_mutex) == 0, 234);
        if (!batch) {
            for (unsigned spin = 0; spin < 12 && !pair_returned; ++spin) {
                ++yields;
                memtrap(0x1fffe, 0, 0, 0, 0);
            }
            PC(pair_returned == 1, 235);
            PC(pthread_mutex_lock(&pair_mutex) == 0 && !pair_tokens, 236);
            pair_tokens = 1;
            PC(pthread_cond_signal(&pair_condition) == 0 &&
                   pthread_mutex_unlock(&pair_mutex) == 0,
               237);
        }
#endif
#ifdef PAIR_DETACHED
        unsigned reaped = 0;
        for (unsigned spin = 0; spin < 24 && reaped != 2; ++spin) {
            for (unsigned i = 0; i < 2; ++i) {
                struct startup *slot = &startups[i];
                if (slot->thread && slot->pending && !slot->allow_exit) {
                    long before = memtrap(0x22000, memory_cap, 0, 0, 0);
                    PC(memtrap(0x2800b, thread_cap, slot->id, 0, 0) == 0, 292);
                    PC(reap_detached(i) == 0, 291);
                    PC(memtrap(0x22003, memory_cap, slot->map_base,
                               slot->map_bytes, 0) == -13 &&
                           memtrap(0x22000, memory_cap, 0, 0, 0) == before,
                       293);
                    slot->allow_exit = 1;
                }
            }
            for (unsigned i = 0; i < 2; ++i) {
                long done = reap_detached(i);
                PC(done >= 0, 294);
                reaped += (unsigned)done;
            }
            if (reaped != 2) {
                ++yields;
                memtrap(0x1fffe, 0, 0, 0, 0);
            }
        }
        PC(reaped == 2 && !used && pthread_attr_destroy(&detached) == 0, 295);
#else
        for (unsigned j = 0; j < 2; ++j) {
            unsigned i = batch ? j : 1 - j;
            void *value = 0;
            PC(pthread_join(threads[i], &value) == 0 &&
                   value == (void *)(0x500UL + i),
               206);
        }
#endif
#ifdef PAIR_CONDITION
        PC(pair_returned == 2 && !pair_tokens && !pair_condition._c_head &&
               !pair_condition._c_tail && !pair_condition._c_lock &&
               !pair_mutex._m_lock && !pair_mutex._m_waiters,
           238);
        PC(!batch || pair_requeues > 0, 239);
#endif
#ifdef PAIR_RW
        PC(rw_arrived == 2 && !rw_active && !rw_writer && !rw._rw_lock &&
               !rw._rw_waiters,
           252);
#endif
#ifdef PAIR_KEYS
        PC(key_records[0].calls == 2 && key_records[1].calls == 2, 263);
        PC(key_records[0].loops == PTHREAD_DESTRUCTOR_ITERATIONS &&
               key_records[1].loops == PTHREAD_DESTRUCTOR_ITERATIONS &&
               !key_records[0].error && !key_records[1].error &&
               !deleted_calls &&
               pthread_getspecific(value_key) == &parent_value &&
               !pthread_getspecific(loop_key),
           265);
        PC(pthread_key_delete(value_key) == 0 &&
               pthread_key_delete(loop_key) == 0 &&
               pthread_key_delete(deleted_key) == 0 && !deleted_calls,
           266);
#endif
#ifdef PAIR_TIME
        PC(time_error[0] != 2, 271);
        PC(!time_error[0] && !time_error[1] && time_done[0] && time_done[1] &&
               !time_cond[0]._c_head && !time_cond[1]._c_head &&
               !time_cond[0]._c_tail && !time_cond[1]._c_tail &&
               !time_mutex[0]._m_waiters && !time_mutex[1]._m_waiters,
           272);
#endif
        PC(!used && !errors[0] && !errors[1] && cookie == 17 && errno == 71,
           207);
        PC(!libc.threads_minus_1 && self->next == self && self->prev == self &&
               !__thread_list_lock &&
               memtrap(0x22000, memory_cap, 0, 0, 0) == quota,
           208);
    }
    pthread_t rejected = (pthread_t)0x1234;
    PC(
#ifndef PAIR_DETACHED
        waits_entered > 0 &&
#endif
            admissions == 4 &&
            pthread_create(&rejected, 0, pair_worker, 0) == EAGAIN &&
            rejected == (pthread_t)0x1234,
        209);
    PC(yields <= 64, 210);
    for (; yields < 64; ++yields)
        memtrap(0x1fffe, 0, 0, 0, 0);
    PC(write(1, "AETHER MUSL NATIVE PASS\n", 24) == 16, 220);
    PC(write(1, &"AETHER MUSL NATIVE PASS\n"[16], 8) == 8, 221);
    return 0;
}
#endif
