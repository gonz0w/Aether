/* SPDX-License-Identifier: BSD-2-Clause */
/* Real C header ABI with synthetic ZPL/SHA providers; not disk decoding. */
#include <errno.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "zpl-read.h"
#include "owner-probe.h"
struct spa {
    int live;
};
typedef struct spa spa_t;
struct aether_zpl_view {
    int live;
};
static struct spa spa = {1};
static struct aether_zpl_view views[4];
static int mode, fail_at, steps, opens, closes, bad_close, live;
static int reads, lookups, updates;
static int fault(void) { return ++steps == fail_at; }
void test_reset(int selected, int failure)
{
    mode = selected;
    fail_at = failure;
    steps = opens = closes = bad_close = live = reads = lookups = updates = 0;
    memset(views, 0, sizeof(views));
}
void *test_spa(void) { return &spa; }
int test_counter(int field)
{
    int values[] = {steps, opens, closes,  bad_close,
                    live,  reads, lookups, updates};
    return field >= 0 && field < 8 ? values[field] : -1;
}
static int valid(aether_zpl_view *view)
{
    for (unsigned i = 0; i < 4; ++i)
        if (view == &views[i])
            return view->live;
    return 0;
}
int aether_zpl_open(struct spa *source, const char *name, aether_zpl_view **out)
{
    *out = NULL;
    if (fault() || mode == 1)
        return EIO;
    if (source != &spa || strcmp(name, "testpool_zstd/x86_64"))
        return EINVAL;
    if (mode == 2)
        return 0;
    for (unsigned i = 0; i < 4; ++i) {
        if (!views[i].live) {
            views[i].live = 1;
            ++live;
            ++opens;
            *out = &views[i];
            return mode == 3 ? EIO : mode == 4 ? -1 : 0;
        }
    }
    return ENOMEM;
}
void aether_zpl_close(aether_zpl_view **owned)
{
    if (!owned || !valid(*owned)) {
        ++bad_close;
        return;
    }
    (*owned)->live = 0;
    --live;
    ++closes;
    *owned = NULL;
}
int aether_zpl_root(aether_zpl_view *view, aether_zpl_node *out)
{
    if (fault() || mode == 5)
        return EIO;
    if (!valid(view))
        return EINVAL;
    *out = (aether_zpl_node){mode == 14 ? 0 : 34, mode == 7 ? 0 : 45, 1,
                             mode == 6 ? 0120777 : 040755};
    return 0;
}
int aether_zpl_lookup(aether_zpl_view *view, uint64_t object,
                      uint64_t generation, const unsigned char *name,
                      size_t length, aether_zpl_node *out)
{
    ++lookups;
    if (fault())
        return EIO;
    if (mode == 8)
        return -1;
    if (!valid(view) || object != 34 || generation != 45)
        return ESTALE;
    if (length != 4 || memcmp(name, "zstd", 4))
        return ENOENT;
    *out = (aether_zpl_node){2, mode == 12 ? 0 : 47, 780248,
                             mode == 13 ? 0120777 : 0100755};
    return 0;
}
static unsigned char pattern(uint64_t offset)
{
    return (offset * 17 + 31) % 251;
}
int aether_zpl_read(aether_zpl_view *view, uint64_t object, uint64_t generation,
                    uint64_t offset, void *buffer, size_t length, size_t *count)
{
    ++reads;
    *count = 0;
    if (!valid(view) || object != 2 || generation != 47)
        return ESTALE;
    memset(buffer, 0xa5, length);
    if (fault() || mode == 9)
        return EIO;
    if (mode == 15)
        return -1;
    size_t n = offset < 780248 ? 780248 - offset : 0;
    if (n > length)
        n = length;
    for (size_t i = 0; i < n; ++i)
        ((unsigned char *)buffer)[i] = pattern(offset + i);
    *count = mode == 10 ? length + 1 : mode == 11 && n ? n - 1 : n;
    return 0;
}
typedef struct {
    uint64_t bytes;
    int valid;
} SHA2_CTX;
#define SHA256 256
#define SHA256_DIGEST_LENGTH 32
static const unsigned char reference[32] = {
    0xcc, 0x9b, 0xfd, 0xde, 0xdd, 0x66, 0x4b, 0x9a, 0x53, 0x34, 0x58,
    0x1a, 0xf7, 0x86, 0x51, 0x6d, 0x14, 0x9c, 0x3f, 0xbd, 0x2c, 0x7e,
    0x65, 0x73, 0x59, 0x85, 0xac, 0xf1, 0x7b, 0xce, 0x59, 0x35};
static void SHA2Init(int algorithm, SHA2_CTX *hash)
{
    hash->bytes = 0;
    hash->valid = algorithm == SHA256;
}
static void SHA2Update(SHA2_CTX *hash, const void *source, size_t length)
{
    ++updates;
    if (mode == 16)
        return;
    const unsigned char *bytes = source;
    for (size_t i = 0; i < length; ++i)
        if (bytes[i] != pattern(hash->bytes + i))
            hash->valid = 0;
    hash->bytes += length;
}
static void SHA2Final(unsigned char *digest, SHA2_CTX *hash)
{
    memset(digest, 0, 32);
    if (hash->valid && hash->bytes == 780248)
        memcpy(digest, reference, 32);
}
#include "owner-probe-bodies.inc"
int test_composed_probe(void) { return aether_pool_namespace_read(&spa); }
