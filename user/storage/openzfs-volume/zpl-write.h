/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_ZPL_WRITE_H
#define AETHER_ZPL_WRITE_H

#include "zpl-read.h"

enum {
    AETHER_ZPL_UNASSIGNED = 0,
    AETHER_ZPL_COMMITTED = 1,
    AETHER_ZPL_SYNCED = 2
};
typedef struct aether_zpl_write_result {
    uint64_t txg;
    uint64_t bytes_staged;
    uint64_t state;
} aether_zpl_write_result;

/* Owner startup, not an RPC: after kernel_init, before import, with no
 * concurrent registry access. Code lives through all drains and kernel_fini. */
void aether_zpl_accounting_init(void);

/* Private engine-owner FFI; never accept these pointers/raw object identities
 * from clients. Select zpl-write.c INSTEAD OF zpl-read.c, never both. The new
 * writable factory retains the reader's format/root/SPA validation and requires
 * writable ownership and readonly property0. The readonly factory is unchanged.
 * Readonly probe validation precedes writable own; required accounting upgrades
 * reject. Probe SA pointers are discarded before fresh writable ownership.
 * Owner registers the original ZPL accounting callback before import/ownership;
 * disabled accounting rejects, even if the dataset otherwise looks complete.
 * Borrow SPA until consuming close, serialize all calls/property changes and
 * forbid concurrent dataset mutation/export/teardown. No pointer escapes.
 */
int aether_zpl_open_write(struct spa *, const char *, aether_zpl_view **);

/* Context comes from open_write. Buffer has length initialized readable bytes,
 * remains valid through return and must not alias result/context/engine state.
 * UTC scalar values come from trusted userland policy; no clock is read here.
 * Existing regular SA files only: overwrite/append without a hole, <=4096
 * bytes. Result is initialized even on rejection. Positive errno is NOT a
 * statement of no effects: an assigned tx always commits, even on failed SA
 * update. After a committed error, retire/investigate; never retry or mutate
 * this context again. bytes_staged is DMU progress, not a POSIX return value.
 * SYNCED is not a public durability acknowledgment: ordered I/O and recovery
 * qualification are separate. Native preparation selects
 * AETHER_ZPL_ORDERED_WRITE: bind the actual assigned transaction before data/SA
 * changes. Failed binding commits without staging bytes. The present witness
 * accepts one transaction per engine lifetime, with no reset or retry.
 */
int aether_zpl_write(aether_zpl_view *, uint64_t object, uint64_t generation,
                     uint64_t offset, const void *, size_t length,
                     uint64_t seconds, uint64_t nanoseconds,
                     aether_zpl_write_result *);

#endif
