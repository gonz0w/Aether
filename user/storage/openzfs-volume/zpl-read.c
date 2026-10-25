/* SPDX-License-Identifier: BSD-2-Clause */
/* Read-only ZPL5 prerequisite. Upstream ZAP/SA/DMU own all disk decoding.
 * See zpl-read.h and OPENZFS-FEASIBILITY: this is not a namespace writer, a
 * mounted filesystem, a POSIX adapter or a capability protocol. */
#include <sys/dmu.h>
#include <sys/dmu_objset.h>
#include <sys/sa.h>
#include <sys/spa.h>
#include <sys/stat.h>
#include <sys/zap.h>
#include <sys/zfs_znode.h>
#include <sys/zfs_sa.h>
#include <string.h>
#include "zpl-read.h"

struct aether_zpl_view {
    objset_t *os;
    sa_attr_type_t *attributes; /* Owned by os, never freed separately. */
    aether_zpl_node root;
};

/* Inspect geometry before SA acquisition, as upstream zfs_grab_sa_handle does.
 * This slice intentionally supports SA only, not legacy znode_phys_t. */
static int aether_zpl_load(aether_zpl_view *view, uint64_t object,
                           aether_zpl_node *node, uint64_t *parent)
{
    if (!object)
        return EIO;
    dmu_object_info_t info;
    int error = dmu_object_info(view->os, object, &info);
    if (error)
        return error;
    if (info.doi_bonus_type != DMU_OT_SA)
        return ENOTSUP;
    if (info.doi_type != DMU_OT_DIRECTORY_CONTENTS &&
        info.doi_type != DMU_OT_PLAIN_FILE_CONTENTS)
        return ENOTSUP;
    sa_handle_t *handle = NULL;
    error = sa_handle_get(view->os, object, NULL, SA_HDL_PRIVATE, &handle);
    if (error)
        return error;
    uint64_t mode = 0, generation = 0, size = 0, links = 0, up = 0, flags = 0;
    sa_bulk_attr_t attributes[6];
    int n = 0;
    SA_ADD_BULK_ATTR(attributes, n, view->attributes[ZPL_MODE], NULL, &mode,
                     sizeof(mode));
    SA_ADD_BULK_ATTR(attributes, n, view->attributes[ZPL_GEN], NULL,
                     &generation, sizeof(generation));
    SA_ADD_BULK_ATTR(attributes, n, view->attributes[ZPL_SIZE], NULL, &size,
                     sizeof(size));
    SA_ADD_BULK_ATTR(attributes, n, view->attributes[ZPL_LINKS], NULL, &links,
                     sizeof(links));
    SA_ADD_BULK_ATTR(attributes, n, view->attributes[ZPL_PARENT], NULL, &up,
                     sizeof(up));
    SA_ADD_BULK_ATTR(attributes, n, view->attributes[ZPL_FLAGS], NULL, &flags,
                     sizeof(flags));
    error = sa_bulk_lookup(handle, attributes, n);
    sa_handle_destroy(handle);
    if (error)
        return error;
    if (!generation || !up)
        return EIO;
    if (!links)
        return ENOENT;
    if (flags & ZFS_XATTR)
        return ENOTSUP;
    if (!S_ISDIR(mode) && !S_ISREG(mode))
        return ENOTSUP;
    if ((S_ISDIR(mode) && info.doi_type != DMU_OT_DIRECTORY_CONTENTS) ||
        (S_ISREG(mode) && info.doi_type != DMU_OT_PLAIN_FILE_CONTENTS))
        return EIO;
    *node = (aether_zpl_node){object, generation, size, mode};
    *parent = up;
    return 0;
}

void aether_zpl_close(aether_zpl_view **owned)
{
    if (!owned || !*owned)
        return;
    aether_zpl_view *view = *owned;
    *owned = NULL;
    if (view->os)
        dmu_objset_disown(view->os, B_FALSE, view);
    memset(view, 0, sizeof(*view));
    kmem_free(view, sizeof(*view));
}

