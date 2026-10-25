/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_ZFS_RESOURCES_H
#define AETHER_ZFS_RESOURCES_H
#include <stdint.h>
uint64_t aether_zfs_granted_pages(void);
uint64_t aether_zfs_free_pages(void);
long aether_zfs_assigned_cpus(void);
#endif
