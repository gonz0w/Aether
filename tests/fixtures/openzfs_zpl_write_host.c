/* SPDX-License-Identifier: BSD-2-Clause */
/* Host-only original-media qualification. All paths are private fixture inputs;
 * never expose this main or its metadata inspection as a service API. */
#include <sys/zfs_context.h>
#include <sys/dmu.h>
#include <sys/dmu_objset.h>
#include <sys/sa.h>
#include <sys/spa.h>
#include <sys/vdev.h>
#include <sys/zap.h>
#include <sys/zfs_znode.h>
#include <sys/zfs_sa.h>
#include <sys/zfs_quota.h>
#include <libzutil.h>
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>
#include "zpl-write.h"
#include "openzfs_zpl_host_fixture.h"

#define ORIGINAL_SIZE UINT64_C(780248)
#define FINAL_SIZE (ORIGINAL_SIZE + 43)
#define FINAL_SECONDS UINT64_C(1893456002)
#define FINAL_NANOSECONDS UINT64_C(123456791)

static void compare(aether_zpl_view *view, uint64_t size, const char *path)
{
    int fd = open(path, O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    REQUIRE(fd >= 0);
    uint64_t offset = 0;
    unsigned char actual[4096], expected[4096];
    while (offset < size) {
        size_t count = 0;
        REQUIRE(!aether_zpl_read(view, 2, 47, offset, actual, sizeof(actual),
                                 &count));
        size_t want = MIN(sizeof(actual), size - offset);
        EXPECT(count == want, "file-size");
        REQUIRE(read(fd, expected, want) == (ssize_t)want);
        EXPECT(!memcmp(actual, expected, want), "file-bytes");
        offset += count;
    }
    REQUIRE(read(fd, expected, 1) == 0);
    REQUIRE(!close(fd));
    size_t count = 99;
    REQUIRE(
        !aether_zpl_read(view, 2, 47, size, actual, sizeof(actual), &count) &&
        !count);
    aether_zpl_node root, file;
    REQUIRE(!aether_zpl_root(view, &root));
    REQUIRE(root.object == 34 && root.generation == 45);
    REQUIRE(!aether_zpl_lookup(view, 34, 45, (const unsigned char *)"zstd", 4,
                               &file));
    EXPECT(file.object == 2 && file.generation == 47 && file.size == size &&
               file.mode == 0100755,
           "file-metadata");
}

static void metadata(void)
{
    /* An additional scoped borrow independently reads the original SA fields.
     * The caller serializes writes; no mutable alias escapes this function. */
    objset_t *os = NULL;
    REQUIRE(!dmu_objset_hold(DATASET, FTAG, &os));
    uint64_t master = 0;
    REQUIRE(!zap_lookup(os, MASTER_NODE_OBJ, ZFS_SA_ATTRS, 8, 1, &master));
    sa_attr_type_t *map = NULL;
    REQUIRE(!sa_setup(os, master, zfs_attr_table, ZPL_END, &map));
    sa_handle_t *handle = NULL;
    REQUIRE(!sa_handle_get(os, 2, NULL, SA_HDL_PRIVATE, &handle));
    uint64_t size = 0, flags = 0, mtime[2] = {0}, ctime[2] = {0};
    sa_bulk_attr_t attrs[4];
    int n = 0;
    SA_ADD_BULK_ATTR(attrs, n, map[ZPL_SIZE], NULL, &size, sizeof(size));
    SA_ADD_BULK_ATTR(attrs, n, map[ZPL_FLAGS], NULL, &flags, sizeof(flags));
    SA_ADD_BULK_ATTR(attrs, n, map[ZPL_MTIME], NULL, mtime, sizeof(mtime));
    SA_ADD_BULK_ATTR(attrs, n, map[ZPL_CTIME], NULL, ctime, sizeof(ctime));
    REQUIRE(!sa_bulk_lookup(handle, attrs, n));
    sa_handle_destroy(handle);
    dmu_objset_rele(os, FTAG);
    EXPECT(size == FINAL_SIZE && mtime[0] == FINAL_SECONDS &&
               mtime[1] == FINAL_NANOSECONDS && ctime[0] == FINAL_SECONDS &&
               ctime[1] == FINAL_NANOSECONDS &&
               (flags & (ZFS_ARCHIVE | ZFS_AV_MODIFIED)) ==
                   (ZFS_ARCHIVE | ZFS_AV_MODIFIED),
           "sa-metadata");
}

static void write_one(aether_zpl_view *view, unsigned step, uint64_t offset,
                      size_t length)
{
    unsigned char data[31];
    REQUIRE(length <= sizeof(data));
    for (size_t i = 0; i < length; ++i)
        data[i] = (unsigned char)(step * 53 + i * 17);
    aether_zpl_node file;
    REQUIRE(!aether_zpl_lookup(view, 34, 45, (const unsigned char *)"zstd", 4,
                               &file));
    uint64_t size = MAX(file.size, offset + length);
    aether_zpl_write_result result;
    int error = aether_zpl_write(view, 2, 47, offset, data, length,
                                 UINT64_C(1893456000) + step,
                                 UINT64_C(123456789) + step, &result);
    if (error)
        fprintf(stderr,
                "HOST ZPL WRITE error=%d txg=%" PRIu64 " staged=%" PRIu64
                " state=%" PRIu64 "\n",
                error, result.txg, result.bytes_staged, result.state);
    EXPECT(!error && result.txg && result.bytes_staged == length &&
               result.state == AETHER_ZPL_SYNCED,
           "write-progress");
    REQUIRE(!aether_zpl_lookup(view, 34, 45, (const unsigned char *)"zstd", 4,
                               &file));
    EXPECT(file.size == size, "write-size");
    printf("HOST ZPL WRITE step=%u txg=%" PRIu64 " bytes=%zu synced=1\n", step,
           result.txg, length);
}

static void denied(aether_zpl_view *view)
{
    const unsigned char byte = 0;
    for (unsigned mode = 0; mode < 6; ++mode) {
        aether_zpl_write_result result = {99, 99, 99};
        int error = aether_zpl_write(
            view, 2, mode == 0 ? 46 : 47,
            mode == 1 ? FINAL_SIZE + 1 : FINAL_SIZE, &byte,
            mode == 2   ? 4097
            : mode == 5 ? 0
                        : 1,
            mode == 3 ? UINT64_MAX : FINAL_SECONDS,
            mode == 4 ? UINT64_C(1000000000) : FINAL_NANOSECONDS, &result);
        int want[] = {ESTALE, EINVAL, EINVAL, EINVAL, EINVAL, 0};
        EXPECT(error == want[mode] && !result.txg && !result.bytes_staged &&
                   result.state == AETHER_ZPL_UNASSIGNED,
               "denial-progress");
    }
}

int main(int argc, char **argv)
{
    REQUIRE(argc == 2 &&
            (!strcmp(argv[1], "write") || !strcmp(argv[1], "read")));
    boolean_t write = !strcmp(argv[1], "write");
    kernel_init(write ? SPA_MODE_READ | SPA_MODE_WRITE : SPA_MODE_READ);
#ifndef OMIT_ACCOUNTING_CALLBACK
    if (write)
        dmu_objset_register_type(DMU_OST_ZFS, zpl_get_file_info);
#endif
    nvlist_t *config = fixture_config(), *props = fnvlist_alloc();
    fnvlist_add_string(props, "cachefile", "none");
    if (!write)
        fnvlist_add_uint64(props, "readonly", 1);
    REQUIRE(!spa_import(POOL, config, props, 0));
    nvlist_free(props);
    nvlist_free(config);
    spa_t *spa = NULL;
    REQUIRE(!spa_open(POOL, &spa, FTAG));
    REQUIRE(!!spa_writeable(spa) == !!write);
    aether_zpl_view *view = NULL;
    int error = write ? aether_zpl_open_write(spa, DATASET, &view)
                      : aether_zpl_open(spa, DATASET, &view);
    if (error)
        fprintf(stderr, "HOST ZPL WRITE open-error=%d\n", error);
    EXPECT(!error && view, "open");
    if (write) {
        compare(view, ORIGINAL_SIZE, REFERENCE);
        write_one(view, 0, 37, 23);
        write_one(view, 1, ORIGINAL_SIZE, 19);
        write_one(view, 2, ORIGINAL_SIZE + 12, 31);
        denied(view);
    }
    compare(view, FINAL_SIZE, "/work/expected-zstd.bin");
    metadata();
    aether_zpl_close(&view);
    REQUIRE(!view);
    spa_close(spa, FTAG);
    if (write) {
        config = NULL;
        REQUIRE(!spa_export(POOL, &config, B_FALSE, B_FALSE));
        nvlist_free(config);
    }
    kernel_fini();
    printf("HOST ZPL WRITE PASS mode=%s bytes=%" PRIu64
           " metadata=1 cleanup=1\n",
           argv[1], FINAL_SIZE);
    return 0;
}
