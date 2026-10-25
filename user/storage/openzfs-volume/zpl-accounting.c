/* SPDX-License-Identifier: BSD-2-Clause */
#include <sys/dmu.h>
#include <sys/zfs_quota.h>
#include "zpl-write.h"

/* Trusted engine startup only: after kernel_init, before import/open; no
 * concurrent registry readers or writers. Callback code remains mapped through
 * all objset/taskq drains and kernel_fini. Never invoke from a client request.
 */
void aether_zpl_accounting_init(void)
{
    dmu_objset_register_type(DMU_OST_ZFS, zpl_get_file_info);
}
