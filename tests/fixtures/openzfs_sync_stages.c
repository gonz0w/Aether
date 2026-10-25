/* SPDX-License-Identifier: BSD-2-Clause */
/* Execute exact pinned early sync prefixes with explicit lock/I/O doubles.
 * Later sync work and cleanup are outside this host fixture, not simulated
 * proof.
 */
#include <setjmp.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(v)                                                               \
    do {                                                                       \
        if (!(v)) {                                                            \
            fprintf(stderr, "SYNC STAGE oracle94 line%d\n", __LINE__);         \
            exit(94);                                                          \
        }                                                                      \
    } while (0)
#define VERIFY CHECK
#define ASSERT CHECK
#define VERIFY0(v) CHECK((v) == 0)
#define TXG_MASK 3
#define B_FALSE 0
#define SCL_CONFIG 1
#define SCL_STATE 2
#define FTAG NULL
#define RW_READER 1
#define RW_WRITER 2
#define TQ_SLEEP 0
#define SPA_VERSION_RAIDZ_DEFLATE 20
#define SPA_MINBLOCKSIZE 512
#define DMU_POOL_DIRECTORY_OBJECT 1
#define DMU_POOL_DEFLATE "deflate"
#define NSEC_TO_TICK(v) (v)
typedef int zio_t;
typedef int objset_t;
typedef struct {
    int value;
} list_t;
typedef struct {
    int unused;
} dsl_dir_t;
typedef struct {
    int ds_synced_link;
} dsl_dataset_t;
typedef struct {
    int unused;
} dmu_tx_t;
typedef struct vdev {
    void *vdev_aux;
    int vdev_children;
    struct vdev **vdev_child;
    int vdev_deflate_ratio;
} vdev_t;
typedef struct spa spa_t;
typedef struct {
    spa_t *dp_spa;
    objset_t *dp_meta_objset;
    int dp_early_sync_tasks, dp_dirty_datasets;
} dsl_pool_t;
struct spa {
    zio_t *spa_txg_zio[4];
    dsl_pool_t *spa_dsl_pool;
    unsigned spa_sync_pass;
    uint64_t spa_syncing_txg, spa_sync_starttime, spa_deadman_tqid,
        spa_deadman_synctime;
    list_t spa_state_dirty_list;
    struct {
        int ub_version;
    } spa_ubsync, spa_uberblock;
    vdev_t *spa_root_vdev;
    int spa_deflate;
    objset_t *spa_meta_objset;
};
typedef struct {
    int unused;
} dsl_sync_task_t;
static spa_t spa;
static dsl_pool_t pool;
static dmu_tx_t transaction;
static zio_t initial_root, dataset_root;
static jmp_buf blocked;
static unsigned mode, initial_done, locks, data_waits, convergence_done,
    assigned, count;
