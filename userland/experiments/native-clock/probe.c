/* SPDX-License-Identifier: BSD-2-Clause */
#include "clock.h"
#include <errno.h>
#include <limits.h>
#include <sys/auxv.h>

#define CHECK(x, n)                                                            \
    do {                                                                       \
        if (!(x))                                                              \
            return (n);                                                        \
    } while (0)

int diagnostic_probe(void)
{
    unsigned long grant = getauxval(0xa001);
    volatile uint32_t word = 0;
    errno = EDOM;
    CHECK(grant != 0, 400);
#ifdef DISABLED
    CHECK(aether_clock_observe(grant) == -ENOSYS, 401);
    CHECK(aether_clock_park(grant, &word, 0, 0) == -ENOSYS, 401);
    CHECK(aether_clock_sleep_until(grant, 0) == -ENOSYS, 401);
#else
    CHECK(aether_clock_observe(0) == -EACCES &&
              aether_clock_observe(grant ^ 3) == -EACCES,
          402);
    CHECK(aether_clock_park(grant ^ 3, &word, 0, 0) == -EACCES, 402);
    CHECK(aether_clock_sleep_until(grant ^ 3, 0) == -EACCES, 402);
    long now = aether_clock_observe(grant);
    CHECK(now >= 0 && aether_clock_observe(grant) >= now, 403);
    CHECK(aether_clock_park(grant, &word, 1, now + 100000000) == -EAGAIN, 404);
    CHECK(aether_clock_park(grant, &word, 0, 0) == -ETIMEDOUT, 405);
    CHECK(aether_clock_sleep_until(grant, 0) == 0, 405);
    CHECK(aether_clock_park(grant, &word, ULONG_MAX, 0) == -EINVAL &&
              aether_clock_sleep_until(grant, ULONG_MAX) == -EINVAL,
          406);
    CHECK(aether_clock_sleep_until(grant, (unsigned long)now + 2000000000) ==
              -EINVAL,
          406);
    CHECK(aether_clock_park(grant, (void *)1, 0, 0) == -EINVAL, 407);
    CHECK(aether_clock_park(grant, (void *)0x80000000, 0, 0) == -EFAULT, 407);
    for (unsigned long i = 1; i <= 2; i++) {
        now = aether_clock_observe(grant);
        CHECK(now >= 0 && (unsigned long)now <= LONG_MAX - i * 200000000, 408);
        unsigned long deadline = (unsigned long)now + i * 200000000;
#ifdef EARLY
        CHECK(aether_clock_sleep_until(grant, deadline) == -EIO, 409);
        CHECK(aether_clock_observe(grant) < (long)deadline, 409);
#else
        CHECK(aether_clock_sleep_until(grant, deadline) == 0, 410);
        CHECK(aether_clock_observe(grant) >= (long)deadline, 411);
#endif
    }
#endif
    CHECK(errno == EDOM, 412);
    return 0;
}
