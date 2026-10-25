/* SPDX-License-Identifier: BSD-2-Clause */
/* Private label intake; ACTIVE selection requires stopped-VM interruption.
 * Valid in-process output borrow. Grant stays live through synchronous reads;
 * Call after kernel_init and volume publication. Caller owns the successful
 * nvlist. This is label data, NOT an import config.
 */
#include <sys/zfs_context.h>
#include <sys/vdev_impl.h>
#include <sys/zfs_file.h>
#include "volume.h"

/* Default clean-export intake remains separate from future stopped-VM
 * interruption recovery. This selector is not authority or a force flag. */
#ifndef AETHER_POOL_ACTIVE_LABELS
#define AETHER_POOL_LABEL_STATE POOL_STATE_EXPORTED
#elif AETHER_POOL_ACTIVE_LABELS == 1
#define AETHER_POOL_LABEL_STATE POOL_STATE_ACTIVE
#else
#error "AETHER_POOL_ACTIVE_LABELS must be 1 when selected"
#endif

_Static_assert(VDEV_LABELS == 4 && sizeof(vdev_label_t) == 262144 &&
                   sizeof(vdev_phys_t) == 114688 && VDEV_SKIP_SIZE == 16384,
               "pinned single-volume label geometry");

struct aether_label_reader {
    zfs_file_t *file;
    int error;
};
struct aether_label_size {
    uint64_t st_size;
};

static int aether_label_stat(struct aether_label_reader *reader,
                             struct aether_label_size *statbuf)
{
    zfs_file_attr_t attr;
    int error = zfs_file_getattr(reader->file, &attr);
#ifdef AETHER_POOL_NAMESPACE
    if (!error && attr.zfa_size != UINT64_C(1073741824))
#else
    if (!error && attr.zfa_size != UINT64_C(67108864))
#endif
        error = EINVAL;
    if (error) {
        reader->error = error;
        return -1;
    }
    statbuf->st_size = attr.zfa_size;
    return 0;
}

static ssize_t aether_label_pread(struct aether_label_reader *reader, void *buf,
                                  size_t length, off_t offset)
{
    ssize_t resid = length;
    int error = zfs_file_pread(reader->file, buf, length, offset, &resid);
    if (!error && resid)
        error = EIO;
    if (error) {
        if (!reader->error)
            reader->error = error;
        return -1;
    }
    return length;
}

/* Only the two I/O bindings, descriptor and size record types differ from the
 * pinned bodies. No host descriptor, stat structure or libc I/O is used. */
#include "pool-label-original.inc"

