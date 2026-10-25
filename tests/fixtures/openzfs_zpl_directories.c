/* SPDX-License-Identifier: BSD-2-Clause */
/* Namespace/SA/transaction doubles. No disk decoding or durability proof. */
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include "zpl-directories.h"
#define CHECK(c)                                                               \
    do {                                                                       \
        if (!(c)) {                                                            \
            fprintf(stderr, "HOST MUTATION oracle94 line%d\n", __LINE__);      \
            exit(94);                                                          \
        }                                                                      \
    } while (0)
#define B_FALSE 0
#define B_TRUE 1
#define DMU_TX_WAIT 1
#define TXG_WAIT_SUSPEND 1
#define SA_HDL_PRIVATE 2
#define DMU_OT_PLAIN_FILE_CONTENTS 19
#define DMU_OT_SA 44
#define DMU_OT_DIRECTORY_CONTENTS 20
#define DMU_NEW_OBJECT UINT64_MAX
#define ACE_EXECUTE (1U << 11)
#define ACE_DELETE_CHILD (1U << 12)
#define DMU_OBJECT_END UINT64_MAX
#define ZFS_SA_BASE_ATTR_SIZE 176
#define DNODE_MIN_SIZE 512
#define DN_BONUS_SIZE(n) ((n) - 192)
#define IFTODT(m) (((m) >> 12) & 15)
#define ZFS_DIRENT_OBJ(v) ((v) & UINT64_C(0xffffffffffff))
#define ZFS_DIRENT_TYPE(v) ((v) >> 60)
#define ZFS_IMMUTABLE (1ULL << 0)
#define ZFS_APPENDONLY (1ULL << 1)
#define ZFS_READONLY (1ULL << 2)
#define ZFS_XATTR (1ULL << 3)
#define ZFS_INHERIT_ACE (1ULL << 4)
#define ZFS_PROJINHERIT (1ULL << 5)
#define ZFS_ARCHIVE (1ULL << 6)
#define ZFS_AV_MODIFIED (1ULL << 7)
#define ZFS_ACL_TRIVIAL (1ULL << 8)
#define ZFS_ACL_PROTECTED (1ULL << 9)
#define ZFS_PROJID (1ULL << 10)
#define ACE_ACCESS_ALLOWED_ACE_TYPE 0
#define ACE_OWNER 1
#define ACE_GROUP 2
#define ACE_IDENTIFIER_GROUP 4
#define ACE_EVERYONE 8
#define ACE_READ_ATTRIBUTES (1U << 0)
#define ACE_READ_NAMED_ATTRS (1U << 1)
#define ACE_READ_ACL (1U << 2)
#define ACE_SYNCHRONIZE (1U << 3)
#define ACE_READ_DATA (1U << 4)
#define ACE_WRITE_DATA (1U << 5)
#define ACE_APPEND_DATA (1U << 6)
#define ACE_WRITE_ATTRIBUTES (1U << 7)
#define ACE_WRITE_NAMED_ATTRS (1U << 8)
#define ACE_WRITE_ACL (1U << 9)
#define ACE_WRITE_OWNER (1U << 10)
enum {
    ZPL_MODE,
    ZPL_SIZE,
    ZPL_GEN,
    ZPL_UID,
    ZPL_GID,
    ZPL_PARENT,
    ZPL_FLAGS,
    ZPL_ATIME,
    ZPL_MTIME,
    ZPL_CTIME,
    ZPL_CRTIME,
    ZPL_LINKS,
    ZPL_PROJID,
    ZPL_DACL_COUNT,
    ZPL_DACL_ACES,
    ZPL_XATTR,
    ZPL_END
};
typedef struct {
    uint16_t z_type, z_flags;
    uint32_t z_access_mask;
} zfs_ace_hdr_t;
typedef struct {
    int attr;
    void *data;
    size_t length;
} sa_bulk_attr_t;
#define SA_ADD_BULK_ATTR(a, n, id, loc, p, len)                                \
    ((a)[(n)++] = (sa_bulk_attr_t){id, p, len})
