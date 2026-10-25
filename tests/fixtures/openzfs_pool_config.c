/* SPDX-License-Identifier: BSD-2-Clause */
/* Actual config builder/validator; synthetic typed deep-copy nvlist API only.
 */
#include <assert.h>
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define SPA_VERSION_FEATURES 5000
#define POOL_STATE_ACTIVE 0
#define POOL_STATE_EXPORTED 1
#define VDEV_TYPE_FILE "file"
#define VDEV_TYPE_ROOT "root"
#define AETHER_VOLUME_PATH "/aether-volume/poc0"
#define NV_UNIQUE_NAME 1
#define ZPOOL_NEVER_REWIND 2
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
    ZPOOL_CONFIG_FEATURES_FOR_READ,
    ZPOOL_CONFIG_METASLAB_ARRAY,
    ZPOOL_CONFIG_METASLAB_SHIFT,
    ZPOOL_CONFIG_ASIZE,
    ZPOOL_LOAD_POLICY,
    ZPOOL_LOAD_REWIND_POLICY,
    ZPOOL_LOAD_REQUEST_TXG,
    POISON
};
typedef struct nvlist nvlist_t;
typedef struct {
    int key, type;
    uint64_t number;
    const char *string;
    nvlist_t *nested;
} nvpair_t;
struct nvlist {
    unsigned count;
    nvpair_t pairs[24];
};
static unsigned live, steps, fail_at;
static int failure;
static int step(void) { return ++steps == fail_at ? failure : 0; }
static int nvlist_alloc(nvlist_t **out, int flags, int sleep)
{
    assert(flags == NV_UNIQUE_NAME && !sleep);
    *out = NULL;
    int error = step();
    if (error)
        return error;
    *out = calloc(1, sizeof(**out));
    assert(*out);
    ++live;
    return 0;
}
static void nvlist_free(nvlist_t *list)
{
    if (!list)
        return;
    for (unsigned i = 0; i < list->count; ++i)
        nvlist_free(list->pairs[i].nested);
    assert(live);
    --live;
    free(list);
}
static nvpair_t *pair(nvlist_t *list, int key)
{
    for (unsigned i = 0; i < list->count; ++i)
        if (list->pairs[i].key == key)
            return &list->pairs[i];
    return NULL;
}
static int add(nvlist_t *list, nvpair_t value)
{
    int error = step();
    if (error)
        return error;
    assert(list->count < 24 && !pair(list, value.key));
    list->pairs[list->count++] = value;
    return 0;
}
static int nvlist_add_string(nvlist_t *list, int key, const char *string)
{
    return add(list, (nvpair_t){.key = key, .type = 1, .string = string});
}
static int nvlist_add_uint64(nvlist_t *list, int key, uint64_t value)
{
    return add(list, (nvpair_t){.key = key, .type = 2, .number = value});
}
static int nvlist_add_uint32(nvlist_t *list, int key, uint32_t value)
{
    return add(list, (nvpair_t){.key = key, .type = 3, .number = value});
}
static int duplicate(const nvlist_t *source, nvlist_t **out)
{
    int error = nvlist_alloc(out, NV_UNIQUE_NAME, 0);
    if (error)
        return error;
    for (unsigned i = 0; i < source->count; ++i) {
        nvpair_t value = source->pairs[i];
        value.nested = NULL;
        if (source->pairs[i].nested)
            error = duplicate(source->pairs[i].nested, &value.nested);
        if (!error)
            error = add(*out, value);
        if (error) {
            nvlist_free(value.nested);
            nvlist_free(*out);
            *out = NULL;
            return error;
        }
    }
    return 0;
}
static int nvlist_add_nvlist(nvlist_t *list, int key, const nvlist_t *nested)
{
    nvpair_t value = {.key = key, .type = 4};
    int error = duplicate(nested, &value.nested);
    if (!error)
        error = add(list, value);
    if (error)
        nvlist_free(value.nested);
    return error;
}
static int nvlist_add_nvlist_array(nvlist_t *list, int key,
                                   const nvlist_t **child, unsigned count)
{
    assert(count == 1);
    int error = nvlist_add_nvlist(list, key, child[0]);
    if (!error)
        pair(list, key)->type = 5;
    return error;
}
static int nvlist_lookup_uint64(nvlist_t *list, int key, uint64_t *out)
{
    nvpair_t *p = pair(list, key);
    if (!p || p->type != 2)
        return EINVAL;
    *out = p->number;
    return 0;
}
static int nvlist_lookup_string(nvlist_t *list, int key, const char **out)
{
    nvpair_t *p = pair(list, key);
    if (!p || p->type != 1)
        return EINVAL;
    *out = p->string;
    return 0;
}
static int nvlist_lookup_nvlist(nvlist_t *list, int key, nvlist_t **out)
{
    nvpair_t *p = pair(list, key);
    if (!p || p->type != 4)
        return EINVAL;
    *out = p->nested;
    return 0;
}
static int nvlist_exists(nvlist_t *list, int key)
{
    return pair(list, key) != NULL;
}
static nvpair_t *nvlist_next_nvpair(nvlist_t *list, nvpair_t *old)
{
    assert(!old);
    return list->count ? &list->pairs[0] : NULL;
}
#include "pool-config-bodies.inc"

