/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FD_FACADE_H
#define AETHER_FD_FACADE_H
#include "fd-client.h"
/* File-only explicit-context facade, not libc interposition. Returns a
 * nonnegative result or negative private errno. No native authority is
 * acquired. All pointer ranges valid/disjoint; retain client
 * serialization/lifetime rules.
 */
int64_t aefd_file_open(struct aefd_client *, const unsigned char *,
                       size_t length, int cloexec);
int64_t aefd_file_read(struct aefd_client *, int fd, unsigned char *,
                       size_t count);
int64_t aefd_file_seek(struct aefd_client *, int fd, int64_t delta, int whence);
int64_t aefd_file_dup(struct aefd_client *, int fd, int minimum, int cloexec);
int64_t aefd_file_close(struct aefd_client *, int fd);
int64_t aefd_file_set_cloexec(struct aefd_client *, int fd, int cloexec);
#ifdef AEFD_DUP2_WIRE
int64_t aefd_file_replace(struct aefd_client *, int source, int target);
#endif
#ifdef AEFD_WRITE_WIRE
int64_t aefd_file_open_home(struct aefd_client *, const unsigned char *, size_t,
                            int access, int cloexec);
int64_t aefd_file_write(struct aefd_client *, int fd, const unsigned char *,
                        size_t, struct aefd_write_result *);
#endif
#endif
