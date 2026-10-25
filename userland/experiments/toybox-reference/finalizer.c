// SPDX-License-Identifier: BSD-2-Clause
#include "finalizer.h"

static void fail(struct tf_state *s)
{
    if (!s->status)
        s->status = 1;
}

static enum tf_result normalize(enum tf_result result)
{
    return result == TF_OK || result == TF_ERROR ? result : TF_UNKNOWN;
}

static int close_role(struct tf_state *s, const struct tf_ops *ops, void *ctx,
                      unsigned role)
{
    s->consumed |= 1u << role;
    enum tf_result result = normalize(ops->close(ctx, role));
    s->closes[role] = result == TF_OK      ? TF_CLOSED
                      : result == TF_ERROR ? TF_FAILED
                                           : TF_UNCERTAIN;
    if (result != TF_OK)
        fail(s);
    return result != TF_UNKNOWN;
}

unsigned tf_finish(struct tf_state *s, unsigned status, int flushed,
                   const struct tf_ops *ops, void *ctx)
{
    if (!s)
        return 1;
    if (s->started) {
        if (!s->done) {
            s->reentered = 1;
            fail(s);
        }
        return s->status;
    }
    s->started = 1;
    s->status = status <= 255 ? status : 1;
    if (status > 255 || flushed != 1 || !ops || !ops->close ||
        !ops->diagnostic) {
        fail(s);
        s->done = 1;
        return s->status;
    }
    if (!close_role(s, ops, ctx, 0) || !close_role(s, ops, ctx, 1))
        goto abandoned;
    if (s->closes[0] == TF_FAILED || s->closes[1] == TF_FAILED) {
        s->diagnostic_attempted = 1;
        s->diagnostic_result = normalize(ops->diagnostic(ctx));
        if (s->diagnostic_result != TF_OK)
            fail(s);
        if (s->diagnostic_result == TF_UNKNOWN)
            goto abandoned;
    }
    (void)close_role(s, ops, ctx, 2);
    goto complete;
abandoned:
    for (unsigned i = 0; i < 3; i++) {
        if (!(s->consumed & (1u << i))) {
            s->consumed |= 1u << i;
            s->closes[i] = TF_ABANDONED;
        }
    }
complete:
    s->done = 1;
    return s->status;
}
