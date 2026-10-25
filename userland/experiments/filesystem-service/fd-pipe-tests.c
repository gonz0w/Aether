/* SPDX-License-Identifier: BSD-2-Clause */
/* Actual host pipe creation/lifetime; completion identity is injected. */
#include "fd-pipe-tests.h"
#include "fd-pipe.h"
#include "fd-write.h"
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
struct observed {
    int ends[4];
    unsigned creates, closes, stream_closes;
    int actual;
    struct aefd_pipe_result reply;
};
static unsigned char scratch[AEFD_READ_MAX], bytes[8];
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
static struct aefd_pipe_result create(void *context)
{
    struct observed *seen = context;
    ++seen->creates;
    if (seen->actual) {
        unsigned at = seen->ends[0] == -1 ? 0 : 2;
        assert(seen->creates <= 2 && seen->ends[at] == -1);
        assert(pipe(seen->ends + at) == 0);
    }
    return seen->reply;
}
static struct aefd_stream_result write_pipe(void *context, unsigned kind,
                                            unsigned selector,
                                            const unsigned char *input,
                                            size_t count)
{
    struct observed *seen = context;
    assert(kind == AEFD_BIND_PIPE && (selector == 4 || selector == 6));
    ssize_t result = write(seen->ends[selector - 3], input, count);
    assert(result >= 0);
    return (struct aefd_stream_result){1, result};
}
static struct aefd_stream_result read_pipe(void *context, unsigned kind,
                                           unsigned selector,
                                           unsigned char *out, size_t count)
{
    struct observed *seen = context;
    assert(kind == AEFD_BIND_PIPE && (selector == 3 || selector == 5));
    ssize_t result = read(seen->ends[selector - 3], out, count);
    assert(result >= 0);
    return (struct aefd_stream_result){1, result};
}
static struct aefd_stream_close_result close_pipe(void *context, unsigned kind,
                                                  unsigned selector)
{
    struct observed *seen = context;
    assert(kind == AEFD_BIND_PIPE && selector >= 3 && selector <= 6);
    unsigned at = selector - 3;
    assert(seen->ends[at] >= 0);
    assert(close(seen->ends[at]) == 0);
    seen->ends[at] = -1;
    ++seen->stream_closes;
    return (struct aefd_stream_close_result){1, 1, 0};
}
static struct aefd_bindings map_for(unsigned mode)
{
    unsigned char raw[AEFD_BINDINGS_BYTES] = {0};
    memcpy(raw, "AEFDT001", 8);
    aefd_put(raw, 1, mode == 5 ? 78 : 77);
    aefd_put(raw, 2, 16);
    raw[64 + 2 * 4] = AEFD_BIND_CONSOLE;
    raw[65 + 2 * 4] = 2;
    raw[64 + 8 * 4] = AEFD_BIND_FILE;
    raw[65 + 8 * 4] = 3;
    if (mode == 2 || mode == 3)
        for (unsigned fd = 0; fd < (mode == 2 ? 16U : 15U); ++fd) {
            raw[64 + fd * 4] = AEFD_BIND_CONSOLE;
            raw[65 + fd * 4] = 1;
        }
    if (mode == 13 || mode == 14) {
        raw[64 + 6 * 4] = AEFD_BIND_PIPE;
        raw[65 + 6 * 4] = mode == 13 ? 3 : 4;
    }
    struct aefd_bindings map;
    assert(aefd_bindings_decode(raw, sizeof raw, mode == 5 ? 78 : 77, &map));
    return map;
}
static void exercise(void)
{
    static int ran;
    if (ran)
        return;
    ran = 1;
    for (unsigned mode = 0; mode < 22; ++mode) {
        struct observed seen = {
            .ends = {-1, -1, -1, -1}, .actual = 1, .reply = {1, 0, 3, 4}};
        struct aefd_io io = {&seen, forbidden_read, forbidden_write,
                             forbidden_wait, file_close};
        struct aefd_client client;
        assert(aefd_client_init(&client, io, scratch, 77));
        struct aefd_bindings map = map_for(mode), before = map;
        struct aefd_pipe_creator creator = {&seen, create};
        int pair[2] = {-77, -88};
        int64_t expected = -5;
        int live = 0, flag = 0;
        unsigned calls = 1;
        if (mode == 0 || mode == 1) {
            expected = 0;
            live = 1;
            flag = (int)mode;
        } else if (mode == 2 || mode == 3) {
            expected = -24;
            live = 1;
            calls = 0;
        } else if (mode == 4) {
            seen.actual = 0;
            seen.reply = (struct aefd_pipe_result){1, -23, 0, 0};
            expected = -23;
            live = 1;
        } else if (mode == 5) {
            calls = 0;
        } else if (mode == 6 || mode == 7) {
            flag = mode == 6 ? -1 : 2;
            expected = -22;
            live = 1;
            calls = 0;
        } else if (mode == 8 || mode == 9) {
            seen.actual = mode == 9;
            seen.reply.complete = 0;
        } else if (mode == 10) {
            seen.reply.read_selector = 4;
            seen.reply.write_selector = 3;
        } else if (mode == 11) {
            seen.reply.write_selector = 3;
        } else if (mode == 12) {
            seen.reply.read_selector = 7;
            seen.reply.write_selector = 8;
        } else if (mode == 15) {
            seen.reply.status = 1;
        } else if (mode == 16) {
            seen.reply.status = -13; /* Error cannot carry claimed selectors. */
        } else if (mode == 17) {
            creator.create = NULL;
            expected = -38;
            live = 1;
            calls = 0;
        } else if (mode == 18) {
            seen.reply.status = -INT64_C(2147483648);
        } else if (mode == 19) {
            seen.reply.complete = 2;
        } else if (mode == 20) {
            expected = -38;
            live = 1;
            calls = 0;
        } else if (mode == 21) {
            seen.actual = 0;
            seen.reply = (struct aefd_pipe_result){1, -5, 0, 0};
            live = 1;
        }
        const struct aefd_pipe_creator *selected = mode == 20 ? NULL : &creator;
        assert(aefd_table_pipe(&map, &client, selected, pair, flag) ==
               expected);
        assert(client.live == live && seen.creates == calls);
        if (expected == 0) {
            assert(pair[0] == 0 && pair[1] == 1);
            assert(map.slots[0].kind == AEFD_BIND_PIPE &&
                   map.slots[0].selector == 3 && map.slots[0].cloexec == flag);
            assert(map.slots[1].kind == AEFD_BIND_PIPE &&
                   map.slots[1].selector == 4 && map.slots[1].cloexec == flag);
            assert(!memcmp(map.slots + 2, before.slots + 2,
                           14 * sizeof map.slots[0]));
            struct aefd_stream_writer writer = {&seen, write_pipe};
            struct aefd_stream_reader reader = {&seen, read_pipe};
            struct aefd_stream_closer closer = {&seen, close_pipe};
            assert(aefd_mixed_dup(&map, &client, pair[0], 3, 0) == 3);
            assert(aefd_mixed_close(&map, &client, &closer, pair[0]) == 0);
            assert(seen.stream_closes == 0);
            assert(aefd_routed_write(&map, &client, &writer, pair[1],
                                     (const unsigned char *)"ab", 2) == 2);
            assert(aefd_routed_read(&map, &client, &reader, 3, bytes, 2) == 2);
            assert(!memcmp(bytes, "ab", 2));
            /* A second distinct pair reuses logical0, not source selector0. */
            seen.reply = (struct aefd_pipe_result){1, 0, 5, 6};
            int second[2] = {-1, -1};
            assert(aefd_table_pipe(&map, &client, &creator, second, 0) == 0);
            assert(second[0] == 0 && second[1] == 4 && seen.creates == 2);
            assert(aefd_routed_write(&map, &client, &writer, second[1],
                                     (const unsigned char *)"cd", 2) == 2);
            assert(aefd_routed_read(&map, &client, &reader, second[0], bytes,
                                    2) == 2);
            assert(!memcmp(bytes, "cd", 2));
            assert(aefd_mixed_close(&map, &client, &closer, 3) == 0);
            assert(aefd_mixed_close(&map, &client, &closer, pair[1]) == 0);
            assert(aefd_mixed_close(&map, &client, &closer, second[0]) == 0);
            assert(aefd_mixed_close(&map, &client, &closer, second[1]) == 0);
            assert(seen.stream_closes == 4 &&
                   map.slots[8].kind == AEFD_BIND_FILE);
        } else {
            assert(!memcmp(&map, &before, sizeof map));
            assert(pair[0] == -77 && pair[1] == -88);
            if (!live) {
                assert(aefd_table_pipe(&map, &client, &creator, pair, 0) == -5);
                assert(seen.creates == calls && seen.closes == 1);
            }
            if (mode == 4) {
                seen.reply = (struct aefd_pipe_result){1, 0, 3, 4};
                seen.actual = 1;
                assert(aefd_table_pipe(&map, &client, &creator, pair, 0) == 0);
                assert(seen.creates == 2 && client.live);
                struct aefd_stream_writer writer = {&seen, write_pipe};
                struct aefd_stream_reader reader = {&seen, read_pipe};
                assert(aefd_routed_write(&map, &client, &writer, pair[1],
                                         (const unsigned char *)"ok", 2) == 2);
                assert(aefd_routed_read(&map, &client, &reader, pair[0], bytes,
                                        2) == 2);
                assert(!memcmp(bytes, "ok", 2));
            }
        }
        int old_pair[2] = {pair[0], pair[1]};
        assert(aefd_table_pipe(&map, &client, &creator, NULL, 0) == -22);
        assert(pair[0] == old_pair[0] && pair[1] == old_pair[1]);
        aefd_client_abort(&client);
        assert(seen.closes == 1);
        /* Explicit source-owner cleanup for uncommitted/unknown pipe objects.
         */
        for (unsigned end = 0; end < 4; ++end)
            if (seen.ends[end] >= 0) {
                int fd = seen.ends[end];
                assert(close(fd) == 0);
                errno = 0;
                assert(fcntl(fd, F_GETFD) == -1 && errno == EBADF);
                seen.ends[end] = -1;
            }
    }
}
int64_t aefd_pipe_test_open(struct aefd_bindings *map,
                            struct aefd_client *client,
                            const unsigned char *name, size_t length, int flag)
{
    exercise();
    return aefd_write_test_open(map, client, name, length, flag);
}
int64_t aefd_pipe_test_dup(struct aefd_bindings *map,
                           struct aefd_client *client, int fd, int minimum,
                           int flag)
{
    exercise();
    return aefd_write_test_dup(map, client, fd, minimum, flag);
}
int64_t aefd_pipe_test_close(struct aefd_bindings *map,
                             struct aefd_client *client, int fd)
{
    exercise();
    return aefd_write_test_close(map, client, fd);
}
int64_t aefd_pipe_test_flags(struct aefd_bindings *map,
                             struct aefd_client *client, int fd, int flag)
{
    exercise();
    return aefd_write_test_flags(map, client, fd, flag);
}
