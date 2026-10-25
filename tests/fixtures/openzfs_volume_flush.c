/* SPDX-License-Identifier: BSD-2-Clause */
/* Host scaffolding for actual owned fsync and pinned upstream flush bodies.
 * Device, ZIO allocation and completion transport are synthetic. No native
 * scheduling, DMA completion, pool or persistence is demonstrated here. */
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include "volume.h"

/* Darwin lacks this flag; retain the selected musl x86_64 value for the shim.
 */
#ifndef O_LARGEFILE
#define O_LARGEFILE 0100000
#endif

typedef int64_t loff_t;
typedef void cred_t;
typedef struct {
    int f_fd, f_dump_fd;
} zfs_file_t;
typedef struct {
    uint64_t zfa_size;
    mode_t zfa_mode;
} zfs_file_attr_t;

static int flush_error;
static unsigned flush_calls;
int aether_volume_bind(uint64_t grant, struct aether_volume *out)
{
    *out = (struct aether_volume){1, 32, grant, 16, 7};
    return 0;
}
int aether_volume_check(const struct aether_volume *volume)
{
    return volume->grant == 17 ? 0 : EBADF;
}
int aether_volume_io(const struct aether_volume *volume, uint32_t write,
                     int64_t offset, void *buffer, size_t count, size_t *done)
{
    (void)volume;
    (void)write;
    (void)offset;
    (void)buffer;
    (void)count;
    *done = 0;
    return ENOTSUP;
}
int aether_volume_flush(const struct aether_volume *volume)
{
    if (aether_volume_check(volume))
        return EBADF;
    if (!(volume->rights & 4))
        return EACCES;
    ++flush_calls;
    return flush_error;
}
#include "file-functions.inc"

typedef struct {
    zfs_file_t *vf_file;
} vdev_file_t;
typedef struct vdev {
    vdev_file_t *vdev_tsd;
    void *vdev_spa;
    unsigned vdev_children;
    struct vdev **vdev_child;
    int vdev_nowritecache;
    int concrete;
} vdev_t;
typedef struct zio {
    vdev_t *io_vd;
    int io_error;
    struct zio *parent;
    unsigned flags;
} zio_t;
typedef unsigned zio_flag_t;
#define ZIO_FLAG_CANFAIL 1
#define ZIO_FLAG_DONT_PROPAGATE 2
#define ZIO_FLAG_DONT_RETRY 4
static zio_t child;
static unsigned interruptions, creations;
static void zio_interrupt(zio_t *zio)
{
    (void)zio;
    ++interruptions;
}
static int vdev_is_concrete(vdev_t *vd) { return vd->concrete; }
static zio_t *record_create(zio_t *parent, vdev_t *vd, unsigned flags)
{
    ++creations;
    child = (zio_t){.io_vd = vd, .parent = parent, .flags = flags};
    return &child;
}
/* Unused macro arguments are inert in these selected body-level checks. */
#define zio_create(parent, spa, txg, bp, abd, logical, physical, done,         \
                   private, type, priority, flags, vd, offset, bookmark,       \
                   stage, pipeline)                                            \
    record_create(parent, vd, flags)
static void zio_nowait(zio_t *zio);
/* Generated only in an owned temporary directory from the pinned sources. */
#include "upstream-flush.inc"
static void zio_nowait(zio_t *zio)
{
    vdev_file_io_fsync(zio);
    /* Model propagation only to expose the actual constructor's flag choice.
     * The full upstream pipeline still requires native qualification. */
    if (!(zio->flags & ZIO_FLAG_DONT_PROPAGATE))
        zio->parent->io_error = zio->io_error;
}

int main(int argc, char **argv)
{
    if (argc != 2)
        return 90;
    int mode = atoi(argv[1]);
    if (mode < 0 || mode > 6 || aether_zfs_volume_bind(17))
        return 91;
    zfs_file_t *file = NULL;
    if (zfs_file_open(AETHER_VOLUME_PATH, O_RDWR, 0, NULL, &file) || !file)
        return 92;
    vdev_file_t ref = {.vf_file = file};
    vdev_t leaf = {.vdev_tsd = &ref, .concrete = 1};
    zio_t parent = {0};
    int expected_error = 0;
    unsigned expected_flushes = 1;
    unsigned expected_children = 1;
    if (mode == 1) {
        flush_error = EIO;
        expected_error = EIO;
    } else if (mode == 2) {
        volume_file(file)->volume.grant = 18;
        expected_error = EBADF;
        expected_flushes = 0;
    } else if (mode == 3) {
        volume_file(file)->volume.rights = 3;
        expected_error = EACCES;
        expected_flushes = 0;
    } else if (mode == 4 || mode == 5) {
        leaf.vdev_nowritecache = mode == 4;
        leaf.concrete = mode != 5;
        expected_children = 0;
        expected_flushes = 0;
    } else if (mode == 6) {
        if (zfs_file_fsync(file, O_APPEND) != ENOTSUP || flush_calls ||
            zfs_file_fsync(NULL, O_SYNC) != EBADF)
            return 93;
    }
    zio_flush(&parent, &leaf);
    if (creations != expected_children || interruptions != expected_children ||
        flush_calls != expected_flushes || parent.io_error != 0)
        return 94;
    if (expected_children &&
        (child.io_error != expected_error || child.io_vd != &leaf ||
         child.flags != (ZIO_FLAG_CANFAIL | ZIO_FLAG_DONT_PROPAGATE |
                         ZIO_FLAG_DONT_RETRY)))
        return 95;
    zfs_file_close(file);
    return 0;
}
