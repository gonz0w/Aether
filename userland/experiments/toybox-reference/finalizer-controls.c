// SPDX-License-Identifier: BSD-2-Clause
#include "finalizer.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

struct fixture {
    struct tf_state state;
    const struct tf_ops *ops;
    unsigned returns[4], events[4], count, recurse;
};

static enum tf_result event(struct fixture *f, unsigned role)
{
    assert(f->count < 4);
    if (role < 3)
        assert(f->state.consumed & (1u << role));
    else
        assert(!(f->state.consumed & 4u));
    f->events[f->count++] = role;
    if (f->count == f->recurse) {
        unsigned nested = tf_finish(&f->state, 0, 1, f->ops, f);
        assert(nested != 0 && !f->state.done);
    }
    return (enum tf_result)f->returns[role];
}
static enum tf_result close_cb(void *ctx, unsigned role)
{
    assert(role < 3);
    return event(ctx, role);
}
static enum tf_result diagnostic_cb(void *ctx) { return event(ctx, 3); }
static const struct tf_ops ops = {close_cb, diagnostic_cb};

int main(void)
{
    unsigned cases = 0;
    for (unsigned a = 0; a < 4; a++)
        for (unsigned b = 0; b < 4; b++)
            for (unsigned c = 0; c < 4; c++)
                for (unsigned d = 0; d < 4; d++)
                    for (unsigned prior = 0; prior < 2; prior++)
                        for (unsigned recursion = 0; recursion < 5;
                             recursion++) {
                            struct fixture f = {.ops = &ops,
                                                .returns = {a, b, c, d},
                                                .recurse = recursion};
                            // Build expected transcript from declarative
                            // outcomes.
                            unsigned expected[4] = {0}, count = 1;
                            enum tf_close closes[3] = {
                                TF_ABANDONED, TF_ABANDONED, TF_ABANDONED};
                            closes[0] = a == 0   ? TF_CLOSED
                                        : a == 1 ? TF_FAILED
                                                 : TF_UNCERTAIN;
                            if (a < 2) {
                                expected[count++] = 1;
                                closes[1] = b == 0   ? TF_CLOSED
                                            : b == 1 ? TF_FAILED
                                                     : TF_UNCERTAIN;
                                if (b < 2) {
                                    if (a == 1 || b == 1)
                                        expected[count++] = 3;
                                    if ((a == 0 && b == 0) || d < 2) {
                                        expected[count++] = 2;
                                        closes[2] = c == 0   ? TF_CLOSED
                                                    : c == 1 ? TF_FAILED
                                                             : TF_UNCERTAIN;
                                    }
                                }
                            }
                            unsigned failed = a != 0 || b != 0 || c != 0;
                            unsigned reentered =
                                recursion && recursion <= count;
                            unsigned want = prior ? 64 : failed || reentered;
                            unsigned actual = tf_finish(
                                &f.state, prior ? 64 : 0, 1, &ops, &f);
                            assert(actual == want && f.state.done);
                            assert(f.state.reentered == reentered);
                            assert(f.state.consumed == 7);
                            assert(f.count == count);
                            assert(!memcmp(f.events, expected,
                                           count * sizeof(unsigned)));
                            assert(!memcmp(f.state.closes, closes,
                                           sizeof(closes)));
                            unsigned diag =
                                a < 2 && b < 2 && (a == 1 || b == 1);
                            assert(f.state.diagnostic_attempted == diag);
                            if (diag)
                                assert(
                                    f.state.diagnostic_result ==
                                    (d < 2 ? (enum tf_result)d : TF_UNKNOWN));
                            struct tf_state before = f.state;
                            assert(tf_finish(&f.state, 255, 0, NULL, NULL) ==
                                   want);
                            assert(!memcmp(&before, &f.state, sizeof(before)));
                            assert(f.count == count);
                            cases++;
                        }
    assert(tf_finish(NULL, 0, 1, &ops, NULL) == 1);
    for (unsigned i = 0; i < 5; i++) {
        struct fixture f = {.ops = &ops};
        struct tf_ops invalid = ops;
        if (i == 3)
            invalid.close = NULL;
        if (i == 4)
            invalid.diagnostic = NULL;
        assert(tf_finish(&f.state, i == 0 ? 256 : 0, i == 1 ? 0 : 1,
                         i == 2 ? NULL : &invalid, &f) == 1);
        assert(f.state.done && !f.count && !f.state.consumed);
    }
    printf("PASS: %u finalizer scenarios and 6 invalid-input controls\n",
           cases);
    return 0;
}