typedef struct spa {
    int unused;
} spa_t;
typedef struct {
    int unused;
} objset_t;
typedef struct {
    uint64_t doi_max_offset;
} dmu_object_info_t;
typedef struct {
    int object, active;
} sa_handle_t;
typedef struct {
    int assigned, new_sa, parent_sa, child_sa, zaps, free_hold, netfree;
} dmu_tx_t;
struct aether_zpl_view {
    objset_t *os;
    int *attributes;
    aether_zpl_node root;
};
struct record {
    int exists;
    uint64_t field[ZPL_END], times[4][2];
    zfs_ace_hdr_t acl[3];
    uint64_t extent;
};
struct entry {
    char name[256];
    uint64_t value;
};
static struct record records[100], before[100];
static struct entry entries[3], entries_before[3];
static int attrs[ZPL_END], mode, fail_call, calls, assigned, commits, aborts,
    bound, waits, handles, op;
static objset_t os;
static spa_t spa;
static aether_zpl_view view = {&os, attrs, {34, 45, 3, S_IFDIR | 0755}};
static sa_handle_t handle_slots[3];
static dmu_tx_t tx;
static int tick(void) { return ++calls == fail_call ? EIO : 0; }
static spa_t *dmu_objset_spa(objset_t *s)
{
    CHECK(s == &os);
    return &spa;
}
static int spa_writeable(spa_t *s)
{
    CHECK(s == &spa);
    return mode != 1 && mode != 41;
}
static int aether_zpl_load(aether_zpl_view *v, uint64_t object,
                           aether_zpl_node *out, uint64_t *parent)
{
    CHECK(v == &view);
    if (tick())
        return EIO;
    if (object >= 100 || !records[object].exists)
        return ENOENT;
    struct record *r = &records[object];
    *out = (aether_zpl_node){object, r->field[ZPL_GEN], r->field[ZPL_SIZE],
                             r->field[ZPL_MODE]};
    *parent = r->field[ZPL_PARENT];
    return 0;
}
static int sa_handle_get(objset_t *s, uint64_t object, void *unused, int kind,
                         sa_handle_t **out)
{
    CHECK(s == &os && object < 100 && records[object].exists && !unused &&
          kind == SA_HDL_PRIVATE);
    if (tick())
        return EIO;
    for (unsigned i = 0; i < 3; ++i)
        if (!handle_slots[i].active) {
            handle_slots[i] = (sa_handle_t){(int)object, 1};
            *out = &handle_slots[i];
            ++handles;
            return 0;
        }
    CHECK(0);
    return ENOMEM;
}
static void sa_handle_destroy(sa_handle_t *h)
{
    CHECK(h && h->active && handles > 0);
    h->active = 0;
    --handles;
}
static int sa_lookup(sa_handle_t *h, int id, void *out, size_t length)
{
    CHECK(h->active && length == 8 && (id == ZPL_XATTR || id == ZPL_PROJID));
    if (tick())
        return EIO;
    *(uint64_t *)out = records[h->object].field[id];
    return 0;
}
static void attribute(sa_handle_t *h, sa_bulk_attr_t *a, int write)
{
    CHECK(h->active && a->attr >= 0 && a->attr < ZPL_END);
    struct record *r = &records[h->object];
    void *slot;
    if (a->attr >= ZPL_ATIME && a->attr <= ZPL_CRTIME) {
        CHECK(a->length == 16);
        slot = r->times[a->attr - ZPL_ATIME];
    } else if (a->attr == ZPL_DACL_ACES) {
        CHECK(a->length == sizeof(r->acl));
        slot = r->acl;
    } else {
        CHECK(a->length == 8);
        slot = &r->field[a->attr];
    }
    if (write)
        memcpy(slot, a->data, a->length);
    else
        memcpy(a->data, slot, a->length);
}
static int sa_bulk_lookup(sa_handle_t *h, sa_bulk_attr_t *a, int n)
{
    CHECK(h->active && n == 2);
    if (tick())
        return EIO;
    for (int i = 0; i < n; ++i)
        attribute(h, &a[i], 0);
    return 0;
}
static int sa_bulk_update(sa_handle_t *h, sa_bulk_attr_t *a, int n, dmu_tx_t *t)
{
    CHECK(t == &tx && t->assigned && bound && h->active &&
          (h->object == 34 ? t->parent_sa : t->child_sa));
    if (tick())
        return EIO;
    for (int i = 0; i < n; ++i)
        attribute(h, &a[i], 1);
    return 0;
}
static int sa_update(sa_handle_t *h, int id, const void *data, size_t size,
                     dmu_tx_t *t)
{
    CHECK(t == &tx && t->assigned && bound && h->active &&
          (h->object == 34 ? t->parent_sa : t->child_sa) && id == ZPL_LINKS &&
          size == 8);
    if (tick())
        return EIO;
    records[h->object].field[id] = *(const uint64_t *)data;
    return 0;
}
static int sa_replace_all_by_template(sa_handle_t *h, sa_bulk_attr_t *a, int n,
                                      dmu_tx_t *t)
{
    CHECK(t == &tx && t->assigned && t->new_sa && bound && h->object == 99 &&
          n == 15);
    if (tick())
        return EIO;
    const int order[15] = {ZPL_MODE,   ZPL_SIZE,       ZPL_GEN,      ZPL_UID,
                           ZPL_GID,    ZPL_PARENT,     ZPL_FLAGS,    ZPL_ATIME,
                           ZPL_MTIME,  ZPL_CTIME,      ZPL_CRTIME,   ZPL_LINKS,
                           ZPL_PROJID, ZPL_DACL_COUNT, ZPL_DACL_ACES};
    for (int i = 0; i < n; ++i) {
        CHECK(a[i].attr == order[i]);
        attribute(h, &a[i], 1);
    }
    return 0;
}
static int zap_count(objset_t *s, uint64_t object, uint64_t *count)
{
    CHECK(s == &os && (object == 34 || object == 2));
    if (tick())
        return EIO;
    *count = object == 2 ? (mode == 50 ? 1 : 0)
             : mode == 14
                 ? 4096
                 : !!entries[0].value + !!entries[1].value + !!entries[2].value;
    return 0;
}
static int zap_lookup(objset_t *s, uint64_t object, const char *name, int size,
                      int count, void *out)
{
    CHECK(s == &os && object == 34 && name && size == 8 && count == 1);
    if (tick())
        return EIO;
    for (unsigned i = 0; i < 3; ++i)
        if (entries[i].value && !strcmp(entries[i].name, name)) {
            *(uint64_t *)out = entries[i].value;
            return 0;
        }
    return ENOENT;
}
static int zap_add(objset_t *s, uint64_t object, const char *name, int size,
                   int count, const void *value, dmu_tx_t *t)
{
    CHECK(s == &os && object == 34 && t == &tx && t->assigned && t->zaps &&
          bound && size == 8 && count == 1);
    if (tick())
        return EIO;
    for (unsigned i = 0; i < 3; ++i)
        CHECK(!entries[i].value || strcmp(entries[i].name, name));
    for (unsigned i = 0; i < 3; ++i)
        if (!entries[i].value) {
            strcpy(entries[i].name, name);
            entries[i].value = *(const uint64_t *)value;
            return 0;
        }
    CHECK(0);
    return ENOSPC;
}
static int zap_remove(objset_t *s, uint64_t object, const char *name,
                      dmu_tx_t *t)
{
    CHECK(s == &os && object == 34 && t == &tx && t->assigned && t->zaps &&
          bound);
    if (tick())
        return EIO;
    for (unsigned i = 0; i < 3; ++i)
        if (entries[i].value && !strcmp(entries[i].name, name)) {
            entries[i].value = 0;
            return 0;
        }
    CHECK(0);
    return ENOENT;
}
static dmu_tx_t *dmu_tx_create(objset_t *s)
{
    CHECK(s == &os && !assigned && !commits && !aborts);
    return tick() ? NULL : &tx;
}
static void dmu_tx_hold_sa_create(dmu_tx_t *t, int size)
{
    CHECK(t == &tx && !t->assigned && size > 100 && size < 512);
    t->new_sa = 1;
}
static void dmu_tx_hold_sa(dmu_tx_t *t, sa_handle_t *h, int grow)
{
    CHECK(t == &tx && !t->assigned && h->active && !grow);
    if (h->object == 34)
        t->parent_sa = 1;
    else
        t->child_sa = 1;
}
static void dmu_tx_hold_zap(dmu_tx_t *t, uint64_t object, int add,
                            const char *name)
{
    CHECK(t == &tx && !t->assigned &&
          ((object == 34 && name) ||
           (object == DMU_NEW_OBJECT && !name && add)) &&
          (add == 0 || add == 1));
    ++t->zaps;
}
static void dmu_tx_hold_free(dmu_tx_t *t, uint64_t object, uint64_t offset,
                             uint64_t length)
{
    CHECK(t == &tx && !t->assigned && object == 2 && !offset &&
          length == UINT64_MAX);
    t->free_hold = 1;
}
static void dmu_tx_mark_netfree(dmu_tx_t *t)
{
    CHECK(t == &tx && !t->assigned && t->free_hold);
    t->netfree = 1;
}
static int dmu_tx_assign(dmu_tx_t *t, int flags)
{
    CHECK(t == &tx && !t->assigned && flags == DMU_TX_WAIT && t->parent_sa &&
          t->zaps && (op == 0 ? t->new_sa : t->child_sa) &&
          (op != 2 || (t->free_hold && t->netfree)));
    if (tick())
        return EIO;
    t->assigned = 1;
    ++assigned;
    return 0;
}
static void dmu_tx_abort(dmu_tx_t *t)
{
    CHECK(t == &tx && !t->assigned && !assigned);
    ++aborts;
}
static uint64_t dmu_tx_get_txg(dmu_tx_t *t)
{
    CHECK(t == &tx && t->assigned);
    return tick() ? 0 : 42;
}
static int aether_pool_hooks_bind_transaction(dmu_tx_t *t)
{
    CHECK(t == &tx && t->assigned && !bound);
    if (tick())
        return EIO;
    bound = 1;
    return 0;
}
static uint64_t dmu_object_alloc(objset_t *s, int type, int block, int bonus,
                                 int length, dmu_tx_t *t)
{
    CHECK(s == &os && t == &tx && t->assigned && bound && t->new_sa &&
          type == DMU_OT_PLAIN_FILE_CONTENTS && !block && bonus == DMU_OT_SA &&
          length == 320);
    if (tick())
        return 0;
    CHECK(!records[99].exists);
    records[99].exists = 1;
    return 99;
}
static int dmu_object_info(objset_t *s, uint64_t object, dmu_object_info_t *out)
{
    CHECK(s == &os && object == 2);
    if (tick())
        return EIO;
    out->doi_max_offset = records[object].extent;
    return 0;
}
static int dmu_object_free(objset_t *s, uint64_t object, dmu_tx_t *t)
{
    CHECK(s == &os && object == 2 && t == &tx && t->assigned && t->free_hold &&
          t->netfree && bound);
    for (int i = 0; i < 3; ++i)
        CHECK(!handle_slots[i].active || handle_slots[i].object != 2);
    if (tick())
        return EIO;
    CHECK(records[2].field[ZPL_LINKS] == 0);
    records[2].exists = 0;
    return 0;
}
static void dmu_tx_commit(dmu_tx_t *t)
{
    CHECK(t == &tx && t->assigned && assigned == 1 && !commits && !aborts);
    ++commits;
}
static void *spa_get_dsl(spa_t *s)
{
    CHECK(s == &spa);
    return s;
}
static int txg_wait_synced_flags(void *s, uint64_t target, int flags)
{
    CHECK(s == &spa && target == 42 && flags == TXG_WAIT_SUSPEND &&
          commits == 1);
    ++waits;
    return tick();
}
static uint64_t spa_last_synced_txg(spa_t *s)
{
    CHECK(s == &spa && waits == 1 && commits == 1);
    return tick() ? 41 : 42;
}

