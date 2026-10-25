/* SPDX-License-Identifier: BSD-2-Clause */
/* Unselected private prerequisite. Reuse one reader/open implementation, not a
 * second decoder or a parallel context layout. Compile this unit instead of the
 * reader only in an explicitly qualified writable experiment. */
#define AETHER_ZPL_WRITE_PROVIDER 1
#include "zpl-read.c"
#include "zpl-write.h"
#include <sys/dmu_tx.h>
#include <sys/dsl_prop.h>
#include <sys/txg.h>

#ifdef AETHER_ZPL_ORDERED_WRITE
extern int aether_pool_hooks_bind_transaction(dmu_tx_t *);
#endif

int aether_zpl_open_write(spa_t *spa, const char *dataset,
                          aether_zpl_view **out)
{
    if (!out)
        return EINVAL;
    *out = NULL;
    aether_zpl_view *view = NULL;
    /* Writable own can launch original accounting upgrades. Validate format,
     * properties and upgrade completeness using readonly ownership first. */
    int error =
        aether_zpl_open_mode(spa, dataset, &view, AETHER_ZPL_PROBE_WRITE);
    uint64_t readonly = 0;
    if (!error)
        error = dsl_prop_get_integer(dataset, "readonly", &readonly, NULL);
    if (!error && readonly)
        error = EROFS;
    if (!error && dmu_objset_is_snapshot(view->os))
        error = EROFS;
    /* A callback-free libzpool can report accounting disabled even though
     * existing dnodes carry accounted flags. Sync would assert or corrupt
     * accounting. The owner must register the original ZPL callback first. */
    if (!error && (!dmu_objset_userused_enabled(view->os) ||
                   dmu_objset_userobjspace_upgradable(view->os) ||
                   dmu_objset_projectquota_upgradable(view->os) ||
                   !dmu_objset_userspace_present(view->os)))
        error = ENOTSUP;
    /* Drop all borrowed SA pointers before reacquiring write ownership. The
     * trusted caller excludes property/dataset changes across this transition.
     * Revalidate using the new context; never reuse a pointer from the probe.
     */
    aether_zpl_close(&view);
    if (error)
        return error;
    return aether_zpl_open_mode(spa, dataset, out, AETHER_ZPL_OWN_WRITE);
}

int aether_zpl_write(aether_zpl_view *view, uint64_t object,
                     uint64_t generation, uint64_t offset, const void *buffer,
                     size_t length, uint64_t seconds, uint64_t nanoseconds,
                     aether_zpl_write_result *out)
{
    if (!out)
        return EINVAL;
    memset(out, 0, sizeof(*out));
    if (!view || length > 4096 || (!buffer && length) || seconds > INT64_MAX ||
        nanoseconds >= UINT64_C(1000000000))
        return EINVAL;
    if (offset > INT64_MAX || length > INT64_MAX - offset)
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
    if (offset > node.size)
        return EINVAL;

    sa_handle_t *handle = NULL;
    error = sa_handle_get(view->os, object, NULL, SA_HDL_PRIVATE, &handle);
    if (error)
        return error;
    uint64_t size = 0, flags = 0, mtime[2], ctime[2];
    sa_bulk_attr_t attributes[4];
    int n = 0;
    SA_ADD_BULK_ATTR(attributes, n, view->attributes[ZPL_SIZE], NULL, &size,
                     sizeof(size));
    SA_ADD_BULK_ATTR(attributes, n, view->attributes[ZPL_FLAGS], NULL, &flags,
                     sizeof(flags));
    SA_ADD_BULK_ATTR(attributes, n, view->attributes[ZPL_MTIME], NULL, mtime,
                     sizeof(mtime));
    SA_ADD_BULK_ATTR(attributes, n, view->attributes[ZPL_CTIME], NULL, ctime,
                     sizeof(ctime));
    /* All attributes must already exist. The transaction does not grow SA. */
    error = sa_bulk_lookup(handle, attributes, n);
    if (error)
        goto done;
    if (size != node.size) {
        error = EIO;
        goto done;
    }
    if (flags & (ZFS_IMMUTABLE | ZFS_APPENDONLY | ZFS_READONLY | ZFS_XATTR)) {
        error = EPERM;
        goto done;
    }
    if (!length)
        goto done;
    /* Own a stable copy before assignment can sleep. No caller memory is
     * consulted while holding the assigned transaction. */
    unsigned char staged[4096];
    memcpy(staged, buffer, length);
    dmu_tx_t *tx = dmu_tx_create(view->os);
    if (!tx) {
        error = ENOMEM;
        goto done;
    }
    dmu_tx_hold_write(tx, object, offset, length);
    dmu_tx_hold_sa(tx, handle, B_FALSE);
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
    if (!error) {
        dmu_write(view->os, object, offset, length, staged, tx,
                  DMU_READ_NO_PREFETCH);
        out->bytes_staged = length;
        uint64_t end = offset + length;
        if (size < end)
            size = end;
        mtime[0] = ctime[0] = seconds;
        mtime[1] = ctime[1] = nanoseconds;
        flags |= ZFS_ARCHIVE | ZFS_AV_MODIFIED;
        error = sa_bulk_update(handle, attributes, n, tx);
    }
    /* Assignment is irreversible here: release by commit on every path.
     * SA errors can follow a dirty data write; retain that progress verbatim.
     */
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
