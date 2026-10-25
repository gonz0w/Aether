/* SPDX-License-Identifier: BSD-2-Clause */
/* Selected private libzpool file provider. Initial thread publishes once before
 * helpers start; no host paths or global mutable descriptor table. File refs
 * returned by open are engine-owned valid borrows until close. Close frees only
 * that ref; the native region grant remains live until owner retirement. */
#include "volume.h"
static struct aether_volume volume_binding;
static int volume_published;
struct volume_file {
    zfs_file_t file;
    struct aether_volume volume;
};
#define VOLUME_FILE_MAGIC 0x41564f4c
int aether_zfs_volume_bind(uint64_t grant)
{
    if (volume_published)
        return EALREADY;
    struct aether_volume candidate;
    int error = aether_volume_bind(grant, &candidate);
    if (error)
        return error;
    volume_binding = candidate;
    volume_published = 1;
    return 0;
}
static struct volume_file *volume_file(zfs_file_t *fp)
{
    return fp && fp->f_dump_fd == VOLUME_FILE_MAGIC ? (struct volume_file *)fp
                                                    : NULL;
}
int zfs_file_open(const char *path, int flags, int mode, cred_t *cr,
                  zfs_file_t **fpp)
{
    (void)cr;
    if (!fpp)
        return EINVAL;
    *fpp = NULL;
    if (!path || strcmp(path, AETHER_VOLUME_PATH))
        return ENOENT;
    if (!volume_published)
        return ENODEV;
    if (mode || (flags & ~(O_ACCMODE | O_LARGEFILE)) ||
        (flags & O_ACCMODE) > O_RDWR)
        return ENOTSUP;
    int error = aether_volume_check(&volume_binding);
    if (error)
        return error;
    int access = flags & O_ACCMODE;
    uint64_t required = access == O_RDONLY ? 1 : access == O_WRONLY ? 2 : 3;
    if ((volume_binding.rights & required) != required)
        return EACCES;
    struct volume_file *ref = calloc(1, sizeof(*ref));
    if (!ref)
        return ENOMEM;
    ref->file.f_fd = access;
    ref->file.f_dump_fd = VOLUME_FILE_MAGIC;
    ref->volume = volume_binding;
    *fpp = &ref->file;
    return 0;
}
void zfs_file_close(zfs_file_t *fp)
{
    struct volume_file *ref = volume_file(fp);
    if (!ref)
        _Exit(125);
    ref->file.f_dump_fd = 0;
    free(ref);
}
static int volume_io(zfs_file_t *fp, int write, void *buf, size_t count,
                     loff_t offset, ssize_t *resid)
{
    if (count > SSIZE_MAX)
        return EOVERFLOW;
    if (resid)
        *resid = count;
    struct volume_file *ref = volume_file(fp);
    if (!ref)
        return EBADF;
    if ((write && fp->f_fd == O_RDONLY) || (!write && fp->f_fd == O_WRONLY))
        return EACCES;
    size_t done = 0;
    int error =
        aether_volume_io(&ref->volume, write, offset, buf, count, &done);
    if (done > count)
        _Exit(125);
    if (resid)
        *resid = count - done;
    return error;
}
int zfs_file_pread(zfs_file_t *fp, void *buf, size_t count, loff_t off,
                   ssize_t *resid)
{
    return volume_io(fp, 0, buf, count, off, resid);
}
int zfs_file_pwrite(zfs_file_t *fp, const void *buf, size_t count, loff_t off,
                    uint8_t ashift, ssize_t *resid)
{
    if (ashift < 9 || ashift > 17) {
        if (resid && count <= SSIZE_MAX)
            *resid = count;
        return EINVAL;
    }
    return volume_io(fp, 1, (void *)buf, count, off, resid);
}
int zfs_file_getattr(zfs_file_t *fp, zfs_file_attr_t *attr)
{
    struct volume_file *ref = volume_file(fp);
    if (!ref || !attr)
        return EINVAL;
    int error = aether_volume_check(&ref->volume);
    if (error)
        return error;
    memset(attr, 0, sizeof(*attr));
    attr->zfa_size = ref->volume.sectors * 512;
    attr->zfa_mode = S_IFBLK;
    return 0;
}
int zfs_file_fsync(zfs_file_t *fp, int flags)
{
    struct volume_file *ref = volume_file(fp);
    if (!ref)
        return EBADF;
    if (flags & ~(O_SYNC | O_DSYNC))
        return ENOTSUP;
    return aether_volume_flush(&ref->volume);
}
int zfs_file_write(zfs_file_t *fp, const void *buf, size_t count,
                   ssize_t *resid)
{
    (void)fp;
    (void)buf;
    if (resid && count <= SSIZE_MAX)
        *resid = count;
    return ENOTSUP;
}
int zfs_file_read(zfs_file_t *fp, void *buf, size_t count, ssize_t *resid)
{
    return zfs_file_write(fp, buf, count, resid);
}
int zfs_file_seek(zfs_file_t *fp, loff_t *offp, int whence)
{
    (void)fp;
    (void)offp;
    (void)whence;
    return ENOTSUP;
}
int zfs_file_deallocate(zfs_file_t *fp, loff_t offset, loff_t len)
{
    (void)fp;
    (void)offset;
    (void)len;
    return ENOTSUP;
}
loff_t zfs_file_off(zfs_file_t *fp)
{
    (void)fp;
    errno = ENOTSUP;
    return -1;
}
int zfs_file_unlink(const char *path)
{
    (void)path;
    return ENOTSUP;
}
