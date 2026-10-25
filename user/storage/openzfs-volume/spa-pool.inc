/* SPDX-License-Identifier: BSD-2-Clause */
/* Private creation/resource checkpoint appended to original spa.c.
 * Original API/config locks own all lifetimes. The opt-in data profile adds
 * one private assigned record and ordered witness; no filesystem is exposed. */
#include "pool-witness.h"
#ifdef AETHER_POOL_DATA
#include "pool-flow-witness.h"
#endif
#include "volume.h"
#include <sys/auxv.h>
#include <sys/vdev_impl.h>
#include <sys/zfeature.h>
#include <sys/zfs_file.h>
extern void aether_engine_utc_phase(unsigned char);
extern int aether_pool_hooks_prepare(struct aether_pool_witness *);
extern unsigned aether_pool_hooks_check(uint64_t);
static struct aether_pool_witness aether_creation_witness;
_Static_assert(SPA_VERSION == 5000 && SPA_VERSION_FEATURES == 5000,
               "creation defaults must remain the pinned feature format");
_Static_assert(sizeof(int) == sizeof(uint32_t), "errno diagnostic width");

int aether_pool_prepare(void) {
  return aether_pool_hooks_prepare(&aether_creation_witness);
}

static int aether_pool_config_hash(nvlist_t *input, uint64_t *hash) {
  char *bytes = NULL;
  size_t length = 0;
  int error = nvlist_pack(input, &bytes, &length, NV_ENCODE_XDR, KM_SLEEP);
  if (error)
    return error;
  if (!length || length > 4096) {
    free(bytes);
    return EOVERFLOW;
  }
  /* Length frame separates root/property payloads. This diagnostic fingerprint
   * conveys no authority; complete source/tool/artifact identities use SHA256.
   */
  for (unsigned i = 0; i < 8; ++i) {
    *hash ^= (length >> (8 * i)) & 255;
    *hash *= UINT64_C(1099511628211);
  }
  for (size_t i = 0; i < length; ++i) {
    *hash ^= (unsigned char)bytes[i];
    *hash *= UINT64_C(1099511628211);
  }
  free(bytes);
  return 0;
}

