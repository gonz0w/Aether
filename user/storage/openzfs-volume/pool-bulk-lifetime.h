/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_POOL_BULK_LIFETIME_H
#define AETHER_POOL_BULK_LIFETIME_H
#include "pool-lifetime.h"
/* Trusted serialized owner only. The original context was consumed; error,
 * target/staged/state are the unmodified successful original result. expected
 * is the validated complete request length,1..4096, never inferred from an
 * untrusted reply. Mismatch, uncertainty, failed history, live graph/pin or bad
 * epoch refuses reuse. Namespace uses the separate fixed0 entry. No reset,
 * replay, durability or general uptime authorization. */
int aether_pool_namespace0_retire(int error, uint64_t target, uint64_t staged,
                                  uint64_t state);
int aether_pool_service_bytes_retire(int error, uint64_t target,
                                     uint64_t staged, uint64_t state,
                                     uint64_t expected);
#endif
