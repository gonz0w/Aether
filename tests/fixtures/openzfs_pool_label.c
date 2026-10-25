/* SPDX-License-Identifier: BSD-2-Clause */
/* Actual reader/adapter bodies over synthetic nvlist decoding and transport.
 * No label codec, checksum, native authority or persistence claim. */
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>

#define VDEV_LABELS 4
#define VDEV_SKIP_SIZE 16384
#define PAGESIZE 4096
#define UMEM_DEFAULT 0
#define SPA_VERSION_FEATURES 5000
#define POOL_STATE_ACTIVE 0
#define POOL_STATE_EXPORTED 1
#define POOL_STATE_SPARE 3
#define POOL_STATE_L2CACHE 4
#define VDEV_TYPE_FILE "file"
#define P2ALIGN_TYPED(x, align, type) ((type)(x) & ~((type)(align) - 1))
#define P2PHASE_TYPED(x, align, type) ((type)(x) & ((type)(align) - 1))
#define ASSERT0(x) assert((x) == 0)
enum {
    ZPOOL_CONFIG_GUID,
    ZPOOL_CONFIG_POOL_GUID,
    ZPOOL_CONFIG_TOP_GUID,
    ZPOOL_CONFIG_POOL_STATE,
    ZPOOL_CONFIG_VERSION,
    ZPOOL_CONFIG_POOL_TXG,
    ZPOOL_CONFIG_VDEV_CHILDREN,
    ZPOOL_CONFIG_POOL_NAME,
    ZPOOL_CONFIG_VDEV_TREE,
    ZPOOL_CONFIG_TYPE,
    ZPOOL_CONFIG_PATH,
    ZPOOL_CONFIG_ID,
    ZPOOL_CONFIG_ASHIFT,
    ZPOOL_CONFIG_IS_LOG,
    ZPOOL_CONFIG_IS_SPARE,
    ZPOOL_CONFIG_CHILDREN,
    ZPOOL_CONFIG_SPARES,
    ZPOOL_CONFIG_L2CACHE,
    ZPOOL_CONFIG_HOLE_ARRAY,
    ZPOOL_CONFIG_FEATURES_FOR_READ
};
typedef struct {
    char vp_nvlist[(112 << 10) - 40];
    char checksum[40];
} vdev_phys_t;
typedef struct {
    char bytes[256 << 10];
} vdev_label_t;
typedef struct {
    int role, index;
} nvlist_t;
typedef struct {
    int value;
} zfs_file_t;
typedef struct {
    uint64_t zfa_size;
} zfs_file_attr_t;
static int mode, reads, opened, closed, allocations, freed, decoded, live;
static zfs_file_t file;
static nvlist_t leaf = {1, 0}, features = {2, 0};

