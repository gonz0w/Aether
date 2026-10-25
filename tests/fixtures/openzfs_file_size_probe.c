/* SPDX-License-Identifier: BSD-2-Clause */
/* API/hash model for actual guest control flow, not a filesystem decoder. */
#include "size-types.inc"
#include "zpl-extend.h"
#if defined(SZ_EIGHT)
#include "zpl-eight-oracle.h"
#define MODEL_COUNT 8
#define MODEL_LAST 10
#define MODEL_BASE 69635
#else
#include "zpl-size-oracle.h"
#define MODEL_COUNT 2
#define MODEL_LAST 4
#define MODEL_BASE 65530
#endif
static int attrs[ZPL_END], mode, fault, calls, owned, handles, opens, closes,
    phase, mutations, checks;
static uint64_t position;
#if !SZ_READER
static uint64_t last_assigned;
#endif
#if defined(SZ_LIFETIMES) && !SZ_READER
#include "pool-lifetime.h"
static aether_zpl_write_result original_result;
static int original_error, retire_calls, retired_successes;
#endif
static spa_t pool;
static aether_zpl_view view = {(void *)1, attrs};
static sa_handle_t handle;
static unsigned char observed[6], disk[780248];
static unsigned observed_count;
#if defined(SZ_EIGHT)
static const uint64_t lengths[11] = {780248, 65539, 69635, 73731, 77827, 81923,
                                     86019,  90115, 94211, 98307, 102403};
