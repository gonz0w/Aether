/* SPDX-License-Identifier: BSD-2-Clause */
/* Actual probe over faulting APIs and a stream-validation hash double; no real
 * SHA, ZPL decoder, native authority or persistence is established here. */
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "zpl-write.h"
#define MIN(a, b) ((a) < (b) ? (a) : (b))
#define SHA256 1
#define SHA256_DIGEST_LENGTH 32
#define CHECK(c)                                                               \
    do {                                                                       \
        if (!(c)) {                                                            \
            fprintf(stderr, "HOST ZPL PROBE oracle96 line%d\n", __LINE__);     \
            exit(96);                                                          \
        }                                                                      \
    } while (0)
typedef struct spa {
    int unused;
} spa_t;
struct aether_zpl_view {
    int unused;
};
typedef struct {
    size_t count;
    int valid, patch;
} SHA2_CTX;
static spa_t pool;
static aether_zpl_view view;
static int mode, calls, owned, closes, writes, reads, clock_calls;
static unsigned char diagnostic[6];
static unsigned diagnostic_count;
void aether_engine_utc_phase(unsigned char value)
{
    CHECK(!owned && diagnostic_count < sizeof(diagnostic));
    diagnostic[diagnostic_count++] = value;
}
static uint64_t cursor;
static const unsigned char pristine[32] = {
    0xcc, 0x9b, 0xfd, 0xde, 0xdd, 0x66, 0x4b, 0x9a, 0x53, 0x34, 0x58,
    0x1a, 0xf7, 0x86, 0x51, 0x6d, 0x14, 0x9c, 0x3f, 0xbd, 0x2c, 0x7e,
    0x65, 0x73, 0x59, 0x85, 0xac, 0xf1, 0x7b, 0xce, 0x59, 0x35};
