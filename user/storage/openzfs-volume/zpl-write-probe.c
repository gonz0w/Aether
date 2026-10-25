/* SPDX-License-Identifier: BSD-2-Clause */
/* Private one-write experiment. No client identities or general filesystem API.
 * Caller retains its live writable SPA and serializes teardown/property
 * changes. Failed writes close the context and stop; never retry assigned work.
 */
#include <sys/dmu.h>
#include <sys/spa.h>
#include <sys/sha2.h>
#include <string.h>
#include <time.h>
#include "zpl-write.h"

#define ZPL_PROBE_BYTES UINT64_C(780248)
#define ZPL_PROBE_OFFSET 37
#define ZPL_PROBE_LENGTH 16

extern void aether_engine_utc_phase(unsigned char);

/* Error-only private diagnostic, after context closure. Six bytes fit the
 * existing output quota; neither errno nor stage establishes write progress. */
static int probe_error(unsigned char stage, int error)
{
    aether_engine_utc_phase('E');
    aether_engine_utc_phase(stage);
    for (unsigned i = 0; i < 4; ++i)
        aether_engine_utc_phase(((uint32_t)error >> (8 * i)) & 255);
    return error;
}

static unsigned char replacement(size_t index)
{
    return (unsigned char)(index * 17 + 91);
}

/* One streaming pass, two hashes: the original bytes and the independently
 * predicted replacement image. No full-file heap or post-write expected data.
 */
static int stream_hash(aether_zpl_view *view, unsigned char *actual,
                       unsigned char *predicted)
{
    SHA2_CTX first, second;
    SHA2Init(SHA256, &first);
    if (predicted)
        SHA2Init(SHA256, &second);
    unsigned char buffer[4096];
    for (uint64_t offset = 0; offset < ZPL_PROBE_BYTES;) {
        size_t count = 0;
        int error = aether_zpl_read(view, 2, 47, offset, buffer, sizeof(buffer),
                                    &count);
        size_t want = MIN(sizeof(buffer), ZPL_PROBE_BYTES - offset);
        if (error || count != want)
            return error ? error : EIO;
        SHA2Update(&first, buffer, count);
        if (predicted) {
            for (size_t i = 0; i < count; ++i)
                if (offset + i >= ZPL_PROBE_OFFSET &&
                    offset + i < ZPL_PROBE_OFFSET + ZPL_PROBE_LENGTH)
                    buffer[i] = replacement(offset + i - ZPL_PROBE_OFFSET);
            SHA2Update(&second, buffer, count);
        }
        offset += count;
    }
    SHA2Final(actual, &first);
    if (predicted)
        SHA2Final(predicted, &second);
    size_t count = 99;
    int error = aether_zpl_read(view, 2, 47, ZPL_PROBE_BYTES, buffer,
                                sizeof(buffer), &count);
    return error ? error : count ? EIO : 0;
}

int aether_pool_namespace_write(spa_t *spa, uint64_t *assigned)
{
    if (!assigned)
        return EINVAL;
    *assigned = 0;
    if (!spa || !spa_writeable(spa))
        return EROFS;
    aether_zpl_view *view = NULL;
    int error = aether_zpl_open_write(spa, "testpool_zstd/x86_64", &view);
    if (error)
        return probe_error(1, error);
    unsigned char stage = 2;
    aether_zpl_node root, file;
    error = aether_zpl_root(view, &root);
    if (!error &&
        (root.object != 34 || root.generation != 45 || root.mode != 040755))
        error = EIO;
    if (!error) {
        stage = 3;
        error = aether_zpl_lookup(view, 34, 45, (const unsigned char *)"zstd",
                                  4, &file);
    }
    if (!error && (file.object != 2 || file.generation != 47 ||
                   file.size != ZPL_PROBE_BYTES || file.mode != 0100755))
        error = EIO;
    unsigned char original[32], predicted[32], actual[32];
    static const unsigned char pristine[32] = {
        0xcc, 0x9b, 0xfd, 0xde, 0xdd, 0x66, 0x4b, 0x9a, 0x53, 0x34, 0x58,
        0x1a, 0xf7, 0x86, 0x51, 0x6d, 0x14, 0x9c, 0x3f, 0xbd, 0x2c, 0x7e,
        0x65, 0x73, 0x59, 0x85, 0xac, 0xf1, 0x7b, 0xce, 0x59, 0x35};
    if (!error) {
        stage = 4;
        error = stream_hash(view, original, predicted);
    }
    if (!error && !memcmp(original, predicted, sizeof(original)))
        error = EIO;
    if (!error && memcmp(original, pristine, sizeof(original)))
        error = EIO;
    struct timespec utc;
    if (!error) {
        stage = 5;
        if (clock_gettime(CLOCK_REALTIME, &utc))
            error = EIO;
    }
    if (!error &&
        (utc.tv_sec < 0 || utc.tv_nsec < 0 || utc.tv_nsec >= 1000000000))
        error = EINVAL;
    aether_zpl_write_result result = {0};
    if (!error) {
        stage = 6;
        unsigned char bytes[ZPL_PROBE_LENGTH];
        for (size_t i = 0; i < sizeof(bytes); ++i)
            bytes[i] = replacement(i);
        error =
            aether_zpl_write(view, 2, 47, ZPL_PROBE_OFFSET, bytes,
                             sizeof(bytes), utc.tv_sec, utc.tv_nsec, &result);
    }
    if (!error) {
        stage = 7;
        if (!result.txg || result.bytes_staged != ZPL_PROBE_LENGTH ||
            result.state != AETHER_ZPL_SYNCED)
            error = EIO;
    }
    if (!error) {
        stage = 8;
        error = aether_zpl_lookup(view, 34, 45, (const unsigned char *)"zstd",
                                  4, &file);
    }
    if (!error && (file.object != 2 || file.generation != 47 ||
                   file.size != ZPL_PROBE_BYTES || file.mode != 0100755))
        error = EIO;
    if (!error) {
        stage = 9;
        error = stream_hash(view, actual, NULL);
    }
    if (!error && memcmp(actual, predicted, sizeof(actual)))
        error = EIO;
    aether_zpl_close(&view);
    if (!error)
        *assigned = result.txg;
    return error ? probe_error(stage, error) : 0;
}
