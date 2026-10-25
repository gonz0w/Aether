/* SPDX-License-Identifier: BSD-2-Clause */
/* Original graph/vdev/wait bodies; fixed eight-record synthetic schedule. */
#include "eight-flow-base.inc"

int main(int argc, char **argv)
{
    REQUIRE(argc == 2);
    unsigned scenario = atoi(argv[1]);
    REQUIRE(scenario <= 38);
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
    size_t budget = sizeof(pool_requests) + sizeof(witness) +
                    sizeof(pool_nodes) + sizeof(pool_repeat_records) +
                    sizeof(pool_repeat_count) + sizeof(pool_synced) +
                    sizeof(pool_observer) + sizeof(pool_spa) + sizeof(pool_dp) +
                    sizeof(pool_transaction) + sizeof(pool_publication) +
                    sizeof(pool_problems);
    REQUIRE(budget == 9704 && budget <= 10240);
    for (unsigned n = 0; n < 8; ++n) {
        uint64_t target = 7 + n * 2;
        selected_tx.tx_txg = target;
        REQUIRE(!aether_pool_hooks_bind_transaction(&selected_tx));
        REQUIRE(atomic_load(&pool_repeat_count) == n + 1);
        REQUIRE(atomic_load(&witness.target_txg) == 7);
        for (unsigned old = 0; old < n; ++old) {
            REQUIRE(atomic_load(&pool_repeat_records[old].txg) == 7 + old * 2);
            REQUIRE(atomic_load(&pool_repeat_records[old].step) == 7);
            REQUIRE(atomic_load(&pool_repeat_records[old].synced) >=
                    7 + old * 2);
        }
        if (scenario >= 9 && scenario <= 16 && n == scenario - 9) {
            selected_tx.tx_txg += 2;
            REQUIRE(aether_pool_hooks_bind_transaction(&selected_tx) != 0);
            REQUIRE(atomic_load(&pool_repeat_count) == n + 1);
            REQUIRE(aether_pool_hooks_check_ordered() != 0);
            vdev_file_close(&leaf);
            return 0;
        }
        if (scenario == 35 && n == 7)
            mode = 4; /* Original provider partial error poisons admission. */
        REQUIRE(!repeat_phases(n, target));
        if ((scenario >= 1 && scenario <= 8 && n == scenario - 1) ||
            (scenario == 34 && n == 7)) {
            if (scenario == 34)
                aether_pool_txg_observe(&dp, 7, 900, 0);
            REQUIRE(aether_pool_hooks_check_ordered() &
                    AETHER_POOL_TXG_PENDING);
            if (n < 7) {
                selected_tx.tx_txg += 2;
                REQUIRE(aether_pool_hooks_bind_transaction(&selected_tx) != 0);
                REQUIRE(atomic_load(&pool_repeat_count) == n + 1);
            }
            vdev_file_close(&leaf);
            return 0;
        }
        aether_pool_txg_observe(&dp, target, target, 0);
        if ((scenario >= 17 && scenario <= 24 && n == scenario - 17) ||
            (scenario >= 25 && scenario <= 32 && n == scenario - 25)) {
            dsl_pool_t foreign_dp = {&foreign_spa};
            if (scenario >= 25) {
                selected_tx.tx_pool = &foreign_dp;
                selected_tx.tx_txg += 2;
            }
            REQUIRE(aether_pool_hooks_bind_transaction(&selected_tx) != 0);
            REQUIRE(atomic_load(&pool_repeat_count) == n + 1);
            REQUIRE(aether_pool_hooks_check_ordered() != 0);
            vdev_file_close(&leaf);
            return 0;
        }
        if (scenario == 36 && n == 3) {
            vdev_file_close(&leaf);
            selected_tx.tx_txg += 2;
            REQUIRE(aether_pool_hooks_bind_transaction(&selected_tx) != 0);
            REQUIRE(atomic_load(&pool_repeat_count) == 4);
            return 0;
        }
        if (scenario == 35 && n == 7) {
            REQUIRE(aether_pool_hooks_check_ordered() & AETHER_POOL_BAD_EVENT);
            selected_tx.tx_txg += 2;
            REQUIRE(aether_pool_hooks_bind_transaction(&selected_tx) == EIO);
            vdev_file_close(&leaf);
            return 0;
        }
        REQUIRE(aether_pool_hooks_check_ordered() ==
                (n < 7 ? AETHER_POOL_INCOMPLETE : 0));
    }
    if (scenario == 33) {
        aether_pool_root_end(7, 0); /* Late slot0 token cannot relabel slot7. */
        REQUIRE(atomic_load(&pool_repeat_records[7].step) == 7);
        REQUIRE(aether_pool_hooks_check_ordered() & AETHER_POOL_BAD_EVENT);
    } else {
        if (scenario == 37) {
            zio_t *unselected = root();
            REQUIRE(!aether_pool_root_begin(unselected, &spa, 8, 1, 1));
            host_graph_done(unselected);
        }
        if (scenario == 38) {
            zio_t *pending = root();
            pool_node_add(pending, 63);
            REQUIRE(aether_pool_hooks_check_ordered() & AETHER_POOL_INCOMPLETE);
            host_graph_done(pending);
        }
        REQUIRE(!aether_pool_hooks_check_ordered());
        selected_tx.tx_txg = 23;
        REQUIRE(aether_pool_hooks_bind_transaction(&selected_tx) == ENOSPC);
        REQUIRE(atomic_load(&pool_repeat_count) == 8);
        REQUIRE(aether_pool_hooks_check_ordered() & AETHER_POOL_CAPACITY);
        REQUIRE(aether_pool_hooks_bind_transaction(&selected_tx) == EIO);
        REQUIRE(atomic_load(&pool_repeat_count) == 8);
    }
    vdev_file_close(&leaf);
    return 0;
}
