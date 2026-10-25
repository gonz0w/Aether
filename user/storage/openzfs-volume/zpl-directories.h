/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_ZPL_DIRECTORIES_H
#define AETHER_ZPL_DIRECTORIES_H
#include "zpl-mutate.h"

/* Trusted serialized provider only; raw objects never confer client authority.
 * Compile zpl-directories.c INSTEAD OF zpl-mutate.c/write.c/read.c. All
 * original SPA/serialization/pointer/UTC/accounting/assigned-error obligations
 * apply. directory refresh validates expected generation and type without
 * mutation. mkdir creates empty0700 SA directories with protected trivial ACL,
 * links2, size2 and exact parent. Parent link/entry counts and times update in
 * one tx. rmdir requires expected parent/child identities, empty size2/links2,
 * no xattr, inherited ACL/project/special modes, and no live aliases (caller
 * obligation). Root/self removal is forbidden. No recursive removal or
 * cross-directory move. Outputs are initialized and separate from inputs.
 * Assigned errors commit; permanently retire/investigate, never replay or infer
 * no effects from errno.
 */
int aether_zpl_directory(aether_zpl_view *, uint64_t object,
                         uint64_t generation, aether_zpl_node *);
int aether_zpl_mkdir(aether_zpl_view *, uint64_t directory,
                     uint64_t directory_generation, const unsigned char *,
                     size_t length, uint64_t uid, uint64_t gid,
                     uint64_t seconds, uint64_t nanoseconds,
                     aether_zpl_node *created, aether_zpl_write_result *);
int aether_zpl_rmdir(aether_zpl_view *, uint64_t directory,
                     uint64_t directory_generation, const unsigned char *,
                     size_t length, uint64_t object, uint64_t generation,
                     uint64_t seconds, uint64_t nanoseconds,
                     aether_zpl_write_result *);
#endif
