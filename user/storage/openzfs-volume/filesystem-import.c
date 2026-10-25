/* SPDX-License-Identifier: BSD-2-Clause */
/* Fixed scoped exported pool, retained original libzpool import/export APIs.
 * Names and label GUIDs constrain this provision; only native grants authorize
 * I/O.
 */
#include <sys/spa_impl.h>
#include <sys/zfeature.h>
#include <sys/dmu.h>
#include <sys/zap.h>
#include "pool-flow-witness.h"
#include "filesystem-engine.h"
extern int aether_pool_label_read(nvlist_t **);
extern int aether_pool_label_config(nvlist_t *, nvlist_t **);

int aether_fs_engine_import(struct aether_fs_launch_state *out)
{
    nvlist_t *label = NULL, *config = NULL, *props = NULL;
    int error = aether_pool_label_read(&label);
    if (!error)
        error = aether_pool_label_config(label, &config);
    nvlist_free(label);
    if (!error)
        error = nvlist_alloc(&props, NV_UNIQUE_NAME, 0);
    if (!error)
        error = nvlist_add_string(props, "cachefile", "none");
    if (!error)
        error = spa_import("testpool_zstd", config, props, 0);
    nvlist_free(props);
    nvlist_free(config);
    if (error)
        return error;
    spa_t *spa = NULL;
    error = spa_open("testpool_zstd", &spa, FTAG);
    if (error)
        return error;
    out->phases |= AETHER_FS_IMPORT;
    uint64_t version = 0;
    int valid = spa_writeable(spa) &&
                spa_version(spa) == SPA_VERSION_FEATURES &&
                spa_guid(spa) == UINT64_C(4253333510760776491) &&
                spa->spa_uberblock.ub_txg >= 782 &&
                spa_feature_is_active(spa, SPA_FEATURE_HOLE_BIRTH) &&
                spa_feature_is_active(spa, SPA_FEATURE_EMBEDDED_DATA) &&
                spa_feature_is_active(spa, SPA_FEATURE_ZSTD_COMPRESS);
    error = zap_lookup(spa->spa_meta_objset, DMU_POOL_DIRECTORY_OBJECT,
                       DMU_POOL_CREATION_VERSION, sizeof(version), 1, &version);
    if (!error && (!valid || version != SPA_VERSION_FEATURES))
        error = EIO;
    int service_error = 0;
    if (!error) {
        out->phases |= AETHER_FS_SERVICE;
        service_error = aether_fs_launch_serve(spa, out);
    }
    spa_close(spa, FTAG);
    out->phases |= AETHER_FS_SPA_CLOSED;
    if (error)
        return error; /* No unvalidated-pool cleanup claim. */
    dmu_buf_user_evict_wait();
    nvlist_t *exported = NULL;
    error = spa_export("testpool_zstd", &exported, B_FALSE, B_FALSE);
    nvlist_free(exported);
    if (error)
        return error;
    spa_namespace_enter(FTAG);
    int remaining = spa_next(NULL) != NULL;
    spa_namespace_exit(FTAG);
    if (remaining || (out->service.txg && aether_pool_hooks_check_ordered()))
        return EIO;
    out->phases |= AETHER_FS_EXPORTED;
    return service_error;
}
