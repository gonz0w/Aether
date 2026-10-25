/* SPDX-License-Identifier: BSD-2-Clause */
/* Included by private file-vdev observer after its owner state is declared.
 * Original child insertion holds original parent/child borrows/locks; readers
 * never dereference a stored address. Original destruction retires before free.
 * Root waits may precede destruction of already completed children. */
#include "pool-flow-witness.h"
#include "pool-sync-witness.h"
#define POOL_GRAPH_SLOTS 64
#define POOL_FLOW_ACTIVE 8
struct pool_node {
  _Atomic uintptr_t address; /* 0 free, 1 reserved, otherwise live address. */
  _Atomic unsigned phase;
};
struct pool_phase {
  _Atomic uint64_t requested_bytes, provided_bytes, requested_flushes,
      provided_flushes;
  _Atomic unsigned writes, required;
};
static struct pool_node pool_nodes[POOL_GRAPH_SLOTS];
static struct pool_phase pool_phases[7];
static _Atomic unsigned pool_step;
static _Atomic uint64_t pool_synced;

static void pool_flow_prepare(void) {
  for (unsigned i = 0; i < POOL_GRAPH_SLOTS; ++i) {
    atomic_init(&pool_nodes[i].address, 0);
    atomic_init(&pool_nodes[i].phase, 0);
  }
  for (unsigned i = 0; i < 7; ++i) {
    atomic_init(&pool_phases[i].requested_bytes, 0);
    atomic_init(&pool_phases[i].provided_bytes, 0);
    atomic_init(&pool_phases[i].requested_flushes, 0);
    atomic_init(&pool_phases[i].provided_flushes, 0);
    atomic_init(&pool_phases[i].writes, 0);
    atomic_init(&pool_phases[i].required, 0);
  }
  atomic_init(&pool_step, 0);
  atomic_init(&pool_synced, 0);
}

static unsigned pool_node_phase(const void *identity) {
  uintptr_t address = (uintptr_t)identity;
  if (address <= 1)
    return 0;
  for (unsigned i = 0; i < POOL_GRAPH_SLOTS; ++i) {
    if (atomic_load_explicit(&pool_nodes[i].address, memory_order_acquire) ==
        address)
      return atomic_load_explicit(&pool_nodes[i].phase, memory_order_relaxed);
  }
  return 0;
}

static void pool_node_add(const void *identity, unsigned phase) {
  uintptr_t address = (uintptr_t)identity;
  if (address <= 1 || !phase || phase > 7) {
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
    atomic_store_explicit(&pool_nodes[i].phase, phase, memory_order_relaxed);
    atomic_store_explicit(&pool_nodes[i].address, address,
                          memory_order_release);
    return;
  }
  atomic_fetch_or_explicit(&pool_problems, AETHER_POOL_CAPACITY,
                           memory_order_relaxed);
}

unsigned aether_pool_root_begin(const void *identity, const void *spa,
                                uint64_t txg, unsigned phase, int required) {
  if (!pool_observer ||
      atomic_load_explicit(&pool_transaction, memory_order_acquire) !=
          POOL_TX_BOUND)
    return 0; /* Earlier constructor/create TXGs cannot qualify target. */
  if (txg !=
      atomic_load_explicit(&pool_observer->target_txg, memory_order_acquire))
    return 0; /* Other original TXGs have independent work. */
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
          &pool_step, &previous, phase + POOL_FLOW_ACTIVE, memory_order_acquire,
          memory_order_relaxed)) {
    pool_problem(); /* Overlap, omission, retry or reordered phase. */
    return 0;
  }
  atomic_store(&pool_phases[phase - 1].required, !!required);
  pool_node_add(root, phase);
  return phase;
}

