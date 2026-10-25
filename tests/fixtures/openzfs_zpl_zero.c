/* SPDX-License-Identifier: BSD-2-Clause */
/* API/hash doubles, not original engine/disk/authority qualification. */
#include "zpl-resize.h"
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#define CHECK(c)                                                               \
    do {                                                                       \
        if (!(c)) {                                                            \
            fprintf(stderr, "HOST ZPL ZERO oracle97 line%d\n", __LINE__);      \
            exit(97);                                                          \
        }                                                                      \
    } while (0)
#define MIN(a, b) ((a) < (b) ? (a) : (b))
#define SHA256 1
#define SA_HDL_PRIVATE 2
#define ZPL_SIZE 0
#define ZPL_FLAGS 1
#define ZPL_MTIME 2
#define ZPL_CTIME 3
#define ZFS_ARCHIVE 8
#define ZFS_AV_MODIFIED 16
#define SA_ADD_BULK_ATTR(a, n, id, locator, p, len)                            \
    ((a)[(n)++] = (sa_bulk_attr_t){id, p, len})
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
struct aether_zpl_view {
    void *os;
    int *attributes;
};
typedef struct {
    size_t count;
    int valid;
} SHA2_CTX;
static int attrs[4] = {0, 1, 2, 3};
static aether_zpl_view view = {(void *)1, attrs};
static spa_t pool;
static sa_handle_t handle;
static int mode, calls, owned, handles, closes, mutations, opens, reads,
    clock_calls;
