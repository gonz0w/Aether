/* SPDX-License-Identifier: BSD-2-Clause */
/* Actual owned provider and original instrumented file-vdev bodies. Transport,
 * ABDs, taskq and interrupt scaffolding are synthetic; no native/pool claim. */
#include "pool-witness.h"
#include "volume.h"
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <pthread.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#ifndef O_LARGEFILE
#define O_LARGEFILE 0100000
#endif
typedef int64_t loff_t;
typedef void cred_t;
typedef struct {
    int f_fd, f_dump_fd;
} zfs_file_t;
typedef struct {
    uint64_t zfa_size;
    mode_t zfa_mode;
} zfs_file_attr_t;
static _Atomic unsigned writes, flushes, reads, returned, interrupted;
static int mode;
static _Atomic unsigned checks, publication_waiters;
enum { SPA_MODE_READ = 1, SPA_MODE_WRITE = 2 };
typedef unsigned spa_mode_t;
typedef int boolean_t;
typedef struct dsl_pool dsl_pool_t;
typedef struct {
    spa_mode_t spa_mode;
    dsl_pool_t *spa_dsl_pool;
    int spa_trust_config;
} spa_t;
struct dsl_pool {
    spa_t *dp_spa;
};
typedef struct {
    dsl_pool_t *tx_pool;
    uint64_t tx_txg;
    int tx_anyobj;
} dmu_tx_t;
static int spa_mode(spa_t *spa) { return spa->spa_mode; }
int aether_volume_bind(uint64_t grant, struct aether_volume *out)
{
    *out = (struct aether_volume){1, 32, grant, 16, 7};
    return 0;
}
int aether_volume_check(const struct aether_volume *volume)
{
    if (mode == 16 && atomic_fetch_add(&checks, 1) >= 1)
        return EIO;
    return volume->grant == 17 ? 0 : EBADF;
}
int aether_volume_io(const struct aether_volume *volume, uint32_t write,
                     int64_t offset, void *buffer, size_t count, size_t *done)
{
    (void)offset;
    if (aether_volume_check(volume))
        return EBADF;
    if (write) {
        atomic_fetch_add(&writes, 1);
        const unsigned char *bytes = buffer;
        for (size_t i = 0; i < count; ++i)
            if (bytes[i] != 0x5b)
                abort();
    } else {
        atomic_fetch_add(&reads, 1);
        memset(buffer, 0x37, count);
    }
    *done = mode == 4 && write ? count / 2 : count;
    return mode == 5 && write ? EIO : 0;
}
int aether_volume_flush(const struct aether_volume *volume)
{
    int error = aether_volume_check(volume);
    if (error)
        return error;
    if (!(volume->rights & 4))
        return EACCES;
    atomic_fetch_add(&flushes, 1);
    return mode == 3 ? ENOTSUP : 0;
}
#include "file-functions.inc"

