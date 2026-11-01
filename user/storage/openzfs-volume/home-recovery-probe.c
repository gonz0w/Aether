/* SPDX-License-Identifier: BSD-2-Clause */
/* Fixed independent AF09 reader. Original OpenZFS owns every DMU/ZAP/SA decode;
 * no writer Rust bootstrap/FILE code or predicted allocated identity is used.
 */
#include "zpl-read.c"
#include "home-recovery-probe.h"
#include <sys/sha2.h>
#include <sys/zfs_acl.h>

struct home_metadata {
    uint64_t mode, generation, size, links, parent, flags, uid, gid, project;
    uint64_t xattr, acl_count, atime[2], mtime[2], ctime[2], birthtime[2];
    int acl_bytes;
    unsigned char acl[1024];
};
struct home_workspace {
    unsigned char buffer[4096];
    struct home_metadata metadata;
    SHA2_CTX preserved;
};
_Static_assert(sizeof(struct home_workspace) <= 8192, "bounded reader scratch");

static int home_metadata_read(aether_zpl_view *view, uint64_t object,
                              struct home_metadata *out)
{
    memset(out, 0, sizeof(*out));
    dmu_object_info_t info;
    int error = dmu_object_info(view->os, object, &info);
    if (error)
        return error;
    if (info.doi_bonus_type != DMU_OT_SA ||
        (info.doi_type != DMU_OT_DIRECTORY_CONTENTS &&
         info.doi_type != DMU_OT_PLAIN_FILE_CONTENTS))
        return EIO;
    sa_handle_t *handle = NULL;
    error = sa_handle_get(view->os, object, NULL, SA_HDL_PRIVATE, &handle);
    if (error)
        return error;
    sa_bulk_attr_t attrs[14];
    int n = 0;
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_MODE], NULL, &out->mode, 8);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_GEN], NULL,
                     &out->generation, 8);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_SIZE], NULL, &out->size, 8);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_LINKS], NULL, &out->links,
                     8);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_PARENT], NULL, &out->parent,
                     8);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_FLAGS], NULL, &out->flags,
                     8);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_UID], NULL, &out->uid, 8);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_GID], NULL, &out->gid, 8);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_PROJID], NULL,
                     &out->project, 8);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_ATIME], NULL, out->atime,
                     16);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_MTIME], NULL, out->mtime,
                     16);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_CTIME], NULL, out->ctime,
                     16);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_CRTIME], NULL,
                     out->birthtime, 16);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_DACL_COUNT], NULL,
                     &out->acl_count, 8);
    error = sa_bulk_lookup(handle, attrs, n);
    if (!error) {
        error = sa_lookup(handle, view->attributes[ZPL_XATTR], &out->xattr, 8);
        if (error == ENOENT)
            error =
                0; /* Missing optional xattr link denotes no xattr object. */
    }
    if (!error)
        error =
            sa_size(handle, view->attributes[ZPL_DACL_ACES], &out->acl_bytes);
    if (!error &&
        (out->acl_bytes <= 0 || out->acl_bytes > (int)sizeof(out->acl) ||
         !out->acl_count || out->acl_count > sizeof(out->acl)))
        error = EIO;
    if (!error)
        error = sa_lookup(handle, view->attributes[ZPL_DACL_ACES], out->acl,
                          (uint32_t)out->acl_bytes);
    sa_handle_destroy(handle);
    if (error)
        return error;
    if (!out->generation || !out->links || !out->parent ||
        (S_ISDIR(out->mode)   ? info.doi_type != DMU_OT_DIRECTORY_CONTENTS
         : S_ISREG(out->mode) ? info.doi_type != DMU_OT_PLAIN_FILE_CONTENTS
                              : 1))
        return EIO;
    const uint64_t *times[] = {out->atime, out->mtime, out->ctime,
                               out->birthtime};
    for (unsigned i = 0; i < 4; ++i)
        if (times[i][0] > INT64_MAX || times[i][1] >= UINT64_C(1000000000))
            return EIO;
    return 0;
}

/* Lengths and scalars are explicitly little-endian64; padding, allocated
 * scratch tails and unstable ZAP iteration order are never hashed. */
