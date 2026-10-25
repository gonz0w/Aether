/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_POOL_WITNESS_H
#define AETHER_POOL_WITNESS_H
#include <stdatomic.h>
#include <stddef.h>
#include <stdint.h>

/* Private host-qualified prerequisite, selected by the opt-in pool checkpoint.
 * Initialize before helper publication. Check/dispose only after actual
 * upstream drains, with no new admissions. Tokens confer no authority. Identity
 * borrows outlive their operations; they are compared only, never dereferenced.
 * No reset operation: an uncertain run cannot license reuse or release of
 * device work. */
#define AETHER_POOL_WITNESS_SLOTS 128
enum aether_pool_io_kind { AETHER_POOL_WRITE = 1, AETHER_POOL_FLUSH = 2 };
enum aether_pool_witness_problem {
    AETHER_POOL_BAD_EVENT = 1,
    AETHER_POOL_CAPACITY = 2,
    AETHER_POOL_PROVIDER_ERROR = 4,
    AETHER_POOL_PARTIAL_WRITE = 8,
    AETHER_POOL_LEAF_ERROR = 16,
    AETHER_POOL_INCOMPLETE = 32,
    AETHER_POOL_NO_WRITE = 64,
    AETHER_POOL_NO_FLUSH = 128,
    AETHER_POOL_TXG_PENDING = 256,
    AETHER_POOL_OVERFLOW = 512
};
struct aether_pool_token {
    unsigned slot;
    uint64_t generation;
};
struct aether_pool_operation {
    _Atomic uint64_t state;
    /* Access only under exclusive BUSY ownership of state. */
    uint64_t txg;
    size_t count;
    enum aether_pool_io_kind kind;
};
struct aether_pool_witness {
    /* Identity is immutable between publication and actual upstream drain. */
    const void *leaf, *file;
    /* Zero until the selected original transaction's target is bound once. */
    _Atomic uint64_t target_txg;
    _Atomic unsigned problems;
    /* First nonzero original error at each boundary; later success cannot erase
     * it. This bounded diagnostic is not an event log or retry instruction. */
    _Atomic int provider_error, leaf_error;
    _Atomic uint64_t writes, flushes;
    struct aether_pool_operation operations[AETHER_POOL_WITNESS_SLOTS];
};
void aether_pool_witness_init(struct aether_pool_witness *, const void *leaf,
                              const void *file, uint64_t target_txg);
/* Original assigned-transaction getter, before commit, supplies this target.
 * The caller proves transaction/pool identity and keeps its borrows live.
 * Zero/repeated/conflicting attempts return EINVAL/EALREADY and reject the run.
 * Binding can overlap I/O; it never clears earlier observations or problems.
 * No further binding/admission may overlap final inspection or disposal. */
int aether_pool_witness_bind_txg(struct aether_pool_witness *, uint64_t target);
/* Private observers report a failed association without fabricating an I/O
 * result or consuming another operation. Bits are sticky, never an authority.
 */
void aether_pool_witness_fail(struct aether_pool_witness *, unsigned bits);
struct aether_pool_token aether_pool_io_begin(struct aether_pool_witness *,
                                              enum aether_pool_io_kind,
                                              uint64_t observed_txg,
                                              size_t count);
void aether_pool_provider_done(struct aether_pool_witness *,
                               struct aether_pool_token, const void *file,
                               int error, size_t residual);
void aether_pool_leaf_done(struct aether_pool_witness *,
                           struct aether_pool_token, const void *leaf,
                           enum aether_pool_io_kind, uint64_t observed_txg,
                           int error);
/* Zero means matched observations only, never a durable acknowledgment. The
 * future native caller must obtain synced_txg from original TXG
 * synchronization, prove ordering/bypass conditions and drain helpers
 * independently. */
unsigned aether_pool_witness_check(const struct aether_pool_witness *,
                                   uint64_t synced_txg);
#endif
