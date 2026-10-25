/* SPDX-License-Identifier: BSD-2-Clause */
/* API doubles, NOT an on-disk filesystem or original SA/ZAP decoder. */
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include "zpl-read.h"

#define CHECK(c)                                                               \
    do {                                                                       \
        if (!(c)) {                                                            \
            fprintf(stderr, "HOST ZPL oracle92 line%d\n", __LINE__);           \
            exit(92);                                                          \
        }                                                                      \
    } while (0)
enum {
    B_FALSE,
    B_TRUE,
    KM_NOSLEEP = 17,
    DMU_OST_ZFS = 2,
    DMU_OT_MASTER_NODE = 21,
    DMU_OT_SA_MASTER_NODE = 22,
    DMU_OT_SA = 23,
    DMU_OT_DIRECTORY_CONTENTS = 24,
    DMU_OT_PLAIN_FILE_CONTENTS = 25,
    SA_HDL_PRIVATE = 2,
    DMU_READ_NO_PREFETCH = 1,
    ZPL_END = 22,
    ZPL_MODE = 5,
    ZPL_GEN = 4,
    ZPL_SIZE = 6,
    ZPL_LINKS = 8,
    ZPL_PARENT = 7,
    ZPL_FLAGS = 11,
    ZPL_VERSION_SA = 5,
    ZFS_CASE_SENSITIVE = 0,
    ZFS_PROP_NORMALIZE = 10,
    ZFS_PROP_CASE = 11,
    ZFS_PROP_UTF8ONLY = 12,
    MASTER_NODE_OBJ = 1
};
#define ZFS_XATTR 1
#define ZPL_VERSION_STR "VERSION"
#define ZFS_SA_ATTRS "SA_ATTRS"
#define ZFS_ROOT_OBJ "ROOT"
#define ZFS_DIRENT_OBJ(e) ((e) & UINT64_C(0xffffffffffff))
#define ZFS_DIRENT_TYPE(e) ((e) >> 60)
#define IFTODT(m) (((m) & S_IFMT) >> 12)
typedef struct spa {
    int writable;
} spa_t;
typedef struct objset {
    int os_encrypted;
} objset_t;
typedef int sa_attr_type_t;
typedef int sa_attr_reg_t;
typedef struct {
    int doi_type, doi_bonus_type;
} dmu_object_info_t;
typedef struct {
    uint64_t object;
} sa_handle_t;
typedef struct {
    int attr;
    void *value;
    size_t bytes;
} sa_bulk_attr_t;
#define SA_ADD_BULK_ATTR(a, n, id, locator, data, length)                      \
    ((a)[(n)++] = (sa_bulk_attr_t){id, data, length})
