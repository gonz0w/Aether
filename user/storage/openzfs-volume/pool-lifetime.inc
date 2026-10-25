/* SPDX-License-Identifier: BSD-2-Clause */
/* One successful-TXG record, reusable only after explicit checked retirement.
 * Original graph borrows/locks protect addresses. A gate pins record access;
 * monotonically increasing epochs isolate callbacks across record reuse.
 * Device identity, errors, first target and cumulative completion never reset.
 */
#include "pool-flow-witness.h"
#include "pool-sync-witness.h"
#include "pool-lifetime.h"
#include <limits.h>
#define POOL_GRAPH_SLOTS 64
#define POOL_FLOW_ACTIVE 8
struct pool_node {
    _Atomic uintptr_t address;
    _Atomic unsigned phase;
};
struct pool_phase {
    _Atomic uint64_t requested_bytes, provided_bytes, requested_flushes,
        provided_flushes;
    _Atomic unsigned writes, required;
};
struct pool_lifetime_record {
    _Atomic uint64_t txg, synced;
    _Atomic unsigned step;
    struct pool_phase phases[7];
};
static struct pool_node pool_nodes[POOL_GRAPH_SLOTS];
static struct pool_lifetime_record pool_record;
/* Gate low bit is exclusive, upper bits count reader pins. An exclusive owner
 * only succeeds at0. No pointer to record state may escape a reader pin. */
static _Atomic unsigned pool_gate, pool_epoch;
static _Atomic uint64_t pool_retired_txg, pool_completed, pool_synced;

static int pool_enter(void)
{
    unsigned old = atomic_load_explicit(&pool_gate, memory_order_relaxed);
    for (;;) {
        if (old & 1) {
            pool_problem();
            return 0;
        }
        if (old > UINT_MAX - 2) {
            atomic_fetch_or(&pool_problems, AETHER_POOL_OVERFLOW);
            return 0;
        }
        if (atomic_compare_exchange_weak_explicit(&pool_gate, &old, old + 2,
                                                  memory_order_acquire,
                                                  memory_order_relaxed))
            return 1;
    }
}
static void pool_leave(void)
{
    atomic_fetch_sub_explicit(&pool_gate, 2, memory_order_release);
}
static int pool_exclusive(void)
{
    unsigned free = 0;
    return atomic_compare_exchange_strong_explicit(
        &pool_gate, &free, 1, memory_order_acquire, memory_order_relaxed);
}
static void pool_release(void)
{
    atomic_store_explicit(&pool_gate, 0, memory_order_release);
}
/* Only exclusive owner writes reusable fields. Atomic stores preserve defined
 * access even for independently filtered scalar observations; no atomic_init
 * after helper publication. This never clears a permanent outcome. */