static void home_hash_blob(SHA2_CTX *preserved, const void *data, size_t length)
{
    unsigned char encoded_length[8];
    for (unsigned i = 0; i < 8; ++i)
        encoded_length[i] = (unsigned char)((uint64_t)length >> (8 * i));
    SHA2Update(preserved, encoded_length, sizeof(encoded_length));
    SHA2Update(preserved, data, length);
}
static void home_hash_u64(SHA2_CTX *hash, uint64_t value)
{
    unsigned char bytes[8];
    for (unsigned i = 0; i < 8; ++i)
        bytes[i] = (unsigned char)(value >> (8 * i));
    home_hash_blob(hash, bytes, sizeof(bytes));
}
static void home_hash_metadata(SHA2_CTX *hash, unsigned role, uint64_t object,
                               const struct home_metadata *m)
{
    home_hash_u64(hash, role);
    home_hash_u64(hash, object);
    const uint64_t scalars[] = {
        m->mode,     m->generation,
        m->parent,   m->uid,
        m->gid,      role ? m->flags : m->flags | ZFS_ARCHIVE | ZFS_AV_MODIFIED,
        m->project,  m->xattr,
        m->acl_count};
    for (unsigned i = 0; i < sizeof(scalars) / sizeof(scalars[0]); ++i)
        home_hash_u64(hash, scalars[i]);
    if (role) {
        home_hash_u64(hash, m->size);
        home_hash_u64(hash, m->links);
        home_hash_u64(hash, m->mtime[0]);
        home_hash_u64(hash, m->mtime[1]);
        home_hash_u64(hash, m->ctime[0]);
        home_hash_u64(hash, m->ctime[1]);
    }
    home_hash_u64(hash, m->atime[0]);
    home_hash_u64(hash, m->atime[1]);
    home_hash_u64(hash, m->birthtime[0]);
    home_hash_u64(hash, m->birthtime[1]);
    home_hash_blob(hash, m->acl, (size_t)m->acl_bytes);
}
static int home_time_valid(const uint64_t time[2], uint64_t minimum,
                           uint64_t maximum)
{
    return time[0] >= minimum && time[0] < maximum &&
           time[1] < UINT64_C(1000000000);
}
static int home_time_before(const uint64_t left[2], const uint64_t right[2])
{
    return left[0] < right[0] || (left[0] == right[0] && left[1] <= right[1]);
}
static int home_count(aether_zpl_view *view, uint64_t object, uint64_t expected)
{
    uint64_t count = 0;
    int error = zap_count(view->os, object, &count);
    return error ? error : count == expected ? 0 : EIO;
}
static int home_eof(aether_zpl_view *view, aether_zpl_node file,
                    uint64_t offset, unsigned char *buffer)
{
    size_t count = 99;
    int error = aether_zpl_read(view, file.object, file.generation, offset,
                                buffer, 1, &count);
    return error ? error : count ? EIO : 0;
}
static int home_original_file(aether_zpl_view *view, aether_zpl_node file,
                              struct home_workspace *w)
{
    static const unsigned char original_hash[32] = {
        0xcc, 0x9b, 0xfd, 0xde, 0xdd, 0x66, 0x4b, 0x9a, 0x53, 0x34, 0x58,
        0x1a, 0xf7, 0x86, 0x51, 0x6d, 0x14, 0x9c, 0x3f, 0xbd, 0x2c, 0x7e,
        0x65, 0x73, 0x59, 0x85, 0xac, 0xf1, 0x7b, 0xce, 0x59, 0x35};
    SHA2_CTX hash;
    SHA2Init(SHA256, &hash);
    int error = 0;
    uint64_t offset = 0;
    while (!error && offset < 780248) {
        size_t count = 0;
        error = aether_zpl_read(view, file.object, file.generation, offset,
                                w->buffer, sizeof(w->buffer), &count);
        uint64_t expected = 780248 - offset;
        if (expected > sizeof(w->buffer))
            expected = sizeof(w->buffer);
        if (!error && count != expected)
            error = EIO;
        if (!error) {
            SHA2Update(&hash, w->buffer, count);
            offset += count;
        }
    }
    unsigned char digest[32];
    SHA2Final(digest, &hash);
    if (!error && memcmp(digest, original_hash, sizeof(digest)))
        error = EIO;
    if (!error)
        error = home_eof(view, file, 780248, w->buffer);
    return error;
}
static int home_inventory(aether_zpl_view *view, const uint64_t original[9],
                          const uint64_t extra[3], unsigned extra_count)
{
    uint64_t ids[12];
    memcpy(ids, original, 9 * sizeof(*ids));
    memcpy(ids + 9, extra, extra_count * sizeof(*ids));
    unsigned count = 9 + extra_count;
    for (unsigned i = 0; i < count; ++i)
        for (unsigned j = 0; j < i; ++j)
            if (!ids[i] || ids[i] >= (UINT64_C(1) << 48) || ids[i] == ids[j])
                return EIO;
    unsigned mask = 0;
    uint64_t object = 0;
    for (unsigned step = 0; step <= count; ++step) {
        int error = dmu_object_next(view->os, &object, B_FALSE, 0);
        if (error == ESRCH)
            return mask == ((1U << count) - 1) ? 0 : EIO;
        if (error)
            return error;
        unsigned i;
        for (i = 0; i < count; ++i)
            if (ids[i] == object)
                break;
        if (i == count || (mask & (1U << i)))
            return EIO;
        mask |= 1U << i;
    }
    return EIO;
}
static int home_new_metadata(aether_zpl_view *view, aether_zpl_node node,
                             uint64_t parent, uint64_t links, uint64_t minimum,
                             uint64_t maximum, struct home_metadata *m)
{
    int error = home_metadata_read(view, node.object, m);
    if (error)
        return error;
    uint64_t flags = ZFS_ARCHIVE | ZFS_AV_MODIFIED | ZFS_ACL_TRIVIAL |
                     ZFS_ACL_PROTECTED | ZFS_PROJID;
    if (m->generation != node.generation || m->mode != node.mode ||
        m->size != node.size || m->parent != parent || m->links != links ||
        m->uid != 1000 || m->gid != 1000 || m->project || m->xattr ||
        m->flags != flags || m->acl_count != 3 ||
        m->acl_bytes != 3 * (int)sizeof(zfs_ace_hdr_t) ||
        !home_time_valid(m->atime, minimum, maximum) ||
        !home_time_valid(m->mtime, minimum, maximum) ||
        !home_time_valid(m->ctime, minimum, maximum) ||
        !home_time_valid(m->birthtime, minimum, maximum) ||
        memcmp(m->atime, m->birthtime, 16) || memcmp(m->mtime, m->ctime, 16) ||
        !home_time_before(m->birthtime, m->mtime))
        return EIO;
    zfs_ace_hdr_t acl[3];
    memcpy(acl, m->acl, sizeof(acl));
    if (acl[0].z_type || acl[0].z_flags != ACE_OWNER ||
        acl[0].z_access_mask !=
            (S_ISDIR(node.mode) ? UINT32_C(0x1e01ff) : UINT32_C(0x1e019f)) ||
        acl[1].z_type || acl[1].z_flags != (ACE_GROUP | ACE_IDENTIFIER_GROUP) ||
        acl[1].z_access_mask != UINT32_C(0x120088) || acl[2].z_type ||
        acl[2].z_flags != ACE_EVERYONE ||
        acl[2].z_access_mask != UINT32_C(0x120088))
        return EIO;
    return 0;
}

