/* SPDX-License-Identifier: BSD-2-Clause */
/* Private assigned-data helper; selected only by explicit --pool-data.
 * Caller holds a live SPA borrow, with no concurrent export or dataset
 * mutation. Return values describe DMU wait/readback only, never durable
 * acknowledgment. Original ordered I/O and final drain must be checked
 * separately. */
#include <sys/dmu.h>
#include <sys/dmu_tx.h>
#include <sys/dmu_objset.h>
#include <sys/spa.h>
#include <sys/txg.h>
#include <string.h>

#define AETHER_DATASET "aether_pool_probe/data_probe"
#define AETHER_DATA_OBJECT 1
#define AETHER_DATA_BYTES 64
#define AETHER_DATA_BLOCK 4096

extern int aether_pool_hooks_bind_transaction(dmu_tx_t *);

static void aether_data_record(unsigned char *record, uint64_t target)
{
    memcpy(record, "AETHDMU1", 8);
    for (unsigned i = 0; i < 8; ++i)
        record[8 + i] = (unsigned char)(target >> (8 * i));
    for (unsigned i = 16; i < AETHER_DATA_BYTES; ++i)
        record[i] = (unsigned char)((i * 73) ^ i ^ (target >> (8 * (i % 8))));
}

static void aether_data_create(objset_t *os, void *arg, cred_t *cr,
                               dmu_tx_t *tx)
{
    (void)cr;
    /* Original create waits for this sync callback before returning; arg is
     * borrowed from that caller's stack. This is not the selected data tx. */
    *(int *)arg = dmu_object_claim(os, AETHER_DATA_OBJECT, DMU_OT_PLAIN_OTHER,
                                   AETHER_DATA_BLOCK, DMU_OT_NONE, 0, tx);
}

int aether_pool_data_write(spa_t *spa, uint64_t *assigned_target)
{
    if (!spa || !assigned_target || !spa_writeable(spa) ||
        strcmp(spa_name(spa), "aether_pool_probe"))
        return EINVAL;
    int claimed = EIO;
    int error = dmu_objset_create(AETHER_DATASET, DMU_OST_OTHER, 0, NULL,
                                  aether_data_create, &claimed);
    if (error || claimed)
        return error ? error : claimed;
    objset_t *os = NULL;
    error = dmu_objset_own(AETHER_DATASET, DMU_OST_OTHER, B_FALSE, B_FALSE,
                           FTAG, &os);
    if (error)
        return error;
    if (dmu_objset_spa(os) != spa) {
        dmu_objset_disown(os, B_FALSE, FTAG);
        return EXDEV;
    }
    dmu_tx_t *tx = dmu_tx_create(os);
    dmu_tx_hold_write(tx, AETHER_DATA_OBJECT, 0, AETHER_DATA_BYTES);
    error = dmu_tx_assign(tx, DMU_TX_WAIT);
    if (error) {
        dmu_tx_abort(tx);
        dmu_objset_disown(os, B_FALSE, FTAG);
        return error;
    }
    /* Assignment holds this TXG through commit; capture/join before commit
     * destroys tx. Even a failed join must release an assigned tx by commit. */
    uint64_t target = dmu_tx_get_txg(tx);
    error = target ? aether_pool_hooks_bind_transaction(tx) : EINVAL;
    unsigned char record[AETHER_DATA_BYTES], readback[AETHER_DATA_BYTES];
    if (!error) {
        aether_data_record(record, target);
        dmu_write(os, AETHER_DATA_OBJECT, 0, sizeof(record), record, tx,
                  DMU_READ_NO_PREFETCH);
    }
    dmu_tx_commit(tx);
    if (!error)
        error =
            txg_wait_synced_flags(spa_get_dsl(spa), target, TXG_WAIT_SUSPEND);
    if (!error)
        error = dmu_read(os, AETHER_DATA_OBJECT, 0, sizeof(readback), readback,
                         DMU_READ_NO_PREFETCH);
    if (!error && memcmp(record, readback, sizeof(record)))
        error = EIO;
    dmu_objset_disown(os, B_FALSE, FTAG);
    if (!error)
        *assigned_target = target;
    return error;
}

#ifdef AETHER_POOL_CAPACITY_PROBE
#include <sys/dsl_dataset.h>
/* Original refreservation checks capacity in syncing context before changing
 * the property. A scalar request allocates no corresponding caller buffer. */
