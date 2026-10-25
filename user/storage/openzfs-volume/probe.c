/* SPDX-License-Identifier: BSD-2-Clause */
/* Actual file-vdev open/close and positioned provider qualification, not a ZIO
 * transaction or pool. All disks and regions are disposable private fixtures.
 */
#include <sys/spa_impl.h>
#include <sys/vdev_impl.h>
#include <sys/zfs_file.h>
#include <sys/auxv.h>
#include <sys/stat.h>
#include <sys/mman.h>
#include "volume.h"
#define REQUIRE(ok)                                                            \
    do {                                                                       \
        if (!(ok))                                                             \
            return 845;                                                        \
    } while (0)
static int bound;
static int data(const unsigned char *bytes, unsigned base)
{
    for (unsigned i = 0; i < 512; ++i)
        if (bytes[i] != (unsigned char)(i * 17 + base))
            return 0;
    return 1;
}
int aether_volume_start_probe(void)
{
    if (getauxval(0xa001) != 0x50000101UL) {
        REQUIRE(aether_zfs_volume_bind(0xf101) == EACCES);
        return 0;
    }
    struct timespec until;
    REQUIRE(!clock_gettime(CLOCK_MONOTONIC, &until));
    ++until.tv_sec;
    int result;
    do {
        result = aether_zfs_volume_bind(0xf101);
        if (result == EACCES) {
            struct timespec current, pause = {0, 1000000};
            REQUIRE(!clock_gettime(CLOCK_MONOTONIC, &current) &&
                    (current.tv_sec < until.tv_sec ||
                     (current.tv_sec == until.tv_sec &&
                      current.tv_nsec < until.tv_nsec)) &&
                    !nanosleep(&pause, NULL));
        }
    } while (result == EACCES);
    REQUIRE(!result && aether_zfs_volume_bind(0xf101) == EALREADY);
    bound = 1;
    return 0;
}
int aether_volume_engine_probe(int verify, int readonly)
{
    zfs_file_t *fp = NULL;
    REQUIRE(zfs_file_open("/host/path", O_RDONLY, 0, NULL, &fp) == ENOENT &&
            !fp);
    if (!bound) {
        REQUIRE(zfs_file_open(AETHER_VOLUME_PATH, O_RDONLY, 0, NULL, &fp) ==
                    ENODEV &&
                !fp);
        return 0;
    }
    REQUIRE(zfs_file_open(AETHER_VOLUME_PATH, O_CREAT | O_RDWR, 0, NULL, &fp) ==
                ENOTSUP &&
            !fp);
    spa_t *spa = calloc(1, sizeof(*spa));
    vdev_t *vd = calloc(1, sizeof(*vd));
    REQUIRE(spa && vd);
    spa->spa_mode = readonly ? SPA_MODE_READ : SPA_MODE_READ | SPA_MODE_WRITE;
    vd->vdev_spa = spa;
    vd->vdev_path = AETHER_VOLUME_PATH;
    uint64_t size = 0, maximum = 0, logical = 0, physical = 0;
    REQUIRE(!vdev_file_ops.vdev_op_open(vd, &size, &maximum, &logical,
                                        &physical, NULL));
    REQUIRE(size == 16384 * 512 && maximum == size && logical == 9 &&
            physical == 9 && vd->vdev_nonrot && !vd->vdev_has_trim &&
            !vd->vdev_has_securetrim && vd->vdev_tsd);
    void *reference = vd->vdev_tsd;
    vd->vdev_reopening = B_TRUE;
    REQUIRE(!vdev_file_ops.vdev_op_open(vd, &size, &maximum, &logical,
                                        &physical, NULL) &&
            vd->vdev_tsd == reference);
    vdev_file_ops.vdev_op_close(vd);
    REQUIRE(vd->vdev_tsd == reference);
    vd->vdev_reopening = B_FALSE;
    vdev_file_ops.vdev_op_close(vd);
    REQUIRE(!vd->vdev_tsd);
    free(vd);
    free(spa);
    REQUIRE(!zfs_file_open(AETHER_VOLUME_PATH, readonly ? O_RDONLY : O_RDWR, 0,
                           NULL, &fp));
    zfs_file_attr_t attr;
    REQUIRE(!zfs_file_getattr(fp, &attr) && attr.zfa_size == size &&
            S_ISBLK(attr.zfa_mode));
    unsigned char bytes[1024];
    memset(bytes, 29, sizeof(bytes));
    ssize_t resid = -1;
    REQUIRE(!zfs_file_pread(fp, bytes, 512, 0, &resid) && resid == 0);
    if (!data(bytes, verify ? 91 : 3))
        return 840;
    REQUIRE(!zfs_file_pread(fp, bytes, sizeof(bytes), 512, &resid) &&
            resid == 0);
    for (unsigned i = 0; i < sizeof(bytes); ++i)
        REQUIRE(bytes[i] == 165);
    REQUIRE(!zfs_file_pread(fp, bytes, 512, size - 512, &resid) && !resid);
    memset(bytes, 29, sizeof(bytes));
    REQUIRE(zfs_file_pread(fp, bytes, 1024, size - 512, &resid) == EINVAL &&
            resid == 1024);
    for (unsigned i = 0; i < sizeof(bytes); ++i)
        REQUIRE(bytes[i] == 29);
    REQUIRE(zfs_file_pread(fp, bytes, 512, -512, &resid) == EINVAL &&
            resid == 512);
    REQUIRE(zfs_file_pread(fp, bytes, 513, 0, &resid) == EINVAL &&
            resid == 513);
    REQUIRE(!zfs_file_pread(fp, NULL, 0, size, &resid) && !resid);
    REQUIRE(zfs_file_pwrite(fp, bytes, 1024, size - 512, 9, &resid) ==
                (readonly ? EACCES : EINVAL) &&
            resid == 1024);
    unsigned char *pages = mmap(NULL, 8192, PROT_READ | PROT_WRITE,
                                MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    REQUIRE(pages != MAP_FAILED);
    memset(pages, 29, 8192);
    REQUIRE(!mprotect(pages + 4096, 4096, PROT_NONE));
    REQUIRE(zfs_file_pread(fp, pages + 3584, 1024, 0, &resid) == EFAULT &&
            resid == 512 && data(pages + 3584, verify ? 91 : 3));
    if (!readonly) {
        memset(pages + 3584, 165, 512);
        REQUIRE(zfs_file_pwrite(fp, pages + 3584, 1024, 512, 9, &resid) ==
                    EFAULT &&
                resid == 512);
    }
    REQUIRE(!mprotect(pages + 4096, 4096, PROT_READ | PROT_WRITE));
    for (unsigned i = 4096; i < 8192; ++i)
        REQUIRE(pages[i] == 29);
    REQUIRE(!munmap(pages, 8192));
    zfs_file_t *readref = NULL;
    REQUIRE(!zfs_file_open(AETHER_VOLUME_PATH, O_RDONLY, 0, NULL, &readref));
    REQUIRE(zfs_file_pwrite(readref, bytes, 512, 0, 9, &resid) == EACCES &&
            resid == 512);
    zfs_file_close(readref);
    if (readonly) {
        REQUIRE(zfs_file_open(AETHER_VOLUME_PATH, O_RDWR, 0, NULL, &readref) ==
                    EACCES &&
                !readref);
        REQUIRE(zfs_file_fsync(fp, O_SYNC | O_DSYNC) == EACCES);
    } else if (!verify) {
        for (unsigned i = 0; i < 512; ++i)
            bytes[i] = (unsigned char)(i * 17 + 91);
        REQUIRE(!zfs_file_pwrite(fp, bytes, 512, 0, 9, &resid) && !resid &&
                !zfs_file_fsync(fp, O_SYNC | O_DSYNC));
    }
    REQUIRE(zfs_file_deallocate(fp, 0, 512) == ENOTSUP &&
            zfs_file_fsync(fp, O_CREAT) == ENOTSUP &&
            zfs_file_unlink(AETHER_VOLUME_PATH) == ENOTSUP);
    loff_t off = 17;
    REQUIRE(zfs_file_seek(fp, &off, SEEK_SET) == ENOTSUP && off == 17 &&
            zfs_file_read(fp, bytes, 512, &resid) == ENOTSUP && resid == 512 &&
            zfs_file_write(fp, bytes, 512, &resid) == ENOTSUP && resid == 512 &&
            zfs_file_off(fp) == -1 && errno == ENOTSUP);
    zfs_file_close(fp);
    REQUIRE(!zfs_file_open(AETHER_VOLUME_PATH, O_RDONLY, 0, NULL, &fp));
    REQUIRE(!zfs_file_pread(fp, bytes, 512, 0, &resid) && !resid &&
            data(bytes, readonly ? 3 : 91));
    zfs_file_close(fp);
    return 0;
}
int aether_volume_finish_probe(void)
{
    if (!bound)
        return 0;
    unsigned long op = 0x27004, second = 0;
    register unsigned long r10 __asm__("r10") = 0;
    register unsigned long r8 __asm__("r8") = 0, r9 __asm__("r9") = 0;
    __asm__ volatile("int $0x81"
                     : "+a"(op), "+d"(second), "+r"(r10), "+r"(r8), "+r"(r9)
                     : "D"(0xf101UL), "S"(0UL)
                     : "rcx", "r11", "memory", "cc");
    REQUIRE(!op);
    zfs_file_t *fp = NULL;
    REQUIRE(zfs_file_open(AETHER_VOLUME_PATH, O_RDONLY, 0, NULL, &fp) ==
                EBADF &&
            !fp);
    return 0;
}
