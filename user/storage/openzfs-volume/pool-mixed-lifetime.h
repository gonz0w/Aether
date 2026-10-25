/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_POOL_MIXED_LIFETIME_H
#define AETHER_POOL_MIXED_LIFETIME_H
#include <stdint.h>
/* Private approved mixed profile. Serialized trusted engine owner only, after
 * consuming/nulling the sole C context. Preserve original errno/TXG/staged/state.
 * namespace0 requires successful namespace progress with exactly0 staged bytes;
 * service16 requires exactly16. Both require SYNCED, fully observed unborrowed
 * original transaction, matching live SPA/epoch and no permanent error.
 * EBUSY releases nothing. No client RPC, arbitrary staging selector, reset,
 * failed-record recycling, automatic replay or device-quiescence guarantee.
 * Engine/code/SPA remain live through original drains. */
int aether_pool_namespace0_retire(int error, uint64_t target,
                                 uint64_t staged, uint64_t state);
int aether_pool_service16_retire(int error, uint64_t target,
                                uint64_t staged, uint64_t state);
#endif
