/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-replace.h"
#include <assert.h>
#include <stdio.h>

struct fixture {
    struct aefd_bindings map;
    struct aefd_client client;
    unsigned char workspace[AEFD_READ_MAX], reply[AEFD_FRAME];
    uint16_t live;
    unsigned calls, closes, stream_closes, last_op;
    int drop, wrong_target, close_error;
    struct aefd_stream_close_result stream;
};
static int64_t receive(void *context, unsigned char *out, size_t count)
{
    struct fixture *f = context;
    if (f->drop)
        return -32;
    assert(count == AEFD_FRAME);
    memcpy(out, f->reply, count);
    return (int64_t)count;
}
static int64_t send(void *context, const unsigned char *in, size_t count)
{
    struct fixture *f = context;
    assert(count == AEFD_FRAME && !memcmp(in, AEFD_MAGIC, 8));
    uint64_t op = aefd_word(in, 1), from = aefd_word(in, 4);
    uint64_t to = aefd_word(in, 5), result = 0;
    int status = 0;
    assert(from < 16 && (f->live & (1U << from)));
    ++f->calls;
    f->last_op = (unsigned)op;
    if (op == 4) {
        assert(!to && !aefd_word(in, 6));
        while (result < 16 && (f->live & (1U << result)))
            ++result;
        assert(result < 16);
        f->live |= (uint16_t)(1U << result);
    } else if (op == 5) {
        status = f->close_error;
        if (!status)
            f->live &= (uint16_t)~(1U << from);
    } else {
        assert(op == 7 && to < 16);
        result = to ^ (uint64_t)f->wrong_target;
    }
    memset(f->reply, 0, sizeof f->reply);
    memcpy(f->reply, AEFD_MAGIC, 8);
    aefd_put(f->reply, 1, (uint64_t)(int64_t)status);
    aefd_put(f->reply, 2, aefd_word(in, 2));
    aefd_put(f->reply, 3, aefd_word(in, 3));
    aefd_put(f->reply, 4, result);
    return (int64_t)count;
}
static int wait_io(void *context, int writing)
{
    (void)context;
    (void)writing;
    assert(0);
    return -1;
}
static struct aefd_close_result close_io(void *context)
{
    struct fixture *f = context;
    ++f->closes;
    return (struct aefd_close_result){-9, -5};
}
static struct aefd_stream_close_result
close_stream(void *context, unsigned kind, unsigned selector)
{
    struct fixture *f = context;
    assert((kind == AEFD_BIND_CONSOLE && selector <= 2) ||
           (kind == AEFD_BIND_PIPE && selector >= 3 && selector <= 6));
    ++f->stream_closes;
    return f->stream;
}
static struct aefd_binding binding(unsigned kind, int target)
{
    return (struct aefd_binding){
        (unsigned char)kind,
        (unsigned char)(kind == AEFD_BIND_FILE      ? (target ? 7 : 5)
                        : kind == AEFD_BIND_CONSOLE ? (target ? 0 : 1)
                        : kind == AEFD_BIND_PIPE    ? (target ? 4 : 3)
                                                    : 0),
        (unsigned char)(kind != AEFD_BIND_EMPTY), 0};
}
static void setup(struct fixture *f, unsigned source, unsigned target)
{
    memset(f, 0, sizeof *f);
    f->map.generation = 17;
    for (unsigned i = 0; i < 16; ++i)
        f->map.slots[i] =
            (struct aefd_binding){AEFD_BIND_FILE, (unsigned char)i, 1, 0};
    f->map.slots[5] = binding(source, 0);
    f->map.slots[7] = binding(target, 1);
    for (unsigned i = 0; i < 16; ++i)
        if (f->map.slots[i].kind == AEFD_BIND_FILE)
            f->live |= (uint16_t)(1U << f->map.slots[i].selector);
    f->stream = (struct aefd_stream_close_result){1, 1, 0};
    assert(aefd_client_init(
        &f->client, (struct aefd_io){f, receive, send, wait_io, close_io},
        f->workspace, 17));
}
static int64_t replace(struct fixture *f, int source, int target)
{
    struct aefd_stream_closer closer = {f, close_stream};
    return aefd_dup2(&f->map, &f->client, &closer, source, target);
}
int main(void)
{
    for (unsigned source = AEFD_BIND_CONSOLE; source <= AEFD_BIND_FILE;
         ++source)
        for (unsigned target = AEFD_BIND_EMPTY; target <= AEFD_BIND_FILE;
             ++target) {
            struct fixture f;
            setup(&f, source, target);
            struct aefd_binding from = f.map.slots[5];
            assert(replace(&f, 5, 7) == 7 && f.client.live && !f.closes);
            assert(!memcmp(&from, &f.map.slots[5], sizeof from));
            assert(f.map.slots[7].kind == source && !f.map.slots[7].cloexec);
            assert(f.calls ==
                   (source == AEFD_BIND_FILE || target == AEFD_BIND_FILE));
            if (source == AEFD_BIND_FILE && target == AEFD_BIND_FILE)
                assert(f.last_op == 7 && f.live == UINT16_MAX &&
                       f.map.slots[7].selector == 7);
            if (source != AEFD_BIND_FILE)
                assert(f.map.slots[7].selector == from.selector);
        }
    for (unsigned mode = 0; mode < 5; ++mode) {
        struct fixture f;
        setup(&f, AEFD_BIND_FILE, AEFD_BIND_CONSOLE);
        struct aefd_binding previous = f.map.slots[7];
        if (mode == 0)
            f.stream = (struct aefd_stream_close_result){1, 0, -13};
        if (mode == 1)
            f.stream = (struct aefd_stream_close_result){1, 1, -5};
        if (mode == 2)
            f.stream = (struct aefd_stream_close_result){0, 0, -5};
        if (mode == 3) {
            f.stream = (struct aefd_stream_close_result){1, 0, -13};
            f.close_error = -5;
        }
        if (mode == 4)
            f.drop = 1;
        int64_t result = replace(&f, 5, 7);
        if (mode == 0) {
            assert(result == -13 && f.client.live && f.calls == 2 && !f.closes);
            assert(!memcmp(&previous, &f.map.slots[7], sizeof previous));
            assert(!(f.live & (1U << 7)));
        } else if (mode == 1) {
            assert(result == 7 && f.client.live &&
                   f.map.slots[7].kind == AEFD_BIND_FILE);
        } else {
            assert(result == -5 && !f.client.live && f.closes == 1);
            unsigned calls = f.calls;
            assert(replace(&f, 5, 7) == -5 && f.calls == calls &&
                   f.closes == 1);
        }
    }
    for (unsigned mode = 0; mode < 6; ++mode) {
        struct fixture f;
        setup(&f, AEFD_BIND_FILE, AEFD_BIND_FILE);
        struct aefd_bindings old = f.map;
        if (mode < 4) {
            int from = mode == 0 ? -1 : mode == 1 ? 16 : 5;
            int to = mode == 2 ? -1 : mode == 3 ? 16 : 7;
            assert(replace(&f, from, to) == -9 && !f.calls && !f.closes);
            assert(!memcmp(&old, &f.map, sizeof old));
        } else if (mode == 4) {
            assert(replace(&f, 5, 5) == 5 && f.map.slots[5].cloexec &&
                   !f.calls);
        } else {
            f.wrong_target = 1;
            assert(replace(&f, 5, 7) == -5 && !f.client.live && f.closes == 1);
            assert(!memcmp(&old, &f.map, sizeof old));
        }
    }
    for (unsigned mode = 0; mode < 3; ++mode) {
        struct fixture f;
        setup(&f, AEFD_BIND_FILE, AEFD_BIND_FILE);
        if (mode == 0)
            f.map.slots[1].selector = 5;
        if (mode == 1)
            f.map.slots[1].kind = 9;
        if (mode == 2)
            f.map.generation = 18;
        assert(replace(&f, 5, 7) == -5 && !f.calls && f.closes == 1);
    }
    puts("26 exact mixed dup2 cases pass");
    return 0;
}
