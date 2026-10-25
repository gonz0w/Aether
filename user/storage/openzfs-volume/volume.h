/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_ZFS_VOLUME_H
#define AETHER_ZFS_VOLUME_H
#include <stddef.h>
#include <stdint.h>
/* Private synchronous C/Rust seam, not a released ABI. Metadata pointers must
 * be valid, aligned in-process borrows with no overlapping outputs. Keep the
 * immutable record and I/O storage alive until return; close/revoke only after
 * all users settle. I/O buffers are forwarded to native validation, never
 * dereferenced by Rust. Positive errno and exact complete-sector byte counts
 * preserve partial effects; callers must not blindly replay failed writes. */
struct aether_volume {
    uint32_t version, bytes;
    uint64_t grant, sectors, rights;
};
_Static_assert(sizeof(struct aether_volume) == 32, "volume layout");
int aether_volume_bind(uint64_t, struct aether_volume *);
int aether_volume_check(const struct aether_volume *);
int aether_volume_io(const struct aether_volume *, uint32_t, int64_t, void *,
                     size_t, size_t *);
int aether_volume_flush(const struct aether_volume *);
#define AETHER_VOLUME_PATH "/aether-volume/poc0"
int aether_zfs_volume_bind(uint64_t);
#endif
