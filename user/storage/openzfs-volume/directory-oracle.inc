/* SPDX-License-Identifier: BSD-2-Clause */
/* Independent fixed AF06 hierarchy verifier; never used to authorize mutation.
 */
#ifndef AETHER_DIRECTORY_LAST
#define AETHER_DIRECTORY_LAST 1791290100
#endif
static int directory_absent(aether_zpl_view *view, aether_zpl_node parent,
                            const char *name)
{
    aether_zpl_node value;
    int error =
        aether_zpl_lookup(view, parent.object, parent.generation,
                          (const unsigned char *)name, strlen(name), &value);
    return error == ENOENT ? 0 : error ? error : EEXIST;
}
static int directory_lookup(aether_zpl_view *view, aether_zpl_node parent,
                            const char *name, uint64_t mode, uint64_t size,
                            aether_zpl_node *out)
{
    int error =
        aether_zpl_lookup(view, parent.object, parent.generation,
                          (const unsigned char *)name, strlen(name), out);
    if (!error &&
        (!out->object || out->object == 2 || out->object == 34 ||
         out->generation <= 782 || out->mode != mode || out->size != size))
        error = EIO;
    return error;
}
static int directory_metadata(aether_zpl_view *view, aether_zpl_node node,
                              uint64_t expected_parent, uint64_t expected_links,
                              int root)
{
    sa_handle_t *handle = NULL;
    int error =
        sa_handle_get(view->os, node.object, NULL, SA_HDL_PRIVATE, &handle);
    if (error)
        return error;
    uint64_t flags = 0, links = 0, parent = 0, uid = 0, gid = 0, size = 0,
             project = 99, count = 0;
    uint64_t mtime[2] = {0}, ctime[2] = {0}, crtime[2] = {0}, atime[2] = {0};
    zfs_ace_hdr_t acl[3] = {{0}};
    sa_bulk_attr_t attrs[14];
    int n = 0;
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_FLAGS], NULL, &flags, 8);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_LINKS], NULL, &links, 8);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_PARENT], NULL, &parent, 8);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_UID], NULL, &uid, 8);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_GID], NULL, &gid, 8);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_SIZE], NULL, &size, 8);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_MTIME], NULL, mtime, 16);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_CTIME], NULL, ctime, 16);
    if (!root) {
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_PROJID], NULL, &project,
                         8);
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_CRTIME], NULL, crtime,
                         16);
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_ATIME], NULL, atime,
                         16);
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_DACL_COUNT], NULL,
                         &count, 8);
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_DACL_ACES], NULL, acl,
                         sizeof(acl));
    }
    error = sa_bulk_lookup(handle, attrs, n);
    sa_handle_destroy(handle);
    if (error)
        return error;
    if (parent != expected_parent || links != expected_links ||
        size != node.size || uid != (root ? 0 : 1000) ||
        gid != (root ? 0 : 1000) ||
        (flags & (ZFS_ARCHIVE | ZFS_AV_MODIFIED)) !=
            (ZFS_ARCHIVE | ZFS_AV_MODIFIED) ||
        ctime[0] < 1791290040 || ctime[0] > AETHER_DIRECTORY_LAST ||
        ctime[1] >= 1000000000 || mtime[0] < 1791290040 ||
        mtime[0] > AETHER_DIRECTORY_LAST || mtime[1] >= 1000000000 ||
        ctime[0] < mtime[0] || (ctime[0] == mtime[0] && ctime[1] < mtime[1]))
        return EIO;
    if (S_ISDIR(node.mode) && memcmp(mtime, ctime, 16))
        return EIO;
    if (!root &&
        (project || count != 3 ||
         (flags & (ZFS_ACL_TRIVIAL | ZFS_ACL_PROTECTED | ZFS_PROJID)) !=
             (ZFS_ACL_TRIVIAL | ZFS_ACL_PROTECTED | ZFS_PROJID) ||
         crtime[0] < 1791290040 || crtime[0] > ctime[0] ||
         crtime[1] >= 1000000000 ||
         (crtime[0] == ctime[0] && crtime[1] > ctime[1]) ||
         memcmp(crtime, atime, 16) || acl[0].z_type ||
         acl[0].z_flags != ACE_OWNER ||
         acl[0].z_access_mask !=
             (S_ISDIR(node.mode) ? UINT32_C(0x1e01ff) : UINT32_C(0x1e019f)) ||
         acl[1].z_type ||
         acl[1].z_flags != (ACE_GROUP | ACE_IDENTIFIER_GROUP) ||
         acl[1].z_access_mask != UINT32_C(0x120088) || acl[2].z_type ||
         acl[2].z_flags != ACE_EVERYONE ||
         acl[2].z_access_mask != UINT32_C(0x120088)))
        return EIO;
    return 0;
}
static int directory_count(aether_zpl_view *view, aether_zpl_node node,
                           uint64_t expected)
{
    uint64_t count = 0;
    int error = zap_count(view->os, node.object, &count);
    return error                                         ? error
           : count != expected || node.size != count + 2 ? EIO
                                                         : 0;
}
static int directory_objects(aether_zpl_view *view, const uint64_t extra[3],
                             unsigned length)
{
    static const uint64_t original[9] = {1, 2, 3, 4, 32, 33, 34, 35, 36};
    unsigned mask = 0, added = 0;
    uint64_t object = 0;
    for (unsigned count = 0; count < 16; ++count) {
        int error = dmu_object_next(view->os, &object, B_FALSE, 0);
        if (error == ESRCH)
            return mask == 511 && added == ((1U << length) - 1) ? 0 : EIO;
        if (error)
            return error;
        if (!object || object > 4096)
            return EIO;
        unsigned i;
        for (i = 0; i < 9; ++i)
            if (original[i] == object) {
                if (mask & (1U << i))
                    return EIO;
                mask |= 1U << i;
                break;
            }
        if (i == 9) {
            for (i = 0; i < length; ++i)
                if (extra[i] == object) {
                    if (added & (1U << i))
                        return EIO;
                    added |= 1U << i;
                    break;
                }
            if (i == length)
                return EIO;
        }
    }
    return EIO;
}
static int directory_check(aether_zpl_view *view, unsigned phase)
{
    aether_zpl_node root = {0}, files = {0}, state = {0}, file = {0};
    int error = aether_zpl_root(view, &root);
    if (!error &&
        (root.object != 34 || root.generation != 45 || root.mode != 040755 ||
         root.size != (phase == 2   ? 5
                       : phase == 1 ? 4
                                    : 3)))
        error = EIO;
    if (!error)
        error = directory_count(view, root,
                                phase == 2   ? 3
                                : phase == 1 ? 2
                                             : 1);
    if (!error)
        error = namespace_original(view);
    uint64_t extra[3] = {0};
    unsigned length = 0;
    if (!error && phase) {
        error = directory_metadata(view, root, 34, phase == 2 ? 4 : 3, 1);
        if (!error)
            error = directory_lookup(view, root, "files", 040700,
                                     phase == 2 ? 3 : 2, &files);
        if (!error)
            error = directory_count(view, files, phase == 2 ? 1 : 0);
        if (!error)
            error = directory_metadata(view, files, 34, 2, 0);
        if (!error)
            extra[length++] = files.object;
        if (!error)
            error = directory_absent(view, files, DIR_FIRST);
        if (!error && phase == 1)
            error = directory_absent(view, files, DIR_SECOND);
    } else if (!error)
        error = directory_absent(view, root, "files");
    if (!error && phase != 2)
        error = directory_absent(view, root, "state");
    if (!error && phase == 2) {
        error = directory_lookup(view, root, "state", 040700, 2, &state);
        if (!error)
            error = directory_count(view, state, 0);
        if (!error)
            error = directory_metadata(view, state, 34, 2, 0);
        if (!error)
            error = directory_absent(view, state, "packages");
        if (!error)
            error = directory_absent(view, state, "stage");
        if (!error)
            extra[length++] = state.object;
        if (!error)
            error =
                directory_lookup(view, files, DIR_SECOND, 0100600, 4096, &file);
        if (!error)
            error = directory_metadata(view, file, files.object, 1, 0);
        if (!error)
            extra[length++] = file.object;
        unsigned char data[64] = {0};
        size_t got = 0;
        for (unsigned offset = 0; !error && offset < 4096;
             offset += sizeof(data)) {
            error = aether_zpl_read(view, file.object, file.generation, offset,
                                    data, sizeof(data), &got);
            if (!error && got != sizeof(data))
                error = EIO;
            for (unsigned i = 0; !error && i < sizeof(data); ++i)
                if (data[i] != (unsigned char)(71 + offset + i))
                    error = EIO;
        }
        if (!error)
            error = aether_zpl_read(view, file.object, file.generation, 4096,
                                    data, 1, &got);
        if (!error && got)
            error = EIO;
    }
    if (!error && length > 1 &&
        (extra[0] == extra[1] || extra[0] == extra[2] || extra[1] == extra[2]))
        error = EIO;
    if (!error)
        error = directory_objects(view, extra, length);
    return error;
}
#if MNS_READER
int aether_pool_namespace_recover(spa_t *spa)
{
    if (!spa || spa_writeable(spa))
        return namespace_error(1, EROFS);
    aether_zpl_view *view = NULL;
    int error = aether_zpl_open(spa, "testpool_zstd/x86_64", &view);
    if (!error)
        error = directory_check(view, DIR_EMPTY ? 1 : 2);
    aether_zpl_close(&view);
    return error ? namespace_error(9, error) : 0;
}
#else
#include "fs-mixed-owner.inc"
int aether_pool_namespace_write(spa_t *spa, uint64_t *assigned)
{
    if (!assigned)
        return EINVAL;
    *assigned = 0;
    if (!spa || !spa_writeable(spa))
        return EROFS;
    aether_zpl_view *view = NULL;
    int error = aether_zpl_open_write(spa, "testpool_zstd/x86_64", &view);
    if (!error)
        error = directory_check(view, 0);
    aether_zpl_close(&view);
    aether_zpl_write_result result = {0};
    if (!error)
        error = aether_fs_owner_probe(spa, &result);
    *assigned = result.txg;
    if (!error && (!result.txg || result.state != AETHER_ZPL_SYNCED ||
                   result.bytes_staged))
        error = EIO;
    if (!error)
        error = aether_zpl_open_write(spa, "testpool_zstd/x86_64", &view);
    if (!error)
        error = directory_check(view, DIR_EMPTY ? 1 : 2);
    aether_zpl_close(&view);
    return error ? namespace_error(9, error) : 0;
}
#endif
