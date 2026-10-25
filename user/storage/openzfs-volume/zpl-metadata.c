/* SPDX-License-Identifier: BSD-2-Clause */
/* Additive unselected provider; original DMU/SA owns on-disk decoding. */
#include "zpl-directories.c"
#include "zpl-metadata.h"

int aether_zpl_getattr(aether_zpl_view *view, uint64_t object,
                       uint64_t generation, aether_zpl_metadata *out)
{
    if (!out)
        return EINVAL;
    memset(out, 0, sizeof(*out));
    if (!view || !object || !generation)
        return EINVAL;
    aether_zpl_metadata metadata = {0};
    int error = aether_zpl_load(view, object, &metadata.node, &metadata.parent);
    if (error)
        return error;
    if (metadata.node.generation != generation)
        return ESTALE;
    sa_handle_t *handle = NULL;
    error = sa_handle_get(view->os, object, NULL, SA_HDL_PRIVATE, &handle);
    if (error)
        return error;
    sa_bulk_attr_t attrs[8];
    int n = 0;
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_LINKS], NULL,
                     &metadata.links, 8);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_UID], NULL, &metadata.uid,
                     8);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_GID], NULL, &metadata.gid,
                     8);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_FLAGS], NULL,
                     &metadata.flags, 8);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_ATIME], NULL,
                     &metadata.atime, 16);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_MTIME], NULL,
                     &metadata.mtime, 16);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_CTIME], NULL,
                     &metadata.ctime, 16);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_CRTIME], NULL,
                     &metadata.birthtime, 16);
    error = sa_bulk_lookup(handle, attrs, n);
    sa_handle_destroy(handle);
    if (error)
        return error;
    if (!metadata.links)
        return ENOENT;
    if (metadata.flags & ZFS_XATTR)
        return ENOTSUP;
    const aether_zpl_time *times[] = {&metadata.atime, &metadata.mtime,
                                      &metadata.ctime, &metadata.birthtime};
    for (size_t i = 0; i < sizeof(times) / sizeof(times[0]); ++i)
        if (times[i]->nanoseconds >= UINT64_C(1000000000))
            return EIO;
    *out = metadata;
    return 0;
}
