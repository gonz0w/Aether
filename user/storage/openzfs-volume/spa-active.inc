/* SPDX-License-Identifier: BSD-2-Clause */
/* Private experiment appended to the original spa.c translation unit. Only
 * upstream activation/deactivation may mutate SPA state. The primary thread
 * owns the namespace and keeps the completion borrow through zio_wait. */
extern void aether_engine_utc_phase(unsigned char);
struct aether_root_completion {
    spa_t *spa;
    unsigned count;
    int invalid;
};
static void aether_root_done(zio_t *zio)
{
    struct aether_root_completion *record = zio->io_private;
    ++record->count;
    record->invalid = zio->io_spa != record->spa ||
                      zio->io_type != ZIO_TYPE_NULL || zio->io_error != 0;
}
int aether_spa_active_probe(int skip_activation, int skip_callback)
{
    spa_namespace_enter(FTAG);
    spa_t *spa = spa_add("aether_active_probe", NULL, NULL);
    if (!spa || spa->spa_state != POOL_STATE_UNINITIALIZED ||
        spa->spa_dsl_pool || spa->spa_root_vdev || spa->spa_sync_on)
        return 859;
    if (!skip_activation)
        spa_activate(spa, SPA_MODE_READ);
    if (spa->spa_state != POOL_STATE_ACTIVE)
        return 857;
    if (!spa->spa_normal_class || !spa->spa_log_class ||
        !spa->spa_embedded_log_class || !spa->spa_special_class ||
        !spa->spa_special_embedded_log_class || !spa->spa_dedup_class ||
        !spa->spa_zvol_taskq || !spa->spa_metaslab_taskq ||
        !spa->spa_prefetch_taskq || !spa->spa_upgrade_taskq)
        return 859;
    for (size_t i = 0; i < TXG_SIZE; ++i)
        if (!spa->spa_txg_zio[i])
            return 859;
    aether_engine_utc_phase('A');
    struct aether_root_completion record = {.spa = spa};
    zio_t *root = zio_root(spa, skip_callback ? NULL : aether_root_done,
                           &record, ZIO_FLAG_CANFAIL);
    if (!root || zio_wait(root) || record.invalid)
        return 859;
    /* zio_wait destroys the ZIO: never dereference root after this point. */
    if (record.count != 1)
        return 858;
    aether_engine_utc_phase('Z');
    spa_deactivate(spa);
    if (spa->spa_state != POOL_STATE_UNINITIALIZED || spa->spa_normal_class ||
        spa->spa_log_class || spa->spa_embedded_log_class ||
        spa->spa_special_class || spa->spa_special_embedded_log_class ||
        spa->spa_dedup_class || spa->spa_zvol_taskq ||
        spa->spa_metaslab_taskq || spa->spa_prefetch_taskq ||
        spa->spa_upgrade_taskq)
        return 859;
    for (int type = 0; type < ZIO_TYPES; ++type)
        for (int queue = 0; queue < ZIO_TASKQ_TYPES; ++queue)
            if (spa->spa_zio_taskq[type][queue].stqs_taskq)
                return 859;
    for (size_t i = 0; i < TXG_SIZE; ++i)
        if (spa->spa_txg_zio[i])
            return 859;
    spa_remove(spa);
    if (spa_lookup("aether_active_probe"))
        return 859;
    spa_namespace_exit(FTAG);
    aether_engine_utc_phase('D');
    return 0;
}