static nvlist_t *input(int mode)
{
    nvlist_t *label, *leaf, *features;
    assert(!nvlist_alloc(&label, NV_UNIQUE_NAME, 0));
    assert(!nvlist_alloc(&leaf, NV_UNIQUE_NAME, 0));
    assert(!nvlist_alloc(&features, NV_UNIQUE_NAME, 0));
    int label_keys[] = {ZPOOL_CONFIG_GUID,         ZPOOL_CONFIG_POOL_GUID,
                        ZPOOL_CONFIG_TOP_GUID,     ZPOOL_CONFIG_POOL_STATE,
                        ZPOOL_CONFIG_VERSION,      ZPOOL_CONFIG_POOL_TXG,
                        ZPOOL_CONFIG_VDEV_CHILDREN};
#ifdef AETHER_POOL_ACTIVE_LABELS
    uint64_t expected_state = 0;
#else
    uint64_t expected_state = 1;
#endif
    uint64_t label_values[] = {11, 77, 11, expected_state, 5000, 7, 1};
    if (mode == 12)
        label_values[3] = expected_state == 0 ? 1 : 0;
    if (mode >= 13 && mode <= 16)
        label_values[3] = mode - 11;
    if (mode == 17)
        label_values[3] = UINT64_MAX;
    for (unsigned i = 0; i < 7; ++i)
        assert(!nvlist_add_uint64(label, label_keys[i], label_values[i]));
    assert(
        !nvlist_add_string(label, ZPOOL_CONFIG_POOL_NAME, "aether_pool_probe"));
    assert(!nvlist_add_string(leaf, ZPOOL_CONFIG_TYPE, VDEV_TYPE_FILE));
    assert(!nvlist_add_string(leaf, ZPOOL_CONFIG_PATH, AETHER_VOLUME_PATH));
    int keys[] = {ZPOOL_CONFIG_ID,
                  ZPOOL_CONFIG_GUID,
                  ZPOOL_CONFIG_ASHIFT,
                  ZPOOL_CONFIG_IS_LOG,
                  ZPOOL_CONFIG_METASLAB_ARRAY,
                  ZPOOL_CONFIG_METASLAB_SHIFT,
                  ZPOOL_CONFIG_ASIZE};
    uint64_t values[] = {0, 11, 9, 0, 42, 22, 66060288};
    if (mode == 4)
        values[5] = 19;
    if (mode == 5)
        values[5] = 27;
    if (mode == 6)
        values[6] = 67108864 + 512;
    if (mode == 7)
        values[6]++;
    if (mode == 8)
        values[4] = 0;
    if (mode == 9)
        values[6] = 0;
    for (unsigned i = 0; i < 7; ++i)
        if (!(mode == 3 && i == 4))
            assert(!nvlist_add_uint64(leaf, keys[i], values[i]));
    if (mode == 10)
        pair(label, ZPOOL_CONFIG_POOL_GUID)->type = 1;
    if (mode == 11)
        assert(!nvlist_add_string(features, POISON, "unsupported"));
    if (mode == 1)
        assert(!nvlist_add_nvlist(label, ZPOOL_LOAD_POLICY, leaf));
    if (mode == 2) {
        assert(!nvlist_add_string(label, POISON, "/host/cache"));
        assert(!nvlist_add_string(leaf, POISON, "/host/device"));
    }
    assert(!nvlist_add_nvlist(label, ZPOOL_CONFIG_VDEV_TREE, leaf));
    assert(!nvlist_add_nvlist(label, ZPOOL_CONFIG_FEATURES_FOR_READ, features));
    nvlist_free(leaf);
    nvlist_free(features);
    return label;
}
static int run(int mode, unsigned fail, int fault)
{
    fail_at = 0;
    steps = 0;
    assert(!live);
    nvlist_t *label = input(mode), *config = (void *)(uintptr_t)1;
    unsigned input_live = live;
    steps = 0;
    fail_at = fail;
    failure = fault;
    int error = aether_pool_label_config(label, &config);
    unsigned total = steps;
    int expected = mode >= 3 ? (mode == 11 ? ENOTSUP : EINVAL)
                   : fail    ? fault
                             : 0;
    if (error != expected) {
        fprintf(stderr, "config oracle: mode%d fail%u expected%d observed%d\n",
                mode, fail, expected, error);
        exit(90);
    }
    assert((error == 0) == (config != NULL));
    if (!error) {
        assert(config->count == 8);
        uint64_t observed_state = pair(config, ZPOOL_CONFIG_POOL_STATE)->number;
#ifdef AETHER_POOL_ACTIVE_LABELS
        uint64_t expected_state = 0;
#else
        uint64_t expected_state = 1;
#endif
        if (observed_state != expected_state) {
            fputs("config oracle: selected pool state must be preserved92\n",
                  stderr);
            exit(92);
        }
        nvlist_t *root = pair(config, ZPOOL_CONFIG_VDEV_TREE)->nested;
        nvlist_t *leaf = pair(root, ZPOOL_CONFIG_CHILDREN)->nested;
        nvlist_t *policy = pair(config, ZPOOL_LOAD_POLICY)->nested;
        assert(root->count == 4 && leaf->count == 8 && policy->count == 2);
        assert(pair(root, ZPOOL_CONFIG_GUID)->number == 77);
        assert(pair(leaf, ZPOOL_CONFIG_GUID)->number == 11);
        assert(
            !strcmp(pair(leaf, ZPOOL_CONFIG_PATH)->string, AETHER_VOLUME_PATH));
        nvpair_t *rewind = pair(policy, ZPOOL_LOAD_REWIND_POLICY);
        if (rewind->type != 3 || rewind->number != ZPOOL_NEVER_REWIND) {
            fprintf(stderr,
                    "config oracle: policy must be uint32 NEVER_REWIND\n");
            exit(91);
        }
        assert(pair(policy, ZPOOL_LOAD_REQUEST_TXG)->number == UINT64_MAX);
        assert(!pair(config, POISON) && !pair(leaf, POISON));
        nvlist_free(config);
    }
    assert(live == input_live);
    nvlist_free(label);
    assert(!live);
    return total;
}
int main(int argc, char **argv)
{
    assert(argc == 2);
    nvlist_t *output = (void *)(uintptr_t)1;
    assert(aether_pool_label_config(NULL, NULL) == EINVAL);
    assert(aether_pool_label_config(NULL, &output) == EINVAL && !output);
    if (!strcmp(argv[1], "failures")) {
        unsigned total = run(0, 0, 0);
        for (unsigned n = 1; n <= total; ++n) {
            run(0, n, ENOMEM);
            run(0, n, EIO);
        }
        return 0;
    }
    run(atoi(argv[1]), 0, 0);
    return 0;
}
