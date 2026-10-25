/* SPDX-License-Identifier: BSD-2-Clause */
/* One context implementation; original DMU/ZAP/SA owns all disk encoding.
 * See zpl-mutate.h and the namespace batch contract for restricted semantics.
 */
#include "zpl-write.c"
#include "zpl-mutate.h"
#include <sys/zfs_acl.h>

struct mutation_node {
    aether_zpl_node node;
    uint64_t parent, links, flags;
    sa_handle_t *handle;
};

static int mutation_name(const unsigned char *name, size_t length,
                         char out[256])
{
    if (!name || !length || length > 255 || (length == 1 && name[0] == '.') ||
        (length == 2 && name[0] == '.' && name[1] == '.'))
        return EINVAL;
    for (size_t i = 0; i < length; ++i)
        if (!name[i] || name[i] == '/')
            return EINVAL;
    memcpy(out, name, length);
    out[length] = 0;
    return 0;
}

static int mutation_input(aether_zpl_view *view, uint64_t seconds,
                          uint64_t nanos)
{
    if (!view || seconds > INT64_MAX || nanos >= UINT64_C(1000000000))
        return EINVAL;
    return spa_writeable(dmu_objset_spa(view->os)) ? 0 : EROFS;
}

static void mutation_release(struct mutation_node *node)
{
    if (node->handle) {
        sa_handle_destroy(node->handle);
        node->handle = NULL;
    }
}

static int mutation_load(aether_zpl_view *view, uint64_t object,
                         uint64_t generation, int directory,
                         struct mutation_node *out)
{
    int error = aether_zpl_load(view, object, &out->node, &out->parent);
    if (error)
        return error;
    if (out->node.generation != generation)
        return ESTALE;
    if (directory ? !S_ISDIR(out->node.mode) : !S_ISREG(out->node.mode))
        return directory ? ENOTDIR : EISDIR;
    if (out->node.mode & (S_ISUID | S_ISGID | S_ISVTX))
        return ENOTSUP;
    error = sa_handle_get(view->os, object, NULL, SA_HDL_PRIVATE, &out->handle);
    if (error)
        return error;
    sa_bulk_attr_t attrs[2];
    int n = 0;
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_LINKS], NULL, &out->links,
                     8);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_FLAGS], NULL, &out->flags,
                     8);
    error = sa_bulk_lookup(out->handle, attrs, n);
    if (!error && (out->flags &
                   (ZFS_IMMUTABLE | ZFS_APPENDONLY | ZFS_READONLY | ZFS_XATTR)))
        error = EPERM;
    if (!error && !directory && out->links != 1)
        error = ENOTSUP;
    if (!error && directory) {
        uint64_t entries = 0, project = 0;
        if (out->flags & (ZFS_INHERIT_ACE | ZFS_PROJINHERIT))
            error = ENOTSUP;
        if (!error) {
            int found = sa_lookup(out->handle, view->attributes[ZPL_PROJID],
                                  &project, 8);
            if (found != 0 && found != ENOENT)
                error = found;
            else if (project)
                error = ENOTSUP;
        }
        if (!error)
            error = zap_count(view->os, object, &entries);
        if (!error &&
            (entries > 4096 || out->node.size != entries + 2 || out->links < 2))
            error = EIO;
    }
    if (error)
        mutation_release(out);
    return error;
}

static int mutation_entry(aether_zpl_view *view, uint64_t directory,
                          const char *name, struct mutation_node *child,
                          uint64_t object, uint64_t generation)
{
    uint64_t entry = 0;
    int error = zap_lookup(view->os, directory, name, 8, 1, &entry);
    if (error)
        return error;
    if (((entry >> 48) & 0xfff) || ZFS_DIRENT_OBJ(entry) != object)
        return ESTALE;
    error = mutation_load(view, object, generation, 0, child);
    if (!error && (ZFS_DIRENT_TYPE(entry) != IFTODT(child->node.mode) ||
                   child->parent != directory)) {
        mutation_release(child);
        error = EIO;
    }
    return error;
}

