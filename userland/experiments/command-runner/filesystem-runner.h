/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FILESYSTEM_RUNNER_H
#define AETHER_FILESYSTEM_RUNNER_H
#include "runner-parse.h"

/* Host composition boundary. These are typed values, not native wire records.
 * The Owner must independently authenticate all incoming facts and grants. */
struct ar_fs_io {
    uint64_t input_read, output_write;
};
struct ar_fs_child {
    uint32_t slot, generation;
};
enum ar_fs_delivery { AR_FS_UNKNOWN, AR_FS_DENIED, AR_FS_ADMITTED };
struct ar_fs_terminal {
    struct ar_fs_child child;
    uint32_t kind, detail;
    int cleanup_complete;
};
/* Admission resolves the command inside the Owner. Collect returns 1 for
 * an authenticated terminal observation, even when subsequent cleanup fails.
 * Cleanup completion must be a distinct fact, never inferred from status. */
struct ar_fs_owner {
    enum ar_fs_delivery (*admit)(void *, const struct ar_invocation *,
                                const struct ar_fs_io *, struct ar_fs_child *);
    int (*collect)(void *, struct ar_fs_child, struct ar_fs_terminal *);
};
enum ar_fs_state {
    AR_FS_NEW,
    AR_FS_INVALID,
    AR_FS_REJECTED,
    AR_FS_ADMISSION_UNCERTAIN,
    AR_FS_COLLECTION_UNCERTAIN,
    AR_FS_CLEANUP_FAILED,
    AR_FS_COMPLETE,
};
struct ar_fs_run {
    enum ar_fs_state state;
    /* In AR_FS_ADMISSION_UNCERTAIN the child is an unverified recovery hint. */
    struct ar_fs_child child;
    struct ar_fs_terminal terminal;
    unsigned exit_status;
};
/* One execution attempt per zero-initialized run. A transport of unknown
 * outcome owns recovery outside this call; running the same state again is
 * prohibited. All borrowed arguments are synchronous and disjoint. */
void ar_fs_run(struct ar_fs_run *, const unsigned char *, size_t,
               const struct ar_fs_io *, const struct ar_fs_owner *, void *);
#endif