int aether_spa_pool_probe(void) {
  if (getauxval(0xa001) != 0x50000101UL) {
    zfs_file_t *file = NULL;
    if (zfs_file_open(AETHER_VOLUME_PATH, O_RDONLY, 0, NULL, &file) != ENODEV ||
        file)
      return 872;
    aether_engine_utc_phase('N');
    return 0;
  }
  nvlist_t *root = NULL, *leaf = NULL, *props = NULL;
  const nvlist_t *child_input[1];
  if (nvlist_alloc(&root, NV_UNIQUE_NAME, KM_SLEEP) ||
      nvlist_alloc(&leaf, NV_UNIQUE_NAME, KM_SLEEP) ||
      nvlist_alloc(&props, NV_UNIQUE_NAME, KM_SLEEP) ||
      nvlist_add_string(root, ZPOOL_CONFIG_TYPE, VDEV_TYPE_ROOT) ||
      nvlist_add_string(leaf, ZPOOL_CONFIG_TYPE, VDEV_TYPE_FILE) ||
      nvlist_add_string(leaf, ZPOOL_CONFIG_PATH, AETHER_VOLUME_PATH) ||
      nvlist_add_uint64(leaf, ZPOOL_CONFIG_ASHIFT, 9) ||
      nvlist_add_string(props, "cachefile", "none") ||
      nvlist_add_uint64(props, "multihost", 0) ||
      nvlist_add_uint64(props, "autotrim", 0) ||
      nvlist_add_uint64(props, "autoexpand", 0))
    return 872;
  child_input[0] = leaf;
  if (nvlist_add_nvlist_array(root, ZPOOL_CONFIG_CHILDREN, child_input, 1))
    return 872;
  uint64_t hash = UINT64_C(14695981039346656037);
  if (aether_pool_config_hash(root, &hash) ||
      aether_pool_config_hash(props, &hash))
    return 872;
  aether_engine_utc_phase('P');
#ifndef AETHER_POOL_UNCOMMITTED
  for (unsigned i = 0; i < 8; ++i)
    aether_engine_utc_phase((hash >> (8 * i)) & 255);
#endif
  /* Inputs are private, pinned construction; no helper/caller mutates them. */
  /* Original spa_prop_validate only accepts explicit legacy versions <=28.
   * Omission selects pinned SPA_VERSION=5000 in original spa_create; no
   * feature@ property is supplied. Inspect the resulting format below. */
#ifdef AETHER_POOL_DIAGNOSTICS
  /* Prove this raw emitter works before entering the failing creation path. */
  extern void aether_pool_failure_site(unsigned);
  aether_pool_failure_site('C');
#else
  aether_engine_utc_phase('C');
#endif
  int error = spa_create("aether_pool_probe", root, props, NULL, NULL);
  nvlist_free(props);
  nvlist_free(leaf);
  nvlist_free(root);
  if (error) {
    aether_engine_utc_phase('E');
    for (unsigned i = 0; i < 4; ++i)
      aether_engine_utc_phase(((uint32_t)error >> (8 * i)) & 255);
    return 872;
  }
  aether_engine_utc_phase('A');
  spa_t *spa = NULL;
  if (spa_open("aether_pool_probe", &spa, FTAG) ||
      spa_version(spa) != SPA_VERSION_FEATURES)
    return 872;
  for (spa_feature_t f = 0; f < SPA_FEATURES; ++f)
    if (spa_feature_is_enabled(spa, f))
      return 872;
#ifdef AETHER_POOL_DATA
  aether_engine_utc_phase('T');
  uint64_t target = 0;
  int data_error = aether_pool_data_write(spa, &target);
  if (data_error) {
    spa_close(spa, FTAG);
    aether_engine_utc_phase('E');
    for (unsigned i = 0; i < 4; ++i)
      aether_engine_utc_phase(((uint32_t)data_error >> (8 * i)) & 255);
    return 872;
  }
  for (unsigned i = 0; i < 8; ++i)
    aether_engine_utc_phase((target >> (8 * i)) & 255);
  aether_engine_utc_phase('S');
#ifdef AETHER_POOL_CAPACITY_PROBE
  _Static_assert(ENOSPC == 28, "pinned native errno observation");
  if (aether_pool_data_capacity(spa, target)) {
    spa_close(spa, FTAG);
    return 872;
  }
  aether_engine_utc_phase('Q');
  aether_engine_utc_phase(ENOSPC);
#endif
#endif
#ifdef AETHER_POOL_UNCOMMITTED
#if !defined(AETHER_POOL_DATA) || !defined(AETHER_POOL_INTERRUPT)
#error "uncommitted checkpoint requires interrupted assigned data"
#endif
  /* Preserve the live SPA borrow while the dirty second TXG is held. */
  if (aether_pool_hooks_check_ordered()) {
    spa_close(spa, FTAG);
    return 872;
  }
  (void)aether_pool_data_hold(spa, target);
  spa_close(spa, FTAG);
  return 872;
#endif
  spa_close(spa, FTAG);
#ifdef AETHER_POOL_INTERRUPT
#ifndef AETHER_POOL_DATA
#error "pool interruption requires assigned data"
#endif
  extern int aether_engine_pool_checkpoint(void);
  /* The actual selected transaction's sync/readback and borrow close precede
   * this check. Never mask pending/ordering bits or export after checkpoint. */
  if (aether_pool_hooks_check_ordered())
    return 872;
  return aether_engine_pool_checkpoint();
#endif
  nvlist_t *exported = NULL, *tree = NULL;
  nvlist_t **children = NULL;
  uint_t count = 0;
  const char *type = NULL, *path = NULL;
  if (spa_export("aether_pool_probe", &exported, B_FALSE, B_FALSE) ||
      !exported ||
      nvlist_lookup_nvlist(exported, ZPOOL_CONFIG_VDEV_TREE, &tree) ||
      nvlist_lookup_nvlist_array(tree, ZPOOL_CONFIG_CHILDREN, &children,
                                 &count) ||
      count != 1 ||
      nvlist_lookup_string(children[0], ZPOOL_CONFIG_TYPE, &type) ||
      strcmp(type, VDEV_TYPE_FILE) ||
      nvlist_lookup_string(children[0], ZPOOL_CONFIG_PATH, &path) ||
      strcmp(path, AETHER_VOLUME_PATH))
    return 872;
  nvlist_free(exported);
  spa_namespace_enter(FTAG);
  int present = spa_lookup("aether_pool_probe") != NULL;
  spa_namespace_exit(FTAG);
  if (present || (aether_pool_hooks_check(0) & ~AETHER_POOL_TXG_PENDING))
    return 872;
#ifdef AETHER_POOL_DATA
  /* Export drained original helpers; no pending/ordering bit may be masked. */
  if (aether_pool_hooks_check_ordered())
    return 872;
#endif
  aether_engine_utc_phase('D');
  return 0;
}