static int mutation_absent(aether_zpl_view *view, uint64_t directory,
                           const char *name)
{
    uint64_t entry = 0;
    int error = zap_lookup(view->os, directory, name, 8, 1, &entry);
    return error == ENOENT ? 0 : error ? error : EEXIST;
}

static int mutation_begin(dmu_tx_t *tx, aether_zpl_write_result *out)
{
    int error = dmu_tx_assign(tx, DMU_TX_WAIT);
    if (error) {
        dmu_tx_abort(tx);
        return error;
    }
    out->state =
        AETHER_ZPL_COMMITTED; /* Assigned, including zero-TXG anomaly. */
    out->txg = dmu_tx_get_txg(tx);
    return 0;
}

static int mutation_bind(dmu_tx_t *tx, aether_zpl_write_result *out)
{
    if (!out->txg)
        return EIO;
#ifdef AETHER_ZPL_ORDERED_WRITE
    return aether_pool_hooks_bind_transaction(tx);
#else
    (void)tx;
    return 0;
#endif
}

static int mutation_finish(aether_zpl_view *view, dmu_tx_t *tx, int error,
                           aether_zpl_write_result *out)
{
    dmu_tx_commit(tx);
    if (!error)
        error = txg_wait_synced_flags(spa_get_dsl(dmu_objset_spa(view->os)),
                                      out->txg, TXG_WAIT_SUSPEND);
    if (!error && spa_last_synced_txg(dmu_objset_spa(view->os)) < out->txg)
        error = EIO;
    if (!error)
        out->state = AETHER_ZPL_SYNCED;
    return error;
}

static int mutation_parent(aether_zpl_view *view, struct mutation_node *parent,
                           uint64_t size, uint64_t seconds, uint64_t nanos,
                           dmu_tx_t *tx)
{
    uint64_t time[2] = {seconds, nanos};
    uint64_t flags = parent->flags | ZFS_ARCHIVE | ZFS_AV_MODIFIED;
    sa_bulk_attr_t attrs[4];
    int n = 0;
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_SIZE], NULL, &size, 8);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_MTIME], NULL, time, 16);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_CTIME], NULL, time, 16);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_FLAGS], NULL, &flags, 8);
    return sa_bulk_update(parent->handle, attrs, n, tx);
}

int aether_zpl_create(aether_zpl_view *view, uint64_t directory,
                      uint64_t directory_generation, const unsigned char *name,
                      size_t length, uint64_t uid, uint64_t gid,
                      uint64_t seconds, uint64_t nanos,
                      aether_zpl_node *created, aether_zpl_write_result *out)
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
    if (!error && parent.node.size >= 4098)
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
    dmu_tx_hold_zap(tx, directory, B_TRUE, component);
    dmu_tx_hold_sa(tx, parent.handle, B_FALSE);
    error = mutation_begin(tx, out);
    if (error)
        goto done;
    error = mutation_bind(tx, out);
    sa_handle_t *handle = NULL;
    if (!error) {
        uint64_t object =
            dmu_object_alloc(view->os, DMU_OT_PLAIN_FILE_CONTENTS, 0, DMU_OT_SA,
                             DN_BONUS_SIZE(DNODE_MIN_SIZE), tx);
        *created = (aether_zpl_node){object, out->txg, 0, S_IFREG | 0600};
        if (!object || object >= (UINT64_C(1) << 48))
            error = EIO;
        if (!error)
            error =
                sa_handle_get(view->os, object, NULL, SA_HDL_PRIVATE, &handle);
    }
    if (!error) {
        uint64_t mode = S_IFREG | 0600, size = 0, links = 1, count = 3,
                 project = 0;
        uint64_t flags = ZFS_ARCHIVE | ZFS_AV_MODIFIED | ZFS_ACL_TRIVIAL |
                         ZFS_ACL_PROTECTED | ZFS_PROJID;
        uint64_t time[2] = {seconds, nanos};
        uint32_t common = ACE_READ_ATTRIBUTES | ACE_READ_NAMED_ATTRS |
                          ACE_READ_ACL | ACE_SYNCHRONIZE;
        zfs_ace_hdr_t acl[3] = {
            {ACE_ACCESS_ALLOWED_ACE_TYPE, ACE_OWNER,
             common | ACE_READ_DATA | ACE_WRITE_DATA | ACE_APPEND_DATA |
                 ACE_WRITE_ATTRIBUTES | ACE_WRITE_NAMED_ATTRS | ACE_WRITE_ACL |
                 ACE_WRITE_OWNER},
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
        uint64_t entry = ((uint64_t)IFTODT(S_IFREG) << 60) | created->object;
        error = zap_add(view->os, directory, component, 8, 1, &entry, tx);
    }
    if (!error)
        error = mutation_parent(view, &parent, parent.node.size + 1, seconds,
                                nanos, tx);
    error = mutation_finish(view, tx, error, out);
done:
    mutation_release(&parent);
    return error;
}

