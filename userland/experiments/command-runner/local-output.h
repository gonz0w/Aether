/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_LOCAL_OUTPUT_H
#define AETHER_LOCAL_OUTPUT_H
#include <stddef.h>
#include <stdint.h>
enum ar_local_kind {
    AL_HELP,
    AL_VERSION,
    AL_USAGE,
    AL_UNAVAILABLE,
    AL_DENIED,
    AL_CAPACITY
};
enum ar_local_close {
    AL_UNATTEMPTED,
    AL_CLOSED,
    AL_CLOSE_FAILED,
    AL_CLOSE_UNKNOWN
};
enum ar_local_failure {
    AL_NONE,
    AL_INVALID,
    AL_ZERO,
    AL_WRITE_ERROR,
    AL_UNKNOWN
};
struct ar_local_io {
    int known;
    size_t count;
    int32_t error;
};
struct ar_local_plan {
    enum ar_local_kind kind;
    const unsigned char *text;
    size_t size;
    int32_t admission_error;
};
struct ar_local_ops {
    struct ar_local_io (*write)(void *, unsigned, const unsigned char *,
                                size_t);
    struct ar_local_io (*close)(void *, unsigned);
};
struct ar_local_state {
    int started;
    enum ar_local_kind kind;
    unsigned intended_exit, exit_status;
    int32_t admission_error, write_error, close_error[2];
    size_t delivered;
    enum ar_local_failure failure;
    enum ar_local_close closes[2];
};
/* Host-only proposal candidate: sink0 is stdout, sink1 stderr, not native FDs.
 * Caller supplies a zeroed state, live disjoint immutable plan/text and
 * callbacks; it already owns both sinks on one connection. Calls are
 * synchronous/non-reentrant. Known replies require error0/count in range, or
 * negative errno/count0. Unknown delivery forbids all further calls; no retry
 * or remote cleanup is inferred. State is single-use even after invalid input.
 * No borrowed pointer is retained.
 */
unsigned ar_local_deliver(struct ar_local_state *, const struct ar_local_plan *,
                          const struct ar_local_ops *, void *context);
#endif