#else
static const uint64_t lengths[5] = {780248, 65539, 69635, 69635, 73722};
#endif
static int tick(void) { return ++calls == fault ? EIO : 0; }
static int spa_writeable(spa_t *s)
{
    CHECK(s == &pool);
    return mode == 14 ? SZ_READER : !SZ_READER;
}
void aether_engine_utc_phase(unsigned char b)
{
    CHECK(!owned && !handles && observed_count < 6);
    observed[observed_count++] = b;
}
int aether_zpl_open(spa_t *s, const char *name, aether_zpl_view **out)
{
    CHECK(s == &pool && !owned && !*out &&
          !strcmp(name, "testpool_zstd/x86_64"));
#if defined(SZ_LIFETIMES) && !SZ_READER
    CHECK(mutations == retired_successes);
#endif
    if (tick())
        return EIO;
    owned = 1;
    ++opens;
    *out = &view;
    return 0;
}
int aether_zpl_open_write(spa_t *s, const char *name, aether_zpl_view **out)
{
    return aether_zpl_open(s, name, out);
}
void aether_zpl_close(aether_zpl_view **out)
{
    CHECK(owned && !handles && *out == &view);
    owned = 0;
    *out = NULL;
    ++closes;
}
int aether_zpl_root(aether_zpl_view *v, aether_zpl_node *out)
{
    CHECK(owned && v == &view);
    if (tick())
        return EIO;
    *out = (aether_zpl_node){34, 45, 3, 040755};
    if (mode == 1)
        ++out->generation;
    position = 0;
    ++checks;
    return 0;
}
int aether_zpl_lookup(aether_zpl_view *v, uint64_t d, uint64_t dg,
                      const unsigned char *name, size_t n, aether_zpl_node *out)
{
    CHECK(owned && v == &view && d == 34 && dg == 45 && n == 4 &&
          !memcmp(name, "zstd", 4));
    if (tick())
        return EIO;
    *out = (aether_zpl_node){2, 47, lengths[phase], 0100755};
    if (mode == 2)
        ++out->size;
    if (mode == 7)
        ++out->generation;
    return 0;
}
int aether_zpl_read(aether_zpl_view *v, uint64_t obj, uint64_t gen,
                    uint64_t off, void *buf, size_t n, size_t *got)
{
    CHECK(owned && v == &view && obj == 2 && gen == 47 && n == 4096 && buf);
    *got = 0;
    if (tick())
        return EIO;
    if (off >= lengths[phase]) {
        if ((mode == 5 && off == lengths[phase]) ||
            (mode == 6 && off == 780248))
            *got = 1;
        return 0;
    }
    CHECK(off == position);
    *got = MIN(n, lengths[phase] - off);
    if (mode == 4)
        --*got;
    memcpy(buf, disk + off, *got);
    position += *got;
    return 0;
}
static unsigned char expected_byte(unsigned p, uint64_t off)
{
#if defined(SZ_EIGHT)
    if (p >= 3 && off >= 69635) {
        uint64_t part = (off - 69635) / 4096, local = (off - 69635) % 4096;
        return (local * 17 + 91 + part * 43) & 255;
    }
#else
    if (p >= 3 && off >= 65530) {
        if (off < 69626)
            return ((off - 65530) * 17 + 91) & 255;
        if (p == 4)
            return ((off - 69626) * 17 + 134) & 255;
        return 0;
    }
#endif
    return p >= 2 && off >= 65539 ? 0 : (off * 17 + 3) & 255;
}
static void SHA2Init(int alg, SHA2_CTX *hash)
{
    CHECK(alg == SHA256);
    hash->bytes = 0;
}
static int hash_valid;
static void SHA2Update(SHA2_CTX *hash, const void *buf, size_t n)
{
    if (!hash->bytes)
        hash_valid = 1;
    for (size_t i = 0; i < n; ++i)
        if (((const unsigned char *)buf)[i] !=
            expected_byte(phase, hash->bytes + i))
            hash_valid = 0;
    hash->bytes += n;
}
static void SHA2Final(unsigned char *out, SHA2_CTX *hash)
{
    memcpy(out, size_hashes[phase], 32);
    if (mode == 3 || !hash_valid || hash->bytes != lengths[phase])
        out[0] ^= 1;
}
static int sa_handle_get(void *os, uint64_t obj, void *tag, int flags,
                         sa_handle_t **out)
{
    CHECK(os == view.os && owned && !handles && obj == 2 && !tag &&
          flags == SA_HDL_PRIVATE);
    if (tick())
        return EIO;
    *out = &handle;
    handles = 1;
    return 0;
}
static void sa_handle_destroy(sa_handle_t *h)
{
    CHECK(h == &handle && handles == 1);
    handles = 0;
}
static int sa_bulk_lookup(sa_handle_t *h, sa_bulk_attr_t *a, int n)
{
    CHECK(h == &handle && handles && n == 4);
    if (tick())
        return EIO;
    for (int i = 0; i < n; ++i) {
        uint64_t value = a[i].attr == ZPL_SIZE ? lengths[phase] + (mode == 8)
                                               : ZFS_ARCHIVE | ZFS_AV_MODIFIED;
        if (a[i].attr == ZPL_FLAGS && mode == 9)
            value = 0;
        if (a[i].attr == ZPL_SIZE || a[i].attr == ZPL_FLAGS) {
            CHECK(a[i].length == 8);
            memcpy(a[i].data, &value, 8);
        } else {
            uint64_t t[2] = {1791290045, 123};
            CHECK(a[i].length == 16);
            if (phase && mode == 10)
                t[0] = 1791290039;
            if (phase && mode == 11)
                t[0] = 1791290101;
            if (phase && mode == 12)
                t[1] = 1000000000;
            if (phase && mode == 13 && a[i].attr == ZPL_CTIME)
                ++t[1];
            memcpy(a[i].data, t, 16);
        }
    }
    return 0;
}
#if !SZ_READER
static int fake_clock(clockid_t id, struct timespec *out)
{
    CHECK(id == CLOCK_REALTIME && owned);
#if defined(SZ_LIFETIMES)
    original_result = (aether_zpl_write_result){0};
    original_error = 0;
#endif
    if (tick() || mode == 23)
        return -1;
    *out = (struct timespec){mode == 22 ? -1 : 1791290045, 123};
    return 0;
}
#define clock_gettime fake_clock
static int mutate(aether_zpl_write_result *out)
{
    CHECK(owned && !handles && mutations < (SZ_KIND == 3 ? MODEL_COUNT : 1));
    if (tick() || (mode == 21 && mutations == 1) ||
        (mode == 26 && mutations == 7))
        return EIO;
    ++mutations;
    ++phase;
    *out = (aether_zpl_write_result){
        788 + 2 * (mutations - 1), SZ_KIND == 1 ? 0 : 4096, AETHER_ZPL_SYNCED};
    if (mode == 17)
        out->txg = 0;
    if (mode == 18)
        ++out->bytes_staged;
    if (mode == 19)
        out->state = AETHER_ZPL_COMMITTED;
    if (mode == 28 && mutations == 8)
        out->txg = 800;
    if (mode == 20 && mutations == 2)
        out->txg = 788;
    if (out->txg)
        last_assigned = out->txg;
    return mode == 16 || (mode == 29 && mutations == 8) ? EIO : 0;
}
int aether_zpl_shrink(aether_zpl_view *v, uint64_t obj, uint64_t gen,
                      uint64_t size, uint64_t sec, uint64_t ns,
                      aether_zpl_write_result *out)
{
    CHECK(v == &view && obj == 2 && gen == 47 && size == 65539 &&
          sec == 1791290045 && ns == 123 && !mutations);
    int e = mutate(out);
    if (mode == 25)
        disk[0] ^= 1;
    return e;
}
int aether_zpl_extend(aether_zpl_view *v, uint64_t obj, uint64_t gen,
                      uint64_t size, uint64_t sec, uint64_t ns,
                      aether_zpl_write_result *out)
{
    CHECK(v == &view && obj == 2 && gen == 47 && size == 69635 &&
          sec == 1791290045 && ns == 123 && !mutations);
    int e = mutate(out);
    if (!e && mode != 24)
        memset(disk + 65539, 0, 4096);
    return e;
}
int aether_zpl_write(aether_zpl_view *v, uint64_t obj, uint64_t gen,
                     uint64_t off, const void *buf, size_t n, uint64_t sec,
                     uint64_t ns, aether_zpl_write_result *out)
{
    CHECK(v == &view && obj == 2 && gen == 47 && n == 4096 &&
          off == MODEL_BASE + 4096 * (unsigned)mutations && sec == 1791290045 &&
          ns == 123);
    for (unsigned i = 0; i < n; ++i)
        CHECK(((const unsigned char *)buf)[i] ==
              ((i * 17 + 91 + mutations * 43) & 255));
    int e = mutate(out);
    if (mutations && !e)
        memcpy(disk + off, buf, n);
    if (mode == 27 && mutations == 8)
        disk[0] ^= 1;
    if (mode == 30 && mutations == 8)
        disk[69635 + 3 * 4096] ^= 1;
#if defined(SZ_LIFETIMES)
    original_result = *out;
    original_error = e;
#endif
    return e;
}
#if defined(SZ_LIFETIMES)
int aether_pool_lifetime_retire(int error, uint64_t target, uint64_t staged,
                                uint64_t state)
{
    CHECK(!owned && !handles && retire_calls < 8);
    CHECK(target == original_result.txg &&
          staged == original_result.bytes_staged &&
          state == original_result.state);
    if (original_error)
        CHECK(error == original_error);
    ++retire_calls;
    if (tick() || mode == 31 || (mode == 32 && retire_calls == 8))
        return EBUSY;
    if (error || !target || staged != 4096 || state != 2)
        return error ? error : EIO;
    ++retired_successes;
    CHECK(retired_successes == mutations);
    return 0;
}
#endif
#endif
#include "size-probe.inc"
int main(int argc, char **argv)
{
    CHECK(argc == 3);
    mode = atoi(argv[1]);
    fault = atoi(argv[2]);
    for (int i = 0; i < ZPL_END; ++i)
        attrs[i] = i;
    phase = SZ_READER ? (SZ_KIND == 3 ? MODEL_LAST : SZ_KIND) : SZ_KIND - 1;
    for (uint64_t i = 0; i < sizeof(disk); ++i)
        disk[i] = expected_byte(phase, i);
#if SZ_READER
    int error = aether_pool_namespace_recover(&pool);
#else
    uint64_t assigned = 99;
    int error = aether_pool_namespace_write(&pool, &assigned);
    CHECK(assigned == last_assigned);
#endif
    CHECK(!owned && !handles && opens == closes &&
          mutations <= (SZ_KIND == 3 ? MODEL_COUNT : 1));
    CHECK((error == 0) == (!mode && !fault));
    if (error && !(mode == 14 && !SZ_READER)) {
        CHECK(observed_count == 6 && observed[0] == 'E');
        uint32_t code = 0;
        for (unsigned i = 0; i < 4; ++i)
            code |= (uint32_t)observed[i + 2] << (i * 8);
        CHECK(code == (uint32_t)error);
    }
    if (!error)
        CHECK(checks == (SZ_READER ? 1 : SZ_KIND == 3 ? MODEL_COUNT + 2 : 3));
    printf("calls=%d\n", calls);
    return 0;
}
