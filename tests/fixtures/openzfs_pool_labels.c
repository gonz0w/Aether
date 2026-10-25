/* SPDX-License-Identifier: BSD-2-Clause */
/* Original config/uberblock/label-list/callback bodies. Lower ZIO, label data,
 * allocation and transport are synthetic: no filesystem or durability claim. */
#include "pool-flow-witness.h"
#include "pool-sync-witness.h"
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef int boolean_t;
#define B_TRUE 1
#define B_FALSE 0
typedef struct vdev vdev_t;
typedef struct {
  vdev_t *head;
} list_t;
typedef struct {
  uint64_t ub_txg;
} uberblock_t;
typedef struct {
  int sav_count, sav_label_sync;
  vdev_t **sav_vdevs;
} spa_aux_vdev_t;
typedef struct spa {
  uberblock_t spa_uberblock;
  vdev_t *spa_root_vdev;
  list_t spa_config_dirty_list, spa_vdev_txg_list;
  struct {
    uint64_t mmp_delay;
  } spa_mmp;
  uint64_t spa_final_txg;
  int spa_aux_sync_uber;
  spa_aux_vdev_t spa_spares, spa_l2cache;
} spa_t;
struct vdev {
  spa_t *vdev_spa;
  int vdev_ishole, vdev_islog;
  void *vdev_aux;
};
typedef struct zio {
  struct zio *parent;
  void *io_private;
  void (*done)(struct zio *);
  int io_error;
} zio_t;
enum {
  ZIO_FLAG_CONFIG_WRITER = 1,
  ZIO_FLAG_CANFAIL = 2,
  ZIO_FLAG_IO_RETRY = 4
};
static int mode;
static spa_t *owner;
static char trace[256];
static unsigned trace_count, stages[7], errors, even_calls, odd_calls,
    flush_calls;
static void event(char symbol) {
  if (trace_count >= sizeof(trace) - 1)
    abort();
  trace[trace_count++] = symbol;
}
static vdev_t *list_head(list_t *list) { return list->head; }
static vdev_t *list_next(list_t *list, vdev_t *vd) {
  (void)list;
  (void)vd;
  return NULL;
}
static int list_is_empty(list_t *list) { return !list->head; }
#define TXG_CLEAN(txg) (txg)
static vdev_t *txg_list_head(list_t *list, uint64_t txg) {
  (void)txg;
  return list_head(list);
}
static vdev_t *txg_list_next(list_t *list, vdev_t *vd, uint64_t txg) {
  (void)txg;
  return list_next(list, vd);
}
static int spa_multihost(spa_t *spa) {
  (void)spa;
  return 0;
}
static uint64_t spa_freeze_txg(spa_t *spa) {
  (void)spa;
  return mode == 1 ? 6 : UINT64_MAX;
}
static const char *spa_name(spa_t *spa) {
  (void)spa;
  return "fixture";
}
static int uberblock_update(uberblock_t *ub, vdev_t *root, uint64_t txg,
                            uint64_t delay) {
  (void)root;
  (void)delay;
  if (mode == 2)
    return 0;
  ub->ub_txg = txg;
  return 1;
}
static void mmp_update_uberblock(spa_t *spa, uberblock_t *ub) {
  (void)spa;
  (void)ub;
  abort();
}
static void zfs_dbgmsg(const char *format, ...) { (void)format; }
#define ASSERT(x)                                                              \
  do {                                                                         \
    if (!(x))                                                                  \
      abort();                                                                 \
  } while (0)
