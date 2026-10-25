/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FD_TABLE_H
#define AETHER_FD_TABLE_H
#include "fd-bindings.h"
#include "fd-facade.h"
/* Mutate the same decoded canonical table used by tagged reads. Exclusive,
 * nonreentrant access; map/client/name ranges valid and disjoint. Stream
 * entries must remain unchanged unless an enforcing owner coordinates their
 * mutation. Return logical FD/nonnegative success or negative private errno.
 * Occupied metadata survives unknown outcomes; a retired client cannot reuse
 * that state. */
int64_t aefd_table_open(struct aefd_bindings *, struct aefd_client *,
                        const unsigned char *name, size_t length, int cloexec);
int64_t aefd_table_dup(struct aefd_bindings *, struct aefd_client *, int fd,
                       int minimum, int cloexec);
int64_t aefd_table_seek(struct aefd_bindings *, struct aefd_client *, int fd,
                        int64_t delta, int whence);
int64_t aefd_table_close(struct aefd_bindings *, struct aefd_client *, int fd);
int64_t aefd_table_set_cloexec(struct aefd_bindings *, struct aefd_client *,
                               int fd, int cloexec);
/* Mixed stream operations keep logical aliases/flags here; actual stream
 * rights/lifetime remain with the enforcing owner. No native dup/exec claim. */
struct aefd_stream_close_result {
    int complete;
    int consumed;
    int64_t status;
};
struct aefd_stream_closer {
    void *context;
    struct aefd_stream_close_result (*close)(void *, unsigned kind,
                                             unsigned selector);
};
int64_t aefd_mixed_dup(struct aefd_bindings *, struct aefd_client *, int fd,
                       int minimum, int cloexec);
int64_t aefd_mixed_set_cloexec(struct aefd_bindings *, struct aefd_client *,
                               int fd, int cloexec);
int64_t aefd_mixed_close(struct aefd_bindings *, struct aefd_client *,
                         const struct aefd_stream_closer *, int fd);
#endif