static void pool_record_clear(void)
{
    atomic_store(&pool_record.txg, 0);
    atomic_store(&pool_record.synced, 0);
    atomic_store(&pool_record.step, 0);
    for (unsigned i = 0; i < 7; ++i) {
        atomic_store(&pool_record.phases[i].requested_bytes, 0);
        atomic_store(&pool_record.phases[i].provided_bytes, 0);
        atomic_store(&pool_record.phases[i].requested_flushes, 0);
        atomic_store(&pool_record.phases[i].provided_flushes, 0);
        atomic_store(&pool_record.phases[i].writes, 0);
        atomic_store(&pool_record.phases[i].required, 0);
    }
}
static void pool_flow_prepare(void)
{
    atomic_init(&pool_gate, 0);
    atomic_init(&pool_epoch, 0);
    atomic_init(&pool_retired_txg, 0);
    atomic_init(&pool_completed, 0);
    atomic_init(&pool_synced, 0);
    pool_record_clear();
    for (unsigned i = 0; i < POOL_GRAPH_SLOTS; ++i) {
        atomic_init(&pool_nodes[i].address, 0);
        atomic_init(&pool_nodes[i].phase, 0);
    }
}
static int pool_repeat_bind(dsl_pool_t *dp, uint64_t target)
{
    if (!pool_exclusive())
        return EBUSY;
    int error = 0;
    unsigned epoch = atomic_load(&pool_epoch);
    if (atomic_load(&pool_problems) || atomic_load(&pool_observer->problems))
        error = EIO;
    else if (atomic_load(&pool_record.txg) || !target ||
             target <= atomic_load(&pool_retired_txg) ||
             epoch != atomic_load(&pool_completed) ||
             (epoch && (dp != pool_dp ||
                        atomic_load(&pool_transaction) != POOL_TX_BOUND))) {
        pool_problem();
        error = EINVAL;
    } else if (epoch == UINT_MAX / 8) {
        atomic_fetch_or(&pool_problems, AETHER_POOL_OVERFLOW);
        error = EOVERFLOW;
    } else if (!epoch) {
        unsigned unbound = POOL_TX_UNBOUND;
        if (!atomic_compare_exchange_strong(&pool_transaction, &unbound,
                                            POOL_TX_BINDING)) {
            pool_problem();
            error = EALREADY;
        } else {
            error = aether_pool_witness_bind_txg(pool_observer, target);
            if (error)
                pool_problem();
            else
                pool_dp = dp;
        }
    }
    if (!error) {
        atomic_store(&pool_record.txg, target);
        atomic_store(&pool_epoch, epoch + 1);
        atomic_store_explicit(&pool_transaction, POOL_TX_BOUND,
                              memory_order_release);
    }
    pool_release();
    return error;
}
static struct pool_lifetime_record *pool_lifetime_find(uint64_t target,
                                                       unsigned *epoch)
{
    if (!target || atomic_load(&pool_record.txg) != target)
        return NULL;
    *epoch = atomic_load(&pool_epoch);
    return &pool_record;
}

unsigned aether_pool_hooks_check(uint64_t);
static unsigned pool_node_phase(const void *identity)
{
    uintptr_t address = (uintptr_t)identity;
    if (address <= 1)
        return 0;
    for (unsigned i = 0; i < POOL_GRAPH_SLOTS; ++i) {
        if (atomic_load_explicit(&pool_nodes[i].address,
                                 memory_order_acquire) == address)
            return atomic_load_explicit(&pool_nodes[i].phase,
                                        memory_order_relaxed);
    }
    return 0;
}

static void pool_node_add(const void *identity, unsigned phase)
{
    uintptr_t address = (uintptr_t)identity;
    if (address <= 1 || !(phase % 8) || phase / 8 != atomic_load(&pool_epoch) ||
        !atomic_load(&pool_record.txg)) {
        pool_problem();
        return;
    }
    unsigned existing = pool_node_phase(identity);
    if (existing) {
        if (existing != phase)
            pool_problem(); /* Never relabel an aggregate/shared child. */
        return;
    }
    for (unsigned i = 0; i < POOL_GRAPH_SLOTS; ++i) {
        uintptr_t free_address = 0;
        if (!atomic_compare_exchange_strong_explicit(
                &pool_nodes[i].address, &free_address, 1, memory_order_acquire,
                memory_order_relaxed))
            continue;
        atomic_store_explicit(&pool_nodes[i].phase, phase,
                              memory_order_relaxed);
        atomic_store_explicit(&pool_nodes[i].address, address,
                              memory_order_release);
        return;
    }
    atomic_fetch_or_explicit(&pool_problems, AETHER_POOL_CAPACITY,
                             memory_order_relaxed);
}

static unsigned pool_root_begin_body(const void *identity, const void *spa,
                                     uint64_t txg, unsigned phase, int required)
{
    if (!pool_observer ||
        atomic_load_explicit(&pool_transaction, memory_order_acquire) !=
            POOL_TX_BOUND)
        return 0; /* Earlier constructor/create TXGs cannot qualify target. */
    unsigned index = 0;
    struct pool_lifetime_record *record = pool_lifetime_find(txg, &index);
    if (!record)
        return 0; /* Unselected original TXGs have independent work. */
    if (atomic_load_explicit(&pool_publication, memory_order_acquire) !=
            POOL_READY ||
        spa != pool_spa || !identity || phase < 1 || phase > 7) {
        pool_problem();
        return 0;
    }
    const zio_t *root = identity;
    if (root->io_spa != pool_spa || pool_node_phase(root)) {
        pool_problem();
        return 0;
    }
    unsigned previous = phase - 1;
    if (!atomic_compare_exchange_strong_explicit(
            &record->step, &previous, phase + POOL_FLOW_ACTIVE,
            memory_order_acquire, memory_order_relaxed)) {
        pool_problem(); /* Overlap, omission, retry or reordered phase. */
        return 0;
    }
    atomic_store(&record->phases[phase - 1].required, !!required);
    unsigned token = index * 8 + phase;
    pool_node_add(root, token);
    return token;
}