static char events[16];
static int system_delay_taskq;
static void boundary(unsigned n)
{
    if (mode == n)
        longjmp(blocked, 1);
}
static int spa_writeable(spa_t *s)
{
    CHECK(s == &spa);
    return 1;
}
static int zio_wait(zio_t *z)
{
    if (z == &initial_root) {
        CHECK(!initial_done && !locks);
        boundary(1);
        initial_done = 1;
    } else {
        CHECK(z == &dataset_root && locks == SCL_CONFIG && assigned);
        boundary(4);
        ++data_waits;
    }
    return 0;
}
static zio_t *zio_root(spa_t *s, void *a, void *b, int flags)
{
    CHECK(s == &spa && !a && !b && (flags == 1 || flags == 2));
    return &dataset_root;
}
#define ZIO_FLAG_CANFAIL 1
#define ZIO_FLAG_MUSTSUCCEED 2
static void brt_pending_apply(spa_t *s, uint64_t txg)
{
    CHECK(s == &spa && txg == 7 && initial_done);
}
static void spa_sync_time_logger(spa_t *s, uint64_t txg, int flag)
{
    CHECK(s == &spa && txg == 7 && !flag);
}
static void spa_config_enter(spa_t *s, int which, void *tag, int rw)
{
    CHECK(s == &spa && !tag && rw == RW_READER);
    if (which == SCL_CONFIG)
        boundary(2);
    CHECK(!(locks & which));
    locks |= which;
}
static void spa_config_exit(spa_t *s, int which, void *tag)
{
    CHECK(s == &spa && !tag && (locks & which) == (unsigned)which);
    locks &= ~which;
}
static void *list_head(list_t *l)
{
    CHECK(l == &spa.spa_state_dirty_list);
    return NULL;
}
static void vdev_state_clean(vdev_t *v)
{
    (void)v;
    CHECK(0);
}
static void vdev_config_dirty(vdev_t *v)
{
    (void)v;
    CHECK(0);
}
static dmu_tx_t *dmu_tx_create_assigned(dsl_pool_t *p, uint64_t txg)
{
    CHECK(p == &pool && txg == 7 && locks == SCL_CONFIG);
    if (spa.spa_sync_pass)
        boundary(3);
    ++assigned;
    return &transaction;
}
static uint64_t getlrtime(void) { return 10; }
static void taskq_cancel_id(int q, uint64_t id, int wait)
{
    (void)q;
    (void)id;
    CHECK(wait == 1);
}
static void spa_deadman(void *p) { (void)p; }
static uint64_t taskq_dispatch_delay(int q, void (*fn)(void *), spa_t *s,
                                     int flags, uint64_t when)
{
    (void)q;
    (void)when;
    CHECK(fn == spa_deadman && s == &spa && flags == TQ_SLEEP);
    return 2;
}
#define B_TRUE 1
#define TRUE 1
static uint64_t ddi_get_lbolt(void) { return 10; }
static int zap_add(objset_t *o, int dir, const char *name, size_t width, int n,
                   int *v, dmu_tx_t *tx)
{
    (void)o;
    (void)dir;
    (void)name;
    (void)width;
    (void)n;
    (void)v;
    (void)tx;
    CHECK(0);
    return 0;
}
static void spa_sync_adjust_vdev_max_queue_depth(spa_t *s) { CHECK(s == &spa); }
static void spa_sync_condense_indirect(spa_t *s, dmu_tx_t *tx)
{
    CHECK(s == &spa && tx == &transaction);
}
static void list_create(list_t *l, size_t size, size_t offset)
{
    (void)l;
    CHECK(size == sizeof(dsl_dataset_t) &&
          offset == offsetof(dsl_dataset_t, ds_synced_link));
}
static int txg_list_empty(int *l, uint64_t txg)
{
    CHECK(l == &pool.dp_early_sync_tasks && txg == 7);
    return 1;
}
static void *txg_list_remove(int *l, uint64_t txg)
{
    CHECK(txg == 7 &&
          (l == &pool.dp_early_sync_tasks || l == &pool.dp_dirty_datasets));
    return NULL;
}
static unsigned spa_sync_pass(spa_t *s)
{
    CHECK(s == &spa);
    return spa.spa_sync_pass;
}
#define ASSERT3U(a, op, b) CHECK((a)op(b))
static int dsl_early_sync_task_verify(dsl_pool_t *p, uint64_t txg)
{
    CHECK(p == &pool && txg == 7);
    return 1;
}
static void dsl_sync_task_sync(dsl_sync_task_t *t, dmu_tx_t *tx)
{
    (void)t;
    (void)tx;
    CHECK(0);
}
static int list_link_active(int *p)
{
    (void)p;
    CHECK(0);
    return 0;
}
static void list_insert_tail(list_t *l, dsl_dataset_t *ds)
{
    (void)l;
    (void)ds;
    CHECK(0);
}
static void dsl_dataset_sync(dsl_dataset_t *ds, zio_t *rio, dmu_tx_t *tx)
{
    (void)ds;
    (void)rio;
    (void)tx;
    CHECK(0);
}
static void dsl_pool_sync(dsl_pool_t *, uint64_t);
static void spa_sync_iterate_to_convergence(spa_t *s, dmu_tx_t *tx)
{
    CHECK(s == &spa && tx == &transaction);
    spa.spa_sync_pass = 1;
    dsl_pool_sync(&pool, 7);
    boundary(5);
    spa.spa_sync_pass = 2;
    dsl_pool_sync(&pool, 7);
    convergence_done = 1;
}
static void aether_pool_worker_progress(const void *p, uint64_t txg,
                                        unsigned char e)
{
    CHECK(p == &pool && txg == 7 && count < sizeof(events));
    switch (e) {
    case 'e':
        CHECK(!initial_done && !locks);
        break;
    case 'i':
        CHECK(initial_done && !locks);
        break;
    case 'c':
        CHECK(initial_done && locks == SCL_CONFIG && !assigned);
        break;
    case 'p':
        CHECK(spa.spa_sync_pass == 1 && assigned == 2 && !data_waits);
        break;
    case 'v':
        CHECK(spa.spa_sync_pass == 1 && assigned == 2 && data_waits == 1);
        break;
    case 'r':
        CHECK(convergence_done && data_waits == 2 && locks == SCL_CONFIG);
        break;
    default:
        CHECK(0);
    }
    events[count++] = e;
}
#include "sync-prefixes.inc"
int main(int argc, char **argv)
{
    CHECK(argc == 2);
    mode = (unsigned)atoi(argv[1]);
    CHECK(mode <= 5);
    spa.spa_dsl_pool = &pool;
    pool.dp_spa = &spa;
    spa.spa_txg_zio[7 & TXG_MASK] = &initial_root;
    spa.spa_ubsync.ub_version = spa.spa_uberblock.ub_version = 50;
    if (!setjmp(blocked))
        spa_sync(&spa, 7);
    const char *expected[] = {"eicpvr", "e", "ei", "eic", "eicp", "eicpv"};
    CHECK(count == strlen(expected[mode]) &&
          !memcmp(events, expected[mode], count));
    return 0;
}