/* Fixed two-entry namespace. Upstream owns the cursor/attribute layout. The
 * copied leaf remains private until the complete oracle succeeds. */
static int home_mktemp_entries(aether_zpl_view *view, aether_zpl_node home,
                               uint64_t objects[2], unsigned char leaf[8])
{
    zap_attribute_t *entry = zap_attribute_alloc();
    if (!entry)
        return ENOMEM;
    zap_cursor_t cursor;
    zap_cursor_init(&cursor, view->os, home.object);
    unsigned seen = 0;
    int error = 0;
    for (unsigned i = 0; i < 2; ++i) {
        error = zap_cursor_retrieve(&cursor, entry);
        if (error)
            break;
        uint64_t value = entry->za_first_integer;
        size_t length = strnlen(entry->za_name, 256);
        if (entry->za_integer_length != 8 || entry->za_num_integers != 1 ||
            ((value >> 48) & 0xfff) || !ZFS_DIRENT_OBJ(value)) {
            error = EIO;
            break;
        }
        unsigned role;
        if (length == 5 && !memcmp(entry->za_name, "probe", 5) &&
            ZFS_DIRENT_TYPE(value) == IFTODT(S_IFREG))
            role = 0;
        else if (length == 8 && entry->za_name[0] == 't' &&
                 entry->za_name[1] == '.' &&
                 ZFS_DIRENT_TYPE(value) == IFTODT(S_IFDIR)) {
            role = 1;
            for (unsigned j = 2; j < 8; ++j) {
                unsigned char c = (unsigned char)entry->za_name[j];
                if (!((c >= 'A' && c <= 'P') || (c >= 'a' && c <= 'p'))) {
                    error = EIO;
                    break;
                }
            }
            if (error)
                break;
            memcpy(leaf, entry->za_name, 8);
        } else {
            error = EIO;
            break;
        }
        if (seen & (1U << role)) {
            error = EIO;
            break;
        }
        objects[role] = ZFS_DIRENT_OBJ(value);
        seen |= 1U << role;
        zap_cursor_advance(&cursor);
    }
    if (!error) {
        int end = zap_cursor_retrieve(&cursor, entry);
        if (end != ENOENT)
            error = end ? end : EIO;
    }
    zap_cursor_fini(&cursor);
    zap_attribute_free(entry);
    return error ? error : seen == 3 ? 0 : EIO;
}

