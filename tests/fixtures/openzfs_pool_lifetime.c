/* SPDX-License-Identifier: BSD-2-Clause */
/* Original graph/provider bodies, synthetic TXGs and controlled borrows. */
#include "lifetime-flow-base.inc"
static pthread_mutex_t pin_mutex = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t pin_cond = PTHREAD_COND_INITIALIZER;
static int pinned, released;
static void *hold_pin(void *unused)
{
    (void)unused;
    ASSERT(pool_enter());
    ASSERT(!pthread_mutex_lock(&pin_mutex));
    pinned = 1;
    ASSERT(!pthread_cond_signal(&pin_cond));
    while (!released)
        ASSERT(!pthread_cond_wait(&pin_cond, &pin_mutex));
    ASSERT(!pthread_mutex_unlock(&pin_mutex));
    pool_leave();
    return NULL;
}
int main(int argc, char **argv)
{
    REQUIRE(argc == 2);
    unsigned scenario = atoi(argv[1]);
    REQUIRE(scenario <= 75);
    memset(bytes, 0x5b, sizeof(bytes));
    spa.spa_dsl_pool = &dp;
    REQUIRE(!aether_zfs_volume_bind(17));
    leaf = (vdev_t){.vdev_spa = &spa,
                    .vdev_path = AETHER_VOLUME_PATH,
                    .vdev_ashift = 9,
                    .vdev_psize = 8192,
                    .readable = 1};
    REQUIRE(!aether_pool_hooks_prepare(&witness));
    REQUIRE(!open_leaf(&leaf));
    size_t budget =
        sizeof(pool_requests) + sizeof(witness) + sizeof(pool_nodes) +
        sizeof(pool_record) + sizeof(pool_epoch) + sizeof(pool_gate) +
        sizeof(pool_retired_txg) + sizeof(pool_completed) +
        sizeof(pool_synced) + sizeof(pool_observer) + sizeof(pool_spa) +
        sizeof(pool_dp) + sizeof(pool_transaction) + sizeof(pool_publication) +
        sizeof(pool_problems);
    REQUIRE(budget <= 8192);
    unsigned loops = scenario == 75 ? 64 : 8;
    for (unsigned n = 0; n < loops; ++n) {
        uint64_t target = 7 + 2 * n;
        selected_tx.tx_txg = target;
        REQUIRE(!aether_pool_hooks_bind_transaction(&selected_tx));
        REQUIRE(atomic_load(&pool_epoch) == n + 1 &&
                atomic_load(&pool_completed) == n);
        REQUIRE(atomic_load(&witness.target_txg) == 7);
        REQUIRE(atomic_load(&pool_record.txg) == target &&
                !atomic_load(&pool_record.step));
        if (scenario == 57 && n == 1) {
            zio_t *current = root();
            REQUIRE(aether_pool_root_begin(current, &spa, target, 1, 1) == 17);
            zio_nowait(physical_write(current, 512));
            run_queue_reverse();
            host_graph_done(current);
            aether_pool_root_end(9, 0); /* Same local phase, different epoch. */
            REQUIRE(atomic_load(&pool_record.step) == 9 &&
                    atomic_load(&pool_problems));
            vdev_file_close(&leaf);
            return 0;
        }
        if (scenario == 58 && n == 1) {
            pool_phase_provided(9, 1, 512, 0, 0);
            REQUIRE(!atomic_load(&pool_record.phases[0].provided_bytes) &&
                    atomic_load(&pool_problems));
            vdev_file_close(&leaf);
            return 0;
        }
        if (scenario == 70) {
            REQUIRE(aether_pool_lifetime_retire(0, target, 4096, 2) == EBUSY);
            REQUIRE(atomic_load(&pool_record.txg) == target &&
                    !atomic_load(&pool_completed));
            vdev_file_close(&leaf);
            return 0;
        }
        if (scenario == 73)
            mode = 4;
        REQUIRE(!repeat_phases(n + 1, target));
        if (scenario >= 9 && scenario <= 16 && n == scenario - 9) {
            REQUIRE(aether_pool_lifetime_retire(0, target, 4096, 2) == EBUSY);
            REQUIRE(atomic_load(&pool_record.txg) == target &&
                    atomic_load(&pool_completed) == n);
        }
        if (scenario == 59 && n == 1) {
            aether_pool_txg_observe(&dp, 7, 900, 0);
            REQUIRE(!atomic_load(&pool_record.synced));
        }
        aether_pool_txg_observe(&dp, target, target, 0);
        if (scenario == 60) {
            selected_tx.tx_txg += 2;
            REQUIRE(aether_pool_hooks_bind_transaction(&selected_tx) != 0);
            REQUIRE(atomic_load(&pool_record.txg) == target &&
                    !atomic_load(&pool_completed));
            vdev_file_close(&leaf);
            return 0;
        }
        if (scenario >= 1 && scenario <= 8 && n == scenario - 1) {
            REQUIRE(pool_enter());
            REQUIRE(aether_pool_lifetime_retire(0, target, 4096, 2) == EBUSY);
            REQUIRE(atomic_load(&pool_record.txg) == target &&
                    atomic_load(&pool_completed) == n);
            pool_leave();
        }
        if (scenario >= 17 && scenario <= 24 && n == scenario - 17) {
            zio_t *pending = root();
            pool_node_add(pending, (n + 1) * 8 + 7);
            REQUIRE(aether_pool_lifetime_retire(0, target, 4096, 2) == EBUSY);
            REQUIRE(atomic_load(&pool_record.txg) == target &&
                    atomic_load(&pool_completed) == n);
            host_graph_done(pending);
        }
        if (scenario >= 25 && scenario <= 32 && n == scenario - 25) {
            atomic_store(&witness.operations[127].state, (42u << 2) | 2);
            REQUIRE(aether_pool_lifetime_retire(0, target, 4096, 2) == EBUSY);
            REQUIRE(atomic_load(&witness.operations[127].state) ==
                    ((42u << 2) | 2));
            atomic_store(&witness.operations[127].state, 42u << 2);
        }
        if (scenario >= 33 && scenario <= 40 && n == scenario - 33) {
            atomic_store(&pool_requests[127].request, (zio_t *)123);
            REQUIRE(aether_pool_lifetime_retire(0, target, 4096, 2) == EBUSY);
            REQUIRE(atomic_load(&pool_requests[127].request) == (zio_t *)123);
            atomic_store(&pool_requests[127].request, NULL);
        }
        if ((scenario >= 41 && scenario <= 56 && n == (scenario - 41) % 8) ||
            scenario == 69 || scenario == 73 || scenario == 74) {
            int error = scenario <= 48 || scenario == 73 ? EIO
                        : scenario == 74                 ? -1
                                                         : 0;
            int got = aether_pool_lifetime_retire(
                error, target + (scenario == 69),
                scenario >= 49 && scenario <= 56 ? 4095 : 4096, 2);
            REQUIRE(got != 0 && atomic_load(&pool_record.txg) == target &&
                    atomic_load(&pool_completed) == n);
            selected_tx.tx_txg += 2;
            REQUIRE(aether_pool_hooks_bind_transaction(&selected_tx) == EIO);
            vdev_file_close(&leaf);
            return 0;
        }
        if (scenario == 65) {
            atomic_store(&pool_completed, UINT64_MAX);
            REQUIRE(aether_pool_lifetime_retire(0, target, 4096, 2) ==
                    EOVERFLOW);
            REQUIRE(atomic_load(&pool_record.txg) == target &&
                    atomic_load(&pool_completed) == UINT64_MAX);
            vdev_file_close(&leaf);
            return 0;
        }
        if (scenario == 66) {
            atomic_store(&pool_gate, UINT_MAX - 1);
            REQUIRE(!pool_enter() &&
                    (atomic_load(&pool_problems) & AETHER_POOL_OVERFLOW));
            REQUIRE(atomic_load(&pool_gate) == UINT_MAX - 1);
            vdev_file_close(&leaf);
            return 0;
        }
        if (scenario == 67 && !n) {
            pthread_t thread;
            REQUIRE(!pthread_create(&thread, NULL, hold_pin, NULL));
            REQUIRE(!pthread_mutex_lock(&pin_mutex));
            while (!pinned)
                REQUIRE(!pthread_cond_wait(&pin_cond, &pin_mutex));
            REQUIRE(aether_pool_lifetime_retire(0, target, 4096, 2) == EBUSY);
            REQUIRE(atomic_load(&pool_record.txg) == target &&
                    !atomic_load(&pool_completed));
            released = 1;
            REQUIRE(!pthread_cond_signal(&pin_cond));
            REQUIRE(!pthread_mutex_unlock(&pin_mutex));
            REQUIRE(!pthread_join(thread, NULL));
        }
        if (scenario == 68) {
            atomic_store(&pool_record.step, 9);
            REQUIRE(pool_exclusive());
            aether_pool_root_end(9, 0);
            REQUIRE(atomic_load(&pool_record.txg) == target &&
                    atomic_load(&pool_record.step) == 9 &&
                    atomic_load(&pool_problems));
            pool_release();
            vdev_file_close(&leaf);
            return 0;
        }
        REQUIRE(aether_pool_hooks_check_ordered() & AETHER_POOL_INCOMPLETE);
        REQUIRE(!aether_pool_lifetime_retire(0, target, 4096, 2));
        REQUIRE(!atomic_load(&pool_record.txg) &&
                !atomic_load(&pool_record.step));
        REQUIRE(atomic_load(&pool_retired_txg) == target &&
                atomic_load(&pool_completed) == n + 1 &&
                atomic_load(&pool_epoch) == n + 1);
        REQUIRE(!aether_pool_hooks_check_ordered());
        if (scenario == 71) {
            REQUIRE(aether_pool_lifetime_retire(0, target, 4096, 2) == ESTALE);
            REQUIRE(atomic_load(&pool_completed) == 1 &&
                    atomic_load(&pool_retired_txg) == 7);
            vdev_file_close(&leaf);
            return 0;
        }
        if (scenario >= 61 && scenario <= 64) {
            selected_tx.tx_txg = target + 2;
            dsl_pool_t foreign_dp = {&foreign_spa};
            if (scenario == 61)
                selected_tx.tx_txg = target;
            if (scenario == 62)
                selected_tx.tx_pool = &foreign_dp;
            if (scenario == 63)
                vdev_file_close(&leaf);
            if (scenario == 64) {
                atomic_store(&pool_epoch, UINT_MAX / 8);
                atomic_store(&pool_completed, UINT_MAX / 8);
            }
            REQUIRE(aether_pool_hooks_bind_transaction(&selected_tx) != 0);
            REQUIRE(!atomic_load(&pool_record.txg) &&
                    atomic_load(&pool_retired_txg) == target);
            if (scenario != 63)
                vdev_file_close(&leaf);
            return 0;
        }
    }
    REQUIRE(atomic_load(&pool_completed) == loops);
    if (!scenario)
        printf("LIFETIME observer bytes=%zu records=1 completed=%u\n", budget,
               loops);
    vdev_file_close(&leaf);
    return 0;
}
