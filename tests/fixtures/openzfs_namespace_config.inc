/* SPDX-License-Identifier: BSD-2-Clause */
/* Appended to the existing typed/deep-copy nvlist scaffold by the host test. */
#define CHECK(c)                                                               \
    do {                                                                       \
        if (!(c)) {                                                            \
            fprintf(stderr, "HOST NAMESPACE LABEL oracle95 line%d\n",          \
                    __LINE__);                                                 \
            exit(95);                                                          \
        }                                                                      \
    } while (0)
static nvlist_t *namespace_input(int mode)
{
    nvlist_t *label, *leaf, *features;
    CHECK(!nvlist_alloc(&label, NV_UNIQUE_NAME, 0));
    CHECK(!nvlist_alloc(&leaf, NV_UNIQUE_NAME, 0));
    CHECK(!nvlist_alloc(&features, NV_UNIQUE_NAME, 0));
    int keys[] = {ZPOOL_CONFIG_GUID,         ZPOOL_CONFIG_POOL_GUID,
                  ZPOOL_CONFIG_TOP_GUID,     ZPOOL_CONFIG_POOL_STATE,
                  ZPOOL_CONFIG_VERSION,      ZPOOL_CONFIG_POOL_TXG,
                  ZPOOL_CONFIG_VDEV_CHILDREN};
    uint64_t values[] = {UINT64_C(7901585125367293011),
                         UINT64_C(4253333510760776491),
                         UINT64_C(7901585125367293011),
                         1,
                         5000,
                         782,
                         1};
    if (mode >= 2 && mode <= 8)
        values[mode - 2]++;
    for (unsigned i = 0; i < 7; ++i)
        CHECK(!nvlist_add_uint64(label, keys[i], values[i]));
    CHECK(!nvlist_add_string(label, ZPOOL_CONFIG_POOL_NAME,
                             mode == 9 ? "foreign" : "testpool_zstd"));
    CHECK(!nvlist_add_string(leaf, ZPOOL_CONFIG_TYPE, VDEV_TYPE_FILE));
    CHECK(!nvlist_add_string(leaf, ZPOOL_CONFIG_PATH, "/host/ignored"));
    int leaf_keys[] = {ZPOOL_CONFIG_ID,
                       ZPOOL_CONFIG_GUID,
                       ZPOOL_CONFIG_ASHIFT,
                       ZPOOL_CONFIG_IS_LOG,
                       ZPOOL_CONFIG_METASLAB_ARRAY,
                       ZPOOL_CONFIG_METASLAB_SHIFT,
                       ZPOOL_CONFIG_ASIZE};
    uint64_t leaf_values[] = {
        0, UINT64_C(7901585125367293011), 9, 0, 60, 26, 1069023232};
    if (mode >= 16 && mode <= 22)
        leaf_values[mode - 16]++;
    if (mode == 22)
        leaf_values[6] += 511;
    for (unsigned i = 0; i < 7; ++i)
        CHECK(!nvlist_add_uint64(leaf, leaf_keys[i], leaf_values[i]));
    CHECK(!add(features, (nvpair_t){.key = POISON + 1,
                                    .type = mode == 11 ? 2 : DATA_TYPE_BOOLEAN,
                                    .string = "com.delphix:hole_birth"}));
    if (mode != 10)
        CHECK(!add(features,
                   (nvpair_t){.key = POISON + 2,
                              .type = DATA_TYPE_BOOLEAN,
                              .string = mode == 12 ? "unknown"
                                        : mode == 13
                                            ? "com.delphix:hole_birth"
                                            : "com.delphix:embedded_data"}));
    if (mode == 14)
        CHECK(!add(features, (nvpair_t){.key = POISON + 3,
                                        .type = DATA_TYPE_BOOLEAN,
                                        .string = "unknown"}));
    if (mode == 15)
        CHECK(!nvlist_add_uint64(leaf, ZPOOL_CONFIG_IS_SPARE, 0));
    if (mode == 1)
        CHECK(!nvlist_add_string(label, POISON, "/host/policy"));
    CHECK(!nvlist_add_nvlist(label, ZPOOL_CONFIG_VDEV_TREE, leaf));
    CHECK(!nvlist_add_nvlist(label, ZPOOL_CONFIG_FEATURES_FOR_READ, features));
    nvlist_free(leaf);
    nvlist_free(features);
    return label;
}
static unsigned namespace_run(int mode, unsigned fail, int injected)
{
    steps = fail_at = 0;
    nvlist_t *label = namespace_input(mode), *config = (void *)(uintptr_t)1;
    unsigned before = live;
    steps = 0;
    fail_at = fail;
    failure = injected;
    int error = aether_pool_label_config(label, &config);
    unsigned total = steps;
    int expected = mode >= 10 && mode <= 15 ? ENOTSUP
                   : mode >= 2              ? EINVAL
                   : fail                   ? injected
                                            : 0;
    CHECK(error == expected && (!error) == (config != NULL));
    if (!error) {
        CHECK(config->count == 8 && !pair(config, POISON));
        nvlist_t *root = pair(config, ZPOOL_CONFIG_VDEV_TREE)->nested;
        nvlist_t *leaf = pair(root, ZPOOL_CONFIG_CHILDREN)->nested;
        nvlist_t *policy = pair(config, ZPOOL_LOAD_POLICY)->nested;
        CHECK(leaf->count == 8 && !strcmp(pair(leaf, ZPOOL_CONFIG_PATH)->string,
                                          AETHER_VOLUME_PATH));
        CHECK(pair(root, ZPOOL_CONFIG_GUID)->number ==
              UINT64_C(4253333510760776491));
        CHECK(pair(leaf, ZPOOL_CONFIG_GUID)->number ==
              UINT64_C(7901585125367293011));
        CHECK(pair(policy, ZPOOL_LOAD_REWIND_POLICY)->type == 3 &&
              pair(policy, ZPOOL_LOAD_REWIND_POLICY)->number ==
                  ZPOOL_NEVER_REWIND);
        CHECK(pair(policy, ZPOOL_LOAD_REQUEST_TXG)->number == UINT64_MAX);
        nvlist_free(config);
    }
    CHECK(live == before);
    nvlist_free(label);
    CHECK(!live);
    return total;
}
int main(int argc, char **argv)
{
    CHECK(argc == 2);
    if (!strcmp(argv[1], "failures")) {
        unsigned n = namespace_run(0, 0, 0);
        for (unsigned i = 1; i <= n; ++i) {
            namespace_run(0, i, ENOMEM);
            namespace_run(0, i, EIO);
        }
    } else
        namespace_run(atoi(argv[1]), 0, 0);
    return 0;
}
