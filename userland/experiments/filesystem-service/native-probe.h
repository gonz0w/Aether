/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FS_POLICY_NATIVE_PROBE_H
#define AETHER_FS_POLICY_NATIVE_PROBE_H
#include <stdint.h>
struct spa;
typedef struct aether_fs_probe_result {
    uint64_t txg, bytes_staged, state;
} aether_fs_probe_result;
/* Proposed private synchronous callback. State0/1/2 describes write progress;
 * state3 is uncertain. Never infer no effects from errno, zero TXG or failed
 * readback. Not a durability acknowledgment or client protocol. Caller retains
 * full file/hash/metadata, ordered teardown and fresh-VM recovery oracles.
 * Live exclusive writable SPA, established UTC/accounting and a distinct
 * initialized writable output are required through return. */
int aether_fs_policy_write_probe(struct spa *, aether_fs_probe_result *);
#endif