#define SET_ERROR(error) (error)
#define KM_SLEEP 0
static void *kmem_zalloc(size_t size, int flags) {
  (void)flags;
  void *p = calloc(1, size);
  if (!p)
    abort();
  return p;
}
static void kmem_free(void *pointer, size_t size) {
  (void)size;
  free(pointer);
}
static zio_t *zio_root(spa_t *spa, void *done, void *private, int flags) {
  (void)spa;
  (void)done;
  (void)private;
  (void)flags;
  return kmem_zalloc(sizeof(zio_t), 0);
}
static zio_t *zio_null(zio_t *parent, spa_t *spa, void *bp,
                       void (*done)(zio_t *), void *private, int flags) {
  (void)spa;
  (void)bp;
  (void)flags;
  zio_t *zio = kmem_zalloc(sizeof(zio_t), 0);
  zio->parent = parent;
  zio->done = done;
  zio->io_private = private;
  return zio;
}
static void zio_nowait(zio_t *zio) {
  zio->done(zio);
  if (zio->io_error)
    zio->parent->io_error = zio->io_error;
  free(zio);
}
static int zio_wait(zio_t *zio) {
  event('W');
  int error = zio->io_error;
  memset(zio, 0xa5, sizeof(*zio));
  free(zio);
  return error;
}
static int vdev_writeable(vdev_t *vd) {
  (void)vd;
  return 1;
}
static void zio_flush(zio_t *zio, vdev_t *vd) {
  (void)zio;
  (void)vd;
  if (mode == 4)
    return;
  event('F');
  ++flush_calls;
}
static void vdev_uberblock_sync(zio_t *zio, uint64_t *good, uberblock_t *ub,
                                vdev_t *vd, int flags) {
  (void)zio;
  (void)ub;
  (void)vd;
  (void)flags;
  event('U');
  if (mode != 8)
    ++*good;
}
static void vdev_label_sync(zio_t *zio, uint64_t *good, vdev_t *vd, int label,
                            uint64_t txg, int flags) {
  (void)zio;
  (void)vd;
  (void)txg;
  (void)flags;
  event(label ? 'O' : 'E');
  if (label)
    ++odd_calls;
  else
    ++even_calls;
  if ((mode == 5 && label == 0) || (mode == 6 && label == 1) ||
      (mode == 7 && label == 0 && even_calls == 1))
    return;
  ++*good;
}
void aether_pool_sync_observe(const void *spa, uint64_t txg,
                              enum aether_pool_sync_stage stage, int error) {
  ASSERT(spa == owner && txg == 7 && stage >= 1 && stage <= 6);
  ++stages[stage];
  if (error)
    ++errors;
  const char symbols[] = "?ABCDGH";
  event(symbols[stage]);
}
static unsigned root_begins[8], root_ends[8];
unsigned aether_pool_root_begin(const void *root, const void *spa, uint64_t txg,
                                unsigned phase, int required) {
  ASSERT(root && spa == owner && txg == 7 && phase >= 1 && phase <= 7);
  ASSERT(required == 0 || required == 1);
  ++root_begins[phase];
  return phase;
}
void aether_pool_root_end(unsigned phase, int error) {
  ASSERT(phase >= 1 && phase <= 7);
  ASSERT(error == 0 || error == EIO);
  ++root_ends[phase];
}
/* Generated original CDDL bodies and notices with only observer additions. */
#include "pool-label-bodies.inc"
#define REQUIRE(x)                                                             \
  do {                                                                         \
    if (!(x)) {                                                                \
      fprintf(stderr, "label ordering rejection: %s\n", #x);                   \
      return 1;                                                                \
    }                                                                          \
  } while (0)
int main(int argc, char **argv) {
  REQUIRE(argc == 2);
  mode = atoi(argv[1]);
  REQUIRE(mode >= 0 && mode <= 8);
  spa_t spa = {0};
  owner = &spa;
  vdev_t leaf = {.vdev_spa = &spa};
  vdev_t *selected[] = {&leaf};
  spa.spa_uberblock.ub_txg = mode == 1 || mode == 2 ? 6 : 7;
  spa.spa_root_vdev = &leaf;
  spa.spa_final_txg = UINT64_MAX;
  spa.spa_config_dirty_list.head = mode == 2 ? NULL : &leaf;
  spa.spa_vdev_txg_list.head = mode == 3 ? NULL : &leaf;
  int result = vdev_config_sync(selected, 1, 7);
  const char *healthy = "AFWBEWFWCUWDFWGOWFWH";
  if (mode == 0) {
    for (unsigned i = 1; i <= 7; ++i)
      REQUIRE(root_begins[i] == 1 && root_ends[i] == 1);
    REQUIRE(result == 0 && strcmp(trace, healthy) == 0 && errors == 0);
    REQUIRE(flush_calls == 4 && even_calls == 1 && odd_calls == 1);
  } else if (mode == 3) {
    REQUIRE(result == 0 && strcmp(trace, "AWBEWFWCUWDFWGOWFWH") == 0);
    REQUIRE(flush_calls == 3 && stages[AETHER_POOL_CONFIG_COMPLETE] == 1);
  } else if (mode == 1 || mode == 2) {
    REQUIRE(result == 0 && strcmp(trace, "A") == 0);
    REQUIRE(stages[AETHER_POOL_CONFIG_COMPLETE] == 0 && flush_calls == 0);
  } else if (mode == 4) {
    /* All markers and parent waits succeed even without provider flushes.
     */
    REQUIRE(result == 0 && stages[AETHER_POOL_CONFIG_COMPLETE] == 1);
    REQUIRE(flush_calls == 0 && strcmp(trace, healthy) != 0);
  } else if (mode == 5 || mode == 6 || mode == 8) {
    REQUIRE(result == EIO && stages[AETHER_POOL_CONFIG_ATTEMPT] == 3);
    REQUIRE(stages[AETHER_POOL_CONFIG_COMPLETE] == 0 && errors >= 2);
  } else if (mode == 7) {
    REQUIRE(result == 0 && stages[AETHER_POOL_CONFIG_ATTEMPT] == 2);
    REQUIRE(stages[AETHER_POOL_CONFIG_COMPLETE] == 1 && errors == 1);
    REQUIRE(even_calls == 2 && odd_calls == 1);
  }
  return 0;
}
