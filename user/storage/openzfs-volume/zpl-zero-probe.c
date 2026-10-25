/* SPDX-License-Identifier: BSD-2-Clause */
/* Private one-transaction truncate-to-zero experiment. Original DMU/SA owns
 * mutation; the owner keeps an exclusive live SPA until export/retirement. */
#include "zpl-resize.c"
#include <sys/sha2.h>
#include <time.h>

extern void aether_engine_utc_phase(unsigned char);

static int zero_error(unsigned char stage, int error)
{
    aether_engine_utc_phase('E');
    aether_engine_utc_phase(stage);
    for (unsigned i = 0; i < 4; ++i)
        aether_engine_utc_phase(((uint32_t)error >> (8 * i)) & 255);
    return error;
}

static int zero_identity(aether_zpl_view *view, uint64_t size)
{
    aether_zpl_node root, file;
    int error = aether_zpl_root(view, &root);
    if (!error &&
        (root.object != 34 || root.generation != 45 || root.mode != 040755))
        error = EIO;
    if (!error)
        error = aether_zpl_lookup(view, 34, 45, (const unsigned char *)"zstd",
                                  4, &file);
    if (!error && (file.object != 2 || file.generation != 47 ||
                   file.size != size || file.mode != 0100755))
        error = EIO;
    return error;
}

static int zero_baseline(aether_zpl_view *view)
{
    static const unsigned char pristine[32] = {
        0xcc, 0x9b, 0xfd, 0xde, 0xdd, 0x66, 0x4b, 0x9a, 0x53, 0x34, 0x58,
        0x1a, 0xf7, 0x86, 0x51, 0x6d, 0x14, 0x9c, 0x3f, 0xbd, 0x2c, 0x7e,
        0x65, 0x73, 0x59, 0x85, 0xac, 0xf1, 0x7b, 0xce, 0x59, 0x35};
    SHA2_CTX hash;
    SHA2Init(SHA256, &hash);
    unsigned char buffer[4096], digest[32];
    for (uint64_t offset = 0; offset < 780248;) {
        size_t count = 0;
        int error = aether_zpl_read(view, 2, 47, offset, buffer, sizeof(buffer),
                                    &count);
        if (error || count != MIN(sizeof(buffer), 780248 - offset))
            return error ? error : EIO;
        SHA2Update(&hash, buffer, count);
        offset += count;
    }
    SHA2Final(digest, &hash);
    if (memcmp(digest, pristine, sizeof(digest)))
        return EIO;
    size_t count = 99;
    int error =
        aether_zpl_read(view, 2, 47, 780248, buffer, sizeof(buffer), &count);
    return error ? error : count ? EIO : 0;
}

static int zero_readback(aether_zpl_view *view, const struct timespec *utc)
{
    sa_handle_t *handle = NULL;
    int error = sa_handle_get(view->os, 2, NULL, SA_HDL_PRIVATE, &handle);
    if (error)
        return error;
    uint64_t size = 99, flags = 0, mtime[2] = {0}, ctime[2] = {0};
    sa_bulk_attr_t attrs[4];
    int n = 0;
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_SIZE], NULL, &size,
                     sizeof(size));
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_FLAGS], NULL, &flags,
                     sizeof(flags));
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_MTIME], NULL, mtime,
                     sizeof(mtime));
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_CTIME], NULL, ctime,
                     sizeof(ctime));
    error = sa_bulk_lookup(handle, attrs, n);
    sa_handle_destroy(handle);
    if (error)
        return error;
    if (size ||
        (flags & (ZFS_ARCHIVE | ZFS_AV_MODIFIED)) !=
            (ZFS_ARCHIVE | ZFS_AV_MODIFIED) ||
        memcmp(mtime, ctime, sizeof(mtime)) ||
        mtime[0] != (uint64_t)utc->tv_sec || mtime[1] != (uint64_t)utc->tv_nsec)
        return EIO;
    unsigned char byte = 0;
    for (unsigned i = 0; i < 2; ++i) {
        size_t count = 99;
        error = aether_zpl_read(view, 2, 47, i ? 780248 : 0, &byte, 1, &count);
        if (error || count)
            return error ? error : EIO;
    }
    return 0;
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
        return zero_error(1, error);
    unsigned char stage = 2;
    error = zero_identity(view, 780248);
    if (!error) {
        stage = 4;
        error = zero_baseline(view);
    }
    struct timespec utc = {0};
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
        error =
            aether_zpl_shrink(view, 2, 47, 0, utc.tv_sec, utc.tv_nsec, &result);
        *assigned = result.txg;
    }
    if (!error) {
        stage = 7;
        if (!result.txg || result.bytes_staged ||
            result.state != AETHER_ZPL_SYNCED)
            error = EIO;
    }
    aether_zpl_close(&view);
    if (!error) {
        stage = 8;
        error = aether_zpl_open_write(spa, "testpool_zstd/x86_64", &view);
    }
    if (!error)
        error = zero_identity(view, 0);
    if (!error) {
        stage = 9;
        error = zero_readback(view, &utc);
    }
    if (view)
        aether_zpl_close(&view);
    return error ? zero_error(stage, error) : 0;
}
