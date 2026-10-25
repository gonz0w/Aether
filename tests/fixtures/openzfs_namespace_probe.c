/* SPDX-License-Identifier: BSD-2-Clause */
/* API/hash model for the actual guest verifier; no native disk qualification.
 */
#include "zpl-mutate.h"
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#define CHECK(c)                                                               \
    do {                                                                       \
        if (!(c)) {                                                            \
            fprintf(stderr, "HOST NAMESPACE oracle95 line%d\n", __LINE__);     \
            exit(95);                                                          \
        }                                                                      \
    } while (0)
#define MIN(a, b) ((a) < (b) ? (a) : (b))
#define B_FALSE 0
#define SA_HDL_PRIVATE 2
#define SHA256 1
#define ZFS_ARCHIVE 1
#define ZFS_AV_MODIFIED 2
#define ZFS_ACL_TRIVIAL 4
#define ZFS_ACL_PROTECTED 8
#define ZFS_PROJID 16
#define ACE_OWNER 1
#define ACE_GROUP 2
#define ACE_IDENTIFIER_GROUP 4
#define ACE_EVERYONE 8
enum {
    ZPL_FLAGS,
    ZPL_LINKS,
    ZPL_PARENT,
    ZPL_UID,
    ZPL_GID,
    ZPL_SIZE,
    ZPL_MTIME,
    ZPL_CTIME,
    ZPL_PROJID,
    ZPL_CRTIME,
    ZPL_ATIME,
    ZPL_DACL_COUNT,
    ZPL_DACL_ACES,
    ZPL_END
};
typedef struct spa {
    int unused;
} spa_t;
typedef struct {
    int object;
} sa_handle_t;
typedef struct {
    int attr;
    void *data;
    size_t length;
} sa_bulk_attr_t;
typedef struct {
    uint16_t z_type, z_flags;
    uint32_t z_access_mask;
} zfs_ace_hdr_t;
typedef struct {
    uint64_t bytes;
} SHA2_CTX;
struct aether_zpl_view {
    void *os;
    int *attributes;
};
#define SA_ADD_BULK_ATTR(a, n, id, loc, p, len)                                \
    ((a)[(n)++] = (sa_bulk_attr_t){id, p, len})
static int attrs[ZPL_END], mode, fault, calls, owned, handles, opens, closes,
    phase, mutations;
