/* SPDX-License-Identifier: BSD-2-Clause */
/* Faulting API/metadata model for the actual independent hierarchy verifier. */
#include "zpl-mutate.h"
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#define CHECK(c)                                                               \
    do {                                                                       \
        if (!(c)) {                                                            \
            fprintf(stderr, "DIRECTORY ORACLE96 line%d\n", __LINE__);          \
            exit(96);                                                          \
        }                                                                      \
    } while (0)
#define B_FALSE 0
#define SA_HDL_PRIVATE 2
#define ZFS_ARCHIVE 1
#define ZFS_AV_MODIFIED 2
#define ZFS_ACL_TRIVIAL 4
#define ZFS_ACL_PROTECTED 8
#define ZFS_PROJID 16
#define ACE_OWNER 1
#define ACE_GROUP 2
#define ACE_IDENTIFIER_GROUP 4
#define ACE_EVERYONE 8
#define DIR_FIRST                                                              \
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
#define DIR_SECOND                                                             \
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b856"
#define MNS_READER 1
#define DIR_EMPTY 0
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
    uint64_t object;
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
#define SA_ADD_BULK_ATTR(a, n, id, loc, p, len)                                \
    ((a)[(n)++] = (sa_bulk_attr_t){id, p, len})
struct aether_zpl_view {
    void *os;
    int *attributes;
};
#ifndef TEST_TIME
#define TEST_TIME 1791290040
#endif
static int attrs[ZPL_END], phase, mode, fault, calls, owned, handles,
    original_checked;
