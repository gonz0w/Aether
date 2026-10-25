// SPDX-License-Identifier: BSD-2-Clause
#ifndef TOYBOX_VECTOR_H
#define TOYBOX_VECTOR_H
#include <stddef.h>
struct tv_part {
    const unsigned char *data;
    size_t size;
};
struct tv_reply {
    int known;
    size_t count;
    int error;
};
struct tv_state {
    unsigned busy, poisoned;
};
typedef struct tv_reply (*tv_send)(void *, unsigned, const unsigned char *,
                                   size_t);
/* Host-only private stdio proposal. Sink0=output,1=diagnostic, not native FDs.
 * Zeroed shared state; synchronous callbacks; valid/disjoint borrowed objects.
 * Validate up to two vectors before copying. Each nonempty data pointer must
 * designate size readable bytes. No arbitrary pointer probing or thread safety.
 * Callback validates actual sink liveness/rights even for a zero-byte request.
 * Re-entry may only call tv_write; otherwise state/inputs must not be mutated.
 */
struct tv_reply tv_write(struct tv_state *, unsigned sink,
                         const struct tv_part *, unsigned parts, tv_send,
                         void *);
#endif
