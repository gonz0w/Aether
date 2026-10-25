/* SPDX-License-Identifier: BSD-2-Clause */
/* Caller timespec pointers are valid in-process libc borrows. The kernel owns
 * wait-word validation/pinning. No pointer is retained after this call returns.
 */
#include "adapter.h"
#include "real_time.h"
#include <errno.h>
#include <limits.h>
#include <stdint.h>
#include <sys/auxv.h>
#include <sys/syscall.h>

#define SECOND 1000000000UL
static long observe(void)
{
    return memtrap(0x2800f, getauxval(0xa001), 0, 0, 0);
}
int __clock_gettime(clockid_t id, struct timespec *out)
{
    if (id != CLOCK_MONOTONIC) {
        errno = ENOTSUP;
        return -1;
    }
    long now = observe();
    if (now < 0) {
        errno = -now;
        return -1;
    }
    *out = (struct timespec){now / SECOND, now % SECOND};
    return 0;
}
int clock_gettime(clockid_t id, struct timespec *out)
{
    return __clock_gettime(id, out);
}
/* Do not multiply before proving signed nanosecond representability. */
static int nanoseconds(const struct timespec *t, unsigned long *out)
{
    if (t->tv_nsec < 0 || t->tv_nsec >= (long)SECOND || t->tv_sec < 0)
        return EINVAL;
    if ((unsigned long)t->tv_sec > LONG_MAX / SECOND ||
        (unsigned long)t->tv_nsec >
            LONG_MAX - (unsigned long)t->tv_sec * SECOND)
        return EOVERFLOW;
    *out = (unsigned long)t->tv_sec * SECOND + t->tv_nsec;
    return 0;
}
static int park(volatile int *word, int expected, unsigned long deadline)
{
    for (;;) {
        unsigned long until = deadline;
#ifdef AETHER_LONG_WAITS
        long start = observe();
        if (start < 0)
            return -start;
        if ((unsigned long)start >= deadline)
            return ETIMEDOUT;
        if (deadline - (unsigned long)start > SECOND)
            until = (unsigned long)start + SECOND;
#endif
        // RDX completion elapsed is deliberately not a libc result or clock
        // read.
        long result = memtrap(0x28010, getauxval(0xa001), (uintptr_t)word,
                              (unsigned)expected, until);
        if (result == -ETIMEDOUT) {
            long now = observe();
            if (now < 0)
                return -now;
            if ((unsigned long)now < until)
                return EIO;
#ifdef AETHER_LONG_WAITS
            if ((unsigned long)now < deadline)
                continue;
#endif
        }
        return result < 0 ? -result : result == 0 ? 0 : EIO;
    }
}
int aether_monotonic_wait(volatile int *word, int expected, clockid_t clock,
                          const struct timespec *at, int private)
{
    if (!private || clock != CLOCK_MONOTONIC)
        return ENOTSUP;
    if (at->tv_nsec < 0 || at->tv_nsec >= (long)SECOND)
        return EINVAL;
    // A negative absolute time is in the past, not an arithmetic overflow.
    if (at->tv_sec < 0)
        return ETIMEDOUT;
    unsigned long deadline;
    int error = nanoseconds(at, &deadline);
    if (error)
        return error;
    long now = observe();
    if (now < 0)
        return -now;
    if (deadline <= (unsigned long)now)
        return ETIMEDOUT;
#ifndef AETHER_LONG_WAITS
    if (deadline - (unsigned long)now > SECOND)
        return EINVAL;
#endif
    error = park(word, expected, deadline);
    // A compare mismatch is a spurious wake; the musl caller retains at.
    return error == EAGAIN ? 0 : error;
}
static int sleep_until(clockid_t clock, int flags, const struct timespec *req)
{
    if (flags != 0 && flags != TIMER_ABSTIME)
        return EINVAL;
    if (clock != CLOCK_MONOTONIC && !(clock == CLOCK_REALTIME && !flags))
        return ENOTSUP;
    unsigned long deadline;
    int error = nanoseconds(req, &deadline);
    if (error)
        return error;
    long now = observe();
    if (now < 0)
        return -now;
    if (!flags) {
#ifndef AETHER_LONG_WAITS
        if (deadline > SECOND)
            return EINVAL;
#endif
        if (deadline > LONG_MAX - (unsigned long)now)
            return EOVERFLOW;
        deadline += now;
    }
    if (deadline <= (unsigned long)now)
        return 0;
#ifndef AETHER_LONG_WAITS
    if (deadline - (unsigned long)now > SECOND)
        return EINVAL;
#endif
    // This stack word is private to the invocation. Spurious wakes cannot
    // restart the duration; retries retain the original operation deadline.
    volatile int word = 0;
    for (;;) {
        error = park(&word, 0, deadline);
        if (error == ETIMEDOUT)
            return 0;
        if (error && error != EAGAIN)
            return error;
        now = observe();
        if (now < 0)
            return -now;
        if ((unsigned long)now >= deadline)
            return 0;
    }
}
long aether_sleep_syscall(long n, long a, long b, long c, long d)
{
    // No signal delivery/cancellation is supported in this private profile;
    // rem is left untouched, including on successful or failed sleep.
    if (n == SYS_nanosleep)
        return -sleep_until(CLOCK_REALTIME, 0, (const void *)a);
    if (n == SYS_clock_nanosleep) {
        if (a != CLOCK_MONOTONIC && a != CLOCK_REALTIME)
            return -ENOTSUP;
        if (b != 0 && b != TIMER_ABSTIME)
            return -EINVAL;
        return -sleep_until(a, b, (const void *)c);
    }
    (void)d;
    return -ENOSYS;
}

