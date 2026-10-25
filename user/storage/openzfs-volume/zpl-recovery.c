/* SPDX-License-Identifier: BSD-2-Clause */
/* Private fixed-file recovery probe. Including the original reader keeps its
 * context layout private; no new public FFI or mutable alias is introduced. */
#include "zpl-read.c"
#include <sys/sha2.h>

static int recovery_metadata(aether_zpl_view *view)
{
    sa_handle_t *handle = NULL;
    int error = sa_handle_get(view->os, 2, NULL, SA_HDL_PRIVATE, &handle);
    if (error)
        return error;
    uint64_t size = 0, flags = 0, mtime[2] = {0}, ctime[2] = {0};
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
    /* Fixed writer VM UTC base, bounded by its unchanged30-second watchdog.
     * Equal persisted fields and this interval reject stale/invalid metadata;
     * they do not measure exact runtime elapsed time or physical clock drift.
     */
    if (size != 780248 ||
        (flags & (ZFS_ARCHIVE | ZFS_AV_MODIFIED)) !=
            (ZFS_ARCHIVE | ZFS_AV_MODIFIED) ||
        memcmp(mtime, ctime, sizeof(mtime)) ||
        mtime[0] < UINT64_C(1791290040) || mtime[0] > UINT64_C(1791290070) ||
        mtime[1] >= 1000000000)
        return EIO;
    return 0;
}

int aether_pool_namespace_recover(spa_t *spa)
{
    if (!spa || spa_writeable(spa))
        return EROFS;
    aether_zpl_view *view = NULL;
    int error = aether_zpl_open(spa, "testpool_zstd/x86_64", &view);
    if (error)
        return error;
    aether_zpl_node root, file;
    error = aether_zpl_root(view, &root);
    if (!error &&
        (root.object != 34 || root.generation != 45 || root.mode != 040755))
        error = EIO;
    if (!error)
        error = aether_zpl_lookup(view, 34, 45, (const unsigned char *)"zstd",
                                  4, &file);
    if (!error && (file.object != 2 || file.generation != 47 ||
                   file.size != 780248 || file.mode != 0100755))
        error = EIO;
    SHA2_CTX hash;
    SHA2Init(SHA256, &hash);
    unsigned char buffer[4096], digest[32];
    uint64_t offset = 0;
    while (!error && offset < 780248) {
        size_t count = 0;
        error = aether_zpl_read(view, 2, 47, offset, buffer, sizeof(buffer),
                                &count);
        size_t want = MIN(sizeof(buffer), 780248 - offset);
        if (!error && count != want)
            error = EIO;
        if (!error) {
            SHA2Update(&hash, buffer, count);
            offset += count;
        }
    }
    SHA2Final(digest, &hash);
    /* Filled only from independent original-zdb extraction plus Python splice.
     * No writer-produced digest or post-write media supplies this expected
     * data. */
    static const unsigned char expected[32] = {
        0x9a, 0xe4, 0xab, 0x7a, 0x89, 0x6f, 0x9d, 0x76, 0x03, 0x34, 0xd1,
        0xf3, 0x22, 0x99, 0x60, 0x43, 0xe1, 0xe1, 0x32, 0xf4, 0xb1, 0x31,
        0xcc, 0xc3, 0xf2, 0xb7, 0xb2, 0xc5, 0x77, 0xd2, 0xaf, 0xb0};
    if (!error && memcmp(digest, expected, sizeof(expected)))
        error = EIO;
    size_t count = 99;
    if (!error &&
        (aether_zpl_read(view, 2, 47, 780248, buffer, sizeof(buffer), &count) ||
         count))
        error = EIO;
    if (!error)
        error = recovery_metadata(view);
    aether_zpl_close(&view);
    return error;
}
