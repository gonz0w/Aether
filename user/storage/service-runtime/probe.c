/* SPDX-License-Identifier: BSD-2-Clause */
/* Independent consumer of the delivered runtime. All arguments, pthread
 * handles and condition words are owner-local borrows. Atomics publish only
 * readiness/completion; the condition predicate is protected by its mutex. */
#include "runtime.h"
#include <errno.h>
#include <pthread.h>
#include <stdint.h>
#include <sys/auxv.h>
#include <time.h>

#define CHECK(x, code)                                                         \
    do {                                                                       \
        if (!(x))                                                              \
            return (code);                                                     \
    } while (0)
static _Thread_local unsigned cookie = 23;
static pthread_key_t key;
static pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t condition;
static struct timespec deadline;
static _Atomic unsigned ready, done, destructors;

static long trap(unsigned long op, unsigned long a)
{
    unsigned long zero = 0;
    __asm__ volatile("int $0x81"
                     : "+a"(op), "+d"(zero)
                     : "D"(a), "S"(0UL)
                     : "rcx", "r8", "r9", "r10", "r11", "memory", "cc");
    return (long)op;
}
static int now(struct timespec *out)
{
    return clock_gettime(CLOCK_MONOTONIC, out);
}
static int expired(const struct timespec *at)
{
    struct timespec current;
    if (now(&current))
        return -1;
    return current.tv_sec > at->tv_sec ||
           (current.tv_sec == at->tv_sec && current.tv_nsec >= at->tv_nsec);
}
static void destructor(void *value)
{
    if (value != (void *)29 || cookie != 47 || pthread_getspecific(key))
        __builtin_trap();
    ++destructors;
}
static void *worker(void *argument)
{
    unsigned mode = (uintptr_t)argument;
    if (cookie != 23 || errno || pthread_setspecific(key, (void *)29))
        return (void *)801;
    cookie = 47;
    errno = 71;
    if (mode != 1) {
        if (pthread_mutex_lock(&mutex))
            return (void *)801;
        ++ready;
        int result = pthread_cond_timedwait(&condition, &mutex, &deadline);
        if (result != ETIMEDOUT || expired(&deadline) != 1)
            return (void *)802;
        if (pthread_mutex_trylock(&mutex) != EBUSY ||
            pthread_mutex_unlock(&mutex))
            return (void *)803;
        if (mode == 0) {
            struct timespec duration = {0, 200000000}, rem = {31, 37};
            if (nanosleep(&duration, &rem) || rem.tv_sec != 31 ||
                rem.tv_nsec != 37)
                return (void *)803;
        }
    }
    if (errno != 71)
        return (void *)803;
    ++done;
    return 0;
}
int main(void)
{
    CHECK(!aether_runtime_init() && aether_runtime_live() == 1 &&
              aether_runtime_admissions() == 1 &&
              aether_runtime_init() == EALREADY,
          800);
    unsigned long memory = getauxval(0xa000);
    /* Both fixture owners use the same memory selector. Read its checked grant.
     */
    unsigned long op = 0x22000;
    unsigned long ignored = 0;
    register unsigned long total __asm__("r8") = 0;
    register unsigned long reserved __asm__("r9") = 0;
    register unsigned long extra __asm__("r10") = 0;
    __asm__ volatile("int $0x81"
                     : "+a"(op), "+r"(total), "+d"(ignored), "+r"(reserved),
                       "+r"(extra)
                     : "D"(memory), "S"(0UL)
                     : "rcx", "r11", "memory", "cc");
    CHECK((long)op >= 0 && (total == 8192 || total == 128), 800);
    unsigned count = total == 8192 ? 81 : 1;
    CHECK(!now(&deadline), 804);
    deadline.tv_sec += 2;
    pthread_condattr_t attr;
    CHECK(!pthread_condattr_init(&attr) &&
              !pthread_condattr_setclock(&attr, CLOCK_MONOTONIC) &&
              !pthread_cond_init(&condition, &attr) &&
              !pthread_condattr_destroy(&attr) &&
              !pthread_key_create(&key, destructor),
          805);
    pthread_t child;
    CHECK(!pthread_create(&child, 0, worker, 0), 806);
    void *result = (void *)17;
    CHECK(!pthread_join(child, &result), 806);
    CHECK(!result, result ? (int)(uintptr_t)result : 806);
    CHECK(aether_runtime_live() == 1 && cookie == 23 && done == 1 &&
              destructors == 1,
          807);
    pthread_attr_t detached;
    CHECK(
        !pthread_attr_init(&detached) &&
            !pthread_attr_setdetachstate(&detached, PTHREAD_CREATE_DETACHED) &&
            !pthread_create(&child, &detached, worker, (void *)1) &&
            !pthread_attr_destroy(&detached),
        808);
    CHECK(!now(&deadline), 804);
    ++deadline.tv_sec;
    while (aether_runtime_live() != 1) {
        CHECK(expired(&deadline) == 0, 809);
        trap(0x1fffe, 0);
    }
    CHECK(done == 2 && destructors == 2, 810);
    ready = done = 0;
    CHECK(!now(&deadline), 804);
    deadline.tv_sec += 3;
    pthread_t workers[81], sentinel = (pthread_t)0x1234;
    for (unsigned i = 0; i < count; ++i)
        CHECK(!pthread_create(&workers[i], 0, worker, (void *)2), 811);
    CHECK(pthread_create(&sentinel, 0, worker, (void *)2) == EAGAIN &&
              sentinel == (pthread_t)0x1234,
          812);
    while (ready != count) {
        CHECK(expired(&deadline) == 0, 813);
        trap(0x1fffe, 0);
    }
#ifdef STOP_LIVE
    if (count == 81 && trap(0x20005, 0) == 1) {
        struct timespec duration = {1, 100000000};
        CHECK(!nanosleep(&duration, 0) && !done, 814);
        CHECK(!trap(0x20004, 0), 814);
        for (;;)
            trap(0x1fffe, 0);
    }
#endif
    CHECK(aether_runtime_live() == count + 1 &&
              aether_runtime_finish() == EBUSY,
          815);
    CHECK(pthread_create(&sentinel, 0, worker, 0) == EAGAIN &&
              sentinel == (pthread_t)0x1234,
          816);
    for (unsigned i = 0; i < count; ++i) {
        result = (void *)17;
        CHECK(!pthread_join(workers[i], &result), 817);
        CHECK(!result, result ? (int)(uintptr_t)result : 817);
    }
    CHECK(done == count && destructors == count + 2 && cookie == 23 &&
              aether_runtime_live() == 1 &&
              aether_runtime_admissions() == count + 3,
          818);
    CHECK(!pthread_key_delete(key) && !pthread_cond_destroy(&condition) &&
              !pthread_mutex_destroy(&mutex),
          819);
    CHECK(!aether_runtime_finish() && !aether_runtime_live() &&
              aether_runtime_admissions() == count + 3,
          820);
    CHECK(pthread_create(&sentinel, 0, worker, 0) == EAGAIN &&
              sentinel == (pthread_t)0x1234,
          821);
    return 0;
}
