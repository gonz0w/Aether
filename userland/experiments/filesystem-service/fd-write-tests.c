/* SPDX-License-Identifier: BSD-2-Clause */
/* Real host pipe writes with explicitly injected completion observations. */
#include "fd-write-tests.h"
#include "fd-write.h"
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
struct observed {
    int output;
    unsigned calls, closes, kind;
    size_t actual;
    struct aefd_stream_result reply;
};
static unsigned char scratch[AEFD_READ_MAX], input[AEFD_READ_MAX];
static int64_t forbidden_read(void *ctx, unsigned char *out, size_t count)
{
    (void)ctx;
    (void)out;
    assert(count == SIZE_MAX);
    return -5;
}
static int64_t forbidden_write(void *ctx, const unsigned char *out,
                               size_t count)
{
    (void)ctx;
    (void)out;
    assert(count == SIZE_MAX);
    return -5;
}
static int forbidden_wait(void *ctx, int writing)
{
    (void)ctx;
    assert(writing == INT32_MIN);
    return -5;
}
static struct aefd_close_result file_close(void *context)
{
    struct observed *seen = context;
    ++seen->closes;
    return (struct aefd_close_result){-5, -9};
}
static struct aefd_stream_result stream_write(void *context, unsigned kind,
                                              unsigned selector,
                                              const unsigned char *bytes,
                                              size_t count)
{
    struct observed *seen = context;
    ++seen->calls;
    assert(kind == seen->kind && selector == (kind == AEFD_BIND_PIPE ? 3 : 1));
    assert(bytes == scratch && bytes != input);
    assert(!memcmp(bytes, input, count));
    assert(seen->actual <= count);
    assert(write(seen->output, bytes, seen->actual) == (ssize_t)seen->actual);
    return seen->reply;
}
static struct aefd_bindings map_for(unsigned mode)
{
    unsigned char raw[AEFD_BINDINGS_BYTES] = {0};
    memcpy(raw, "AEFDT001", 8);
    aefd_put(raw, 1, mode == 12 ? 78 : 77);
    aefd_put(raw, 2, 16);
    raw[64 + 1 * 4] = AEFD_BIND_CONSOLE;
    raw[65 + 1 * 4] = 1;
    raw[64 + 3 * 4] = AEFD_BIND_PIPE;
    raw[65 + 3 * 4] = 3;
    raw[64 + 8 * 4] = AEFD_BIND_FILE;
    raw[65 + 8 * 4] = 3;
    struct aefd_bindings map;
    assert(aefd_bindings_decode(raw, sizeof raw, mode == 12 ? 78 : 77, &map));
    return map;
}
static void exercise(void)
{
    static int ran;
    if (ran)
        return;
    ran = 1;
    for (unsigned mode = 0; mode < 18; ++mode) {
        int pair[2];
        assert(pipe(pair) == 0);
        struct observed seen = {.output = pair[1],
                                .kind = AEFD_BIND_PIPE,
                                .actual = 2,
                                .reply = {1, 2}};
        struct aefd_io io = {&seen, forbidden_read, forbidden_write,
                             forbidden_wait, file_close};
        struct aefd_client client;
        assert(aefd_client_init(&client, io, scratch, 77));
        memset(input, 0x5a, sizeof input);
        memset(scratch, 0xa5, sizeof scratch);
        struct aefd_bindings map = map_for(mode), before = map;
        struct aefd_stream_writer writer = {&seen, stream_write};
        int fd = 3, live = 1;
        int64_t expected = 2;
        unsigned calls = 1;
        size_t count = 4;
        const unsigned char *data = input;
        if (mode == 1) { /* Full maximum bounded write. */
            count = sizeof input;
            seen.actual = count;
            seen.reply.result = (int64_t)count;
            expected = (int64_t)count;
        } else if (mode == 2) {
            count = 0;
            data = NULL;
            seen.actual = 0;
            seen.reply.result = expected = 0;
        } else if (mode == 3) {
            seen.actual = 0;
            seen.reply.result = expected = -13;
        } else if (mode == 4 || mode == 5) {
            seen.actual = mode == 5 ? 2 : 0;
            seen.reply = (struct aefd_stream_result){0, 2};
            expected = -5;
            live = 0;
        } else if (mode == 6) {
            seen.actual = 0;
            seen.reply.result = 5;
            expected = -5;
            live = 0;
        } else if (mode == 7) {
            seen.actual = 0;
            seen.reply.complete = 2;
            expected = -5;
            live = 0;
        } else if (mode == 8) {
            seen.actual = 0;
            seen.reply.result = -INT64_C(2147483648);
            expected = -5;
            live = 0;
        } else if (mode == 9 || mode == 10) {
            fd = 8;
            count = mode == 10 ? 0 : 4;
            expected = -30;
            calls = 0;
        } else if (mode == 11) {
            writer.write = NULL;
            expected = -38;
            calls = 0;
        } else if (mode == 12) {
            expected = -5;
            live = 0;
            calls = 0;
        } else if (mode == 13) {
            fd = 15;
            expected = -9;
            calls = 0;
        } else if (mode == 14 || mode == 15) {
            count = mode == 14 ? sizeof input + 1 : 1;
            data = mode == 15 ? NULL : input;
            expected = -22;
            calls = 0;
        } else if (mode == 16) {
            fd = 1;
            seen.kind = AEFD_BIND_CONSOLE;
        } else if (mode == 17) {
            seen.actual = 0;
            seen.reply.result = expected = 0;
        }
        assert(aefd_routed_write(&map, &client, &writer, fd, data, count) ==
               expected);
        assert(client.live == live && seen.calls == calls);
        assert(!memcmp(&map, &before, sizeof map));
        for (size_t i = 0; i < sizeof input; ++i)
            assert(input[i] == 0x5a);
        if (calls || mode == 9 || mode == 10 || mode == 11 || mode == 12)
            for (size_t i = 0; i < sizeof scratch; ++i)
                assert(scratch[i] == 0);
        if (mode == 3) {
            seen.actual = 2;
            seen.reply = (struct aefd_stream_result){1, 2};
            assert(aefd_routed_write(&map, &client, &writer, fd, input, 4) ==
                   2);
            assert(seen.calls == 2 && client.live);
        }
        unsigned before_calls = seen.calls;
        if (!live) {
            assert(aefd_routed_write(&map, &client, &writer, fd, input, 4) ==
                   -5);
            assert(seen.calls == before_calls && seen.closes == 1);
        }
        /* Unknown result cannot stand for no output. Observe actual host bytes.
         */
        assert(close(pair[1]) == 0);
        unsigned char received[AEFD_READ_MAX];
        size_t total = 0;
        for (;;) {
            ssize_t got = read(pair[0], received, sizeof received);
            assert(got >= 0);
            if (!got)
                break;
            for (ssize_t i = 0; i < got; ++i)
                assert(received[i] == 0x5a);
            total += (size_t)got;
        }
        assert(total == (calls ? seen.actual : 0));
        assert(close(pair[0]) == 0);
        errno = 0;
        assert(fcntl(pair[0], F_GETFD) == -1 && errno == EBADF);
        aefd_client_abort(&client);
        assert(seen.closes == 1);
    }
}
int64_t aefd_write_test_open(struct aefd_bindings *map,
                             struct aefd_client *client,
                             const unsigned char *name, size_t length, int flag)
{
    exercise();
    return aefd_stream_test_open(map, client, name, length, flag);
}
int64_t aefd_write_test_dup(struct aefd_bindings *map,
                            struct aefd_client *client, int fd, int minimum,
                            int flag)
{
    exercise();
    return aefd_stream_test_dup(map, client, fd, minimum, flag);
}
int64_t aefd_write_test_close(struct aefd_bindings *map,
                              struct aefd_client *client, int fd)
{
    exercise();
    return aefd_stream_test_close(map, client, fd);
}
int64_t aefd_write_test_flags(struct aefd_bindings *map,
                              struct aefd_client *client, int fd, int flag)
{
    exercise();
    return aefd_stream_test_flags(map, client, fd, flag);
}
