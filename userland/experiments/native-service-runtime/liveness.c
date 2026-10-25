/* SPDX-License-Identifier: BSD-2-Clause */
/* Focused runtime/UTC helper lifetime witness, not an OpenZFS engine replay. */
#include "runtime.h"
#include "utc.h"
#include "adapter.h"
#include <errno.h>
#include <pthread.h>
#include <stdint.h>
#include <sys/auxv.h>
#include <time.h>
#define CHECK(x, n)                                                            \
    do {                                                                       \
        if (!(x))                                                              \
            return (n);                                                        \
    } while (0)
static _Thread_local volatile unsigned cookie = 17;
#ifndef RTC_DISABLED
static _Atomic unsigned done, destructors;
static pthread_key_t key;
static pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t condition;
static struct timespec at;
static void destructor(void *value)
{
    if (value != (void *)19 || cookie != 23)
        __builtin_trap();
    ++destructors;
}
static int stamp(void)
{
    struct timespec t;
    errno = 73;
    return clock_gettime(CLOCK_REALTIME, &t) || errno != 73 ||
           t.tv_sec < UTC_EXPECTED || t.tv_sec > UTC_EXPECTED + 30 ||
           t.tv_nsec < 0 || t.tv_nsec >= 1000000000;
}
static void *worker(void *detached)
{
    if (cookie != 17 || stamp() || pthread_setspecific(key, (void *)19))
        return (void *)871;
    cookie = 23;
    if (!detached) {
        if (pthread_mutex_lock(&mutex))
            return (void *)872;
        int result = pthread_cond_timedwait(&condition, &mutex, &at);
        if (result != ETIMEDOUT || pthread_mutex_trylock(&mutex) != EBUSY ||
            pthread_mutex_unlock(&mutex))
            return (void *)873;
    } else {
        struct timespec pause = {0, 1000000};
        if (nanosleep(&pause, 0))
            return (void *)874;
    }
    if (stamp())
        return (void *)875;
    ++done;
    return 0;
}
static int collect_detached(unsigned target)
{
    struct timespec deadline, current, pause = {0, 1000000};
    if (clock_gettime(CLOCK_MONOTONIC, &deadline))
        return 876;
    deadline.tv_sec += 2;
    while (aether_runtime_live() != 1) {
        if (clock_gettime(CLOCK_MONOTONIC, &current) ||
            current.tv_sec > deadline.tv_sec ||
            (current.tv_sec == deadline.tv_sec &&
             current.tv_nsec >= deadline.tv_nsec) ||
            nanosleep(&pause, 0))
            return 876;
    }
    return done == target && destructors == target ? 0 : 877;
}
#endif
int main(void)
{
    CHECK(cookie == 17 && !aether_runtime_init(), 870);
    int error = EAGAIN;
    for (unsigned i = 0; i < 16 && error == EAGAIN; ++i) {
        error = aether_utc_establish(1);
        if (error == EAGAIN) {
            struct timespec pause = {0, 1000000};
            CHECK(!nanosleep(&pause, 0), 870);
        }
    }
#ifdef RTC_DISABLED
    CHECK(error == ENOSYS && !aether_runtime_finish(), 870);
    return 856;
#else
    CHECK(!error && !stamp(), 870);
    unsigned long op = 0x22000, ignored = 0;
    register unsigned long total __asm__("r8") = 0;
    register unsigned long extra __asm__("r10") = 0;
    register unsigned long reserved __asm__("r9") = 0;
    __asm__ volatile("int $0x81"
                     : "+a"(op), "+d"(ignored), "+r"(total), "+r"(extra),
                       "+r"(reserved)
                     : "D"(getauxval(0xa000)), "S"(0UL)
                     : "rcx", "r11", "memory", "cc");
    CHECK((long)op >= 0 && (total == 8192 || total == 128), 870);
    unsigned count = total == 8192 ? 8 : 1;
    pthread_condattr_t attr;
    CHECK(!pthread_condattr_init(&attr) &&
              !pthread_condattr_setclock(&attr, CLOCK_MONOTONIC) &&
              !pthread_cond_init(&condition, &attr) &&
              !pthread_condattr_destroy(&attr) &&
              !pthread_key_create(&key, destructor),
          870);
    for (unsigned wave = 0; wave < 8; ++wave) {
        CHECK(!clock_gettime(CLOCK_MONOTONIC, &at), 878);
        at.tv_nsec += 10000000;
        if (at.tv_nsec >= 1000000000) {
            ++at.tv_sec;
            at.tv_nsec -= 1000000000;
        }
        pthread_t cohort[8];
        for (unsigned i = 0; i < count; ++i)
            CHECK(!pthread_create(&cohort[i], 0, worker, 0), 878);
#ifdef STOP_LIVE
        if (wave == 0 && total == 8192 && memtrap(0x20005, 0, 0, 0, 0) == 1) {
            CHECK(!memtrap(0x20004, 0, 0, 0, 0), 878);
            for (;;)
                memtrap(0x1fffe, 0, 0, 0, 0);
        }
#endif
        for (unsigned i = count; i > 0; --i) {
            void *result = (void *)1;
            CHECK(!pthread_join(cohort[i - 1], &result) && !result, 879);
        }
        CHECK(aether_runtime_live() == 1 && done == (wave + 1) * count &&
                  destructors == done && !stamp(),
              880);
    }
    pthread_attr_t detached;
    CHECK(!pthread_attr_init(&detached) &&
              !pthread_attr_setdetachstate(&detached, PTHREAD_CREATE_DETACHED),
          881);
    for (unsigned round = 0; round < 32; ++round) {
        pthread_t thread;
        CHECK(!pthread_create(&thread, &detached, worker, (void *)1), 882);
        CHECK(!collect_detached(count * 8 + round + 1), 883);
    }
    CHECK(aether_runtime_admissions() == count * 8 + 33 &&
              !pthread_attr_destroy(&detached) && !pthread_key_delete(key) &&
              !pthread_cond_destroy(&condition) &&
              !pthread_mutex_destroy(&mutex) && !aether_utc_close() &&
              !aether_runtime_finish() && !aether_runtime_live() &&
              cookie == 17,
          884);
    return 0;
#endif
}
