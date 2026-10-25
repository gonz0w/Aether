/* SPDX-License-Identifier: BSD-2-Clause */
/* Actual provider over deterministic API doubles, not a disk decoder. Common
 * reader doubles are generated from the existing fixture's definition prefix.
 */
static int tx_live, snapshot, own_attempts, writable_owns, allocations, frees;
#include "zpl-test-common.inc"
#include "zpl-write.h"

#define ZPL_MTIME 1
#define ZPL_CTIME 2
#define ZFS_ARCHIVE 2
#define ZFS_AV_MODIFIED 4
#define ZFS_IMMUTABLE 8
#define ZFS_APPENDONLY 16
#define ZFS_READONLY 32
#define DMU_TX_WAIT 1
#define TXG_WAIT_SUSPEND 1

typedef struct {
    int assigned, data_hold, sa_hold;
} dmu_tx_t;
static dmu_tx_t transaction;
static int stage, creates, commits, aborts, writes, updates, waits, last_checks;
static int property_error, metadata_size_error, mutate_input;
static int upgrade_mode;
static uint64_t readonly_property, synced = 41, modified[2], changed[2];
static unsigned char disk[8192], input[4096], expected[4096];
static char order[64];
static size_t order_length;
#ifdef AETHER_ZPL_ORDERED_WRITE
static int joins;
#endif
static int dmu_objset_is_snapshot(objset_t *os)
{
    CHECK(os == &dataset && owned);
    return snapshot;
}
static int dmu_objset_userobjspace_upgradable(objset_t *os)
{
    CHECK(os == &dataset && owned);
    return upgrade_mode == 1;
}
static int dmu_objset_projectquota_upgradable(objset_t *os)
{
    CHECK(os == &dataset && owned);
    return upgrade_mode == 2;
}
static int dmu_objset_userused_enabled(objset_t *os)
{
    CHECK(os == &dataset && owned);
    return upgrade_mode != 4;
}
static int dmu_objset_userspace_present(objset_t *os)
{
    CHECK(os == &dataset && owned);
    return upgrade_mode != 3;
}
static void note(char c)
{
    CHECK(order_length < sizeof(order));
    order[order_length++] = c;
}

#ifdef AETHER_ZPL_ORDERED_WRITE
static int aether_pool_hooks_bind_transaction(dmu_tx_t *tx)
{
    CHECK(tx == &transaction && tx_live && tx->assigned && !joins && !writes &&
          !updates && !commits && order_length &&
          order[order_length - 1] == 'G');
    ++joins;
    note('J');
    return stage == 7 ? EIO : stage == 8 ? EXDEV : stage == 9 ? EALREADY : 0;
}
#endif

static int dsl_prop_get_integer(const char *name, const char *property,
                                uint64_t *out, char *setpoint)
{
    CHECK(!strcmp(name, "test/files") && !strcmp(property, "readonly") &&
          !setpoint && owned);
    int error = fail();
    if (error || property_error)
        return EIO;
    *out = readonly_property;
    return 0;
}

static int sa_bulk_lookup(sa_handle_t *p, sa_bulk_attr_t *attrs, int n)
{
    if (n == 6)
        return reader_sa_bulk_lookup(p, attrs, n);
    CHECK(p == &handle && handles == 1 && n == 4 && p->object == 4);
    int error = fail();
    if (error)
        return error;
    for (int i = 0; i < n; ++i) {
        int id = attrs[i].attr;
        if (id == mapping[ZPL_SIZE]) {
            CHECK(attrs[i].bytes == 8);
            uint64_t value = nodes[4].size + metadata_size_error;
            memcpy(attrs[i].value, &value, 8);
        } else if (id == mapping[ZPL_FLAGS]) {
            CHECK(attrs[i].bytes == 8);
            memcpy(attrs[i].value, &nodes[4].flags, 8);
        } else {
            CHECK(attrs[i].bytes == 16);
            CHECK(id == mapping[ZPL_MTIME] || id == mapping[ZPL_CTIME]);
            memcpy(attrs[i].value,
                   id == mapping[ZPL_MTIME] ? modified : changed, 16);
        }
    }
    return 0;
}