int aether_pool_data_capacity(spa_t *spa, uint64_t baseline)
{
    const uint64_t reservation = UINT64_C(128) * 1024 * 1024;
    if (!spa || !baseline || !spa_writeable(spa) ||
        strcmp(spa_name(spa), "aether_pool_probe") ||
        baseline > spa_last_synced_txg(spa))
        return EINVAL;
    objset_t *os = NULL;
    int error = dmu_objset_own(AETHER_DATASET, DMU_OST_OTHER, B_FALSE, B_FALSE,
                               FTAG, &os);
    if (error)
        return error;
    if (dmu_objset_spa(os) != spa) {
        dmu_objset_disown(os, B_FALSE, FTAG);
        return EXDEV;
    }
    /* os owns this dataset throughout the synchronous check; there are no
     * concurrent property callers in this private fixture. */
    dsl_dataset_t *ds = dmu_objset_ds(os);
    if (dsl_get_refreservation(ds)) {
        dmu_objset_disown(os, B_FALSE, FTAG);
        return EINVAL;
    }
    error = dsl_dataset_set_refreservation(AETHER_DATASET, ZPROP_SRC_LOCAL,
                                           reservation);
    if (error == ENOSPC) {
        if (dsl_get_refreservation(ds)) {
            error = EIO;
        } else {
            unsigned char record[AETHER_DATA_BYTES],
                expected[AETHER_DATA_BYTES];
            aether_data_record(expected, baseline);
            error = dmu_read(os, AETHER_DATA_OBJECT, 0, sizeof(record), record,
                             DMU_READ_NO_PREFETCH);
            if (!error && memcmp(record, expected, sizeof(record)))
                error = EIO;
        }
    } else if (!error) {
        /* Never report a successful write, or hide an unexpected property
         * change by restoring it. Stop acceptance and retain the failure. */
        error = EIO;
    }
    dmu_objset_disown(os, B_FALSE, FTAG);
    return error;
}
#endif

#ifdef AETHER_POOL_UNCOMMITTED
/* Private stop boundary: the caller retains its SPA borrow and has already
 * validated the baseline's data and ordered sync. Assignment holds the new
 * TXG from syncing until commit; keep that hold and dataset ownership while
 * parked. A returning checkpoint is always failure, never an acknowledgment. */
int aether_pool_data_hold(spa_t *spa, uint64_t baseline)
{
    if (!spa || !baseline || !spa_writeable(spa) ||
        strcmp(spa_name(spa), "aether_pool_probe") ||
        baseline > spa_last_synced_txg(spa))
        return EINVAL;
    objset_t *os = NULL;
    int error = dmu_objset_own(AETHER_DATASET, DMU_OST_OTHER, B_FALSE, B_FALSE,
                               FTAG, &os);
    if (error)
        return error;
    if (dmu_objset_spa(os) != spa) {
        dmu_objset_disown(os, B_FALSE, FTAG);
        return EXDEV;
    }
    dmu_tx_t *tx = dmu_tx_create(os);
    dmu_tx_hold_write(tx, AETHER_DATA_OBJECT, 0, AETHER_DATA_BYTES);
    error = dmu_tx_assign(tx, DMU_TX_WAIT);
    if (error) {
        dmu_tx_abort(tx);
        dmu_objset_disown(os, B_FALSE, FTAG);
        return error;
    }
    uint64_t candidate = dmu_tx_get_txg(tx);
    error = EINVAL;
    if (candidate > baseline) {
        unsigned char record[AETHER_DATA_BYTES];
        aether_data_record(record, candidate);
        dmu_write(os, AETHER_DATA_OBJECT, 0, sizeof(record), record, tx,
                  DMU_READ_NO_PREFETCH);
        extern int aether_engine_pool_uncommitted(uint64_t);
        (void)aether_engine_pool_uncommitted(candidate);
        error = EIO;
    }
    /* An assigned transaction must commit even on error, never abort. The
     * healthy checkpoint never returns; these releases cannot claim recovery.
     */
    dmu_tx_commit(tx);
    dmu_objset_disown(os, B_FALSE, FTAG);
    return error;
}
#endif

int aether_pool_data_read(spa_t *spa, uint64_t *record_target)
{
    if (!spa || !record_target || spa_writeable(spa) ||
        strcmp(spa_name(spa), "aether_pool_probe"))
        return EINVAL;
    objset_t *os = NULL;
    int error = dmu_objset_own(AETHER_DATASET, DMU_OST_OTHER, B_TRUE, B_FALSE,
                               FTAG, &os);
    if (error)
        return error;
    dmu_object_info_t info;
    unsigned char record[AETHER_DATA_BYTES], expected[AETHER_DATA_BYTES];
    uint64_t target = 0;
    if (dmu_objset_spa(os) != spa)
        error = EXDEV;
    if (!error)
        error = dmu_object_info(os, AETHER_DATA_OBJECT, &info);
    if (!error && (info.doi_type != DMU_OT_PLAIN_OTHER ||
                   info.doi_data_block_size != AETHER_DATA_BLOCK ||
                   info.doi_bonus_type != DMU_OT_NONE || info.doi_bonus_size))
        error = EINVAL;
    if (!error)
        error = dmu_read(os, AETHER_DATA_OBJECT, 0, sizeof(record), record,
                         DMU_READ_NO_PREFETCH);
    if (!error) {
        for (unsigned i = 0; i < 8; ++i)
            target |= (uint64_t)record[8 + i] << (8 * i);
        aether_data_record(expected, target);
        if (!target || target > spa_last_synced_txg(spa) ||
            memcmp(record, expected, sizeof(record)))
            error = EIO;
    }
    dmu_objset_disown(os, B_FALSE, FTAG);
    if (!error)
        *record_target = target;
    return error;
}
