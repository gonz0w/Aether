/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FD_WRITE_H
#define AETHER_FD_WRITE_H
#include "fd-routing.h"
struct aefd_stream_writer {
    void *context;
    /* Trusted owner: actual rights/deadline/settlement, known count or private
     * negative errno. Unknown may already have written bytes; never replay.
     * Input is borrowed const workspace for this call only. */
    struct aefd_stream_result (*write)(void *, unsigned kind, unsigned selector,
                                       const unsigned char *, size_t count);
};
/* Same exclusive/nonreentrant decoded-map/client contract as routed read.
 * Input/map/client/workspace ranges valid and disjoint. Read-only file entries
 * reject with -30; no file-to-stream fallback or new wire operation. */
int64_t aefd_routed_write(const struct aefd_bindings *, struct aefd_client *,
                          const struct aefd_stream_writer *, int logical_fd,
                          const unsigned char *input, size_t count);
#endif