/* The writer compiles this same implementation in its own replacement unit.
 * Preserve the qualified reader's function order and constant readonly mode. */
#ifdef AETHER_ZPL_WRITE_PROVIDER
enum aether_zpl_open_kind {
    AETHER_ZPL_OPEN_READ,
    AETHER_ZPL_PROBE_WRITE,
    AETHER_ZPL_OWN_WRITE
};
static int aether_zpl_open_mode(spa_t *spa, const char *dataset,
                                aether_zpl_view **out,
                                enum aether_zpl_open_kind kind)
#else
int aether_zpl_open(spa_t *spa, const char *dataset, aether_zpl_view **out)
#endif
{
    if (!out)
        return EINVAL;
    *out = NULL;
    if (!spa || !dataset || !*dataset)
        return EINVAL;
#ifdef AETHER_ZPL_WRITE_PROVIDER
    if (kind != AETHER_ZPL_OPEN_READ ? !spa_writeable(spa) : spa_writeable(spa))
#else
    if (spa_writeable(spa))
#endif
        return EROFS;
    aether_zpl_view *view = kmem_zalloc(sizeof(*view), KM_NOSLEEP);
    if (!view)
        return ENOMEM;
    /* own_impl can set its out pointer and then fail a type check. Only a
     * successful own transfers a longhold which this context may disown. */
    objset_t *os = NULL;
    int error =
#ifdef AETHER_ZPL_WRITE_PROVIDER
        dmu_objset_own(dataset, DMU_OST_ZFS,
                       kind == AETHER_ZPL_OWN_WRITE ? B_FALSE : B_TRUE,
                       B_FALSE, view, &os);
#else
        dmu_objset_own(dataset, DMU_OST_ZFS, B_TRUE, B_FALSE, view, &os);
#endif
    if (error)
        goto fail;
    view->os = os;
    if (dmu_objset_spa(view->os) != spa) {
        error = EXDEV;
        goto fail;
    }
    if (view->os->os_encrypted) {
        error = ENOTSUP;
        goto fail;
    }
    dmu_object_info_t info;
    error = dmu_object_info(view->os, MASTER_NODE_OBJ, &info);
    if (error)
        goto fail;
    if (info.doi_type != DMU_OT_MASTER_NODE) {
        error = EIO;
        goto fail;
    }
    uint64_t version = 0, norm = 0, sense = 0, utf8 = 0, sa = 0, root = 0;
    /* VERSION must exist; do not accept zfs_get_zplprop's default on a bare
     * DMU_OST_ZFS objset (libzpool does not populate a root ZPL itself). */
    error =
        zap_lookup(view->os, MASTER_NODE_OBJ, ZPL_VERSION_STR, 8, 1, &version);
    if (!error)
        error = zfs_get_zplprop(view->os, ZFS_PROP_NORMALIZE, &norm);
    if (!error)
        error = zfs_get_zplprop(view->os, ZFS_PROP_CASE, &sense);
    if (!error)
        error = zfs_get_zplprop(view->os, ZFS_PROP_UTF8ONLY, &utf8);
    if (error)
        goto fail;
    if (version != ZPL_VERSION_SA || norm || sense != ZFS_CASE_SENSITIVE ||
        utf8) {
        error = ENOTSUP;
        goto fail;
    }
    error = zap_lookup(view->os, MASTER_NODE_OBJ, ZFS_SA_ATTRS, 8, 1, &sa);
    if (!error && !sa)
        error = EIO;
    if (!error)
        error = dmu_object_info(view->os, sa, &info);
    if (!error && info.doi_type != DMU_OT_SA_MASTER_NODE)
        error = EIO;
    if (!error)
        error =
            sa_setup(view->os, sa, zfs_attr_table, ZPL_END, &view->attributes);
    if (!error)
        error =
            zap_lookup(view->os, MASTER_NODE_OBJ, ZFS_ROOT_OBJ, 8, 1, &root);
    uint64_t parent = 0;
    if (!error)
        error = aether_zpl_load(view, root, &view->root, &parent);
    if (!error && (!S_ISDIR(view->root.mode) || parent != root))
        error = EIO;
    if (!error) {
        *out = view;
        return 0;
    }
fail:
    aether_zpl_close(&view);
    return error;
}

