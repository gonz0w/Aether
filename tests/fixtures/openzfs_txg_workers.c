/* SPDX-License-Identifier: BSD-2-Clause */
/* Execute original worker bodies with explicit lock/handoff doubles. */
#include <setjmp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#define CHECK(v)                                                               \
    do {                                                                       \
        if (!(v)) {                                                            \
            fprintf(stderr, "TXG WORKER oracle99 line%d\n", __LINE__);         \
            exit(99);                                                          \
        }                                                                      \
    } while (0)
#define ASSERT CHECK
#define dprintf(...) ((void)0)
#define DTRACE_PROBE2(...) ((void)0)
typedef int callb_cpr_t;
typedef int txg_stat_t;
typedef struct {
    int unused;
} spa_t;
typedef struct {
    int tx_sync_lock, tx_sync_more_cv, tx_quiesce_more_cv, tx_quiesce_done_cv,
        tx_sync_done_cv;
    int tx_exiting;
    void *tx_sync_thread, *tx_quiesce_thread;
    uint64_t tx_synced_txg, tx_sync_txg_waiting, tx_open_txg, tx_quiesced_txg,
        tx_syncing_txg, tx_quiescing_txg, tx_quiesce_txg_waiting;
} tx_state_t;
typedef struct {
    spa_t *dp_spa;
    void *dp_scan;
    tx_state_t dp_tx;
} dsl_pool_t;
static spa_t spa;
static dsl_pool_t pool;
static jmp_buf finished;
static int locked, quiesced, synced, history, broadcasts;
static unsigned count;
static char events[4];
static int zfs_txg_timeout = 1, hz = 100;
static void mutex_enter(int *m)
{
    CHECK(m == &pool.dp_tx.tx_sync_lock && !locked);
    locked = 1;
}
static void mutex_exit(int *m)
{
    CHECK(m == &pool.dp_tx.tx_sync_lock && locked);
    locked = 0;
}
static int spl_fstrans_mark(void) { return 0; }
static int dsl_scan_active(void *p)
{
    CHECK(p == &pool);
    return 1;
}
static int spa_suspended(spa_t *p)
{
    CHECK(p == &spa);
    return 0;
}
static clock_t ddi_get_lbolt(void) { return 10; }
static int txg_has_quiesced_to_sync(dsl_pool_t *p)
{
    return !!p->dp_tx.tx_quiesced_txg;
}
static int txg_is_quiescing(dsl_pool_t *p)
{
    return !!p->dp_tx.tx_quiescing_txg;
}
static void txg_thread_enter(tx_state_t *tx, callb_cpr_t *c)
{
    CHECK(tx == &pool.dp_tx && c && !locked);
    locked = 1;
}
static __attribute__((noreturn)) void
txg_thread_exit(tx_state_t *tx, callb_cpr_t *c, void *thread)
{
    (void)tx;
    (void)c;
    (void)thread;
    CHECK(0);
    abort();
}
static void txg_thread_wait(tx_state_t *tx, callb_cpr_t *c, int *cv,
                            clock_t timer)
{
    CHECK(tx == &pool.dp_tx && c && locked && !timer &&
          cv == &tx->tx_quiesce_more_cv);
    CHECK(quiesced && tx->tx_quiesced_txg == 7 && broadcasts == 2);
    longjmp(finished, 1);
}
static void cv_broadcast(int *cv)
{
    CHECK(locked && cv);
    ++broadcasts;
}
static void txg_quiesce(dsl_pool_t *dp, uint64_t txg)
{
    CHECK(dp == &pool && txg == 7 && !locked && !quiesced && !count);
    quiesced = 1;
}
static txg_stat_t *spa_txg_history_init_io(spa_t *p, uint64_t txg,
                                           dsl_pool_t *dp)
{
    CHECK(p == &spa && dp == &pool && txg == 7 && !locked && count == 2);
    history = 1;
    return &history;
}
static void spa_sync(spa_t *p, uint64_t txg)
{
    CHECK(p == &spa && txg == 7 && !locked && history && !synced &&
          pool.dp_tx.tx_syncing_txg == 7);
    synced = 1;
}
static void spa_txg_history_fini_io(spa_t *p, txg_stat_t *ts)
{
    CHECK(p == &spa && ts == &history && !locked && synced && count == 3);
}
static void txg_dispatch_callbacks(dsl_pool_t *dp, uint64_t txg)
{
    CHECK(dp == &pool && txg == 7 && locked && dp->dp_tx.tx_synced_txg == 7 &&
          !dp->dp_tx.tx_syncing_txg && broadcasts == 4);
    longjmp(finished, 2);
}
void aether_pool_worker_progress(const void *dp, uint64_t txg,
                                 unsigned char event)
{
    CHECK(dp == &pool && txg == 7 && !locked && count < 3);
    if (event == 'q')
        CHECK(quiesced && !pool.dp_tx.tx_quiesced_txg && !count);
    else if (event == 's')
        CHECK(count == 1 && !synced && !pool.dp_tx.tx_quiesced_txg &&
              pool.dp_tx.tx_syncing_txg == 7);
    else if (event == 'd')
        CHECK(count == 2 && synced && pool.dp_tx.tx_synced_txg == 6);
    else
        CHECK(0);
    events[count++] = (char)event;
}
/* The original bodies refer to these thread members only on exit. */
#include "worker-bodies.inc"
int main(void)
{
    pool.dp_spa = &spa;
    pool.dp_scan = &pool;
    pool.dp_tx.tx_open_txg = 7;
    pool.dp_tx.tx_quiesce_txg_waiting = 8;
    pool.dp_tx.tx_synced_txg = 6;
    int result = setjmp(finished);
    if (!result)
        txg_quiesce_thread(&pool);
    CHECK(result == 1 && count == 1 && events[0] == 'q');
    locked = 0;
    result = setjmp(finished);
    if (!result)
        txg_sync_thread(&pool);
    CHECK(result == 2 && count == 3 && !memcmp(events, "qsd", 3));
    return 0;
}
