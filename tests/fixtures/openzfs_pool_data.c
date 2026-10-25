/* SPDX-License-Identifier: BSD-2-Clause */
/* Synthetic DMU/ownership calls around the actual private data helper. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#define B_FALSE 0
#define B_TRUE 1
#define FTAG ((void *)7)
#define DMU_OST_OTHER 4
#define DMU_OT_PLAIN_OTHER 5
#define DMU_OT_NONE 0
#define DMU_TX_WAIT 1
#define DMU_READ_NO_PREFETCH 1
#define TXG_WAIT_SUSPEND 2
#define ASSERT(x) require(x)
#define ASSERT3U(a, op, b) require((a)op(b))
typedef int cred_t;
typedef struct spa {
    int writable;
    const char *name;
} spa_t;
typedef struct dsl_pool {
    spa_t *spa;
} dsl_pool_t;
typedef struct objset {
    spa_t *spa;
} objset_t;
typedef struct dmu_tx {
    uint64_t tx_txg;
    int live;
    objset_t *os;
} dmu_tx_t;
typedef struct {
    unsigned doi_type, doi_data_block_size, doi_bonus_type;
    uint64_t doi_bonus_size;
} dmu_object_info_t;
static spa_t spa = {1, "aether_pool_probe"}, foreign = {1, "foreign"};
static dsl_pool_t dp = {&spa};
static objset_t os = {&spa};
static dmu_tx_t tx, constructor;
static int mode, owned, readonly, commits, aborts, writes, waits, reads, binds;
static char events[128];
static unsigned count;
static unsigned char media[64];
static void require(int condition)
{
    if (!condition) {
        fputs("HOST DATA oracle92\n", stderr);
        exit(92);
    }
}
static void event(char c)
{
    require(count < 127);
    events[count++] = c;
}
#include "original-getter.inc"
static int spa_writeable(spa_t *p) { return p->writable; }
static const char *spa_name(spa_t *p) { return p->name; }
static dsl_pool_t *spa_get_dsl(spa_t *p)
{
    require(p == &spa);
    return &dp;
}
static uint64_t spa_last_synced_txg(spa_t *p)
{
    require(p == &spa);
    return 19;
}
static int dmu_object_claim(objset_t *o, uint64_t object, int type, int block,
                            int bonus, int length, dmu_tx_t *t)
{
    require(o == &os && t == &constructor && object == 1 && type == 5 &&
            block == 4096 && bonus == 0 && length == 0);
    event('Q');
    return mode == 2 ? ENOSPC : 0;
}
static int
dmu_objset_create(const char *name, int type, uint64_t flags, void *crypto,
                  void (*callback)(objset_t *, void *, cred_t *, dmu_tx_t *),
                  void *arg)
{
    require(!strcmp(name, "aether_pool_probe/data_probe") && type == 4 &&
            !flags && !crypto);
    event('C');
    if (mode == 1)
        return EEXIST;
    constructor.tx_txg = 12;
    callback(&os, arg, NULL, &constructor);
    return 0;
}
static int dmu_objset_own(const char *name, int type, int ro, int decrypt,
                          void *tag, objset_t **out)
{
    require(!owned && !strcmp(name, "aether_pool_probe/data_probe") &&
            type == 4 && !decrypt && tag == FTAG);
    require(ro == readonly);
    event('O');
    if (mode == 3 || mode == 20)
        return ENOENT;
    owned = 1;
    *out = &os;
    return 0;
}
static spa_t *dmu_objset_spa(objset_t *o)
{
    require(owned && o == &os);
    return os.spa;
}
static void dmu_objset_disown(objset_t *o, int decrypt, void *tag)
{
    require(owned && o == &os && !decrypt && tag == FTAG && !tx.live);
    owned = 0;
    event('D');
}
static dmu_tx_t *dmu_tx_create(objset_t *o)
{
    require(owned && !readonly && o == &os && !tx.live);
    tx.live = 1;
    tx.os = o;
    event('T');
    return &tx;
}
static void dmu_tx_hold_write(dmu_tx_t *t, uint64_t object, uint64_t offset,
                              int length)
{
    require(t == &tx && tx.live && !tx.tx_txg && object == 1 && !offset &&
            length == 64);
    event('H');
}
static int dmu_tx_assign(dmu_tx_t *t, int flags)
{
    require(t == &tx && tx.live && flags == DMU_TX_WAIT);
    event('A');
    if (mode == 5)
        return ENOSPC;
    tx.tx_txg = 17;
    return 0;
}
static void dmu_tx_abort(dmu_tx_t *t)
{
    require(t == &tx && tx.live && !tx.tx_txg);
    tx.live = 0;
    ++aborts;
    event('X');
}
static int aether_pool_hooks_bind_transaction(dmu_tx_t *t)
{
    require(t == &tx && tx.live && tx.tx_txg == 17 && owned);
    ++binds;
    event('B');
    return mode == 6 ? EXDEV : 0;
}
static void dmu_write(objset_t *o, uint64_t object, uint64_t offset,
                      uint64_t length, const void *data, dmu_tx_t *t, int flags)
{
    require(o == &os && owned && !readonly && object == 1 && !offset &&
            length == 64 && t == &tx && tx.live && tx.tx_txg == 17 &&
            binds == 1 && flags == 1);
    memcpy(media, data, 64);
    ++writes;
    event('W');
}
static void dmu_tx_commit(dmu_tx_t *t)
{
    require(t == &tx && tx.live && tx.tx_txg == 17);
    ++commits;
    event('K');
    /* Simulate destruction: no later getter can capture this borrow. */
    tx.live = 0;
    tx.tx_txg = 0;
    tx.os = NULL;
}
static int txg_wait_synced_flags(dsl_pool_t *pool, uint64_t target, int flags)
{
    require(pool == &dp && target == 17 && flags == TXG_WAIT_SUSPEND && owned &&
            !tx.live && commits == 1);
    ++waits;
    event('S');
    return mode == 7 ? ESHUTDOWN : 0;
}
static int dmu_read(objset_t *o, uint64_t object, uint64_t offset,
                    uint64_t length, void *out, int flags)
{
    require(o == &os && owned && object == 1 && !offset && length == 64 &&
            flags == 1);
    if (!readonly)
        require(waits == 1 && !tx.live);
    ++reads;
    event('R');
    if (mode == 8 || mode == 25)
        return EIO;
    memcpy(out, media, 64);
    if (mode == 9)
        ((unsigned char *)out)[63] ^= 1;
    return 0;
}
static int dmu_object_info(objset_t *o, uint64_t object,
                           dmu_object_info_t *info)
{
    require(o == &os && owned && readonly && object == 1);
    event('I');
    if (mode == 24)
        return ENOENT;
    *info = (dmu_object_info_t){5, 4096, 0, 0};
    if (mode == 21)
        info->doi_type = 9;
    if (mode == 22)
        info->doi_data_block_size = 8192;
    if (mode == 23)
        info->doi_bonus_type = 5;
    if (mode == 26)
        info->doi_bonus_size = 1;
    return 0;
}
#include "data-helper.inc"
int main(int argc, char **argv)
{
    (void)dmu_objset_spa;
    (void)
        spa_last_synced_txg; /* Mutation-only omitted calls remain declared. */
    require(argc == 2);
    mode = atoi(argv[1]);
    uint64_t result = 0xdead;
    if (mode == 4 || mode == 27)
        os.spa = &foreign;
    if (mode >= 20) {
        readonly = 1;
        spa.writable = 0;
        aether_data_record(media, 17);
        if (mode == 28)
            aether_data_record(media, 0);
        if (mode == 29)
            aether_data_record(media, 20);
        if (mode >= 100 && mode < 164)
            media[mode - 100] ^= 1;
        if (mode == 30)
            spa.writable = 1;
        if (mode == 31)
            spa.name = "foreign";
        int error = aether_pool_data_read(&spa, &result);
        int expected = mode == 20 || mode == 24 ? ENOENT
                       : mode == 21 || mode == 22 || mode == 23 || mode == 26 ||
                               mode == 30 || mode == 31
                           ? EINVAL
                       : mode == 27 ? EXDEV
                       : mode == 25 || mode == 28 || mode == 29 ||
                               (mode >= 100 && mode < 164)
                           ? EIO
                           : 0;
        require(error == expected && !owned && !tx.live && !commits &&
                !aborts && !writes);
        require(result == (expected ? 0xdead : 17));
        if (mode == 30 || mode == 31)
            require(!count);
        else if (mode != 20)
            require(events[count - 1] == 'D');
    } else {
        if (mode == 10)
            spa.writable = 0;
        if (mode == 11)
            spa.name = "foreign";
        int error = aether_pool_data_write(&spa, &result);
        int expected = mode == 1                  ? EEXIST
                       : mode == 2 || mode == 5   ? ENOSPC
                       : mode == 3                ? ENOENT
                       : mode == 4 || mode == 6   ? EXDEV
                       : mode == 7                ? ESHUTDOWN
                       : mode == 8 || mode == 9   ? EIO
                       : mode == 10 || mode == 11 ? EINVAL
                                                  : 0;
        require(error == expected && !owned && !tx.live);
        require(result == (expected ? 0xdead : 17));
        require(aborts == (mode == 5) &&
                commits == (mode == 0 || (mode >= 6 && mode <= 9)));
        require(writes == (mode == 0 || (mode >= 7 && mode <= 9)));
        if (!mode)
            require(!strcmp(events, "CQOTHABWKSRD"));
        if (mode == 10 || mode == 11)
            require(!count);
    }
    return 0;
}
