/* SPDX-License-Identifier: BSD-2-Clause */
/* Executes the actual oracle and original zpl-read.c with typed host providers.
 * SHA instrumentation compares every original payload byte with the pinned
 * reference; metadata uses a deterministic stream observation, not host SHA2
 * qualification. The target object consumes original OpenZFS SHA2. */
#include "home-recovery-host.h"
#include "home-recovery-probe.h"
#include <stdio.h>

struct fixture_node {
    uint64_t object, value[ZPL_END][2];
    unsigned type;
    zfs_ace_hdr_t acl[3];
};
static struct fixture_node nodes[11];
static unsigned selected, recovered, owns, handles, allocations, hash_calls;
static unsigned object_calls, probe_reads;
static unsigned char *reference;
static spa_t pool;
static objset_t dataset = {0, &pool};
static sa_attr_type_t attributes[ZPL_END];
const void *zfs_attr_table;
static const unsigned char payload[16] = {'A', 'F', '0', '9', '-', 'H',
                                          'O', 'M', 'E', '-', 'W', 'R',
                                          'I', 'T', 'E', '\n'};
static const unsigned char original_digest[32] = {
    0xcc, 0x9b, 0xfd, 0xde, 0xdd, 0x66, 0x4b, 0x9a, 0x53, 0x34, 0x58,
    0x1a, 0xf7, 0x86, 0x51, 0x6d, 0x14, 0x9c, 0x3f, 0xbd, 0x2c, 0x7e,
    0x65, 0x73, 0x59, 0x85, 0xac, 0xf1, 0x7b, 0xce, 0x59, 0x35};