static void *umem_alloc_aligned(size_t size, size_t align, int flags)
{
    assert(size == sizeof(vdev_phys_t) && align == PAGESIZE && !flags);
    if (mode == 5)
        return NULL;
    ++allocations;
    return malloc(size);
}
static void umem_free_aligned(void *ptr, size_t size)
{
    assert(ptr && size == sizeof(vdev_phys_t));
    --allocations;
    free(ptr);
}
static int nvlist_unpack(char *bytes, size_t size, nvlist_t **output, int flags)
{
    assert(size == sizeof(((vdev_phys_t *)0)->vp_nvlist) && !flags);
    *output = NULL;
    if (mode == 8)
        return EINVAL;
    *output = malloc(sizeof(**output));
    assert(*output);
    **output = (nvlist_t){0, bytes[0]};
    ++decoded;
    ++live;
    return 0;
}
static void nvlist_free(nvlist_t *list)
{
    if (list) {
        assert(!list->role);
        --live;
        ++freed;
        free(list);
    }
}
static int nvlist_lookup_uint64(nvlist_t *list, int key, uint64_t *output)
{
    if (mode == 23 && key == ZPOOL_CONFIG_POOL_GUID)
        return ENOENT;
    if (mode == 31 && key == ZPOOL_CONFIG_IS_LOG)
        return EINVAL;
    switch (key) {
    case ZPOOL_CONFIG_GUID:
        *output = mode == 10                      ? 0
                  : mode == 9 && list->index == 3 ? 22
                  : mode == 24 && list->role      ? 33
                                                  : 11;
        break;
    case ZPOOL_CONFIG_POOL_GUID:
        *output = mode == 25 ? 0 : 77;
        break;
    case ZPOOL_CONFIG_TOP_GUID:
        *output = mode == 17 ? 22 : 11;
        break;
    case ZPOOL_CONFIG_POOL_STATE:
        if (mode == 34)
            return ENOENT;
#ifdef AETHER_POOL_ACTIVE_LABELS
        *output = mode == 11   ? 1
                  : mode == 27 ? 5
                  : mode == 28 ? 4
                  : mode == 33 ? 2
                               : 0;
#else
        *output = mode == 11   ? 0
                  : mode == 27 ? 5
                  : mode == 28 ? 4
                  : mode == 33 ? 2
                               : 1;
#endif
        break;
    case ZPOOL_CONFIG_VERSION:
        *output = mode == 12 ? 28 : 5000;
        break;
    case ZPOOL_CONFIG_POOL_TXG:
        *output = mode == 26 ? 0 : 7;
        break;
    case ZPOOL_CONFIG_VDEV_CHILDREN:
        *output = mode == 32 ? 2 : 1;
        break;
    case ZPOOL_CONFIG_ID:
        *output = mode == 15 ? 1 : 0;
        break;
    case ZPOOL_CONFIG_ASHIFT:
        *output = mode == 16 ? 12 : 9;
        break;
    case ZPOOL_CONFIG_IS_LOG:
        *output = mode == 30;
        break;
    default:
        return ENOENT;
    }
    return 0;
}
static int nvlist_lookup_string(nvlist_t *list, int key, const char **output)
{
    (void)list;
    switch (key) {
    case ZPOOL_CONFIG_POOL_NAME:
        *output = mode == 13 ? "foreign" : "aether_pool_probe";
        break;
    case ZPOOL_CONFIG_TYPE:
        *output = mode == 29 ? "disk" : "file";
        break;
    case ZPOOL_CONFIG_PATH:
        *output = mode == 14 ? "/host/device" : "/aether-volume/poc0";
        break;
    default:
        return ENOENT;
    }
    return 0;
}
static int nvlist_lookup_nvlist(nvlist_t *list, int key, nvlist_t **output)
{
    (void)list;
    if (key == ZPOOL_CONFIG_VDEV_TREE)
        *output = &leaf;
    else if (key == ZPOOL_CONFIG_FEATURES_FOR_READ && mode != 19)
        *output = &features;
    else
        return ENOENT;
    return 0;
}
static void *nvlist_next_nvpair(nvlist_t *list, void *pair)
{
    assert(list == &features && !pair);
    return mode == 18 ? &features : NULL;
}
static int nvlist_exists(nvlist_t *list, int key)
{
    (void)list;
    return (mode == 20 && key == ZPOOL_CONFIG_IS_SPARE) ||
           (mode == 21 && key == ZPOOL_CONFIG_CHILDREN) ||
           (mode == 22 && key == ZPOOL_CONFIG_HOLE_ARRAY);
}
static int zfs_file_open(const char *path, int flags, int permissions,
                         void *cred, zfs_file_t **output)
{
    assert(!strcmp(path, "/aether-volume/poc0") && flags == O_RDONLY &&
           !permissions && !cred);
    *output = NULL;
    if (mode == 1)
        return EACCES;
    *output = &file;
    ++opened;
    return 0;
}
static void zfs_file_close(zfs_file_t *ptr)
{
    assert(ptr == &file);
    ++closed;
}
static int zfs_file_getattr(zfs_file_t *ptr, zfs_file_attr_t *attr)
{
    assert(ptr == &file);
    if (mode == 2)
        return EACCES;
    attr->zfa_size = mode == 3 ? 524288 : mode == 4 ? 67108864 + 512 : 67108864;
    return 0;
}
static int zfs_file_pread(zfs_file_t *ptr, void *buf, size_t size, off_t offset,
                          ssize_t *resid)
{
    static const off_t offsets[] = {16384, 278528, 66600960, 66863104};
    assert(ptr == &file && size == (112 << 10) && reads < 4);
    assert(offset == offsets[reads]);
    memset(buf, 0, size);
    ((char *)buf)[0] = reads++;
    *resid = 0;
    if (mode == 6 && reads == 2)
        return EPERM;
    if (mode == 7 && reads == 2)
        *resid = 512;
    return 0;
}

#include "pool-label.c"

static int exercise(int selected)
{
    mode = selected;
    reads = opened = closed = allocations = freed = decoded = live = 0;
    nvlist_t *output = (void *)(uintptr_t)1;
    int error = aether_pool_label_read(&output);
    int expected = selected == 0                      ? 0
                   : selected == 1 || selected == 2   ? EACCES
                   : selected == 5                    ? ENOMEM
                   : selected == 6                    ? EPERM
                   : selected >= 18 && selected <= 22 ? ENOTSUP
                   : selected == 30 || selected == 31 ? ENOTSUP
                   : (selected >= 7 && selected <= 10) || selected == 26 ||
                           selected == 27 || selected == 34
                       ? EIO
                       : EINVAL;
    if (error != expected) {
        fprintf(stderr, "label oracle: mode%d expected%d observed%d\n",
                selected, expected, error);
        return 90;
    }
    assert((error == 0) == (output != NULL));
    assert(opened == closed && allocations == 0);
    assert(reads == (selected >= 1 && selected <= 5 ? 0 : 4));
    nvlist_free(output);
    assert(live == 0 && freed == decoded);
    return 0;
}
int main(int argc, char **argv)
{
    assert(argc == 2);
    assert(aether_pool_label_read(NULL) == EINVAL);
    int result = exercise(atoi(argv[1]));
    return result ? result : exercise(0);
}