static spa_t pool;
static aether_zpl_view view = {(void *)1, attrs};
static sa_handle_t handle;
static int tick(void) { return ++calls == fault ? EIO : 0; }
static int spa_writeable(spa_t *p)
{
    CHECK(p == &pool);
    return 0;
}
int aether_zpl_open(spa_t *p, const char *name, aether_zpl_view **out)
{
    CHECK(p == &pool && name && !strcmp(name, "testpool_zstd/x86_64") && out &&
          !*out && !owned);
    if (tick())
        return EIO;
    owned = 1;
    *out = &view;
    return 0;
}
void aether_zpl_close(aether_zpl_view **out)
{
    if (out && *out) {
        CHECK(owned && !handles);
        owned = 0;
        *out = NULL;
    }
}
int aether_zpl_root(aether_zpl_view *v, aether_zpl_node *out)
{
    CHECK(v == &view && owned);
    if (tick())
        return EIO;
    *out = (aether_zpl_node){34, 45,
                             phase == 2   ? 5
                             : phase == 1 ? 4
                                          : 3,
                             040755};
    if (mode == 1)
        ++out->generation;
    if (mode == 2)
        ++out->size;
    return 0;
}
int aether_zpl_lookup(aether_zpl_view *v, uint64_t parent, uint64_t generation,
                      const unsigned char *name, size_t length,
                      aether_zpl_node *out)
{
    CHECK(v == &view && owned && length == strlen((const char *)name));
    if (tick())
        return EIO;
    if (parent == 34) {
        CHECK(generation == 45);
        if (phase && !strcmp((const char *)name, "files")) {
            *out = (aether_zpl_node){99, 788, phase == 2 ? 3 : 2, 040700};
            if (mode == 5)
                ++out->size;
            if (mode == 6)
                out->mode = 0100600;
            if (mode == 7)
                out->generation = 782;
            return 0;
        }
        if (phase == 2 && !strcmp((const char *)name, "state")) {
            *out = (aether_zpl_node){mode == 21 ? 99 : 100, 789, 2, 040700};
            return 0;
        }
    } else if (parent == 99) {
        CHECK(generation == 788);
        if (phase == 2 && !strcmp((const char *)name, DIR_SECOND)) {
            *out = (aether_zpl_node){101, 790, 4096, 0100600};
            return 0;
        }
    } else {
        CHECK(parent == 100 && generation == 789);
        if (mode == 16 && !strcmp((const char *)name, "packages")) {
            *out = (aether_zpl_node){102, 791, 2, 040700};
            return 0;
        }
    }
    return ENOENT;
}
int aether_zpl_read(aether_zpl_view *v, uint64_t object, uint64_t generation,
                    uint64_t offset, void *out, size_t length, size_t *count)
{
    CHECK(v == &view && owned && object == 101 && generation == 790 &&
          offset <= 4096);
    if (tick())
        return EIO;
    *count = offset == 4096 ? (mode == 11 ? 1 : 0) : length;
    for (size_t i = 0; i < *count; ++i)
        ((unsigned char *)out)[i] = (unsigned char)(71 + offset + i);
    if (mode == 10 && offset == 4032)
        ((unsigned char *)out)[length - 1] ^= 1;
    return 0;
}
static int namespace_original(aether_zpl_view *v)
{
    CHECK(v == &view && owned);
    ++original_checked;
    return tick() || mode == 22 ? EIO : 0;
}
static int namespace_error(unsigned char stage, int error)
{
    CHECK(stage && error);
    return error;
}
static int zap_count(void *os, uint64_t object, uint64_t *count)
{
    CHECK(os == view.os && owned);
    if (tick())
        return EIO;
    *count = object == 34   ? (phase == 2   ? 3
                               : phase == 1 ? 2
                                            : 1)
             : object == 99 ? (phase == 2 ? 1 : 0)
                            : 0;
    if (mode == 15)
        ++*count;
    return 0;
}
static int dmu_object_next(void *os, uint64_t *object, int holes, uint64_t txg)
{
    CHECK(os == view.os && owned && !holes && !txg);
    if (tick())
        return EIO;
    static const uint64_t objects[] = {1,  2,  3,  4,   32,  33, 34,
                                       35, 36, 99, 100, 101, 102};
    unsigned length = 9 +
                      (phase == 2   ? 3
                       : phase == 1 ? 1
                                    : 0) +
                      (mode == 12 ? 1 : 0);
    if (mode == 13)
        --length;
    if (mode == 14 && *object == 2)
        return 0;
    for (unsigned i = 0; i < length; ++i)
        if (objects[i] > *object) {
            *object = objects[i];
            return 0;
        }
    return ESRCH;
}
static int sa_handle_get(void *os, uint64_t object, void *tag, int kind,
                         sa_handle_t **out)
{
    CHECK(os == view.os && owned && !handles && !tag && kind == SA_HDL_PRIVATE);
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
static int sa_bulk_lookup(sa_handle_t *h, sa_bulk_attr_t *attrs, int n)
{
    CHECK(h == &handle && handles == 1 && (n == 8 || n == 13));
    if (tick())
        return EIO;
    uint64_t object = h->object;
    int root = object == 34;
    int directory = object != 101;
    for (int i = 0; i < n; ++i) {
        sa_bulk_attr_t *a = &attrs[i];
        if (a->attr == ZPL_DACL_ACES) {
            zfs_ace_hdr_t acl[3] = {
                {0, ACE_OWNER, directory ? 0x1e01ff : 0x1e019f},
                {0, ACE_GROUP | ACE_IDENTIFIER_GROUP, 0x120088},
                {0, ACE_EVERYONE, 0x120088}};
            CHECK(a->length == sizeof(acl));
            if (mode == 9)
                acl[0].z_access_mask ^= 1;
            memcpy(a->data, acl, sizeof(acl));
            continue;
        }
        if (a->length == 16) {
            uint64_t time[2] = {TEST_TIME, 123};
            if (a->attr == ZPL_CTIME || a->attr == ZPL_MTIME)
                time[0] += 3;
            if (mode == 17)
                time[1] = 1000000000;
            if (mode == 20 && a->attr == ZPL_ATIME)
                time[1]++;
            memcpy(a->data, time, 16);
            continue;
        }
        CHECK(a->length == 8);
        uint64_t value = 0;
        switch (a->attr) {
        case ZPL_FLAGS:
            value =
                ZFS_ARCHIVE | ZFS_AV_MODIFIED |
                (root ? 0 : ZFS_ACL_TRIVIAL | ZFS_ACL_PROTECTED | ZFS_PROJID);
            if (mode == 18)
                value = 0;
            break;
        case ZPL_LINKS:
            value = root ? (phase == 2 ? 4 : 3) : directory ? 2 : 1;
            if (mode == 3)
                ++value;
            break;
        case ZPL_PARENT:
            value = object == 101 ? 99 : 34;
            if (mode == 4)
                value = 999;
            break;
        case ZPL_UID:
        case ZPL_GID:
            value = root ? 0 : 1000;
            if (mode == 8)
                ++value;
            break;
        case ZPL_SIZE:
            value = root            ? (phase == 2 ? 5 : 4)
                    : object == 99  ? (phase == 2 ? 3 : 2)
                    : object == 100 ? 2
                                    : 4096;
            break;
        case ZPL_PROJID:
            value = mode == 19;
            break;
        case ZPL_DACL_COUNT:
            value = 3;
            break;
        default:
            CHECK(0);
        }
        memcpy(a->data, &value, 8);
    }
    return 0;
}
#include "directory-oracle.inc"
int main(int argc, char **argv)
{
    CHECK(argc == 4);
    phase = atoi(argv[1]);
    mode = atoi(argv[2]);
    fault = atoi(argv[3]);
    CHECK(phase >= 0 && phase <= 2);
    for (int i = 0; i < ZPL_END; ++i)
        attrs[i] = i;
    owned = 1;
    int error = directory_check(&view, (unsigned)phase);
    CHECK(!handles);
    if (mode || fault)
        CHECK(error);
    else
        CHECK(!error && original_checked == 1);
    printf("DIRECTORY ORACLE phase=%d mode=%d fault=%d calls=%d error=%d\n",
           phase, mode, fault, calls, error);
    return 0;
}
