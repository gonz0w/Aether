/* SPDX-License-Identifier: BSD-2-Clause */
/* Host-only original-decoder comparison on the pinned upstream pool. Not a
 * native capability interface: paths and metadata below are trusted fixtures.
 * Input is READ-only; only zdb's separate private reference output is opened.
 */
#include <sys/zfs_context.h>
#include <sys/dmu.h>
#include <sys/spa.h>
#include <sys/vdev.h>
#include <sys/zfs_znode.h>
#include <libzutil.h>
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>
#include "zpl-read.h"

#include "openzfs_zpl_host_fixture.h"

int main(void)
{
    kernel_init(SPA_MODE_READ);
    nvlist_t *config = fixture_config(), *props = fnvlist_alloc();
    fnvlist_add_string(props, "cachefile", "none");
    fnvlist_add_uint64(props, "readonly", 1);
    REQUIRE(!spa_import(POOL, config, props, 0));
    nvlist_free(props);
    nvlist_free(config);
    spa_t *spa = NULL;
    REQUIRE(!spa_open(POOL, &spa, FTAG));
    REQUIRE(!spa_writeable(spa));
    aether_zpl_view *view = NULL;
    REQUIRE(!aether_zpl_open(spa, DATASET, &view));
    aether_zpl_node root, file, denied;
    REQUIRE(!aether_zpl_root(view, &root));
    REQUIRE(root.object == 34 && root.generation == 45 && root.mode == 040755);
    REQUIRE(!aether_zpl_lookup(view, root.object, root.generation,
                               (const unsigned char *)"zstd", 4, &file));
    REQUIRE(file.object == 2 && file.generation == 47 && file.size == 780248 &&
            file.mode == 0100755);
    EXPECT(aether_zpl_lookup(view, root.object, root.generation - 1,
                             (const unsigned char *)"zstd", 4,
                             &denied) == ESTALE,
           "stale-directory");
    REQUIRE(!denied.object && !denied.generation && !denied.size &&
            !denied.mode);
    REQUIRE(aether_zpl_lookup(view, root.object, root.generation,
                              (const unsigned char *)"..", 2,
                              &denied) == EINVAL);
    REQUIRE(aether_zpl_lookup(view, root.object, root.generation,
                              (const unsigned char *)"absent", 6,
                              &denied) == ENOENT);
    int reference = open(REFERENCE, O_RDONLY | O_CLOEXEC);
    REQUIRE(reference >= 0);
    uint64_t offset = 0;
    unsigned reads = 0;
    unsigned char actual[4096], expected[4096];
    while (offset < file.size) {
        size_t count = 99;
        REQUIRE(!aether_zpl_read(view, file.object, file.generation, offset,
                                 actual, sizeof(actual), &count));
        size_t want = MIN(sizeof(actual), file.size - offset);
        REQUIRE(count == want);
        REQUIRE(read(reference, expected, want) == (ssize_t)want);
        EXPECT(!memcmp(actual, expected, want), "file-bytes");
        offset += count;
        ++reads;
    }
    REQUIRE(read(reference, expected, 1) == 0);
    REQUIRE(!close(reference));
    size_t count = 99;
    REQUIRE(!aether_zpl_read(view, file.object, file.generation, offset, actual,
                             sizeof(actual), &count) &&
            !count);
    REQUIRE(!aether_zpl_read(view, file.object, file.generation, 0, NULL, 0,
                             &count) &&
            !count);
    REQUIRE(aether_zpl_read(view, file.object, file.generation - 1, 0, actual,
                            sizeof(actual), &count) == ESTALE &&
            !count);
    REQUIRE(aether_zpl_read(view, root.object, root.generation, 0, actual,
                            sizeof(actual), &count) == EISDIR &&
            !count);
    aether_zpl_close(&view);
    REQUIRE(!view);
    aether_zpl_close(&view);
    spa_close(spa, FTAG);
    kernel_fini();
    printf("HOST ZPL NAMESPACE PASS root=34 gen=45 file=2 gen=47 bytes=%" PRIu64
           " reads=%u readonly=1 cleanup=1\n",
           offset, reads);
    return 0;
}