static void pool_zio_child_body(const void *parent, const void *child)
{
    unsigned phase = pool_node_phase(parent);
    if (!phase) {
        if (pool_node_phase(child))
            pool_problem(); /* Do not mix unrelated parents into this phase. */
        return;
    }
    const zio_t *pio = parent, *cio = child;
    if (pio->io_spa != pool_spa || cio->io_spa != pool_spa) {
        pool_problem();
        return;
    }
    pool_node_add(child, phase);
}

void aether_pool_zio_retire(const void *identity)
{
    uintptr_t address = (uintptr_t)identity;
    if (address <= 1)
        return;
    for (unsigned i = 0; i < POOL_GRAPH_SLOTS; ++i) {
        uintptr_t expected = address;
        if (atomic_compare_exchange_strong_explicit(
                &pool_nodes[i].address, &expected, 0, memory_order_release,
                memory_order_relaxed))
            return;
    }
}

static void pool_add_count(_Atomic uint64_t *counter, uint64_t value)
{
    uint64_t old =
        atomic_fetch_add_explicit(counter, value, memory_order_relaxed);
    if (value > UINT64_MAX - old)
        atomic_fetch_or_explicit(&pool_problems, AETHER_POOL_OVERFLOW,
                                 memory_order_relaxed);
}

static int pool_phase_write(unsigned phase)
{
    phase %= 8;
    return phase == AETHER_POOL_EVEN_WRITE_ROOT ||
           phase == AETHER_POOL_UB_WRITE_ROOT ||
           phase == AETHER_POOL_ODD_WRITE_ROOT;
}

/* Caller holds a reader pin through all returned field access. */
static struct pool_phase *pool_active_phase(unsigned phase, int write)
{
    if (!phase)
        return NULL;
    unsigned local = phase % 8;
    if (!local || phase / 8 != atomic_load(&pool_epoch) ||
        !atomic_load(&pool_record.txg) || pool_phase_write(phase) != !!write ||
        atomic_load_explicit(&pool_record.step, memory_order_acquire) !=
            local + POOL_FLOW_ACTIVE) {
        pool_problem();
        return NULL;
    }
    return &pool_record.phases[local - 1];
}

static void pool_write_requested_body(const void *parent, const void *identity)
{
    const zio_t *zio = identity;
    unsigned token = pool_node_phase(parent);
    if (token != pool_node_phase(zio)) {
        pool_problem(); /* A missing physical-child association cannot hide. */
        return;
    }
    struct pool_phase *phase = pool_active_phase(token, 1);
    if (!phase)
        return;
    if (zio->io_spa != pool_spa || zio->io_vd != pool_observer->leaf ||
        zio->io_type != ZIO_TYPE_WRITE || !zio->io_size) {
        pool_problem();
        return;
    }
    pool_add_count(&phase->requested_bytes, zio->io_size);
}

static void pool_flush_requested_body(const void *parent, const void *vdev)
{
    if (!pool_observer || vdev != pool_observer->leaf)
        return; /* Original recursion reaches the selected concrete leaf. */
    struct pool_phase *phase = pool_active_phase(pool_node_phase(parent), 0);
    if (phase)
        pool_add_count(&phase->requested_flushes, 1);
}