static int tick(void) { return ++calls == mode - 100 ? EIO : 0; }
static int spa_writeable(spa_t *spa)
{
    CHECK(spa == &pool);
    return mode != 9;
}
int aether_zpl_open_write(spa_t *spa, const char *name, aether_zpl_view **out)
{
    CHECK(spa == &pool && !owned && !strcmp(name, "testpool_zstd/x86_64"));
    if (tick() || mode == 1)
        return EIO;
    *out = &view;
    owned = 1;
    return 0;
}
void aether_zpl_close(aether_zpl_view **out)
{
    CHECK(owned && *out == &view);
    *out = NULL;
    owned = 0;
    ++closes;
}
int aether_zpl_root(aether_zpl_view *context, aether_zpl_node *out)
{
    CHECK(owned && context == &view);
    if (tick())
        return EIO;
    *out = (aether_zpl_node){34, 45, 3, 040755};
    return 0;
}
int aether_zpl_lookup(aether_zpl_view *context, uint64_t object,
                      uint64_t generation, const unsigned char *name,
                      size_t length, aether_zpl_node *out)
{
    CHECK(owned && context == &view && object == 34 && generation == 45 &&
          length == 4 && !memcmp(name, "zstd", 4));
    if (tick())
        return EIO;
    *out = (aether_zpl_node){2, mode == 5 || (mode == 17 && writes) ? 48 : 47,
                             mode == 2 ? 780249 : 780248,
                             mode == 6 ? 0100644 : 0100755};
    return 0;
}
static unsigned char pattern(uint64_t offset, int patched)
{
    if (patched && offset >= 37 && offset < 53)
        return (unsigned char)((offset - 37) * 17 + 91);
    return (unsigned char)(offset * 17 + 3);
}
int aether_zpl_read(aether_zpl_view *context, uint64_t object,
                    uint64_t generation, uint64_t offset, void *buffer,
                    size_t length, size_t *count)
{
    CHECK(owned && context == &view && object == 2 && generation == 47 &&
          length <= 4096);
    *count = 0;
    if (tick())
        return EIO;
    if (offset == 780248) {
        CHECK(cursor == 780248);
        cursor = 0;
        if (mode == 7)
            *count = 1;
        return 0;
    }
    CHECK(offset == cursor && buffer);
    *count = MIN(length, 780248 - offset);
    if (mode == 4)
        --*count;
    for (size_t i = 0; i < *count; ++i)
        ((unsigned char *)buffer)[i] = pattern(offset + i, writes);
    if (mode == 18 && writes && !offset)
        ((unsigned char *)buffer)[3] ^= 1;
    cursor += *count;
    ++reads;
    return 0;
}
static int probe_clock_gettime(clockid_t clock, struct timespec *out)
{
    CHECK(clock == CLOCK_REALTIME && owned && !writes);
    ++clock_calls;
    if (tick() || mode == 10)
        return -1;
    *out = (struct timespec){mode == 11 ? -1 : 1234,
                             mode == 12 ? 1000000000 : 5678};
    return 0;
}
int aether_zpl_write(aether_zpl_view *context, uint64_t object,
                     uint64_t generation, uint64_t offset, const void *buffer,
                     size_t length, uint64_t seconds, uint64_t nanos,
                     aether_zpl_write_result *out)
{
    CHECK(owned && context == &view && object == 2 && generation == 47 &&
          offset == 37 && length == 16 && !writes && cursor == 0 &&
          seconds == 1234 && nanos == 5678 && clock_calls == 1);
    for (size_t i = 0; i < length; ++i)
        CHECK(((const unsigned char *)buffer)[i] == pattern(37 + i, 1));
    if (tick()) {
        *out = (aether_zpl_write_result){42, 16, AETHER_ZPL_COMMITTED};
        ++writes;
        return EIO;
    }
    ++writes;
    *out = (aether_zpl_write_result){
        mode == 15 ? 0 : 42, mode == 14 ? 0 : 16,
        mode == 13 || mode == 16 ? AETHER_ZPL_COMMITTED : AETHER_ZPL_SYNCED};
    return mode == 13 ? EIO : 0;
}
static void SHA2Init(int algorithm, SHA2_CTX *hash)
{
    CHECK(algorithm == SHA256);
    *hash = (SHA2_CTX){0, 1, -1};
}
static void SHA2Update(SHA2_CTX *hash, const void *data, size_t count)
{
    CHECK(count && count <= 4096);
    const unsigned char *bytes = data;
    if (!hash->count)
        hash->patch = bytes[37] == pattern(37, 1);
    for (size_t i = 0; i < count; ++i)
        if (bytes[i] != pattern(hash->count + i, hash->patch))
            hash->valid = 0;
    hash->count += count;
}
static void SHA2Final(unsigned char *out, SHA2_CTX *hash)
{
    memset(out, 0, 32);
    if (hash->valid && hash->count == 780248) {
        memcpy(out, pristine, 32);
        if (hash->patch)
            out[0] ^= 1;
    }
    if (mode == 3)
        out[31] ^= 1;
}
#define clock_gettime probe_clock_gettime
#include "write-probe.inc"
int main(int argc, char **argv)
{
    CHECK(argc == 2);
    mode = atoi(argv[1]);
    uint64_t assigned = 99;
    int error = aether_pool_namespace_write(&pool, &assigned);
    CHECK((error == 0) == (mode == 0));
    CHECK(!owned &&
          closes == ((mode == 1 || mode == 9 || mode == 101) ? 0 : 1));
    CHECK(assigned == (error ? 0 : 42));
    if (error && mode != 9) {
        unsigned stage = mode == 1                             ? 1
                         : mode == 2 || mode == 5 || mode == 6 ? 3
                         : mode == 3 || mode == 4 || mode == 7 ? 4
                         : mode >= 10 && mode <= 12            ? 5
                         : mode == 13                          ? 6
                         : mode >= 14 && mode <= 16            ? 7
                         : mode == 17                          ? 8
                         : mode == 18                          ? 9
                                                               : 0;
        if (mode >= 101) {
            unsigned call = mode - 100;
            stage = call <= 3     ? call
                    : call <= 195 ? 4
                    : call == 196 ? 5
                    : call == 197 ? 6
                    : call == 198 ? 8
                                  : 9;
        }
        CHECK(diagnostic_count == 6 && diagnostic[0] == 'E' &&
              diagnostic[1] == stage);
        uint32_t observed = 0;
        for (unsigned i = 0; i < 4; ++i)
            observed |= (uint32_t)diagnostic[i + 2] << (8 * i);
        CHECK(observed == (uint32_t)error);
    } else
        CHECK(!diagnostic_count);
    if (!mode) {
        CHECK(writes == 1 && reads == 382 && clock_calls == 1 && calls == 390);
    }
    if (mode == 13 || mode == 14 || mode == 15 || mode == 16 || mode == 297)
        CHECK(reads == 191 && writes == 1);
    return 0;
}
