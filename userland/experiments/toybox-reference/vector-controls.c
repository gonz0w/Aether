// SPDX-License-Identifier: BSD-2-Clause
#include "vector.h"
#include <assert.h>
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
struct fixture {
    struct tv_state state;
    unsigned char expected[66];
    size_t size;
    unsigned sink, kind, recursion, calls;
};
static struct tv_reply send_cb(void *ctx, unsigned sink,
                               const unsigned char *data, size_t size)
{
    struct fixture *f = ctx;
    f->calls++;
    assert(f->state.busy && sink == f->sink && size == f->size);
    assert(!memcmp(data, f->expected, size));
    if (f->recursion) {
        struct tv_reply nested = tv_write(&f->state, sink, NULL, 0, send_cb, f);
        assert(!nested.known && f->calls == 1);
    }
    switch (f->kind) {
    case 0:
        return (struct tv_reply){1, size, 0};
    case 1:
        return (struct tv_reply){1, size ? 1 : 0, 0};
    case 2:
        return (struct tv_reply){1, 0, 0};
    case 3:
        return (struct tv_reply){1, 0, -EINTR};
    case 4:
        return (struct tv_reply){0, 0, 0};
    case 5:
        return (struct tv_reply){1, size + 1, 0};
    case 6:
        return (struct tv_reply){1, 0, 7};
    default:
        return (struct tv_reply){1, 1, -EIO};
    }
}
int main(void)
{
    unsigned char a[33], b[33];
    for (unsigned i = 0; i < 33; i++) {
        a[i] = (unsigned char)i;
        b[i] = (unsigned char)(255 - i);
    }
    unsigned cases = 0;
    for (unsigned n = 0; n <= 33; n++)
        for (unsigned m = 0; m <= 33; m++)
            for (unsigned sink = 0; sink < 2; sink++)
                for (unsigned kind = 0; kind < 8; kind++)
                    for (unsigned recursion = 0; recursion < 2; recursion++) {
                        struct fixture f = {
                            .sink = sink, .kind = kind, .recursion = recursion};
                        for (unsigned i = 0; i < n + m; i++)
                            f.expected[i] = i < n ? a[i] : b[i - n];
                        f.size = n + m < 16 ? n + m : 16;
                        struct tv_part parts[2] = {{n ? a : NULL, n},
                                                   {m ? b : NULL, m}};
                        struct tv_reply r =
                            tv_write(&f.state, sink, parts, 2, send_cb, &f);
                        unsigned unknown = recursion || kind >= 4;
                        assert(r.known == !unknown &&
                               f.state.poisoned == unknown);
                        assert(f.calls == 1 && !f.state.busy);
                        if (unknown) {
                            assert(r.error == -EIO && !r.count);
                            r = tv_write(&f.state, sink, parts, 2, send_cb, &f);
                            assert(!r.known && f.calls == 1);
                        } else {
                            int err = kind == 3             ? -EINTR
                                      : kind == 2 && f.size ? -EIO
                                                            : 0;
                            size_t progress = kind == 0             ? f.size
                                              : kind == 1 && f.size ? 1
                                                                    : 0;
                            assert(r.error == err && r.count == progress);
                        }
                        cases++;
                    }
    struct fixture f = {0};
    struct tv_part invalid[2] = {{a, 1}, {NULL, 1}};
    assert(tv_write(&f.state, 0, invalid, 2, send_cb, &f).error == -EFAULT);
    invalid[1] = (struct tv_part){b, (size_t)PTRDIFF_MAX};
    assert(tv_write(&f.state, 0, invalid, 2, send_cb, &f).error == -EINVAL);
    assert(tv_write(&f.state, 0, NULL, 1, send_cb, &f).error == -EINVAL);
    assert(tv_write(&f.state, 0, NULL, 3, send_cb, &f).error == -EINVAL);
    assert(tv_write(&f.state, 2, NULL, 0, send_cb, &f).error == -EBADF);
    assert(tv_write(&f.state, 0, NULL, 0, NULL, &f).error == -EINVAL);
    assert(tv_write(NULL, 0, NULL, 0, send_cb, &f).error == -EINVAL);
    assert(!f.calls && !f.state.poisoned);
    assert(tv_write(&f.state, 0, NULL, 0, send_cb, &f).known && f.calls == 1);
    printf("PASS: %u vector scenarios and 8 boundary controls\n", cases);
    return 0;
}
