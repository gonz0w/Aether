/* SPDX-License-Identifier: BSD-2-Clause */
/* Appended to actual spa.c; upstream functions own every SPA/vdev transition.
 * Namespace and configuration ownership live through all actual ZIO waits.
 * The synchronous linear ABD borrows stack bytes through completion only. */
#include <sys/vdev_impl.h>
#include <sys/abd.h>
#include <sys/zfs_file.h>
#include <sys/auxv.h>
#include "volume.h"
extern int aether_volume_finish_probe(void);
struct aether_physical_completion {
    spa_t *spa;
    vdev_t *vdev;
    abd_t *abd;
    unsigned count;
    int error;
    int invalid;
};
static void aether_physical_done(zio_t *zio)
{
    struct aether_physical_completion *record = zio->io_private;
    ++record->count;
    record->error = zio->io_error;
    record->invalid =
        zio->io_spa != record->spa || zio->io_vd != record->vdev ||
        zio->io_abd != record->abd || zio->io_type != ZIO_TYPE_READ ||
        zio->io_size != 512 || zio->io_offset != 1048576;
    aether_engine_utc_phase('K');
}
#ifdef AETHER_PHYSICAL_WRITE
#include "spa-write.inc"
#endif
int aether_spa_physical_probe(int small, int completion_mode, int revoked)
{
    if (getauxval(0xa001) != 0x50000101UL) {
        zfs_file_t *file = NULL;
        if (zfs_file_open(AETHER_VOLUME_PATH, O_RDONLY, 0, NULL, &file) !=
                ENODEV ||
            file)
            return 863;
        aether_engine_utc_phase('N');
        return 0;
    }
    spa_namespace_enter(FTAG);
    spa_t *spa = spa_add("aether_physical_probe", NULL, NULL);
    if (!spa || spa->spa_state != POOL_STATE_UNINITIALIZED)
        return 863;
#ifdef AETHER_PHYSICAL_WRITE
    spa_activate(spa,
                 SPA_MODE_READ | (completion_mode == 1 ? 0 : SPA_MODE_WRITE));
#else
    spa_activate(spa, SPA_MODE_READ);
#endif
    if (spa->spa_state != POOL_STATE_ACTIVE || spa->spa_dsl_pool ||
        spa->spa_sync_on)
        return 863;
    aether_engine_utc_phase('A');
    spa_config_enter(spa, SCL_ALL, FTAG, RW_WRITER);
    nvlist_t *config = NULL;
    vdev_t *root = NULL, *leaf = NULL;
    if (nvlist_alloc(&config, NV_UNIQUE_NAME, KM_SLEEP) ||
        nvlist_add_string(config, ZPOOL_CONFIG_TYPE, VDEV_TYPE_ROOT) ||
        vdev_alloc(spa, &root, config, NULL, 0, VDEV_ALLOC_ADD))
        return 863;
    nvlist_free(config);
    config = NULL;
    if (nvlist_alloc(&config, NV_UNIQUE_NAME, KM_SLEEP) ||
        nvlist_add_string(config, ZPOOL_CONFIG_TYPE, VDEV_TYPE_FILE) ||
        nvlist_add_string(config, ZPOOL_CONFIG_PATH, AETHER_VOLUME_PATH) ||
        vdev_alloc(spa, &leaf, config, root, 0, VDEV_ALLOC_ADD))
        return 863;
    nvlist_free(config);
    aether_engine_utc_phase('C');
    int opened = vdev_open(root, NULL);
    if (small) {
        if (!opened || leaf->vdev_open_error != EOVERFLOW ||
            leaf->vdev_state != VDEV_STATE_CANT_OPEN ||
            leaf->vdev_stat.vs_aux != VDEV_AUX_TOO_SMALL)
            return 863;
        /* The leaf preserves the upstream TOO_SMALL/EOVERFLOW reason; root
         * may aggregate its error to ENXIO. This is a denied, unclean owner. */
        return 861;
    }
    if (opened || spa->spa_root_vdev != root || leaf->vdev_parent != root ||
        root->vdev_state != VDEV_STATE_HEALTHY ||
        leaf->vdev_state != VDEV_STATE_HEALTHY ||
        leaf->vdev_psize != 67108864 || !leaf->vdev_tsd)
        return 863;
    aether_engine_utc_phase('O');
#ifndef AETHER_PHYSICAL_WRITE
    if (completion_mode == 2)
        return 867; /* Intentional unclean open checkpoint, not retirement. */
#endif
#ifdef AETHER_PHYSICAL_WRITE
    int write_result = aether_physical_write_probe(spa, leaf, completion_mode);
    if (write_result)
        return write_result;
#endif
    unsigned char bytes[544];
    memset(bytes, 29, sizeof(bytes));
    abd_t *abd = abd_get_from_buf(bytes + 16, 512);
    if (!abd)
        return 863;
    struct aether_physical_completion record = {
        .spa = spa, .vdev = leaf, .abd = abd};
    zio_flag_t flags = ZIO_FLAG_CANFAIL | ZIO_FLAG_DONT_RETRY |
                       ZIO_FLAG_DONT_AGGREGATE | ZIO_FLAG_SPECULATIVE |
                       ZIO_FLAG_CONFIG_WRITER;
    if (!revoked) {
        aether_engine_utc_phase('Q');
        int result = zio_wait(
            zio_read_phys(NULL, leaf, 1048576, 512, abd, ZIO_CHECKSUM_OFF,
#ifdef AETHER_PHYSICAL_WRITE
                          aether_physical_done,
#else
                          completion_mode == 1 ? NULL : aether_physical_done,
#endif
                          &record, ZIO_PRIORITY_SYNC_READ, flags, B_FALSE));
        aether_engine_utc_phase('H');
        if (result || record.invalid)
            return 863;
        if (record.count != 1)
            return 862;
        for (unsigned i = 0; i < sizeof(bytes); ++i) {
            unsigned char expected = i < 16 || i >= 528
                                         ? 29
                                         : (unsigned char)((i - 16) * 17 +
#ifdef AETHER_PHYSICAL_WRITE
                                                           91
#else
                                                           7
#endif
                                           );
            if (bytes[i] != expected)
                return 860;
        }
        aether_engine_utc_phase('P');
    }
    if (revoked) {
        if (aether_volume_finish_probe())
            return 863;
        memset(bytes, 29, sizeof(bytes));
        record.count = 0;
        record.invalid = 0;
        record.error = 0;
        aether_engine_utc_phase('Q');
        int result = zio_wait(
            zio_read_phys(NULL, leaf, 1048576, 512, abd, ZIO_CHECKSUM_OFF,
                          aether_physical_done, &record, ZIO_PRIORITY_SYNC_READ,
                          flags, B_FALSE));
        aether_engine_utc_phase('H');
        /* Real file-vdev error and its upstream probe propagate ENXIO. No
         * substitute return value, retry of writes or fictitious device stop.
         */
        if (result != ENXIO || record.count != 1 || record.error != result ||
            record.invalid)
            return 863;
        for (unsigned i = 0; i < sizeof(bytes); ++i)
            if (bytes[i] != 29)
                return 863;
        aether_engine_utc_phase('E');
    }
    abd_free(abd);
    vdev_free(root);
    if (spa->spa_root_vdev)
        return 863;
    spa_config_exit(spa, SCL_ALL, FTAG);
    spa_deactivate(spa);
    if (spa->spa_state != POOL_STATE_UNINITIALIZED || spa->spa_root_vdev ||
        spa->spa_dsl_pool || spa->spa_normal_class || spa->spa_zvol_taskq)
        return 863;
    spa_remove(spa);
    if (spa_lookup("aether_physical_probe"))
        return 863;
    spa_namespace_exit(FTAG);
    aether_engine_utc_phase('D');
    return 0;
}
