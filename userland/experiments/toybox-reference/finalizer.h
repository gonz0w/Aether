// SPDX-License-Identifier: BSD-2-Clause
#ifndef TOYBOX_FINALIZER_H
#define TOYBOX_FINALIZER_H

enum tf_result { TF_OK, TF_ERROR, TF_UNKNOWN };
enum tf_close {
    TF_UNATTEMPTED,
    TF_CLOSED,
    TF_FAILED,
    TF_UNCERTAIN,
    TF_ABANDONED
};
struct tf_ops {
    enum tf_result (*close)(void *, unsigned role);
    enum tf_result (*diagnostic)(void *);
};
struct tf_state {
    unsigned started, done, status, reentered, consumed;
    enum tf_close closes[3];
    unsigned diagnostic_attempted;
    enum tf_result diagnostic_result;
};
/* Host candidate, not native FDs: roles 0=input,1=output,2=diagnostic.
 * Requires zeroed private state, three owned roles and completed Toybox flush.
 * Callbacks are synchronous and may only reenter via tf_finish, not mutate
 * state. All arguments remain valid/disjoint throughout; no pointers are
 * retained. Unknown transport on this shared connection forbids further
 * callbacks. Diagnostic callback owns bounded delivery and returns its
 * aggregate outcome. No allocation, thread concurrency, grants or
 * remote-reclaim guarantee.
 */
unsigned tf_finish(struct tf_state *, unsigned command_status, int flushed,
                   const struct tf_ops *, void *);
#endif
