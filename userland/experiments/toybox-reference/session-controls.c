// SPDX-License-Identifier: BSD-2-Clause
#include "session.h"
#include <assert.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
struct fixture {
    struct ts_state state;
    unsigned write_kind, outcome[4], events[4], count, writes;
    unsigned recurse, finish_in_write;
};
static const struct tf_ops ops;
static struct tv_reply send_cb(void *ctx, unsigned sink, const unsigned char *p,
                               size_t n)
{
    struct fixture *f = ctx;
    assert(sink == 0 && n == 1 && p[0] == 42);
    f->writes++;
    if (f->finish_in_write)
        assert(ts_finish(&f->state, 0, 1, &ops, f) == 1);
    if (f->write_kind == 1)
        return (struct tv_reply){1, 0, -EIO};
    if (f->write_kind == 2)
        return (struct tv_reply){0, 0, 0};
    if (f->write_kind == 3)
        return (struct tv_reply){1, 2, 0};
    return (struct tv_reply){1, 1, 0};
}
static enum tf_result event(struct fixture *f, unsigned role)
{
    assert(!f->state.io.poisoned && f->count < 4);
    f->events[f->count++] = role;
    if (f->recurse) {
        assert(ts_write(&f->state, 0, NULL, 0, send_cb, f).error == -EBADF);
        assert(ts_finish(&f->state, 0, 1, &ops, f) != 0);
    }
    return (enum tf_result)f->outcome[role];
}
static enum tf_result close_cb(void *ctx, unsigned role)
{
    return event(ctx, role);
}
static enum tf_result diag_cb(void *ctx) { return event(ctx, 3); }
static const struct tf_ops ops = {close_cb, diag_cb};
int main(void)
{
    unsigned char byte = 42;
    struct tv_part part = {&byte, 1};
    unsigned scenarios = 0;
    for (unsigned w = 0; w < 4; w++)
        for (unsigned a = 0; a < 4; a++)
            for (unsigned b = 0; b < 4; b++)
                for (unsigned c = 0; c < 4; c++)
                    for (unsigned d = 0; d < 4; d++)
                        for (unsigned prior = 0; prior < 2; prior++)
                            for (unsigned recursion = 0; recursion < 2;
                                 recursion++) {
                                struct fixture f = {.write_kind = w,
                                                    .outcome = {a, b, c, d},
                                                    .recurse = recursion};
                                struct tv_reply wr = ts_write(
                                    &f.state, 0, &part, 1, send_cb, &f);
                                assert(wr.known == (w < 2));
                                unsigned expected[4], count = 0,
                                                      poisoned = w >= 2;
                                if (!poisoned) {
                                    expected[count++] = 0;
                                    if (a < 2) {
                                        expected[count++] = 1;
                                        if (b < 2) {
                                            if (a == 1 || b == 1)
                                                expected[count++] = 3;
                                            if ((a == 0 && b == 0) || d < 2)
                                                expected[count++] = 2;
                                        }
                                    }
                                    for (unsigned i = 0; i < count; i++)
                                        if (f.outcome[expected[i]] >= 2)
                                            poisoned = 1;
                                }
                                // The caller forwards its observed write
                                // failure as command status.
                                unsigned command = prior ? 64 : w ? 1 : 0;
                                unsigned want = command ? command
                                                : a || b || c || recursion ? 1
                                                                           : 0;
                                assert(ts_finish(&f.state, command, 1, &ops,
                                                 &f) == want);
                                assert(f.count == count && f.writes == 1);
                                assert(!memcmp(f.events, expected,
                                               count * sizeof(unsigned)));
                                assert(f.state.io.poisoned == poisoned);
                                assert(f.state.finish.done &&
                                       f.state.finish.consumed == 7);
                                if (w >= 2)
                                    for (unsigned i = 0; i < 3; i++)
                                        assert(f.state.finish.closes[i] ==
                                               TF_ABANDONED);
                                assert(
                                    ts_write(&f.state, 0, &part, 1, send_cb, &f)
                                        .error == (poisoned ? -EIO : -EBADF));
                                assert(ts_finish(&f.state, 0, 1, &ops, &f) ==
                                       want);
                                assert(f.count == count && f.writes == 1);
                                scenarios++;
                            }
    struct fixture active = {.finish_in_write = 1};
    assert(!ts_write(&active.state, 0, &part, 1, send_cb, &active).known);
    assert(active.state.io.poisoned && active.state.finish.done);
    assert(active.state.finish.consumed == 7 && active.writes == 1 &&
           !active.count);
    assert(ts_finish(&active.state, 0, 1, &ops, &active) == 1);
    struct fixture invalid = {0};
    assert(ts_finish(&invalid.state, 0, 0, &ops, &invalid) == 1);
    assert(!invalid.count && !invalid.state.finish.consumed);
    assert(ts_write(NULL, 0, &part, 1, send_cb, NULL).error == -EINVAL);
    assert(ts_finish(NULL, 0, 1, &ops, NULL) == 1);
    printf("PASS: %u session scenarios and 4 boundary controls\n", scenarios);
    return 0;
}
