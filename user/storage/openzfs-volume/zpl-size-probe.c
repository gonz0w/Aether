/* SPDX-License-Identifier: BSD-2-Clause */
/* Fixed original-file finite mutation sequence. Host admits qualified seeds. */
#if SZ_READER
#include "zpl-read.c"
#else
#include "zpl-extend.c"
#endif
#include <sys/sha2.h>
#include <sys/spa_impl.h>
#include <time.h>
#if defined(SZ_EIGHT)
#define SZ_WRITE_COUNT 8
#define SZ_WRITE_BASE 69635
#define SZ_LAST_PHASE 10
#include "zpl-eight-oracle.h"
#else
#define SZ_WRITE_COUNT 2
#define SZ_WRITE_BASE 65530
#define SZ_LAST_PHASE 4
#include "zpl-size-oracle.h"
#endif
#if defined(SZ_LIFETIMES) && !SZ_READER
#include "pool-lifetime.h"
#endif
extern void aether_engine_utc_phase(unsigned char);

static int size_error(unsigned char stage, int error)
{
    aether_engine_utc_phase('E');
    aether_engine_utc_phase(stage);
    for (unsigned i = 0; i < 4; ++i)
        aether_engine_utc_phase(((uint32_t)error >> (i * 8)) & 255);
    return error;
}

static int size_check(aether_zpl_view *view, unsigned phase)
{
    if (phase > SZ_LAST_PHASE)
        return EINVAL;
    aether_zpl_node root, file;
    int error = aether_zpl_root(view, &root);
    if (!error && (root.object != 34 || root.generation != 45 ||
                   root.mode != 040755 || root.size != 3))
        error = EIO;
    if (!error)
        error = aether_zpl_lookup(view, 34, 45, (const unsigned char *)"zstd",
                                  4, &file);
    if (!error && (file.object != 2 || file.generation != 47 ||
                   file.mode != 0100755 || file.size != size_lengths[phase]))
        error = EIO;
    SHA2_CTX hash;
    SHA2Init(SHA256, &hash);
    unsigned char buffer[4096], digest[32];
    uint64_t offset = 0;
    while (!error && offset < size_lengths[phase]) {
        size_t count = 0;
        error = aether_zpl_read(view, 2, 47, offset, buffer, sizeof(buffer),
                                &count);
        if (!error &&
            count != MIN(sizeof(buffer), size_lengths[phase] - offset))
            error = EIO;
        if (!error) {
            SHA2Update(&hash, buffer, count);
            offset += count;
        }
    }
    SHA2Final(digest, &hash);
    if (!error && memcmp(digest, size_hashes[phase], sizeof(digest)))
        error = EIO;
    uint64_t positions[2] = {size_lengths[phase], 780248};
    for (unsigned i = 0; !error && i < 2; ++i) {
        size_t count = 99;
        error = aether_zpl_read(view, 2, 47, positions[i], buffer,
                                sizeof(buffer), &count);
        if (!error && count)
            error = EIO;
    }
    sa_handle_t *handle = NULL;
    if (!error)
        error = sa_handle_get(view->os, 2, NULL, SA_HDL_PRIVATE, &handle);
    if (!error) {
        uint64_t size = 0, flags = 0, mtime[2] = {0}, ctime[2] = {0};
        sa_bulk_attr_t attrs[4];
        int n = 0;
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_SIZE], NULL, &size, 8);
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_FLAGS], NULL, &flags,
                         8);
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_MTIME], NULL, mtime,
                         16);
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_CTIME], NULL, ctime,
                         16);
        error = sa_bulk_lookup(handle, attrs, n);
        if (!error && (size != size_lengths[phase] ||
                       (flags & (ZFS_ARCHIVE | ZFS_AV_MODIFIED)) !=
                           (ZFS_ARCHIVE | ZFS_AV_MODIFIED)))
            error = EIO;
        if (!error && phase &&
            (memcmp(mtime, ctime, 16) || mtime[0] < 1791290040 ||
             mtime[0] > 1791290100 || mtime[1] >= 1000000000))
            error = EIO;
    }
    if (handle)
        sa_handle_destroy(handle);
    return error;
}

