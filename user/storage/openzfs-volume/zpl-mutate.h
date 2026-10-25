/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_ZPL_MUTATE_H
#define AETHER_ZPL_MUTATE_H
#include "zpl-write.h"

/* Private serialized engine-owner FFI, not client authority/POSIX policy.
 * Compile zpl-mutate.c instead of zpl-write.c/read.c. All write-header SPA,
 * pointer/alias, accounting, property/teardown and irreversible-error rules
 * apply. Components are 1..255 bytes, not NUL/slash/dot/dotdot. Local IDs
 * <=INT32_MAX are labels only. Create makes a private0600 empty regular SA file
 * with a trivial protected ACL; inherited ACL/project, FUID/special directory
 * modes are unsupported. Rename is same-directory, no replace, single-link
 * regular; identical names are a validated UNASSIGNED no-op. Remove requires no
 * live aliases, no external xattr object and physical extent <=1MiB. No open
 * unlink. Parent/child expected identities are mandatory. bytes_staged stays0,
 * never proof of no effects. Assigned errors commit: retire/stop/investigate,
 * never export/reuse/replay or claim failure atomicity. Created node on error
 * is only an allocation record, not a usable handle. SYNCED is not a public
 * durability acknowledgment. Results/created are initialized and must not alias
 * inputs.
 */
int aether_zpl_create(aether_zpl_view *, uint64_t directory,
                      uint64_t directory_generation, const unsigned char *,
                      size_t length, uint64_t uid, uint64_t gid,
                      uint64_t seconds, uint64_t nanoseconds,
                      aether_zpl_node *created, aether_zpl_write_result *);
int aether_zpl_rename(aether_zpl_view *, uint64_t directory,
                      uint64_t directory_generation, const unsigned char *from,
                      size_t from_length, const unsigned char *to,
                      size_t to_length, uint64_t object, uint64_t generation,
                      uint64_t seconds, uint64_t nanoseconds,
                      aether_zpl_write_result *);
int aether_zpl_remove(aether_zpl_view *, uint64_t directory,
                      uint64_t directory_generation, const unsigned char *,
                      size_t length, uint64_t object, uint64_t generation,
                      uint64_t seconds, uint64_t nanoseconds,
                      aether_zpl_write_result *);
#endif
