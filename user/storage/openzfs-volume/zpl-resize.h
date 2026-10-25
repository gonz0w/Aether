/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_ZPL_RESIZE_H
#define AETHER_ZPL_RESIZE_H
#include "zpl-write.h"

/* Private engine-owner FFI, not client authority or POSIX ftruncate. Compile
 * zpl-resize.c INSTEAD OF zpl-write.c/zpl-read.c. All write-header ownership,
 * UTC, serialization, aliasing and irreversible-error rules apply. Existing
 * regular files only: shrink a finite tail <=1MiB, never grow. Same-size is a
 * checked no-op (UNASSIGNED). Result bytes_staged is always0, not evidence of
 * unchanged data. COMMITTED on error requires retirement, even with txg0.
 * SYNCED alone does not acknowledge public durability. */
int aether_zpl_shrink(aether_zpl_view *, uint64_t object, uint64_t generation,
                      uint64_t size, uint64_t seconds, uint64_t nanoseconds,
                      aether_zpl_write_result *);
#endif
