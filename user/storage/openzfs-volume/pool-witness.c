/* SPDX-License-Identifier: BSD-2-Clause */
#include "pool-witness.h"
#include <errno.h>

/* Low two bits are state; upper bits retain the generation after release.
 * BUSY is exclusive ownership, not a spin lock. Same-token contention fails
 * closed. The last FREE publication follows counters/errors and field access.
 */
enum { FREE = 0, BUSY = 1, OPEN = 2, PROVIDED = 3 };
#define GENERATION_MAX (UINT64_MAX >> 2)
_Static_assert(sizeof(struct aether_pool_witness) <= 8192,
               "private pool witness exceeds its observation budget");
_Static_assert(ATOMIC_LLONG_LOCK_FREE == 2,
               "pool witness requires lock-free 64-bit atomics");
_Static_assert(ATOMIC_INT_LOCK_FREE == 2,
               "pool witness requires lock-free problem flags");

static void problem(struct aether_pool_witness *w, unsigned bits)
{
    atomic_fetch_or_explicit(&w->problems, bits, memory_order_relaxed);
}

void aether_pool_witness_fail(struct aether_pool_witness *w, unsigned bits)
{
    problem(w, bits);
}

void aether_pool_witness_init(struct aether_pool_witness *w, const void *leaf,
                              const void *file, uint64_t target_txg)
{
    w->leaf = leaf;
    w->file = file;
    atomic_init(&w->target_txg, target_txg);
    atomic_init(&w->problems, (!leaf || !file) ? AETHER_POOL_BAD_EVENT : 0);
    atomic_init(&w->provider_error, 0);
    atomic_init(&w->leaf_error, 0);
    atomic_init(&w->writes, 0);
    atomic_init(&w->flushes, 0);
    for (unsigned i = 0; i < AETHER_POOL_WITNESS_SLOTS; ++i)
        atomic_init(&w->operations[i].state, FREE);
}

int aether_pool_witness_bind_txg(struct aether_pool_witness *w, uint64_t target)
{
    if (!target) {
        problem(w, AETHER_POOL_BAD_EVENT);
        return EINVAL;
    }
    uint64_t unbound = 0;
    if (!atomic_compare_exchange_strong_explicit(&w->target_txg, &unbound,
                                                 target, memory_order_release,
                                                 memory_order_relaxed)) {
        problem(w, AETHER_POOL_BAD_EVENT);
        return EALREADY;
    }
    return 0;
}

struct aether_pool_token aether_pool_io_begin(struct aether_pool_witness *w,
                                              enum aether_pool_io_kind kind,
                                              uint64_t txg, size_t count)
{
    struct aether_pool_token invalid = {AETHER_POOL_WITNESS_SLOTS, 0};
    if ((kind != AETHER_POOL_WRITE && kind != AETHER_POOL_FLUSH) ||
        (kind == AETHER_POOL_WRITE ? !count : count != 0)) {
        problem(w, AETHER_POOL_BAD_EVENT);
        return invalid;
    }
    for (unsigned i = 0; i < AETHER_POOL_WITNESS_SLOTS; ++i) {
        struct aether_pool_operation *op = &w->operations[i];
        uint64_t old = atomic_load_explicit(&op->state, memory_order_acquire);
        if ((old & 3) != FREE)
            continue;
        if ((old >> 2) == GENERATION_MAX) {
            problem(w, AETHER_POOL_OVERFLOW);
            continue;
        }
        uint64_t generation = (old >> 2) + 1;
        if (!atomic_compare_exchange_strong_explicit(
                &op->state, &old, (generation << 2) | BUSY,
                memory_order_acquire, memory_order_relaxed))
            continue;
        op->txg = txg;
        op->kind = kind;
        op->count = count;
        atomic_store_explicit(&op->state, (generation << 2) | OPEN,
                              memory_order_release);
        return (struct aether_pool_token){i, generation};
    }
    problem(w, AETHER_POOL_CAPACITY);
    return invalid;
}

