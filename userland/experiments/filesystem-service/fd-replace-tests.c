/* SPDX-License-Identifier: BSD-2-Clause */
/* Host pipe-backed stream replacement, not native console or POSIX dup2. */
#include "fd-replace-tests.h"
#include "fd-replace.h"
#include "fd-write.h"
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
struct observed {
    int ends[4];
    int actual_close;
    unsigned calls, closes, closed_at;
    struct aefd_stream_close_result reply;
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
static unsigned endpoint(unsigned kind, unsigned selector)
{
    assert((kind == AEFD_BIND_CONSOLE && selector == 1) ||
           (kind == AEFD_BIND_PIPE && selector == 4));
    return kind == AEFD_BIND_CONSOLE ? 3U : 1U;
}
static struct aefd_stream_close_result
close_stream(void *context, unsigned kind, unsigned selector)
{
    struct observed *seen = context;
    ++seen->calls;
    unsigned at = endpoint(kind, selector);
    assert(at == seen->closed_at);
    if (seen->actual_close) {
        assert(seen->ends[at] >= 0);
        assert(close(seen->ends[at]) == 0);
        seen->ends[at] = -1;
    }
    return seen->reply;
}
static struct aefd_stream_result write_stream(void *context, unsigned kind,
                                              unsigned selector,
                                              const unsigned char *input,
                                              size_t count)
{
    struct observed *seen = context;
    ssize_t result = write(seen->ends[endpoint(kind, selector)], input, count);
    assert(result >= 0);
    return (struct aefd_stream_result){1, result};
}
static struct aefd_bindings map_for(unsigned mode)
{
    unsigned char raw[AEFD_BINDINGS_BYTES] = {0};
    memcpy(raw, "AEFDT001", 8);
    aefd_put(raw, 1, mode == 7 ? 78 : 77);
    aefd_put(raw, 2, 16);
    raw[64 + 1 * 4] = AEFD_BIND_CONSOLE;
    raw[65 + 1 * 4] = 1;
    raw[66 + 1 * 4] = 1;
    raw[64 + 4 * 4] = AEFD_BIND_PIPE;
    raw[65 + 4 * 4] = 4;
    raw[66 + 4 * 4] = 1;
    raw[64 + 8 * 4] = AEFD_BIND_FILE;
    raw[65 + 8 * 4] = 3;
    if (mode == 3 || mode == 4)
        for (unsigned fd = 0; fd < 16; ++fd)
            if (mode == 4 || fd == 1) {
                raw[64 + fd * 4] = AEFD_BIND_PIPE;
                raw[65 + fd * 4] = 4;
                raw[66 + fd * 4] = 1;
            }
    struct aefd_bindings map;
    assert(aefd_bindings_decode(raw, sizeof raw, mode == 7 ? 78 : 77, &map));
    if (mode == 15)
        map.slots[1].reserved = 1;
    return map;
}
static void exercise(void)
{
    static int ran;
    if (ran)
        return;
    ran = 1;
    for (unsigned mode = 0; mode < 19; ++mode) {
        struct observed seen = {
            .actual_close = 1, .closed_at = 3, .reply = {1, 1, 0}};
        assert(pipe(seen.ends) == 0 && pipe(seen.ends + 2) == 0);
        struct aefd_io io = {&seen, forbidden_read, forbidden_write,
                             forbidden_wait, file_close};
        struct aefd_client client;
        assert(aefd_client_init(&client, io, scratch, 77));
        struct aefd_bindings map = map_for(mode), before = map;
        struct aefd_stream_closer closer = {&seen, close_stream};
        int source = 4, target = 1, live = 1;
        int64_t expected = 1;
        unsigned calls = 1;
        const struct aefd_stream_closer *adapter = &closer;
        struct aefd_client *selected = &client;
        if (mode == 1 || mode == 2 || mode == 3 || mode == 4) {
            target = mode == 1 ? 4 : mode == 2 ? 0 : 1;
            expected = target;
            adapter = NULL;
            calls = 0;
        } else if (mode == 5) {
            source = 15;
            expected = -9;
            calls = 0;
        } else if (mode == 6) {
            target = 16;
            expected = -9;
            calls = 0;
        } else if (mode == 7 || mode == 15) {
            expected = -5;
            live = 0;
            calls = 0;
        } else if (mode == 8 || mode == 9) {
            if (mode == 8)
                source = 8;
            else
                target = 8;
            expected = -38;
            calls = 0;
        } else if (mode == 10) {
            seen.actual_close = 0;
            seen.reply = (struct aefd_stream_close_result){1, 0, -13};
            expected = -13;
        } else if (mode == 11) {
            seen.reply.status = -5;
            expected = -5;
        } else if (mode == 12 || mode == 13) {
            seen.actual_close = mode == 13;
            seen.reply.complete = 0;
            expected = -5;
            live = 0;
        } else if (mode == 14) {
            adapter = NULL;
            expected = -38;
            calls = 0;
        } else if (mode == 16) {
            selected = NULL;
            expected = -5;
            calls = 0;
        } else if (mode == 17) {
            source = 1;
            target = 4;
            expected = 4;
            seen.closed_at = 1;
        } else if (mode == 18) {
            source = target = 8;
            expected = -38;
            calls = 0;
        }
        assert(aefd_stream_replace(&map, selected, adapter, source, target) ==
               expected);
        assert(client.live == live && seen.calls == calls);
        if (expected >= 0) {
            struct aefd_binding value = before.slots[source];
            if (source != target)
                value.cloexec = 0;
            assert(!memcmp(&map.slots[target], &value, sizeof value));
            assert(map.slots[source].cloexec == 1);
            for (int fd = 0; fd < 16; ++fd)
                if (fd != target)
                    assert(!memcmp(&map.slots[fd], &before.slots[fd],
                                   sizeof value));
            struct aefd_stream_writer writer = {&seen, write_stream};
            assert(aefd_routed_write(&map, &client, &writer, target,
                                     (const unsigned char *)"ab", 2) == 2);
            unsigned at = source == 1 ? 2U : 0U;
            assert(read(seen.ends[at], bytes, 2) == 2 &&
                   !memcmp(bytes, "ab", 2));
            if (calls) {
                unsigned old_reader = seen.closed_at - 1;
                assert(read(seen.ends[old_reader], bytes, sizeof bytes) == 0);
            }
        } else if (mode == 11) {
            assert(map.slots[target].kind == AEFD_BIND_EMPTY);
            before.slots[target] = (struct aefd_binding){0};
            assert(!memcmp(&map, &before, sizeof map) && seen.ends[3] == -1);
            struct aefd_stream_writer writer = {&seen, write_stream};
            assert(aefd_routed_write(&map, &client, &writer, source,
                                     (const unsigned char *)"ok", 2) == 2);
            assert(read(seen.ends[0], bytes, 2) == 2 &&
                   !memcmp(bytes, "ok", 2));
            assert(read(seen.ends[2], bytes, sizeof bytes) == 0);
        } else {
            assert(!memcmp(&map, &before, sizeof map));
            if (!live) {
                assert(aefd_stream_replace(&map, &client, &closer, 4, 1) == -5);
                assert(seen.calls == calls && seen.closes == 1);
            }
            if (mode == 10) {
                seen.actual_close = 1;
                seen.reply = (struct aefd_stream_close_result){1, 1, 0};
                assert(aefd_stream_replace(&map, &client, &closer, 4, 1) == 1);
                assert(seen.calls == 2 && map.slots[1].kind == AEFD_BIND_PIPE);
                assert(map.slots[1].cloexec == 0);
                struct aefd_stream_writer writer = {&seen, write_stream};
                assert(aefd_routed_write(&map, &client, &writer, 1,
                                         (const unsigned char *)"ok", 2) == 2);
                assert(read(seen.ends[0], bytes, 2) == 2 &&
                       !memcmp(bytes, "ok", 2));
            }
        }
        aefd_client_abort(&client);
        assert(seen.closes == 1);
        /* File abort is not stream cleanup. Explicitly settle fixture
         * endpoints. */
        for (unsigned end = 0; end < 4; ++end)
            if (seen.ends[end] >= 0) {
                int fd = seen.ends[end];
                assert(close(fd) == 0);
                errno = 0;
                assert(fcntl(fd, F_GETFD) == -1 && errno == EBADF);
            }
    }
}
int64_t aefd_replace_test_open(struct aefd_bindings *map,
                               struct aefd_client *client,
                               const unsigned char *name, size_t length,
                               int flag)
{
    exercise();
    return aefd_pipe_test_open(map, client, name, length, flag);
}
int64_t aefd_replace_test_dup(struct aefd_bindings *map,
                              struct aefd_client *client, int fd, int minimum,
                              int flag)
{
    exercise();
    return aefd_pipe_test_dup(map, client, fd, minimum, flag);
}
int64_t aefd_replace_test_close(struct aefd_bindings *map,
                                struct aefd_client *client, int fd)
{
    exercise();
    return aefd_pipe_test_close(map, client, fd);
}
int64_t aefd_replace_test_flags(struct aefd_bindings *map,
                                struct aefd_client *client, int fd, int flag)
{
    exercise();
    return aefd_pipe_test_flags(map, client, fd, flag);
}
