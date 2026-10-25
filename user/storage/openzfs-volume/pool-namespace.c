/* SPDX-License-Identifier: BSD-2-Clause */
/* Private fixed-fixture consumer. SPA stays borrowed; context/SA borrows are
 * closed before return, including errors. No externally supplied identities. */
#include <sys/dmu.h>
#include <sys/spa.h>
#include <sys/sha2.h>
#include <string.h>
#include "zpl-read.h"

int aether_pool_namespace_read(spa_t *spa)
{
    aether_zpl_view *view = NULL;
    int error = aether_zpl_open(spa, "testpool_zstd/x86_64", &view);
    if (error)
        return error;
    aether_zpl_node root, file, denied;
    error = aether_zpl_root(view, &root);
    if (!error &&
        (root.object != 34 || root.generation != 45 || root.mode != 040755))
        error = EIO;
    if (!error)
        error = aether_zpl_lookup(view, root.object, root.generation,
                                  (const unsigned char *)"zstd", 4, &file);
    if (!error && (file.object != 2 || file.generation != 47 ||
                   file.size != 780248 || file.mode != 0100755))
        error = EIO;
    if (!error &&
        (aether_zpl_lookup(view, root.object, root.generation - 1,
                           (const unsigned char *)"zstd", 4,
                           &denied) != ESTALE ||
         aether_zpl_lookup(view, root.object, root.generation,
                           (const unsigned char *)"..", 2, &denied) != EINVAL ||
         aether_zpl_lookup(view, root.object, root.generation,
                           (const unsigned char *)"absent", 6,
                           &denied) != ENOENT))
        error = EIO;
    SHA2_CTX hash;
    SHA2Init(SHA256, &hash);
    uint64_t offset = 0;
    unsigned char buffer[4096], digest[SHA256_DIGEST_LENGTH];
    while (!error && offset < file.size) {
        size_t count = 0;
        error = aether_zpl_read(view, file.object, file.generation, offset,
                                buffer, sizeof(buffer), &count);
        size_t want = MIN(sizeof(buffer), file.size - offset);
        if (!error && count != want)
            error = EIO;
        if (!error) {
            SHA2Update(&hash, buffer, count);
            offset += count;
        }
    }
    SHA2Final(digest, &hash);
    static const unsigned char expected[32] = {
        0xcc, 0x9b, 0xfd, 0xde, 0xdd, 0x66, 0x4b, 0x9a, 0x53, 0x34, 0x58,
        0x1a, 0xf7, 0x86, 0x51, 0x6d, 0x14, 0x9c, 0x3f, 0xbd, 0x2c, 0x7e,
        0x65, 0x73, 0x59, 0x85, 0xac, 0xf1, 0x7b, 0xce, 0x59, 0x35};
    if (!error &&
        (offset != 780248 || memcmp(digest, expected, sizeof(expected))))
        error = EIO;
    size_t count = 99;
    if (!error && (aether_zpl_read(view, file.object, file.generation, offset,
                                   buffer, sizeof(buffer), &count) ||
                   count ||
                   aether_zpl_read(view, file.object, file.generation, 0, NULL,
                                   0, &count) ||
                   count ||
                   aether_zpl_read(view, file.object, file.generation - 1, 0,
                                   buffer, sizeof(buffer), &count) != ESTALE ||
                   count ||
                   aether_zpl_read(view, root.object, root.generation, 0,
                                   buffer, sizeof(buffer), &count) != EISDIR ||
                   count))
        error = EIO;
    aether_zpl_close(&view);
    return error;
}
