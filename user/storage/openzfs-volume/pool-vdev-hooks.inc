/* SPDX-License-Identifier: BSD-2-Clause */
/* Private observer for pinned file-vdev bodies, not native-selected yet.
 * Prepare before workers. Original successful open initializes/publishes actual
 * identities once; close retires them permanently. No reset or quiescence
 * claim. Inspect/dispose only after actual drain and no
 * admissions/publications. Token borrows finish before original interrupt may
 * release their ZIO. */
#include "pool-witness.h"
/* This pointer and request table are prepared before any helper starts. */
static struct aether_pool_witness *pool_observer;
static spa_t *pool_spa;
static dsl_pool_t *pool_dp;
enum { POOL_TX_UNBOUND, POOL_TX_BINDING, POOL_TX_BOUND };
static _Atomic unsigned pool_transaction;
enum { POOL_UNBOUND, POOL_PUBLISHING, POOL_READY, POOL_CLOSED };
static _Atomic unsigned pool_publication, pool_problems;
struct pool_request {
  _Atomic(zio_t *) request;
  uint64_t generation;
};
static struct pool_request pool_requests[AETHER_POOL_WITNESS_SLOTS];
static void pool_problem(void) {
  atomic_fetch_or_explicit(&pool_problems, AETHER_POOL_BAD_EVENT,
                           memory_order_relaxed);
}

struct pool_observation {
  struct aether_pool_token token;
  int active;
  unsigned phase;
  uint64_t count;
  int write;
};

#include "pool-flow.inc"
_Static_assert(sizeof(pool_requests) + sizeof(struct aether_pool_witness) +
                       sizeof(pool_observer) + sizeof(pool_spa) +
                       sizeof(pool_dp) + sizeof(pool_transaction) +
                       sizeof(pool_nodes) + sizeof(pool_phases) +
                       sizeof(pool_step) + sizeof(pool_synced) +
                       sizeof(pool_publication) + sizeof(pool_problems) <=
                   8192,
               "private pool observations exceed their budget");
_Static_assert(ATOMIC_POINTER_LOCK_FREE == 2,
               "pool request associations require lock-free pointers");

int aether_pool_hooks_prepare(struct aether_pool_witness *witness) {
  if (!witness)
    return EINVAL;
  if (pool_observer)
    return EALREADY;
  for (unsigned i = 0; i < AETHER_POOL_WITNESS_SLOTS; ++i)
    atomic_init(&pool_requests[i].request, NULL);
  atomic_init(&pool_publication, POOL_UNBOUND);
  atomic_init(&pool_problems, 0);
  atomic_init(&pool_transaction, POOL_TX_UNBOUND);
  pool_flow_prepare();
  pool_observer = witness;
  return 0;
}

static void aether_pool_hook_open(vdev_t *vd) {
  if (!pool_observer)
    return;
  vdev_file_t *vf = vd->vdev_tsd;
  if (!vd->vdev_spa || !vf || !vf->vf_file) {
    pool_problem();
    return;
  }
  unsigned phase =
      atomic_load_explicit(&pool_publication, memory_order_acquire);
  if (phase == POOL_READY && vd->vdev_reopening && vd->vdev_spa == pool_spa &&
      vd == pool_observer->leaf && vf->vf_file == pool_observer->file)
    return;
  unsigned unbound = POOL_UNBOUND;
  if (!atomic_compare_exchange_strong_explicit(
          &pool_publication, &unbound, POOL_PUBLISHING, memory_order_acquire,
          memory_order_relaxed)) {
    pool_problem();
    return;
  }
  pool_spa = vd->vdev_spa;
  aether_pool_witness_init(pool_observer, vd, vf->vf_file, 0);
  atomic_store_explicit(&pool_publication, POOL_READY, memory_order_release);
}

static void aether_pool_hook_close(vdev_t *vd) {
  if (!pool_observer)
    return;
  unsigned phase =
      atomic_load_explicit(&pool_publication, memory_order_acquire);
  if (phase == POOL_UNBOUND)
    return; /* Failed original open never published an identity. */
  if (phase != POOL_READY) {
    pool_problem();
    return;
  }
  vdev_file_t *vf = vd->vdev_tsd;
  if (vd != pool_observer->leaf || vd->vdev_spa != pool_spa || !vf ||
      vf->vf_file != pool_observer->file) {
    pool_problem();
    return;
  }
  atomic_store_explicit(&pool_publication, POOL_CLOSED, memory_order_release);
}

/* Trusted experiment caller holds live assigned transaction and pool borrows;
 * no concurrent commit/export/close. No transaction pointer escapes this call.
 * Actual I/O helpers may overlap it; no join overlaps final inspection. */