static const sa_attr_reg_t zfs_attr_table[ZPL_END + 1] = {0};
static sa_attr_type_t mapping[ZPL_END];
static spa_t pool, other_pool;
static objset_t dataset;
static sa_handle_t handle;
static int allocated, owned, handles, reads, step, fault, foreign;
static const void *owner;
static uint64_t version = 5, norm, sense, utf8, sa_object = 2, root_object = 3;
static uint64_t entry;
static struct inode {
    int type, bonus;
    uint64_t mode, gen, size, links, parent, flags;
} nodes[6];
static int fail(void) { return ++step == fault ? EIO : 0; }
static int spa_writeable(spa_t *p) { return p->writable; }
static void *kmem_zalloc(size_t bytes, int flags)
{
    CHECK(flags == KM_NOSLEEP);
    if (fault == -1)
        return NULL;
    ++allocated;
    return calloc(1, bytes);
}
static void kmem_free(void *p, size_t bytes)
{
    CHECK(allocated == 1 && bytes && !owned && !handles);
    --allocated;
    free(p);
}
static int dmu_objset_own(const char *name, int type, int ro, int decrypt,
                          const void *tag, objset_t **out)
{
    CHECK(!strcmp(name, "test/files") && type == DMU_OST_ZFS && ro == B_TRUE &&
          decrypt == B_FALSE && tag && !owned);
    *out = &dataset; /* Upstream may set osp then fail own_impl's type check. */
    int error = fail();
    if (!error) {
        owned = 1;
        owner = tag;
    }
    return error;
}
static void dmu_objset_disown(objset_t *os, int decrypt, const void *tag)
{
    CHECK(os == &dataset && owned == 1 && !handles && decrypt == B_FALSE &&
          tag == owner);
    --owned;
}
static spa_t *dmu_objset_spa(objset_t *os)
{
    CHECK(os == &dataset && owned);
    return foreign ? &other_pool : &pool;
}
static int dmu_object_info(objset_t *os, uint64_t object,
                           dmu_object_info_t *out)
{
    CHECK(os == &dataset && owned);
    int error = fail();
    if (error)
        return error;
    if (object >= 6)
        return ENOENT;
    *out = (dmu_object_info_t){nodes[object].type, nodes[object].bonus};
    return 0;
}
static int zap_lookup(objset_t *os, uint64_t object, const char *name,
                      int width, int count, uint64_t *out)
{
    CHECK(os == &dataset && owned && width == 8 && count == 1);
    int error = fail();
    if (error)
        return error;
    if (object == 1) {
        if (!strcmp(name, "VERSION"))
            *out = version;
        else if (!strcmp(name, "SA_ATTRS"))
            *out = sa_object;
        else {
            CHECK(!strcmp(name, "ROOT"));
            *out = root_object;
        }
    } else {
        CHECK(object == 3);
        if (!strcmp(name, "absent"))
            return ENOENT;
        CHECK(!strcmp(name, "file") || !strcmp(name, "child") ||
              strlen(name) == 255);
        *out = entry;
    }
    return 0;
}
static int zfs_get_zplprop(objset_t *os, int prop, uint64_t *out)
{
    CHECK(os == &dataset && owned);
    int error = fail();
    if (error)
        return error;
    CHECK(prop >= 10 && prop <= 12);
    *out = prop == 10 ? norm : prop == 11 ? sense : utf8;
    return 0;
}
static int sa_setup(objset_t *os, uint64_t object, const sa_attr_reg_t *table,
                    int n, sa_attr_type_t **out)
{
    CHECK(os == &dataset && owned && object == 2 && table == zfs_attr_table &&
          n == ZPL_END);
    int error = fail();
    if (error)
        return error;
    for (int i = 0; i < ZPL_END; ++i)
        mapping[i] = 19 + i * 7;
    *out = mapping;
    return 0;
}
static int sa_handle_get(objset_t *os, uint64_t object, void *user, int kind,
                         sa_handle_t **out)
{
    CHECK(os == &dataset && owned && !handles && !user &&
          kind == SA_HDL_PRIVATE);
    int error = fail();
    if (error)
        return error;
    CHECK(object < 6);
    handles = 1;
    handle.object = object;
    *out = &handle;
    return 0;
}
static void sa_handle_destroy(sa_handle_t *p)
{
    CHECK(p == &handle && handles == 1);
    --handles;
}
static int sa_bulk_lookup(sa_handle_t *p, sa_bulk_attr_t *attrs, int n)
{
    CHECK(p == &handle && handles == 1 && n == 6);
    int error = fail();
    if (error)
        return error;
    struct inode *node = &nodes[p->object];
    for (int i = 0; i < n; ++i) {
        CHECK(attrs[i].bytes == 8);
        uint64_t value = 0;
        int id = attrs[i].attr;
        if (id == mapping[ZPL_MODE])
            value = node->mode;
        else if (id == mapping[ZPL_GEN])
            value = node->gen;
        else if (id == mapping[ZPL_SIZE])
            value = node->size;
        else if (id == mapping[ZPL_LINKS])
            value = node->links;
        else if (id == mapping[ZPL_PARENT])
            value = node->parent;
        else {
            CHECK(id == mapping[ZPL_FLAGS]);
            value = node->flags;
        }
        memcpy(attrs[i].value, &value, 8);
    }
    return 0;
}
static int dmu_read(objset_t *os, uint64_t object, uint64_t offset, size_t n,
                    void *buffer, int flags)
{
    CHECK(os == &dataset && owned && !handles && object == 4 && offset <= 6 &&
          n <= 6 - offset && flags == DMU_READ_NO_PREFETCH);
    ++reads;
    memset(buffer, 0xed, n); /* Even a failed underlying read may copy bytes. */
    int error = fail();
    if (!error)
        memcpy(buffer, &"abcdef"[offset], n);
    return error;
}

#include "zpl-adapter.inc"