static struct aether_pool_operation *claim(struct aether_pool_witness *w,
                                           struct aether_pool_token token,
                                           unsigned phase)
{
    if (token.slot >= AETHER_POOL_WITNESS_SLOTS || !token.generation ||
        token.generation > GENERATION_MAX) {
        problem(w, AETHER_POOL_BAD_EVENT);
        return NULL;
    }
    struct aether_pool_operation *op = &w->operations[token.slot];
    uint64_t expected = (token.generation << 2) | phase;
    if (!atomic_compare_exchange_strong_explicit(
            &op->state, &expected, (token.generation << 2) | BUSY,
            memory_order_acquire, memory_order_relaxed)) {
        problem(w, AETHER_POOL_BAD_EVENT);
        return NULL;
    }
    return op;
}

void aether_pool_provider_done(struct aether_pool_witness *w,
                               struct aether_pool_token token, const void *file,
                               int error, size_t residual)
{
    struct aether_pool_operation *op = claim(w, token, OPEN);
    if (!op)
        return;
    if (file != w->file || residual > op->count)
        problem(w, AETHER_POOL_BAD_EVENT);
    if (error) {
        int none = 0;
        atomic_compare_exchange_strong_explicit(&w->provider_error, &none,
                                                error, memory_order_relaxed,
                                                memory_order_relaxed);
        problem(w, AETHER_POOL_PROVIDER_ERROR);
    }
    if (op->kind == AETHER_POOL_WRITE && residual)
        problem(w, AETHER_POOL_PARTIAL_WRITE);
    atomic_store_explicit(&op->state, (token.generation << 2) | PROVIDED,
                          memory_order_release);
}

void aether_pool_leaf_done(struct aether_pool_witness *w,
                           struct aether_pool_token token, const void *leaf,
                           enum aether_pool_io_kind kind, uint64_t txg,
                           int error)
{
    struct aether_pool_operation *op = claim(w, token, PROVIDED);
    if (!op)
        return;
    if (leaf != w->leaf || kind != op->kind || txg != op->txg)
        problem(w, AETHER_POOL_BAD_EVENT);
    if (error) {
        int none = 0;
        atomic_compare_exchange_strong_explicit(&w->leaf_error, &none, error,
                                                memory_order_relaxed,
                                                memory_order_relaxed);
        problem(w, AETHER_POOL_LEAF_ERROR);
    }
    _Atomic uint64_t *counter =
        op->kind == AETHER_POOL_WRITE ? &w->writes : &w->flushes;
    if (atomic_fetch_add_explicit(counter, 1, memory_order_relaxed) ==
        UINT64_MAX)
        problem(w, AETHER_POOL_OVERFLOW);
    atomic_store_explicit(&op->state, token.generation << 2,
                          memory_order_release);
}

unsigned aether_pool_witness_check(const struct aether_pool_witness *w,
                                   uint64_t synced_txg)
{
    unsigned bits = 0;
    for (unsigned i = 0; i < AETHER_POOL_WITNESS_SLOTS; ++i)
        if ((atomic_load_explicit(&w->operations[i].state,
                                  memory_order_acquire) &
             3) != FREE)
            bits |= AETHER_POOL_INCOMPLETE;
    /* Read errors/counters after acquiring the final slot publications. Actual
     * upstream drain and no further admissions are still caller obligations. */
    bits |= atomic_load_explicit(&w->problems, memory_order_acquire);
    if (!atomic_load_explicit(&w->writes, memory_order_relaxed))
        bits |= AETHER_POOL_NO_WRITE;
    if (!atomic_load_explicit(&w->flushes, memory_order_relaxed))
        bits |= AETHER_POOL_NO_FLUSH;
    uint64_t target =
        atomic_load_explicit(&w->target_txg, memory_order_acquire);
    if (!target || synced_txg < target)
        bits |= AETHER_POOL_TXG_PENDING;
    return bits;
}
