/* SPDX-License-Identifier: BSD-2-Clause */
/* API/SHA doubles only: ownership, stream order and metadata, not disk
 * decoding. */
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "zpl-read.h"
#define CHECK(c)                                                               \
    do {                                                                       \
        if (!(c)) {                                                            \
            fprintf(stderr, "HOST ZPL RECOVERY oracle98 line%d\n", __LINE__);  \
            exit(98);                                                          \
        }                                                                      \
    } while (0)
#define MIN(a, b) ((a) < (b) ? (a) : (b))
#define SHA256 1
#define SA_HDL_PRIVATE 2
#define ZFS_ARCHIVE 8
#define ZFS_AV_MODIFIED 16
#define ZPL_SIZE 0
#define ZPL_FLAGS 1
#define ZPL_MTIME 2
#define ZPL_CTIME 3
typedef struct spa {
    int unused;
} spa_t;
typedef struct {
    int unused;
} sa_handle_t;
typedef struct {
    int attr;
    void *data;
    size_t length;
} sa_bulk_attr_t;
#define SA_ADD_BULK_ATTR(a, n, id, locator, p, len)                            \
    ((a)[(n)++] = (sa_bulk_attr_t){id, p, len})
struct aether_zpl_view {
    void *os;
    int *attributes;
};
typedef struct {
    size_t count;
} SHA2_CTX;
static int attrs[4] = {0, 1, 2, 3};
static aether_zpl_view view = {(void *)1, attrs};
static spa_t pool;
static sa_handle_t handle;
static int mode, calls, owned, handles, closes;
static size_t position;
static int tick(void) { return ++calls == mode - 100 ? EIO : 0; }
static int spa_writeable(spa_t *s)
{
    CHECK(s == &pool);
    return mode == 1;
}
int aether_zpl_open(spa_t *s, const char *name, aether_zpl_view **out)
{
    CHECK(s == &pool && !strcmp(name, "testpool_zstd/x86_64") && !owned);
    if (tick())
        return EIO;
    *out = &view;
    owned = 1;
    return 0;
}
void aether_zpl_close(aether_zpl_view **v)
{
    CHECK(*v == &view && owned && !handles);
    *v = NULL;
    owned = 0;
    closes++;
}
int aether_zpl_root(aether_zpl_view *v, aether_zpl_node *out)
{
    CHECK(v == &view && owned);
    if (tick())
        return EIO;
    *out = (aether_zpl_node){34, 45, 0, 040755};
    if (mode == 2)
        out->generation--;
    if (mode == 3)
        out->object++;
    if (mode == 4)
        out->mode = 0100755;
    return 0;
}
int aether_zpl_lookup(aether_zpl_view *v, uint64_t obj, uint64_t gen,
                      const unsigned char *name, size_t length,
                      aether_zpl_node *out)
{
    CHECK(v == &view && owned && obj == 34 && gen == 45 && length == 4 &&
          !memcmp(name, "zstd", 4));
    if (tick())
        return EIO;
    *out = (aether_zpl_node){2, 47, 780248, 0100755};
    if (mode == 5)
        out->generation--;
    if (mode == 6)
        out->size++;
    if (mode == 7)
        out->mode = 040755;
    if (mode == 8)
        out->object++;
    return 0;
}
int aether_zpl_read(aether_zpl_view *v, uint64_t obj, uint64_t gen,
                    uint64_t off, void *buf, size_t len, size_t *count)
{
    CHECK(v == &view && owned && obj == 2 && gen == 47 && len == 4096 &&
          off == position && buf);
    *count = 0;
    if (tick())
        return EIO;
    if (off == 780248) {
        if (mode == 9)
            *count = 1;
        return 0;
    }
    *count = MIN(len, 780248 - off);
    if (mode == 10)
        (*count)--;
    memset(buf, 0, *count);
    position += *count;
    return 0;
}
static void SHA2Init(int algorithm, SHA2_CTX *hash)
{
    CHECK(algorithm == SHA256);
    hash->count = 0;
}
static void SHA2Update(SHA2_CTX *hash, const void *buf, size_t count)
{
    CHECK(buf && count <= 4096);
    hash->count += count;
}
static void SHA2Final(void *out, SHA2_CTX *hash)
{
    static const unsigned char expected[32] = {EXPECTED_HASH_BYTES};
    memset(out, 0, 32);
    if (hash->count == 780248)
        memcpy(out, expected, 32);
    if (mode == 11)
        ((unsigned char *)out)[0] ^= 1;
}
static int sa_handle_get(void *os, uint64_t obj, void *unused, int flags,
                         sa_handle_t **out)
{
    CHECK(os == (void *)1 && obj == 2 && !unused && flags == SA_HDL_PRIVATE &&
          owned && !handles && position == 780248);
    if (tick())
        return EIO;
    handles = 1;
    *out = &handle;
    return 0;
}
static int sa_bulk_lookup(sa_handle_t *h, sa_bulk_attr_t *a, int n)
{
    CHECK(h == &handle && handles && n == 4);
    if (tick())
        return EIO;
    for (int i = 0; i < n; i++) {
        CHECK(a[i].attr == i && a[i].length == (i < 2 ? 8 : 16));
        uint64_t *p = a[i].data;
        if (i == 0)
            *p = mode == 12 ? 1 : 780248;
        if (i == 1)
            *p = mode == 13   ? ZFS_ARCHIVE
                 : mode == 14 ? ZFS_AV_MODIFIED
                              : ZFS_ARCHIVE | ZFS_AV_MODIFIED;
        if (i >= 2) {
            p[0] = 1791290041;
            p[1] = 12345;
            if (mode == 15)
                p[0] = 1791290039;
            if (mode == 16)
                p[0] = 1791290071;
            if (mode == 17)
                p[1] = 1000000000;
            if (mode == 18 && i == 3)
                p[1]++;
        }
    }
    return 0;
}
static void sa_handle_destroy(sa_handle_t *h)
{
    CHECK(h == &handle && handles);
    handles = 0;
}
#include "zpl-recovery.inc"
int main(int argc, char **argv)
{
    CHECK(argc == 2);
    mode = atoi(argv[1]);
    int error = aether_pool_namespace_recover(&pool);
    CHECK((error == 0) == (mode == 0));
    CHECK(!owned && !handles);
    CHECK(closes == ((mode == 1 || mode == 101) ? 0 : 1));
    if (!mode)
        CHECK(calls == 197 && position == 780248);
    return 0;
}
