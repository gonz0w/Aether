/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FD_SESSION_H
#define AETHER_FD_SESSION_H
#include "fd-pipe.h"
#include "fd-redirect.h"
#include "fd-replace.h"
#include "fd-write.h"
struct aefd_adapters {
    struct aefd_stream_reader reader;
    struct aefd_stream_writer writer;
    struct aefd_stream_closer closer;
    struct aefd_pipe_creator creator;
};
struct aefd_finish {
    unsigned attempted, removed, remaining;
    int64_t first_error;
    int unknown;
    struct aefd_close_result transport;
};
/* Fresh zeroed storage; all borrows valid/disjoint/exclusive/nonreentrant.
 * One canonical table/client; adapters retain actual native authority/lifetime.
 * No reinitialization after admission/finish, even on unknown completion. */
struct aefd_session {
    struct aefd_bindings *map;
    struct aefd_client *client;
    struct aefd_adapters adapters;
    int initialized, finished;
    struct aefd_finish receipt;
};
int64_t aefd_session_init(struct aefd_session *, struct aefd_bindings *,
                          struct aefd_client *, const unsigned char *, size_t,
                          uint64_t generation, struct aefd_io,
                          unsigned char workspace[AEFD_READ_MAX],
                          struct aefd_adapters);
#ifdef AEFD_TERMINAL_DUPLEX_BINDINGS
int64_t aefd_session_open_duplex(struct aefd_session *, int);
#endif
int64_t aefd_session_open(struct aefd_session *, const unsigned char *, size_t,
                          int);
int64_t aefd_session_read(struct aefd_session *, int, unsigned char *, size_t);
int64_t aefd_session_write(struct aefd_session *, int, const unsigned char *,
                           size_t);
int64_t aefd_session_dup(struct aefd_session *, int, int, int);
struct aefd_redirect_result aefd_session_redirect(struct aefd_session *, int,
                                                  int);
int64_t aefd_session_replace(struct aefd_session *, int, int);
int64_t aefd_session_pipe(struct aefd_session *, int pair[2], int);
int64_t aefd_session_close(struct aefd_session *, int);
int64_t aefd_session_binding(struct aefd_session *, int, struct aefd_binding *);
int64_t aefd_session_flags(struct aefd_session *, int);
int64_t aefd_session_set_flags(struct aefd_session *, int, int);
int64_t aefd_session_seek(struct aefd_session *, int, int64_t, int);
/* Output unchanged on failure; projection never closes or authorizes exec. */
int64_t aefd_session_snapshot(struct aefd_session *, unsigned char *, size_t,
                              int omit_cloexec);
/* Terminal cached local receipt, not proof of native settlement. Raw transport
 * errors/remaining objects/unknown must be reconciled by actual owner. */
struct aefd_finish aefd_session_finish(struct aefd_session *);
#endif
