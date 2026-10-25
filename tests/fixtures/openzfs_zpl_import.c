/* SPDX-License-Identifier: BSD-2-Clause */
/* Actual private import orchestration over ownership/order API doubles. */
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(c)                                                               \
    do {                                                                       \
        if (!(c)) {                                                            \
            fprintf(stderr, "HOST ZPL IMPORT oracle97 line%d\n", __LINE__);    \
            exit(97);                                                          \
        }                                                                      \
    } while (0)
#define AETHER_VOLUME_PATH "/private-volume"
#define O_RDONLY 0
#define NV_UNIQUE_NAME 1
#define FTAG ((void *)1)
#define SPA_VERSION_FEATURES 5000
#define SPA_FEATURE_HOLE_BIRTH 1
#define SPA_FEATURE_EMBEDDED_DATA 2
#define SPA_FEATURE_ZSTD_COMPRESS 3
#define DMU_POOL_DIRECTORY_OBJECT 1
#define DMU_POOL_CREATION_VERSION 2
#define B_FALSE 0
typedef struct {
    int live;
} nvlist_t;
typedef struct {
    int unused;
} zfs_file_t;
typedef struct {
    struct {
        uint64_t ub_txg;
    } spa_uberblock;
    void *spa_meta_objset;
} spa_t;
static nvlist_t lists[4];
static spa_t pool = {{782}, (void *)2};
static int mode, calls, allocated, borrowed, imported, drained, exports,
    checked, namespace_locked, writes;
