/* SPDX-License-Identifier: BSD-2-Clause */
/* Original TXG wait body with real host mutex/condition waiting and synthetic
 * progress/signal/suspension. No original TXG workers or native pool run. */
#include "pool-sync-witness.h"
#include <errno.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
typedef unsigned txg_wait_flag_t;
typedef unsigned long long u_longlong_t;
enum {
    TXG_WAIT_NONE = 0,
    TXG_WAIT_SIGNAL = 1,
    TXG_WAIT_SUSPEND = 2,
    TXG_DEFER_SIZE = 2
};
typedef struct {
    pthread_mutex_t tx_sync_lock;
    pthread_cond_t tx_sync_more_cv, tx_sync_done_cv;
    uint64_t tx_open_txg, tx_sync_txg_waiting, tx_quiesce_txg_waiting,
        tx_synced_txg;
    unsigned tx_threads;
} tx_state_t;
typedef struct {
    tx_state_t dp_tx;
    void *dp_spa;
} dsl_pool_t;
static int mode, locked, stop;
static dsl_pool_t *running;
static unsigned wait_calls, broadcasts;
static struct {
    const void *dp;
    uint64_t target, synced;
    int error, under_lock;
    unsigned calls;
} observed;
static void mutex_enter(pthread_mutex_t *lock)
{
    if (pthread_mutex_lock(lock))
        abort();
    locked = 1;
}
static void mutex_exit(pthread_mutex_t *lock)
{
    locked = 0;
    if (pthread_mutex_unlock(lock))
        abort();
}
static int dsl_pool_config_held(dsl_pool_t *dp)
{
    (void)dp;
    return 0;
}
static int spa_suspended(void *spa)
{
    (void)spa;
    return mode == 2;
}
static void cv_broadcast(pthread_cond_t *cv)
{
    ++broadcasts;
    if (pthread_cond_broadcast(cv))
        abort();
}
static void cv_wait_io(pthread_cond_t *cv, pthread_mutex_t *lock)
{
    ++wait_calls;
    locked = 0;
    if (pthread_cond_wait(cv, lock))
        abort();
    locked = 1;
}
static int cv_wait_io_sig(pthread_cond_t *cv, pthread_mutex_t *lock)
{
    (void)cv;
    (void)lock;
    ++wait_calls;
    if (mode == 3)
        running->dp_tx.tx_synced_txg = 7;
    return 0;
}
#define ASSERT(x)                                                              \
    do {                                                                       \
        if (!(x))                                                              \
            abort();                                                           \
    } while (0)
#define ASSERT0(x) ASSERT(!(x))
#define ASSERT3U(a, op, b) ASSERT((a)op(b))
#define dprintf(...) ((void)0)
#define SET_ERROR(error) (error)
void aether_pool_txg_observe(const void *dp, uint64_t target, uint64_t synced,
                             int error)
{
    observed.dp = dp;
    observed.target = target;
    observed.synced = synced;
    observed.error = error;
    observed.under_lock = locked;
    ++observed.calls;
}
/* Generated pinned original body and CDDL notices, with one observer call. */
#include "pool-txg-body.inc"
static void *sync_worker(void *argument)
{
    dsl_pool_t *dp = argument;
    pthread_mutex_lock(&dp->dp_tx.tx_sync_lock);
    while (!stop && dp->dp_tx.tx_sync_txg_waiting == 0)
        pthread_cond_wait(&dp->dp_tx.tx_sync_more_cv, &dp->dp_tx.tx_sync_lock);
    if (!stop) {
        dp->dp_tx.tx_synced_txg = dp->dp_tx.tx_sync_txg_waiting;
        pthread_cond_broadcast(&dp->dp_tx.tx_sync_done_cv);
    }
    pthread_mutex_unlock(&dp->dp_tx.tx_sync_lock);
    return NULL;
}
#define REQUIRE(x)                                                             \
    do {                                                                       \
        if (!(x)) {                                                            \
            fprintf(stderr, "TXG observation rejection: %s\n", #x);            \
            return 1;                                                          \
        }                                                                      \
    } while (0)
int main(int argc, char **argv)
{
    REQUIRE(argc == 2);
    mode = atoi(argv[1]);
    REQUIRE(mode >= 0 && mode <= 5);
    dsl_pool_t dp = {0};
    running = &dp;
    REQUIRE(pthread_mutex_init(&dp.dp_tx.tx_sync_lock, NULL) == 0);
    REQUIRE(pthread_cond_init(&dp.dp_tx.tx_sync_more_cv, NULL) == 0);
    REQUIRE(pthread_cond_init(&dp.dp_tx.tx_sync_done_cv, NULL) == 0);
    dp.dp_tx.tx_threads = 2;
    dp.dp_tx.tx_open_txg = 7;
    dp.dp_tx.tx_synced_txg = mode == 4 ? 7 : 6;
    uint64_t requested = mode == 5 ? 0 : 7;
    txg_wait_flag_t flags = mode == 1 || mode == 3 ? TXG_WAIT_SIGNAL
                            : mode == 2            ? TXG_WAIT_SUSPEND
                                                   : TXG_WAIT_NONE;
    pthread_t worker;
    int threaded = mode == 0 || mode == 5;
    if (threaded)
        REQUIRE(pthread_create(&worker, NULL, sync_worker, &dp) == 0);
    /* Model signal arrival after progress: still preserve EINTR, not success.
     */
    if (mode == 3) {
        /* The loop begins below target; the signal wait publishes progress. */
        dp.dp_tx.tx_synced_txg = 6;
    }
    int result = txg_wait_synced_flags(&dp, requested, flags);
    if (threaded)
        REQUIRE(pthread_join(worker, NULL) == 0);
    int expected = mode == 1 || mode == 3 ? EINTR : mode == 2 ? ESHUTDOWN : 0;
    REQUIRE(result == expected && observed.calls == 1 && observed.under_lock);
    REQUIRE(observed.dp == &dp && observed.target == (mode == 5 ? 9 : 7));
    REQUIRE(observed.error == result &&
            observed.synced == dp.dp_tx.tx_synced_txg);
    REQUIRE(dp.dp_tx.tx_sync_txg_waiting == (mode == 5 ? 9 : 7));
    if (threaded)
        REQUIRE(wait_calls >= 1 && broadcasts >= 1 &&
                observed.synced >= observed.target);
    if (mode == 4)
        REQUIRE(wait_calls == 0 && broadcasts == 0);
    if (mode == 1 || mode == 2)
        REQUIRE(observed.synced < observed.target);
    if (mode == 3)
        REQUIRE(observed.synced == observed.target && observed.error == EINTR);
    REQUIRE(pthread_cond_destroy(&dp.dp_tx.tx_sync_more_cv) == 0);
    REQUIRE(pthread_cond_destroy(&dp.dp_tx.tx_sync_done_cv) == 0);
    REQUIRE(pthread_mutex_destroy(&dp.dp_tx.tx_sync_lock) == 0);
    return 0;
}
