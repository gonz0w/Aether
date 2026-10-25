/* SPDX-License-Identifier: BSD-2-Clause */
/* Actual original graph/write/flush/file-vdev bodies and owned provider.
 * Allocation/list/pipeline/aggregation/assignment are host scaffolding, not
 * native ZIO completion, TXG construction, disk durability or resource fit. */
#define AETHER_POOL_FLOW_HOST 1
#define main lower_fixture_main
#include "openzfs_pool_hooks.c"
#undef main
#include "pool-flow-witness.h"
typedef int boolean_t;
typedef int zio_flag_t, zio_priority_t;
typedef void zio_done_func_t(zio_t *);
typedef void abd_t;
typedef struct {
  zio_t *zl_parent, *zl_child;
} zio_link_t;
enum {
  ZIO_CHILD_VDEV = 0,
  ZIO_WAIT_TYPES = 2,
  ZIO_WAIT_DONE = 1,
  ZIO_STAGE_READY = 1,
  ZIO_STAGE_OPEN = 0,
  ZIO_FLAG_PHYSICAL = 1,
  ZIO_FLAG_CANFAIL = 64,
  ZIO_FLAG_DONT_PROPAGATE = 2,
  ZIO_FLAG_DONT_RETRY = 4,
  ZIO_FLAG_DONT_QUEUE = 8,
  ZIO_FLAG_IO_BYPASS = 16,
  ZIO_FLAG_CONFIG_WRITER = 32,
  ZIO_PRIORITY_NOW = 0,
  ZIO_WRITE_PHYS_PIPELINE = 1,
  ZIO_FLUSH_PIPELINE = 2,
  ZCHECKSUM_FLAG_EMBEDDED = 1,
  VDEV_LABEL_START_SIZE = 1024,
  VDEV_LABEL_END_SIZE = 1024
};
#define ZIO_VDEV_CHILD_FLAGS 0xff
#define ASSERT0(x) ASSERT(!(x))
#define IMPLY(a, b) ASSERT(!(a) || (b))
static void *zio_link_cache = (void *)1, *zio_cache = (void *)2;
static unsigned retired;
static void mutex_enter(pthread_mutex_t *lock) {
  ASSERT(pthread_mutex_lock(lock) == 0);
}
static void mutex_exit(pthread_mutex_t *lock) {
  ASSERT(pthread_mutex_unlock(lock) == 0);
}
static void mutex_destroy(pthread_mutex_t *lock) {
  ASSERT(pthread_mutex_destroy(lock) == 0);
}
static int list_is_empty(graph_list_t *list) { return !list->count; }
static void list_insert_head(graph_list_t *list, void *item) {
  ASSERT(list->count < 128);
  list->items[list->count++] = item;
}
static void list_remove(graph_list_t *list, void *item) {
  for (unsigned i = 0; i < list->count; ++i) {
    if (list->items[i] == item) {
      list->items[i] = list->items[--list->count];
      return;
    }
  }
  abort();
}
static void list_destroy(graph_list_t *list) { ASSERT(!list->count); }
static void cv_destroy(int *cv) { (void)cv; }
static void metaslab_trace_fini(int *list) { (void)list; }
static void *kmem_cache_alloc(void *cache, int flags) {
  (void)flags;
  ASSERT(cache == zio_link_cache);
  return calloc(1, sizeof(zio_link_t));
}
static void kmem_cache_free(void *cache, void *p) {
  ASSERT(cache == zio_cache);
  ++retired;
  memset(p, 0xa5, sizeof(zio_t));
  free(p);
}
static void zio_add_child_impl(zio_t *, zio_t *, boolean_t);
void zio_destroy(zio_t *);
void zio_flush(zio_t *, vdev_t *);
static zio_t *zio_create(zio_t *parent, spa_t *owner, uint64_t txg,
                         const void *bp, void *data, uint64_t lsize,
                         uint64_t psize, zio_done_func_t *done, void *private,
                         int type, zio_priority_t priority, zio_flag_t flags,
                         vdev_t *vd, uint64_t offset, const void *bookmark,
                         int stage, int pipeline) {
  (void)bp;
  (void)lsize;
  (void)bookmark;
  (void)stage;
  zio_t *zio = calloc(1, sizeof(zio_t));
  ASSERT(zio && pthread_mutex_init(&zio->io_lock, NULL) == 0);
  zio->io_spa = owner;
  zio->io_vd = vd;
  zio->io_txg = txg;
  zio->io_size = psize;
  zio->io_abd = data;
  zio->io_type = type;
  zio->io_flags = flags;
  zio->io_priority = priority;
  zio->io_offset = offset;
  zio->io_pipeline = pipeline;
  zio->io_done = done;
  zio->io_private = private;
  if (parent)
    zio_add_child_impl(parent, zio, B_TRUE);
  return zio;
}
static void zio_nowait(zio_t *zio) { vdev_file_io_start(zio); }
static int vdev_is_concrete(vdev_t *vd) { return vd == &leaf; }
static struct {
  unsigned ci_flags;
} zio_checksum_table[1];
static void *abd_alloc_sametype(void *data, uint64_t size) {
  (void)data;
  return malloc(size);
}
static void abd_copy(void *dest, void *src, uint64_t size) {
  memcpy(dest, src, size);
}
static void zio_push_transform(zio_t *zio, void *buf, uint64_t lsize,
                               uint64_t psize, void *callback) {
  (void)zio;
  (void)buf;
  (void)lsize;
  (void)psize;
  (void)callback;
  abort(); /* Embedded checksum path not selected by this fixture. */
}
/* Exact pinned original graph/physical bodies, audited additions only. */
#include "pool-graph-bodies.inc"