enum { ZIO_TYPE_READ = 1, ZIO_TYPE_WRITE, ZIO_TYPE_FLUSH, ZIO_TYPE_TRIM };
typedef struct {
    zfs_file_t *vf_file;
} vdev_file_t;
typedef struct vdev {
    vdev_file_t *vdev_tsd;
    spa_t *vdev_spa;
    const char *vdev_path;
    uint8_t vdev_ashift;
    int readable;
    int vdev_nonrot, vdev_has_trim, vdev_has_securetrim;
    int vdev_reopening, vdev_delayed_close;
#ifdef AETHER_POOL_FLOW_HOST
    uint64_t vdev_children, vdev_psize;
    struct vdev **vdev_child;
    int vdev_nowritecache;
#endif
    struct {
        int vs_aux;
    } vdev_stat;
} vdev_t;
#ifdef AETHER_POOL_FLOW_HOST
typedef struct {
    unsigned count;
    void *items[128];
} graph_list_t;
struct zio;
static void host_graph_done(struct zio *);
#endif
typedef struct zio {
    vdev_t *io_vd;
    spa_t *io_spa;
    void *io_abd;
    uint64_t io_txg, io_size, io_offset, io_target_timestamp;
    int io_type, io_error;
#ifdef AETHER_POOL_FLOW_HOST
    pthread_mutex_t io_lock;
    graph_list_t io_parent_list, io_child_list;
    int io_child_type, io_pipeline, io_state[2], io_alloc_list, io_cv;
    uint64_t io_children[1][2];
    int io_flags, io_priority, graph_auto;
    void (*io_done)(struct zio *);
    void *io_private;
    struct {
        int zp_checksum;
    } io_prop;
#endif
} zio_t;
static void *abd_borrow_buf(void *abd, size_t size)
{
    (void)size;
    return abd;
}
static void *abd_borrow_buf_copy(void *abd, size_t size)
{
    return abd_borrow_buf(abd, size);
}
static void abd_return_buf(void *abd, void *buf, size_t size)
{
    (void)size;
    if (abd != buf)
        abort();
    atomic_fetch_add(&returned, 1);
}
static void abd_return_buf_copy(void *abd, void *buf, size_t size)
{
    abd_return_buf(abd, buf, size);
}
static int vdev_readable(vdev_t *vd) { return vd->readable; }
static uint64_t zio_handle_io_delay(zio_t *zio)
{
    (void)zio;
    return 0;
}
static void zio_interrupt(zio_t *zio)
{
    atomic_fetch_add(&interrupted, 1);
#ifdef AETHER_POOL_FLOW_HOST
    host_graph_done(zio);
#else
    /* Model the original handoff releasing/reusing ZIO storage immediately.
     * Exact ledger bits also expose a misplaced hook reading poisoned fields.
     */
    memset(zio, 0xa5, sizeof(*zio));
#endif
}
static void zio_delay_interrupt(zio_t *zio) { zio_interrupt(zio); }
struct queued {
    void (*function)(void *);
    void *argument;
};
static struct queued queue[AETHER_POOL_WITNESS_SLOTS];
static unsigned queued;
static int vdev_file_taskq, zfs_nocacheflush;
static unsigned taskq_dispatch(int q, void (*function)(void *), void *arg,
                               int flags)
{
    (void)q;
    (void)flags;
    if (mode == 8 || mode == 12) {
        function(arg);
    } else {
        if (queued == AETHER_POOL_WITNESS_SLOTS)
            abort();
        queue[queued++] = (struct queued){function, arg};
    }
    return 1;
}
#define TQ_SLEEP 0
#define TASKQID_INVALID 0
enum { B_FALSE, B_TRUE, KM_SLEEP, VDEV_AUX_BAD_LABEL, VDEV_AUX_OPEN_FAILED };
static unsigned vdev_file_logical_ashift = 9, vdev_file_physical_ashift = 9;
static void *kmem_zalloc(size_t size, int flags)
{
    (void)flags;
    return calloc(1, size);
}
static void kmem_free(void *p, size_t size)
{
    (void)size;
    free(p);
}
#define ASSERT(x)                                                              \
    do {                                                                       \
        if (!(x))                                                              \
            abort();                                                           \
    } while (0)
#define ASSERT3U(a, op, b) ASSERT((a)op(b))
#define ASSERT3P(a, op, b) ASSERT((a)op(b))
#define ASSERT3S(a, op, b) ASSERT((a)op(b))
#define VERIFY3U(a, op, b) ASSERT3U(a, op, b)
#define SET_ERROR(error) (error)
static void vdev_file_io_deallocate(void *argument)
{
    (void)argument;
    abort();
}
/* Generated from pinned bodies with only audited observer additions. */
#include "pool-bodies.inc"