static char phases[64];
static size_t phase_count;
static int tick(void) { return ++calls == mode - 100 ? EIO : 0; }
static nvlist_t *allocate(void)
{
    for (unsigned i = 0; i < 4; ++i)
        if (!lists[i].live) {
            lists[i].live = 1;
            ++allocated;
            return &lists[i];
        }
    CHECK(0);
    return NULL;
}
static void nvlist_free(nvlist_t *p)
{
    if (!p)
        return;
    CHECK(p->live && allocated);
    p->live = 0;
    --allocated;
}
static int getauxval(unsigned long tag)
{
    CHECK(tag == 0xa001);
    return mode == 1 ? 0 : 0x50000101;
}
static int zfs_file_open(const char *path, int flags, int mode_arg, void *cr,
                         zfs_file_t **out)
{
    CHECK(!strcmp(path, AETHER_VOLUME_PATH) && flags == O_RDONLY && !mode_arg &&
          !cr && !*out);
    return ENODEV;
}
static void aether_engine_utc_phase(unsigned char value)
{
    CHECK(phase_count < sizeof(phases));
    phases[phase_count++] = value;
}
static int aether_pool_label_read(nvlist_t **out)
{
    if (tick())
        return EIO;
    *out = allocate();
    return 0;
}
static int aether_pool_label_config(nvlist_t *label, nvlist_t **out)
{
    CHECK(label && label->live);
    if (tick())
        return EIO;
    *out = allocate();
    return 0;
}
static int nvlist_alloc(nvlist_t **out, int flags, int how)
{
    CHECK(flags == NV_UNIQUE_NAME && !how);
    if (tick())
        return EIO;
    *out = allocate();
    return 0;
}
static int nvlist_add_string(nvlist_t *p, const char *key, const char *value)
{
    CHECK(p->live && !strcmp(key, "cachefile") && !strcmp(value, "none"));
    return tick();
}
static int aether_pool_config_hash(nvlist_t *p, uint64_t *hash)
{
    CHECK(p->live);
    *hash = 42;
    return tick();
}
static int spa_import(const char *name, nvlist_t *config, nvlist_t *props,
                      int flags)
{
    CHECK(!strcmp(name, "testpool_zstd") && config->live && props->live &&
          !flags && !imported);
    if (tick())
        return EIO;
    imported = 1;
    return 0;
}
static int spa_open(const char *name, spa_t **out, const void *tag)
{
    CHECK(!strcmp(name, "testpool_zstd") && imported && !allocated &&
          tag == FTAG && !borrowed);
    if (tick())
        return EIO;
    *out = &pool;
    borrowed = 1;
    return 0;
}
static void spa_close(spa_t *spa, const void *tag)
{
    CHECK(spa == &pool && borrowed && tag == FTAG);
    borrowed = 0;
}
static int spa_writeable(spa_t *spa)
{
    CHECK(spa == &pool && borrowed);
    return mode != 20;
}
static uint64_t spa_version(spa_t *spa)
{
    CHECK(spa == &pool);
    return mode == 21 ? 28 : 5000;
}
static uint64_t spa_guid(spa_t *spa)
{
    CHECK(spa == &pool);
    return mode == 22 ? 1 : UINT64_C(4253333510760776491);
}
static int spa_feature_is_active(spa_t *spa, int feature)
{
    CHECK(spa == &pool);
    return mode != 23 || feature != SPA_FEATURE_ZSTD_COMPRESS;
}
static int zap_lookup(void *os, int object, int key, int size, int count,
                      uint64_t *out)
{
    CHECK(os == (void *)2 && object == 1 && key == 2 && size == 8 &&
          count == 1 && borrowed);
    if (tick())
        return EIO;
    *out = mode == 24 ? 28 : 5000;
    return 0;
}
static int aether_pool_namespace_write(spa_t *spa, uint64_t *out)
{
    CHECK(spa == &pool && borrowed && !writes);
    ++writes;
    if (tick() || mode == 25)
        return EIO;
    *out = mode == 26 ? 0 : 788;
    return 0;
}
static void dmu_buf_user_evict_wait(void)
{
    CHECK(imported && !borrowed && writes == 1 && !drained && !exports);
    drained = 1;
}
static int spa_export(const char *name, nvlist_t **out, int force,
                      int hardforce)
{
    CHECK(!strcmp(name, "testpool_zstd") && imported && !borrowed && drained &&
          !force && !hardforce);
    ++exports;
    *out = allocate();
    if (tick() || mode == 27)
        return EIO;
    imported = 0;
    return 0;
}
static void spa_namespace_enter(const void *tag)
{
    CHECK(tag == FTAG && !namespace_locked && exports && drained);
    namespace_locked = 1;
}
static spa_t *spa_next(spa_t *previous)
{
    CHECK(namespace_locked && !previous);
    return mode == 28 ? &pool : NULL;
}
static void spa_namespace_exit(const void *tag)
{
    CHECK(tag == FTAG && namespace_locked);
    namespace_locked = 0;
}
static unsigned aether_pool_hooks_check_ordered(void)
{
    CHECK(exports == 1 && drained && !borrowed && !allocated &&
          !namespace_locked);
    ++checked;
    return tick() || mode == 29;
}
#include "zpl-import.inc"
int main(int argc, char **argv)
{
    CHECK(argc == 2);
    mode = atoi(argv[1]);
    if (mode == 30)
        pool.spa_uberblock.ub_txg = 781;
    int error = aether_spa_import_probe();
    CHECK((error == 0) == (mode == 0 || mode == 1));
    CHECK(!borrowed && !allocated && !namespace_locked);
    if (!mode) {
        CHECK(calls == 12 && exports == 1 && checked == 1 && !imported &&
              phases[phase_count - 1] == 'D');
        /* The surrounding engine supplies BIUVW then JFR: exactly32 rows,
         * within the unchanged256-byte kernel output capacity. */
        static const unsigned char expected[] =
            "LP\x2a\0\0\0\0\0\0\0OAMT\x14\x03\0\0\0\0\0\0SD";
        CHECK(phase_count == sizeof(expected) - 1 &&
              !memcmp(phases, expected, sizeof(expected) - 1) &&
              (phase_count + 8) * 8 == 256);
    } else if (mode == 1)
        CHECK(calls == 0 && phase_count == 1 && phases[0] == 'N');
    else
        CHECK(!phase_count || phases[phase_count - 1] != 'D');
    return 0;
}