#ifdef AETHER_POOL_NAMESPACE
#include "namespace-label.inc"
#else
static int aether_label_validate(nvlist_t *label)
{
    uint64_t guid, pool, top, state, version, txg, children, id, ashift,
        leaf_guid;
    const char *name, *type, *path;
    nvlist_t *leaf, *features;
    if (nvlist_lookup_uint64(label, ZPOOL_CONFIG_GUID, &guid) || !guid ||
        nvlist_lookup_uint64(label, ZPOOL_CONFIG_POOL_GUID, &pool) || !pool ||
        nvlist_lookup_uint64(label, ZPOOL_CONFIG_TOP_GUID, &top) ||
        top != guid ||
        nvlist_lookup_uint64(label, ZPOOL_CONFIG_POOL_STATE, &state) ||
        state != AETHER_POOL_LABEL_STATE ||
        nvlist_lookup_uint64(label, ZPOOL_CONFIG_VERSION, &version) ||
        version != SPA_VERSION_FEATURES ||
        nvlist_lookup_uint64(label, ZPOOL_CONFIG_POOL_TXG, &txg) || !txg ||
        nvlist_lookup_uint64(label, ZPOOL_CONFIG_VDEV_CHILDREN, &children) ||
        children != 1 ||
        nvlist_lookup_string(label, ZPOOL_CONFIG_POOL_NAME, &name) ||
        strcmp(name, "aether_pool_probe") ||
        nvlist_lookup_nvlist(label, ZPOOL_CONFIG_VDEV_TREE, &leaf) ||
        nvlist_lookup_string(leaf, ZPOOL_CONFIG_TYPE, &type) ||
        strcmp(type, VDEV_TYPE_FILE) ||
        nvlist_lookup_string(leaf, ZPOOL_CONFIG_PATH, &path) ||
        strcmp(path, AETHER_VOLUME_PATH) ||
        nvlist_lookup_uint64(leaf, ZPOOL_CONFIG_ID, &id) || id ||
        nvlist_lookup_uint64(leaf, ZPOOL_CONFIG_GUID, &leaf_guid) ||
        leaf_guid != guid ||
        nvlist_lookup_uint64(leaf, ZPOOL_CONFIG_ASHIFT, &ashift) || ashift != 9)
        return EINVAL;
    uint64_t islog;
    if (nvlist_lookup_uint64(leaf, ZPOOL_CONFIG_IS_LOG, &islog) || islog ||
        nvlist_exists(leaf, ZPOOL_CONFIG_IS_SPARE) ||
        nvlist_exists(leaf, ZPOOL_CONFIG_CHILDREN) ||
        nvlist_exists(leaf, ZPOOL_CONFIG_SPARES) ||
        nvlist_exists(leaf, ZPOOL_CONFIG_L2CACHE) ||
        nvlist_exists(label, ZPOOL_CONFIG_HOLE_ARRAY) ||
        nvlist_lookup_nvlist(label, ZPOOL_CONFIG_FEATURES_FOR_READ,
                             &features) ||
        nvlist_next_nvpair(features, NULL))
        return ENOTSUP;
    return 0;
}

/* Build only this experiment's root; raw labels contain policy/path fields that
 * must not flow into spa_import. Original APIs duplicate nested nvlists. */