#ifdef AETHER_ZPL_WRITE_PROVIDER
int aether_zpl_open(spa_t *spa, const char *dataset, aether_zpl_view **out)
{
    return aether_zpl_open_mode(spa, dataset, out, AETHER_ZPL_OPEN_READ);
}
#endif

int aether_zpl_root(aether_zpl_view *view, aether_zpl_node *out)
{
    if (!out)
        return EINVAL;
    memset(out, 0, sizeof(*out));
    if (!view)
        return EINVAL;
    aether_zpl_node root;
    uint64_t parent = 0;
    int error = aether_zpl_load(view, view->root.object, &root, &parent);
    if (error)
        return error;
    if (root.generation != view->root.generation)
        return ESTALE;
    if (!S_ISDIR(root.mode) || parent != root.object)
        return EIO;
    *out = root;
    return 0;
}

int aether_zpl_lookup(aether_zpl_view *view, uint64_t directory,
                      uint64_t generation, const unsigned char *name,
                      size_t length, aether_zpl_node *out)
{
    if (!out)
        return EINVAL;
    memset(out, 0, sizeof(*out));
    if (!view || !name || !length || length > 255)
        return EINVAL;
    if ((length == 1 && name[0] == '.') ||
        (length == 2 && name[0] == '.' && name[1] == '.'))
        return EINVAL;
    for (size_t i = 0; i < length; ++i)
        if (!name[i] || name[i] == '/')
            return EINVAL;
    aether_zpl_node dir, node;
    uint64_t parent = 0;
    int error = aether_zpl_load(view, directory, &dir, &parent);
    if (error)
        return error;
    if (dir.generation != generation)
        return ESTALE;
    if (!S_ISDIR(dir.mode))
        return ENOTDIR;
    char component[256];
    memcpy(component, name, length);
    component[length] = 0;
    uint64_t entry = 0;
    error = zap_lookup(view->os, directory, component, 8, 1, &entry);
    if (error)
        return error;
    if ((entry >> 48) & 0xfff)
        return EIO;
    error = aether_zpl_load(view, ZFS_DIRENT_OBJ(entry), &node, &parent);
    if (error)
        return error;
    if (ZFS_DIRENT_TYPE(entry) != IFTODT(node.mode) ||
        (S_ISDIR(node.mode) && parent != directory))
        return EIO;
    *out = node;
    return 0;
}

int aether_zpl_read(aether_zpl_view *view, uint64_t object, uint64_t generation,
                    uint64_t offset, void *buffer, size_t length, size_t *count)
{
    if (!count)
        return EINVAL;
    *count = 0;
    if (!view || length > 4096 || (!buffer && length))
        return EINVAL;
    if (length)
        memset(buffer, 0, length);
    if (length > UINT64_MAX - offset)
        return EINVAL;
    aether_zpl_node node;
    uint64_t parent = 0;
    int error = aether_zpl_load(view, object, &node, &parent);
    if (error)
        return error;
    if (node.generation != generation)
        return ESTALE;
    if (!S_ISREG(node.mode))
        return EISDIR;
    if (!length || offset >= node.size)
        return 0;
    size_t bytes = length;
    if (node.size - offset < bytes)
        bytes = (size_t)(node.size - offset);
    error =
        dmu_read(view->os, object, offset, bytes, buffer, DMU_READ_NO_PREFETCH);
    if (error) {
        memset(buffer, 0, length);
        return error;
    }
    *count = bytes;
    return 0;
}
