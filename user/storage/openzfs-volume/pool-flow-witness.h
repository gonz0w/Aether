/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_POOL_FLOW_WITNESS_H
#define AETHER_POOL_FLOW_WITNESS_H
#include <stdint.h>
/* Private original-body observations, not a public storage/authority API.
 * No added upstream locks, allocation, I/O or changed outcomes. All incoming
 * object borrows are valid during the call. The returned scalar root token,
 * not its pointer, survives original zio_wait/destroy. */
enum aether_pool_root_phase {
  AETHER_POOL_BLOCK_ROOT = 1,
  AETHER_POOL_EVEN_WRITE_ROOT,
  AETHER_POOL_EVEN_FLUSH_ROOT,
  AETHER_POOL_UB_WRITE_ROOT,
  AETHER_POOL_UB_FLUSH_ROOT,
  AETHER_POOL_ODD_WRITE_ROOT,
  AETHER_POOL_ODD_FLUSH_ROOT
};
unsigned aether_pool_root_begin(const void *root, const void *spa, uint64_t txg,
                                unsigned phase, int required);
void aether_pool_root_end(unsigned token, int error);
void aether_pool_zio_child(const void *parent, const void *child);
void aether_pool_zio_retire(const void *zio);
void aether_pool_write_requested(const void *parent, const void *zio);
void aether_pool_flush_requested(const void *parent, const void *vdev);
/* Final only after actual drains. Zero means matched observations, not a
 * durable acknowledgment; native data/readback/recovery remain independent. */
unsigned aether_pool_hooks_check_ordered(void);
/* Lower-layer observation check, retained for focused file-vdev fixtures. */
unsigned aether_pool_hooks_check(uint64_t synced_txg);
#endif