int aether_pool_label_config(nvlist_t *label, nvlist_t **output)
{
    if (!output)
        return EINVAL;
    *output = NULL;
    if (!label)
        return EINVAL;
    int error = aether_label_validate(label);
    if (error)
        return error;
    nvlist_t *source;
    uint64_t pool, guid, txg, array, shift, asize;
    if (nvlist_lookup_nvlist(label, ZPOOL_CONFIG_VDEV_TREE, &source) ||
        nvlist_lookup_uint64(label, ZPOOL_CONFIG_POOL_GUID, &pool) ||
        nvlist_lookup_uint64(label, ZPOOL_CONFIG_GUID, &guid) ||
        nvlist_lookup_uint64(label, ZPOOL_CONFIG_POOL_TXG, &txg) ||
        nvlist_lookup_uint64(source, ZPOOL_CONFIG_METASLAB_ARRAY, &array) ||
        !array ||
        nvlist_lookup_uint64(source, ZPOOL_CONFIG_METASLAB_SHIFT, &shift) ||
        shift < 20 || shift > 26 ||
        nvlist_lookup_uint64(source, ZPOOL_CONFIG_ASIZE, &asize) || !asize ||
        asize > UINT64_C(67108864) || (asize & 511))
        return EINVAL;
    /* At most64 initial metaslabs from admitted label geometry; original MOS
     * reload must still validate authoritative metadata, not trust this label.
     */
    nvlist_t *config = NULL, *root = NULL, *leaf = NULL, *policy = NULL;
    const nvlist_t *child[1];
#define LABEL_STEP(operation)                                                  \
    do {                                                                       \
        if ((error = (operation)))                                             \
            goto done;                                                         \
    } while (0)
    LABEL_STEP(nvlist_alloc(&config, NV_UNIQUE_NAME, 0));
    LABEL_STEP(nvlist_alloc(&root, NV_UNIQUE_NAME, 0));
    LABEL_STEP(nvlist_alloc(&leaf, NV_UNIQUE_NAME, 0));
    LABEL_STEP(nvlist_alloc(&policy, NV_UNIQUE_NAME, 0));
    LABEL_STEP(nvlist_add_string(leaf, ZPOOL_CONFIG_TYPE, VDEV_TYPE_FILE));
    LABEL_STEP(nvlist_add_string(leaf, ZPOOL_CONFIG_PATH, AETHER_VOLUME_PATH));
    LABEL_STEP(nvlist_add_uint64(leaf, ZPOOL_CONFIG_ID, 0));
    LABEL_STEP(nvlist_add_uint64(leaf, ZPOOL_CONFIG_GUID, guid));
    LABEL_STEP(nvlist_add_uint64(leaf, ZPOOL_CONFIG_ASHIFT, 9));
    LABEL_STEP(nvlist_add_uint64(leaf, ZPOOL_CONFIG_METASLAB_ARRAY, array));
    LABEL_STEP(nvlist_add_uint64(leaf, ZPOOL_CONFIG_METASLAB_SHIFT, shift));
    LABEL_STEP(nvlist_add_uint64(leaf, ZPOOL_CONFIG_ASIZE, asize));
    LABEL_STEP(nvlist_add_string(root, ZPOOL_CONFIG_TYPE, VDEV_TYPE_ROOT));
    LABEL_STEP(nvlist_add_uint64(root, ZPOOL_CONFIG_ID, 0));
    LABEL_STEP(nvlist_add_uint64(root, ZPOOL_CONFIG_GUID, pool));
    child[0] = leaf;
    LABEL_STEP(nvlist_add_nvlist_array(root, ZPOOL_CONFIG_CHILDREN, child, 1));
    LABEL_STEP(
        nvlist_add_string(config, ZPOOL_CONFIG_POOL_NAME, "aether_pool_probe"));
    LABEL_STEP(
        nvlist_add_uint64(config, ZPOOL_CONFIG_VERSION, SPA_VERSION_FEATURES));
    LABEL_STEP(nvlist_add_uint64(config, ZPOOL_CONFIG_POOL_STATE,
                                 AETHER_POOL_LABEL_STATE));
    LABEL_STEP(nvlist_add_uint64(config, ZPOOL_CONFIG_POOL_GUID, pool));
    LABEL_STEP(nvlist_add_uint64(config, ZPOOL_CONFIG_POOL_TXG, txg));
    LABEL_STEP(nvlist_add_uint64(config, ZPOOL_CONFIG_VDEV_CHILDREN, 1));
    LABEL_STEP(nvlist_add_nvlist(config, ZPOOL_CONFIG_VDEV_TREE, root));
    LABEL_STEP(nvlist_add_uint32(policy, ZPOOL_LOAD_REWIND_POLICY,
                                 ZPOOL_NEVER_REWIND));
    LABEL_STEP(nvlist_add_uint64(policy, ZPOOL_LOAD_REQUEST_TXG, UINT64_MAX));
    LABEL_STEP(nvlist_add_nvlist(config, ZPOOL_LOAD_POLICY, policy));
    *output = config;
    config = NULL;
done:
    nvlist_free(policy);
    nvlist_free(leaf);
    nvlist_free(root);
    nvlist_free(config);
#undef LABEL_STEP
    return error;
}

#endif

int aether_pool_label_read(nvlist_t **output)
{
    if (!output)
        return EINVAL;
    *output = NULL;
    struct aether_label_reader reader = {0};
    int error =
        zfs_file_open(AETHER_VOLUME_PATH, O_RDONLY, 0, NULL, &reader.file);
    if (error)
        return error;
    nvlist_t *label = NULL;
    int count = 0;
    int result = zpool_read_label_slow(&reader, &label, &count);
    zfs_file_close(reader.file);
    if (reader.error)
        error = reader.error;
    else if (result)
        error = ENOMEM;
    else if (!label || count != VDEV_LABELS)
        error = EIO;
    else
        error = aether_label_validate(label);
    if (error) {
        nvlist_free(label);
        return error;
    }
    *output = label;
    return 0;
}