#define REQUIRE(x)                                                             \
    do {                                                                       \
        if (!(x)) {                                                            \
            fprintf(stderr, "pool hook rejection: %s\n", #x);                  \
            return 1;                                                          \
        }                                                                      \
    } while (0)
static struct aether_pool_witness witness;
static zfs_file_t *file;
static vdev_t leaf;
static spa_t spa = {.spa_mode = SPA_MODE_READ | SPA_MODE_WRITE,
                    .spa_trust_config = 1},
             foreign_spa = {.spa_mode = SPA_MODE_READ | SPA_MODE_WRITE,
                            .spa_trust_config = 1};
static dsl_pool_t dp = {&spa};
static dmu_tx_t selected_tx = {&dp, 7, 0};
static void setup_zio(zio_t *zio, int kind, void *buffer)
{
    *zio = (zio_t){.io_vd = &leaf,
                   .io_spa = &spa,
                   .io_abd = buffer,
                   .io_size = kind == ZIO_TYPE_FLUSH ? 0 : 512,
                   .io_txg = kind == ZIO_TYPE_WRITE ? 7 : 0,
                   .io_offset = 4096,
                   .io_type = kind};
}
static void run_queue_reverse(void)
{
    while (queued) {
        struct queued entry = queue[--queued];
        entry.function(entry.argument);
    }
}
static void *worker(void *argument)
{
    (void)argument;
    unsigned char data[512];
    memset(data, 0x5b, sizeof(data));
    zio_t write, flush;
    for (unsigned i = 0; i < 64; ++i) {
        setup_zio(&write, ZIO_TYPE_WRITE, data);
        setup_zio(&flush, ZIO_TYPE_FLUSH, NULL);
        vdev_file_io_start(&write);
        vdev_file_io_start(&flush);
    }
    return NULL;
}
static int open_leaf(vdev_t *vd)
{
    uint64_t size = 123, max_size = 123, logical = 123, physical = 123;
    int error = vdev_file_open(vd, &size, &max_size, &logical, &physical, NULL);
    if (!error &&
        (size != 8192 || max_size != size || logical != 9 || physical != 9))
        abort();
    if (error &&
        (size != 123 || max_size != 123 || logical != 123 || physical != 123))
        abort();
    return error;
}

static void *publication_worker(void *argument)
{
    (void)argument;
    atomic_fetch_add(&publication_waiters, 1);
    while (atomic_load_explicit(&pool_publication, memory_order_acquire) !=
           POOL_READY)
        sched_yield();
    if (pool_spa != &spa || witness.leaf != &leaf ||
        witness.file != leaf.vdev_tsd->vf_file)
        abort();
    return worker(NULL);
}

static _Atomic unsigned constructors_ready, constructors_go;
static void *constructor_worker(void *argument)
{
    atomic_fetch_add(&constructors_ready, 1);
    while (!atomic_load(&constructors_go))
        sched_yield();
    if (open_leaf(argument))
        abort();
    return NULL;
}

static _Atomic unsigned join_ready, join_go, join_winners, join_losers;
static void *join_worker(void *argument)
{
    dmu_tx_t tx = {&dp, (uintptr_t)argument + 11, 0};
    atomic_fetch_add(&join_ready, 1);
    while (!atomic_load(&join_go))
        sched_yield();
    int error = aether_pool_hooks_bind_transaction(&tx);
    if (!error)
        atomic_fetch_add(&join_winners, 1);
    else if (error == EALREADY)
        atomic_fetch_add(&join_losers, 1);
    else
        abort();
    return NULL;
}

static int transaction_cases(void)
{
    unsigned expected = 0;
    if (mode == 33) {
        vdev_file_close(&leaf);
        REQUIRE(aether_pool_hooks_bind_transaction(&selected_tx) == ENODEV);
        REQUIRE(aether_pool_hooks_check(UINT64_MAX) ==
                (AETHER_POOL_BAD_EVENT | AETHER_POOL_NO_WRITE |
                 AETHER_POOL_NO_FLUSH | AETHER_POOL_TXG_PENDING));
        return 0;
    }
    if (mode == 26) {
        REQUIRE(aether_pool_hooks_bind_transaction(NULL) == EINVAL);
        expected = AETHER_POOL_BAD_EVENT;
    } else if (mode == 27) {
        selected_tx.tx_txg = 0;
        REQUIRE(aether_pool_hooks_bind_transaction(&selected_tx) == EINVAL);
        selected_tx.tx_txg = 7;
        expected = AETHER_POOL_BAD_EVENT;
    } else if (mode == 28 || mode == 29) {
        dsl_pool_t foreign_dp = {mode == 28 ? &foreign_spa : &spa};
        if (mode == 28) {
            selected_tx.tx_pool = &foreign_dp;
            spa.spa_dsl_pool = &foreign_dp; /* Forward check independently. */
        } else {
            spa.spa_dsl_pool = &foreign_dp; /* Reverse check independently. */
        }
        REQUIRE(aether_pool_hooks_bind_transaction(&selected_tx) == EXDEV);
        selected_tx.tx_pool = &dp;
        spa.spa_dsl_pool = &dp;
        expected = AETHER_POOL_BAD_EVENT;
    } else if (mode == 30) {
        selected_tx.tx_pool = NULL;
        REQUIRE(aether_pool_hooks_bind_transaction(&selected_tx) == EINVAL);
        selected_tx.tx_pool = &dp;
        expected = AETHER_POOL_BAD_EVENT;
    } else if (mode == 31) {
        selected_tx.tx_anyobj = 1;
        REQUIRE(aether_pool_hooks_bind_transaction(&selected_tx) == EINVAL);
        selected_tx.tx_anyobj = 0;
        expected = AETHER_POOL_BAD_EVENT;
    } else if (mode == 32) {
        expected = AETHER_POOL_BAD_EVENT;
    }
    REQUIRE(atomic_load(&witness.target_txg) == 0);
    if (mode == 35) {
        pthread_t threads[16];
        for (uintptr_t i = 0; i < 16; ++i)
            REQUIRE(pthread_create(&threads[i], NULL, join_worker, (void *)i) ==
                    0);
        while (atomic_load(&join_ready) != 16)
            sched_yield();
        atomic_store(&join_go, 1);
        for (unsigned i = 0; i < 16; ++i)
            REQUIRE(pthread_join(threads[i], NULL) == 0);
        REQUIRE(atomic_load(&join_winners) == 1 &&
                atomic_load(&join_losers) == 15);
        REQUIRE(atomic_load(&witness.target_txg) >= 11 &&
                atomic_load(&witness.target_txg) <= 26);
        REQUIRE(pool_dp == &dp);
        expected = AETHER_POOL_BAD_EVENT;
    } else if (mode != 37) {
        if (mode == 25)
            selected_tx.tx_txg = 11;
        REQUIRE((mode == 36
                     ? aether_pool_witness_bind_txg(&witness, 7)
                     : aether_pool_hooks_bind_transaction(&selected_tx)) == 0);
        if (mode == 25) {
            REQUIRE(atomic_load(&witness.target_txg) == 11);
            memset(&selected_tx, 0xa5, sizeof(selected_tx));
            REQUIRE(pool_dp == &dp); /* No retained transaction borrow. */
        }
    }
    if (mode == 34) {
        REQUIRE(aether_pool_hooks_bind_transaction(&selected_tx) == EALREADY);
        selected_tx.tx_txg = 11;
        REQUIRE(aether_pool_hooks_bind_transaction(&selected_tx) == EALREADY);
        REQUIRE(atomic_load(&witness.target_txg) == 7 && pool_dp == &dp);
        expected = AETHER_POOL_BAD_EVENT;
    }
    unsigned char data[512];
    memset(data, 0x5b, sizeof(data));
    zio_t write, flush;
    setup_zio(&write, ZIO_TYPE_WRITE, data);
    setup_zio(&flush, ZIO_TYPE_FLUSH, NULL);
    if (mode == 37)
        mode = 5; /* Real provider EIO before binding, then healthy traffic. */
    vdev_file_io_start(&write);
    vdev_file_io_start(&flush);
    run_queue_reverse();
    if (mode == 5) {
        mode = 37;
        REQUIRE(aether_pool_hooks_bind_transaction(&selected_tx) == 0);
        setup_zio(&write, ZIO_TYPE_WRITE, data);
        setup_zio(&flush, ZIO_TYPE_FLUSH, NULL);
        vdev_file_io_start(&write);
        vdev_file_io_start(&flush);
        run_queue_reverse();
        REQUIRE(atomic_load(&witness.provider_error) == EIO &&
                atomic_load(&witness.leaf_error) == EIO);
        expected = AETHER_POOL_PROVIDER_ERROR | AETHER_POOL_LEAF_ERROR;
    }
    if (mode == 36) {
        REQUIRE(aether_pool_hooks_check(7) == AETHER_POOL_TXG_PENDING);
    } else {
        REQUIRE(atomic_load(&pool_transaction) == POOL_TX_BOUND);
        REQUIRE(aether_pool_hooks_check(UINT64_MAX) == expected);
        if (mode == 25)
            REQUIRE(aether_pool_hooks_check(10) == AETHER_POOL_TXG_PENDING);
    }
    vdev_file_close(&leaf);
    REQUIRE(aether_pool_hooks_check(UINT64_MAX) ==
            (mode == 36 ? AETHER_POOL_TXG_PENDING : expected));
    return 0;
}

int main(int argc, char **argv)
{
    REQUIRE(argc == 2);
    mode = atoi(argv[1]);
    REQUIRE(mode >= 0 && mode <= 40);
    spa.spa_dsl_pool = &dp;
    REQUIRE(aether_zfs_volume_bind(17) == 0);
    leaf = (vdev_t){.vdev_spa = &spa,
                    .vdev_path = AETHER_VOLUME_PATH,
                    .vdev_ashift = 9,
                    .readable = 1};
    REQUIRE(aether_pool_hooks_prepare(NULL) == EINVAL);
    if (mode != 22) {
        REQUIRE(aether_pool_hooks_prepare(&witness) == 0);
        REQUIRE(aether_pool_hooks_prepare(&witness) == EALREADY);
    }
    REQUIRE(aether_pool_hooks_check(0) == AETHER_POOL_INCOMPLETE);
    if (mode >= 38) {
        spa.spa_trust_config = mode == 40;
        if (mode == 40)
            spa.spa_mode = SPA_MODE_READ;
        REQUIRE(open_leaf(&leaf) == 0);
        REQUIRE(atomic_load(&pool_publication) ==
                (mode == 38 ? POOL_READY : POOL_UNBOUND));
        vdev_file_close(&leaf);
        REQUIRE(atomic_load(&pool_publication) ==
                (mode == 38 ? POOL_CLOSED : POOL_UNBOUND));
        spa.spa_trust_config = 1;
        spa.spa_mode = SPA_MODE_READ | SPA_MODE_WRITE;
        vdev_t trusted = leaf;
        REQUIRE(open_leaf(&trusted) == 0);
        REQUIRE(atomic_load(&pool_publication) ==
                (mode == 38 ? POOL_CLOSED : POOL_READY));
        REQUIRE(aether_pool_hooks_bind_transaction(&selected_tx) ==
                (mode == 38 ? ENODEV : 0));
        if (mode != 38)
            REQUIRE(witness.leaf == &trusted &&
                    witness.file == trusted.vdev_tsd->vf_file &&
                    atomic_load(&witness.target_txg) == selected_tx.tx_txg);
        vdev_file_close(&trusted);
        REQUIRE(atomic_load(&pool_publication) == POOL_CLOSED);
        REQUIRE(open_leaf(&trusted) == 0);
        REQUIRE(atomic_load(&pool_publication) == POOL_CLOSED);
        REQUIRE(aether_pool_hooks_bind_transaction(&selected_tx) == ENODEV);
        vdev_file_close(&trusted);
        return 0;
    }
    if (mode == 18) {
        pthread_t threads[16];
        vdev_t candidates[16];
        for (unsigned i = 0; i < 16; ++i) {
            candidates[i] = leaf;
            REQUIRE(pthread_create(&threads[i], NULL, constructor_worker,
                                   &candidates[i]) == 0);
        }
        while (atomic_load(&constructors_ready) != 16)
            sched_yield();
        atomic_store(&constructors_go, 1);
        for (unsigned i = 0; i < 16; ++i)
            REQUIRE(pthread_join(threads[i], NULL) == 0);
        REQUIRE(atomic_load(&pool_publication) == POOL_READY);
        REQUIRE(pool_spa == &spa && atomic_load(&witness.target_txg) == 0);
        unsigned winners = 0;
        for (unsigned i = 0; i < 16; ++i)
            winners += witness.leaf == &candidates[i];
        REQUIRE(winners == 1);
        REQUIRE(aether_pool_hooks_check(UINT64_MAX) ==
                (AETHER_POOL_BAD_EVENT | AETHER_POOL_NO_WRITE |
                 AETHER_POOL_NO_FLUSH | AETHER_POOL_TXG_PENDING));
        for (unsigned i = 0; i < 16; ++i)
            vdev_file_close(&candidates[i]);
        return 0;
    }
    if (mode == 11) {
        /* Valid provider borrows, but deliberately admit before original open
         * publication. The observer must retain this omission after it opens.
         */
        REQUIRE(zfs_file_open(AETHER_VOLUME_PATH, O_RDWR, 0, NULL, &file) == 0);
        leaf.vdev_tsd = calloc(1, sizeof(vdev_file_t));
        REQUIRE(leaf.vdev_tsd != NULL);
        leaf.vdev_tsd->vf_file = file;
        leaf.vdev_reopening = 1;
        unsigned char early[512];
        memset(early, 0x5b, sizeof(early));
        zio_t write, flush;
        setup_zio(&write, ZIO_TYPE_WRITE, early);
        setup_zio(&flush, ZIO_TYPE_FLUSH, NULL);
        vdev_file_io_start(&write);
        vdev_file_io_start(&flush);
        run_queue_reverse();
        REQUIRE(aether_pool_hooks_check(0) ==
                (AETHER_POOL_INCOMPLETE | AETHER_POOL_BAD_EVENT));
    }
    if (mode == 20)
        leaf.vdev_path = "relative";
    if (mode == 21)
        leaf.vdev_path = "/absent";
    pthread_t publication_threads[16];
    if (mode == 12) {
        for (unsigned i = 0; i < 16; ++i)
            REQUIRE(pthread_create(&publication_threads[i], NULL,
                                   publication_worker, NULL) == 0);
        while (atomic_load(&publication_waiters) != 16)
            sched_yield();
    }
    if (mode == 32) {
        REQUIRE(aether_pool_hooks_bind_transaction(&selected_tx) == ENODEV);
        REQUIRE(aether_pool_hooks_check(0) ==
                (AETHER_POOL_INCOMPLETE | AETHER_POOL_BAD_EVENT));
    }
    int error = open_leaf(&leaf);
    if (mode == 16 || mode == 20 || mode == 21) {
        REQUIRE(error == (mode == 16 ? EIO : mode == 20 ? EINVAL : ENOENT));
        REQUIRE(aether_pool_hooks_check(0) == AETHER_POOL_INCOMPLETE);
        REQUIRE(atomic_load(&writes) == 0 && atomic_load(&flushes) == 0);
        vdev_file_close(&leaf);
        return 0;
    }
    REQUIRE(error == 0);
    if (mode == 22) {
        REQUIRE(aether_pool_hooks_check(0) == AETHER_POOL_INCOMPLETE);
        vdev_file_close(&leaf);
        return 0;
    }
    if (mode >= 25)
        return transaction_cases();
    unsigned initial_bits =
        AETHER_POOL_NO_WRITE | AETHER_POOL_NO_FLUSH | AETHER_POOL_TXG_PENDING;
    if (mode == 11)
        initial_bits |= AETHER_POOL_BAD_EVENT;
    if (mode != 12)
        REQUIRE(aether_pool_hooks_check(0) == initial_bits);
    /* Original getters on a synthetic assigned host object, not native assign.
     */
    REQUIRE(aether_pool_hooks_bind_transaction(&selected_tx) == 0);
    file = leaf.vdev_tsd->vf_file;
    if (mode == 11)
        leaf.vdev_reopening = 0;
    if (mode == 8 || mode == 12) {
        pthread_t threads[16];
        if (mode == 8)
            for (unsigned i = 0; i < 16; ++i)
                REQUIRE(pthread_create(&threads[i], NULL, worker, NULL) == 0);
        for (unsigned i = 0; i < 16; ++i)
            REQUIRE(
                pthread_join(mode == 8 ? threads[i] : publication_threads[i],
                             NULL) == 0);
        REQUIRE(atomic_load(&witness.writes) == 1024);
        REQUIRE(atomic_load(&witness.flushes) == 1024);
        REQUIRE(atomic_load(&writes) == 1024 && atomic_load(&flushes) == 1024);
        REQUIRE(atomic_load(&returned) == 1024 &&
                atomic_load(&interrupted) == 2048);
        REQUIRE(aether_pool_hooks_check(7) == 0);
        vdev_file_close(&leaf);
        REQUIRE(aether_pool_hooks_check(7) == 0);
        return 0;
    }
    unsigned char data[512];
    memset(data, 0x5b, sizeof(data));
    zio_t write, flush, second, read;
    setup_zio(&write, ZIO_TYPE_WRITE, data);
    setup_zio(&flush, ZIO_TYPE_FLUSH, NULL);
    vdev_file_io_start(&write);
    vdev_file_io_start(&flush);
    if (mode == 23) {
        REQUIRE(queued == 2);
        vdev_file_close(&leaf);
        REQUIRE(aether_pool_hooks_check(7) ==
                (AETHER_POOL_INCOMPLETE | AETHER_POOL_NO_WRITE |
                 AETHER_POOL_NO_FLUSH));
        REQUIRE(atomic_load(&writes) == 0 && atomic_load(&flushes) == 0);
        return 0; /* Dropped callbacks never establish quiescence. */
    }
    if (mode == 24)
        aether_pool_hook_close(
            &leaf); /* Synthetic preemption before release. */
    run_queue_reverse();
    if (mode == 24) {
        REQUIRE(aether_pool_hooks_check(7) == 0);
        /* Model continuation of original close; do not notify retirement twice.
         */
        zfs_file_close(file);
        kmem_free(leaf.vdev_tsd, sizeof(vdev_file_t));
        leaf.vdev_tsd = NULL;
        return 0;
    }
    unsigned expected = 0;
    if (mode == 11) {
        expected = AETHER_POOL_BAD_EVENT;
    } else if (mode == 13) {
        aether_pool_hook_open(
            &leaf); /* Duplicate publication without reopening. */
        REQUIRE(atomic_load(&witness.target_txg) == 7);
        expected = AETHER_POOL_BAD_EVENT;
    } else if (mode == 14) {
        volume_file(file)->volume.rights = 3;
        setup_zio(&second, ZIO_TYPE_FLUSH, NULL);
        vdev_file_io_start(&second);
        run_queue_reverse();
        volume_file(file)->volume.rights = 7;
        uint64_t generation = atomic_load(&witness.operations[0].state);
        leaf.vdev_reopening = 1;
        vdev_file_close(&leaf); /* Original reopen close is an early no-op. */
        REQUIRE(atomic_load(&pool_publication) == POOL_READY);
        REQUIRE(open_leaf(&leaf) == 0);
        REQUIRE(atomic_load(&witness.operations[0].state) == generation);
        REQUIRE(atomic_load(&witness.target_txg) == 7);
        REQUIRE(atomic_load(&witness.provider_error) == EACCES);
        leaf.vdev_reopening = 0;
        expected = AETHER_POOL_PROVIDER_ERROR | AETHER_POOL_LEAF_ERROR;
    } else if (mode == 15 || mode == 19) {
        vdev_t foreign = leaf;
        setup_zio(&second, ZIO_TYPE_WRITE, data);
        if (mode == 15)
            second.io_spa = &foreign_spa;
        else
            second.io_vd = &foreign;
        vdev_file_io_start(&second);
        run_queue_reverse();
        expected = AETHER_POOL_BAD_EVENT;
    } else if (mode == 17) {
        vdev_file_close(&leaf);
        REQUIRE(atomic_load(&pool_publication) == POOL_CLOSED);
        REQUIRE(aether_pool_hooks_check(7) == 0);
        REQUIRE(open_leaf(&leaf) ==
                0); /* Upstream succeeds; observer rejects reuse. */
        REQUIRE(atomic_load(&pool_publication) == POOL_CLOSED);
        REQUIRE(aether_pool_hooks_check(7) == AETHER_POOL_BAD_EVENT);
        vdev_file_close(&leaf);
        return 0;
    } else if (mode == 1 || mode == 2) {
        /* A later bypass cannot disappear behind the earlier healthy flush. */
        setup_zio(&second, ZIO_TYPE_FLUSH, NULL);
        if (mode == 1)
            zfs_nocacheflush = 1;
        else
            leaf.readable = 0;
        vdev_file_io_start(&second);
        expected = AETHER_POOL_BAD_EVENT | AETHER_POOL_INCOMPLETE;
    } else if (mode == 3) {
        expected = AETHER_POOL_PROVIDER_ERROR | AETHER_POOL_LEAF_ERROR;
        REQUIRE(atomic_load(&witness.provider_error) == ENOTSUP);
        REQUIRE(atomic_load(&witness.leaf_error) == ENOTSUP);
    } else if (mode == 4) {
        expected = AETHER_POOL_PARTIAL_WRITE | AETHER_POOL_LEAF_ERROR;
        REQUIRE(atomic_load(&witness.leaf_error) == ENOSPC);
    } else if (mode == 5) {
        expected = AETHER_POOL_PROVIDER_ERROR | AETHER_POOL_LEAF_ERROR;
        REQUIRE(atomic_load(&witness.provider_error) == EIO);
    } else if (mode == 6) {
        setup_zio(&second, ZIO_TYPE_FLUSH, NULL);
        vdev_file_io_start(&second);
        REQUIRE(queued == 1);
        /* Drop a queued callback: observe incompleteness, never fake
         * completion. */
        expected = AETHER_POOL_INCOMPLETE;
    } else if (mode == 7) {
        setup_zio(&read, ZIO_TYPE_READ, data);
        vdev_file_io_start(&read);
        run_queue_reverse();
        for (unsigned i = 0; i < sizeof(data); ++i)
            REQUIRE(data[i] == 0x37);
        REQUIRE(atomic_load(&reads) == 1 && atomic_load(&returned) == 2);
        REQUIRE(atomic_load(&witness.writes) == 1 &&
                atomic_load(&witness.flushes) == 1);
    } else if (mode == 9 || mode == 10) {
        if (mode == 9)
            volume_file(file)->volume.rights = 3;
        else
            volume_file(file)->volume.grant = 18;
        setup_zio(&second, ZIO_TYPE_FLUSH, NULL);
        vdev_file_io_start(&second);
        run_queue_reverse();
        expected = AETHER_POOL_PROVIDER_ERROR | AETHER_POOL_LEAF_ERROR;
        REQUIRE(atomic_load(&witness.provider_error) ==
                (mode == 9 ? EACCES : EBADF));
    }
    REQUIRE(aether_pool_hooks_check(7) == expected);
    REQUIRE(atomic_load(&writes) ==
                (mode == 11 || mode == 15 || mode == 19 ? 2 : 1) &&
            atomic_load(&flushes) == (mode == 11 ? 2 : 1));
    /* Incomplete observer borrows remain until this disposable process ends;
     * this fixture cannot authorize native cleanup or replacement. */
    if (!(expected & AETHER_POOL_INCOMPLETE))
        vdev_file_close(&leaf);
    return 0;
}
