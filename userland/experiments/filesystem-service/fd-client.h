/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FD_CLIENT_H
#define AETHER_FD_CLIENT_H
#include "fd-protocol.h"

#define AEFD_IO_BUDGET 16384U

struct aefd_close_result {
    int64_t input;
    int64_t output;
};
/* Trusted endpoint adapter. Only -11 is retryable, after wait returns zero.
 * Callbacks must bound their own duration and retain native ownership evidence.
 */
struct aefd_io {
    void *context;
    int64_t (*read)(void *, unsigned char *, size_t);
    int64_t (*write)(void *, const unsigned char *, size_t);
    int (*wait)(void *, int writing);
    struct aefd_close_result (*close)(void *);
};
struct aefd_client {
    struct aefd_io io;
    unsigned char *workspace;
    uint64_t generation;
    uint64_t sequence;
    int live;
    struct aefd_close_result closed;
};
/* Initialize fresh unowned storage once. On success callbacks/workspace become
 * exclusive borrows until abort. No authentication or native admission occurs.
 * Reinitializing a live/retired client to reuse its stream is forbidden. */
int aefd_client_init(struct aefd_client *, struct aefd_io,
                     unsigned char workspace[AEFD_READ_MAX],
                     uint64_t generation);
void aefd_client_abort(struct aefd_client *);
/* All ranges valid and disjoint from client/workspace. Serialized,
 * nonreentrant. Returns 1 for a complete validated reply (inspect status), 0
 * for local invalid arguments with no I/O, -1 for retirement. Output metadata
 * changes only on 1. Successful read bytes reside in workspace until the next
 * call/abort; every failure clears it. No libc/errno interposition or full
 * pathname support. */
int aefd_client_exchange(struct aefd_client *, uint64_t opcode,
                         const uint64_t args[4], const unsigned char *name,
                         size_t name_length, struct aefd_reply *);
#ifdef AEFD_WRITE_WIRE
#include "fd-file-write.h"
#endif
#endif
