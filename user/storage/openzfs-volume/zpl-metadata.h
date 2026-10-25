/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_ZPL_METADATA_H
#define AETHER_ZPL_METADATA_H
#include "zpl-directories.h"

typedef struct aether_zpl_time {
    int64_t seconds;
    uint64_t nanoseconds;
} aether_zpl_time;

typedef struct aether_zpl_metadata {
    aether_zpl_node node;
    uint64_t parent, links, uid, gid, flags;
    aether_zpl_time atime, mtime, ctime, birthtime;
} aether_zpl_metadata;

_Static_assert(sizeof(aether_zpl_time) == 16 &&
                   offsetof(aether_zpl_time, nanoseconds) == 8 &&
                   sizeof(aether_zpl_metadata) == 136 &&
                   offsetof(aether_zpl_metadata, parent) == 32 &&
                   offsetof(aether_zpl_metadata, atime) == 72,
               "private metadata FFI layout");

/* Trusted engine-owner FFI only. Compile zpl-metadata.c INSTEAD OF the
 * directory/mutation/write/read providers. Their existing context, SPA and
 * serialization obligations remain unchanged. No filesystem mutation or new
 * retained allocation; temporary original SA handles may allocate and are
 * released before return. No new allocator, transaction or retained state.
 * Expected identity must come from an authorized service handle, never a raw
 * client object. The valid output is disjoint from all inputs/context and is
 * zero on any error; positive errno, no retained pointer or mutable state.
 * Raw owner/FUID labels, mode, flags and links confer no authority and are not
 * a POSIX credential/ACL translation. Preserve high labels/special bits/links;
 * the caller must translate with checked bounds or explicitly reject support.
 * Times preserve signed seconds, nanoseconds must be below1e9. Calls must be
 * serialized against ALL external mutation/property changes/export/teardown;
 * no cross-call atomic snapshot or public stat/permission guarantee is implied.
 */
int aether_zpl_getattr(aether_zpl_view *, uint64_t object, uint64_t generation,
                       aether_zpl_metadata *);
#endif