static void pool_phase_provided_body(unsigned token, int write, uint64_t count,
                                     int error, size_t residual)
{
    struct pool_phase *phase = pool_active_phase(token, write);
    if (!phase || error || residual)
        return; /* Existing operation ledger preserves original failures. */
    if (write) {
        pool_add_count(&phase->provided_bytes, count);
        if (atomic_fetch_add(&phase->writes, 1) == UINT32_MAX)
            atomic_fetch_or(&pool_problems, AETHER_POOL_OVERFLOW);
    } else {
        pool_add_count(&phase->provided_flushes, 1);
    }
}

static void pool_root_end_body(unsigned token, int error)
{
    if (!token)
        return;
    unsigned index = token / 8;
    unsigned local = token % 8;
    if (!local || index != atomic_load(&pool_epoch) ||
        !atomic_load(&pool_record.txg)) {
        pool_problem();
        return;
    }
    struct pool_lifetime_record *record = &pool_record;
    struct pool_phase *phase = &record->phases[local - 1];
    uint64_t requested = pool_phase_write(token)
                             ? atomic_load(&phase->requested_bytes)
                             : atomic_load(&phase->requested_flushes);
    uint64_t provided = pool_phase_write(token)
                            ? atomic_load(&phase->provided_bytes)
                            : atomic_load(&phase->provided_flushes);
    if (error || requested != provided ||
        (atomic_load(&phase->required) && !requested) ||
        (pool_phase_write(token) && requested && !atomic_load(&phase->writes)))
        pool_problem();
    unsigned active = local + POOL_FLOW_ACTIVE;
    if (!atomic_compare_exchange_strong_explicit(&record->step, &active, local,
                                                 memory_order_release,
                                                 memory_order_relaxed))
        pool_problem();
}

static void pool_sync_observe_body(const void *spa, uint64_t txg,
                                   enum aether_pool_sync_stage stage, int error)
{
    if (!pool_observer ||
        atomic_load_explicit(&pool_transaction, memory_order_acquire) !=
            POOL_TX_BOUND)
        return;
    unsigned index = 0;
    struct pool_lifetime_record *record = pool_lifetime_find(txg, &index);
    if (!record)
        return;
    /* Retain existing original-boundary diagnostics without another stage
     * ledger. Only actual roots/requests/provider completions qualify ordering.
     */
    const unsigned completed[] = {0, 0, 1, 3, 4, 5, 7};
    if (spa != pool_spa || stage < 1 || stage > 6 || error ||
        atomic_load(&record->step) != completed[stage])
        pool_problem();
}

/* Public callback wrappers own reader pins; inner helpers never acquire twice.
 */
unsigned aether_pool_root_begin(const void *identity, const void *spa,
                                uint64_t txg, unsigned phase, int required)
{
    if (!txg || atomic_load(&pool_record.txg) != txg)
        return 0;
    if (!pool_enter())
        return 0;
    unsigned token = pool_root_begin_body(identity, spa, txg, phase, required);
    pool_leave();
    return token;
}
void aether_pool_zio_child(const void *parent, const void *child)
{
    if (!pool_node_phase(parent) && !pool_node_phase(child))
        return;
    if (!pool_enter())
        return;
    pool_zio_child_body(parent, child);
    pool_leave();
}
void aether_pool_write_requested(const void *parent, const void *identity)
{
    if (!pool_node_phase(parent) && !pool_node_phase(identity))
        return;
    if (!pool_enter())
        return;
    pool_write_requested_body(parent, identity);
    pool_leave();
}
void aether_pool_flush_requested(const void *parent, const void *vdev)
{
    if (!pool_node_phase(parent))
        return;
    if (!pool_enter())
        return;
    pool_flush_requested_body(parent, vdev);
    pool_leave();
}
static void pool_phase_provided(unsigned token, int write, uint64_t count,
                                int error, size_t residual)
{
    if (!token)
        return;
    if (!pool_enter())
        return;
    pool_phase_provided_body(token, write, count, error, residual);
    pool_leave();
}
void aether_pool_root_end(unsigned token, int error)
{
    if (!token)
        return;
    if (!pool_enter())
        return;
    pool_root_end_body(token, error);
    pool_leave();
}
void aether_pool_sync_observe(const void *spa, uint64_t txg,
                              enum aether_pool_sync_stage stage, int error)
{
    if (!txg || atomic_load(&pool_record.txg) != txg)
        return;
    if (!pool_enter())
        return;
    pool_sync_observe_body(spa, txg, stage, error);
    pool_leave();
}
void aether_pool_txg_observe(const void *dp, uint64_t requested,
                             uint64_t synced, int error)
{
    if (!pool_observer ||
        atomic_load_explicit(&pool_transaction, memory_order_acquire) !=
            POOL_TX_BOUND)
        return;
    if (dp != pool_dp) {
        pool_problem();
        return;
    }
    uint64_t target = atomic_load(&pool_record.txg);
    if (!target || requested < target) {
        if (error)
            pool_problem();
        return; /* Old original waits cannot publish success for a new TXG. */
    }
    if (!pool_enter())
        return;
    target = atomic_load(&pool_record.txg);
    if (target && requested >= target) {
        if (error || synced < requested || atomic_load(&pool_record.step) != 7)
            pool_problem();
        else {
            atomic_store_explicit(&pool_record.synced, synced,
                                  memory_order_release);
            atomic_store_explicit(&pool_synced, synced, memory_order_release);
        }
    } else if (error)
        pool_problem();
    pool_leave();
}
/* Caller owns a consumed context and passes the original, unmodified outcome.
 * This is a trusted engine-owner boundary, not a client RPC or pointer API. */
