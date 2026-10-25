/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_POOL_SERVICE_LIFETIME_H
#define AETHER_POOL_SERVICE_LIFETIME_H
#include <stdint.h>
/* Private, unselected service16 profile; never a client RPC. Serialized trusted
 * owner only, after consuming its sole C context. Preserve the exact original
 * errno/TXG/staged/state, including errors. Success requires16 staged bytes,
 * SYNCED and a fully observed, unborrowed original transaction. EBUSY releases
 * nothing. No reset, replacement/replay authority or device-quiescence promise.
 * Engine/code/SPA remain live through original drains. This distinct entry
 * cannot be substituted for the existing4096-byte lifetime profile. */
int aether_pool_service16_retire(int operation_error, uint64_t target,
                                 uint64_t staged, uint64_t state);
#endif
