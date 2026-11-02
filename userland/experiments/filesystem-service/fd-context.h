/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FD_CONTEXT_H
#define AETHER_FD_CONTEXT_H
#include "fd-native.h"
/* Place outside the small init stack: this object contains4096 workspace bytes.
 * Fresh zeroed, stable exclusive storage, all input/output ranges disjoint from
 * context and each other. Never memcpy/move an admitted context: internal
 * borrows point to its members. No native fork/exec authority follows from
 * snapshot data. Owner authenticates all startup inputs; no greeting is read
 * here.
 */
struct aefd_context {
    struct aefd_native native;
    struct aefd_bindings map;
    struct aefd_client client;
    struct aefd_session session;
    unsigned char workspace[AEFD_READ_MAX];
    int state;
#ifdef AEFD_TERMINAL_MODE_BINDINGS
    uint32_t mode_control;
    uint64_t mode_revision;
#endif
};
int64_t aefd_context_init(struct aefd_context *, aefd_native_call, void *,
                          uint64_t input, uint64_t output,
                          const unsigned char *, size_t, uint64_t generation,
                          const struct aefd_native_source[7],
                          const unsigned generations[2], uint32_t factory);
/* Each call owns its complete native mask guard, including compound redirect.
 * Serialized, single-threaded, nonreentrant. -16 on nested entry leaves the
 * running operation alone. Mask failure terminally aborts transport. Private
 * errno/count API, not libc/POSIX interposition; stream counts remain <=16.
 */
#ifdef AEFD_TERMINAL_DUPLEX_BINDINGS
int64_t aefd_context_open_duplex(struct aefd_context *, int);
#endif
#ifdef AEFD_TERMINAL_MODE_BINDINGS
/* Private scalar005 control. Output remains untouched on every failure. */
int64_t aefd_context_mode(struct aefd_context *, int, unsigned, unsigned,
                          unsigned, unsigned *);
#endif
int64_t aefd_context_open(struct aefd_context *, const unsigned char *, size_t,
                          int);
#ifdef AEFD_CWD_WIRE
/* Physical NUL-terminated path, at most256 bytes, caller owns disjoint output.
 */
int64_t aefd_context_chdir(struct aefd_context *, const unsigned char *,
                           size_t);
int64_t aefd_context_getcwd(struct aefd_context *, unsigned char[256]);
#endif
int64_t aefd_context_read(struct aefd_context *, int, unsigned char *, size_t);
int64_t aefd_context_write(struct aefd_context *, int, const unsigned char *,
                           size_t);
int64_t aefd_context_dup(struct aefd_context *, int, int, int);
int64_t aefd_context_replace(struct aefd_context *, int, int);
struct aefd_redirect_result aefd_context_redirect(struct aefd_context *, int,
                                                  int);
int64_t aefd_context_pipe(struct aefd_context *, int[2], int);
int64_t aefd_context_close(struct aefd_context *, int);
/* Ephemeral description from the same guarded canonical table. Rights are the
 * admitted source READ/WRITE bits, not a new capability or cached status. */
int64_t aefd_context_describe(struct aefd_context *, int, struct aefd_binding *,
                              unsigned *);
int64_t aefd_context_flags(struct aefd_context *, int);
int64_t aefd_context_set_flags(struct aefd_context *, int, int);
int64_t aefd_context_seek(struct aefd_context *, int, int64_t, int);
int64_t aefd_context_snapshot(struct aefd_context *, unsigned char *, size_t,
                              int);
/* 0 publishes a terminal cached receipt (possibly unknown); negative leaves out
 * untouched. No source cleanup after retirement. Physical settlement remains
 * with owner. Fresh/invalid context cannot manufacture a completed receipt.
 */
int64_t aefd_context_finish(struct aefd_context *, struct aefd_finish *out);
#endif