static void setup(void)
{
    nodes[1].type = DMU_OT_MASTER_NODE;
    nodes[2].type = DMU_OT_SA_MASTER_NODE;
    nodes[3] = (struct inode){
        DMU_OT_DIRECTORY_CONTENTS, DMU_OT_SA, S_IFDIR | 0755, 7, 3, 2, 3, 0};
    nodes[4] = (struct inode){
        DMU_OT_PLAIN_FILE_CONTENTS, DMU_OT_SA, S_IFREG | 0644, 8, 6, 1, 3, 0};
    nodes[5] = (struct inode){
        DMU_OT_DIRECTORY_CONTENTS, DMU_OT_SA, S_IFDIR | 0755, 9, 2, 2, 3, 0};
    entry = (UINT64_C(8) << 60) | 4;
}
static int zero(const void *p, size_t n)
{
    const unsigned char *bytes = p;
    for (size_t i = 0; i < n; ++i)
        if (bytes[i])
            return 0;
    return 1;
}
static void open_case(int mode)
{
    int expected = 0;
    if (mode >= 100 && mode < 113) {
        fault = mode - 99;
        expected = EIO;
    }
    switch (mode) {
    case 1:
        pool.writable = 1;
        expected = EROFS;
        break;
    case 2:
        fault = -1;
        expected = ENOMEM;
        break;
    case 3:
        foreign = 1;
        expected = EXDEV;
        break;
    case 4:
        dataset.os_encrypted = 1;
        expected = ENOTSUP;
        break;
    case 5:
        nodes[1].type = 0;
        expected = EIO;
        break;
    case 6:
        version = 4;
        expected = ENOTSUP;
        break;
    case 7:
        version = 6;
        expected = ENOTSUP;
        break;
    case 8:
        norm = 1;
        expected = ENOTSUP;
        break;
    case 9:
        sense = 1;
        expected = ENOTSUP;
        break;
    case 10:
        utf8 = 1;
        expected = ENOTSUP;
        break;
    case 11:
        sa_object = 0;
        expected = EIO;
        break;
    case 12:
        nodes[2].type = 0;
        expected = EIO;
        break;
    case 13:
        root_object = 0;
        expected = EIO;
        break;
    case 14:
        root_object = 4;
        expected = EIO;
        break;
    case 15:
        nodes[3].parent = 5;
        expected = EIO;
        break;
    case 16:
        nodes[3].gen = 0;
        expected = EIO;
        break;
    case 17:
        nodes[3].links = 0;
        expected = ENOENT;
        break;
    case 18:
        nodes[3].bonus = 0;
        expected = ENOTSUP;
        break;
    case 19:
        nodes[3].flags = ZFS_XATTR;
        expected = ENOTSUP;
        break;
    case 20:
        nodes[3].mode = S_IFREG;
        expected = EIO;
        break;
    }
    aether_zpl_view *view = (void *)(uintptr_t)1;
    CHECK(aether_zpl_open(&pool, "test/files", &view) == expected);
    CHECK((view != NULL) == !expected);
    if (view) {
        aether_zpl_node root;
        CHECK(aether_zpl_root(view, &root) == 0 && root.object == 3 &&
              root.generation == 7);
    }
    aether_zpl_close(&view);
    aether_zpl_close(&view);
}
static void lookup_case(int mode, aether_zpl_view *view)
{
    aether_zpl_node out;
    memset(&out, 0xaa, sizeof(out));
    unsigned char name[256];
    memset(name, 'x', sizeof(name));
    memcpy(name, "file", 4);
    size_t length = 4;
    uint64_t directory = 3, generation = 7;
    int expected = 0;
    if (mode >= 200 && mode < 207) {
        fault = mode - 199;
        expected = EIO;
    }
    switch (mode) {
    case 30:
        generation = 6;
        expected = ESTALE;
        break;
    case 31:
        directory = 4;
        generation = 8;
        expected = ENOTDIR;
        break;
    case 32:
        memcpy(name, "absent", 6);
        length = 6;
        expected = ENOENT;
        break;
    case 33:
        length = 0;
        expected = EINVAL;
        break;
    case 34:
        length = 256;
        expected = EINVAL;
        break;
    case 35:
        memcpy(name, ".", 1);
        length = 1;
        expected = EINVAL;
        break;
    case 36:
        memcpy(name, "..", 2);
        length = 2;
        expected = EINVAL;
        break;
    case 37:
        name[2] = '/';
        expected = EINVAL;
        break;
    case 38:
        name[2] = 0;
        expected = EINVAL;
        break;
    case 39:
        memset(name, 'x', 255);
        length = 255;
        break;
    case 40:
        entry |= UINT64_C(1) << 48;
        expected = EIO;
        break;
    case 41:
        entry = UINT64_C(8) << 60;
        expected = EIO;
        break;
    case 42:
        entry = (UINT64_C(4) << 60) | 4;
        expected = EIO;
        break;
    case 43:
        nodes[4].links = 0;
        expected = ENOENT;
        break;
    case 44:
        nodes[4].mode = S_IFLNK;
        expected = ENOTSUP;
        break;
    case 45:
        nodes[4].bonus = 0;
        expected = ENOTSUP;
        break;
    case 46:
        nodes[4].type = DMU_OT_DIRECTORY_CONTENTS;
        expected = EIO;
        break;
    case 47:
        entry = (UINT64_C(4) << 60) | 5;
        break;
    case 48:
        entry = (UINT64_C(4) << 60) | 5;
        nodes[5].parent = 4;
        expected = EIO;
        break;
    }
    CHECK(aether_zpl_lookup(view, directory, generation, name, length, &out) ==
          expected);
    if (expected)
        CHECK(zero(&out, sizeof(out)));
    else
        CHECK(out.object == ((mode == 47) ? 5 : 4) &&
              out.generation == ((mode == 47) ? 9 : 8));
    CHECK(!handles);
}
static void read_case(int mode, aether_zpl_view *view)
{
    unsigned char bytes[4098];
    memset(bytes, 0xaa, sizeof(bytes));
    size_t length = 4, count = 99, expected_count = 4;
    uint64_t offset = 1, object = 4, generation = 8;
    int expected = 0;
    if (mode >= 300 && mode < 304) {
        fault = mode - 299;
        expected = EIO;
    }
    switch (mode) {
    case 51:
        offset = 4;
        expected_count = 2;
        break;
    case 52:
        offset = 6;
        expected_count = 0;
        break;
    case 53:
        offset = 100;
        expected_count = 0;
        break;
    case 54:
        length = 0;
        expected_count = 0;
        break;
    case 55:
        length = 4096;
        offset = 0;
        expected_count = 6;
        break;
    case 56:
        offset = UINT64_MAX - 1;
        expected = EINVAL;
        break;
    case 57:
        generation = 7;
        expected = ESTALE;
        break;
    case 58:
        object = 3;
        generation = 7;
        expected = EISDIR;
        break;
    case 59:
        nodes[4].links = 0;
        expected = ENOENT;
        break;
    case 60:
        nodes[4].gen = 9;
        expected = ESTALE;
        break;
    }
    CHECK(aether_zpl_read(view, object, generation, offset, bytes + 1, length,
                          &count) == expected);
    CHECK(bytes[0] == 0xaa && bytes[length + 1] == 0xaa);
    if (expected)
        CHECK(!count && zero(bytes + 1, length));
    else {
        CHECK(count == expected_count);
        if (count)
            CHECK(!memcmp(bytes + 1, &"abcdef"[offset], count));
        CHECK(zero(bytes + 1 + count, length - count));
    }
    if (!expected && !count)
        CHECK(!reads);
    CHECK(!handles);
}
int main(int argc, char **argv)
{
    CHECK(argc == 2);
    int mode = atoi(argv[1]);
    setup();
    if (mode < 21 || (mode >= 100 && mode < 113))
        open_case(mode);
    else {
        aether_zpl_view *view = NULL;
        CHECK(!aether_zpl_open(&pool, "test/files", &view));
        step = 0;
        if ((mode >= 30 && mode < 50) || (mode >= 200 && mode < 207))
            lookup_case(mode, view);
        else if ((mode >= 50 && mode <= 60) || (mode >= 300 && mode < 304))
            read_case(mode, view);
        else if (mode == 70) {
            aether_zpl_node out;
            nodes[3].gen++;
            CHECK(aether_zpl_root(view, &out) == ESTALE &&
                  zero(&out, sizeof(out)));
        } else if (mode == 71) {
            aether_zpl_node out;
            nodes[3].parent = 5;
            CHECK(aether_zpl_root(view, &out) == EIO &&
                  zero(&out, sizeof(out)));
        } else {
            size_t n = 77;
            CHECK(aether_zpl_read(view, 4, 8, 0, NULL, 0, &n) == 0 && !n);
            CHECK(aether_zpl_read(view, 4, 8, 0, NULL, 1, &n) == EINVAL && !n);
            CHECK(aether_zpl_read(view, 4, 8, 0, NULL, 4097, &n) == EINVAL &&
                  !n);
            CHECK(aether_zpl_read(view, 4, 8, 0, NULL, 0, NULL) == EINVAL);
        }
        aether_zpl_close(&view);
    }
    CHECK(!allocated && !owned && !handles);
    return 0;
}
