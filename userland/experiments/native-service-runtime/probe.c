/* SPDX-License-Identifier: BSD-2-Clause */
#include "runtime.h"
#include "adapter.h"
#include <errno.h>
#include <limits.h>
#include <pthread.h>
#include <stdlib.h>
#include <sys/auxv.h>
#include <time.h>

#define CHECK(x, n)                                                            \
    do {                                                                       \
        if (!(x))                                                              \
            return (void *)(unsigned long)(n);                                 \
    } while (0)
static _Thread_local unsigned cookie = 19;
static pthread_key_t key;
static _Atomic unsigned destructors, done;
static pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t condition;
#if !defined(DISABLED) && !defined(EARLY)
static unsigned predicate;
#endif
static struct timespec deadline;
static void destructor(void *value)
{
    if (value != (void *)17 || cookie != 41 || pthread_getspecific(key))
        __builtin_trap();
    ++destructors;
}
static void *worker(void *argument)
{
    CHECK(cookie == 19 && !errno, 601);
    cookie = 41;
    errno = 73;
    CHECK(!pthread_setspecific(key, (void *)17), 602);
    CHECK(!pthread_mutex_lock(&mutex), 603);
    int status = pthread_cond_timedwait(&condition, &mutex, &deadline);
#ifdef EARLY
    CHECK(status == EIO, 604);
#elif defined(DISABLED)
    CHECK(status == ENOSYS, 604);
#else
    CHECK(status == ETIMEDOUT || (status == 0 && predicate), 604);
    if (status == ETIMEDOUT) {
        struct timespec now;
        CHECK(!clock_gettime(CLOCK_MONOTONIC, &now), 605);
        CHECK(now.tv_sec > deadline.tv_sec || (now.tv_sec == deadline.tv_sec &&
                                               now.tv_nsec >= deadline.tv_nsec),
              605);
    }
#endif
    CHECK(pthread_mutex_trylock(&mutex) == EBUSY &&
              !pthread_mutex_unlock(&mutex),
          606);
#ifndef DISABLED
#ifdef EARLY
    struct timespec sleep = {2, 0}, rem = {77, 88};
#else
    struct timespec sleep = {0, 200000000}, rem = {77, 88};
#endif
#ifdef EARLY
    CHECK(nanosleep(&sleep, &rem) == -1 && errno == EIO, 607);
    errno = 73;
#else
    CHECK(!nanosleep(&sleep, &rem) && errno == 73, 607);
#endif
    CHECK(rem.tv_sec == 77 && rem.tv_nsec == 88, 607);
#endif
    CHECK(errno == 73, 608);
    ++done;
    return argument;
}
static void *creator(void *unused)
{
    (void)unused;
    pthread_t child;
    CHECK(!pthread_create(&child, 0, worker, 0), 609);
    void *result = (void *)1;
    CHECK(!pthread_join(child, &result) && !result, 609);
    return 0;
}
#if !defined(DISABLED) && !defined(EARLY)
static void yield(void) { memtrap(0x1fffe, 0, 0, 0, 0); }
#endif
int main(int argc, char **argv)
{
    if (argc != 2 || !argv || aether_runtime_init())
        return 600;
    if (aether_runtime_live() != 1 || aether_runtime_init() != EALREADY)
        return 610;
    unsigned large = argv[0][11] == '1';
    pthread_condattr_t attr;
    if (pthread_condattr_init(&attr) ||
        pthread_condattr_setclock(&attr, CLOCK_MONOTONIC) ||
        pthread_cond_init(&condition, &attr) ||
        pthread_condattr_destroy(&attr) || pthread_key_create(&key, destructor))
        return 611;
    pthread_attr_t thread_attr;
    pthread_attr_init(&thread_attr);
    pthread_attr_setstack(&thread_attr, (void *)0x1234, 65536);
    pthread_t sentinel = (pthread_t)0x1234;
    if (pthread_create(&sentinel, &thread_attr, worker, 0) != ENOTSUP ||
        sentinel != (pthread_t)0x1234)
        return 612;
    pthread_attr_destroy(&thread_attr);
    if (pthread_cancel(pthread_self()) != ENOTSUP ||
        pthread_detach(pthread_self()) != ENOTSUP)
        return 613;
    for (unsigned cycle = 0; cycle < 3; ++cycle) {
#ifdef DISABLED
        deadline = (struct timespec){0, 100000000};
#else
        if (clock_gettime(CLOCK_MONOTONIC, &deadline))
            return 614;
#ifdef EARLY
        deadline.tv_sec += 2;
#endif
        deadline.tv_nsec += 200000000;
        if (deadline.tv_nsec >= 1000000000) {
            ++deadline.tv_sec;
            deadline.tv_nsec -= 1000000000;
        }
#endif
        pthread_t child;
        if (pthread_create(&child, 0, large && cycle == 0 ? creator : worker,
                           0))
            return 615;
        void *result = (void *)1;
        if (pthread_join(child, &result) || result)
            return result ? (int)(uintptr_t)result : 616;
        if (aether_runtime_live() != 1 || cookie != 19)
            return 617;
    }
#ifndef DISABLED
#ifndef EARLY
    if (large) {
        if (clock_gettime(CLOCK_MONOTONIC, &deadline))
            return 618;
        deadline.tv_sec += 1;
        pthread_t detached;
        pthread_attr_init(&thread_attr);
        pthread_attr_setdetachstate(&thread_attr, PTHREAD_CREATE_DETACHED);
        if (pthread_create(&detached, &thread_attr, worker, 0))
            return 619;
        pthread_attr_destroy(&thread_attr);
        struct timespec limit = deadline, now;
        limit.tv_sec += 3;
        do {
            yield();
            if (clock_gettime(CLOCK_MONOTONIC, &now))
                return 624;
            if (now.tv_sec > limit.tv_sec ||
                (now.tv_sec == limit.tv_sec && now.tv_nsec >= limit.tv_nsec))
                return 625;
        } while (done != 4 || aether_runtime_live() != 1);
        if (aether_runtime_live() != 1 || done != 4 || destructors != 4)
            return 620;
    }
#endif
#endif
    if (pthread_key_delete(key) || pthread_cond_destroy(&condition) ||
        pthread_mutex_destroy(&mutex))
        return 621;
    if (aether_runtime_finish() || aether_runtime_live())
        return 622;
    if (pthread_create(&sentinel, 0, worker, 0) != EAGAIN ||
        sentinel != (pthread_t)0x1234)
        return 623;
    return 0;
}
