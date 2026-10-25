/* SPDX-License-Identifier: BSD-2-Clause */
/* Private extension to the pinned actual-pthread lifecycle witness. No SDK API.
 * All timespecs/words are owner-local borrows; atomics publish a live
 * diagnostic word only until its backend call returns. Native waiting must
 * precede a wake.
 */
#include "real_time.h"
static void yield_primary(void);
static long waiting(unsigned);
static pthread_mutex_t timed_mutex = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t timed_condition;
static struct timespec timed_deadline;
static _Atomic(volatile int *) timed_words[82];
static _Atomic unsigned timed_calls[82], timed_returned, timed_predicate;
static _Atomic unsigned timed_relocks;
#ifdef AETHER_LONG_WAITS
static _Atomic unsigned long timed_sleep_starts[82];
static _Atomic unsigned timed_slept;
#define SERVICE_SLEEP_NS 2000000000L
#else
#define SERVICE_SLEEP_NS 200000000L
#endif

static long timed_now(void) { return memtrap(0x2800f, thread_cap, 0, 0, 0); }
static struct timespec timed_at(unsigned long ns)
{
    return (struct timespec){ns / 1000000000UL, ns % 1000000000UL};
}
int aether_libc_timedwait(volatile int *word, int value, clockid_t clock,
                          const struct timespec *at, int private)
{
    unsigned i = limit;
    if (clock == CLOCK_MONOTONIC && at->tv_sec == timed_deadline.tv_sec &&
        at->tv_nsec == timed_deadline.tv_nsec) {
        unsigned id = __pthread_self()->tid;
        for (unsigned n = 0; n < limit; ++n)
            if (startups[n].id == id)
                i = n;
    }
    if (i < limit) {
        timed_words[i] = word;
        ++timed_calls[i];
    }
    int result = aether_monotonic_wait(word, value, clock, at, private);
    if (i < limit)
        timed_words[i] = 0;
    return result;
}
static unsigned service_time_initialize(void)
{
    CHECK(timed_now() >= 0, 380);
    pthread_condattr_t attr;
    CHECK(!pthread_condattr_init(&attr) &&
              !pthread_condattr_setclock(&attr, CLOCK_MONOTONIC) &&
              !pthread_cond_init(&timed_condition, &attr) &&
              !pthread_condattr_destroy(&attr),
          382);
    return 0;
}
static unsigned service_time_worker(unsigned i)
{
    int saved_errno = errno;
    CHECK(!pthread_mutex_lock(&timed_mutex), 382);
    int result =
        pthread_cond_timedwait(&timed_condition, &timed_mutex, &timed_deadline);
    CHECK(result != EIO, 381);
#if TIME_MODE == 2
    CHECK(!result && timed_predicate, 382);
#else
    CHECK(result == ETIMEDOUT && !timed_predicate, 382);
#endif
    /* A normal mutex is owned again; trylock must report busy. */
    CHECK(pthread_mutex_trylock(&timed_mutex) == EBUSY, 383);
    CHECK(!pthread_mutex_unlock(&timed_mutex), 383);
    ++timed_returned;
    long now = timed_now();
#if TIME_MODE != 2
    unsigned long deadline =
        (unsigned long)timed_deadline.tv_sec * 1000000000UL +
        timed_deadline.tv_nsec;
    CHECK(now >= 0 && (unsigned long)now >= deadline, 381);
#else
    CHECK(now >= 0, 380);
#endif
    struct timespec rem = {77, 88};
#ifdef AETHER_LONG_WAITS
    CHECK(now <= LONG_MAX - SERVICE_SLEEP_NS, 384);
    timed_sleep_starts[i] = (unsigned long)now;
#endif
    if (i % 2) {
        struct timespec duration = {SERVICE_SLEEP_NS / 1000000000L,
                                    SERVICE_SLEEP_NS % 1000000000L};
        CHECK(!nanosleep(&duration, &rem) &&
                  timed_now() >= now + SERVICE_SLEEP_NS,
              384);
    } else {
        /* Compute one absolute time; spurious completion never restarts it. */
        struct timespec at = timed_at((unsigned long)now + SERVICE_SLEEP_NS);
        CHECK(!clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &at, &rem) &&
                  timed_now() >= now + SERVICE_SLEEP_NS,
              384);
    }
    CHECK(errno == saved_errno && rem.tv_sec == 77 && rem.tv_nsec == 88, 384);
#ifdef AETHER_LONG_WAITS
    ++timed_slept;
#endif
    CHECK(!pthread_mutex_lock(&timed_mutex), 385);
    struct timespec bad = {0, -1}, overflow = {LONG_MAX, 0};
#ifdef AETHER_LONG_WAITS
    struct timespec far = {0, 0};
#else
    struct timespec far = timed_at((unsigned long)timed_now() + 2000000000UL);
