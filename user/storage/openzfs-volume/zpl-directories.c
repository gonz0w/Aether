/* SPDX-License-Identifier: BSD-2-Clause */
/* Serialized directory extension. The qualified regular-file unit is unchanged.
 * Original OpenZFS owns directory ZAP/SA encoding, accounting and transaction
 * I/O.
 */
#include "zpl-mutate.c"
#include "zpl-directories.h"

int aether_zpl_directory(aether_zpl_view *view, uint64_t object,
                         uint64_t generation, aether_zpl_node *out)
{
    if (!out)
        return EINVAL;
    memset(out, 0, sizeof(*out));
    if (!view)
        return EINVAL;
    aether_zpl_node node;
    uint64_t parent = 0;
    int error = aether_zpl_load(view, object, &node, &parent);
    if (!error && node.generation != generation)
        error = ESTALE;
    if (!error && !S_ISDIR(node.mode))
        error = ENOTDIR;
    if (!error)
        *out = node;
    return error;
}

int aether_zpl_mkdir(aether_zpl_view *view, uint64_t directory,
                     uint64_t directory_generation, const unsigned char *name,
                     size_t length, uint64_t uid, uint64_t gid,
                     uint64_t seconds, uint64_t nanos, aether_zpl_node *created,
                     aether_zpl_write_result *out)
{
    if (out)
        memset(out, 0, sizeof(*out));
    if (created)
        memset(created, 0, sizeof(*created));
    if (!out || !created)
        return EINVAL;
    char component[256];
    int error = mutation_input(view, seconds, nanos);
    if (!error)
        error = mutation_name(name, length, component);
    if (!error && (uid > INT32_MAX || gid > INT32_MAX))
        error = EOVERFLOW;
    if (error)
        return error;
    struct mutation_node parent = {0};
    error = mutation_load(view, directory, directory_generation, 1, &parent);
    if (!error && (parent.node.size >= 4098 || parent.links == UINT64_MAX))
        error = ENOSPC;
    if (!error)
        error = mutation_absent(view, directory, component);
    if (error)
        goto done;
    dmu_tx_t *tx = dmu_tx_create(view->os);
    if (!tx) {
        error = ENOMEM;
        goto done;
    }
    dmu_tx_hold_sa_create(tx,
                          ZFS_SA_BASE_ATTR_SIZE + 3 * sizeof(zfs_ace_hdr_t));
    dmu_tx_hold_zap(tx, DMU_NEW_OBJECT, B_TRUE, NULL);
    dmu_tx_hold_zap(tx, directory, B_TRUE, component);
    dmu_tx_hold_sa(tx, parent.handle, B_FALSE);
    error = mutation_begin(tx, out);
    if (error)
        goto done;
    error = mutation_bind(tx, out);
    sa_handle_t *handle = NULL;
    if (!error) {
        uint64_t object =
            zap_create(view->os, DMU_OT_DIRECTORY_CONTENTS, DMU_OT_SA,
                       DN_BONUS_SIZE(DNODE_MIN_SIZE), tx);
        *created = (aether_zpl_node){object, out->txg, 2, S_IFDIR | 0700};
        if (!object || object >= (UINT64_C(1) << 48))
            error = EIO;
        if (!error)
            error =
                sa_handle_get(view->os, object, NULL, SA_HDL_PRIVATE, &handle);
    }
    if (!error) {
        uint64_t mode = S_IFDIR | 0700, size = 2, links = 2, count = 3,
                 project = 0;
        uint64_t flags = ZFS_ARCHIVE | ZFS_AV_MODIFIED | ZFS_ACL_TRIVIAL |
                         ZFS_ACL_PROTECTED | ZFS_PROJID;
        uint64_t time[2] = {seconds, nanos};
        uint32_t common = ACE_READ_ATTRIBUTES | ACE_READ_NAMED_ATTRS |
                          ACE_READ_ACL | ACE_SYNCHRONIZE;
        zfs_ace_hdr_t acl[3] = {
            {ACE_ACCESS_ALLOWED_ACE_TYPE, ACE_OWNER,
             common | ACE_READ_DATA | ACE_WRITE_DATA | ACE_APPEND_DATA |
                 ACE_EXECUTE | ACE_DELETE_CHILD | ACE_WRITE_ATTRIBUTES |
                 ACE_WRITE_NAMED_ATTRS | ACE_WRITE_ACL | ACE_WRITE_OWNER},
            {ACE_ACCESS_ALLOWED_ACE_TYPE, ACE_GROUP | ACE_IDENTIFIER_GROUP,
             common},
            {ACE_ACCESS_ALLOWED_ACE_TYPE, ACE_EVERYONE, common}};
        sa_bulk_attr_t attrs[16];
        int n = 0;
        /* Fixed leading SA offsets are also consumed by original ZPL
         * accounting. */
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_MODE], NULL, &mode, 8);
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_SIZE], NULL, &size, 8);
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_GEN], NULL, &out->txg,
                         8);
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_UID], NULL, &uid, 8);
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_GID], NULL, &gid, 8);
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_PARENT], NULL,
                         &directory, 8);
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_FLAGS], NULL, &flags,
                         8);
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_ATIME], NULL, time, 16);
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_MTIME], NULL, time, 16);
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_CTIME], NULL, time, 16);
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_CRTIME], NULL, time,
                         16);
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_LINKS], NULL, &links,
                         8);
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_PROJID], NULL, &project,
                         8);
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_DACL_COUNT], NULL,
                         &count, 8);
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_DACL_ACES], NULL, acl,
                         sizeof(acl));
        error = sa_replace_all_by_template(handle, attrs, n, tx);
    }
    if (handle)
        sa_handle_destroy(handle);
    if (!error) {
        uint64_t entry = ((uint64_t)IFTODT(S_IFDIR) << 60) | created->object;
        error = zap_add(view->os, directory, component, 8, 1, &entry, tx);
    }
    if (!error) {
        uint64_t links = parent.links + 1;
        error = sa_update(parent.handle, view->attributes[ZPL_LINKS], &links, 8,
                          tx);
    }
    if (!error)
        error = mutation_parent(view, &parent, parent.node.size + 1, seconds,
                                nanos, tx);
    error = mutation_finish(view, tx, error, out);
