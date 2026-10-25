// SPDX-License-Identifier: BSD-2-Clause
#ifndef TOYBOX_SESSION_H
#define TOYBOX_SESSION_H
#include "vector.h"
#include "finalizer.h"
struct ts_state {
    struct tv_state io;
    struct tf_state finish;
};
/* Private host composition. Same valid-buffer/callback/zero-state requirements
 * as vector.h/finalizer.h. No native authority, remote reclaim or concurrency.
 * Callbacks may reenter these APIs, but cannot mutate state or component
 * fields. Once finishing starts, public writes are forbidden; diagnostic
 * callback owns its bounded delivery. Initial poison abandons all roles without
 * callbacks.
 */
struct tv_reply ts_write(struct ts_state *, unsigned, const struct tv_part *,
                         unsigned, tv_send, void *);
unsigned ts_finish(struct ts_state *, unsigned, int, const struct tf_ops *,
                   void *);
#endif
