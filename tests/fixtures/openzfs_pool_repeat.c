/* SPDX-License-Identifier: BSD-2-Clause */
/* Original graph/vdev/getter bodies, synthetic assignment and wait schedule. */
#define pool_phases (pool_repeat_records[0].phases)
#include "repeat-flow-base.inc"
#undef pool_phases

static unsigned repeat_mode;
static int repeat_phases(unsigned index, uint64_t txg)
{
    for (unsigned phase = 1; phase <= 7; ++phase) {
        zio_t *zio = root();
        unsigned token = aether_pool_root_begin(zio, &spa, txg, phase, 1);
        REQUIRE(token == index * 8 + phase);
        if (pool_phase_write(phase))
            zio_nowait(physical_write(zio, 512));
        else if (!(repeat_mode == 8 && index == 1 && phase == 5))
            zio_flush(zio, &leaf);
        run_queue_reverse();
        host_graph_done(zio);
        aether_pool_root_end(token, 0);
        static const unsigned stages[7] = {2, 0, 3, 4, 5, 0, 6};
        if (stages[phase - 1])
            aether_pool_sync_observe(&spa, txg, stages[phase - 1], 0);
    }
    return 0;
}

int main(int argc, char **argv)
{
    REQUIRE(argc == 2);
    repeat_mode = atoi(argv[1]);
    REQUIRE(repeat_mode <= 16);
    memset(bytes, 0x5b, sizeof(bytes));
    dsl_pool_t foreign_dp = {&foreign_spa};
    spa.spa_dsl_pool = &dp;
    REQUIRE(!aether_zfs_volume_bind(17));
    leaf = (vdev_t){.vdev_spa = &spa,
                    .vdev_path = AETHER_VOLUME_PATH,
                    .vdev_ashift = 9,
                    .vdev_psize = 8192,
                    .readable = 1};
    REQUIRE(!aether_pool_hooks_prepare(&witness));
    REQUIRE(!open_leaf(&leaf));
    REQUIRE(!aether_pool_hooks_bind_transaction(&selected_tx));
    REQUIRE(atomic_load(&pool_repeat_count) == 1);
    REQUIRE(atomic_load(&witness.target_txg) == 7);
    if (repeat_mode == 3 || repeat_mode == 4) {
        if (repeat_mode == 4)
            aether_pool_txg_observe(&dp, 7, 7, 0);
        selected_tx.tx_txg = 9;
        REQUIRE(aether_pool_hooks_bind_transaction(&selected_tx) != 0);
        REQUIRE(atomic_load(&pool_repeat_count) == 1);
        REQUIRE(aether_pool_hooks_check_ordered() != 0);
        vdev_file_close(&leaf);
        return 0;
    }
    if (repeat_mode == 16)
        mode =
            4; /* Original partial provider work must poison later admission. */
    REQUIRE(!repeat_phases(0, 7));
    if (repeat_mode != 15)
        aether_pool_txg_observe(&dp, 7, 7, 0);
    if (repeat_mode == 15 || repeat_mode == 16) {
        selected_tx.tx_txg = 9;
        REQUIRE(aether_pool_hooks_bind_transaction(&selected_tx) != 0);
        REQUIRE(atomic_load(&pool_repeat_count) == 1);
        REQUIRE(aether_pool_hooks_check_ordered() != 0);
        vdev_file_close(&leaf);
        return 0;
    }
    REQUIRE(atomic_load(&pool_repeat_records[0].step) == 7 &&
            atomic_load(&pool_repeat_records[0].synced) == 7);
    REQUIRE(aether_pool_hooks_check_ordered() == AETHER_POOL_INCOMPLETE);
    selected_tx.tx_txg = repeat_mode == 1 ? 7 : repeat_mode == 2 ? 6 : 9;
    if (repeat_mode == 6)
        selected_tx.tx_pool = &foreign_dp;
    if (repeat_mode == 14)
        vdev_file_close(&leaf);
    int joined = aether_pool_hooks_bind_transaction(&selected_tx);
    if (repeat_mode == 1 || repeat_mode == 2 || repeat_mode == 6 ||
        repeat_mode == 14) {
        REQUIRE(joined != 0 && atomic_load(&pool_repeat_count) == 1);
        REQUIRE(aether_pool_hooks_check_ordered() != 0);
        if (repeat_mode != 14)
            vdev_file_close(&leaf);
        return 0;
    }
    REQUIRE(!joined && atomic_load(&pool_repeat_count) == 2);
    REQUIRE(atomic_load(&witness.target_txg) == 7);
    REQUIRE(atomic_load(&pool_repeat_records[0].step) == 7 &&
            atomic_load(&pool_repeat_records[0].synced) == 7 &&
            !atomic_load(&pool_repeat_records[1].step) &&
            !atomic_load(&pool_repeat_records[1].synced));
    if (repeat_mode == 7) {
        zio_t *unselected = root();
        REQUIRE(!aether_pool_root_begin(unselected, &spa, 8, 1, 1));
        host_graph_done(unselected);
    }
    if (repeat_mode == 9) {
        aether_pool_root_end(7, 0); /* Late duplicate belongs to slot0 only. */
        REQUIRE(atomic_load(&pool_repeat_records[1].step) == 0);
    }
    if (repeat_mode == 13)
        aether_pool_root_end(17, 0); /* Unbound transaction token. */
    REQUIRE(!repeat_phases(1, 9));
    if (repeat_mode == 11)
        aether_pool_txg_observe(&dp, 7, 9,
                                0); /* Old target cannot satisfy slot1. */
    else if (repeat_mode != 10)
        aether_pool_txg_observe(&dp, 9, 9, 0);
    if (repeat_mode == 10 || repeat_mode == 11)
        REQUIRE(aether_pool_hooks_check_ordered() & AETHER_POOL_TXG_PENDING);
    else if (repeat_mode == 8 || repeat_mode == 9 || repeat_mode == 13)
        REQUIRE(aether_pool_hooks_check_ordered() & AETHER_POOL_BAD_EVENT);
    else
        REQUIRE(!aether_pool_hooks_check_ordered());
    if (repeat_mode == 5) {
        selected_tx.tx_txg = 11;
        REQUIRE(aether_pool_hooks_bind_transaction(&selected_tx) == ENOSPC);
        REQUIRE(atomic_load(&pool_repeat_count) == 2);
        REQUIRE(aether_pool_hooks_check_ordered() & AETHER_POOL_CAPACITY);
    }
    if (repeat_mode == 12) {
        zio_t *pending = root();
        pool_node_add(pending, 15);
        REQUIRE(aether_pool_hooks_check_ordered() & AETHER_POOL_INCOMPLETE);
        host_graph_done(pending);
        REQUIRE(!aether_pool_hooks_check_ordered());
    }
    if (repeat_mode == 8) {
        selected_tx.tx_txg = 11;
        REQUIRE(aether_pool_hooks_bind_transaction(&selected_tx) == EIO);
        REQUIRE(aether_pool_hooks_check_ordered() & AETHER_POOL_BAD_EVENT);
    }
    vdev_file_close(&leaf);
    if (!repeat_mode)
        printf("REPEAT two TXGs retained; witness budget=%zu\n",
               sizeof(pool_requests) + sizeof(witness) + sizeof(pool_nodes) +
                   sizeof(pool_repeat_records) + sizeof(pool_repeat_count) +
                   sizeof(pool_synced) + sizeof(pool_observer) +
                   sizeof(pool_spa) + sizeof(pool_dp) +
                   sizeof(pool_transaction) + sizeof(pool_publication) +
                   sizeof(pool_problems));
    return 0;
}