int aether_pool_hooks_bind_transaction(dmu_tx_t *tx) {
  if (!pool_observer ||
      atomic_load_explicit(&pool_publication, memory_order_acquire) !=
          POOL_READY) {
    pool_problem();
    return ENODEV;
  }
  /* Guard original getter assertions; this is not pointer validation. */
  if (!tx || !tx->tx_pool || !tx->tx_txg || tx->tx_anyobj) {
    pool_problem();
    return EINVAL;
  }
  dsl_pool_t *dp = dmu_tx_pool(tx);
  if (dp->dp_spa != pool_spa || spa_get_dsl(pool_spa) != dp) {
    pool_problem();
    return EXDEV;
  }
  unsigned unbound = POOL_TX_UNBOUND;
  if (!atomic_compare_exchange_strong_explicit(
          &pool_transaction, &unbound, POOL_TX_BINDING, memory_order_acquire,
          memory_order_relaxed)) {
    pool_problem();
    return EALREADY;
  }
  int error = aether_pool_witness_bind_txg(pool_observer, dmu_tx_get_txg(tx));
  if (error) {
    pool_problem();
    return error; /* BINDING remains incomplete, never reset/retry. */
  }
  pool_dp = dp;
  atomic_store_explicit(&pool_transaction, POOL_TX_BOUND, memory_order_release);
  return 0;
}

unsigned aether_pool_hooks_check(uint64_t synced_txg) {
  unsigned phase =
      atomic_load_explicit(&pool_publication, memory_order_acquire);
  unsigned bits = !pool_observer || phase < POOL_READY
                      ? AETHER_POOL_INCOMPLETE
                      : aether_pool_witness_check(pool_observer, synced_txg);
  if (atomic_load_explicit(&pool_transaction, memory_order_acquire) !=
          POOL_TX_BOUND &&
      pool_observer && phase >= POOL_READY)
    bits |= AETHER_POOL_TXG_PENDING;
  return bits | atomic_load_explicit(&pool_problems, memory_order_acquire);
}

static int pool_observed(zio_t *zio) {
  return pool_observer &&
         (zio->io_type == ZIO_TYPE_WRITE || zio->io_type == ZIO_TYPE_FLUSH);
}

static void aether_pool_hook_admit(zio_t *zio) {
  if (!pool_observed(zio))
    return;
  if (atomic_load_explicit(&pool_publication, memory_order_acquire) !=
          POOL_READY ||
      zio->io_spa != pool_spa || zio->io_vd != pool_observer->leaf) {
    pool_problem();
    return;
  }
  enum aether_pool_io_kind kind =
      zio->io_type == ZIO_TYPE_WRITE ? AETHER_POOL_WRITE : AETHER_POOL_FLUSH;
  struct aether_pool_token token =
      aether_pool_io_begin(pool_observer, kind, zio->io_txg,
                           kind == AETHER_POOL_WRITE ? zio->io_size : 0);
  if (!token.generation)
    return;
  struct pool_request *record = &pool_requests[token.slot];
  /* The ledger holds OPEN until completion, preventing a second admission
   * to this index while the token is written or consumed by the callback. */
  record->generation = token.generation;
  atomic_store_explicit(&record->request, zio, memory_order_release);
}

static struct pool_observation aether_pool_hook_take(zio_t *zio) {
  if (!pool_observed(zio))
    return (struct pool_observation){0};
  if (atomic_load_explicit(&pool_publication, memory_order_acquire) <
      POOL_READY) {
    pool_problem();
    return (struct pool_observation){0};
  }
  for (unsigned i = 0; i < AETHER_POOL_WITNESS_SLOTS; ++i) {
    zio_t *expected = zio;
    if (atomic_compare_exchange_strong_explicit(
            &pool_requests[i].request, &expected, NULL, memory_order_acquire,
            memory_order_relaxed))
      return (struct pool_observation){
          .token = {i, pool_requests[i].generation},
          .active = 1,
          .phase = pool_node_phase(zio),
          .count = zio->io_size,
          .write = zio->io_type == ZIO_TYPE_WRITE};
  }
  pool_problem();
  return (struct pool_observation){0};
}

static void aether_pool_hook_provider(struct pool_observation *observation,
                                      zfs_file_t *file, int error,
                                      ssize_t residual) {
  if (observation->active)
    pool_phase_provided(observation->phase, observation->write,
                        observation->count, error, (size_t)residual);
  if (observation->active)
    aether_pool_provider_done(pool_observer, observation->token, file, error,
                              (size_t)residual);
}

static void aether_pool_hook_finish(struct pool_observation *observation,
                                    zio_t *zio) {
  if (!observation->active)
    return;
  aether_pool_leaf_done(pool_observer, observation->token, zio->io_vd,
                        zio->io_type == ZIO_TYPE_WRITE ? AETHER_POOL_WRITE
                                                       : AETHER_POOL_FLUSH,
                        zio->io_txg, zio->io_error);
  observation->active = 0;
}

static void aether_pool_hook_direct(zio_t *zio) {
  struct pool_observation observation = aether_pool_hook_take(zio);
  aether_pool_hook_finish(&observation, zio);
}