void aether_pool_zio_child(const void *parent, const void *child) {
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

void aether_pool_zio_retire(const void *identity) {
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

static void pool_add_count(_Atomic uint64_t *counter, uint64_t value) {
  uint64_t old =
      atomic_fetch_add_explicit(counter, value, memory_order_relaxed);
  if (value > UINT64_MAX - old)
    atomic_fetch_or_explicit(&pool_problems, AETHER_POOL_OVERFLOW,
                             memory_order_relaxed);
}

static int pool_phase_write(unsigned phase) {
  return phase == AETHER_POOL_EVEN_WRITE_ROOT ||
         phase == AETHER_POOL_UB_WRITE_ROOT ||
         phase == AETHER_POOL_ODD_WRITE_ROOT;
}

static struct pool_phase *pool_active_phase(unsigned phase, int write) {
  if (!phase)
    return NULL;
  if (phase > 7 || pool_phase_write(phase) != !!write ||
      atomic_load_explicit(&pool_step, memory_order_acquire) !=
          phase + POOL_FLOW_ACTIVE) {
    pool_problem();
    return NULL;
  }
  return &pool_phases[phase - 1];
}

void aether_pool_write_requested(const void *parent, const void *identity) {
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

void aether_pool_flush_requested(const void *parent, const void *vdev) {
  if (!pool_observer || vdev != pool_observer->leaf)
    return; /* Original recursion reaches the selected concrete leaf. */
  struct pool_phase *phase = pool_active_phase(pool_node_phase(parent), 0);
  if (phase)
    pool_add_count(&phase->requested_flushes, 1);
}

static void pool_phase_provided(unsigned token, int write, uint64_t count,
                                int error, size_t residual) {
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

void aether_pool_root_end(unsigned token, int error) {
  if (!token)
    return;
  if (token > 7) {
    pool_problem();
    return;
  }
  struct pool_phase *phase = &pool_phases[token - 1];
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
  unsigned active = token + POOL_FLOW_ACTIVE;
  if (!atomic_compare_exchange_strong_explicit(&pool_step, &active, token,
                                               memory_order_release,
                                               memory_order_relaxed))
    pool_problem();
}

void aether_pool_sync_observe(const void *spa, uint64_t txg,
                              enum aether_pool_sync_stage stage, int error) {
  if (!pool_observer ||
      atomic_load_explicit(&pool_transaction, memory_order_acquire) !=
          POOL_TX_BOUND ||
      txg != atomic_load(&pool_observer->target_txg))
    return;
  /* Retain existing original-boundary diagnostics without another stage
   * ledger. Only actual roots/requests/provider completions qualify ordering.
   */
  const unsigned completed[] = {0, 0, 1, 3, 4, 5, 7};
  if (spa != pool_spa || stage < 1 || stage > 6 || error ||
      atomic_load(&pool_step) != completed[stage])
    pool_problem();
}

void aether_pool_txg_observe(const void *dp, uint64_t requested,
                             uint64_t synced, int error) {
  if (!pool_observer ||
      atomic_load_explicit(&pool_transaction, memory_order_acquire) !=
          POOL_TX_BOUND)
    return;
  uint64_t target = atomic_load(&pool_observer->target_txg);
  if (dp != pool_dp) {
    pool_problem();
    return;
  }
  if (requested < target)
    return; /* An earlier original wait cannot satisfy selected target. */
  if (error || synced < requested || atomic_load(&pool_step) != 7) {
    pool_problem();
    return;
  }
  /* Existing original tx_sync_lock serializes these calls for this dp. */
  atomic_store_explicit(&pool_synced, synced, memory_order_release);
}

unsigned aether_pool_hooks_check_ordered(void) {
  unsigned bits = aether_pool_hooks_check(
      atomic_load_explicit(&pool_synced, memory_order_acquire));
  if (atomic_load_explicit(&pool_step, memory_order_acquire) != 7)
    bits |= AETHER_POOL_INCOMPLETE;
  for (unsigned i = 0; i < POOL_GRAPH_SLOTS; ++i)
    if (atomic_load_explicit(&pool_nodes[i].address, memory_order_acquire))
      bits |= AETHER_POOL_INCOMPLETE;
  return bits;
}
