/* SPDX-License-Identifier: BSD-2-Clause */
/* Private complete writer; execution stays gated pending fresh-VM readback. */
#include <sys/dmu.h>
#include <sys/spa_impl.h>
#include <sys/zap.h>
#include "pool-flow-witness.h"
extern int aether_pool_label_read(nvlist_t **);
extern int aether_pool_label_config(nvlist_t *, nvlist_t **);
extern int aether_pool_namespace_write(spa_t *, uint64_t *);

int aether_spa_import_probe(void)
{
    if (getauxval(0xa001) != 0x50000101UL) {
        zfs_file_t *file = NULL;
        if (zfs_file_open(AETHER_VOLUME_PATH, O_RDONLY, 0, NULL, &file) !=
                ENODEV ||
            file)
            return 873;
        aether_engine_utc_phase('N');
        return 0;
    }
    aether_engine_utc_phase('L');
    nvlist_t *label = NULL, *config = NULL, *props = NULL;
    int error = aether_pool_label_read(&label);
    if (!error)
        error = aether_pool_label_config(label, &config);
    nvlist_free(label);
    if (!error)
        error = nvlist_alloc(&props, NV_UNIQUE_NAME, 0);
    if (!error)
        error = nvlist_add_string(props, "cachefile", "none");
    uint64_t hash = UINT64_C(14695981039346656037);
    if (!error)
        error = aether_pool_config_hash(config, &hash);
    if (!error)
        error = aether_pool_config_hash(props, &hash);
    if (!error) {
        aether_engine_utc_phase('P');
        for (unsigned i = 0; i < 8; ++i)
            aether_engine_utc_phase((hash >> (8 * i)) & 255);
        aether_engine_utc_phase('O');
        error = spa_import("testpool_zstd", config, props, 0);
    }
    nvlist_free(props);
    nvlist_free(config);
    if (error)
        return 873;
    aether_engine_utc_phase('A');
    spa_t *spa = NULL;
    if (spa_open("testpool_zstd", &spa, FTAG))
        return 873;
    uint64_t version = 0, target = 0;
    int valid = spa_writeable(spa) &&
                spa_version(spa) == SPA_VERSION_FEATURES &&
                spa_guid(spa) == UINT64_C(4253333510760776491) &&
                spa->spa_uberblock.ub_txg >= 782 &&
                spa_feature_is_active(spa, SPA_FEATURE_HOLE_BIRTH) &&
                spa_feature_is_active(spa, SPA_FEATURE_EMBEDDED_DATA) &&
                spa_feature_is_active(spa, SPA_FEATURE_ZSTD_COMPRESS);
    error = zap_lookup(spa->spa_meta_objset, DMU_POOL_DIRECTORY_OBJECT,
                       DMU_POOL_CREATION_VERSION, sizeof(version), 1, &version);
    if (valid && !error && version == SPA_VERSION_FEATURES) {
        aether_engine_utc_phase('M');
        aether_engine_utc_phase('T');
        error = aether_pool_namespace_write(spa, &target);
    } else
        error = EIO;
    spa_close(spa, FTAG);
    if (error || !target)
        return 873;
    for (unsigned i = 0; i < 8; ++i)
        aether_engine_utc_phase((target >> (8 * i)) & 255);
    aether_engine_utc_phase('S');
    dmu_buf_user_evict_wait();
    nvlist_t *exported = NULL;
    error = spa_export("testpool_zstd", &exported, B_FALSE, B_FALSE);
    nvlist_free(exported);
    if (error)
        return 873;
    spa_namespace_enter(FTAG);
    int remaining = spa_next(NULL) != NULL;
    spa_namespace_exit(FTAG);
    if (remaining || aether_pool_hooks_check_ordered())
        return 873;
    aether_engine_utc_phase('D');
    return 0;
}
