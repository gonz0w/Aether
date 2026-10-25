/* SPDX-License-Identifier: BSD-2-Clause */
/* Private core-local resource binding; quota is not physical memory. */
#include <errno.h>
#include <stdint.h>
#include <stdlib.h>
#include <sys/auxv.h>

static long aether_zfs_native_pages(uint64_t *total)
{
    unsigned long op = 0x22000, grant = getauxval(0xa000);
    unsigned long a = 0, b = 0;
    register unsigned long r10 __asm__("r10") = 0;
    register unsigned long r8 __asm__("r8") = 0;
    register unsigned long r9 __asm__("r9") = 0;
    if (!grant)
        _Exit(125);
    __asm__ __volatile__("int $0x81"
                         : "+a"(op), "+D"(grant), "+S"(a), "+d"(b), "+r"(r10),
                           "+r"(r8), "+r"(r9)
                         :
                         : "rcx", "r11", "cc", "memory");
    *total = r8;
    return (long)op;
}

static uint64_t aether_zfs_observe(int free_pages)
{
    uint64_t total;
    long remaining = aether_zfs_native_pages(&total);
    if (remaining < 0 || !total || (uint64_t)remaining > total ||
        total > INT64_MAX / 4096)
        _Exit(125);
    return free_pages ? (uint64_t)remaining : total;
}

uint64_t aether_zfs_granted_pages(void) { return aether_zfs_observe(0); }

uint64_t aether_zfs_free_pages(void) { return aether_zfs_observe(1); }

long aether_zfs_assigned_cpus(void)
{
    /* Every domain in this profile remains pinned to its owner core. */
    (void)aether_zfs_granted_pages();
    return 1;
}
