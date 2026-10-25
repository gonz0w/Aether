/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FD_ROUTING_H
#define AETHER_FD_ROUTING_H
#include "fd-bindings.h"
#include "fd-facade.h"

struct aefd_stream_result {
    int complete;
    int64_t result;
};
struct aefd_stream_reader {
    void *context;
    /* Workspace has4096-byte capacity; source may write only requested count.
     * complete1: known count/private negative errno; otherwise unknown outcome.
     * Trusted adapter owns actual rights, deadlines and endpoint settlement. */
    struct aefd_stream_result (*read)(void *, unsigned kind, unsigned selector,
                                      unsigned char *, size_t count);
};
/* Read-only dispatch of a decoded immutable map. All ranges valid/disjoint,
 * serialized/nonreentrant; callback must not mutate map/client. No table
 * mutation, native authority, libc interposition or file-to-stream fallback. */
int64_t aefd_routed_read(const struct aefd_bindings *, struct aefd_client *,
                         const struct aefd_stream_reader *, int logical_fd,
                         unsigned char *out, size_t count);
#endif
