/* SPDX-License-Identifier: BSD-2-Clause */
/* Fixed pinned fixture only. Never inherit the on-disk host path or policy. */
static int aether_label_validate(nvlist_t *label)
{
    uint64_t guid, pool, top, state, version, txg, children, id, ashift,
        leaf_guid, islog;
    const char *name, *type;
    nvlist_t *leaf, *features;
    if (nvlist_lookup_uint64(label, ZPOOL_CONFIG_GUID, &guid) ||
        guid != UINT64_C(7901585125367293011) ||
        nvlist_lookup_uint64(label, ZPOOL_CONFIG_POOL_GUID, &pool) ||
        pool != UINT64_C(4253333510760776491) ||
        nvlist_lookup_uint64(label, ZPOOL_CONFIG_TOP_GUID, &top) ||
        top != guid ||
        nvlist_lookup_uint64(label, ZPOOL_CONFIG_POOL_STATE, &state) ||
        state != POOL_STATE_EXPORTED ||
        nvlist_lookup_uint64(label, ZPOOL_CONFIG_VERSION, &version) ||
        version != SPA_VERSION_FEATURES ||
        nvlist_lookup_uint64(label, ZPOOL_CONFIG_POOL_TXG, &txg) ||
        txg != 782 ||
        nvlist_lookup_uint64(label, ZPOOL_CONFIG_VDEV_CHILDREN, &children) ||
        children != 1 ||
        nvlist_lookup_string(label, ZPOOL_CONFIG_POOL_NAME, &name) ||
        strcmp(name, "testpool_zstd") ||
        nvlist_lookup_nvlist(label, ZPOOL_CONFIG_VDEV_TREE, &leaf) ||
        nvlist_lookup_string(leaf, ZPOOL_CONFIG_TYPE, &type) ||
        strcmp(type, VDEV_TYPE_FILE) ||
        nvlist_lookup_uint64(leaf, ZPOOL_CONFIG_ID, &id) || id ||
        nvlist_lookup_uint64(leaf, ZPOOL_CONFIG_GUID, &leaf_guid) ||
        leaf_guid != guid ||
        nvlist_lookup_uint64(leaf, ZPOOL_CONFIG_ASHIFT, &ashift) ||
        ashift != 9 ||
        nvlist_lookup_uint64(leaf, ZPOOL_CONFIG_IS_LOG, &islog) || islog)
        return EINVAL;
    if (nvlist_exists(leaf, ZPOOL_CONFIG_IS_SPARE) ||
        nvlist_exists(leaf, ZPOOL_CONFIG_CHILDREN) ||
        nvlist_exists(leaf, ZPOOL_CONFIG_SPARES) ||
        nvlist_exists(leaf, ZPOOL_CONFIG_L2CACHE) ||
        nvlist_exists(label, ZPOOL_CONFIG_HOLE_ARRAY) ||
        nvlist_lookup_nvlist(label, ZPOOL_CONFIG_FEATURES_FOR_READ, &features))
        return ENOTSUP;
    unsigned bits = 0, count = 0;
    for (nvpair_t *item = nvlist_next_nvpair(features, NULL); item;
         item = nvlist_next_nvpair(features, item)) {
        if (nvpair_type(item) != DATA_TYPE_BOOLEAN)
            return ENOTSUP;
        const char *feature = nvpair_name(item);
        if (!strcmp(feature, "com.delphix:hole_birth"))
            bits |= 1;
        else if (!strcmp(feature, "com.delphix:embedded_data"))
            bits |= 2;
        else
            return ENOTSUP;
        ++count;
    }
    return bits == 3 && count == 2 ? 0 : ENOTSUP;
}

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
        array != 60 ||
        nvlist_lookup_uint64(source, ZPOOL_CONFIG_METASLAB_SHIFT, &shift) ||
        shift != 26 ||
        nvlist_lookup_uint64(source, ZPOOL_CONFIG_ASIZE, &asize) || !asize ||
        asize != UINT64_C(1069023232) || (asize & 511))
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
        nvlist_add_string(config, ZPOOL_CONFIG_POOL_NAME, "testpool_zstd"));
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
