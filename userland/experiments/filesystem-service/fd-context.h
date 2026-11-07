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
#ifdef AEFD_ZSH_HOME_REDIRECTION_BINDINGS
    struct aefd_note_create_result note_create;
    struct aefd_write_result note_write;
    struct aefd_redirect_result note_redirect;
    uint16_t note_writers;
    int note_create_attempted, note_write_attempted;
#endif
#ifdef AEFD_ZSH_HOME_WRITE_BINDINGS
    /* Local correlated observations survive finish; they grant no authority. */
    struct aefd_write_result home_write;
    uint64_t home_close_generation, home_close_sequence;
    int64_t home_close_status;
    int home_write_fd, home_write_attempted, home_close_attempted;
#endif
#ifdef AEFD_TERMINAL_MODE_BINDINGS
    uint32_t mode_control;
    uint64_t mode_revision;
#ifdef AEFD_ZSH_FILESYSTEM_BINDINGS
    uint64_t directory_key, directory_epoch;
#endif
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
#ifdef AEFD_ZSH_FILESYSTEM_BINDINGS
struct aether_tinfo_directory_view {
    uint64_t kind, size, key, epoch;
};
int64_t aefd_context_access(struct aefd_context *, const unsigned char *,
                            size_t, unsigned);
/* Publish checked physical root and typed view before unmasking. */
int64_t aefd_context_root(struct aefd_context *, unsigned char[2]);
int64_t aefd_context_directory(struct aefd_context *, const unsigned char *,
                               size_t, struct aether_tinfo_directory_view *);
#endif
#ifdef AEFD_ZSH_HOME_WRITE_BINDINGS
int64_t aefd_context_open_home_write(struct aefd_context *,
                                     const unsigned char *, size_t, int);
#endif
#ifdef AEFD_ZSH_HOME_REDIRECTION_BINDINGS
int64_t aefd_context_create_note(struct aefd_context *, const unsigned char *,
                                 size_t, int, unsigned);
int64_t aefd_context_note_replace(struct aefd_context *, int, int);
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
