/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_LOCAL_FRONTEND_H
#define AETHER_LOCAL_FRONTEND_H
#include "local-output.h"
#include "runner-parse.h"
#include "runner-result.h"
enum ar_front_action { AF_FAILED, AF_LOCAL, AF_ADMITTED };
struct ar_front_ops {
    int (*admit)(void *, const struct ar_invocation *, unsigned char[32],
                 size_t *);
    struct ar_local_ops output;
};
struct ar_front_state {
    int started;
    enum ar_front_action action;
    enum ar_action selection;
    enum ar_reply_action admission_action;
    struct ar_invocation invocation;
    struct ar_reply admission;
    struct ar_local_state delivery;
};
/* Host proposal candidate, not a native launcher. Zeroed single-use state;
 * live disjoint carrier/state/context; synchronous callbacks with no re-entry
 * or mutation of borrowed const inputs. Admission may fill at most32 bytes and
 * returns1 only for a known reply; size is its actual length. Other results are
 * unknown. Caller owns both output roles and all admitted/unknown resources.
 * AF_ADMITTED hands off validated receipt only, not child completion. AF_FAILED
 * performs no invented cleanup; caller retains unresolved ownership. */
enum ar_front_action ar_front_run(struct ar_front_state *,
                                  const unsigned char *, size_t, uint32_t,
                                  const struct ar_front_ops *, void *);
#endif
