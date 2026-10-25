/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_ZPL_EXTEND_H
#define AETHER_ZPL_EXTEND_H
#include "zpl-resize.h"
/* Private serialized engine-owner initialized growth, not POSIX ftruncate.
 * Compile zpl-extend.c instead of resize/write/read. All write/resize pointer,
 * SPA, alias, accounting, flags, UTC and irreversible-error obligations apply.
 * Same size is a checked no-op; growth is at most4096 initialized zero bytes.
 * No sparse allocation promise. Result is the original writer's progress:
 * bytes_staged can be positive before metadata/sync failure. Retire on assigned
 * error; never infer no effects or replay. Numeric IDs convey no authority. */
int aether_zpl_extend(aether_zpl_view *, uint64_t object, uint64_t generation,
                      uint64_t size, uint64_t seconds, uint64_t nanoseconds,
                      aether_zpl_write_result *);
#endif