done:
    mutation_release(&parent);
    return error;
}

int aether_zpl_rmdir(aether_zpl_view *view, uint64_t directory,
                     uint64_t directory_generation, const unsigned char *name,
                     size_t length, uint64_t object, uint64_t generation,
                     uint64_t seconds, uint64_t nanos,
                     aether_zpl_write_result *out)
{
    if (!out)
        return EINVAL;
    memset(out, 0, sizeof(*out));
    char component[256];
    int error = mutation_input(view, seconds, nanos);
    if (!error)
        error = mutation_name(name, length, component);
    if (error)
        return error;
    struct mutation_node parent = {0}, child = {0};
    error = mutation_load(view, directory, directory_generation, 1, &parent);
    uint64_t entry = 0;
    if (!error)
        error = zap_lookup(view->os, directory, component, 8, 1, &entry);
    if (!error && (((entry >> 48) & 0xfff) || ZFS_DIRENT_OBJ(entry) != object ||
                   ZFS_DIRENT_TYPE(entry) != IFTODT(S_IFDIR)))
        error = ESTALE;
    if (!error && (object == directory || object == view->root.object))
        error = EINVAL;
    if (!error)
        error = mutation_load(view, object, generation, 1, &child);
    if (!error && child.parent != directory)
        error = EIO;
    if (!error && (child.node.size != 2 || child.links != 2))
        error = ENOTEMPTY;
    if (!error && (parent.links < 3 || parent.node.size < 3))
        error = EIO;
    if (!error) {
        uint64_t xattr = 0;
        int found =
            sa_lookup(child.handle, view->attributes[ZPL_XATTR], &xattr, 8);
        if (found && found != ENOENT)
            error = found;
        else if (xattr)
            error = ENOTSUP;
    }
    if (error)
        goto done;
    dmu_tx_t *tx = dmu_tx_create(view->os);
    if (!tx) {
        error = ENOMEM;
        goto done;
    }
    dmu_tx_hold_zap(tx, directory, B_FALSE, component);
    dmu_tx_hold_sa(tx, parent.handle, B_FALSE);
    dmu_tx_hold_sa(tx, child.handle, B_FALSE);
    dmu_tx_hold_free(tx, object, 0, DMU_OBJECT_END);
    dmu_tx_mark_netfree(tx);
    error = mutation_begin(tx, out);
    if (error)
        goto done;
    error = mutation_bind(tx, out);
    if (!error)
        error = zap_remove(view->os, directory, component, tx);
    if (!error) {
        uint64_t links = parent.links - 1;
        error = sa_update(parent.handle, view->attributes[ZPL_LINKS], &links, 8,
                          tx);
    }
    if (!error)
        error = mutation_parent(view, &parent, parent.node.size - 1, seconds,
                                nanos, tx);
    if (!error) {
        uint64_t links = 0;
        error =
            sa_update(child.handle, view->attributes[ZPL_LINKS], &links, 8, tx);
    }
    mutation_release(&child);
    if (!error)
        error = zap_destroy(view->os, object, tx);
    error = mutation_finish(view, tx, error, out);
done:
    mutation_release(&child);
    mutation_release(&parent);
    return error;
}
