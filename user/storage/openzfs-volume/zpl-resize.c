/* SPDX-License-Identifier: BSD-2-Clause */
/* Unselected bounded shrink prerequisite; one original context implementation.
 */
#include "zpl-write.c"
#include "zpl-resize.h"

int aether_zpl_shrink(aether_zpl_view *view, uint64_t object,
                      uint64_t generation, uint64_t size, uint64_t seconds,
                      uint64_t nanoseconds, aether_zpl_write_result *out)
{
    if (!out)
        return EINVAL;
    memset(out, 0, sizeof(*out));
    if (!view || seconds > INT64_MAX || nanoseconds >= UINT64_C(1000000000))
        return EINVAL;
    if (size > INT64_MAX)
        return EFBIG;
    spa_t *spa = dmu_objset_spa(view->os);
    if (!spa_writeable(spa))
        return EROFS;
    aether_zpl_node node;
    uint64_t parent = 0;
    int error = aether_zpl_load(view, object, &node, &parent);
    if (error)
        return error;
    if (node.generation != generation)
        return ESTALE;
    if (!S_ISREG(node.mode))
        return EISDIR;
    if (node.mode & (S_ISUID | S_ISGID))
        return ENOTSUP;
    if (node.size > INT64_MAX)
        return EFBIG;
    if (size > node.size)
        return ENOTSUP;
    uint64_t tail = node.size - size;
    if (tail > UINT64_C(1048576))
        return EFBIG;

    sa_handle_t *handle = NULL;
    error = sa_handle_get(view->os, object, NULL, SA_HDL_PRIVATE, &handle);
    if (error)
        return error;
    uint64_t original_size = 0, flags = 0, mtime[2], ctime[2];
    sa_bulk_attr_t attributes[4];
    int n = 0;
    SA_ADD_BULK_ATTR(attributes, n, view->attributes[ZPL_SIZE], NULL,
                     &original_size, sizeof(original_size));
    SA_ADD_BULK_ATTR(attributes, n, view->attributes[ZPL_FLAGS], NULL, &flags,
                     sizeof(flags));
    SA_ADD_BULK_ATTR(attributes, n, view->attributes[ZPL_MTIME], NULL, mtime,
                     sizeof(mtime));
    SA_ADD_BULK_ATTR(attributes, n, view->attributes[ZPL_CTIME], NULL, ctime,
                     sizeof(ctime));
    error = sa_bulk_lookup(handle, attributes, n);
    if (error)
        goto done;
    if (original_size != node.size) {
        error = EIO;
        goto done;
    }
    if (flags & (ZFS_IMMUTABLE | ZFS_APPENDONLY | ZFS_READONLY | ZFS_XATTR)) {
        error = EPERM;
        goto done;
    }
    if (!tail)
        goto done;
    dmu_tx_t *tx = dmu_tx_create(view->os);
    if (!tx) {
        error = ENOMEM;
        goto done;
    }
    dmu_tx_hold_free(tx, object, size, tail);
    dmu_tx_hold_sa(tx, handle, B_FALSE);
    dmu_tx_mark_netfree(tx);
    error = dmu_tx_assign(tx, DMU_TX_WAIT);
    if (error) {
        dmu_tx_abort(tx);
        goto done;
    }
    out->txg = dmu_tx_get_txg(tx);
    if (!out->txg)
        error = EIO;
#ifdef AETHER_ZPL_ORDERED_WRITE
    else
        error = aether_pool_hooks_bind_transaction(tx);
#endif
    if (!error)
        error = dmu_free_range(view->os, object, size, tail, tx);
    if (!error) {
        original_size = size;
        mtime[0] = ctime[0] = seconds;
        mtime[1] = ctime[1] = nanoseconds;
        flags |= ZFS_ARCHIVE | ZFS_AV_MODIFIED;
        error = sa_bulk_update(handle, attributes, n, tx);
    }
    /* Freeing can succeed before SA fails: the assigned transaction must
     * commit and its progress must survive every error, just like writes. */
    dmu_tx_commit(tx);
    out->state = AETHER_ZPL_COMMITTED;
    if (!error)
        error =
            txg_wait_synced_flags(spa_get_dsl(spa), out->txg, TXG_WAIT_SUSPEND);
    if (!error && spa_last_synced_txg(spa) < out->txg)
        error = EIO;
    if (!error)
        out->state = AETHER_ZPL_SYNCED;
done:
    sa_handle_destroy(handle);
    return error;
}
