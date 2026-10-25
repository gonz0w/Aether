/* SPDX-License-Identifier: BSD-2-Clause */
#include "runtime.h"
#include "adapter.h"
#include <errno.h>
#include <limits.h>
#include <pthread.h>
#include <stdint.h>
#include <time.h>
#include <string.h>

static _Thread_local volatile unsigned cookie = 19;
static pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t condition;
static _Atomic unsigned ready, done;
static unsigned release;
static struct timespec deadline;
static void yield(void) { memtrap(0x1fffe, 0, 0, 0, 0); }
static int expired(void)
{
    struct timespec now;
    return clock_gettime(CLOCK_MONOTONIC, &now) ||
           now.tv_sec > deadline.tv_sec ||
           (now.tv_sec == deadline.tv_sec && now.tv_nsec >= deadline.tv_nsec);
}
static void *blocked(void *unused)
{
    (void)unused;
    if (cookie != 19)
        return (void *)728;
    cookie = 41;
    if (pthread_mutex_lock(&mutex))
        return (void *)701;
    ++ready;
    while (!release) {
        if (pthread_cond_timedwait(&condition, &mutex, &deadline)) {
            pthread_mutex_unlock(&mutex);
            return (void *)702;
        }
    }
    if (pthread_mutex_unlock(&mutex))
        return (void *)703;
    ++done;
    return 0;
}
static _Atomic unsigned relay_start;
static void *detached_exit(void *unused)
{
    (void)unused;
    if (cookie != 19)
        __builtin_trap();
    cookie = 41;
    while (!relay_start) {
        if (expired())
            __builtin_trap();
        yield();
    }
    return 0;
}
static void *relay(void *unused)
{
    (void)unused;
    pthread_attr_t attr;
    pthread_t detached;
    if (pthread_attr_init(&attr) ||
        pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_DETACHED) ||
        pthread_create(&detached, &attr, detached_exit, 0) ||
        pthread_attr_destroy(&attr))
        return (void *)730;
    void *untouched = (void *)17;
    if (pthread_join(detached, &untouched) != EINVAL || untouched != (void *)17)
        return (void *)735;
    relay_start = 1;
    /* Primary is blocked joining this creator. Reaper must settle the child. */
    while (aether_runtime_live() != 2) {
        if (expired())
            return (void *)731;
        yield();
    }
    return 0;
}
int main(int argc, char **argv)
{
    if (argc != 2 || !argv || aether_runtime_init())
        return 700;
    unsigned count = argv[0][11] == '1' ? 81 : 1;
    pthread_condattr_t attr;
    if (pthread_condattr_init(&attr) ||
        pthread_condattr_setclock(&attr, CLOCK_MONOTONIC) ||
        pthread_cond_init(&condition, &attr) || pthread_condattr_destroy(&attr))
        return 704;
    pthread_mutexattr_t ma;
    pthread_mutex_t unsupported, saved;
    memset(&unsupported, 0xa5, sizeof unsupported);
    saved = unsupported;
    if (pthread_mutexattr_init(&ma) ||
        pthread_mutexattr_setrobust(&ma, PTHREAD_MUTEX_ROBUST) != ENOSYS ||
        ma.__attr)
        return 741;
    if (pthread_mutexattr_settype(&ma, PTHREAD_MUTEX_ERRORCHECK) ||
        pthread_mutex_init(&unsupported, &ma) != ENOTSUP ||
        memcmp(&unsupported, &saved, sizeof saved) ||
        pthread_mutexattr_destroy(&ma))
        return 736;
    pthread_condattr_t ca;
    pthread_cond_t shared, saved_cond;
    memset(&shared, 0xa5, sizeof shared);
    saved_cond = shared;
    if (pthread_condattr_init(&ca) ||
        pthread_condattr_setpshared(&ca, PTHREAD_PROCESS_SHARED) ||
        pthread_cond_init(&shared, &ca) != ENOTSUP ||
        memcmp(&shared, &saved_cond, sizeof shared) ||
        pthread_condattr_destroy(&ca))
        return 737;
    pthread_rwlockattr_t ra;
    pthread_rwlock_t rw, saved_rw;
    memset(&rw, 0xa5, sizeof rw);
    saved_rw = rw;
    if (pthread_rwlockattr_init(&ra) ||
        pthread_rwlockattr_setpshared(&ra, PTHREAD_PROCESS_SHARED) ||
        pthread_rwlock_init(&rw, &ra) != ENOTSUP ||
        memcmp(&rw, &saved_rw, sizeof rw) || pthread_rwlockattr_destroy(&ra))
        return 738;
    pthread_mutex_t recursive = PTHREAD_MUTEX_INITIALIZER;
    /* Craft the unsupported type tag exposed by this pinned musl header. */
    recursive.__u.__i[0] = PTHREAD_MUTEX_RECURSIVE;
    if (pthread_mutex_lock(&recursive) != ENOTSUP ||
        pthread_mutex_trylock(&recursive) != ENOTSUP ||
        pthread_mutex_unlock(&recursive) != ENOTSUP)
        return 739;
    void *join_sentinel = (void *)17;
    if (pthread_tryjoin_np(pthread_self(), &join_sentinel) != ENOTSUP ||
        pthread_timedjoin_np(pthread_self(), &join_sentinel, &deadline) !=
            ENOTSUP ||
        join_sentinel != (void *)17)
        return 740;
    struct timespec invalid = {0, 1000000000}, huge = {LONG_MAX, 0};
    if (clock_nanosleep(CLOCK_MONOTONIC, 0, &invalid, 0) != EINVAL ||
        clock_nanosleep(CLOCK_MONOTONIC, 0, &huge, 0) != EOVERFLOW ||
        clock_nanosleep(CLOCK_REALTIME, TIMER_ABSTIME, &invalid, 0) != ENOTSUP)
        return 705;
    struct timespec untouched = {77, 88};
    errno = 73;
    if (clock_gettime(CLOCK_REALTIME, &untouched) != -1 || errno != ENOTSUP ||
        untouched.tv_sec != 77 || untouched.tv_nsec != 88)
        return 706;
    if (clock_gettime(CLOCK_MONOTONIC, &deadline))
        return 707;
    deadline.tv_sec += 2;
    errno = 73;
    if (clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &deadline, 0) ||
        errno != 73 || !expired())
        return 708;
    if (clock_gettime(CLOCK_MONOTONIC, &deadline))
        return 709;
    deadline.tv_sec += 8;
    pthread_t workers[81], sentinel = (pthread_t)0x1234;
    for (unsigned i = 0; i < count; ++i)
        if (pthread_create(&workers[i], 0, blocked, 0))
            return 710;
    while (ready != count) {
        if (expired())
            return 711;
        yield();
    }
    if (aether_runtime_live() != count + 1 ||
        pthread_create(&sentinel, 0, blocked, 0) != EAGAIN ||
        sentinel != (pthread_t)0x1234)
        return 712;
    if (pthread_mutex_lock(&mutex) || pthread_cond_broadcast(&condition))
        return 713;
    /* A broadcast without predicate change must preserve the original deadline.
     */
    if (pthread_mutex_unlock(&mutex))
        return 714;
    for (unsigned i = 0; i < 100; ++i)
        yield();
    if (done || pthread_mutex_lock(&mutex))
        return 715;
    release = 1;
    if (pthread_cond_broadcast(&condition))
        return 716;
    struct timespec delay = {0, 200000000};
    if (nanosleep(&delay, 0) || done || pthread_mutex_unlock(&mutex))
        return 717;
    for (unsigned i = 0; i < count; ++i) {
        void *result = (void *)1;
        if (pthread_join(workers[i], &result) || result)
            return result ? (int)(uintptr_t)result : 718;
    }
    if (done != count || aether_runtime_live() != 1)
        return 719;
    if (count == 81) {
        for (unsigned cycle = 0; cycle < 16; ++cycle) {
            relay_start = 0;
            if (clock_gettime(CLOCK_MONOTONIC, &deadline))
                return 732;
            deadline.tv_sec += 3;
            if (pthread_create(&workers[0], 0, relay, 0))
                return 733;
            void *result = (void *)1;
            if (pthread_join(workers[0], &result) || result ||
                aether_runtime_live() != 1)
                return result ? (int)(uintptr_t)result : 734;
        }
    }
    ready = done = release = 0;
    if (clock_gettime(CLOCK_MONOTONIC, &deadline))
        return 720;
    deadline.tv_sec += 4;
    if (pthread_create(&workers[0], 0, blocked, 0))
        return 721;
    while (!ready) {
        if (expired())
            return 722;
        yield();
    }
    if (aether_runtime_finish() != EBUSY ||
        pthread_create(&sentinel, 0, blocked, 0) != EAGAIN ||
        sentinel != (pthread_t)0x1234)
        return 723;
    if (pthread_mutex_lock(&mutex))
        return 724;
    release = 1;
    if (pthread_cond_signal(&condition) || pthread_mutex_unlock(&mutex))
        return 725;
    void *result = (void *)1;
    if (pthread_join(workers[0], &result) || result ||
        aether_runtime_finish() || aether_runtime_live())
        return 726;
    if (pthread_cond_destroy(&condition) || pthread_mutex_destroy(&mutex))
        return 727;
    return 0;
}
