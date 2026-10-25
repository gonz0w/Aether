/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_POOL_SYNC_WITNESS_H
#define AETHER_POOL_SYNC_WITNESS_H
#include <stdint.h>
/* Private callbacks for the opt-in pool checkpoint. Consumers
 * must provide bounded nonblocking observations: no I/O, upstream locking or
 * changed outcomes. Identity borrows are valid only during the call. These
 * facts alone cannot acknowledge durability or authorize cleanup/replacement.
 */
enum aether_pool_sync_stage {
    AETHER_POOL_CONFIG_ATTEMPT = 1,
    AETHER_POOL_BLOCK_FLUSH_RETURNED,
    AETHER_POOL_EVEN_LABELS_RETURNED,
    AETHER_POOL_UB_WRITES_RETURNED,
    AETHER_POOL_UB_FLUSH_RETURNED,
    AETHER_POOL_CONFIG_COMPLETE
};
/* Called under original tx_sync_lock, including failed/unfinished waits.
 * requested_txg is the original function's resolved target, never a guess. */
void aether_pool_txg_observe(const void *dsl_pool, uint64_t requested_txg,
                             uint64_t synced_txg, int error);
/* Parent flush waits can hide child errors. Returned here means the original
 * wait/call returned; actual root/leaf/provider completion remains independent.
 * UB_WRITES records original good-write status; CONFIG_ATTEMPT retains retries.
 */
void aether_pool_sync_observe(const void *spa, uint64_t txg,
                              enum aether_pool_sync_stage, int error);
#endif