static uint64_t zap_create(objset_t *s, int type, int bonus, int length,
                           dmu_tx_t *t)
{
    CHECK(s == &os && type == DMU_OT_DIRECTORY_CONTENTS && bonus == DMU_OT_SA &&
          length == 320 && t == &tx && t->assigned && bound && t->new_sa &&
          t->zaps == 2);
    if (tick())
        return 0;
    CHECK(!records[99].exists);
    records[99].exists = 1;
    return 99;
}
static int zap_destroy(objset_t *s, uint64_t object, dmu_tx_t *t)
{
    return dmu_object_free(s, object, t);
}
#define AETHER_ZPL_ORDERED_WRITE 1
#include "directories.inc"

int main(int argc, char **argv)
{
    CHECK(argc == 4);
    op = atoi(argv[1]);
    mode = atoi(argv[2]);
    fail_call = atoi(argv[3]);
    CHECK(op == 0 || op == 2 || op == 3);
    for (int i = 0; i < ZPL_END; ++i)
        attrs[i] = i;
    records[34].exists = 1;
    records[34].field[ZPL_MODE] = S_IFDIR | 0755;
    records[34].field[ZPL_GEN] = 45;
    records[34].field[ZPL_PARENT] = 34;
    records[34].field[ZPL_LINKS] = op == 2 ? 3 : 2;
    records[34].field[ZPL_SIZE] = op == 2 ? 3 : 2;
    records[2].exists = 1;
    records[2].field[ZPL_MODE] = S_IFDIR | 0700;
    records[2].field[ZPL_GEN] = 47;
    records[2].field[ZPL_PARENT] = 34;
    records[2].field[ZPL_LINKS] = 2;
    records[2].field[ZPL_SIZE] = 2;
    if (op == 2) {
        strcpy(entries[0].name, "new");
        entries[0].value = (UINT64_C(4) << 60) | 2;
    }
    uint64_t dirgen = 45, gen = 47, seconds = 1234, nanos = 5678, uid = 1000;
    const unsigned char *name = (const unsigned char *)"new";
    size_t length = 3;
    switch (mode) {
    case 1:
        break; // readonly checked by shared input
    case 2:
        ++dirgen;
        break;
    case 3:
        ++gen;
        break;
    case 4:
        records[34].field[ZPL_MODE] = S_IFREG | 0600;
        break;
    case 7:
        records[34].field[ZPL_FLAGS] = ZFS_IMMUTABLE;
        break;
    case 10:
        records[34].field[ZPL_FLAGS] = ZFS_INHERIT_ACE;
        break;
    case 11:
        records[34].field[ZPL_FLAGS] = ZFS_PROJINHERIT;
        break;
    case 12:
        records[34].field[ZPL_PROJID] = 1;
        break;
    case 13:
        ++records[34].field[ZPL_SIZE];
        break;
    case 15:
        name = (const unsigned char *)"a/b";
        break;
    case 16:
        name = (const unsigned char *)".";
        length = 1;
        break;
    case 17:
        name = (const unsigned char *)"..";
        length = 2;
        break;
    case 18:
        name = (const unsigned char *)"a\0b";
        break;
    case 19:
        length = 256;
        break;
    case 20:
        length = 0;
        break;
    case 21:
        name = NULL;
        break;
    case 22:
        seconds = UINT64_C(1) << 63;
        break;
    case 23:
        nanos = 1000000000;
        break;
    case 24:
        uid = UINT64_C(1) << 31;
        break;
    case 50:
        records[2].field[ZPL_SIZE] = 3;
        break;
    case 51:
        records[2].field[ZPL_LINKS] = 3;
        break;
    case 52:
        records[2].field[ZPL_PARENT] = 99;
        break;
    case 53:
        records[2].field[ZPL_XATTR] = 1;
        break;
    case 54:
        records[2].field[ZPL_MODE] = S_IFREG | 0600;
        break;
    case 55:
        records[2].field[ZPL_FLAGS] = ZFS_PROJINHERIT;
        break;
    case 56:
        records[34].field[ZPL_LINKS] = UINT64_MAX;
        break;
    case 57:
        records[34].field[ZPL_LINKS] = 2;
        break;
    case 58:
        entries[0].value |= UINT64_C(1) << 48;
        break;
    case 59:
        view.root.object = 2;
        break;
    case 60:
        records[2].field[ZPL_MODE] |= S_ISVTX;
        break;
    case 61:
        records[2].field[ZPL_FLAGS] = ZFS_IMMUTABLE;
        break;
    default:
        CHECK(mode == 0);
        break;
    }
    memcpy(before, records, sizeof(records));
    memcpy(entries_before, entries, sizeof(entries));
    aether_zpl_node created = {0};
    aether_zpl_write_result result = {0};
    int error;
    if (op == 0)
        error = aether_zpl_mkdir(&view, 34, dirgen, name, length, uid, 1000,
                                 seconds, nanos, &created, &result);
    else if (op == 2)
        error = aether_zpl_rmdir(&view, 34, dirgen, name, length, 2, gen,
                                 seconds, nanos, &result);
    else
        error = aether_zpl_directory(&view, mode == 4 ? 34 : 2, gen, &created);
    CHECK(!handles && !result.bytes_staged);
    if (op == 3) {
        CHECK(!assigned && !commits);
        if (!mode && !fail_call)
            CHECK(!error && created.object == 2 && created.generation == 47 &&
                  created.mode == (S_IFDIR | 0700));
        else
            CHECK(error && !created.object && !created.generation &&
                  !created.size && !created.mode);
    } else if (mode || fail_call) {
        CHECK(error);
        if (!assigned)
            CHECK(!commits && !result.state && !result.txg &&
                  !memcmp(before, records, sizeof(records)) &&
                  !memcmp(entries_before, entries, sizeof(entries)));
        else
            CHECK(commits == 1 && result.state == AETHER_ZPL_COMMITTED &&
                  (result.txg == 42 || !result.txg));
    } else {
        CHECK(!error && assigned == 1 && commits == 1 && !aborts && bound &&
              waits == 1 && result.state == AETHER_ZPL_SYNCED &&
              result.txg == 42);
        CHECK(records[34].field[ZPL_SIZE] == (op == 0 ? 3 : 2) &&
              records[34].field[ZPL_LINKS] == (op == 0 ? 3 : 2));
        CHECK(records[34].times[ZPL_MTIME - ZPL_ATIME][0] == 1234 &&
              records[34].times[ZPL_CTIME - ZPL_ATIME][1] == 5678);
        if (op == 0) {
            struct record *r = &records[99];
            CHECK(created.object == 99 && created.generation == 42 &&
                  created.size == 2 && created.mode == (S_IFDIR | 0700));
            CHECK(r->exists && r->field[ZPL_MODE] == (S_IFDIR | 0700) &&
                  r->field[ZPL_SIZE] == 2 && r->field[ZPL_LINKS] == 2 &&
                  r->field[ZPL_PARENT] == 34 && r->field[ZPL_UID] == 1000 &&
                  r->field[ZPL_GID] == 1000);
            CHECK(r->field[ZPL_FLAGS] ==
                      (ZFS_ARCHIVE | ZFS_AV_MODIFIED | ZFS_ACL_TRIVIAL |
                       ZFS_ACL_PROTECTED | ZFS_PROJID) &&
                  !r->field[ZPL_PROJID] && r->field[ZPL_DACL_COUNT] == 3);
            uint32_t common = ACE_READ_ATTRIBUTES | ACE_READ_NAMED_ATTRS |
                              ACE_READ_ACL | ACE_SYNCHRONIZE;
            CHECK(r->acl[0].z_access_mask ==
                  (common | ACE_READ_DATA | ACE_WRITE_DATA | ACE_APPEND_DATA |
                   ACE_EXECUTE | ACE_DELETE_CHILD | ACE_WRITE_ATTRIBUTES |
                   ACE_WRITE_NAMED_ATTRS | ACE_WRITE_ACL | ACE_WRITE_OWNER));
            CHECK(r->acl[1].z_access_mask == common &&
                  r->acl[2].z_access_mask == common &&
                  r->acl[0].z_flags == ACE_OWNER &&
                  r->acl[1].z_flags == (ACE_GROUP | ACE_IDENTIFIER_GROUP) &&
                  r->acl[2].z_flags == ACE_EVERYONE);
            for (unsigned i = 0; i < 4; ++i)
                CHECK(r->times[i][0] == 1234 && r->times[i][1] == 5678);
            CHECK(entries[0].value == ((UINT64_C(4) << 60) | 99) &&
                  !strcmp(entries[0].name, "new"));
        } else
            CHECK(!records[2].exists && !entries[0].value &&
                  !records[2].field[ZPL_LINKS]);
    }
    printf("DIRECTORY op=%d mode=%d fault=%d calls=%d assigned=%d error=%d\n",
           op, mode, fail_call, calls, assigned, error);
    return 0;
}
