/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_HOME_NATIVE_HOST_H
#define AETHER_HOME_NATIVE_HOST_H
#include <errno.h>
#include <stddef.h>
#include <stdint.h>
typedef struct {
    unsigned unused;
} nvlist_t;
typedef struct {
    unsigned unused;
} objset_t;
struct aether_zfs_startup;
typedef struct {
    struct {
        uint64_t ub_txg;
    } spa_uberblock;
    objset_t *spa_meta_objset;
} spa_t;
#define NV_UNIQUE_NAME 1U
#define SPA_VERSION_FEATURES UINT64_C(5000)
#define SPA_FEATURE_HOLE_BIRTH 1
#define SPA_FEATURE_EMBEDDED_DATA 2
#define SPA_FEATURE_ZSTD_COMPRESS 3
#define DMU_POOL_DIRECTORY_OBJECT UINT64_C(1)
#define DMU_POOL_CREATION_VERSION "creation_version"
#define FTAG ((const void *)"home-host")
#define B_FALSE 0
#define AETHER_UTC_Q35_RTC_UNAUTHENTICATED 1U
void nvlist_free(nvlist_t *);
int nvlist_alloc(nvlist_t **, unsigned, int);
int nvlist_add_string(nvlist_t *, const char *, const char *);
int spa_import(char *, nvlist_t *, nvlist_t *, uint64_t);
int spa_open(const char *, spa_t **, const void *);
int spa_writeable(spa_t *);
uint64_t spa_version(spa_t *);
uint64_t spa_guid(spa_t *);
int spa_feature_is_active(spa_t *, int);
int zap_lookup(objset_t *, uint64_t, const char *, uint64_t, uint64_t, void *);
void spa_close(spa_t *, const void *);
void dmu_buf_user_evict_wait(void);
int spa_export(const char *, nvlist_t **, int, int);
void spa_namespace_enter(const void *);
void spa_namespace_exit(const void *);
spa_t *spa_next(spa_t *);
int aether_runtime_init(void);
unsigned aether_runtime_live(void);
unsigned aether_runtime_admissions(void);
int aether_runtime_finish(void);
int aether_zfs_startup_bind(const struct aether_zfs_startup *);
int aether_zfs_volume_bind(uint64_t);
int aether_utc_establish(unsigned);
int aether_utc_close(void);
int home_host_block_close(uint64_t);
#endif
