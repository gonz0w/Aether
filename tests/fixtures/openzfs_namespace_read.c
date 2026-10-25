/* SPDX-License-Identifier: BSD-2-Clause */
/* Actual native helper, synthetic reader and hash-provider calls. These doubles
 * check stream order/ownership/error handling, NOT SHA256 or ZPL decoding. */
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "zpl-read.h"
#define MIN(a, b) ((a) < (b) ? (a) : (b))
#define SHA256 1
#define SHA256_DIGEST_LENGTH 32
typedef struct spa {
    int unused;
} spa_t;
struct aether_zpl_view {
    int unused;
};
typedef struct {
    size_t count;
    int valid;
} SHA2_CTX;
static spa_t pool;
static aether_zpl_view context;
static int mode, calls, owned, closes, data_reads;
static size_t bytes_read;
#define CHECK(c)                                                               \
    do {                                                                       \
        if (!(c)) {                                                            \
            fprintf(stderr, "HOST NAMESPACE HELPER oracle94 line%d\n",         \
                    __LINE__);                                                 \
            exit(94);                                                          \
        }                                                                      \
    } while (0)
static int tick(void) { return ++calls == mode - 100 ? EIO : 0; }
int aether_zpl_open(spa_t *spa, const char *name, aether_zpl_view **out)
{
    CHECK(spa == &pool && !strcmp(name, "testpool_zstd/x86_64") && !owned);
    int error = tick();
    if (error || mode == 1)
        return EIO;
    *out = &context;
    owned = 1;
    return 0;
}
void aether_zpl_close(aether_zpl_view **out)
{
    CHECK(owned && *out == &context);
    *out = NULL;
    owned = 0;
    ++closes;
}
int aether_zpl_root(aether_zpl_view *view, aether_zpl_node *node)
{
    CHECK(view == &context && owned);
    int error = tick();
    if (error)
        return error;
    *node = (aether_zpl_node){34, 45, 3, 040755};
    return 0;
}
int aether_zpl_lookup(aether_zpl_view *view, uint64_t object,
                      uint64_t generation, const unsigned char *name,
                      size_t length, aether_zpl_node *node)
{
    CHECK(view == &context && owned && object == 34);
    int error = tick();
    if (error)
        return error;
    if (generation != 45)
        return mode == 5 ? 0 : ESTALE;
    if (length == 2 && !memcmp(name, "..", 2))
        return EINVAL;
    if (length == 6 && !memcmp(name, "absent", 6))
        return mode == 6 ? 0 : ENOENT;
    CHECK(length == 4 && !memcmp(name, "zstd", 4));
    *node = (aether_zpl_node){2, 47, mode == 2 ? 780249 : 780248, 0100755};
    return 0;
}
int aether_zpl_read(aether_zpl_view *view, uint64_t object, uint64_t generation,
                    uint64_t offset, void *buffer, size_t length, size_t *count)
{
    CHECK(view == &context && owned && length <= 4096);
    *count = 0;
    int error = tick();
    if (error)
        return error;
    if (object == 34)
        return mode == 8 ? 0 : EISDIR;
    CHECK(object == 2);
    if (generation != 47)
        return ESTALE;
    if (!length)
        return 0;
    if (offset >= 780248) {
        if (mode == 7)
            *count = 1;
        return 0;
    }
    CHECK(buffer && offset == bytes_read);
    *count = MIN(length, 780248 - offset);
    if (mode == 4)
        --*count;
    for (size_t i = 0; i < *count; ++i)
        ((unsigned char *)buffer)[i] = (unsigned char)((offset + i) * 17 + 3);
    bytes_read += *count;
    ++data_reads;
    return 0;
}
void SHA2Init(int algorithm, SHA2_CTX *hash)
{
    CHECK(algorithm == SHA256);
    hash->count = 0;
    hash->valid = 1;
}
void SHA2Update(SHA2_CTX *hash, const void *buffer, size_t count)
{
    CHECK(count <= 4096);
    for (size_t i = 0; i < count; ++i)
        if (((const unsigned char *)buffer)[i] !=
            (unsigned char)((hash->count + i) * 17 + 3))
            hash->valid = 0;
    hash->count += count;
}
void SHA2Final(void *out, SHA2_CTX *hash)
{
    static const unsigned char golden[32] = {
        0xcc, 0x9b, 0xfd, 0xde, 0xdd, 0x66, 0x4b, 0x9a, 0x53, 0x34, 0x58,
        0x1a, 0xf7, 0x86, 0x51, 0x6d, 0x14, 0x9c, 0x3f, 0xbd, 0x2c, 0x7e,
        0x65, 0x73, 0x59, 0x85, 0xac, 0xf1, 0x7b, 0xce, 0x59, 0x35};
    memset(out, 0, 32);
    if (hash->valid && hash->count == 780248)
        memcpy(out, golden, 32);
    if (mode == 3)
        ((unsigned char *)out)[31] ^= 1;
}
#include "namespace-helper.inc"
int main(int argc, char **argv)
{
    CHECK(argc == 2);
    mode = atoi(argv[1]);
    int error = aether_pool_namespace_read(&pool);
    CHECK((error == 0) == (mode == 0));
    CHECK(!owned && closes == ((mode == 1 || mode == 101) ? 0 : 1));
    if (!mode)
        CHECK(calls == 201 && data_reads == 191 && bytes_read == 780248);
    return 0;
}