static int home_mktemp_namespace(aether_zpl_view *view, aether_zpl_node home,
                                 const uint64_t root_time[2], uint64_t minimum,
                                 uint64_t maximum, aether_zpl_node *probe,
                                 aether_zpl_node *generated,
                                 unsigned char leaf[8],
                                 struct home_workspace *w)
{
    if (home.mode != (S_IFDIR | 0700U) || home.size != 4)
        return EIO;
    int error = home_count(view, home.object, 2);
    if (!error)
        error = home_new_metadata(view, home, view->root.object, 3, minimum,
                                  maximum, &w->metadata);
    if (!error && memcmp(w->metadata.birthtime, root_time, 16))
        error = EIO;
    uint64_t final_time[2] = {0}, probe_time[2] = {0}, objects[2] = {0};
    if (!error)
        memcpy(final_time, w->metadata.mtime, 16);
    if (!error)
        error = home_mktemp_entries(view, home, objects, leaf);
    if (!error)
        error = aether_zpl_lookup(view, home.object, home.generation,
                                  (const unsigned char *)"probe", 5, probe);
    if (!error && (probe->object != objects[0] ||
                   probe->mode != (S_IFREG | 0600) || probe->size))
        error = EIO;
    if (!error)
        error = home_new_metadata(view, *probe, home.object, 1, minimum,
                                  maximum, &w->metadata);
    if (!error && (memcmp(w->metadata.birthtime, w->metadata.mtime, 16) ||
                   !home_time_before(root_time, w->metadata.birthtime)))
        error = EIO;
    if (!error)
        memcpy(probe_time, w->metadata.birthtime, 16);
    if (!error)
        error = home_eof(view, *probe, 0, w->buffer);
    if (!error)
        error = aether_zpl_lookup(view, home.object, home.generation, leaf, 8,
                                  generated);
    if (!error && (generated->object != objects[1] ||
                   generated->mode != (S_IFDIR | 0700) || generated->size != 2))
        error = EIO;
    if (!error)
        error = home_count(view, generated->object, 0);
    if (!error)
        error = home_new_metadata(view, *generated, home.object, 2, minimum,
                                  maximum, &w->metadata);
    if (!error && (memcmp(w->metadata.birthtime, w->metadata.mtime, 16) ||
                   memcmp(w->metadata.birthtime, final_time, 16) ||
                   !home_time_before(probe_time, w->metadata.birthtime)))
        error = EIO;
    return error;
}