static uint64_t cursor;
static unsigned char observed[6];
static unsigned observed_count;
static int tick(void) { return ++calls == mode - 100 ? EIO : 0; }
static int spa_writeable(spa_t *s)
{
    CHECK(s == &pool);
    return mode != 1;
}
void aether_engine_utc_phase(unsigned char byte)
{
    CHECK(!owned && !handles && observed_count < 6);
    observed[observed_count++] = byte;
}
int aether_zpl_open_write(spa_t *s, const char *name, aether_zpl_view **out)
{
    CHECK(s == &pool && !strcmp(name, "testpool_zstd/x86_64") && !owned &&
          !*out);
    if (tick())
        return EIO;
    owned = 1;
    *out = &view;
    ++opens;
    return 0;
}
void aether_zpl_close(aether_zpl_view **out)
{
    CHECK(owned && !handles && *out == &view);
    owned = 0;
    *out = NULL;
    ++closes;
}
int aether_zpl_root(aether_zpl_view *v, aether_zpl_node *out)
{
    CHECK(owned && v == &view);
    if (tick())
        return EIO;
    *out = (aether_zpl_node){34, 45, 0, 040755};
    if (mode == 2)
        out->object++;
    return 0;
}
int aether_zpl_lookup(aether_zpl_view *v, uint64_t object, uint64_t generation,
                      const unsigned char *name, size_t length,
                      aether_zpl_node *out)
{
    CHECK(owned && v == &view && object == 34 && generation == 45 &&
          length == 4 && !memcmp(name, "zstd", 4));
    if (tick())
        return EIO;
    *out = (aether_zpl_node){2, 47, mutations ? 0 : 780248, 0100755};
    if (mode == 3 && !mutations)
        out->size++;
    if (mode == 11 && mutations)
        out->generation++;
    return 0;
}
int aether_zpl_read(aether_zpl_view *v, uint64_t object, uint64_t generation,
                    uint64_t offset, void *buffer, size_t capacity,
                    size_t *count)
{
    CHECK(owned && v == &view && object == 2 && generation == 47 && buffer &&
          capacity <= 4096);
    *count = 0;
    if (tick())
        return EIO;
    ++reads;
    if (mutations) {
        CHECK(opens == 2 && (offset == 0 || offset == 780248));
        if (mode == 12 || (mode == 13 && offset))
            *count = 1;
        return 0;
    }
    CHECK(opens == 1 && offset == cursor);
    if (offset == 780248) {
        if (mode == 4)
            *count = 1;
        return 0;
    }
    *count = MIN(capacity, 780248 - offset);
    if (mode == 5)
        --*count;
    for (size_t i = 0; i < *count; ++i)
        ((unsigned char *)buffer)[i] = (unsigned char)((offset + i) * 17 + 3);
    cursor += *count;
    return 0;
}
static int zero_clock(clockid_t id, struct timespec *out)
{
    CHECK(id == CLOCK_REALTIME && owned && !mutations && cursor == 780248);
    ++clock_calls;
    if (tick())
        return -1;
    *out = (struct timespec){mode == 7 ? -1 : 1234,
                             mode == 19 ? 1000000000 : 5678};
    return 0;
}
int aether_zpl_shrink(aether_zpl_view *v, uint64_t object, uint64_t generation,
                      uint64_t size, uint64_t seconds, uint64_t nanos,
                      aether_zpl_write_result *out)
{
    CHECK(v == &view && owned && !mutations && object == 2 &&
          generation == 47 && !size && seconds == 1234 && nanos == 5678);
    CHECK(!out->txg && !out->bytes_staged && !out->state);
    ++mutations;
    *out = (aether_zpl_write_result){
        mode == 9 ? 0 : 42, mode == 10 ? 16 : 0,
        (mode == 8 || mode == 18) ? AETHER_ZPL_COMMITTED : AETHER_ZPL_SYNCED};
    return tick() || mode == 8 ? EIO : 0;
}
static int sa_handle_get(void *os, uint64_t object, void *unused, int flags,
                         sa_handle_t **out)
{
    CHECK(os == (void *)1 && object == 2 && !unused &&
          flags == SA_HDL_PRIVATE && owned && !handles && mutations &&
          opens == 2);
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
    for (int i = 0; i < n; ++i) {
        CHECK(a[i].attr == i && a[i].length == (i < 2 ? 8 : 16));
        uint64_t *p = a[i].data;
        if (i == 0)
            *p = mode == 14 ? 1 : 0;
        if (i == 1)
            *p = mode == 15 ? ZFS_ARCHIVE : ZFS_ARCHIVE | ZFS_AV_MODIFIED;
        if (i >= 2) {
            p[0] = mode == 17 ? 1235 : 1234;
            p[1] = 5678;
            if (mode == 16 && i == 3)
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
static void SHA2Init(int algorithm, SHA2_CTX *hash)
{
    CHECK(algorithm == SHA256);
    *hash = (SHA2_CTX){0, 1};
}
static void SHA2Update(SHA2_CTX *hash, const void *data, size_t size)
{
    CHECK(size && size <= 4096);
    const unsigned char *bytes = data;
    for (size_t i = 0; i < size; ++i)
        if (bytes[i] != (unsigned char)((hash->count + i) * 17 + 3))
            hash->valid = 0;
    hash->count += size;
}
static void SHA2Final(unsigned char *out, SHA2_CTX *hash)
{
    static const unsigned char expected[32] = {
        0xcc, 0x9b, 0xfd, 0xde, 0xdd, 0x66, 0x4b, 0x9a, 0x53, 0x34, 0x58,
        0x1a, 0xf7, 0x86, 0x51, 0x6d, 0x14, 0x9c, 0x3f, 0xbd, 0x2c, 0x7e,
        0x65, 0x73, 0x59, 0x85, 0xac, 0xf1, 0x7b, 0xce, 0x59, 0x35};
    memset(out, 0, 32);
    if (hash->valid && hash->count == 780248)
        memcpy(out, expected, 32);
    if (mode == 6)
        out[0] ^= 1;
}
#define clock_gettime zero_clock
#include "zero-probe.inc"
int main(int argc, char **argv)
{
    CHECK(argc == 2);
    mode = atoi(argv[1]);
    uint64_t assigned = 99;
    int error = aether_pool_namespace_write(&pool, &assigned);
    CHECK((error == 0) == (mode == 0));
    CHECK(!owned && !handles && closes == opens);
    CHECK(assigned == (mutations && mode != 9 ? 42 : 0));
    CHECK(mutations <= 1 && clock_calls <= 1 && opens <= 2);
    if (error && mode != 1) {
        CHECK(observed_count == 6 && observed[0] == 'E');
        uint32_t code = 0;
        for (unsigned i = 0; i < 4; ++i)
            code |= (uint32_t)observed[i + 2] << (8 * i);
        CHECK(code == (uint32_t)error);
    } else
        CHECK(!observed_count);
    if (!mode) {
        CHECK(opens == 2 && closes == 2 && mutations == 1 && calls == 204 &&
              reads == 194);
    }
    return 0;
}
