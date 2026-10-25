/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_POOL_LIFETIME_H
#define AETHER_POOL_LIFETIME_H
#include <stdint.h>
/* Private serialized engine owner only, after consuming its context. Pass the
 * exact original result and verification error. Success releases only a fully
 * synced, unborrowed record. EBUSY proves no release; failures never reset.
 * No pointer/client authority, whole-pool quiescence or replay permission. */
int aether_pool_lifetime_retire(int operation_error, uint64_t target,
                                uint64_t staged, uint64_t state);
#endif