static int home_readback(spa_t *spa, int expectation, uint64_t minimum,
                         uint64_t maximum, unsigned char digest32[32],
                         int mktemp, unsigned char leaf8[8])
{
    if (!digest32)
        return EINVAL;
    memset(digest32, 0, 32);
    if (!spa || (expectation < 0 || expectation > 2) || minimum >= maximum ||
        maximum > INT64_MAX || maximum - minimum > 60)
        return EINVAL;
    int recovered = expectation != 0;
    if (spa_writeable(spa))
        return EROFS;
    struct home_workspace *w = kmem_zalloc(sizeof(*w), KM_NOSLEEP);
    if (!w)
        return ENOMEM;
    aether_zpl_view *view = NULL;
    int error = aether_zpl_open(spa, "testpool_zstd/x86_64", &view);
    aether_zpl_node root = {0}, file = {0}, home = {0}, probe = {0},
                    generated = {0};
    unsigned char leaf[8] = {0};
    if (!error)
        error = aether_zpl_root(view, &root);
    if (!error &&
        (root.mode != (S_IFDIR | 0755) || root.size != (recovered ? 4U : 3U)))
        error = EIO;
    if (!error)
        error = home_count(view, root.object, recovered ? 2 : 1);
    if (!error)
        error = aether_zpl_lookup(view, root.object, root.generation,
                                  (const unsigned char *)"zstd", 4, &file);
    if (!error && (file.mode != (S_IFREG | 0755) || file.size != 780248))
        error = EIO;
    if (!error)
        error = home_original_file(view, file, w);
    uint64_t original[9] = {MASTER_NODE_OBJ, file.object, 0, 0, 0, 0,
                            root.object,     0,           0};
    if (!error)
        error = zap_lookup(view->os, MASTER_NODE_OBJ, ZFS_SA_ATTRS, 8, 1,
                           &original[4]);
    if (!error)
        error = zap_lookup(view->os, MASTER_NODE_OBJ, ZFS_UNLINKED_SET, 8, 1,
                           &original[5]);
    if (!error)
        error =
            zap_lookup(view->os, original[4], "REGISTRY", 8, 1, &original[7]);
    if (!error)
        error =
            zap_lookup(view->os, original[4], "LAYOUTS", 8, 1, &original[8]);
    if (!error)
        error = home_count(view, MASTER_NODE_OBJ, 7);
    if (!error)
        error = home_count(view, original[4], 2);
    if (!error)
        error = home_count(view, original[5], 0);
    if (!error)
        error = home_metadata_read(view, file.object, &w->metadata);
    if (!error)
        original[2] = w->metadata.xattr;
    uint64_t entry = 0;
    if (!error && !original[2])
        error = EIO;
    if (!error)
        error = home_count(view, original[2], 1);
    if (!error)
        error =
            zap_lookup(view->os, original[2], "security.selinux", 8, 1, &entry);
    if (!error &&
        (((entry >> 48) & 0xfff) || ZFS_DIRENT_TYPE(entry) != IFTODT(S_IFREG)))
        error = EIO;
    original[3] = ZFS_DIRENT_OBJ(entry);
    uint64_t root_time[2] = {0}, home_time[2] = {0};
    SHA2Init(SHA256, &w->preserved);
    static const unsigned char schema[] = "aether-home-preserved-metadata-v1";
    home_hash_blob(&w->preserved, schema, sizeof(schema) - 1);
    for (unsigned i = 0; !error && i < 4; ++i) {
        uint64_t object = i == 0 ? root.object : original[i];
        struct home_metadata *m = &w->metadata;
        error = home_metadata_read(view, object, m);
        uint64_t parent = i == 0   ? root.object
                          : i == 1 ? root.object
                          : i == 2 ? file.object
                                   : original[2];
        uint64_t size = i == 0   ? (recovered ? 4 : 3)
                        : i == 1 ? 780248
                        : i == 2 ? 3
                                 : 37;
        uint64_t mode = i == 0   ? (S_IFDIR | 0755)
                        : i == 1 ? (S_IFREG | 0755)
                        : i == 2 ? (S_IFDIR | 01777)
                                 : (S_IFREG | 0644);
        if (!error &&
            ((i == 0 && m->generation != root.generation) ||
             (i == 1 && m->generation != file.generation) ||
             m->parent != parent || m->size != size || m->mode != mode ||
             m->links != (i == 0   ? (recovered ? 3U : 2U)
                          : i == 2 ? 2U
                                   : 1U) ||
             m->uid || m->gid || m->project ||
             !!(m->flags & ZFS_XATTR) != (i >= 2)))
            error = EIO;
        if (!error && i == 0 && recovered) {
            if ((m->flags & (ZFS_ARCHIVE | ZFS_AV_MODIFIED)) !=
                    (ZFS_ARCHIVE | ZFS_AV_MODIFIED) ||
                !home_time_valid(m->mtime, minimum, maximum) ||
                memcmp(m->mtime, m->ctime, 16))
                error = EIO;
            memcpy(root_time, m->mtime, 16);
        }
        if (!error)
            home_hash_metadata(&w->preserved, i, object, m);
    }
    for (unsigned i = 0; !error && i < 9; ++i) {
        static const unsigned types[9] = {
            DMU_OT_MASTER_NODE,        DMU_OT_PLAIN_FILE_CONTENTS,
            DMU_OT_DIRECTORY_CONTENTS, DMU_OT_PLAIN_FILE_CONTENTS,
            DMU_OT_SA_MASTER_NODE,     DMU_OT_UNLINKED_SET,
            DMU_OT_DIRECTORY_CONTENTS, DMU_OT_SA_ATTR_REGISTRATION,
            DMU_OT_SA_ATTR_LAYOUTS};
        dmu_object_info_t info;
        error = dmu_object_info(view->os, original[i], &info);
        if (!error && info.doi_type != types[i])
            error = EIO;
        if (!error)
            home_hash_u64(&w->preserved, original[i]);
    }
    if (!error)
        error = dmu_read(view->os, original[3], 0, 37, w->buffer,
                         DMU_READ_NO_PREFETCH);
    if (!error)
        home_hash_blob(&w->preserved, w->buffer, 37);
    if (!error) {
        int found = aether_zpl_lookup(view, root.object, root.generation,
                                      (const unsigned char *)"home", 4, &home);
        if (!recovered)
            error = found == ENOENT ? 0 : found ? found : EEXIST;
        else
            error = found;
    }
    if (!error && recovered && mktemp)
        error = home_mktemp_namespace(view, home, root_time, minimum, maximum,
                                      &probe, &generated, leaf, w);
    if (!error && recovered && !mktemp) {
        if (home.mode != (S_IFDIR | 0700) || home.size != 3)
            error = EIO;
        if (!error)
            error = home_count(view, home.object, 1);
        if (!error)
            error = home_new_metadata(view, home, root.object, 2, minimum,
                                      maximum, &w->metadata);
        if (!error && memcmp(w->metadata.birthtime, root_time, 16))
            error = EIO;
        if (!error)
            memcpy(home_time, w->metadata.mtime, 16);
        if (!error)
            error =
                aether_zpl_lookup(view, home.object, home.generation,
                                  (const unsigned char *)"probe", 5, &probe);
        if (!error && (probe.mode != (S_IFREG | 0600) ||
                       probe.size != (expectation == 2 ? 0U : 16U)))
            error = EIO;
        if (!error)
            error = home_new_metadata(view, probe, home.object, 1, minimum,
                                      maximum, &w->metadata);
        if (!error && (memcmp(w->metadata.birthtime, home_time, 16) ||
                       !home_time_before(root_time, home_time) ||
                       !home_time_before(home_time, w->metadata.mtime)))
            error = EIO;
        if (expectation == 1) {
            size_t count = 0;
            static const unsigned char payload[16] = {
                'A', 'F', '0', '9', '-', 'H', 'O', 'M',
                'E', '-', 'W', 'R', 'I', 'T', 'E', '\n'};
            if (!error)
                error = aether_zpl_read(view, probe.object, probe.generation, 0,
                                        w->buffer, sizeof(payload), &count);
            if (!error && (count != sizeof(payload) ||
                           memcmp(w->buffer, payload, sizeof(payload))))
                error = EIO;
            if (!error)
                error = home_eof(view, probe, 16, w->buffer);
        } else if (!error)
            /* A nonzero request must observe EOF even for an empty object. */
            error = home_eof(view, probe, 0, w->buffer);
    }
    uint64_t extra[3] = {home.object, probe.object, generated.object};
    if (!error)
        error = home_inventory(view, original, extra,
                               recovered ? (mktemp ? 3 : 2) : 0);
    if (!error) {
        SHA2Final(w->buffer, &w->preserved);
        memcpy(digest32, w->buffer, 32);
        if (mktemp)
            memcpy(leaf8, leaf, sizeof(leaf));
    }
    aether_zpl_close(&view);
    memset(w, 0, sizeof(*w));
    kmem_free(w, sizeof(*w));
    return error;
}

int aether_home_readback(spa_t *spa, int expectation, uint64_t minimum,
                         uint64_t maximum, unsigned char digest32[32])
{
    return home_readback(spa, expectation, minimum, maximum, digest32, 0, NULL);
}

int aether_home_mktemp_readback(spa_t *spa, int recovered, uint64_t minimum,
                                uint64_t maximum, unsigned char result40[40])
{
    if (!result40)
        return EINVAL;
    memset(result40, 0, 40);
    if (recovered != 0 && recovered != 1)
        return EINVAL;
    return home_readback(spa, recovered, minimum, maximum, result40, 1,
                         result40 + 32);
}
