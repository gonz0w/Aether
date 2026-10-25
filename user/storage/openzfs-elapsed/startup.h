/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_ZFS_STARTUP_H
#define AETHER_ZFS_STARTUP_H
#include <stdint.h>
#include <sys/utsname.h>

/* Private same-domain record, not a wire/kernel ABI or authenticated identity.
 * Bind/copy once from the initial thread before engine workers exist. */
enum { AETHER_ZFS_EMPTY_CACHE = 1 };
struct aether_zfs_startup {
    uint32_t version, bytes, hostid, cache_policy;
    uint8_t reserved[8];
    char sysname[65], nodename[65], release[65], version_label[65], machine[65];
    uint8_t padding[3];
};
_Static_assert(sizeof(struct aether_zfs_startup) == 352,
               "private startup layout");
int aether_zfs_startup_bind(const struct aether_zfs_startup *);
unsigned long aether_zfs_hostid(void);
void aether_zfs_uname(struct utsname *);
void aether_zfs_empty_cache(void);
#endif