static uint64_t position;
static spa_t pool;
static aether_zpl_view view = {(void *)1, attrs};
static sa_handle_t handle;
static unsigned char observed[6];
static unsigned observed_count;
static int tick(void) { return ++calls == fault ? EIO : 0; }
static int spa_writeable(spa_t *s)
{
    CHECK(s == &pool);
    return !MNS_READER;
}
void aether_engine_utc_phase(unsigned char byte)
{
    CHECK(!owned && !handles && observed_count < 6);
    observed[observed_count++] = byte;
}
int aether_zpl_open(struct spa *s, const char *name, aether_zpl_view **out)
{
    CHECK(s == &pool && !strcmp(name, "testpool_zstd/x86_64") && !owned &&
          !*out);
    if (tick())
        return EIO;
    *out = &view;
    owned = 1;
    ++opens;
    position = 0;
    return 0;
}
int aether_zpl_open_write(struct spa *s, const char *name,
                          aether_zpl_view **out)
{
    return aether_zpl_open(s, name, out);
}
void aether_zpl_close(aether_zpl_view **out)
{
    CHECK(owned && !handles && *out == &view);
    *out = NULL;
    owned = 0;
    ++closes;
}
int aether_zpl_root(aether_zpl_view *v, aether_zpl_node *out)
{
    CHECK(v == &view && owned);
    if (tick())
        return EIO;
    *out = (aether_zpl_node){34, 45, phase == 1 || phase == 2 ? 4 : 3, 040755};
    if (mode == 1)
        ++out->generation;
    if (mode == 2)
        ++out->size;
    return 0;
}
int aether_zpl_lookup(aether_zpl_view *v, uint64_t object, uint64_t gen,
                      const unsigned char *name, size_t length,
                      aether_zpl_node *out)
{
    CHECK(v == &view && owned && object == 34 && gen == 45 &&
          length == strlen((const char *)name));
    if (tick())
        return EIO;
    if (!strcmp((const char *)name, "zstd")) {
        *out = (aether_zpl_node){2, 47, 780248, 0100755};
        if (mode == 3)
            ++out->generation;
        return 0;
    }
    int present =
        (phase == 1 && !strcmp((const char *)name, "aether-created")) ||
        (phase == 2 && !strcmp((const char *)name, "aether-renamed"));
    if (mode == 6)
        present = !present;
    if (!present)
        return ENOENT;
    *out = (aether_zpl_node){99, 788, 0, 0100600};
    if (mode == 7)
        out->generation = 47;
    if (mode == 8)
        ++out->mode;
    if (mode == 9)
        ++out->size;
    if (mode == 20 && opens == 2)
        ++out->object;
    return 0;
}
int aether_zpl_read(aether_zpl_view *v, uint64_t object, uint64_t gen,
                    uint64_t off, void *buf, size_t length, size_t *count)
{
    CHECK(v == &view && owned && buf && count);
    *count = 0;
    if (tick())
        return EIO;
    if (object == 99 || object == 100) {
        CHECK(gen == 788 && !off && length == 1);
        *count = mode == 10;
        return 0;
    }
    CHECK(object == 2 && gen == 47 && length == 4096 && off == position);
    *count = MIN(length, 780248 - position);
    memset(buf, 0xa5, *count);
    position += *count;
    if (mode == 5 && position == 780248 && !*count)
        *count = 1;
    return 0;
}
static void SHA2Init(int kind, SHA2_CTX *hash)
{
    CHECK(kind == SHA256);
    hash->bytes = 0;
}
static void SHA2Update(SHA2_CTX *hash, const void *buf, size_t size)
{
    CHECK(buf && size && size <= 4096);
    const unsigned char *p = buf;
    for (size_t i = 0; i < size; ++i)
        CHECK(p[i] == 0xa5);
    hash->bytes += size;
}
static void SHA2Final(unsigned char *digest, SHA2_CTX *hash)
{
    static const unsigned char original[32] = {
        0xcc, 0x9b, 0xfd, 0xde, 0xdd, 0x66, 0x4b, 0x9a, 0x53, 0x34, 0x58,
        0x1a, 0xf7, 0x86, 0x51, 0x6d, 0x14, 0x9c, 0x3f, 0xbd, 0x2c, 0x7e,
        0x65, 0x73, 0x59, 0x85, 0xac, 0xf1, 0x7b, 0xce, 0x59, 0x35};
    memcpy(digest, original, 32);
    if (mode == 4 || hash->bytes != 780248)
        digest[0] ^= 1;
}
static int zap_count(void *os, uint64_t object, uint64_t *count)
{
    CHECK(os == view.os && owned && object == 34);
    if (tick())
        return EIO;
    *count = phase == 1 || phase == 2 ? 2 : 1;
    if (mode == 15)
        ++*count;
    return 0;
}
static int dmu_object_next(void *os, uint64_t *object, int holes, uint64_t txg)
{
    CHECK(os == view.os && owned && !holes && !txg);
    if (tick())
        return EIO;
    static const uint64_t list[] = {1, 2, 3, 4, 32, 33, 34, 35, 36, 99};
    unsigned end = phase == 1 || phase == 2 ? 10 : 9;
    for (unsigned i = 0; i < end; ++i)
        if (list[i] > *object) {
            *object = list[i];
            if (mode == 17 && i == 0)
                *object = 98;
            if (mode == 18 && i == end - 1)
                return ESRCH;
            if (mode == 19 && i == 1)
                *object = 1;
            return 0;
        }
    return ESRCH;
}
static int sa_handle_get(void *os, uint64_t object, void *tag, int flags,
                         sa_handle_t **out)
{
    CHECK(os == view.os && owned && !handles && !tag &&
          flags == SA_HDL_PRIVATE);
    if (tick())
        return EIO;
    handle.object = object;
    *out = &handle;
    ++handles;
    return 0;
}
static void sa_handle_destroy(sa_handle_t *h)
{
    CHECK(h == &handle && handles == 1);
    --handles;
}
static int sa_bulk_lookup(sa_handle_t *h, sa_bulk_attr_t *a, int n)
{
    CHECK(h == &handle && handles == 1 && n == (h->object == 34 ? 8 : 13));
    if (tick())
        return EIO;
    int file = h->object != 34;
    for (int i = 0; i < n; ++i) {
        uint64_t value = 0;
        switch (a[i].attr) {
        case ZPL_FLAGS:
            value = 31;
            if (mode == 11)
                value = 0;
            break;
        case ZPL_LINKS:
            value = file ? 1 : 2;
            break;
        case ZPL_PARENT:
            value = 34 + (mode == 16);
            break;
        case ZPL_UID:
        case ZPL_GID:
            value = file ? 1000 : 0;
            if (mode == 12)
                ++value;
            break;
        case ZPL_SIZE:
            value = file ? 0 : phase == 1 || phase == 2 ? 4 : 3;
            break;
        case ZPL_DACL_COUNT:
            value = 3;
            break;
        case ZPL_MTIME:
        case ZPL_CTIME:
        case ZPL_CRTIME:
        case ZPL_ATIME: {
            uint64_t time[2] = {1791290045, 123};
            if (mode == 13)
                time[0] = 1791290101;
            CHECK(a[i].length == 16);
            memcpy(a[i].data, time, 16);
            continue;
        }
        case ZPL_DACL_ACES: {
            zfs_ace_hdr_t acl[3] = {
                {0, ACE_OWNER, 0x1e019f},
                {0, ACE_GROUP | ACE_IDENTIFIER_GROUP, 0x120088},
                {0, ACE_EVERYONE, 0x120088}};
            if (mode == 14)
                acl[1].z_access_mask |= 2;
            CHECK(a[i].length == sizeof(acl));
            memcpy(a[i].data, acl, sizeof(acl));
            continue;
        }
        default:
            CHECK(a[i].attr == ZPL_PROJID);
        }
        CHECK(a[i].length == 8);
        memcpy(a[i].data, &value, 8);
    }
    return 0;
}
#if !MNS_READER
static int host_clock_gettime(clockid_t clock, struct timespec *out)
{
    CHECK(clock == CLOCK_REALTIME && owned);
    if (tick())
        return -1;
    *out = (struct timespec){1791290045, 123};
    return 0;
}
#define clock_gettime host_clock_gettime
static int mutate(aether_zpl_write_result *out)
{
    CHECK(owned && !handles && !mutations && phase == MNS_KIND - 1);
    if (tick())
        return EIO;
    ++mutations;
    ++phase;
    *out = (aether_zpl_write_result){788, 0, AETHER_ZPL_SYNCED};
    if (mode == 21)
        out->state = AETHER_ZPL_COMMITTED;
    if (mode == 22)
        out->txg = 0;
    return mode == 23 ? EIO : 0;
}
int aether_zpl_create(aether_zpl_view *v, uint64_t d, uint64_t dg,
                      const unsigned char *name, size_t len, uint64_t uid,
                      uint64_t gid, uint64_t sec, uint64_t ns,
                      aether_zpl_node *out, aether_zpl_write_result *r)
{
    CHECK(v == &view && d == 34 && dg == 45 && len == 14 &&
          !memcmp(name, "aether-created", 14) && uid == 1000 && gid == 1000 &&
          sec == 1791290045 && ns == 123);
    int e = mutate(r);
    if (mutations)
        *out = (aether_zpl_node){99, 788, 0, 0100600};
    return e;
}
int aether_zpl_rename(aether_zpl_view *v, uint64_t d, uint64_t dg,
                      const unsigned char *from, size_t fl,
                      const unsigned char *to, size_t tl, uint64_t obj,
                      uint64_t gen, uint64_t sec, uint64_t ns,
                      aether_zpl_write_result *r)
{
    CHECK(v == &view && d == 34 && dg == 45 && fl == 14 && tl == 14 &&
          !memcmp(from, "aether-created", 14) &&
          !memcmp(to, "aether-renamed", 14) && obj == 99 && gen == 788 &&
          sec == 1791290045 && ns == 123);
    return mutate(r);
}
int aether_zpl_remove(aether_zpl_view *v, uint64_t d, uint64_t dg,
                      const unsigned char *name, size_t len, uint64_t obj,
                      uint64_t gen, uint64_t sec, uint64_t ns,
                      aether_zpl_write_result *r)
{
    CHECK(v == &view && d == 34 && dg == 45 && len == 14 &&
          !memcmp(name, "aether-renamed", 14) && obj == 99 && gen == 788 &&
          sec == 1791290045 && ns == 123);
    return mutate(r);
}
#endif
#include "namespace-probe.inc"
int main(int argc, char **argv)
{
    CHECK(argc == 3);
    mode = atoi(argv[1]);
    fault = atoi(argv[2]);
    for (int i = 0; i < ZPL_END; ++i)
        attrs[i] = i;
    phase = MNS_READER ? MNS_KIND : MNS_KIND - 1;
#if MNS_READER
    int error = aether_pool_namespace_recover(&pool);
#else
    uint64_t assigned = 999;
    int error = aether_pool_namespace_write(&pool, &assigned);
    CHECK(assigned == (mutations && mode != 22 ? 788 : 0));
#endif
    CHECK(!owned && !handles && opens == closes && mutations <= 1);
    CHECK((error == 0) == (!mode && !fault));
    if (error) {
        CHECK(observed_count == 6 && observed[0] == 'E');
        uint32_t code = 0;
        for (unsigned i = 0; i < 4; ++i)
            code |= (uint32_t)observed[i + 2] << (8 * i);
        CHECK(code == (uint32_t)error);
    } else
        CHECK(!observed_count && opens == (MNS_READER ? 1 : 2));
    printf("calls=%d\n", calls);
    return 0;
}