int aether_pool_lifetime_retire(int operation_error, uint64_t target,
                                uint64_t staged, uint64_t state)
{
    if (operation_error || !target || staged != 4096 || state != 2) {
        pool_problem();
        return operation_error > 0 ? operation_error : EIO;
    }
    if (!pool_observer ||
        atomic_load_explicit(&pool_publication, memory_order_acquire) !=
            POOL_READY) {
        pool_problem();
        return ENODEV;
    }
    if (!pool_exclusive())
        return EBUSY;
    int error = 0;
    if (atomic_load(&pool_problems) || atomic_load(&pool_observer->problems))
        error = EIO;
    else if (atomic_load(&pool_record.txg) != target) {
        pool_problem();
        error = ESTALE;
    } else if (atomic_load(&pool_record.step) != 7 ||
               atomic_load(&pool_record.synced) < target)
        error = EBUSY;
    for (unsigned i = 0; !error && i < POOL_GRAPH_SLOTS; ++i)
        if (atomic_load_explicit(&pool_nodes[i].address, memory_order_acquire))
            error = EBUSY;
    for (unsigned i = 0; !error && i < AETHER_POOL_WITNESS_SLOTS; ++i)
        if (atomic_load_explicit(&pool_requests[i].request,
                                 memory_order_acquire) ||
            (atomic_load_explicit(&pool_observer->operations[i].state,
                                  memory_order_acquire) &
             3))
            error = EBUSY;
    if (!error && aether_pool_hooks_check(atomic_load(&pool_synced)))
        error = EIO;
    if (!error && atomic_load(&pool_completed) == UINT64_MAX) {
        atomic_fetch_or(&pool_problems, AETHER_POOL_OVERFLOW);
        error = EOVERFLOW;
    }
    if (!error) {
        atomic_store(&pool_retired_txg, target);
        atomic_fetch_add(&pool_completed, 1);
        pool_record_clear();
    }
    pool_release();
    return error;
}
unsigned aether_pool_hooks_check_ordered(void)
{
    if (!pool_exclusive())
        return AETHER_POOL_INCOMPLETE;
    unsigned bits = aether_pool_hooks_check(atomic_load(&pool_synced));
    if (!atomic_load(&pool_completed) ||
        atomic_load(&pool_completed) != atomic_load(&pool_epoch) ||
        atomic_load(&pool_record.txg))
        bits |= AETHER_POOL_INCOMPLETE;
    for (unsigned i = 0; i < POOL_GRAPH_SLOTS; ++i)
        if (atomic_load_explicit(&pool_nodes[i].address, memory_order_acquire))
            bits |= AETHER_POOL_INCOMPLETE;
    pool_release();
    return bits;
}
