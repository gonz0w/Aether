/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FD_PIPE_H
#define AETHER_FD_PIPE_H
#include "fd-table.h"
struct aefd_pipe_result {
    int complete;
    int64_t status;
    unsigned read_selector, write_selector;
};
struct aefd_pipe_creator {
    void *context;
    /* Trusted source: complete1/status0 reports actual ordered pair3/4 or5/6.
     * Known negative has zero selectors. Own native rights, generations,
     * deadlines and cleanup; unknown may already have created resources. */
    struct aefd_pipe_result (*create)(void *);
};
/* Exclusive/nonreentrant canonical map/client; pair points to two valid ints,
 * disjoint from map/client/adapter. Publish both only after source validation.
 * cloexec is per-logical C metadata, not native exec enforcement. */
int64_t aefd_table_pipe(struct aefd_bindings *, struct aefd_client *,
                        const struct aefd_pipe_creator *, int pair[2],
                        int cloexec);
#endif