static dmu_tx_t *dmu_tx_create(objset_t *os)
{
    CHECK(os == &dataset && owned && handles && !tx_live && !creates);
    ++creates;
    note('C');
    if (stage == 1)
        return NULL;
    tx_live = 1;
    return &transaction;
}
static void dmu_tx_hold_write(dmu_tx_t *tx, uint64_t object, uint64_t offset,
                              size_t length)
{
    CHECK(tx == &transaction && tx_live && !tx->assigned && object == 4 &&
          offset <= nodes[4].size && length && length <= 4096);
    tx->data_hold = 1;
    note('D');
}
static void dmu_tx_hold_sa(dmu_tx_t *tx, sa_handle_t *p, int grow)
{
    CHECK(tx == &transaction && tx_live && !tx->assigned && p == &handle &&
          handles && grow == B_FALSE);
    tx->sa_hold = 1;
    note('S');
}
static int dmu_tx_assign(dmu_tx_t *tx, int flags)
{
    CHECK(tx == &transaction && tx_live && !tx->assigned && tx->data_hold &&
          tx->sa_hold && flags == DMU_TX_WAIT);
    note('A');
    if (stage == 2)
        return ENOSPC;
    tx->assigned = 1;
    if (mutate_input)
        memset(input, 0xee, sizeof(input));
    return 0;
}
static uint64_t dmu_tx_get_txg(dmu_tx_t *tx)
{
    CHECK(tx == &transaction && tx_live && tx->assigned);
    note('G');
    return stage == 3 ? 0 : 42;
}
static void dmu_write(objset_t *os, uint64_t object, uint64_t offset,
                      size_t length, const void *bytes, dmu_tx_t *tx, int flags)
{
#ifdef AETHER_ZPL_ORDERED_WRITE
    CHECK(joins == 1 && stage < 7);
#endif
    CHECK(os == &dataset && object == 4 && tx == &transaction && tx_live &&
          tx->assigned && handles && flags == DMU_READ_NO_PREFETCH && !writes &&
          offset <= sizeof(disk) && length <= sizeof(disk) - offset);
    CHECK(memcmp(bytes, expected, length) == 0);
    memcpy(disk + offset, bytes, length);
    ++writes;
    note('W');
}
static int sa_bulk_update(sa_handle_t *p, sa_bulk_attr_t *attrs, int n,
                          dmu_tx_t *tx)
{
    CHECK(p == &handle && handles && tx == &transaction && tx_live &&
          tx->assigned && writes == 1 && n == 4 && !updates);
    ++updates;
    note('U');
    for (int i = 0; i < n; ++i) {
        int id = attrs[i].attr;
        if (id == mapping[ZPL_SIZE]) {
            CHECK(attrs[i].bytes == 8);
            memcpy(&nodes[4].size, attrs[i].value, 8);
        } else if (id == mapping[ZPL_FLAGS]) {
            CHECK(attrs[i].bytes == 8);
            memcpy(&nodes[4].flags, attrs[i].value, 8);
        } else {
            CHECK(attrs[i].bytes == 16);
            CHECK(id == mapping[ZPL_MTIME] || id == mapping[ZPL_CTIME]);
            memcpy(id == mapping[ZPL_MTIME] ? modified : changed,
                   attrs[i].value, 16);
        }
        if (stage == 4)
            return EIO; /* May already have changed size. */
    }
    return 0;
}
static void dmu_tx_commit(dmu_tx_t *tx)
{
    CHECK(tx == &transaction && tx_live && tx->assigned && !commits && !aborts);
    ++commits;
    tx_live = 0;
    note('K');
}
static void dmu_tx_abort(dmu_tx_t *tx)
{
    CHECK(tx == &transaction && tx_live && !tx->assigned && !commits &&
          !aborts);
    ++aborts;
    tx_live = 0;
    note('B');
}
static void *spa_get_dsl(spa_t *spa)
{
    CHECK(spa == &pool);
    return &pool;
}
static int txg_wait_synced_flags(void *dp, uint64_t target, int flags)
{
    CHECK(dp == &pool && target == 42 && flags == TXG_WAIT_SUSPEND &&
          commits == 1 && !tx_live && updates == 1 && !waits);
    ++waits;
    note('T');
    if (stage == 5)
        return EIO;
    if (stage != 6)
        synced = target;
    return 0;
}
static uint64_t spa_last_synced_txg(spa_t *spa)
{
    CHECK(spa == &pool && waits == 1 && !tx_live);
    ++last_checks;
    note('L');
    return synced;
}

#include "zpl-adapter.inc"

