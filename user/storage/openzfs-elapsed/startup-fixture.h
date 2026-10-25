/* SPDX-License-Identifier: BSD-2-Clause */
#include "startup.h"
/* Declared private experiment labels, not a persistent machine-ID policy.
 * No cache/pool is imported; labels confer no native permission. */
static const struct aether_zfs_startup startup_fixture = {
    .version = 1,
    .bytes = sizeof(struct aether_zfs_startup),
    .hostid = 0x41455448,
    .cache_policy = AETHER_ZFS_EMPTY_CACHE,
    .sysname = "Aether",
    .nodename = "storage-fixture",
    .release = "experimental",
    .version_label = "private-empty-engine",
    .machine = "x86_64",
};
