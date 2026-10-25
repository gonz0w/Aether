/* SPDX-License-Identifier: BSD-2-Clause */
/* Types replace upstream headers only; actual import/control logic is included.
 */
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "filesystem-engine.h"
#define CHECK(x)                                                               \
    do {                                                                       \
        if (!(x)) {                                                            \
            fprintf(stderr, "IMPORT oracle94 line %d\n", __LINE__);            \
            exit(94);                                                          \
        }                                                                      \
    } while (0)
#define FTAG ((void *)1)
#define NV_UNIQUE_NAME 1
#define B_FALSE 0
#define SPA_VERSION_FEATURES 5000
#define SPA_FEATURE_HOLE_BIRTH 1
#define SPA_FEATURE_EMBEDDED_DATA 2
#define SPA_FEATURE_ZSTD_COMPRESS 3
#define DMU_POOL_DIRECTORY_OBJECT 1
#define DMU_POOL_CREATION_VERSION "version"
typedef struct {
    int live;
} nvlist_t;
typedef struct {
    struct {
        uint64_t ub_txg;
    } spa_uberblock;
    void *spa_meta_objset;
} spa_t;
static spa_t pool = {{782}, (void *)2};
static nvlist_t nodes[4];
static unsigned allocated, fault, calls, opens, closes, waits, exports, served,
    locks, ordered, mode;
static int point(void) { return ++calls == fault ? EIO : 0; }
static nvlist_t *new_node(void)
{
    for (int i = 0; i < 4; i++)
        if (!nodes[i].live) {
            nodes[i].live = 1;
            ++allocated;
            return &nodes[i];
        }
    exit(94);
}
static void nvlist_free(nvlist_t *p)
{
    if (p) {
        CHECK(p->live);
        p->live = 0;
        --allocated;
    }
}
static int aether_pool_label_read(nvlist_t **out)
{
    int e = point();
    if (!e)
        *out = new_node();
    return e;
}
static int aether_pool_label_config(nvlist_t *label, nvlist_t **out)
{
    CHECK(label && label->live);
    int e = point();
    if (!e)
        *out = new_node();
    return e;
}
static int nvlist_alloc(nvlist_t **out, int flags, int zero)
{
    CHECK(flags == 1 && !zero);
    int e = point();
    if (!e)
        *out = new_node();
    return e;
}
static int nvlist_add_string(nvlist_t *p, const char *key, const char *value)
{
    CHECK(p && p->live && !strcmp(key, "cachefile") && !strcmp(value, "none"));
    return point();
}
static int spa_import(const char *name, nvlist_t *config, nvlist_t *props,
                      int flags)
{
    CHECK(!strcmp(name, "testpool_zstd") && config->live && props->live &&
          !flags);
    return point();
}
static int spa_open(const char *name, spa_t **out, void *tag)
{
    CHECK(!strcmp(name, "testpool_zstd") && tag == FTAG);
    int e = point();
    if (!e) {
        *out = &pool;
        ++opens;
    }
    return e;
}
static int spa_writeable(spa_t *s)
{
    CHECK(s == &pool);
    return mode != 1;
}
static uint64_t spa_version(spa_t *s)
{
    CHECK(s == &pool);
    return mode == 2 ? 0 : 5000;
}
static uint64_t spa_guid(spa_t *s)
{
    CHECK(s == &pool);
    return mode == 3 ? 0 : UINT64_C(4253333510760776491);
}
static int spa_feature_is_active(spa_t *s, int feature)
{
    CHECK(s == &pool);
    return mode != (unsigned)(feature + 4);
}
static int zap_lookup(void *os, int object, const char *key, int size,
                      int count, uint64_t *v)
{
    CHECK(os == (void *)2 && object == 1 && !strcmp(key, "version") &&
          size == 8 && count == 1);
    int e = point();
    if (!e)
        *v = mode == 8 ? 0 : 5000;
    return e;
}
int aether_fs_launch_serve(void *s, struct aether_fs_launch_state *out)
{
    CHECK(s == &pool && opens == 1 && !closes && !waits && !exports &&
          out->phases == (16 | 32));
    ++served;
    out->service.txg = mode == 9 ? 0 : 800;
    return mode == 10 ? EPIPE : 0;
}
static void spa_close(spa_t *s, void *tag)
{
    CHECK(s == &pool && tag == FTAG && opens == 1 && !closes && !waits);
    ++closes;
}
static void dmu_buf_user_evict_wait(void)
{
    CHECK(closes == 1 && !exports);
    ++waits;
}
static int spa_export(const char *name, nvlist_t **out, int force, int hard)
{
    CHECK(!strcmp(name, "testpool_zstd") && closes == 1 && waits == 1 &&
          !force && !hard);
    ++exports;
    int e = point();
    if (!e)
        *out = new_node();
    return e;
}
static void spa_namespace_enter(void *tag)
{
    CHECK(tag == FTAG && exports == 1 && !locks);
    ++locks;
}
static void *spa_next(void *s)
{
    CHECK(!s && locks == 1);
    return mode == 11 ? &pool : NULL;
}
static void spa_namespace_exit(void *tag)
{
    CHECK(tag == FTAG && locks == 1);
    --locks;
}
static unsigned aether_pool_hooks_check_ordered(void)
{
    CHECK(exports == 1 && !locks);
    ++ordered;
    return mode == 12;
}
#include "import-under-test.inc"
int main(int argc, char **argv)
{
    CHECK(argc == 3);
    fault = atoi(argv[1]);
    mode = atoi(argv[2]);
    if (mode == 4)
        pool.spa_uberblock.ub_txg = 781;
    if (mode == 13)
        pool.spa_uberblock.ub_txg = 900;
    struct aether_fs_launch_state out = {0};
    int error = aether_fs_engine_import(&out);
    CHECK(!allocated && !locks && closes == opens);
    if (fault) {
        CHECK(calls == fault && error == EIO);
        CHECK(!(out.phases & AETHER_FS_EXPORTED));
    } else if ((mode >= 1 && mode <= 8) || mode == 11 || mode == 12) {
        CHECK(error == EIO && !(out.phases & AETHER_FS_EXPORTED));
    } else {
        CHECK(error == (mode == 10 ? EPIPE : 0));
        CHECK(out.phases == (16 | 32 | 64 | 128) && served == 1 &&
              closes == 1 && waits == 1 && exports == 1);
        CHECK(ordered == (mode == 9 ? 0 : 1));
    }
    if (mode >= 1 && mode <= 8)
        CHECK(!served && !waits && !exports);
    printf("calls=%u\n", calls);
    return 0;
}