static void setup(void)
{
    nodes[1].type = DMU_OT_MASTER_NODE;
    nodes[2].type = DMU_OT_SA_MASTER_NODE;
    nodes[3] = (struct inode){
        DMU_OT_DIRECTORY_CONTENTS, DMU_OT_SA, S_IFDIR | 0755, 7, 3, 2, 3, 0};
    nodes[4] = (struct inode){
        DMU_OT_PLAIN_FILE_CONTENTS, DMU_OT_SA, S_IFREG | 0644, 8, 6, 1, 3, 0};
    pool.writable = 1;
    memcpy(disk, "abcdef", 6);
    for (size_t i = 0; i < sizeof(input); ++i)
        input[i] = (unsigned char)(i * 19 + 1);
    memcpy(expected, input, sizeof(input));
}

int main(int argc, char **argv)
{
    CHECK(argc == 2);
    int mode = atoi(argv[1]);
    setup();
    aether_zpl_view *view = (void *)(uintptr_t)1;
    int expected_error = 0;
    if (mode >= 100) {
        switch (mode) {
        case 100:
            pool.writable = 0;
            expected_error = EROFS;
            break;
        case 101:
            readonly_property = 1;
            expected_error = EROFS;
            break;
        case 102:
            property_error = 1;
            expected_error = EIO;
            break;
        case 103:
            snapshot = 1;
            expected_error = EROFS;
            break;
        case 104:
            expected_error = EROFS;
            break;
        case 105:
            expected_error = EINVAL;
            break;
        case 106:
            foreign = 1;
            expected_error = EXDEV;
            break;
        case 107:
            version = 4;
            expected_error = ENOTSUP;
            break;
        case 108:
            fault = -1;
            expected_error = ENOMEM;
            break;
        case 109:
        case 110:
        case 111:
        case 112:
            upgrade_mode = mode - 108;
            expected_error = ENOTSUP;
            break;
        default:
            CHECK(mode >= 120 && mode < 147);
            fault = mode - 119;
            expected_error = EIO;
        }
        int error = mode == 104
                        ? aether_zpl_open(&pool, "test/files", &view)
                        : aether_zpl_open_write(&pool, "test/files",
                                                mode == 105 ? NULL : &view);
        CHECK(error == expected_error);
        if (mode != 105)
            CHECK(view == NULL);
        CHECK(!owned && !allocated && !handles && !creates);
        CHECK(allocations == frees);
        if (mode < 134)
            CHECK(!writable_owns);
        return 0;
    }
    CHECK(aether_zpl_open_write(&pool, "test/files", &view) == 0 && view &&
          owned);
    CHECK(own_attempts == 2 && writable_owns == 1 && allocations == 2 &&
          frees == 1);
    step = 0;
    fault = 0;
    uint64_t object = 4, generation = 8, offset = 1, seconds = 1234,
             nanos = 5678;
    size_t length = 3;
    const void *buffer = input;
    switch (mode) {
    case 0:
        break;
    case 1:
        offset = 6;
        break;
    case 2:
        offset = 4;
        length = 4;
        break;
    case 3:
        length = 0;
        buffer = NULL;
        break;
    case 4:
        offset = 6;
        length = 4096;
        break;
    case 10:
        offset = 7;
        expected_error = EINVAL;
        break;
    case 11:
        offset = UINT64_MAX;
        expected_error = EFBIG;
        break;
    case 12:
        offset = INT64_MAX;
        length = 1;
        expected_error = EFBIG;
        break;
    case 13:
        length = 4097;
        expected_error = EINVAL;
        break;
    case 14:
        buffer = NULL;
        expected_error = EINVAL;
        break;
    case 15:
        seconds = UINT64_MAX;
        expected_error = EINVAL;
        break;
    case 16:
        nanos = UINT64_C(1000000000);
        expected_error = EINVAL;
        break;
    case 17:
        generation = 7;
        expected_error = ESTALE;
        break;
    case 18:
        object = 3;
        generation = 7;
        expected_error = EISDIR;
        break;
    case 19:
        nodes[4].mode |= S_ISUID;
        expected_error = ENOTSUP;
        break;
    case 20:
        nodes[4].mode |= S_ISGID;
        expected_error = ENOTSUP;
        break;
    case 21:
        nodes[4].flags = ZFS_IMMUTABLE;
        expected_error = EPERM;
        break;
    case 22:
        nodes[4].flags = ZFS_APPENDONLY;
        expected_error = EPERM;
        break;
    case 23:
        nodes[4].flags = ZFS_READONLY;
        expected_error = EPERM;
        break;
    case 24:
        nodes[4].flags = ZFS_XATTR;
        expected_error = ENOTSUP;
        break;
    case 25:
        nodes[4].links = 0;
        expected_error = ENOENT;
        break;
    case 26:
        nodes[4].gen = 0;
        expected_error = EIO;
        break;
    case 27:
        nodes[4].mode = S_IFLNK | 0777;
        expected_error = ENOTSUP;
        break;
    case 28:
        nodes[4].bonus = 0;
        expected_error = ENOTSUP;
        break;
    case 29:
        nodes[4].size = (uint64_t)INT64_MAX + 1;
        expected_error = EFBIG;
        break;
    case 30:
        metadata_size_error = 1;
        expected_error = EIO;
        break;
    case 31:
        pool.writable = 0;
        expected_error = EROFS;
        break;
    case 32:
        expected_error = EINVAL;
        break;
    case 33:
        expected_error = EINVAL;
        break;
    case 34:
        length = 0;
        nodes[4].flags = ZFS_IMMUTABLE;
        expected_error = EPERM;
        break;
    case 60:
        stage = 1;
        expected_error = ENOMEM;
        break;
    case 61:
        stage = 2;
        expected_error = ENOSPC;
        break;
    case 62:
        stage = 3;
        expected_error = EIO;
        break;
    case 63:
        stage = 4;
        expected_error = EIO;
        break;
    case 64:
        stage = 5;
        expected_error = EIO;
        break;
    case 65:
        stage = 6;
        expected_error = EIO;
        break;
    case 66:
        mutate_input = 1;
        break;
#ifdef AETHER_ZPL_ORDERED_WRITE
    case 68:
    case 69:
    case 70:
        stage = mode - 61;
        expected_error = stage == 7 ? EIO : stage == 8 ? EXDEV : EALREADY;
        break;
#endif
    default:
        CHECK(mode >= 50 && mode < 55);
        fault = mode - 49;
        expected_error = EIO;
    }
    aether_zpl_write_result result;
    memset(&result, 0xa5, sizeof(result));
    int error = aether_zpl_write(mode == 32 ? NULL : view, object, generation,
                                 offset, buffer, length, seconds, nanos,
                                 mode == 33 ? NULL : &result);
    CHECK(error == expected_error);
    CHECK(!handles && !tx_live);
    if (mode != 33) {
        CHECK(
            result.state ==
            (commits ? (error ? AETHER_ZPL_COMMITTED : AETHER_ZPL_SYNCED) : 0));
        CHECK(result.txg == (commits && stage != 3 ? 42 : 0));
        CHECK(result.bytes_staged == (writes ? length : 0));
    }
    if (writes)
        CHECK(!memcmp(disk + offset, expected, length));
    else
        CHECK(!memcmp(disk, "abcdef", 6));
    if (!error && length) {
        CHECK(nodes[4].size == (offset + length > 6 ? offset + length : 6));
        CHECK(modified[0] == seconds && modified[1] == nanos &&
              changed[0] == seconds && changed[1] == nanos);
        CHECK(nodes[4].flags == (ZFS_ARCHIVE | ZFS_AV_MODIFIED));
        CHECK(commits == 1 && !aborts && writes == 1 && updates == 1 &&
              waits == 1 && last_checks == 1);
#ifdef AETHER_ZPL_ORDERED_WRITE
        CHECK(order_length == 11 && !memcmp(order, "CDSAGJWUKTL", 11));
#else
        CHECK(order_length == 10 && !memcmp(order, "CDSAGWUKTL", 10));
#endif
    }
    if (!commits)
        CHECK(!writes && !updates && !waits && !last_checks);
    if (stage == 2)
        CHECK(aborts == 1 && !commits);
    if (stage == 3 || stage == 4)
        CHECK(commits == 1 && !aborts && !waits);
    if (stage == 5 || stage == 6)
        CHECK(commits == 1 && waits == 1 && error);
#ifdef AETHER_ZPL_ORDERED_WRITE
    CHECK(joins == (commits && stage != 3 ? 1 : 0));
    if (stage >= 7)
        CHECK(commits == 1 && !aborts && !writes && !updates && !waits &&
              !last_checks && order_length == 7 &&
              !memcmp(order, "CDSAGJK", 7));
#endif
    aether_zpl_close(&view);
    CHECK(!view && !owned && !allocated && !handles && !tx_live);
    CHECK(allocations == frees);
    return 0;
}
