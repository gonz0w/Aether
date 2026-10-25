/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FD_HOME_PROBE_ADAPTER_H
#define AETHER_FD_HOME_PROBE_ADAPTER_H
#include "fd-context.h"
#include "fd-table.h"
#ifndef AEFD_WRITE_WIRE
#error "home probe requires explicit FILE write wire"
#endif
/* One already-admitted stable context. Every range is initialized, live,
 * exclusively borrowed and disjoint from this context and its workspace.
 * These private operations retain the existing guard and authoritative map.
 * They neither admit a context nor activate routed/libc FILE writes. */
int64_t aefd_home_probe_open(struct aefd_context *, const unsigned char *,
                             size_t, int access, int cloexec);
int64_t aefd_home_probe_write(struct aefd_context *, int logical,
                              const unsigned char *, size_t,
                              struct aefd_write_result *);
int aefd_home_probe_run(struct aefd_context *);
#endif
