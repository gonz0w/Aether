// SPDX-License-Identifier: BSD-2-Clause
#include "session.h"
#include <errno.h>
struct closure {
    struct ts_state *state;
    const struct tf_ops *ops;
    void *context;
};

struct tv_reply ts_write(struct ts_state *s, unsigned sink,
                         const struct tv_part *parts, unsigned count,
                         tv_send send, void *context)
{
    if (!s)
        return (struct tv_reply){1, 0, -EINVAL};
    if (s->io.poisoned)
        return (struct tv_reply){0, 0, -EIO};
    if (s->finish.started)
        return (struct tv_reply){1, 0, -EBADF};
    return tv_write(&s->io, sink, parts, count, send, context);
}
static enum tf_result observe(struct closure *c, enum tf_result result)
{
    if (result != TF_OK && result != TF_ERROR) {
        c->state->io.poisoned = 1;
        return TF_UNKNOWN;
    }
    return result;
}
static enum tf_result close_role(void *context, unsigned role)
{
    struct closure *c = context;
    if (c->state->io.poisoned)
        return TF_UNKNOWN;
    return observe(c, c->ops->close(c->context, role));
}
static enum tf_result diagnostic(void *context)
{
    struct closure *c = context;
    if (c->state->io.poisoned)
        return TF_UNKNOWN;
    return observe(c, c->ops->diagnostic(c->context));
}
unsigned ts_finish(struct ts_state *s, unsigned status, int flushed,
                   const struct tf_ops *ops, void *context)
{
    if (!s)
        return 1;
    if (s->finish.started)
        return tf_finish(&s->finish, status, flushed, NULL, NULL);
    if (status > 255 || flushed != 1 || !ops || !ops->close || !ops->diagnostic)
        return tf_finish(&s->finish, status, flushed, NULL, NULL);
    if (s->io.poisoned || s->io.busy) {
        s->io.poisoned = 1;
        s->finish.started = s->finish.done = 1;
        s->finish.status = status ? status : 1;
        s->finish.consumed = 7;
        for (unsigned i = 0; i < 3; i++)
            s->finish.closes[i] = TF_ABANDONED;
        return s->finish.status;
    }
    struct closure c = {s, ops, context};
    const struct tf_ops wrapped = {close_role, diagnostic};
    return tf_finish(&s->finish, status, flushed, &wrapped, &c);
}
