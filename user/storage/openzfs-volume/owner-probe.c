/* SPDX-License-Identifier: BSD-2-Clause */
/* Original SHA2 verifies only bytes returned through the Rust handle owner. */
#include <sys/dmu.h>
#include <sys/spa.h>
#include <sys/sha2.h>
#include <string.h>
#include "owner-probe.h"
#include "zpl-read.h"

_Static_assert(sizeof(aether_zpl_node) == 32, "Rust ZPL node size");
_Static_assert(_Alignof(aether_zpl_node) == 8, "Rust ZPL node alignment");
_Static_assert(offsetof(aether_zpl_node, mode) == 24, "Rust ZPL mode offset");

int aether_namespace_hash_update(void *state, const unsigned char *bytes,
                                 size_t length)
{
    if (!state || !bytes || !length || length > 4096)
        return EINVAL;
    SHA2Update(state, bytes, length);
    return 0;
}

int aether_pool_namespace_read(spa_t *spa)
{
    if (!spa)
        return EINVAL;
    SHA2_CTX hash;
    unsigned char digest[SHA256_DIGEST_LENGTH];
    SHA2Init(SHA256, &hash);
    int error = aether_namespace_owner_probe(spa, &hash);
    SHA2Final(digest, &hash);
    static const unsigned char expected[32] = {
        0xcc, 0x9b, 0xfd, 0xde, 0xdd, 0x66, 0x4b, 0x9a, 0x53, 0x34, 0x58,
        0x1a, 0xf7, 0x86, 0x51, 0x6d, 0x14, 0x9c, 0x3f, 0xbd, 0x2c, 0x7e,
        0x65, 0x73, 0x59, 0x85, 0xac, 0xf1, 0x7b, 0xce, 0x59, 0x35};
    if (!error && memcmp(digest, expected, sizeof(expected)))
        error = EIO;
    return error;
}
