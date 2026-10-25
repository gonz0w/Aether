/* SPDX-License-Identifier: BSD-2-Clause */
/* Actual checked engine wall-time bodies over the independently sealed UTC
 * provider. Helper borrows live through real taskq drain/destruction. */
#include <sys/spa_impl.h>
#include <sys/zfs_context.h>
#include <sys/time.h>
#include "utc.h"
#include "runtime.h"
#define REQUIRE(ok)                                                            \
    do {                                                                       \
        if (!(ok))                                                             \
            return 854;                                                        \
    } while (0)
extern void aether_engine_utc_phase(unsigned char);
static int unavailable(int error)
{
    struct timespec ts = {17, 29};
    struct timeval tv = {17, 29};
    time_t seconds = 17;
    return clock_gettime(CLOCK_REALTIME, &ts) == -1 && errno == error &&
           ts.tv_sec == 17 && ts.tv_nsec == 29 && time(&seconds) == -1 &&
           errno == error && seconds == 17 && gettimeofday(&tv, NULL) == -1 &&
           errno == error && tv.tv_sec == 17 && tv.tv_usec == 29;
}
int aether_engine_utc_start(int policy, int disabled)
{
    REQUIRE(unavailable(ENODATA));
    int result = EAGAIN;
    for (unsigned attempt = 0; attempt < 16 && result == EAGAIN; ++attempt) {
        result = aether_utc_establish(policy);
        if (result == EAGAIN) {
            struct timespec pause = {0, 1000000};
            REQUIRE(!nanosleep(&pause, NULL));
        }
    }
    if (!policy) {
        REQUIRE(result == ENOTSUP && unavailable(ENODATA));
        return 855;
    }
    if (disabled) {
        REQUIRE(result == ENOSYS && unavailable(ENODATA));
        return 856;
    }
    REQUIRE(!result && aether_utc_establish(policy) == EALREADY);
    return 0;
}
static int stamps(int64_t base)
{
    struct timespec before, calendar, after;
    REQUIRE(!clock_gettime(CLOCK_REALTIME, &before));
    gethrestime(&calendar); /* Actual selected guarded inline body. */
    uint64_t seconds = gethrestime_sec();
    hrtime_t ns = getlrtime();
    REQUIRE(!clock_gettime(CLOCK_REALTIME, &after));
    REQUIRE(
        before.tv_sec >= base && after.tv_sec <= base + 30 &&
        calendar.tv_sec >= before.tv_sec && calendar.tv_sec <= after.tv_sec &&
        calendar.tv_nsec >= 0 && calendar.tv_nsec < 1000000000 &&
        !(calendar.tv_nsec % 1000) && seconds >= (uint64_t)before.tv_sec &&
        seconds <= (uint64_t)after.tv_sec && ns >= 0 &&
        ns / 1000000000 >= before.tv_sec && ns / 1000000000 <= after.tv_sec);
    struct timeval tv;
    time_t out;
    REQUIRE(time(&out) >= before.tv_sec && out <= base + 30 &&
            !gettimeofday(&tv, NULL) && tv.tv_sec >= before.tv_sec &&
            tv.tv_sec <= base + 30 && tv.tv_usec >= 0 && tv.tv_usec < 1000000);
    return 0;
}
struct request {
    taskq_t *queue;
    pthread_t primary;
    int64_t base;
    int result;
};
static void callback(void *argument)
{
    struct request *r = argument;
    r->result = pthread_equal(pthread_self(), r->primary) ||
                        taskq_of_curthread() != r->queue
                    ? 854
                    : stamps(r->base);
}
int aether_engine_utc_probe(int64_t base)
{
    REQUIRE(!stamps(base));
    aether_engine_utc_phase('U');
    spa_namespace_enter(FTAG);
    spa_t *spa = spa_add("aether_shared_utc", NULL, NULL);
    REQUIRE(spa && spa->spa_state == POOL_STATE_UNINITIALIZED &&
            !spa->spa_dsl_pool && !spa->spa_sync_on);
    spa_remove(spa);
    REQUIRE(!spa_lookup("aether_shared_utc"));
    spa_namespace_exit(FTAG);
    aether_engine_utc_phase('V');
    taskq_t *queue =
        taskq_create("utc_probe", 1, minclsyspri, 1, 1, TASKQ_PREPOPULATE);
    REQUIRE(queue);
    struct request r = {
        .queue = queue, .primary = pthread_self(), .base = base, .result = 854};
    REQUIRE(taskq_dispatch(queue, callback, &r, TQ_NOSLEEP) != TASKQID_INVALID);
    taskq_wait(queue);
    REQUIRE(!r.result);
    taskq_destroy(queue);
    aether_engine_utc_phase('W');
    return 0;
}
int aether_engine_utc_finish(void)
{
    struct timespec deadline, now;
    REQUIRE(!clock_gettime(CLOCK_MONOTONIC, &deadline));
    deadline.tv_sec += 2;
    while (aether_runtime_live() != 1) {
        struct timespec pause = {0, 1000000};
        REQUIRE(!clock_gettime(CLOCK_MONOTONIC, &now) &&
                (now.tv_sec < deadline.tv_sec ||
                 (now.tv_sec == deadline.tv_sec &&
                  now.tv_nsec < deadline.tv_nsec)) &&
                !nanosleep(&pause, NULL));
    }
    REQUIRE(!aether_utc_close() && aether_utc_close() == ENODATA &&
            unavailable(ENODATA));
    return 0;
}