#if SZ_READER
int aether_pool_namespace_recover(spa_t *spa)
{
    if (!spa || spa_writeable(spa))
        return size_error(1, EROFS);
    aether_zpl_view *view = NULL;
    int error = aether_zpl_open(spa, "testpool_zstd/x86_64", &view);
    if (error)
        return size_error(2, error);
    error = size_check(view, SZ_KIND == 3 ? SZ_LAST_PHASE : SZ_KIND);
    aether_zpl_close(&view);
    return error ? size_error(9, error) : 0;
}
#else
static int size_utc(struct timespec *utc)
{
    if (clock_gettime(CLOCK_REALTIME, utc))
        return EIO;
    return utc->tv_sec < 0 || utc->tv_nsec < 0 || utc->tv_nsec >= 1000000000
               ? EINVAL
               : 0;
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
        return size_error(1, error);
    unsigned char stage = 4;
    error = size_check(view, SZ_KIND - 1);
    struct timespec utc = {0};
    unsigned loops = SZ_KIND == 3 ? SZ_WRITE_COUNT : 1;
    uint64_t previous = 0;
    for (unsigned part = 0; !error && part < loops; ++part) {
        stage = 5;
        error = size_utc(&utc);
        aether_zpl_write_result result = {0};
        if (!error) {
            stage = 6;
#if SZ_KIND == 1
            error = aether_zpl_shrink(view, 2, 47, 65539, utc.tv_sec,
                                      utc.tv_nsec, &result);
#elif SZ_KIND == 2
            error = aether_zpl_extend(view, 2, 47, 69635, utc.tv_sec,
                                      utc.tv_nsec, &result);
#else
            unsigned char bytes[4096];
            for (size_t i = 0; i < sizeof(bytes); ++i)
                bytes[i] = (i * 17 + 91 + part * 43) & 255;
            error = aether_zpl_write(view, 2, 47, SZ_WRITE_BASE + part * 4096,
                                     bytes, sizeof(bytes), utc.tv_sec,
                                     utc.tv_nsec, &result);
#endif
            /* Preserve earlier committed progress even if a later call fails
             * before assigning its own TXG. No error authorizes a replay. */
            if (result.txg)
                *assigned = result.txg;
        }
        if (!error) {
            stage = 7;
            if (result.txg <= previous || result.state != AETHER_ZPL_SYNCED ||
                result.bytes_staged != (SZ_KIND == 1 ? 0 : 4096))
                error = EIO;
            previous = result.txg;
        }
        if (!error) {
            stage = 9;
            error = size_check(view, SZ_KIND == 3 ? 3 + part : SZ_KIND);
        }
#if defined(SZ_LIFETIMES)
        /* Preserve original progress on every failure. Consume all view borrows
         * before asking the trusted observer to release a successful record. */
        aether_zpl_close(&view);
        int retired = aether_pool_lifetime_retire(
            error, result.txg, result.bytes_staged, result.state);
        if (!error && retired) {
            stage = 10;
            error = retired;
        }
        if (!error && part + 1 < loops) {
            stage = 8;
            error = aether_zpl_open_write(spa, "testpool_zstd/x86_64", &view);
        }
#endif
    }
#if defined(SZ_LIFETIMES)
    if (view)
#endif
        aether_zpl_close(&view);
    if (!error) {
        stage = 8;
        error = aether_zpl_open_write(spa, "testpool_zstd/x86_64", &view);
    }
    if (!error) {
        stage = 9;
        error = size_check(view, SZ_KIND == 3 ? SZ_LAST_PHASE : SZ_KIND);
    }
    if (view)
        aether_zpl_close(&view);
    return error ? size_error(stage, error) : 0;
}
#endif