static void host_graph_done(zio_t *zio) {
  /* Synthetic DONE/unlink, preserving the original destruction body. Parent
   * wait may return before already-completed descendants are destroyed. */
  if (zio->io_done)
    zio->io_done(zio);
  while (zio->io_parent_list.count) {
    zio_link_t *link = zio->io_parent_list.items[0];
    zio_t *parent = link->zl_parent;
    mutex_enter(&parent->io_lock);
    list_remove(&parent->io_child_list, link);
    for (unsigned w = 0; w < ZIO_WAIT_TYPES; ++w) {
      ASSERT(parent->io_children[0][w]);
      --parent->io_children[0][w];
    }
    mutex_exit(&parent->io_lock);
    list_remove(&zio->io_parent_list, link);
    free(link);
    if (parent->graph_auto && list_is_empty(&parent->io_child_list))
      host_graph_done(parent);
  }
  zio_destroy(zio);
}
static zio_t *root(void) {
  return zio_create(NULL, &spa, 0, NULL, NULL, 0, 0, NULL, NULL, 0, 0, 0, NULL,
                    0, NULL, 0, 0);
}
static zio_t *null_child(zio_t *parent) {
  zio_t *child = zio_create(parent, &spa, 0, NULL, NULL, 0, 0, NULL, NULL, 0, 0,
                            0, NULL, 0, NULL, 0, 0);
  child->graph_auto = 1;
  return child;
}
static unsigned char bytes[1024];
static zio_t *physical_write(zio_t *parent, uint64_t size) {
  return zio_write_phys(parent, &leaf, 4096, size, bytes, 0, NULL, NULL, 1,
                        ZIO_FLAG_CONFIG_WRITER, B_FALSE);
}
static int test_mode;
static unsigned token_for(unsigned phase, zio_t *zio, int required) {
  return aether_pool_root_begin(zio, &spa, 7, phase, required);
}
static void *phase_worker(void *parent) {
  for (unsigned i = 0; i < 64; ++i)
    zio_nowait(physical_write(parent, 512));
  return NULL;
}
static unsigned expected;
static int run_phase(unsigned phase) {
  zio_t *zio = root();
  int write = pool_phase_write(phase);
  int optional =
      test_mode == 1 && (phase == 2 || phase == 3 || phase == 6 || phase == 7);
  unsigned token = token_for(phase, zio, !optional);
  REQUIRE(token == phase);
  if (test_mode == 2 && phase == 5) {
    leaf.vdev_nowritecache = 1;
    expected = AETHER_POOL_BAD_EVENT;
  }
  if (test_mode == 3 && phase == 5) {
    zfs_nocacheflush = 1;
    expected = AETHER_POOL_BAD_EVENT | AETHER_POOL_INCOMPLETE;
  }
  if (test_mode == 4 && phase == 4) {
    mode = 4; /* Original provider partial write and ENOSPC leaf. */
    expected = AETHER_POOL_BAD_EVENT | AETHER_POOL_PARTIAL_WRITE |
               AETHER_POOL_LEAF_ERROR;
  }
  if (test_mode == 5 && phase == 5) {
    volume_file(leaf.vdev_tsd->vf_file)->volume.rights = 3;
    expected = AETHER_POOL_BAD_EVENT | AETHER_POOL_PROVIDER_ERROR |
               AETHER_POOL_LEAF_ERROR;
  }
  if (test_mode == 6 && phase == 4) {
    /* Whole requested write bypassed, not merely a missing stage marker. */
    zio_t *child = physical_write(zio, 512);
    host_graph_done(child);
    expected = AETHER_POOL_BAD_EVENT;
  } else if (test_mode == 16 && phase == 4) {
    zio_nowait(physical_write(zio, 512));
    host_graph_done(physical_write(zio, 512));
    expected = AETHER_POOL_BAD_EVENT;
  } else if (test_mode == 17 && phase == 4) {
    mode = 8; /* Original inline fixture taskq completes on worker. */
    pthread_t workers[16];
    for (unsigned i = 0; i < 16; ++i)
      REQUIRE(pthread_create(&workers[i], NULL, phase_worker, zio) == 0);
    for (unsigned i = 0; i < 16; ++i)
      REQUIRE(pthread_join(workers[i], NULL) == 0);
    REQUIRE(atomic_load(&pool_phases[phase - 1].requested_bytes) ==
            UINT64_C(1024) * 512);
    REQUIRE(atomic_load(&pool_phases[phase - 1].provided_bytes) ==
            UINT64_C(1024) * 512);
  } else if (test_mode == 7 && phase == 4) {
    /* Two original writes share one aggregate provider request. */
    zio_t *a = physical_write(zio, 512), *b = physical_write(zio, 512);
    a->graph_auto = b->graph_auto = 1;
    zio_t *aggregate =
        zio_create(NULL, &spa, 0, NULL, bytes, 1024, 1024, NULL, NULL,
                   ZIO_TYPE_WRITE, 0, 0, &leaf, 4096, NULL, 0, 0);
    zio_add_child_impl(a, aggregate, B_FALSE);
    zio_add_child_impl(b, aggregate, B_FALSE);
    zio_nowait(aggregate);
  } else if (!optional) {
    if (write) {
      zio_t *parent = phase == 2 || phase == 6 ? null_child(zio) : zio;
      zio_nowait(physical_write(parent, 512));
    } else {
      zio_flush(zio, &leaf);
    }
  }
  run_queue_reverse();
  host_graph_done(zio); /* Original wait consumes/frees root: scalar only. */
  aether_pool_root_end(token, 0);
  leaf.vdev_nowritecache = zfs_nocacheflush = 0;
  volume_file(leaf.vdev_tsd->vf_file)->volume.rights = 7;
  mode = 0;
  return 0;
}
int main(int argc, char **argv) {
  REQUIRE(argc == 2);
  test_mode = atoi(argv[1]);
  REQUIRE(test_mode >= 0 && test_mode <= 20);
  memset(bytes, 0x5b, sizeof(bytes));
  mode = 0;
  spa.spa_dsl_pool = &dp;
  REQUIRE(aether_zfs_volume_bind(17) == 0);
  leaf = (vdev_t){.vdev_spa = &spa,
                  .vdev_path = AETHER_VOLUME_PATH,
                  .vdev_ashift = 9,
                  .vdev_psize = 8192,
                  .readable = 1};
  REQUIRE(aether_pool_hooks_prepare(&witness) == 0);
  REQUIRE(open_leaf(&leaf) == 0);
  REQUIRE(aether_pool_hooks_bind_transaction(&selected_tx) == 0);
  REQUIRE(aether_pool_hooks_check_ordered() ==
          (AETHER_POOL_NO_WRITE | AETHER_POOL_NO_FLUSH |
           AETHER_POOL_TXG_PENDING | AETHER_POOL_INCOMPLETE));
  if (test_mode >= 8 && test_mode <= 15) {
    zio_t *zio = root();
    unsigned token = token_for(1, zio, 1);
    REQUIRE(token == 1);
    if (test_mode == 8) {
      REQUIRE(token_for(2, zio, 1) == 0);
      REQUIRE(atomic_load(&pool_problems) & AETHER_POOL_BAD_EVENT);
    } else if (test_mode == 9) {
      zio_t *foreign = root();
      foreign->io_spa = &foreign_spa;
      zio_add_child_impl(zio, foreign, B_TRUE);
      REQUIRE(atomic_load(&pool_problems) & AETHER_POOL_BAD_EVENT);
      host_graph_done(foreign);
    } else if (test_mode == 10) {
      zio_t *nodes[64];
      for (unsigned i = 0; i < 64; ++i)
        nodes[i] = null_child(zio);
      REQUIRE(atomic_load(&pool_problems) & AETHER_POOL_CAPACITY);
      /* Disable synthetic recursive auto-destruction of root. */
      for (unsigned i = 0; i < 64; ++i)
        host_graph_done(nodes[i]);
    } else if (test_mode == 11) {
      atomic_store(&pool_phases[0].requested_flushes, UINT64_MAX);
      zio_flush(zio, &leaf);
      run_queue_reverse();
      REQUIRE(atomic_load(&pool_problems) & AETHER_POOL_OVERFLOW);
    } else if (test_mode == 12) {
      zio_flush(zio, &leaf);
      run_queue_reverse();
      aether_pool_root_end(token, 0);
      REQUIRE(aether_pool_hooks_check_ordered() & AETHER_POOL_INCOMPLETE);
      host_graph_done(zio);
      aether_pool_root_end(token, 0); /* Duplicate end stays bad. */
      REQUIRE(atomic_load(&pool_problems) & AETHER_POOL_BAD_EVENT);
      vdev_file_close(&leaf);
      return 0;
    } else if (test_mode == 13) {
      zio_flush(zio, &leaf);
      run_queue_reverse();
      aether_pool_txg_observe(&dp, 7, 7, 0);
      REQUIRE(atomic_load(&pool_synced) == 0);
      REQUIRE(atomic_load(&pool_problems) & AETHER_POOL_BAD_EVENT);
    } else if (test_mode == 14) {
      zio_t *other = root();
      REQUIRE(aether_pool_root_begin(other, &spa, 8, 2, 1) == 0);
      REQUIRE(atomic_load(&pool_problems) == 0);
      host_graph_done(other);
    } else {
      aether_pool_txg_observe(&dp, 6, 6, 0);
      REQUIRE(atomic_load(&pool_synced) == 0 &&
              atomic_load(&pool_problems) == 0);
      aether_pool_txg_observe(&dp, 7, 7, EINTR);
      REQUIRE(atomic_load(&pool_problems) & AETHER_POOL_BAD_EVENT);
    }
    host_graph_done(zio);
    vdev_file_close(&leaf);
    return 0;
  }
  for (unsigned phase = 1; phase <= 7; ++phase)
    REQUIRE(run_phase(phase) == 0);
  if (test_mode == 18) {
    aether_pool_txg_observe(&dp, 7, 7, EINTR);
    REQUIRE(atomic_load(&pool_synced) == 0);
    expected = AETHER_POOL_BAD_EVENT;
  } else if (test_mode == 19) {
    dsl_pool_t foreign = {&spa};
    aether_pool_txg_observe(&foreign, 7, 7, 0);
    REQUIRE(atomic_load(&pool_synced) == 0);
    expected = AETHER_POOL_BAD_EVENT;
  }
  if (test_mode != 20)
    aether_pool_txg_observe(&dp, 7, 7, 0);
  else
    expected = AETHER_POOL_TXG_PENDING;
  REQUIRE(aether_pool_hooks_check_ordered() == expected);
  vdev_file_close(&leaf);
  REQUIRE(aether_pool_hooks_check_ordered() == expected);
  REQUIRE(retired >= 10);
  return 0;
}
