/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_TASKQ_BRIDGE_H
#define AETHER_TASKQ_BRIDGE_H
#include <sys/zfs_context.h>
/* Integration hooks: no fallback/no-op implementation is supplied here. */
void aether_taskq_require_parent(void);
void *aether_taskq_map_arena(void);
void aether_taskq_unmap_arena(void *);
void aether_taskq_reap_all(void);
void aether_taskq_before_wait(kcondvar_t *);
/* fail() and start() hooks are declared in the private context header. */
void aether_taskq_begin(void);
void aether_taskq_end(void);
taskq_t *aether_taskq_create(const char *, unsigned);
void aether_taskq_destroy(taskq_t *);
taskqid_t aether_taskq_dispatch(taskq_t *, task_func_t, void *, unsigned);
#endif