int aether_zpl_rename(aether_zpl_view *view, uint64_t directory,
                      uint64_t directory_generation, const unsigned char *from,
                      size_t from_length, const unsigned char *to,
                      size_t to_length, uint64_t object, uint64_t generation,
                      uint64_t seconds, uint64_t nanos,
                      aether_zpl_write_result *out)
{
    if (!out)
        return EINVAL;
    memset(out, 0, sizeof(*out));
    char source[256], destination[256];
    int error = mutation_input(view, seconds, nanos);
    if (!error)
        error = mutation_name(from, from_length, source);
    if (!error)
        error = mutation_name(to, to_length, destination);
    if (error)
        return error;
    struct mutation_node parent = {0}, child = {0};
    error = mutation_load(view, directory, directory_generation, 1, &parent);
    if (!error)
        error =
            mutation_entry(view, directory, source, &child, object, generation);
    if (!error && strcmp(source, destination))
        error = mutation_absent(view, directory, destination);
    if (error || !strcmp(source, destination))
        goto done;
    dmu_tx_t *tx = dmu_tx_create(view->os);
    if (!tx) {
        error = ENOMEM;
        goto done;
    }
    dmu_tx_hold_zap(tx, directory, B_TRUE, destination);
    dmu_tx_hold_zap(tx, directory, B_FALSE, source);
    dmu_tx_hold_sa(tx, parent.handle, B_FALSE);
    dmu_tx_hold_sa(tx, child.handle, B_FALSE);
    error = mutation_begin(tx, out);
    if (error)
        goto done;
    error = mutation_bind(tx, out);
    uint64_t entry = ((uint64_t)IFTODT(S_IFREG) << 60) | object;
    if (!error)
        error = zap_add(view->os, directory, destination, 8, 1, &entry, tx);
    if (!error)
        error = zap_remove(view->os, directory, source, tx);
    if (!error) {
        uint64_t time[2] = {seconds, nanos},
                 flags = child.flags | ZFS_ARCHIVE | ZFS_AV_MODIFIED;
        sa_bulk_attr_t attrs[2];
        int n = 0;
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_CTIME], NULL, time, 16);
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_FLAGS], NULL, &flags,
                         8);
        error = sa_bulk_update(child.handle, attrs, n, tx);
    }
    if (!error)
        error = mutation_parent(view, &parent, parent.node.size, seconds, nanos,
                                tx);
    error = mutation_finish(view, tx, error, out);
done:
    mutation_release(&child);
    mutation_release(&parent);
    return error;
}

int aether_zpl_remove(aether_zpl_view *view, uint64_t directory,
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
    if (!error)
        error = mutation_entry(view, directory, component, &child, object,
                               generation);
    dmu_object_info_t info;
    if (!error)
        error = dmu_object_info(view->os, object, &info);
    if (!error && info.doi_max_offset > UINT64_C(1048576))
        error = EFBIG;
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
        error = dmu_object_free(view->os, object, tx);
    error = mutation_finish(view, tx, error, out);
done:
    mutation_release(&child);
    mutation_release(&parent);
    return error;
}
