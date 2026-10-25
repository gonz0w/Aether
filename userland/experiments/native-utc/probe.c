/* SPDX-License-Identifier: BSD-2-Clause */
#include "utc.h"
#include "runtime.h"
#include "adapter.h"
#include <errno.h>
#include <pthread.h>
#include <string.h>
#include <sys/auxv.h>
#include <sys/time.h>
#define CHECK(x, n)                                                            \
    do {                                                                       \
        if (!(x))                                                              \
            return (n);                                                        \
    } while (0)
static _Thread_local volatile unsigned cookie = 17;
#if !defined(ABSENT_POLICY) && !defined(RTC_DISABLED)
static _Atomic unsigned ready, release;
static struct timespec first;
#endif
static int check_wrappers(int error)
{
    struct timespec t = {17, 23};
    struct timeval tv = {19, 29};
    time_t seconds = 31;
    errno = 73;
    CHECK(clock_gettime(CLOCK_REALTIME, &t) == -1 && errno == error &&
              t.tv_sec == 17 && t.tv_nsec == 23,
          851);
    CHECK(time(&seconds) == -1 && errno == error && seconds == 31, 852);
    CHECK(gettimeofday(&tv, 0) == -1 && errno == error && tv.tv_sec == 19 &&
              tv.tv_usec == 29,
          853);
    return 0;
}
#if !defined(ABSENT_POLICY) && !defined(RTC_DISABLED)
static void *worker(void *unused)
{
    (void)unused;
    errno = 73;
    struct timespec wall, mono;
    if (cookie != 17 || aether_utc_establish(1) != EPERM ||
        aether_utc_close() != EPERM || clock_gettime(CLOCK_REALTIME, &wall) ||
        errno != 73 || clock_gettime(CLOCK_MONOTONIC, &mono) ||
        wall.tv_sec < first.tv_sec || wall.tv_sec > first.tv_sec + 5 ||
        wall.tv_nsec < 0 || wall.tv_nsec >= 1000000000 ||
        wall.tv_sec < UTC_EXPECTED || wall.tv_sec > UTC_EXPECTED + 30)
        return (void *)857;
    ++ready;
    while (!release)
        memtrap(0x1fffe, 0, 0, 0, 0);
    return 0;
}
#endif
int main(void)
{
    CHECK(cookie == 17 && !check_wrappers(ENODATA), 851);
    CHECK(aether_utc_establish(0) == ENOTSUP, 854);
    int before_init = aether_utc_establish(1);
    CHECK(before_init == EBUSY, 900 + before_init);
    CHECK(!aether_runtime_init(), 850);
#ifdef ABSENT_POLICY
    CHECK(aether_utc_establish(0) == ENOTSUP && !check_wrappers(ENODATA), 854);
    CHECK(!aether_runtime_finish(), 850);
    return 855;
#else
    int established = EAGAIN;
    for (unsigned retry = 0; retry < 16 && established == EAGAIN; ++retry) {
        established = aether_utc_establish(1);
        if (established == EAGAIN) {
            struct timespec pause = {0, 1000000};
            CHECK(!nanosleep(&pause, 0), 866);
        }
    }
#ifdef RTC_DISABLED
    CHECK(established == ENOSYS && !check_wrappers(ENODATA), 854);
    CHECK(!aether_runtime_finish(), 850);
    return 856;
#else
    CHECK(!established, 1000 + established);
    CHECK(aether_utc_establish(1) == EALREADY, 854);
    errno = 73;
    CHECK(!clock_gettime(CLOCK_REALTIME, &first) && errno == 73 &&
              first.tv_sec >= UTC_EXPECTED && first.tv_sec <= UTC_EXPECTED + 30,
          858);
    struct timeval tv;
    time_t seconds = 0;
    CHECK(time(&seconds) >= first.tv_sec && seconds >= first.tv_sec &&
              !gettimeofday(&tv, 0) && tv.tv_sec >= first.tv_sec && errno == 73,
          859);
    struct timespec req = {first.tv_sec + 1, 0}, rem = {31, 37};
    CHECK(clock_nanosleep(CLOCK_REALTIME, TIMER_ABSTIME, &req, &rem) ==
                  ENOTSUP &&
              rem.tv_sec == 31 && rem.tv_nsec == 37,
          859);
    pthread_t threads[1];
    CHECK(!pthread_create(&threads[0], 0, worker, 0), 860);
    struct timespec deadline;
    CHECK(!clock_gettime(CLOCK_MONOTONIC, &deadline), 860);
    deadline.tv_sec += 3;
    while (ready != 1) {
        struct timespec current;
        CHECK(!clock_gettime(CLOCK_MONOTONIC, &current) &&
                  current.tv_sec < deadline.tv_sec,
              860);
        memtrap(0x1fffe, 0, 0, 0, 0);
    }
    CHECK(aether_utc_close() == EBUSY, 861);
    release = 1;
    void *result = (void *)1;
    CHECK(!pthread_join(threads[0], &result) && !result, 862);
    struct timespec pause = {0, 200000000}, later;
    CHECK(!nanosleep(&pause, 0) && !clock_gettime(CLOCK_REALTIME, &later) &&
              (later.tv_sec > first.tv_sec || (later.tv_sec == first.tv_sec &&
                                               later.tv_nsec >= first.tv_nsec)),
          863);
    CHECK(!aether_utc_close() && !check_wrappers(ENODATA) &&
              aether_utc_establish(1) == EALREADY &&
              aether_utc_close() == ENODATA,
          864);
    CHECK(!aether_runtime_finish(), 865);
    return 0;
#endif
#endif
}
