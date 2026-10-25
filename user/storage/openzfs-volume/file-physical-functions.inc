/* SPDX-License-Identifier: BSD-2-Clause */
/* Physical fixture only. Preserve the provider body and delegate exactly once.
 * The weak phase hook supports unexecuted intermediate links; final composition
 * requires its strong definition. Pointers remain synchronous provider borrows.
 */
int aether_physical_pread_original(zfs_file_t *, void *, size_t, loff_t,
                                   ssize_t *) __attribute__((__noinline__));
#ifdef AETHER_PHYSICAL_WRITE
#include "write-witness.h"
int aether_physical_pwrite_original(zfs_file_t *, const void *, size_t, loff_t,
                                    uint8_t, ssize_t *)
    __attribute__((__noinline__));
int aether_physical_fsync_provider_original(zfs_file_t *, int)
    __attribute__((__noinline__));
#define zfs_file_pwrite aether_physical_pwrite_original
#define zfs_file_fsync aether_physical_fsync_provider_original
#endif
#define zfs_file_pread aether_physical_pread_original
#include "file-functions.inc"
#undef zfs_file_pread
extern void aether_physical_io_phase(unsigned char) __attribute__((__weak__));
#ifdef AETHER_PHYSICAL_WRITE
#undef zfs_file_pwrite
#undef zfs_file_fsync
#include "write-functions.inc"
#endif
int zfs_file_pread(zfs_file_t *fp, void *buf, size_t count, loff_t off,
                   ssize_t *resid)
{
    int observed = count == 512 && off == 1048576;
    if (observed && aether_physical_io_phase)
        aether_physical_io_phase('S');
#ifdef AETHER_PHYSICAL_OPEN_TRACE
    if (count == 8192 && aether_physical_io_phase)
        aether_physical_io_phase('L');
#endif
    int error = aether_physical_pread_original(fp, buf, count, off, resid);
    if (observed && aether_physical_io_phase)
        aether_physical_io_phase(error ? 'X' : 'T');
#ifdef AETHER_PHYSICAL_OPEN_TRACE
    if (count == 8192 && aether_physical_io_phase)
        aether_physical_io_phase(error ? 'Y' : 'M');
#endif
    return error;
}
