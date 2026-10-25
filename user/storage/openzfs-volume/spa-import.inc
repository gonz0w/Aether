#ifdef AETHER_POOL_NAMESPACE
#ifdef AETHER_POOL_ZPL_WRITE
#include "spa-zpl-write.inc"
#elif defined(AETHER_POOL_ZPL_RECOVER)
#include "spa-zpl-recover.inc"
#else
#include "spa-namespace.inc"
#endif
#else
/* SPDX-License-Identifier: BSD-2-Clause */
/* Fresh readonly original-SPA/MOS metadata witness; no application DMU commit.
 */
#include <sys/dmu.h>
#include <sys/zap.h>
#include <sys/spa_impl.h>
extern int aether_pool_label_read(nvlist_t **);
extern int aether_pool_label_config(nvlist_t *, nvlist_t **);

/* One trusted experiment owns this private namespace; no concurrent API caller.
 * Original eviction drops the lock while stopping helpers. Close all client
 * borrows first, and never use the checked pointer after releasing the lock. */
static int aether_spa_import_retire(void)
{
    spa_namespace_enter(FTAG);
    spa_t *pool = spa_lookup("aether_pool_probe");
    int valid = pool && spa_next(NULL) == pool && spa_next(pool) == NULL &&
                !spa_writeable(pool) && spa_refcount_zero(pool);
    spa_namespace_exit(FTAG);
    if (!valid)
        return 873;
    /* spa_export requires global WRITE mode. Retire the readonly cache through
     * the same original routine used by spa_fini, without changing media. */
    spa_evict_all();
    spa_namespace_enter(FTAG);
    int remaining = spa_next(NULL) != NULL;
    spa_namespace_exit(FTAG);
    return remaining ? 873 : 0;
}

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
    uint64_t guid = 0, label_txg = 0;
    int error = aether_pool_label_read(&label);
    if (!error)
        error = aether_pool_label_config(label, &config);
    if (!error)
        error = nvlist_lookup_uint64(label, ZPOOL_CONFIG_POOL_GUID, &guid);
    if (!error)
        error = nvlist_lookup_uint64(label, ZPOOL_CONFIG_POOL_TXG, &label_txg);
    nvlist_free(label);
    if (!error)
        error = nvlist_alloc(&props, NV_UNIQUE_NAME, 0);
    if (!error)
        error = nvlist_add_string(props, "cachefile", "none");
    if (!error)
        error = nvlist_add_uint64(props, "readonly", 1);
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
        error = spa_import("aether_pool_probe", config, props, 0);
    }
    nvlist_free(props);
    nvlist_free(config);
    if (error) {
#ifdef AETHER_POOL_BAD_UBERBLOCKS
        /* Observe the original error without translating or repairing it. */
        aether_engine_utc_phase('E');
        for (unsigned i = 0; i < 4; ++i)
            aether_engine_utc_phase(((uint32_t)error >> (8 * i)) & 255);
#endif
        return 873;
    }
    aether_engine_utc_phase('A');
    spa_t *spa = NULL;
    if (spa_open("aether_pool_probe", &spa, FTAG))
        return 873;
    int valid = !spa_writeable(spa) &&
                spa_version(spa) == SPA_VERSION_FEATURES &&
                spa_guid(spa) == guid && spa->spa_uberblock.ub_txg >= label_txg;
    for (spa_feature_t f = 0; f < SPA_FEATURES; ++f)
        if (spa_feature_is_enabled(spa, f))
            valid = 0;
    uint64_t version = 0;
    error = zap_lookup(spa->spa_meta_objset, DMU_POOL_DIRECTORY_OBJECT,
                       DMU_POOL_CREATION_VERSION, sizeof(version), 1, &version);
#ifdef AETHER_POOL_DATA
    if (!valid || error || version != SPA_VERSION_FEATURES) {
        spa_close(spa, FTAG);
        return 873;
    }
    aether_engine_utc_phase('M');
    aether_engine_utc_phase('T');
    uint64_t target = 0;
    error = aether_pool_data_read(spa, &target);
    if (error) {
        spa_close(spa, FTAG);
        aether_engine_utc_phase('E');
        for (unsigned i = 0; i < 4; ++i)
            aether_engine_utc_phase(((uint32_t)error >> (8 * i)) & 255);
        return 873;
    }
    for (unsigned i = 0; i < 8; ++i)
        aether_engine_utc_phase((target >> (8 * i)) & 255);
    aether_engine_utc_phase('S');
    spa_close(spa, FTAG);
    /* Disown queues original user eviction. Drain without namespace/config
     * locks before checking actual remaining SPA references. */
    dmu_buf_user_evict_wait();
#else
    spa_close(spa, FTAG);
    if (!valid || error || version != SPA_VERSION_FEATURES)
        return 873;
    aether_engine_utc_phase('M');
#endif
    if (aether_spa_import_retire())
        return 873;
    aether_engine_utc_phase('D');
    return 0;
}

#endif
