/* SPDX-License-Identifier: BSD-2-Clause */
/* Shared host-only admission for the pinned private regular-file pool copy. */
#ifndef AETHER_ZPL_HOST_FIXTURE_H
#define AETHER_ZPL_HOST_FIXTURE_H

#define EXPECT(condition, name)                                                \
    do {                                                                       \
        if (!(condition)) {                                                    \
            fprintf(stderr, "HOST ZPL NAMESPACE oracle93 %s line%d\n", name,   \
                    __LINE__);                                                 \
            exit(93);                                                          \
        }                                                                      \
    } while (0)
#define REQUIRE(condition) EXPECT(condition, "contract")

#define INPUT "/work/fixture/namespace-pool.img"
#define REFERENCE "/work/reference-zstd.bin"
#define POOL "testpool_zstd"
#define DATASET POOL "/x86_64"

static nvlist_t *fixture_config(void)
{
    int fd = open(INPUT, O_RDONLY | O_CLOEXEC);
    REQUIRE(fd >= 0);
    nvlist_t *label = NULL;
    int labels = 0;
    REQUIRE(!zpool_read_label(fd, &label, &labels));
    REQUIRE(!close(fd));
    REQUIRE(label && labels == 4);
    REQUIRE(
        !strcmp(fnvlist_lookup_string(label, ZPOOL_CONFIG_POOL_NAME), POOL));
    REQUIRE(fnvlist_lookup_uint64(label, ZPOOL_CONFIG_POOL_STATE) ==
            POOL_STATE_EXPORTED);
    REQUIRE(fnvlist_lookup_uint64(label, ZPOOL_CONFIG_POOL_GUID) ==
            UINT64_C(4253333510760776491));
    nvlist_t *source = fnvlist_lookup_nvlist(label, ZPOOL_CONFIG_VDEV_TREE);
    REQUIRE(!strcmp(fnvlist_lookup_string(source, ZPOOL_CONFIG_TYPE),
                    VDEV_TYPE_FILE));
    REQUIRE(!nvlist_exists(source, ZPOOL_CONFIG_CHILDREN));
    REQUIRE(fnvlist_lookup_uint64(source, ZPOOL_CONFIG_ID) == 0);
    REQUIRE(fnvlist_lookup_uint64(source, ZPOOL_CONFIG_GUID) ==
            UINT64_C(7901585125367293011));
    REQUIRE(fnvlist_lookup_uint64(source, ZPOOL_CONFIG_ASHIFT) == 9);
    REQUIRE(fnvlist_lookup_uint64(source, ZPOOL_CONFIG_IS_LOG) == 0);
    /* Reconstruct the sole admitted leaf; never use the on-disk host pathname.
     */
    nvlist_t *leaf = fnvlist_alloc(), *root = fnvlist_alloc();
    fnvlist_add_string(leaf, ZPOOL_CONFIG_TYPE, VDEV_TYPE_FILE);
    fnvlist_add_string(leaf, ZPOOL_CONFIG_PATH, INPUT);
    fnvlist_add_uint64(leaf, ZPOOL_CONFIG_ID, 0);
    fnvlist_add_uint64(leaf, ZPOOL_CONFIG_GUID, UINT64_C(7901585125367293011));
    fnvlist_add_uint64(leaf, ZPOOL_CONFIG_ASHIFT, 9);
    fnvlist_add_uint64(
        leaf, ZPOOL_CONFIG_METASLAB_ARRAY,
        fnvlist_lookup_uint64(source, ZPOOL_CONFIG_METASLAB_ARRAY));
    fnvlist_add_uint64(
        leaf, ZPOOL_CONFIG_METASLAB_SHIFT,
        fnvlist_lookup_uint64(source, ZPOOL_CONFIG_METASLAB_SHIFT));
    fnvlist_add_uint64(leaf, ZPOOL_CONFIG_ASIZE,
                       fnvlist_lookup_uint64(source, ZPOOL_CONFIG_ASIZE));
    fnvlist_add_string(root, ZPOOL_CONFIG_TYPE, VDEV_TYPE_ROOT);
    fnvlist_add_uint64(root, ZPOOL_CONFIG_ID, 0);
    fnvlist_add_uint64(root, ZPOOL_CONFIG_GUID, UINT64_C(4253333510760776491));
    const nvlist_t *children[] = {leaf};
    fnvlist_add_nvlist_array(root, ZPOOL_CONFIG_CHILDREN, children, 1);
    nvlist_t *config = fnvlist_alloc(), *policy = fnvlist_alloc();
    fnvlist_add_string(config, ZPOOL_CONFIG_POOL_NAME, POOL);
    fnvlist_add_uint64(config, ZPOOL_CONFIG_POOL_GUID,
                       UINT64_C(4253333510760776491));
    fnvlist_add_uint64(config, ZPOOL_CONFIG_POOL_STATE, POOL_STATE_EXPORTED);
    fnvlist_add_uint64(config, ZPOOL_CONFIG_VERSION, SPA_VERSION_FEATURES);
    fnvlist_add_uint64(config, ZPOOL_CONFIG_POOL_TXG,
                       fnvlist_lookup_uint64(label, ZPOOL_CONFIG_POOL_TXG));
    fnvlist_add_uint64(config, ZPOOL_CONFIG_VDEV_CHILDREN, 1);
    fnvlist_add_nvlist(config, ZPOOL_CONFIG_VDEV_TREE, root);
    fnvlist_add_uint32(policy, ZPOOL_LOAD_REWIND_POLICY, ZPOOL_NEVER_REWIND);
    fnvlist_add_uint64(policy, ZPOOL_LOAD_REQUEST_TXG, UINT64_MAX);
    fnvlist_add_nvlist(config, ZPOOL_LOAD_POLICY, policy);
    nvlist_free(policy);
    nvlist_free(root);
    nvlist_free(leaf);
    nvlist_free(label);
    return config;
}

#endif