#endif
    pthread_cond_t utc = PTHREAD_COND_INITIALIZER;
    CHECK(pthread_cond_timedwait(&timed_condition, &timed_mutex, &bad) ==
                  EINVAL &&
              pthread_cond_timedwait(&timed_condition, &timed_mutex,
                                     &overflow) == EOVERFLOW &&
              pthread_cond_timedwait(&timed_condition, &timed_mutex, &far) ==
#ifdef AETHER_LONG_WAITS
                  ETIMEDOUT &&
#else
                  EINVAL &&
#endif
              pthread_cond_timedwait(&utc, &timed_mutex, &far) == ENOTSUP &&
              pthread_mutex_trylock(&timed_mutex) == EBUSY && !utc._c_head &&
              !utc._c_tail && !utc._c_lock && !pthread_cond_destroy(&utc),
          385);
    CHECK(!pthread_mutex_unlock(&timed_mutex) && errno == saved_errno, 385);
    return 0;
}
static unsigned service_time_parked(unsigned calls)
{
    for (unsigned spin = 0; spin < 10000; ++spin) {
        unsigned count = 0;
        for (unsigned i = 0; i < limit; ++i) {
            CHECK(!startups[i].error, startups[i].error);
            if (timed_calls[i] >= calls && timed_words[i] &&
                waiting(startups[i].id) == 1)
                ++count;
        }
        if (count == limit)
            return 0;
        yield_primary();
    }
    return 386;
}
static unsigned service_time_parent(void)
{
    unsigned result = service_time_parked(1);
    CHECK(!result, result);
#ifdef STOP_LIVE
    if (limit == 82 && memtrap(0x20005, 0, 0, 0, 0) == 1) {
#ifdef AETHER_LONG_WAITS
        unsigned long condition_ns =
            (unsigned long)timed_deadline.tv_sec * 1000000000UL +
            timed_deadline.tv_nsec;
        CHECK(condition_ns <= LONG_MAX - 1000000UL, 387);
        struct timespec after_condition = timed_at(condition_ns + 1000000UL);
        CHECK(!clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &after_condition,
                               NULL),
              387);
        unsigned count = 0;
        unsigned long latest = 0;
        for (unsigned spin = 0; spin < 10000 && count != limit; ++spin) {
            count = 0;
            for (unsigned i = 0; i < limit; ++i) {
                unsigned long started = timed_sleep_starts[i];
                if (started) {
                    ++count;
                    if (started > latest)
                        latest = started;
                }
            }
            if (count != limit)
                yield_primary();
        }
        CHECK(count == limit && latest <= LONG_MAX - 1100000000UL, 387);
        struct timespec after_chunk = timed_at(latest + 1100000000UL);
        CHECK(!clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &after_chunk,
                               NULL) &&
                  timed_now() >= (long)(latest + 1100000000UL) &&
                  timed_returned == limit && !timed_slept,
              387);
        for (unsigned i = 0; i < limit; ++i)
            CHECK(waiting(startups[i].id) == 1, 387);
#endif
        CHECK(!memtrap(0x20004, 0, 0, 0, 0), 387);
        for (;;)
            yield_primary();
    }
#endif
#if TIME_MODE == 1
    for (unsigned i = 0; i < limit; ++i) {
        volatile int *word = timed_words[i];
        CHECK(word && waiting(startups[i].id) == 1 &&
                  memtrap(0x2800c, thread_cap, (unsigned long)word, 1, 0) == 1,
              388);
    }
    result = service_time_parked(2);
    CHECK(!result, result);
#elif TIME_MODE == 2
    CHECK(!pthread_mutex_lock(&timed_mutex) && !timed_returned, 389);
    timed_predicate = 1;
    CHECK(!pthread_cond_broadcast(&timed_condition), 389);
    /* First signaled worker blocks on the held mutex before requeue chains
     * hand ownership onwards. Observe the actual untimed lock wait. */
    for (unsigned spin = 0; spin < 10000 && !timed_relocks; ++spin)
        yield_primary();
    CHECK(timed_relocks && !timed_returned, 389);
    CHECK(!pthread_mutex_unlock(&timed_mutex), 389);
#endif
    return 0;
}
static unsigned service_time_cleanup(void)
{
#ifdef AETHER_LONG_WAITS
    CHECK(timed_slept == limit, 390);
#endif
    CHECK(timed_returned == limit && !timed_condition._c_head &&
              !timed_condition._c_tail && !timed_condition._c_lock,
          390);
    for (unsigned i = 0; i < limit; ++i)
        CHECK(!timed_words[i] && timed_calls[i] >= 1 + (TIME_MODE == 1), 390);
    CHECK(!pthread_cond_destroy(&timed_condition) &&
              !pthread_mutex_destroy(&timed_mutex),
          390);
    return 0;
}