static uint64_t home_object(void) { return selected == 2 ? 210 : 110; }
static uint64_t probe_object(void) { return selected == 2 ? 211 : 111; }
static struct fixture_node *find(uint64_t object)
{
    for (unsigned i = 0; i < (recovered ? 11U : 9U); ++i)
        if (nodes[i].object == object)
            return &nodes[i];
    return NULL;
}
static void stamp(struct fixture_node *n, unsigned kind, uint64_t seconds,
                  uint64_t nanos)
{
    n->value[kind][0] = seconds;
    n->value[kind][1] = nanos;
}
static void initialize(unsigned phase)
{
    recovered = phase;
    object_calls = probe_reads = hash_calls = 0;
    memset(nodes, 0, sizeof(nodes));
    static const uint64_t ids[9] = {1, 2, 3, 4, 32, 33, 34, 35, 36};
    static const unsigned types[9] = {
        DMU_OT_MASTER_NODE,        DMU_OT_PLAIN_FILE_CONTENTS,
        DMU_OT_DIRECTORY_CONTENTS, DMU_OT_PLAIN_FILE_CONTENTS,
        DMU_OT_SA_MASTER_NODE,     DMU_OT_UNLINKED_SET,
        DMU_OT_DIRECTORY_CONTENTS, DMU_OT_SA_ATTR_REGISTRATION,
        DMU_OT_SA_ATTR_LAYOUTS};
    for (unsigned i = 0; i < 11; ++i) {
        struct fixture_node *n = &nodes[i];
        n->object = i < 9 ? ids[i] : i == 9 ? home_object() : probe_object();
        n->type = i < 9    ? types[i]
                  : i == 9 ? DMU_OT_DIRECTORY_CONTENTS
                           : DMU_OT_PLAIN_FILE_CONTENTS;
        n->value[ZPL_GEN][0] = i + 41;
        n->value[ZPL_MODE][0] =
            n->type == DMU_OT_DIRECTORY_CONTENTS ? 040755 : 0100755;
        n->value[ZPL_SIZE][0] = 3;
        n->value[ZPL_PARENT][0] = 34;
        n->value[ZPL_LINKS][0] = n->type == DMU_OT_DIRECTORY_CONTENTS ? 2 : 1;
        n->value[ZPL_DACL_COUNT][0] = 3;
        for (unsigned t = ZPL_ATIME; t <= ZPL_CRTIME; ++t)
            stamp(n, t, 1620802862, 123);
        n->acl[0] = (zfs_ace_hdr_t){0, ACE_OWNER, 0x1e01ff};
        n->acl[1] =
            (zfs_ace_hdr_t){0, ACE_GROUP | ACE_IDENTIFIER_GROUP, 0x1200a9};
        n->acl[2] = (zfs_ace_hdr_t){0, ACE_EVERYONE, 0x1200a9};
    }
    struct fixture_node *root = &nodes[6], *file = &nodes[1];
    root->value[ZPL_FLAGS][0] = UINT64_C(0x840800000144);
    root->value[ZPL_SIZE][0] = phase ? 4 : 3;
    root->value[ZPL_LINKS][0] = phase ? 3 : 2;
    stamp(root, ZPL_CRTIME, 1620802853, 123);
    stamp(root, ZPL_ATIME, 1621447687, 123);
    file->value[ZPL_FLAGS][0] = UINT64_C(0x840800000104);
    file->value[ZPL_SIZE][0] = 780248;
    file->value[ZPL_XATTR][0] = 3;
    stamp(file, ZPL_ATIME, 1621447692, 123);
    nodes[2].value[ZPL_MODE][0] = 041777;
    nodes[2].value[ZPL_PARENT][0] = 2;
    nodes[2].value[ZPL_FLAGS][0] = UINT64_C(0x840800000145);
    nodes[3].value[ZPL_MODE][0] = 0100644;
    nodes[3].value[ZPL_PARENT][0] = 3;
    nodes[3].value[ZPL_SIZE][0] = 37;
    nodes[3].value[ZPL_FLAGS][0] = UINT64_C(0x840800000005);
    if (!phase)
        return;
    for (unsigned t = ZPL_MTIME; t <= ZPL_CTIME; ++t)
        stamp(root, t, 1791290041, 100);
    for (unsigned i = 9; i < 11; ++i) {
        struct fixture_node *n = &nodes[i];
        n->value[ZPL_MODE][0] = i == 9 ? 040700 : 0100600;
        n->value[ZPL_SIZE][0] = i == 9 ? 3 : 16;
        n->value[ZPL_UID][0] = n->value[ZPL_GID][0] = 1000;
        n->value[ZPL_PARENT][0] = i == 9 ? root->object : home_object();
        n->value[ZPL_FLAGS][0] = ZFS_ARCHIVE | ZFS_AV_MODIFIED |
                                 ZFS_ACL_TRIVIAL | ZFS_ACL_PROTECTED |
                                 ZFS_PROJID;
        for (unsigned t = ZPL_ATIME; t <= ZPL_CRTIME; ++t)
            stamp(n, t, 1791290040 + (i == 9 ? 1 : 2), 100);
        stamp(n, ZPL_MTIME, 1791290040 + (i == 9 ? 2 : 3), 100);
        stamp(n, ZPL_CTIME, 1791290040 + (i == 9 ? 2 : 3), 100);
        n->acl[0].z_access_mask = i == 9 ? 0x1e01ff : 0x1e019f;
        n->acl[1].z_access_mask = n->acl[2].z_access_mask = 0x120088;
    }
    if (selected == 1 || selected == 35) {
        uint64_t seconds = selected == 1 ? 1791290040 : 1791290100;
        stamp(root, ZPL_MTIME, seconds, 0);
        stamp(root, ZPL_CTIME, seconds, 0);
        for (unsigned i = 9; i < 11; ++i)
            for (unsigned t = ZPL_ATIME; t <= ZPL_CRTIME; ++t)
                stamp(&nodes[i], t, seconds, 0);
    }
    switch (selected) {
    case 3:
        nodes[9].value[ZPL_MODE][0] = 040755;
        break;
    case 4:
        nodes[10].value[ZPL_UID][0] = 0;
        break;
    case 5:
        nodes[10].value[ZPL_GID][0] = 0;
        break;
    case 6:
        nodes[10].value[ZPL_PARENT][0] = 34;
        break;
    case 7:
        nodes[9].value[ZPL_LINKS][0] = 3;
        break;
    case 8:
        nodes[10].value[ZPL_SIZE][0] = 15;
        break;
    case 9:
        nodes[10].acl[2].z_access_mask ^= 1;
        break;
    case 10:
        nodes[9].value[ZPL_MTIME][1] = 1000000000;
        break;
    case 11:
        nodes[10].value[ZPL_MTIME][0] = 1791290101;
        nodes[10].value[ZPL_CTIME][0] = 1791290101;
        break;
    case 12:
        nodes[10].value[ZPL_CTIME][1] = 99;
        break;
    case 13:
        nodes[10].value[ZPL_CRTIME][0] = 1791290041;
        break;
    case 14:
        root->value[ZPL_LINKS][0] = 2;
        break;
    case 15:
        root->value[ZPL_SIZE][0] = 3;
        break;
    case 16:
        root->value[ZPL_PARENT][0] = 2;
        break;
    case 17:
        root->value[ZPL_MODE][0] = 040700;
        break;
    case 18:
        file->value[ZPL_CRTIME][1] ^= 1;
        break;
    case 19:
        nodes[2].acl[1].z_access_mask ^= 1;
        break;
    case 20:
        root->value[ZPL_ATIME][1] ^= 1;
        break;
    case 21:
        nodes[10].value[ZPL_FLAGS][0] ^= ZFS_ACL_PROTECTED;
        break;
    default:
        break;
    }
}
void *kmem_zalloc(size_t bytes, int flags)
{
    (void)flags;
    if (recovered && selected == 34)
        return NULL;
    void *p = calloc(1, bytes);
    if (p)
        ++allocations;
    return p;
}
void kmem_free(void *p, size_t bytes)
{
    (void)bytes;
    if (p)
        --allocations;
    free(p);
}
int spa_writeable(spa_t *spa) { return spa->writable; }
int dmu_objset_own(const char *name, int type, int read, int decrypted,
                   const void *tag, objset_t **out)
{
    (void)decrypted;
    (void)tag;
    if (strcmp(name, "testpool_zstd/x86_64") || type != DMU_OST_ZFS || !read ||
        owns)
        abort();
    ++owns;
    *out = &dataset;
    return 0;
}
void dmu_objset_disown(objset_t *os, int decrypted, const void *tag)
{
    (void)os;
    (void)decrypted;
    (void)tag;
    if (owns != 1 || handles)
        abort();
    --owns;
}
spa_t *dmu_objset_spa(objset_t *os) { return os->spa; }
int dmu_object_info(objset_t *os, uint64_t object, dmu_object_info_t *out)
{
    (void)os;
    struct fixture_node *n = find(object);
    if (!n)
        return ENOENT;
    *out = (dmu_object_info_t){n->type, DMU_OT_SA};
    return 0;
}
int dmu_object_next(objset_t *os, uint64_t *object, int hole, uint64_t txg)
{
    (void)os;
    (void)hole;
    (void)txg;
    ++object_calls;
    if (recovered && selected == 26 && object_calls > 1)
        return 0;
    uint64_t next = UINT64_MAX;
    for (unsigned i = 0; i < (recovered ? 11U : 9U); ++i) {
        if (recovered && selected == 24 && nodes[i].object == 4)
            continue;
        if (nodes[i].object > *object && nodes[i].object < next)
            next = nodes[i].object;
    }
    if (recovered && selected == 25 && *object < 150 && next > 150)
        next = 150;
    if (next == UINT64_MAX)
        return ESRCH;
    *object = next;
    return 0;
}
int dmu_read(objset_t *os, uint64_t object, uint64_t offset, uint64_t bytes,
             void *out, unsigned flags)
{
    (void)os;
    (void)flags;
    if (recovered && selected == 32)
        return EIO;
    if (object == 2) {
        if (offset + bytes > 780248)
            return EIO;
        memcpy(out, reference + offset, (size_t)bytes);
        if (recovered && selected == 22 && offset <= 500000 &&
            offset + bytes > 500000)
            ((unsigned char *)out)[500000 - offset] ^= 1;
    } else if (object == probe_object()) {
        for (uint64_t i = 0; i < bytes; ++i)
            ((unsigned char *)out)[i] =
                offset + i < 16 ? payload[offset + i] : 0x7f;
        if (recovered && selected == 23 && offset == 0)
            ((unsigned char *)out)[15] ^= 1;
        if (recovered && selected == 27 && ++probe_reads == 1)
            nodes[10].value[ZPL_SIZE][0] = 17;
    } else if (object == 4 && offset == 0 && bytes == 37)
        memset(out, 0x5a, 37);
    else
        return EIO;
    return 0;
}
int zap_lookup(objset_t *os, uint64_t object, const char *name, uint64_t width,
               uint64_t count, void *out)
{
    (void)os;
    if (width != 8 || count != 1)
        abort();
    uint64_t value = 0;
    if (object == 1) {
        if (!strcmp(name, ZPL_VERSION_STR))
            value = 5;
        else if (!strcmp(name, ZFS_ROOT_OBJ))
            value = 34;
        else if (!strcmp(name, ZFS_SA_ATTRS))
            value = 32;
        else if (!strcmp(name, ZFS_UNLINKED_SET))
            value = 33;
    } else if (object == 32) {
        if (!strcmp(name, "REGISTRY"))
            value = 35;
        else if (!strcmp(name, "LAYOUTS"))
            value = 36;
    } else if (object == 34) {
        if (!strcmp(name, "zstd"))
            value = (UINT64_C(8) << 60) | 2;
        else if (recovered && !strcmp(name, "home"))
            value = (UINT64_C(4) << 60) | (selected == 28 ? 34 : home_object());
    } else if (object == 3 && !strcmp(name, "security.selinux"))
        value = (UINT64_C(8) << 60) | 4;
    else if (recovered && object == home_object() && !strcmp(name, "probe"))
        value = (UINT64_C(8) << 60) | probe_object();
    if (recovered && selected == 29 && !strcmp(name, "probe"))
        return EIO;
    if (!value)
        return ENOENT;
    memcpy(out, &value, 8);
    return 0;
}
int zap_count(objset_t *os, uint64_t object, uint64_t *out)
{
    (void)os;
    *out = object == 34                             ? (recovered ? 2 : 1)
           : object == 3 || object == home_object() ? 1
           : object == 33                           ? 0
           : object == 1                            ? 7
                                                    : 2;
    if (recovered && selected == 30 && object == 34)
        ++*out;
    return 0;
}
int zfs_get_zplprop(objset_t *os, int property, uint64_t *out)
{
    (void)os;
    (void)property;
    *out = 0;
    return 0;
}
int sa_handle_get(objset_t *os, uint64_t object, void *user, int kind,
                  sa_handle_t **out)
{
    (void)os;
    (void)user;
    (void)kind;
    if (!find(object))
        return ENOENT;
    *out = malloc(sizeof(**out));
    if (!*out)
        return ENOMEM;
    (*out)->object = object;
    ++handles;
    return 0;
}
void sa_handle_destroy(sa_handle_t *h)
{
    --handles;
    free(h);
}
int sa_lookup(sa_handle_t *h, sa_attr_type_t attribute, void *out,
              uint32_t length)
{
    struct fixture_node *n = find(h->object);
    if (!n || attribute >= ZPL_END)
        return EIO;
    if (recovered && selected == 31 && h->object == probe_object())
        return EIO;
    if (attribute == ZPL_DACL_ACES) {
        if (length != sizeof(n->acl))
            return EIO;
        memcpy(out, n->acl, length);
    } else {
        if (length > sizeof(n->value[attribute]))
            return EIO;
        memcpy(out, n->value[attribute], length);
    }
    return 0;
}
int sa_bulk_lookup(sa_handle_t *h, sa_bulk_attr_t *attrs, int count)
{
    for (int i = 0; i < count; ++i) {
        int e = sa_lookup(h, attrs[i].attribute, attrs[i].data,
                          (uint32_t)attrs[i].length);
        if (e)
            return e;
    }
    return 0;
}
int sa_size(sa_handle_t *h, sa_attr_type_t attr, int *length)
{
    (void)h;
    if (attr != ZPL_DACL_ACES)
        return EIO;
    *length = recovered && selected == 33 ? 1025 : 24;
    return 0;
}
int sa_setup(objset_t *os, uint64_t object, const void *table, int count,
             sa_attr_type_t **out)
{
    (void)os;
    (void)table;
    if (object != 32 || count != ZPL_END)
        abort();
    for (unsigned i = 0; i < ZPL_END; ++i)
        attributes[i] = i;
    *out = attributes;
    return 0;
}
void SHA2Init(unsigned algorithm, SHA2_CTX *h)
{
    if (algorithm != SHA256)
        abort();
    *h = (SHA2_CTX){0, UINT64_C(14695981039346656037), ++hash_calls, 1};
}
void SHA2Update(SHA2_CTX *h, const void *data, size_t length)
{
    const unsigned char *b = data;
    if (h->kind == 1 && (h->bytes + length > 780248 ||
                         memcmp(data, reference + h->bytes, length)))
        h->exact = 0;
    for (size_t i = 0; i < length; ++i)
        h->observed = (h->observed ^ b[i]) * UINT64_C(1099511628211);
    h->bytes += length;
}
void SHA2Final(unsigned char *out, SHA2_CTX *h)
{
    if (h->kind == 1) {
        if (h->exact && h->bytes == 780248)
            memcpy(out, original_digest, 32);
        else
            memset(out, 0, 32);
    } else
        for (unsigned i = 0; i < 32; ++i)
            out[i] = (unsigned char)(h->observed >> (8 * (i % 8)));
}
int main(int argc, char **argv)
{
    if (argc != 3)
        return 64;
    selected = (unsigned)strtoul(argv[1], NULL, 10);
    reference = malloc(780248);
    FILE *f = fopen(argv[2], "rb");
    if (!reference || !f || fread(reference, 1, 780248, f) != 780248 ||
        fgetc(f) != EOF)
        return 65;
    fclose(f);
    unsigned char baseline[32] = {0}, after[32] = {0};
    initialize(0);
    int error =
        aether_home_readback(&pool, 0, 1791290040, 1791290100, baseline);
    if (error || owns || handles || allocations) {
        fprintf(stderr, "HOME_BASELINE case=%u error=%d\n", selected, error);
        return 1;
    }
    initialize(1);
    pool.writable = selected == 36;
    error = aether_home_readback(&pool, 1, 1791290040,
                                 selected == 37 ? 1791290040 : 1791290100,
                                 selected == 38 ? NULL : after);
    int valid = selected < 3;
    int observed = error == 0 && !memcmp(baseline, after, 32);
    if (observed != valid || owns || handles || allocations) {
        fprintf(stderr, "HOME_RECOVERY_ORACLE case=%u error=%d preserved=%d\n",
                selected, error, !memcmp(baseline, after, 32));
        return 1;
    }
    free(reference);
    printf("home recovery case %u passed\n", selected);
    return 0;
}