#define CHECK(x, n)                                                            \
    do {                                                                       \
        if (!(x))                                                              \
            return n;                                                          \
    } while (0)
int aether_sleep_probe(void)
{
    struct timespec req = {0, 200000000}, rem = {77, 88}, invalid = {0, -1};
    long start = observe();
    errno = 71;
    CHECK(start >= 0, 330);
    CHECK(nanosleep(&req, &rem) == 0 && errno == 71 && rem.tv_sec == 77 &&
              rem.tv_nsec == 88,
          331);
    CHECK(observe() >= start + 200000000, 332);
    long until = observe() + 200000000;
    req = (struct timespec){until / SECOND, until % SECOND};
    CHECK(clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &req, &rem) == 0 &&
              observe() >= until && errno == 71,
          333);
    req = (struct timespec){0, 0};
    CHECK(clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &req, &rem) == 0 &&
              nanosleep(&req, &rem) == 0,
          334);
    CHECK(nanosleep(&invalid, &rem) == -1 && errno == EINVAL &&
              clock_nanosleep(CLOCK_MONOTONIC, 2, &req, &rem) == EINVAL,
          335);
    req = (struct timespec){2, 0};
#ifdef AETHER_LONG_WAITS
    start = observe();
    CHECK(start >= 0 && start <= LONG_MAX - 2000000000L &&
              clock_nanosleep(CLOCK_MONOTONIC, 0, &req, &rem) == 0 &&
              observe() >= start + 2000000000L,
          336);
    start = observe();
    CHECK(start >= 0 && start <= LONG_MAX - 2000000000L, 339);
    until = start + 2000000000L;
    req = (struct timespec){until / SECOND, until % SECOND};
    CHECK(clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &req, &rem) == 0 &&
              observe() >= until,
          339);
#else
    CHECK(clock_nanosleep(CLOCK_MONOTONIC, 0, &req, &rem) == EINVAL, 336);
#endif
    req = (struct timespec){LONG_MAX, 0};
    CHECK(clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &req, &rem) ==
              EOVERFLOW,
          337);
    CHECK(clock_nanosleep(CLOCK_REALTIME, TIMER_ABSTIME, &req, &rem) ==
                  ENOTSUP &&
              rem.tv_sec == 77 && rem.tv_nsec == 88,
          338);
    return 0;
}
